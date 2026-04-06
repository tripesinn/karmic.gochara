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
 * Deux modèles selon la RAM disponible :
 *   E2B (~800 Mo, ≥ 4 Go RAM) → synthèse quotidienne  — rapide, offline
 *   E4B (~2 Go,  ≥ 6 Go RAM) → rapport annuel PDF     — qualité narrative
 *
 * Sélection automatique via getDeviceMemory() + choix utilisateur.
 * URLs à mettre à jour dès la sortie officielle Gemma 4 (Google AI Edge).
 */
@CapacitorPlugin(name = "GemmaSynthesis")
public class GemmaSynthesisPlugin extends Plugin {

    // ── Modèles disponibles ───────────────────────────────────────────────────
    // E2B — Gemma 4 2B int4 (~800 Mo) — synthèse quotidienne
    // En attendant Gemma 4 officiel : Gemma 3 1B (~400 Mo) en placeholder
    private static final String MODEL_2B_URL      =
            "https://huggingface.co/google/gemma-3-1b-it-mediapipe/resolve/main/gemma3-1b-it-cpu-int4.task";
    private static final String MODEL_2B_FILENAME = "gemma_e2b.task";
    private static final long   MODEL_2B_RAM_GB   = 4L;   // RAM minimum requise

    // E4B — Gemma 4 4B int4 (~2 Go) — rapport annuel
    // URL placeholder : à remplacer par l'URL officielle Gemma 4 4B quand disponible
    private static final String MODEL_4B_URL      =
            "https://huggingface.co/google/gemma-3-4b-it-mediapipe/resolve/main/gemma3-4b-it-cpu-int4.task";
    private static final String MODEL_4B_FILENAME = "gemma_e4b.task";
    private static final long   MODEL_4B_RAM_GB   = 6L;   // RAM minimum requise

    // ── Paramètres d'inférence ────────────────────────────────────────────────
    private static final int   MAX_TOKENS_SYNTHESIS = 2048;  // synthèse quotidienne
    private static final int   MAX_TOKENS_REPORT    = 4096;  // rapport annuel
    private static final float TEMPERATURE          = 0.7f;
    private static final int   TOP_K                = 40;

    // ── État runtime ──────────────────────────────────────────────────────────
    private LlmInference    llm2b       = null;  // E2B chargé
    private LlmInference    llm4b       = null;  // E4B chargé
    private ExecutorService executor    = Executors.newSingleThreadExecutor();


    // ── checkModels : état des deux modèles ───────────────────────────────────
    @PluginMethod
    public void checkModels(PluginCall call) {
        File f2b = getModelFile(MODEL_2B_FILENAME);
        File f4b = getModelFile(MODEL_4B_FILENAME);

        JSObject result = new JSObject();
        result.put("e2b_exists",  f2b.exists() && f2b.length() > 1_000_000L);
        result.put("e2b_loaded",  llm2b != null);
        result.put("e2b_sizeMb",  f2b.exists() ? f2b.length() / (1024 * 1024) : 0);
        result.put("e4b_exists",  f4b.exists() && f4b.length() > 1_000_000L);
        result.put("e4b_loaded",  llm4b != null);
        result.put("e4b_sizeMb",  f4b.exists() ? f4b.length() / (1024 * 1024) : 0);
        call.resolve(result);
    }

    // Rétrocompat avec l'ancien checkModel()
    @PluginMethod
    public void checkModel(PluginCall call) { checkModels(call); }


