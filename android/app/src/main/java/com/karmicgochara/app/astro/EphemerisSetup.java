package com.karmicgochara.app.astro;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;

/**
 * EphemerisSetup — Copie les fichiers d'éphémérides de assets/ vers le stockage interne.
 * À appeler une seule fois au démarrage (idempotent si les fichiers existent déjà).
 *
 * Fichiers attendus dans assets/ephemeris/ :
 *   sepl_18.se1  (~18 Mo) — planètes principales 1800-2399
 *   semo_18.se1  (~10 Mo) — Lune, Nœuds, Lilith
 *   seas_18.se1  (~2 Mo)  — Chiron et astéroïdes
 */
public final class EphemerisSetup {

    private static final String ASSET_DIR  = "ephemeris";
    private static final String[] EPH_FILES = {
        "sepl_18.se1",
        "semo_18.se1",
    };

    private EphemerisSetup() {}

    /**
     * Retourne le chemin du répertoire d'éphémérides dans le stockage interne.
     * Copie les fichiers depuis assets si nécessaire.
     * @throws Exception si un fichier est manquant dans les assets.
     */
    public static String getEphemerisPath(Context ctx) throws Exception {
        File ephDir = new File(ctx.getFilesDir(), ASSET_DIR);
        if (!ephDir.exists()) ephDir.mkdirs();

        AssetManager assets = ctx.getAssets();

        for (String filename : EPH_FILES) {
            File dest = new File(ephDir, filename);
            if (dest.exists()) continue;   // déjà copié

            String assetPath = ASSET_DIR + "/" + filename;
            try (InputStream in = assets.open(assetPath);
                 FileOutputStream out = new FileOutputStream(dest)) {
                byte[] buf = new byte[64 * 1024];
                int n;
                while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
            } catch (Exception e) {
                throw new Exception("Fichier d'éphéméride manquant : assets/" + assetPath
                    + ". Télécharge les fichiers SE depuis astro.com/swisseph/ae/", e);
            }
        }

        return ephDir.getAbsolutePath();
    }
}
