package com.karmicgochara.app;

import android.content.Context;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import org.json.JSONObject;

import com.google.mlkit.genai.inference.GenerativeModel;
import com.google.mlkit.genai.inference.GenerativeModelOptions;
import com.google.mlkit.genai.inference.ContentGenerationRequest;
import com.google.mlkit.genai.inference.InferenceFeature;
import com.google.mlkit.genai.inference.LoraWeightsParameters;
import com.google.mlkit.genai.inference.DownloadConfig;
import com.google.mlkit.genai.inference.InferenceAvailability;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * GemmaSynthesisPlugin — Inférence locale Gemma via ML Kit GenAI APIs.
 *
 * Architecture :
 *   - Modèle de base : géré par le système (AICore / Play Services), pas bundlé dans l'APK.
 *   - LoRA adapter   : assets/lora/doctrine_adapter.bin — doctrine karmique @siderealAstro13
 *                      baked dans les poids, contexte réduit de ~4000 → ~400 tokens.
 *
 * Capacitor methods exposés au JS :
 *   checkAvailability()  → {available: bool, status: string, downloading: bool}
 *   prepareModel()       → télécharge le modèle si nécessaire, charge le LoRA
 *   generate(system, user, type) → {synthesis: string, local: true, loraUsed: bool}
 *   unloadModel()        → libère la mémoire
 *   getDeviceMemory()    → {totalRamGb, sufficient, recommended}
 */
@CapacitorPlugin(name = "GemmaSynthesis")
public class GemmaSynthesisPlugin extends Plugin {

    // Fichier LoRA bundlé dans l'APK (assets/lora/)
    private static final String LORA_ASSET_PATH    = "lora/doctrine_adapter.bin";
    private static final String LORA_CACHE_FILENAME = "doctrine_adapter.bin";

    // Paramètres d'inférence
    private static final int MAX_TOKENS_SYNTHESIS = 2048;
    private static final int MAX_TOKENS_REPORT    = 4096;

    // État runtime — static pour survivre aux recreations d'Activity
    private static GenerativeModel  sModel      = null;
    private static boolean          sLoraLoaded = false;
    private static boolean          sPreparing  = false;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();


    // ── checkAvailability : modèle disponible sur ce device ? ────────────────
    @PluginMethod
    public void checkAvailability(PluginCall call) {
        GenerativeModelOptions opts = buildOptions(false, MAX_TOKENS_SYNTHESIS);
        GenerativeModel.checkFeatureAvailability(getContext(), opts)
            .addOnSuccessListener(status -> {
                JSObject result = new JSObject();
                switch (status) {
                    case InferenceAvailability.AVAILABLE:
                        result.put("available",   true);
                        result.put("status",      "available");
                        result.put("downloading", false);
                        break;
                    case InferenceAvailability.DOWNLOADABLE:
                        result.put("available",   false);
                        result.put("status",      "downloadable");
                        result.put("downloading", false);
                        break;
                    case InferenceAvailability.DOWNLOADING:
                        result.put("available",   false);
                        result.put("status",      "downloading");
                        result.put("downloading", true);
                        break;
                    default:
                        result.put("available",   false);
                        result.put("status",      "unavailable");
                        result.put("downloading", false);
                }
                call.resolve(result);
            })
            .addOnFailureListener(e ->
                call.reject("CHECK_ERROR", e.getMessage(), e)
            );
    }