    // ── getDeviceMemory : RAM + recommandation modèle ─────────────────────────
    @PluginMethod
    public void getDeviceMemory(PluginCall call) {
        android.app.ActivityManager am = (android.app.ActivityManager)
                getContext().getSystemService(Context.ACTIVITY_SERVICE);
        android.app.ActivityManager.MemoryInfo memInfo =
                new android.app.ActivityManager.MemoryInfo();
        am.getMemoryInfo(memInfo);

        long totalRamGb   = memInfo.totalMem / (1024L * 1024L * 1024L);
        boolean can2b     = totalRamGb >= MODEL_2B_RAM_GB;
        boolean can4b     = totalRamGb >= MODEL_4B_RAM_GB;

        JSObject result = new JSObject();
        result.put("totalRamGb",   totalRamGb);
        result.put("sufficient",   can2b);          // rétrocompat
        result.put("can_e2b",      can2b);
        result.put("can_e4b",      can4b);
        result.put("recommended",  can4b ? "e4b" : can2b ? "e2b" : "cloud");
        call.resolve(result);
    }


    // ── loadModel : charge E2B ou E4B en mémoire ──────────────────────────────
    @PluginMethod
    public void loadModel(PluginCall call) {
        String type = call.getString("type", "e2b"); // "e2b" ou "e4b"
        boolean isE4b = "e4b".equals(type);

        File modelFile = getModelFile(isE4b ? MODEL_4B_FILENAME : MODEL_2B_FILENAME);
        int  maxTokens = isE4b ? MAX_TOKENS_REPORT : MAX_TOKENS_SYNTHESIS;

        if (!modelFile.exists()) {
            call.reject("MODEL_NOT_FOUND", "Modèle " + type.toUpperCase() + " non téléchargé.");
            return;
        }

        executor.execute(() -> {
            try {
                LlmInference existing = isE4b ? llm4b : llm2b;
                if (existing != null) { try { existing.close(); } catch (Exception ignored) {} }

                LlmInferenceOptions options = LlmInferenceOptions.builder()
                        .setModelPath(modelFile.getAbsolutePath())
                        .setMaxTokens(maxTokens)
                        .setTemperature(TEMPERATURE)
                        .setTopK(TOP_K)
                        .build();

                LlmInference llm = LlmInference.createFromOptions(getContext(), options);
                if (isE4b) llm4b = llm; else llm2b = llm;

                JSObject result = new JSObject();
                result.put("ok",   true);
                result.put("type", type);
                call.resolve(result);

            } catch (Exception e) {
                call.reject("LOAD_ERROR", "Erreur chargement " + type + " : " + e.getMessage(), e);
            }
        });
    }


    // ── generate : inférence avec le modèle approprié ────────────────────────
    @PluginMethod
    public void generate(PluginCall call) {
        String system = call.getString("system", "");
        String user   = call.getString("user",   "");
        String type   = call.getString("type",   "e2b"); // "e2b" ou "e4b"
        boolean isE4b = "e4b".equals(type);

        if (user == null || user.isEmpty()) {
            call.reject("INVALID_PROMPT", "Prompt vide.");
            return;
        }

        LlmInference llm = isE4b ? llm4b : llm2b;
        // Fallback : si E4B demandé mais non chargé, tente E2B
        if (llm == null && isE4b && llm2b != null) {
            llm = llm2b;
            type = "e2b";
        }
        if (llm == null) {
            call.reject("MODEL_NOT_LOADED", "Aucun modèle chargé. Appelle loadModel() d'abord.");
            return;
        }

        final LlmInference finalLlm = llm;
        final String       finalType = type;

        executor.execute(() -> {
            try {
                String fullPrompt = buildGemmaPrompt(system, user);
                String response   = finalLlm.generateResponse(fullPrompt);

                JSObject result = new JSObject();
                result.put("ok",        true);
                result.put("synthesis", response.trim());
                result.put("local",     true);
                result.put("model",     finalType);
                call.resolve(result);

            } catch (Exception e) {
                call.reject("INFERENCE_ERROR", "Erreur inférence : " + e.getMessage(), e);
            }
        });
    }


