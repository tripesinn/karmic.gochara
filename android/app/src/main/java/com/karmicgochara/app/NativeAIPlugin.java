package com.karmicgochara.app;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "NativeAI")
public class NativeAIPlugin extends Plugin {

    @PluginMethod
    public void checkModels(PluginCall call) {
        JSObject ret = new JSObject();
        ret.put("loaded", false);
        call.resolve(ret);
    }

    @PluginMethod
    public void isAvailable(PluginCall call) {
        // TODO: Vérifier la disponibilité de Android AICore (Gemini Nano)
        JSObject ret = new JSObject();
        ret.put("available", false);
        call.resolve(ret);
    }

    @PluginMethod
    public void generate(PluginCall call) {
        String system = call.getString("system", "");
        String user = call.getString("user", "");

        // TODO: Appeler Android AICore pour générer le texte
        JSObject ret = new JSObject();
        ret.put("text", "TODO: Implémentation Android AICore manquante");
        ret.put("model", "android-aicore");
        call.resolve(ret);
    }
}
