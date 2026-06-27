package com.karmicgochara.app;

import android.content.Context;
import androidx.documentfile.provider.DocumentFile;
import android.os.ParcelFileDescriptor;
import android.content.SharedPreferences;
import java.io.OutputStream;


import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import com.google.ai.edge.litertlm.Engine;
import com.google.ai.edge.litertlm.EngineConfig;
import com.google.ai.edge.litertlm.Conversation;
import com.google.ai.edge.litertlm.ConversationConfig;
import com.google.ai.edge.litertlm.Backend;
import com.google.ai.edge.litertlm.SamplerConfig;
import com.google.ai.edge.litertlm.Contents;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import androidx.activity.result.ActivityResult;
import com.getcapacitor.annotation.ActivityCallback;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicReference;


/**
 * GemmaSynthesisPlugin — Inférence locale Gemma via MediaPipe LlmInference 0.10.35.
 *
 * Architecture 0.10.35 :
 *   - LlmInferenceOptions : uniquement setModelPath() + setMaxTokens()
 *   - LlmInferenceSession : porte Temperature / TopK / LoraPath (déplacés depuis LlmInferenceOptions)
 *   - generateResponse() : via LlmInferenceSession (et non plus directement sur LlmInference)
 *
 *   - Modèle .task téléchargé depuis HuggingFace au premier lancement
 *     (URL configurable via MODEL_URL).
 *   - LoRA adapter : assets/lora/doctrine_adapter.bin — doctrine karmique @siderealAstro13
 *   - Fallback vault (assets/karmic_vault/) quand LoRA absent.
 *
 * Capacitor methods (inchangés pour le JS) :
 *   checkAvailability()  → {available, status, downloading}
 *   prepareModel()       → télécharge le modèle + charge l'inférence
 *   generate(system, user, type) → {synthesis, local: true, loraUsed}
 *   unloadModel()        → close()
 *   getDeviceMemory()    → {totalRamGb, sufficient, recommended}
 */
@CapacitorPlugin(name = "GemmaSynthesis")
public class GemmaSynthesisPlugin extends Plugin {

    // ── LoRA ─────────────────────────────────────────────────────────────────
    private static final String LORA_ASSET_PATH    = "lora/doctrine_adapter.bin";
    private static final String LORA_CACHE_FILENAME = "doctrine_adapter.bin";

    // ── Modèle ────────────────────────────────────────────────────────────────
    // Gemma 4 E2B It 4‑bit quantisé (LiteRT format) — dynamique via setModel()
    private static String sModelUrl = "https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm/resolve/main/gemma-4-E2B-it.litertlm";
    private static String sModelFilename = "gemma-4-E2B-it.litertlm";

    // ── Paramètres inférence constants ────────────────────────────────────────
    private static final int   MAX_TOKENS_SYNTHESIS = 2048;
    private static final int   MAX_TOKENS_REPORT    = 4096;
    private static final float TEMPERATURE          = 0.7f;
    private static final int   TOP_K                = 40;

    // ── État runtime — static pour survivre aux recreations d'Activity ────────
    // Modèle (lourd, partagé entre sessions). Créé une fois, fermé via unloadModel().
    private static final AtomicReference<Engine> sEngineRef = new AtomicReference<>(null);
    // Session de base créée pour LiteRT-LM
    private static final AtomicReference<Conversation> sBaseConversationRef = new AtomicReference<>(null);
    private static ParcelFileDescriptor sModelPfd = null;
    private static boolean             sLoraLoaded = false;
    private static boolean             sPreparing  = false;
    private static boolean             sDownloading = false;
    private static int                 sMaxTokens  = MAX_TOKENS_SYNTHESIS;

    // Utilisation de CachedThreadPool pour éviter le blocage du thread unique en cas d'erreur réseau
    private final ExecutorService executor = Executors.newCachedThreadPool();

