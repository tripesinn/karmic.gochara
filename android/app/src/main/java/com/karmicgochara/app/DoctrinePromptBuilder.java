package com.karmicgochara.app;

import android.content.Context;

import org.json.JSONObject;
import org.json.JSONException;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.List;

/**
 * DoctrinePromptBuilder — construit le prompt Edge AI compressé sur device.
 *
 * Budget total : ~400-450 tokens.
 *   - System prompt compressé : ~250 tokens (system_prompt_mobile.json)
 *   - Contexte nakshatra RAG  : ~50 tokens × 4 planètes = ~200 tokens
 *
 * Sources bundlées dans APK (assets/) :
 *   - system_prompt_mobile.json  — prompts FR/EN compressés
 *   - nakshatra_karma.json       — 27 nakshatras × 8 planètes
 *
 * Régénérer les assets après toute modif de doctrine.py :
 *   python export_mobile_assets.py
 */
public class DoctrinePromptBuilder {

    // Planètes par ordre de priorité doctrinale : ROM → RAM → Dharma → Épreuve → structure
    private static final List<String[]> PLANET_PRIORITY = Arrays.asList(
        new String[]{"ketu",    "ketu"},
        new String[]{"chiron",  "chiron"},
        new String[]{"rahu",    "rahu"},
        new String[]{"lilith",  "lilith"},
        new String[]{"saturn",  "saturn"},
        new String[]{"jupiter", "jupiter"}
    );

    private static final int MAX_PLANETS = 4;

    // Cache chargé une fois, réutilisé
    private static JSONObject _nakshatraCache = null;
    private static JSONObject _promptCache    = null;


    /**
     * Construit le prompt complet pour une synthèse Edge AI.
     *
     * @param context      Android context (pour lire les assets)
     * @param profile      JSONObject du profil utilisateur (contient ketu_nakshatra, etc.)
     * @param lang         "fr" ou "en"
     * @return             String prête à passer à GemmaSynthesisPlugin.generate()
     */
    public static String buildSystemPrompt(Context context, JSONObject profile, String lang) {
        String base    = getBasePrompt(context, lang);
        String naksCtx = getNakshatraContext(context, profile);

        if (naksCtx.isEmpty()) return base;
        return base + "\n\n" + naksCtx;
    }


    /**
     * Charge le system prompt compressé depuis assets/system_prompt_mobile.json.
     */
    public static String getBasePrompt(Context context, String lang) {
        try {
            JSONObject prompts = loadPromptCache(context);
            String key = "en".equals(lang) ? "en" : "fr";
            return prompts.optString(key, "");
        } catch (Exception e) {
            return "";
        }
    }


    /**
     * Construit le bloc nakshatra RAG pour les planètes clés du profil.
     * Retourne une string vide si aucun nakshatra reconnu.
     */
    public static String getNakshatraContext(Context context, JSONObject profile) {
        JSONObject nakshatraKarma = loadNakshatraCache(context);
        if (nakshatraKarma == null || profile == null) return "";

        StringBuilder sb = new StringBuilder();
        int count = 0;

        for (String[] entry : PLANET_PRIORITY) {
            if (count >= MAX_PLANETS) break;

            String planetKey = entry[0];
            String karmaKey  = entry[1];
            String nakKey    = planetKey + "_nakshatra";

            String nak = profile.optString(nakKey, "").trim();
            if (nak.isEmpty() || !nakshatraKarma.has(nak)) continue;

            try {
                JSONObject nakshatraEntry = nakshatraKarma.getJSONObject(nak);
                String text = nakshatraEntry.optString(karmaKey, "").trim();
                if (text.isEmpty()) continue;

                if (sb.length() == 0) sb.append("MEMOIRE NAKSHATRA :\n");
                sb.append("[").append(planetKey.toUpperCase())
                  .append(" \u00b7 ").append(nak).append("] ")
                  .append(text).append("\n");
                count++;

            } catch (JSONException ignored) {}
        }

        return sb.toString().trim();
    }


    // ── Chargement des assets avec cache ─────────────────────────────────────

    private static JSONObject loadNakshatraCache(Context context) {
        if (_nakshatraCache != null) return _nakshatraCache;
        String json = readAsset(context, "nakshatra_karma.json");
        if (json == null) return null;
        try {
            _nakshatraCache = new JSONObject(json);
            return _nakshatraCache;
        } catch (JSONException e) {
            return null;
        }
    }

    private static JSONObject loadPromptCache(Context context) throws JSONException {
        if (_promptCache != null) return _promptCache;
        String json = readAsset(context, "system_prompt_mobile.json");
        if (json == null) return new JSONObject();
        _promptCache = new JSONObject(json);
        return _promptCache;
    }

    private static String readAsset(Context context, String filename) {
        try (InputStream is = context.getAssets().open(filename);
             BufferedReader reader = new BufferedReader(new InputStreamReader(is, "UTF-8"))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) sb.append(line).append("\n");
            return sb.toString();
        } catch (IOException e) {
            return null;
        }
    }
}
