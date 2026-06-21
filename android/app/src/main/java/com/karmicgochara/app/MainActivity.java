package com.karmicgochara.app;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(android.os.Bundle savedInstanceState) {
        // Plugin KarmicGoogleAuth — Google Sign-In via Credential Manager
        registerPlugin(KarmicGoogleAuthPlugin.class);
        // Plugin NativeAI — inférence locale via Apple Intelligence / Android AICore
        registerPlugin(NativeAIPlugin.class);
        // Plugin Unlock — achat "Supprimer les pubs" via Play Billing
        registerPlugin(UnlockPlugin.class);

        super.onCreate(savedInstanceState);
    }
}
