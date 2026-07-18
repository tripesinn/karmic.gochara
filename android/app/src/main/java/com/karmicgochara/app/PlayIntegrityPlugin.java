package com.karmicgochara.app;

import android.content.Context;
import android.util.Log;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import com.google.android.play.core.integrity.IntegrityManagerFactory;
import com.google.android.play.core.integrity.StandardIntegrityManager;
import com.google.android.play.core.integrity.StandardIntegrityManager.StandardIntegrityTokenProvider;
import com.google.android.play.core.integrity.StandardIntegrityManager.StandardIntegrityTokenRequest;
import com.google.android.play.core.integrity.StandardIntegrityManager.PrepareIntegrityTokenRequest;

import java.util.concurrent.atomic.AtomicReference;

/**
 * PlayIntegrityPlugin — génère un StandardIntegrityToken au login natif.
 *
 * Le token (opaque, signé par Google Play) est renvoyé au web, qui le poste à
 * /login_firebase. Le backend (gochara-api) le décode via decodeIntegrityToken
 * (service account play-integrity-decoder) et refuse la session si invalide.
 *
 * API : com.google.android.play:integrity:1.4.0 (package public
 * com.google.android.play.core.integrity.*, identique à l'ancien play-core).
 * Changements vs play-core :
 *   - StandardIntegrityManager est une INTERFACE ; on l'obtient via
 *     IntegrityManagerFactory.createStandard(context).
 *   - prepareIntegrityToken() prend un PrepareIntegrityTokenRequest avec
 *     setCloudProjectNumber(long) (le project number GCP, plus de nonce).
 *   - request() prend un StandardIntegrityTokenRequest avec setRequestHash(String)
 *     (empreinte de la requête à sécuriser, plus de nonce).
 *
 * cloudProjectNumber : 732214018947 (karmic-gochara-cloud, depuis google-services.json).
 *
 * Désactivable : si provider non prêt (build/test), on renvoie un token vide pour
 * ne pas bloquer le login (backend ignore si PLAY_INTEGRITY_ENABLED=false).
 */
@CapacitorPlugin(name = "PlayIntegrity")
public class PlayIntegrityPlugin extends Plugin {

    private static final String TAG = "PlayIntegrity";
    // GCP cloud project number (karmic-gochara-cloud) — requis par l'API 1.4.0.
    private static final long CLOUD_PROJECT_NUMBER = 732214018947L;
    private final AtomicReference<StandardIntegrityTokenProvider> providerRef =
            new AtomicReference<>();

    @Override
    public void load() {
        try {
            Context ctx = getContext();
            StandardIntegrityManager manager =
                    IntegrityManagerFactory.createStandard(ctx);
            PrepareIntegrityTokenRequest request =
                    PrepareIntegrityTokenRequest.builder()
                            .setCloudProjectNumber(CLOUD_PROJECT_NUMBER)
                            .build();
            manager.prepareIntegrityToken(request)
                    .addOnSuccessListener(provider -> {
                        providerRef.set(provider);
                        Log.i(TAG, "StandardIntegrityTokenProvider prêt");
                    })
                    .addOnFailureListener(e -> {
                        Log.w(TAG, "prepareIntegrityToken échoué: " + e.getMessage());
                    });
        } catch (Exception e) {
            Log.w(TAG, "load: impossible d'init Play Integrity: " + e.getMessage());
        }
    }

    @PluginMethod()
    public void getIntegrityToken(PluginCall call) {
        StandardIntegrityTokenProvider provider = providerRef.get();
        if (provider == null) {
            // Provider pas prêt (ou non natif) -> renvoie vide, backend ignore si flag off
            Log.w(TAG, "getIntegrityToken: provider non prêt -> token vide");
            JSObject ret = new JSObject();
            ret.put("token", "");
            call.resolve(ret);
            return;
        }

        // requestHash = empreinte opaque de la requête à sécuriser (nonce-style).
        // On utilise un hash hex aléatoire de 32 octets (recommandé par Google).
        String requestHash = generateNonce();
        StandardIntegrityTokenRequest request =
                StandardIntegrityTokenRequest.builder().setRequestHash(requestHash).build();

        provider.request(request).addOnSuccessListener(token -> {
            JSObject ret = new JSObject();
            ret.put("token", token.token());
            call.resolve(ret);
        }).addOnFailureListener(e -> {
            Log.w(TAG, "request IntegrityToken échoué: " + e.getMessage());
            // Fail soft : token vide plutôt que reject (backend gère le refus si flag on)
            JSObject ret = new JSObject();
            ret.put("token", "");
            call.resolve(ret);
        });
    }

    private String generateNonce() {
        // nonce/hash = hex aléatoire (min 16 bytes recommandés par Google)
        java.security.SecureRandom sr = new java.security.SecureRandom();
        byte[] bytes = new byte[32];
        sr.nextBytes(bytes);
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
