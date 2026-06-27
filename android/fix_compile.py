import re

with open("app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "r") as f:
    content = f.read()

# Fix downloadModelWithProgress
content = re.sub(
    r"File parent = dest\.getParentFile\(\);\n            if \(parent != null && !parent\.exists\(\)\) \{\n                parent\.mkdirs\(\);\n            \}",
    "",
    content
)

content = re.sub(
    r"try \(InputStream in  = conn\.getInputStream\(\);\n                 FileOutputStream out = new FileOutputStream\(dest\)\) \{",
    """try (InputStream in  = conn.getInputStream();
                 java.io.OutputStream out = getContext().getContentResolver().openOutputStream(dest.getUri())) {""",
    content
)

content = re.sub(
    r"try \(java\.io\.OutputStream fos = getContext\(\)\.getContentResolver\(\)\.openOutputStream\(dest\.getUri\(\)\)\) \{",
    """try (java.io.FileOutputStream fos = new java.io.FileOutputStream(dest)) {""",
    content
)


with open("app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "w") as f:
    f.write(content)
