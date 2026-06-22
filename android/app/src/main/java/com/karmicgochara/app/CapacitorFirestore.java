package com.karmicgochara.app;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.firebase.firestore.FirebaseFirestore;
import java.util.Map;

@CapacitorPlugin(name = "CapacitorFirestore")
public class CapacitorFirestore extends Plugin {

    @PluginMethod()
    public void getDocument(PluginCall call) {
        String collection = call.getString("collection");
        String docId = call.getString("docId");

        if (collection == null || docId == null) {
            call.reject("collection and docId are required");
            return;
        }

        FirebaseFirestore.getInstance()
            .collection(collection)
            .document(docId)
            .get()
            .addOnSuccessListener(doc -> {
                JSObject result = new JSObject();
                if (doc.exists()) {
                    Map<String, Object> data = doc.getData();
                    if (data != null) {
                        for (Map.Entry<String, Object> entry : data.entrySet()) {
                            result.put(entry.getKey(), entry.getValue());
                        }
                    }
                }
                JSObject wrapper = new JSObject();
                wrapper.put("data", doc.exists() ? result : null);
                call.resolve(wrapper);
            })
            .addOnFailureListener(e -> call.reject("Firestore Native Error: " + e.getMessage()));
    }
}
