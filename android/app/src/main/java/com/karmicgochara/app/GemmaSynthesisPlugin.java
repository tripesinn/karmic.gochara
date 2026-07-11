package com.karmicgochara.app;

import android.content.Context;
import android.os.Environment;
import android.content.SharedPreferences;
import android.os.ParcelFileDescriptor;
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

    private long getModelSize() {
        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        String customUriStr = prefs.getString("custom_model_uri", null);
        if (customUriStr != null) {
            try {
                ParcelFileDescriptor pfd = getContext().getContentResolver().openFileDescriptor(Uri.parse(customUriStr), "r");
                if (pfd != null) {
                    long size = pfd.getStatSize();
                    pfd.close();
                    if (size > 0) return size;
                }
            } catch (Exception e) {}
        }
        File f = getModelFile();
        return f.exists() ? f.length() : 0;
    }

    private File getModelFile() {
        File dir = getContext().getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (dir == null) {
            dir = getContext().getFilesDir();
        }
        if (!dir.exists()) dir.mkdirs();
        return new File(dir, sModelFilename);
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
        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        String customUriStr = prefs.getString("custom_model_uri", null);
        File modelFile = getModelFile();
        boolean isAvailable = false;
        if (customUriStr != null) {
            try {
                ParcelFileDescriptor pfd = getContext().getContentResolver().openFileDescriptor(Uri.parse(customUriStr), "r");
                if (pfd != null) {
                    isAvailable = pfd.getStatSize() > 0;
                    pfd.close();
                }
            } catch (Exception e) {}
        }
        if (!isAvailable && modelFile.exists() && modelFile.length() > 0) {
            isAvailable = true;
        }

        if (isAvailable) {
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
        JSObject result = new JSObject();
        long size = getModelSize();
        result.put("downloaded", size > 0);
        result.put("modelId", sModelFilename);
        result.put("sizeBytes", size);
        call.resolve(result);
    }

    @PluginMethod
    public void isModelDownloaded(PluginCall call) {
        JSObject result = new JSObject();
        result.put("downloaded", getModelSize() > 0);
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
                File modelFile = getModelFile();
                // Clear custom URI if downloading explicitly
                getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE).edit().remove("custom_model_uri").apply();
                if (!force && modelFile.exists() && modelFile.length() > 0) {
                    JSObject result = new JSObject();
                    result.put("ok", true);
                    result.put("alreadyDownloaded", true);
                    call.resolve(result);
                    return;
                }

                if (downloadModelWithProgress(modelFile)) {
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
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(call, intent, "pickModelResult");
    }

    @ActivityCallback
    private void pickModelResult(PluginCall call, ActivityResult result) {
        if (call == null) return;
        if (result.getResultCode() == Activity.RESULT_OK && result.getData() != null) {
            Uri uri = result.getData().getData();
            if (uri != null) {
                try {
                    getContext().getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                } catch (Exception ignored) {} // Some URIs don't support persistable permissions
                
                SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                prefs.edit().putString("custom_model_uri", uri.toString()).apply();
                
                JSObject res = new JSObject();
                res.put("ok", true);
                call.resolve(res);
            } else {
                call.reject("NO_URI", "Fichier non sélectionné.");
            }
        } else {
            call.reject("CANCELLED", "Sélection annulée.");
        }
    }

    private boolean downloadModelWithProgress(File dest) throws IOException {
        sDownloading = true;
        try {
            URL url = new URL(sModelUrl);
            HttpURLConnection conn = null;
            int redirects = 0;
            while (redirects < 5) {
                conn = (HttpURLConnection) url.openConnection();
                conn.setConnectTimeout(15_000);
                conn.setReadTimeout(0); // Pas de timeout lecture — modèle de 2.58 Go
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
                 java.io.OutputStream out = new java.io.FileOutputStream(dest)) {
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
            return dest != null && dest.exists() && dest.length() > 0;
        } catch (Exception e) {
            android.util.Log.e("GemmaPlugin", "Erreur lors du téléchargement", e);
            if (dest != null && dest.exists()) dest.delete();
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
                String modelPath = null;
                SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                String customUriStr = prefs.getString("custom_model_uri", null);
                
                if (customUriStr != null) {
                    try {
                        Uri customUri = Uri.parse(customUriStr);
                        File targetFile = getModelFile();
                        java.io.InputStream in = getContext().getContentResolver().openInputStream(customUri);
                        if (in != null) {
                            java.io.FileOutputStream out = new java.io.FileOutputStream(targetFile);
                            byte[] buffer = new byte[8192];
                            int read;
                            long total = 0;
                            try {
                                android.os.ParcelFileDescriptor pfd = getContext().getContentResolver().openFileDescriptor(customUri, "r");
                                if (pfd != null) {
                                    total = pfd.getStatSize();
                                    pfd.close();
                                }
                            } catch (Exception ignored) {}
                            
                            long copied = 0;
                            long lastReport = 0;
                            sDownloading = true; // Use downloading flag to prevent concurrent actions
                            while ((read = in.read(buffer)) != -1) {
                                out.write(buffer, 0, read);
                                copied += read;
                                
                                // Report progress every 50MB
                                if (total > 0 && copied - lastReport > 50_000_000) {
                                    lastReport = copied;
                                    int progress = (int) (copied * 100 / total);
                                    JSObject data = new JSObject();
                                    data.put("progress", progress);
                                    data.put("bytes", copied);
                                    data.put("total", total);
                                    notifyListeners("modelDownloadProgress", data);
                                }
                            }
                            out.flush();
                            out.close();
                            in.close();
                            sDownloading = false;
                            
                            prefs.edit().remove("custom_model_uri").apply();
                            modelPath = targetFile.getAbsolutePath();
                        }
                    } catch (Exception e) {
                        prefs.edit().remove("custom_model_uri").apply();
                        throw new IOException("Erreur lors de la copie du modèle importé", e);
                    }
                }
                
                if (modelPath == null) {
                    File modelFile = getModelFile();
                    if (!modelFile.exists() || modelFile.length() == 0) {
                        if (!downloadModelWithProgress(modelFile)) {
                            throw new IOException("Modèle absent et impossible d'initialiser le téléchargement.");
                        }
                    }
                    modelPath = modelFile.getAbsolutePath();
                }

                // 2. Construire l'Engine LiteRT-LM
                // Configuration multimodale explicite pour Gemma 4 (Text + Vision + Audio)
                EngineConfig modelOpts = new EngineConfig(
                    modelPath,
                    new Backend.CPU(), // Text
                    null,              // Vision (null for text-only model)
                    null,              // Audio (null for text-only model)
                    sMaxTokens,        // Tokens
                    null,              // Max Images
                    getContext().getCacheDir().getAbsolutePath() // Cache
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
                android.util.Log.e("GemmaSynthesis", "Erreur lors de la préparation", e);
                String msg = e.getMessage() != null ? e.getMessage() : "";
                if (msg.contains("Unsupported or unknown file format") || msg.contains("INVALID_ARGUMENT") || msg.contains("No such file or directory")) {
                    File mf = getModelFile();
                    if (mf.exists()) {
                        mf.delete();
                    }
                }
                String stackTrace = android.util.Log.getStackTraceString(e);
                call.reject("PREPARE_ERROR", msg + "\n" + stackTrace);
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
                    String modelPath = null;
                        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                        String customUriStr = prefs.getString("custom_model_uri", null);
                        
                        if (customUriStr != null) {
                            try {
                                Uri customUri = Uri.parse(customUriStr);
                                File targetFile = getModelFile();
                                java.io.InputStream in = getContext().getContentResolver().openInputStream(customUri);
                                if (in != null) {
                                    java.io.FileOutputStream out = new java.io.FileOutputStream(targetFile);
                                    byte[] buffer = new byte[8192];
                                    int read;
                                    long total = 0;
                                    try {
                                        android.os.ParcelFileDescriptor pfd = getContext().getContentResolver().openFileDescriptor(customUri, "r");
                                        if (pfd != null) {
                                            total = pfd.getStatSize();
                                            pfd.close();
                                        }
                                    } catch (Exception ignored) {}
                                    
                                    long copied = 0;
                                    long lastReport = 0;
                                    sDownloading = true;
                                    while ((read = in.read(buffer)) != -1) {
                                        out.write(buffer, 0, read);
                                        copied += read;
                                        if (total > 0 && copied - lastReport > 50_000_000) {
                                            lastReport = copied;
                                            int progress = (int) (copied * 100 / total);
                                            JSObject data = new JSObject();
                                            data.put("progress", progress);
                                            data.put("bytes", copied);
                                            data.put("total", total);
                                            notifyListeners("modelDownloadProgress", data);
                                        }
                                    }
                                    out.flush();
                                    out.close();
                                    in.close();
                                    sDownloading = false;
                                    prefs.edit().remove("custom_model_uri").apply();
                                    modelPath = targetFile.getAbsolutePath();
                                }
                            } catch (Exception e) {}
                        }
                        
                        if (modelPath == null) {
                            File modelFile = getModelFile();
                            if (!modelFile.exists() || modelFile.length() == 0) {
                                downloadModelWithProgress(modelFile);
                            }
                            if (modelFile.exists() && modelFile.length() > 0) {
                                modelPath = modelFile.getAbsolutePath();
                            }
                        }

                        if (modelPath != null) {

                        EngineConfig modelOpts = new EngineConfig(
                            modelPath,
                            new Backend.CPU(),
                            null,
                            null,
                            sMaxTokens,
                            null,
                            getContext().getCacheDir().getAbsolutePath()
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

        double totalRamGb = (double) memInfo.totalMem / (1024.0 * 1024.0 * 1024.0);

        JSObject result = new JSObject();
        result.put("totalRamGb",  totalRamGb);
        result.put("sufficient",  totalRamGb >= 3.5);
        result.put("recommended", totalRamGb >= 5.5 ? "full"
                                 : totalRamGb >= 3.5 ? "standard"
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
