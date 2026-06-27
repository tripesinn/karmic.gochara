import re

with open("android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "r") as f:
    content = f.read()

content = content.replace("File modelFile = getModelFile();", "DocumentFile modelFile = getModelDocumentFile();")
content = content.replace("File destFile = getModelFile();", "DocumentFile destFile = getModelDocumentFile();")

with open("android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java", "w") as f:
    f.write(content)
