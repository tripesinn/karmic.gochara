package com.karmicgochara.app;

import com.getcapacitor.BridgeActivity;
import java.io.File;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(android.os.Bundle savedInstanceState) {
        // Plugin KarmicGoogleAuth — Google Sign-In via Credential Manager
        registerPlugin(KarmicGoogleAuthPlugin.class);
        // Plugin CapacitorFirestore — Bridge Firestore
        registerPlugin(CapacitorFirestore.class);
        // Plugin NativeAI — inférence locale via Apple Intelligence / Android AICore
        registerPlugin(NativeAIPlugin.class);
        // Plugin GemmaSynthesis — inférence locale Gemma via MediaPipe
        registerPlugin(GemmaSynthesisPlugin.class);

        // Plugin Unlock — achat "Supprimer les pubs" via Play Billing
        registerPlugin(UnlockPlugin.class);
        // Plugin AstroCalc — moteur Swiss Ephemeris local
        registerPlugin(AstroCalcPlugin.class);
        // Plugin PlayIntegrity — StandardIntegrityToken posté à /login_firebase
        // EXCLU TEMPORAIREMENT : commit ed812c5 cassé (play-core retiré de Maven,
        // play-integrity:1.4.0 ne se résout pas). À réparer séparément.
        // registerPlugin(PlayIntegrityPlugin.class);

        super.onCreate(savedInstanceState);

        // Activer le zoom (pinch-to-zoom) sur tablette/mobile
        try {
            android.webkit.WebView webView = this.bridge.getWebView();
            if (webView != null) {
                android.webkit.WebSettings settings = webView.getSettings();
                settings.setBuiltInZoomControls(true);
                settings.setDisplayZoomControls(false); // Masque les boutons +/- inesthétiques
                settings.setSupportZoom(true);
            }
        } catch (Exception e) {
            android.util.Log.e("MainActivity", "Erreur configuration zoom WebView", e);
        }
    }
}
