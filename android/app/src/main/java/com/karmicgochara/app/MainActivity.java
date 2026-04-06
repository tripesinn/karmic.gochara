package com.karmicgochara.app;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(android.os.Bundle savedInstanceState) {
        // Plugin Gemma 3/4 — inférence locale via MediaPipe Tasks GenAI
        registerPlugin(GemmaSynthesisPlugin.class);
        // Plugin Unlock — achat "Supprimer les pubs" via Play Billing
        registerPlugin(UnlockPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
