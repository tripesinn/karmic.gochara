package com.karmicgochara.app;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(android.os.Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Plugin NativeAI — inférence locale via Apple Intelligence / Android AICore
        registerPlugin(NativeAIPlugin.class);
        // Plugin Unlock — achat "Supprimer les pubs" via Play Billing
        registerPlugin(UnlockPlugin.class);
    }
}
