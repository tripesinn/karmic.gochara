import re

with open("android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "r") as f:
    content = f.read()

# Remove Environment, Settings, ContextCompat, Manifest, PackageManager
content = re.sub(r"import android\.os\.Environment;\n", "", content)
content = re.sub(r"import android\.provider\.Settings;\n", "", content)
content = re.sub(r"import androidx\.core\.content\.ContextCompat;\n", "", content)
content = re.sub(r"import android\.Manifest;\n", "", content)
content = re.sub(r"import android\.content\.pm\.PackageManager;\n", "", content)

# Add DocumentFile and ParcelFileDescriptor imports
imports = """import androidx.documentfile.provider.DocumentFile;
import android.os.ParcelFileDescriptor;
import android.content.SharedPreferences;
import java.io.OutputStream;
"""
content = content.replace("import android.content.Context;", "import android.content.Context;\n" + imports)

# Replace requestStoragePermission
content = re.sub(
    r"private boolean checkStoragePermission\(\) \{.*?\n    \}\n\n    @PluginMethod\n    public void requestStoragePermission\(PluginCall call\) \{.*?\n    \}\n\n    @ActivityCallback\n    private void storagePermResult\(PluginCall call, ActivityResult result\) \{.*?\n    \}",
    """private boolean hasStoredDocumentTree() {
        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        return prefs.getString("model_tree_uri", null) != null;
    }

    private DocumentFile getModelDocumentFile() {
        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        String uriStr = prefs.getString("model_tree_uri", null);
        if (uriStr == null) return null;
        Uri treeUri = Uri.parse(uriStr);
        DocumentFile dir = DocumentFile.fromTreeUri(getContext(), treeUri);
        if (dir == null || !dir.exists() || !dir.canRead()) return null;
        return dir.findFile(sModelFilename);
    }

    @PluginMethod
    public void requestStoragePermission(PluginCall call) {
        saveCall(call);
        if (hasStoredDocumentTree()) {
            JSObject res = new JSObject();
            res.put("ok", true);
            call.resolve(res);
            return;
        }
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(call, intent, "storagePermResult");
    }

    @ActivityCallback
    private void storagePermResult(PluginCall call, ActivityResult result) {
        if (call == null) return;
        boolean ok = false;
        if (result.getResultCode() == Activity.RESULT_OK) {
            Intent data = result.getData();
            if (data != null && data.getData() != null) {
                Uri treeUri = data.getData();
                getContext().getContentResolver().takePersistableUriPermission(treeUri,
                        Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                prefs.edit().putString("model_tree_uri", treeUri.toString()).apply();
                ok = true;
            }
        }
        JSObject res = new JSObject();
        res.put("ok", ok);
        call.resolve(res);
    }""",
    content,
    flags=re.DOTALL
)

# Replace getModelFile method
content = re.sub(
    r"private File getModelFile\(\) \{.*?\n    \}",
    "",
    content,
    flags=re.DOTALL
)

# Refactor checkAvailability
content = re.sub(
    r"if \(\!checkStoragePermission\(\)\) \{",
    "if (!hasStoredDocumentTree()) {",
    content
)

content = re.sub(
    r"File modelFile = getModelFile\(\);\n        if \(modelFile != null && modelFile\.exists\(\) && modelFile\.length\(\) > 0\)",
    "DocumentFile modelFile = getModelDocumentFile();\n        if (modelFile != null && modelFile.exists() && modelFile.length() > 0)",
    content
)

# Prepare model uses fd
content = re.sub(
    r"File modelFile = getModelFile\(\);\n        if \(modelFile == null \|\| !modelFile\.exists\(\)\) \{",
    """DocumentFile modelFile = getModelDocumentFile();
        if (modelFile == null || !modelFile.exists()) {""",
    content
)

content = re.sub(
    r"EngineConfig modelOpts = new EngineConfig\(\n                        modelFile\.getAbsolutePath\(\),",
    """ParcelFileDescriptor pfd = getContext().getContentResolver().openFileDescriptor(modelFile.getUri(), "r");
                int fd = pfd.getFd();
                String fdPath = "/proc/self/fd/" + fd;
                
                EngineConfig modelOpts = new EngineConfig(
                        fdPath,""",
    content
)

# And we have to handle pfd closure (wait, MediaPipe needs the fd open until Engine is destroyed, but Java PFD will close if GC'd? Let's hold a static reference).
content = re.sub(
    r"private static final AtomicReference<Conversation> sBaseConversationRef = new AtomicReference<>\(null\);",
    "private static final AtomicReference<Conversation> sBaseConversationRef = new AtomicReference<>(null);\n    private static ParcelFileDescriptor sModelPfd = null;",
    content
)

content = re.sub(
    r"int fd = pfd\.getFd\(\);",
    "sModelPfd = pfd;\n                int fd = pfd.getFd();",
    content
)

content = re.sub(
    r"if \(sEngineRef\.get\(\) != null\) \{.*?\}",
    "if (sEngineRef.get() != null) {\n            sEngineRef.get().close();\n            sEngineRef.set(null);\n        }\n        if (sModelPfd != null) {\n            try { sModelPfd.close(); } catch (Exception ignored) {}\n            sModelPfd = null;\n        }",
    content,
    flags=re.DOTALL
)

# We need to fix downloadModel
download_model_replacement = """DocumentFile modelFile = getModelDocumentFile();
                if (modelFile == null) {
                    SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                    String uriStr = prefs.getString("model_tree_uri", null);
                    if (uriStr != null) {
                        DocumentFile dir = DocumentFile.fromTreeUri(getContext(), Uri.parse(uriStr));
                        if (dir != null) {
                            modelFile = dir.createFile("application/octet-stream", sModelFilename);
                        }
                    }
                }
                
                if (modelFile == null) {
                    sDownloading = false;
                    call.reject("ERR_IO", "Cannot create file in the selected folder");
                    return;
                }
                
                try (OutputStream fos = getContext().getContentResolver().openOutputStream(modelFile.getUri())) {"""

content = re.sub(
    r"File destFile = getModelFile\(\);\n.*?try \(FileOutputStream fos = new FileOutputStream\(destFile\)\) \{",
    download_model_replacement,
    content,
    flags=re.DOTALL
)


content = re.sub(
    r"File modelFile = getModelFile\(\);\n                if \(modelFile \!= null && modelFile\.exists\(\)\) \{.*?\}",
    """DocumentFile modelFile = getModelDocumentFile();
                if (modelFile != null && modelFile.exists()) {
                    modelFile.delete();
                }""",
    content,
    flags=re.DOTALL
)

content = re.sub(
    r"File modelFile = getModelFile\(\);\n                    if \(modelFile != null && modelFile\.exists\(\)\) \{.*?\}",
    """DocumentFile modelFile = getModelDocumentFile();
                    if (modelFile != null && modelFile.exists()) {
                        modelFile.delete();
                    }""",
    content,
    flags=re.DOTALL
)

with open("android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "w") as f:
    f.write(content)
