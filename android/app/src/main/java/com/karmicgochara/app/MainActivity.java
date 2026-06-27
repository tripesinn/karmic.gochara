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

        super.onCreate(savedInstanceState);
    }
}
