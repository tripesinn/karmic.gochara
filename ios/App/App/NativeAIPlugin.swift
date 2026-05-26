import Foundation
import Capacitor

@objc(NativeAIPlugin)
public class NativeAIPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "NativeAIPlugin"
    public let jsName = "NativeAI"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "checkModels", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "isAvailable", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "generate", returnType: CAPPluginReturnPromise)
    ]
    
    @objc func checkModels(_ call: CAPPluginCall) {
        call.resolve(["loaded": false])
    }
    
    @objc func isAvailable(_ call: CAPPluginCall) {
        // TODO: Vérifier la disponibilité d'Apple Intelligence ou de MLX
        call.resolve(["available": false])
    }
    
    @objc func generate(_ call: CAPPluginCall) {
        let system = call.getString("system") ?? ""
        let user = call.getString("user") ?? ""
        
        // TODO: Appeler Apple Intelligence / MLX pour générer le texte
        call.resolve([
            "text": "TODO: Implémentation Apple Intelligence manquante",
            "model": "apple-intelligence"
        ])
    }
}
