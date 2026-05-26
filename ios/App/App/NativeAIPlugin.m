#import <Foundation/Foundation.h>
#import <Capacitor/Capacitor.h>

// Définir le plugin pour Capacitor
CAP_PLUGIN(NativeAIPlugin, "NativeAI",
    CAP_PLUGIN_METHOD(checkModels, CAPPluginReturnPromise);
    CAP_PLUGIN_METHOD(isAvailable, CAPPluginReturnPromise);
    CAP_PLUGIN_METHOD(generate, CAPPluginReturnPromise);
)
