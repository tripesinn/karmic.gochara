package com.karmicgochara.app;

import android.content.Context;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import com.google.mediapipe.tasks.genai.llminference.LlmInference;

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

/**
 * GemmaSynthesisPlugin — Inférence locale Gemma via MediaPipe LlmInference.
 *
 * Architecture :
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
    // Gemma 3 1B It 4‑bit quantisé (LiteRT format) — change l'URL pour un
    // modèle personnalisé ou un miroir.
    private static final String MODEL_URL      =
        "https://huggingface.co/litert-community/Gemma3-1B-IT/resolve/main/gemma3-1b-it-int4.task";
    private static final String MODEL_FILENAME = "gemma3-1b-it-int4.task";

    // ── Paramètres inférence constants ────────────────────────────────────────
    private static final int   MAX_TOKENS_SYNTHESIS = 2048;
    private static final int   MAX_TOKENS_REPORT    = 4096;
    private static final float TEMPERATURE          = 0.7f;
    private static final int   TOP_K                = 40;

    // ── État runtime — static pour survivre aux recreations d'Activity ────────
    private static LlmInference sModel       = null;
    private static boolean     sLoraLoaded   = false;
    private static boolean     sPreparing    = false;
    private static boolean     sDownloading  = false;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();


    // ══════════════════════════════════════════════════════════════════════════
    //  checkAvailability
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void checkAvailability(PluginCall call) {
        JSObject result = new JSObject();
        File modelFile = getModelFile();
        if (modelFile.exists() && modelFile.length() > 0) {
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
    //  prepareModel
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void prepareModel(PluginCall call) {
        if (sModel != null) {
            JSObject result = new JSObject();
            result.put("ok",       true);
            result.put("loraUsed", sLoraLoaded);
            result.put("cached",   true);
            call.resolve(result);
            return;
        }

        boolean useReport = Boolean.TRUE.equals(call.getBoolean("report", false));
        int maxTokens = useReport ? MAX_TOKENS_REPORT : MAX_TOKENS_SYNTHESIS;

        synchronized (GemmaSynthesisPlugin.class) {
            if (sPreparing) {
                call.reject("ALREADY_PREPARING", "prepareModel() déjà en cours.");
                return;
            }
            sPreparing = true;
        }

        executor.execute(() -> {
            try {
                // 1. Télécharger le modèle .task si pas encore en cache
                File modelFile = getModelFile();
                if (!modelFile.exists() || modelFile.length() == 0) {
                    if (!downloadModel(modelFile)) {
                        throw new IOException("Échec du téléchargement du modèle");
                    }
                }

                // 2. Extraire le LoRA depuis assets/ si dispo
                boolean loraAvailable = ensureLoraExtracted();

                // 3. Construire les options MediaPipe et créer la session
                LlmInference.LlmInferenceOptions.Builder optsBuilder =
                    LlmInference.LlmInferenceOptions.builder()
                        .setModelPath(modelFile.getAbsolutePath())
                        .setMaxTokens(maxTokens)
                        .setTemperature(TEMPERATURE)
                        .setTopK(TOP_K);

                if (loraAvailable) {
                    optsBuilder.setLoraPath(getLoraFile().getAbsolutePath());
                }

                LlmInference model = LlmInference.createFromOptions(
                    getContext(), optsBuilder.build()
                );

                synchronized (GemmaSynthesisPlugin.class) {
                    sModel      = model;
                    sLoraLoaded = loraAvailable;
                    sPreparing  = false;
                }

                JSObject result = new JSObject();
                result.put("ok",       true);
                result.put("loraUsed", sLoraLoaded);
                result.put("cached",   false);
                call.resolve(result);

            } catch (Exception e) {
                synchronized (GemmaSynthesisPlugin.class) { sPreparing = false; }
                call.reject("PREPARE_ERROR", e.getMessage(), e);
            }
        });
    }


    // ══════════════════════════════════════════════════════════════════════════
    //  generate
    // ══════════════════════════════════════════════════════════════════════════
    @PluginMethod
    public void generate(PluginCall call) {
        String system = call.getString("system", "");
        String user   = call.getString("user",   "");
        String type   = call.getString("type",   "synthesis");
        String lang   = call.getString("lang",   "fr");

        if (user == null || user.isEmpty()) {
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
            if (sModel == null) {
                try {
                    File modelFile = getModelFile();
                    if (!modelFile.exists() || modelFile.length() == 0) {
                        if (!downloadModel(modelFile)) {
                            call.reject("MODEL_NOT_READY",
                                "Modèle pas encore téléchargé — appelle prepareModel() d'abord.");
                            return;
                        }
                    }

                    boolean loraAvailable = ensureLoraExtracted();

                    LlmInference.LlmInferenceOptions.Builder optsBuilder =
                        LlmInference.LlmInferenceOptions.builder()
                            .setModelPath(modelFile.getAbsolutePath())
                            .setMaxTokens(MAX_TOKENS_SYNTHESIS)
                            .setTemperature(TEMPERATURE)
                            .setTopK(TOP_K);

                    if (loraAvailable) {
                        optsBuilder.setLoraPath(getLoraFile().getAbsolutePath());
                    }

                    LlmInference model = LlmInference.createFromOptions(
                        getContext(), optsBuilder.build()
                    );

                    synchronized (GemmaSynthesisPlugin.class) {
                        sModel      = model;
                        sLoraLoaded = loraAvailable;
                    }

                } catch (Exception e) {
                    call.reject("MODEL_NOT_READY", e.getMessage(), e);
                    return;
                }
            }

            try {
                // Construire le prompt system + user
                String contextualSystem;
                if (sLoraLoaded) {
                    // Avec LoRA, on peut utiliser le system fourni ou rien
                    contextualSystem = (system != null && !system.isEmpty()) ? system : "";
                } else if (system != null && !system.isEmpty()) {
                    contextualSystem = system;
                } else {
                    // Fallback vault → DoctrinePromptBuilder
                    contextualSystem = DoctrinePromptBuilder.buildSystemPrompt(
                        getContext(), finalProfile, lang
                    );
                }

                String fullPrompt = buildGemmaPrompt(contextualSystem, user);

                // Inférence synchrone MediaPipe
                String response = sModel.generateResponse(fullPrompt);

                JSObject result = new JSObject();
                result.put("ok",        true);
                result.put("synthesis", response.trim());
                result.put("local",     true);
                result.put("loraUsed",  sLoraLoaded);
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
            if (sModel != null) {
                try { sModel.close(); } catch (Exception ignored) {}
                sModel = null;
            }
            sLoraLoaded = false;
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
     * Télécharge le modèle .task depuis MODEL_URL vers le cache interne.
     * Bloque jusqu'à la fin du téléchargement.
     */
    private boolean downloadModel(File dest) throws IOException {
        sDownloading = true;
        try {
            dest.getParentFile().mkdirs();

            HttpURLConnection conn = (HttpURLConnection) new URL(MODEL_URL).openConnection();
            conn.setConnectTimeout(15_000);
            conn.setReadTimeout(30_000);
            conn.setInstanceFollowRedirects(true);
            conn.connect();

            int responseCode = conn.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("HTTP " + responseCode + " pour " + MODEL_URL);
            }

            long total = conn.getContentLengthLong();
            long downloaded = 0;

            try (InputStream in  = conn.getInputStream();
                 FileOutputStream out = new FileOutputStream(dest)) {
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) != -1) {
                    out.write(buf, 0, n);
                    downloaded += n;
                }
            }

            return dest.exists() && dest.length() > 0;
        } finally {
            sDownloading = false;
        }
    }

    /**
     * Copie le LoRA depuis assets/lora/ vers le cache interne.
     * Retourne true si dispo et non-vide.
     */
    private boolean ensureLoraExtracted() {
        File dest = getLoraFile();
        if (dest.exists() && dest.length() > 0) return true;

        try (InputStream is = getContext().getAssets().open(LORA_ASSET_PATH)) {
            dest.getParentFile().mkdirs();
            try (FileOutputStream fos = new FileOutputStream(dest)) {
                byte[] buf = new byte[8192];
                int n;
                while ((n = is.read(buf)) != -1) fos.write(buf, 0, n);
            }
            return dest.exists() && dest.length() > 0;
        } catch (IOException e) {
            return false;
        }
    }

    private File getModelFile() {
        return new File(getContext().getFilesDir(), "models/" + MODEL_FILENAME);
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
        // Ne PAS fermer sModel ici — static, survit aux recreations d'Activity.
        // Appeler unloadModel() explicitement si besoin de libérer la mémoire.
        super.handleOnDestroy();
    }
}
