package com.karmicgochara.app;

import android.app.DownloadManager;
import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.os.Environment;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import com.google.mediapipe.tasks.genai.llminference.LlmInference;
import com.google.mediapipe.tasks.genai.llminference.LlmInference.LlmInferenceOptions;

import java.io.File;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * GemmaSynthesisPlugin — Inférence locale Gemma 4 via MediaPipe Tasks GenAI
 *
 * Flow :
 *   1. JS appelle checkModel()     → le modèle est-il téléchargé ?
 *   2. Si non : JS appelle downloadModel() → télécharge via DownloadManager
 *   3. JS appelle generate(prompt) → inférence locale, retourne la synthèse
 *
 * Le modèle (~2 Go) est stocké dans :
 *   /Android/data/com.karmicgochara.app/files/gemma4.task
 *
 * Pour obtenir le fichier .task compatible MediaPipe :
 *   https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/android
 */
@CapacitorPlugin(name = "GemmaSynthesis")
public class GemmaSynthesisPlugin extends Plugin {

    // ── URL de téléchargement du modèle Gemma 3 (1B, int4, CPU) ─────────────
    // Gemma 3 1B — ~400 Mo, fonctionne sur CPU, compatible MediaPipe 0.10.24+
    // Remplacer par gemma3-4b-it-cpu-int4.task (~1.5 Go) pour plus de qualité.
    // Docs : https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/android
    private static final String MODEL_DOWNLOAD_URL =
            "https://storage.googleapis.com/mediapipe-models/llm_inference/gemma3-1b-it-cpu-int4/float32/1/gemma3-1b-it-cpu-int4.task";

    private static final String MODEL_FILENAME = "gemma3.task";
    private static final int    MAX_TOKENS     = 2048;
    private static final float  TEMPERATURE    = 0.7f;
    private static final int    TOP_K          = 40;

    private LlmInference    llmInference = null;
    private boolean         modelLoaded  = false;
    private ExecutorService executor     = Executors.newSingleThreadExecutor();


    // ── Chemin du fichier modèle ──────────────────────────────────────────────
    private File getModelFile() {
        File dir = getContext().getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (dir == null) {
            dir = getContext().getFilesDir();
        }
        return new File(dir, MODEL_FILENAME);
    }


    // ── checkModel : le modèle est-il présent et chargé ? ────────────────────
    @PluginMethod
    public void checkModel(PluginCall call) {
        File modelFile = getModelFile();
        boolean exists = modelFile.exists() && modelFile.length() > 1_000_000L;

        JSObject result = new JSObject();
        result.put("exists", exists);
        result.put("loaded", modelLoaded);
        result.put("path",   exists ? modelFile.getAbsolutePath() : "");
        result.put("sizeMb", exists ? modelFile.length() / (1024 * 1024) : 0);
        call.resolve(result);
    }


    // ── loadModel : charge le modèle en mémoire ───────────────────────────────
    @PluginMethod
    public void loadModel(PluginCall call) {
        File modelFile = getModelFile();
        if (!modelFile.exists()) {
            call.reject("MODEL_NOT_FOUND", "Le fichier modèle n'est pas téléchargé.");
            return;
        }

        executor.execute(() -> {
            try {
                if (llmInference != null) {
                    llmInference.close();
                    llmInference = null;
                }

                LlmInferenceOptions options = LlmInferenceOptions.builder()
                        .setModelPath(modelFile.getAbsolutePath())
                        .setMaxTokens(MAX_TOKENS)
                        .setTemperature(TEMPERATURE)
                        .setTopK(TOP_K)
                        .build();

                llmInference = LlmInference.createFromOptions(getContext(), options);
                modelLoaded  = true;

                JSObject result = new JSObject();
                result.put("ok", true);
                call.resolve(result);

            } catch (Exception e) {
                modelLoaded = false;
                call.reject("LOAD_ERROR", "Erreur chargement modèle : " + e.getMessage(), e);
            }
        });
    }


    // ── generate : inférence locale ───────────────────────────────────────────
    @PluginMethod
    public void generate(PluginCall call) {
        String systemPrompt = call.getString("system", "");
        String userPrompt   = call.getString("user",   "");

        if (userPrompt == null || userPrompt.isEmpty()) {
            call.reject("INVALID_PROMPT", "Le prompt ne peut pas être vide.");
            return;
        }
        if (!modelLoaded || llmInference == null) {
            call.reject("MODEL_NOT_LOADED", "Le modèle n'est pas chargé. Appelle loadModel() d'abord.");
            return;
        }

        // Gemma 4 utilise le format de chat standard
        // system et user sont concaténés dans un seul prompt structuré
        String fullPrompt = buildGemmaPrompt(systemPrompt, userPrompt);

        executor.execute(() -> {
            try {
                String response = llmInference.generateResponse(fullPrompt);

                JSObject result = new JSObject();
                result.put("ok",       true);
                result.put("synthesis", response.trim());
                result.put("local",    true);
                call.resolve(result);

            } catch (Exception e) {
                call.reject("INFERENCE_ERROR", "Erreur inférence : " + e.getMessage(), e);
            }
        });
    }


