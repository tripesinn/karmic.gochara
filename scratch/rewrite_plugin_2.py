import re

with open("android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "r") as f:
    content = f.read()

# 1. Add Environment import
if "import android.os.Environment;" not in content:
    content = content.replace("import android.content.Context;", "import android.content.Context;\nimport android.os.Environment;\nimport android.content.SharedPreferences;\nimport android.os.ParcelFileDescriptor;")

# 2. Modify getModelFile to point to Downloads
content = re.sub(
    r"private File getModelFile\(\) \{.*?\n    \}",
    """private File getModelFile() {
        File dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        if (!dir.exists()) dir.mkdirs();
        return new File(dir, sModelFilename);
    }""",
    content,
    flags=re.DOTALL
)

# 3. Add sModelPfd
if "private static ParcelFileDescriptor sModelPfd = null;" not in content:
    content = re.sub(
        r"private static final AtomicReference<Conversation> sBaseConversationRef = new AtomicReference<>\(null\);",
        "private static final AtomicReference<Conversation> sBaseConversationRef = new AtomicReference<>(null);\n    private static ParcelFileDescriptor sModelPfd = null;",
        content
    )

# 4. Modify checkAvailability
content = re.sub(
    r"File modelFile = getModelFile\(\);\n\s*if \(modelFile\.exists\(\) && modelFile\.length\(\) > 0\)",
    """SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        String customUriStr = prefs.getString("custom_model_uri", null);
        File modelFile = getModelFile();
        boolean isAvailable = false;
        if (customUriStr != null) {
            try {
                ParcelFileDescriptor pfd = getContext().getContentResolver().openFileDescriptor(Uri.parse(customUriStr), "r");
                if (pfd != null) {
                    isAvailable = pfd.getStatSize() > 0;
                    pfd.close();
                }
            } catch (Exception e) {}
        }
        if (!isAvailable && modelFile.exists() && modelFile.length() > 0) {
            isAvailable = true;
        }

        if (isAvailable)""",
    content
)

# 5. Modify isModelDownloaded and getModelStatus similarly
# We will just write a helper method getModelSize()
content = re.sub(
    r"private File getModelFile\(\) \{",
    """private long getModelSize() {
        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
        String customUriStr = prefs.getString("custom_model_uri", null);
        if (customUriStr != null) {
            try {
                ParcelFileDescriptor pfd = getContext().getContentResolver().openFileDescriptor(Uri.parse(customUriStr), "r");
                if (pfd != null) {
                    long size = pfd.getStatSize();
                    pfd.close();
                    if (size > 0) return size;
                }
            } catch (Exception e) {}
        }
        File f = getModelFile();
        return f.exists() ? f.length() : 0;
    }

    private File getModelFile() {""",
    content
)

content = re.sub(
    r"File modelFile = getModelFile\(\);\n\s*JSObject result = new JSObject\(\);\n\s*result\.put\(\"downloaded\", modelFile\.exists\(\) && modelFile\.length\(\) > 0\);\n\s*result\.put\(\"modelId\", sModelFilename\);\n\s*result\.put\(\"sizeBytes\", modelFile\.exists\(\) \? modelFile\.length\(\) : 0\);",
    """JSObject result = new JSObject();
        long size = getModelSize();
        result.put("downloaded", size > 0);
        result.put("modelId", sModelFilename);
        result.put("sizeBytes", size);""",
    content
)

content = re.sub(
    r"File modelFile = getModelFile\(\);\n\s*JSObject result = new JSObject\(\);\n\s*result\.put\(\"downloaded\", modelFile\.exists\(\) && modelFile\.length\(\) > 0\);\n\s*call\.resolve\(result\);",
    """JSObject result = new JSObject();
        result.put("downloaded", getModelSize() > 0);
        call.resolve(result);""",
    content
)

# 6. Modify selectLocalModel / pickModelResult
content = re.sub(
    r"if \(uri != null\) \{.*?sDownloading = false;\n\s*JSObject res = new JSObject\(\);\n\s*res\.put\(\"ok\", true\);\n\s*call\.resolve\(res\);.*?\} catch \(Exception e\)",
    """if (uri != null) {
                getContext().getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                prefs.edit().putString("custom_model_uri", uri.toString()).apply();
                
                JSObject res = new JSObject();
                res.put("ok", true);
                call.resolve(res);
            } catch (Exception e)""",
    content,
    flags=re.DOTALL
)

# 7. Modify prepareModel to use FD if available
prepare_replacement = """String modelPath = null;
                SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                String customUriStr = prefs.getString("custom_model_uri", null);
                
                if (customUriStr != null) {
                    try {
                        sModelPfd = getContext().getContentResolver().openFileDescriptor(Uri.parse(customUriStr), "r");
                        if (sModelPfd != null) {
                            modelPath = "/proc/self/fd/" + sModelPfd.getFd();
                        }
                    } catch (Exception e) {
                        prefs.edit().remove("custom_model_uri").apply(); // invalid URI
                    }
                }
                
                if (modelPath == null) {
                    File modelFile = getModelFile();
                    if (!modelFile.exists() || modelFile.length() == 0) {
                        if (!downloadModelWithProgress(modelFile)) {
                            throw new IOException("Modèle absent et impossible d'initialiser le téléchargement.");
                        }
                    }
                    modelPath = modelFile.getAbsolutePath();
                }"""

content = re.sub(
    r"File modelFile = getModelFile\(\);\n\s*if \(\!modelFile\.exists\(\) \|\| modelFile\.length\(\) == 0\) \{.*?\n\s*\}\n\s*String modelPath = modelFile\.getAbsolutePath\(\);",
    prepare_replacement,
    content,
    flags=re.DOTALL
)

# 8. Modify generate lazy-init to match prepareModel logic
generate_replacement = """String modelPath = null;
                        SharedPreferences prefs = getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE);
                        String customUriStr = prefs.getString("custom_model_uri", null);
                        
                        if (customUriStr != null) {
                            try {
                                sModelPfd = getContext().getContentResolver().openFileDescriptor(Uri.parse(customUriStr), "r");
                                if (sModelPfd != null) {
                                    modelPath = "/proc/self/fd/" + sModelPfd.getFd();
                                }
                            } catch (Exception e) {}
                        }
                        
                        if (modelPath == null) {
                            File modelFile = getModelFile();
                            if (!modelFile.exists() || modelFile.length() == 0) {
                                downloadModelWithProgress(modelFile);
                            }
                            if (modelFile.exists() && modelFile.length() > 0) {
                                modelPath = modelFile.getAbsolutePath();
                            }
                        }

                        if (modelPath != null) {"""

content = re.sub(
    r"File modelFile = getModelFile\(\);\n\s*if \(\!modelFile\.exists\(\) \|\| modelFile\.length\(\) == 0\) \{\n\s*downloadModelWithProgress\(modelFile\);\n\s*\}\n\n\s*if \(modelFile\.exists\(\) && modelFile\.length\(\) > 0\) \{\n\s*String modelPath = modelFile\.getAbsolutePath\(\);",
    generate_replacement,
    content,
    flags=re.DOTALL
)

# 9. Modify downloadModel
content = re.sub(
    r"if \(\!force && modelFile\.exists\(\) && modelFile\.length\(\) > 0\) \{",
    """// Clear custom URI if downloading explicitly
                getContext().getSharedPreferences("GemmaPrefs", Context.MODE_PRIVATE).edit().remove("custom_model_uri").apply();
                if (!force && modelFile.exists() && modelFile.length() > 0) {""",
    content
)

with open("android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "w") as f:
    f.write(content)