    // ── prepareModel : télécharge le modèle si besoin + charge le LoRA ───────
    @PluginMethod
    public void prepareModel(PluginCall call) {
        if (sModel != null) {
            // Déjà chargé (survit aux recreations d'Activity)
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
                boolean loraAvailable = ensureLoraExtracted();
                GenerativeModelOptions opts = buildOptions(loraAvailable, maxTokens);

                GenerativeModel.createOrDownload(getContext(), opts)
                    .addOnSuccessListener(m -> {
                        synchronized (GemmaSynthesisPlugin.class) {
                            sModel      = m;
                            sLoraLoaded = loraAvailable;
                            sPreparing  = false;
                        }
                        JSObject result = new JSObject();
                        result.put("ok",       true);
                        result.put("loraUsed", sLoraLoaded);
                        result.put("cached",   false);
                        call.resolve(result);
                    })
                    .addOnFailureListener(e -> {
                        synchronized (GemmaSynthesisPlugin.class) { sPreparing = false; }
                        call.reject("PREPARE_ERROR", e.getMessage(), e);
                    });

            } catch (Exception e) {
                synchronized (GemmaSynthesisPlugin.class) { sPreparing = false; }
                call.reject("PREPARE_ERROR", e.getMessage(), e);
            }
        });
    }


    // ── generate : lazy-init + inférence ─────────────────────────────────────
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
        JSONObject profile;
        try { profile = new JSONObject(profileJs.toString()); }
        catch (Exception e) { profile = new JSONObject(); }
        final JSONObject finalProfile = profile;

        executor.execute(() -> {
            // Lazy-init : prépare le modèle si pas encore chargé
            if (sModel == null) {
                try {
                    boolean loraAvailable = ensureLoraExtracted();
                    GenerativeModelOptions opts = buildOptions(loraAvailable, MAX_TOKENS_SYNTHESIS);
                    // createOrDownload bloquant simulé via CountDownLatch
                    java.util.concurrent.CountDownLatch latch = new java.util.concurrent.CountDownLatch(1);
                    final Exception[] loadError = {null};

                    GenerativeModel.createOrDownload(getContext(), opts)
                        .addOnSuccessListener(m -> {
                            synchronized (GemmaSynthesisPlugin.class) {
                                sModel      = m;
                                sLoraLoaded = loraAvailable;
                            }
                            latch.countDown();
                        })
                        .addOnFailureListener(e -> {
                            loadError[0] = e;
                            latch.countDown();
                        });

                    latch.await(30, java.util.concurrent.TimeUnit.SECONDS);

                    if (loadError[0] != null || sModel == null) {
                        call.reject("MODEL_NOT_READY", "Modèle non disponible — vérifie la connexion.");
                        return;
                    }
                } catch (Exception e) {
                    call.reject("MODEL_NOT_READY", e.getMessage(), e);
                    return;
                }
            }

            try {
                String contextualSystem;
                if (sLoraLoaded) {
                    contextualSystem = (system != null && !system.isEmpty()) ? system : "";
                } else if (system != null && !system.isEmpty()) {
                    contextualSystem = system;
                } else {
                    contextualSystem = DoctrinePromptBuilder.buildSystemPrompt(
                        getContext(), finalProfile, lang
                    );
                }

                String fullPrompt = buildGemmaPrompt(contextualSystem, user);

                ContentGenerationRequest request = ContentGenerationRequest.builder()
                    .setContents(fullPrompt)
                    .build();

                sModel.generateContent(request)
                    .addOnSuccessListener(response -> {
                        JSObject result = new JSObject();
                        result.put("ok",        true);
                        result.put("synthesis", response.getText().trim());
                        result.put("local",     true);
                        result.put("loraUsed",  sLoraLoaded);
                        result.put("type",      type);
                        call.resolve(result);
                    })
                    .addOnFailureListener(e ->
                        call.reject("INFERENCE_ERROR", e.getMessage(), e)
                    );

            } catch (Exception e) {
                call.reject("INFERENCE_ERROR", e.getMessage(), e);
            }
        });
    }


    // ── unloadModel : libère la mémoire ───────────────────────────────────────
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


    // ── getDeviceMemory : RAM + recommandation ────────────────────────────────
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
        result.put("recommended", totalRamGb >= 6 ? "full" : totalRamGb >= 4 ? "standard" : "unavailable");
        call.resolve(result);
    }


    // ── checkModel / checkModels : rétrocompat JS ─────────────────────────────
    @PluginMethod
    public void checkModel(PluginCall call)  { checkAvailability(call); }
    @PluginMethod
    public void checkModels(PluginCall call) { checkAvailability(call); }


    // ── Helpers privés ────────────────────────────────────────────────────────

    /**
     * Construit les options ML Kit GenAI.
     * Si le LoRA est disponible en cache, l'injecte dans les options.
     */
    private GenerativeModelOptions buildOptions(boolean withLora, int maxTokens) {
        GenerativeModelOptions.Builder builder = GenerativeModelOptions.builder()
            .setInferenceFeature(InferenceFeature.TEXT_GENERATION)
            .setMaxTokens(maxTokens);

        if (withLora) {
            File loraFile = getLoraFile();
            if (loraFile.exists() && loraFile.length() > 0) {
                builder.setLoraWeightsParameters(
                    LoraWeightsParameters.builder()
                        .setWeightsFilePath(loraFile.getAbsolutePath())
                        .build()
                );
            }
        }

        return builder.build();
    }

    /**
     * Copie le LoRA depuis assets/lora/ vers le cache interne au premier lancement.
     * Retourne true si le fichier est disponible et non vide.
     */
    private boolean ensureLoraExtracted() {
        File dest = getLoraFile();
        if (dest.exists() && dest.length() > 0) return true;

        try (InputStream is = getContext().getAssets().open(LORA_ASSET_PATH)) {
            dest.getParentFile().mkdirs();
            java.io.FileOutputStream fos = new java.io.FileOutputStream(dest);
            byte[] buf = new byte[8192];
            int n;
            while ((n = is.read(buf)) != -1) fos.write(buf, 0, n);
            fos.close();
            return dest.exists() && dest.length() > 0;
        } catch (IOException e) {
            // LoRA non bundlé — fallback vault en contexte
            return false;
        }
    }

    private File getLoraFile() {
        File cacheDir = new File(getContext().getFilesDir(), "lora");
        return new File(cacheDir, LORA_CACHE_FILENAME);
    }

    /**
     * Fallback : charge le vault depuis assets/karmic_vault/ si LoRA absent.
     * Utilisé uniquement si lora_adapter.bin n'est pas encore bundlé.
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
        // Ne pas fermer sModel ici — il est static et doit survivre aux recreations d'Activity.
        // Appeler unloadModel() explicitement si on veut libérer la mémoire.
        super.handleOnDestroy();
    }
}