    // ── downloadModel : lance le téléchargement via DownloadManager ───────────
    @PluginMethod
    public void downloadModel(PluginCall call) {
        File modelFile = getModelFile();
        if (modelFile.exists() && modelFile.length() > 1_000_000L) {
            JSObject result = new JSObject();
            result.put("ok",      true);
            result.put("already", true);
            call.resolve(result);
            return;
        }

        try {
            DownloadManager.Request request = new DownloadManager.Request(
                    Uri.parse(MODEL_DOWNLOAD_URL))
                    .setTitle("Gemma 4 — Karmic Gochara")
                    .setDescription("Téléchargement du modèle IA local (~2 Go)")
                    .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    .setDestinationUri(Uri.fromFile(modelFile))
                    .setAllowedOverMetered(false)
                    .setAllowedOverRoaming(false);

            DownloadManager dm = (DownloadManager)
                    getContext().getSystemService(Context.DOWNLOAD_SERVICE);
            long downloadId = dm.enqueue(request);

            JSObject result = new JSObject();
            result.put("ok",         true);
            result.put("downloadId", downloadId);
            result.put("already",    false);
            call.resolve(result);

        } catch (Exception e) {
            call.reject("DOWNLOAD_ERROR", "Erreur lancement téléchargement : " + e.getMessage(), e);
        }
    }


    // ── checkDownloadProgress : état du téléchargement ───────────────────────
    @PluginMethod
    public void checkDownloadProgress(PluginCall call) {
        long downloadId = call.getLong("downloadId", -1L);
        if (downloadId == -1) {
            call.reject("INVALID_ID", "downloadId requis.");
            return;
        }

        DownloadManager dm = (DownloadManager)
                getContext().getSystemService(Context.DOWNLOAD_SERVICE);
        DownloadManager.Query query = new DownloadManager.Query().setFilterById(downloadId);
        Cursor cursor = dm.query(query);

        JSObject result = new JSObject();
        if (cursor != null && cursor.moveToFirst()) {
            int statusIdx   = cursor.getColumnIndex(DownloadManager.COLUMN_STATUS);
            int dlIdx       = cursor.getColumnIndex(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR);
            int totalIdx    = cursor.getColumnIndex(DownloadManager.COLUMN_TOTAL_SIZE_BYTES);

            int    status    = statusIdx  >= 0 ? cursor.getInt(statusIdx)  : -1;
            long   dlBytes   = dlIdx      >= 0 ? cursor.getLong(dlIdx)     : 0;
            long   total     = totalIdx   >= 0 ? cursor.getLong(totalIdx)  : -1;
            int    progress  = (total > 0) ? (int)(dlBytes * 100 / total) : 0;

            result.put("status",   statusToString(status));
            result.put("progress", progress);
            result.put("dlMb",     dlBytes / (1024 * 1024));
            result.put("totalMb",  total   / (1024 * 1024));
            cursor.close();
        } else {
            result.put("status",   "unknown");
            result.put("progress", 0);
        }
        call.resolve(result);
    }


    // ── unloadModel : libère la mémoire ───────────────────────────────────────
    @PluginMethod
    public void unloadModel(PluginCall call) {
        if (llmInference != null) {
            try { llmInference.close(); } catch (Exception ignored) {}
            llmInference = null;
        }
        modelLoaded = false;
        JSObject result = new JSObject();
        result.put("ok", true);
        call.resolve(result);
    }


    // ── Helpers ───────────────────────────────────────────────────────────────
    /**
     * Formate le prompt au format Gemma 4 / Gemma Instruct.
     * Format : <start_of_turn>user\n{system}\n\n{user}<end_of_turn>\n<start_of_turn>model\n
     */
    private String buildGemmaPrompt(String system, String user) {
        StringBuilder sb = new StringBuilder();
        if (system != null && !system.isEmpty()) {
            sb.append("<start_of_turn>user\n").append(system).append("\n\n");
        } else {
            sb.append("<start_of_turn>user\n");
        }
        sb.append(user);
        sb.append("<end_of_turn>\n<start_of_turn>model\n");
        return sb.toString();
    }

    private String statusToString(int status) {
        switch (status) {
            case DownloadManager.STATUS_PENDING:    return "pending";
            case DownloadManager.STATUS_RUNNING:    return "running";
            case DownloadManager.STATUS_PAUSED:     return "paused";
            case DownloadManager.STATUS_SUCCESSFUL: return "success";
            case DownloadManager.STATUS_FAILED:     return "failed";
            default:                                return "unknown";
        }
    }

    @Override
    protected void handleOnDestroy() {
        executor.shutdown();
        if (llmInference != null) {
            try { llmInference.close(); } catch (Exception ignored) {}
        }
        super.handleOnDestroy();
    }
}