    // ── Méthode pour init forcée depuis MainActivity ─────────────────────────
    public static void forceInit(Context context) {
        android.util.Log.i("GemmaSynthesis", "Init forcée au démarrage...");
    }


    // ══════════════════════════════════════════════════════════════════════════
    //  checkAvailability
    // ══════════════════════════════════════════════════════════════════════════
    private boolean hasStoredDocumentTree() {
        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        return prefs.getString("model_tree_uri", null) != null;
    }

    private DocumentFile getTreeDocumentFile() {
        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        String uriStr = prefs.getString("model_tree_uri", null);
        if (uriStr == null) return null;
        Uri treeUri = Uri.parse(uriStr);
        DocumentFile dir = DocumentFile.fromTreeUri(getContext(), treeUri);
        if (dir == null || !dir.exists() || !dir.canRead()) return null;
        return dir;
    }

    private DocumentFile getModelDocumentFile() {
        DocumentFile dir = getTreeDocumentFile();
        if (dir == null) return null;
        return dir.findFile(sModelFilename);
    }

    private DocumentFile getOrCreateModelDocumentFile() {
        DocumentFile dir = getTreeDocumentFile();
        if (dir == null) return null;
        DocumentFile file = dir.findFile(sModelFilename);
        if (file == null) {
            file = dir.createFile("application/octet-stream", sModelFilename);
        }
        return file;
    }

    @PluginMethod
    public void requestStoragePermission(PluginCall call) {
        saveCall(call);
        if (hasStoredDocumentTree()) {
            JSObject res = new JSObject();
            res.put("ok", true);
            call.resolve(res);
            return;
        }
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(call, intent, "storagePermResult");
    }