    // ── downloadModel : télécharge E2B ou E4B ────────────────────────────────
    @PluginMethod
    public void downloadModel(PluginCall call) {
        String type  = call.getString("type", "e2b");
        boolean isE4b = "e4b".equals(type);

        String url      = isE4b ? MODEL_4B_URL      : MODEL_2B_URL;
        String filename = isE4b ? MODEL_4B_FILENAME  : MODEL_2B_FILENAME;
        String label    = isE4b ? "Gemma E4B (~2 Go)" : "Gemma E2B (~800 Mo)";

        File modelFile = getModelFile(filename);
        if (modelFile.exists() && modelFile.length() > 1_000_000L) {
            JSObject result = new JSObject();
            result.put("ok",      true);
            result.put("already", true);
            result.put("type",    type);
            call.resolve(result);
            return;
        }

        try {
            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url))
                    .setTitle("Karmic Gochara — " + label)
                    .setDescription("Téléchargement du modèle IA local")
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
            result.put("type",       type);
            call.resolve(result);

        } catch (Exception e) {
            call.reject("DOWNLOAD_ERROR", e.getMessage(), e);
        }
    }


    // ── checkDownloadProgress ─────────────────────────────────────────────────
    @PluginMethod
    public void checkDownloadProgress(PluginCall call) {
        long downloadId = call.getLong("downloadId", -1L);
        if (downloadId == -1) { call.reject("INVALID_ID", "downloadId requis."); return; }

        DownloadManager dm = (DownloadManager)
                getContext().getSystemService(Context.DOWNLOAD_SERVICE);
        Cursor cursor = dm.query(new DownloadManager.Query().setFilterById(downloadId));

        JSObject result = new JSObject();
        if (cursor != null && cursor.moveToFirst()) {
            int statusIdx = cursor.getColumnIndex(DownloadManager.COLUMN_STATUS);
            int dlIdx     = cursor.getColumnIndex(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR);
            int totalIdx  = cursor.getColumnIndex(DownloadManager.COLUMN_TOTAL_SIZE_BYTES);

            int  status   = statusIdx >= 0 ? cursor.getInt(statusIdx)  : -1;
            long dlBytes  = dlIdx     >= 0 ? cursor.getLong(dlIdx)     : 0;
            long total    = totalIdx  >= 0 ? cursor.getLong(totalIdx)  : -1;
            int  progress = total > 0 ? (int)(dlBytes * 100 / total) : 0;

            result.put("status",   statusToString(status));
            result.put("progress", progress);
            result.put("dlMb",     dlBytes / (1024 * 1024));
            result.put("totalMb",  total   / (1024 * 1024));
            cursor.close();
        } else {
            result.put("status", "unknown");
            result.put("progress", 0);
        }
        call.resolve(result);
    }


    // ── unloadModel ───────────────────────────────────────────────────────────
    @PluginMethod
    public void unloadModel(PluginCall call) {
        String type   = call.getString("type", "all");
        if ("e2b".equals(type) || "all".equals(type)) {
            if (llm2b != null) { try { llm2b.close(); } catch (Exception ignored) {} llm2b = null; }
        }
        if ("e4b".equals(type) || "all".equals(type)) {
            if (llm4b != null) { try { llm4b.close(); } catch (Exception ignored) {} llm4b = null; }
        }
        JSObject result = new JSObject();
        result.put("ok", true);
        call.resolve(result);
    }


    // ── Helpers ───────────────────────────────────────────────────────────────
    private File getModelFile(String filename) {
        File dir = getContext().getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (dir == null) dir = getContext().getFilesDir();
        return new File(dir, filename);
    }

    /**
     * Format de prompt Gemma Instruct (Gemma 3 & 4) :
     * <start_of_turn>user\n{system}\n\n{user}<end_of_turn>\n<start_of_turn>model\n
     */
    private String buildGemmaPrompt(String system, String user) {
        StringBuilder sb = new StringBuilder("<start_of_turn>user\n");
        if (system != null && !system.isEmpty()) sb.append(system).append("\n\n");
        sb.append(user).append("<end_of_turn>\n<start_of_turn>model\n");
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
        if (llm2b != null) { try { llm2b.close(); } catch (Exception ignored) {} }
        if (llm4b != null) { try { llm4b.close(); } catch (Exception ignored) {} }
        super.handleOnDestroy();
    }
}