    @ActivityCallback
    private void storagePermResult(PluginCall call, ActivityResult result) {
        if (call == null) return;
        boolean ok = false;
        if (result.getResultCode() == Activity.RESULT_OK) {
            Intent data = result.getData();
            if (data != null && data.getData() != null) {
                Uri treeUri = data.getData();
                getContext().getContentResolver().takePersistableUriPermission(treeUri,
                        Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                prefs.edit().putString("model_tree_uri", treeUri.toString()).apply();
                ok = true;
            }
        }
        JSObject res = new JSObject();
        res.put("ok", ok);
        call.resolve(res);
    }

    @PluginMethod
    public void checkAvailability(PluginCall call) {
        JSObject result = new JSObject();
        if (!hasStoredDocumentTree()) {
            result.put("available",   false);
            result.put("status",      "permission_required");
            result.put("downloading", false);
            call.resolve(result);
            return;
        }

        DocumentFile modelFile = getModelDocumentFile();
        if (modelFile != null && modelFile.exists() && modelFile.length() > 0) {
            result.put("available",   true);
            result.put("status",      "available");
            result.put("downloading", false);
        } else if (sDownloading) {
            result.put("available",   false);
            result.put("status",      "downloading");
            result.put("downloading", true);
        } else {
            result.put("available",   false);
            result.put("status",      "downloadable");
            result.put("downloading", false);
        }
        call.resolve(result);
    }


    // ══════════════════════════════════════════════════════════════════════════
    //  Dynamic Model Configuration
    // ══════════════════════════════════════════════════════════════════════════

    @PluginMethod
    public void setModel(PluginCall call) {
        String url = call.getString("modelUrl");
        String filename = call.getString("filename");

        if (url == null || filename == null) {
            call.reject("INVALID_PARAMS", "modelUrl and filename are required.");
            return;
        }

        synchronized (GemmaSynthesisPlugin.class) {
            sModelUrl = url;
            sModelFilename = filename;
            
            // Si on change de modèle, on décharge l'ancien
            unloadModelInternal();
        }

        JSObject result = new JSObject();
        result.put("ok", true);
        result.put("modelId", filename);
        call.resolve(result);
    }

    @PluginMethod
    public void getModelStatus(PluginCall call) {
        DocumentFile modelFile = getModelDocumentFile();
        JSObject result = new JSObject();
        result.put("downloaded", modelFile != null && modelFile.exists() && modelFile.length() > 0);
        result.put("modelId", sModelFilename);
        result.put("sizeBytes", modelFile != null && modelFile.exists() ? modelFile.length() : 0);
        call.resolve(result);
    }

    @PluginMethod
    public void isModelDownloaded(PluginCall call) {
        DocumentFile modelFile = getModelDocumentFile();
        JSObject result = new JSObject();
        result.put("downloaded", modelFile != null && modelFile.exists() && modelFile.length() > 0);
        call.resolve(result);
    }

    @PluginMethod
    public void downloadModel(PluginCall call) {
        if (sDownloading) {
            call.reject("ALREADY_DOWNLOADING", "Un téléchargement est déjà en cours.");
            return;
        }

        boolean force = Boolean.TRUE.equals(call.getBoolean("force", false));

        executor.execute(() -> {
            try {
                DocumentFile modelFile = getModelDocumentFile();
                if (!force && modelFile != null && modelFile.exists() && modelFile.length() > 0) {
                    JSObject result = new JSObject();
                    result.put("ok", true);
                    result.put("alreadyDownloaded", true);
                    call.resolve(result);
                    return;
                }

                DocumentFile destFile = getOrCreateModelDocumentFile();
                if (destFile == null) {
                    call.reject("DOWNLOAD_ERROR", "Dossier de stockage non configuré ou invalide.");
                    return;
                }

                if (downloadModelWithProgress(destFile)) {
                    JSObject result = new JSObject();
                    result.put("ok", true);
                    call.resolve(result);
                } else {
                    call.reject("DOWNLOAD_FAILED", "Échec du téléchargement.");
                }
            } catch (IOException e) {
                call.reject("DOWNLOAD_ERROR", e.getMessage());
            }
        });
    }

    @PluginMethod
    public void selectLocalModel(PluginCall call) {
        if (sDownloading) {
            call.reject("ALREADY_DOWNLOADING", "Un téléchargement ou une copie est déjà en cours.");
            return;
        }
        saveCall(call);
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        startActivityForResult(call, intent, "pickModelResult");
    }

    @ActivityCallback
    private void pickModelResult(PluginCall call, ActivityResult result) {
        if (call == null) return;
        if (result.getResultCode() == Activity.RESULT_OK && result.getData() != null) {
            Uri uri = result.getData().getData();
            if (uri != null) {
                sDownloading = true;
                executor.execute(() -> {
                    try {
                        long totalSize = -1;
                        try (android.database.Cursor cursor = getContext().getContentResolver().query(uri, null, null, null, null)) {
                            if (cursor != null && cursor.moveToFirst()) {
                                int sizeIndex = cursor.getColumnIndex(android.provider.OpenableColumns.SIZE);
                                if (sizeIndex != -1) {
                                    totalSize = cursor.getLong(sizeIndex);
                                }
                            }
                        }

                        DocumentFile destFile = getOrCreateModelDocumentFile();
                        if (destFile == null) {
                            throw new IOException("Dossier de stockage non configuré ou invalide.");
                        }
                        try (java.io.InputStream in = getContext().getContentResolver().openInputStream(uri);
                             java.io.OutputStream out = getContext().getContentResolver().openOutputStream(destFile.getUri())) {
                            if (in == null) {
                                throw new IOException("Impossible d'ouvrir le fichier sélectionné.");
                            }
                            byte[] buf = new byte[65536];
                            int n;
                            long copied = 0;
                            while ((n = in.read(buf)) != -1) {
                                out.write(buf, 0, n);
                                copied += n;
                                if (totalSize > 0) {
                                    int progress = (int) (copied * 100 / totalSize);
                                    JSObject data = new JSObject();
                                    data.put("progress", progress);
                                    data.put("bytes", copied);
                                    data.put("total", totalSize);
                                    notifyListeners("modelDownloadProgress", data);
                                }
                            }
                        }

                        sDownloading = false;
                        JSObject res = new JSObject();
                        res.put("ok", true);
                        call.resolve(res);

                    } catch (Exception e) {
                        sDownloading = false;
                        android.util.Log.e("GemmaSynthesis", "Erreur copie : " + e.getMessage());
                        call.reject("COPY_FAILED", e.getMessage());
                    }
                });
            } else {
                call.reject("NO_URI", "Fichier non sélectionné.");
            }
        } else {
            call.reject("CANCELLED", "Sélection annulée.");
        }
    }

    private boolean downloadModelWithProgress(DocumentFile dest) throws IOException {
        sDownloading = true;
        try {
            URL url = new URL(sModelUrl);
            HttpURLConnection conn = null;
            int redirects = 0;
            while (redirects < 5) {
                conn = (HttpURLConnection) url.openConnection();
                conn.setConnectTimeout(15_000);
                conn.setReadTimeout(30_000);
                conn.setInstanceFollowRedirects(false); // Manual redirect
                conn.connect();

                int responseCode = conn.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_MOVED_PERM ||
                    responseCode == HttpURLConnection.HTTP_MOVED_TEMP ||
                    responseCode == HttpURLConnection.HTTP_SEE_OTHER ||
                    responseCode == 307 || responseCode == 308) {
                    String newUrl = conn.getHeaderField("Location");
                    url = new URL(newUrl);
                    redirects++;
                    continue;
                }
                
                if (responseCode != HttpURLConnection.HTTP_OK) {
                    throw new IOException("HTTP " + responseCode + " pour " + sModelUrl);
                }
                break;
            }

            long total = conn.getContentLengthLong();
            long downloaded = 0;

            try (InputStream in  = conn.getInputStream();
                 java.io.OutputStream out = getContext().getContentResolver().openOutputStream(dest.getUri())) {
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) != -1) {
                    out.write(buf, 0, n);
                    downloaded += n;
                    
                    if (total > 0) {
                        int progress = (int) (downloaded * 100 / total);
                        JSObject data = new JSObject();
                        data.put("progress", progress);
                        data.put("bytes", downloaded);
                        data.put("total", total);
                        notifyListeners("modelDownloadProgress", data);
                    }
                }
            }
            if (total > 0 && downloaded != total) {
                dest.delete();
                throw new IOException("Téléchargement incomplet: " + downloaded + " / " + total);
            }
            // Sanity check: Gemma 4 E2B is ~2.5GB. If it's less than 50MB, it's definitely an error page.
            if (downloaded < 50_000_000L) {
                dest.delete();
                throw new IOException("Fichier téléchargé trop petit (erreur ou redirection non suivie) : " + downloaded + " octets");
            }
            return dest.exists() && dest.length() > 0;
        } catch (Exception e) {
            if (dest.exists()) dest.delete();
            throw new IOException(e);
        } finally {
            sDownloading = false;
        }
    }

    private void unloadModelInternal() {
        Engine engine = sEngineRef.getAndSet(null);
        if (engine != null) {
            try { engine.close(); } catch (Exception ignored) {}
        }
        Conversation conversation = sBaseConversationRef.getAndSet(null);
        if (conversation != null) {
            try { conversation.close(); } catch (Exception ignored) {}
        }
        if (sModelPfd != null) {
            try { sModelPfd.close(); } catch (Exception ignored) {}
            sModelPfd = null;
        }
        sLoraLoaded = false;
    }

    // ══════════════════════════════════════════════════════════════════════════
    //  prepareModel
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void prepareModel(PluginCall call) {
        if (sEngineRef.get() != null && sBaseConversationRef.get() != null) {
            JSObject result = new JSObject();
            result.put("ok",       true);
            result.put("loraUsed", false);
            result.put("cached",   true);
            call.resolve(result);
            return;
        }

        boolean useReport = Boolean.TRUE.equals(call.getBoolean("report", false));
        sMaxTokens = useReport ? MAX_TOKENS_REPORT : MAX_TOKENS_SYNTHESIS;

        synchronized (GemmaSynthesisPlugin.class) {
            if (sPreparing) {
                call.reject("ALREADY_PREPARING", "prepareModel() déjà en cours.");
                return;
            }
            sPreparing = true;
        }

        executor.execute(() -> {
            try {
                DocumentFile modelFile = getModelDocumentFile();
                if (modelFile == null || !modelFile.exists() || modelFile.length() == 0) {
                    // Si absent, lancer le téléchargement
                    modelFile = getOrCreateModelDocumentFile();
                    if (modelFile == null) {
                        throw new IOException("Dossier de stockage invalide ou manquant.");
                    }
                    if (!downloadModelWithProgress(modelFile)) {
                        throw new IOException("Modèle absent et impossible d'initialiser le téléchargement.");
                    }
                }
                
                // Get the updated model file (in case it was just created)
                if (modelFile == null) {
                    modelFile = getModelDocumentFile();
                }

                // Open ParcelFileDescriptor for the model in SAF
                if (sModelPfd != null) {
                    try { sModelPfd.close(); } catch (Exception ignored) {}
                }
                sModelPfd = getContext().getContentResolver().openFileDescriptor(modelFile.getUri(), "r");
                if (sModelPfd == null) {
                    throw new IOException("Impossible d'ouvrir le descripteur de fichier pour le modèle.");
                }
                
                int fd = sModelPfd.getFd();
                String fdPath = "/proc/self/fd/" + fd;

                // 2. Construire l'Engine LiteRT-LM
                EngineConfig modelOpts = new EngineConfig(
                    fdPath,
                    new Backend.CPU(),
                    null, null, sMaxTokens, null, null
                );

                Engine engine = new Engine(modelOpts);
                engine.initialize();

                SamplerConfig samplerOpts = new SamplerConfig(TOP_K, 1.0, TEMPERATURE, 0);
                ConversationConfig conversationOpts = new ConversationConfig(
                    null, new java.util.ArrayList<>(), new java.util.ArrayList<>(),
                    samplerOpts, true, null, new java.util.HashMap<>(), null
                );

                Conversation conversation = engine.createConversation(conversationOpts);

                synchronized (GemmaSynthesisPlugin.class) {
                    sEngineRef.set(engine);
                    sBaseConversationRef.set(conversation);
                    sLoraLoaded  = false;
                    sPreparing   = false;
                }

                JSObject result = new JSObject();
                result.put("ok",       true);
                result.put("loraUsed", false);
                result.put("cached",   false);
                call.resolve(result);

            } catch (Exception e) {
                synchronized (GemmaSynthesisPlugin.class) { sPreparing = false; }
                android.util.Log.w("GemmaSynthesis", "Erreur lors de la préparation : " + e.getMessage());
                String msg = e.getMessage() != null ? e.getMessage() : "";
                if (msg.contains("Unsupported or unknown file format") || msg.contains("INVALID_ARGUMENT") || msg.contains("No such file or directory")) {
                    DocumentFile modelFile = getModelDocumentFile();
                    if (modelFile != null && modelFile.exists()) {
                        modelFile.delete();
                    }
                }
                call.reject("PREPARE_ERROR", e.getMessage());
            }
        });
    }


    // ══════════════════════════════════════════════════════════════════════════
    //  generate
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void generate(PluginCall call) {
        String lightPrompt = call.getString("lightPrompt");
        String system = call.getString("system", "");
        String user   = call.getString("user",   "");
        String type   = call.getString("type",   "synthesis");
        String lang   = call.getString("lang",   "fr");

        // Priorité au lightPrompt (RAG) s'il est fourni
        final String effectiveUser = (lightPrompt != null && !lightPrompt.isEmpty()) ? lightPrompt : user;

        if (effectiveUser == null || effectiveUser.isEmpty()) {
            call.reject("INVALID_PROMPT", "Prompt vide.");
            return;
        }

        JSObject profileJs = call.getObject("profile", new JSObject());
        org.json.JSONObject profile;
        try { profile = new org.json.JSONObject(profileJs.toString()); }
        catch (Exception e) { profile = new org.json.JSONObject(); }
        final org.json.JSONObject finalProfile = profile;

        executor.execute(() -> {
            // Lazy-init : charger le modèle au premier appel si pas déjà fait
            if (sEngineRef.get() == null) {
                try {
                    DocumentFile modelFile = getModelDocumentFile();
                    if (modelFile == null || !modelFile.exists() || modelFile.length() == 0) {
                        modelFile = getOrCreateModelDocumentFile();
                        if (modelFile != null) downloadModelWithProgress(modelFile);
                    }

                    if (modelFile != null && modelFile.exists() && modelFile.length() > 0) {
                        if (sModelPfd != null) {
                            try { sModelPfd.close(); } catch (Exception ignored) {}
                        }
                        sModelPfd = getContext().getContentResolver().openFileDescriptor(modelFile.getUri(), "r");
                        if (sModelPfd != null) {
                            int fd = sModelPfd.getFd();
                            String fdPath = "/proc/self/fd/" + fd;

                            EngineConfig modelOpts = new EngineConfig(
                                fdPath,
                                new Backend.CPU(),
                                null, null, sMaxTokens, null, null
                            );
                            Engine engine = new Engine(modelOpts);
                            engine.initialize();

                            SamplerConfig samplerOpts = new SamplerConfig(TOP_K, 1.0, TEMPERATURE, 0);
                            ConversationConfig conversationOpts = new ConversationConfig(
                                null, new java.util.ArrayList<>(), new java.util.ArrayList<>(),
                                samplerOpts, true, null, new java.util.HashMap<>(), null
                            );
                            Conversation conversation = engine.createConversation(conversationOpts);

                            synchronized (GemmaSynthesisPlugin.class) {
                                sEngineRef.set(engine);
                                sBaseConversationRef.set(conversation);
                            }
                        }
                    }
                } catch (Exception e) {
                    android.util.Log.w("GemmaSynthesis", "Erreur init différée : " + e.getMessage());
                }
            }

            Engine engine = sEngineRef.get();
            if (engine == null) {
                call.reject("MODEL_NOT_READY", "Moteur non disponible. Vérifiez l'installation.");
                return;
            }

            String contextualSystem;
            if (system != null && !system.isEmpty()) {
                contextualSystem = system;
            } else {
                contextualSystem = DoctrinePromptBuilder.buildSystemPrompt(
                    getContext(), finalProfile, lang
                );
            }

            SamplerConfig samplerOpts = new SamplerConfig(TOP_K, 1.0, TEMPERATURE, 0);
            ConversationConfig conversationOpts = new ConversationConfig(
                Contents.Companion.of(contextualSystem),
                new java.util.ArrayList<>(),
                new java.util.ArrayList<>(),
                samplerOpts,
                true,
                null,
                new java.util.HashMap<>(),
                null
            );

            try (Conversation conversation = engine.createConversation(conversationOpts)) {
                // Inférence synchrone bloquante via le helper Kotlin
                String response = GemmaHelper.generateSync(conversation, effectiveUser);

                JSObject result = new JSObject();
                result.put("ok",        true);
                result.put("synthesis", response.trim());
                result.put("local",     true);
                result.put("loraUsed",  false);
                result.put("type",      type);
                call.resolve(result);

            } catch (Exception e) {
                call.reject("INFERENCE_ERROR", e.getMessage(), e);
            }
        });
    }


    // ══════════════════════════════════════════════════════════════════════════
    //  unloadModel
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void unloadModel(PluginCall call) {
        synchronized (GemmaSynthesisPlugin.class) {
            unloadModelInternal();
        }
        JSObject result = new JSObject();
        result.put("ok", true);
        call.resolve(result);
    }


    // ══════════════════════════════════════════════════════════════════════════
    //  getDeviceMemory
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void getDeviceMemory(PluginCall call) {
        android.app.ActivityManager am = (android.app.ActivityManager)
            getContext().getSystemService(Context.ACTIVITY_SERVICE);
        android.app.ActivityManager.MemoryInfo memInfo =
            new android.app.ActivityManager.MemoryInfo();
        am.getMemoryInfo(memInfo);

        long totalRamGb = memInfo.totalMem / (1024L * 1024L * 1024L);

        JSObject result = new JSObject();
        result.put("totalRamGb",  totalRamGb);
        result.put("sufficient",  totalRamGb >= 4);
        result.put("recommended", totalRamGb >= 6 ? "full"
                                 : totalRamGb >= 4 ? "standard"
                                 : "unavailable");
        call.resolve(result);
    }


    // ══════════════════════════════════════════════════════════════════════════
    //  checkModel / checkModels : rétrocompat JS
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void checkModel(PluginCall call)  { checkAvailability(call); }
    @PluginMethod
    public void checkModels(PluginCall call) { checkAvailability(call); }


    // ══════════════════════════════════════════════════════════════════════════
    //  Helpers privés
    // ══════════════════════════════════════════════════════════════════════════

    /**
     * Copie le LoRA depuis assets/lora/ vers le cache interne.
     * Retourne true si dispo et non-vide.
     */
    private boolean ensureLoraExtracted() {
        File dest = getLoraFile();
        if (dest.exists() && dest.length() > 0) return true;

        try (InputStream is = getContext().getAssets().open(LORA_ASSET_PATH)) {
            
            try (java.io.FileOutputStream fos = new java.io.FileOutputStream(dest)) {
                byte[] buf = new byte[8192];
                int n;
                while ((n = is.read(buf)) != -1) fos.write(buf, 0, n);
            }
            return dest.exists() && dest.length() > 0;
        } catch (IOException e) {
            return false;
        }
    }

    

    private File getLoraFile() {
        return new File(getContext().getFilesDir(), "lora/" + LORA_CACHE_FILENAME);
    }

    /**
     * Fallback : charge le vault depuis assets/karmic_vault/ si LoRA absent.
     */
    private String getVaultContent() {
        StringBuilder sb = new StringBuilder();
        try {
            String[] files = getContext().getAssets().list("karmic_vault");
            if (files == null) return "";
            for (String fileName : files) {
                if (!fileName.endsWith(".md")) continue;
                try (InputStream is = getContext().getAssets().open("karmic_vault/" + fileName);
                     BufferedReader reader = new BufferedReader(new InputStreamReader(is))) {
                    String line;
                    while ((line = reader.readLine()) != null) sb.append(line).append("\n");
                    sb.append("\n---\n");
                }
            }
        } catch (IOException e) {
            return "";
        }
        return sb.toString();
    }

    /**
     * Format prompt Gemma Instruct (Gemma 3/4) :
     * <start_of_turn>user\n{system}\n\n{user}<end_of_turn>\n<start_of_turn>model\n
     */
    private String buildGemmaPrompt(String system, String user) {
        StringBuilder sb = new StringBuilder("<start_of_turn>user\n");
        if (system != null && !system.isEmpty()) sb.append(system).append("\n\n");
        sb.append(user).append("<end_of_turn>\n<start_of_turn>model\n");
        return sb.toString();
    }

    @Override
    protected void handleOnDestroy() {
        executor.shutdown();
        // Ne PAS fermer sModel / sBaseSession ici — static, survit aux recreations d'Activity.
        // Appeler unloadModel() explicitement si besoin de libérer la mémoire.
        super.handleOnDestroy();
    }
}
