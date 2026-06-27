#!/bin/bash
# scratch/push_model.sh — Injecte le modèle Gemma4 téléchargé dans le téléphone

MODEL_FILE="gemma-4-E2B-it-web.task"
LOCAL_PATH="scratch/$MODEL_FILE"
ADB="/Users/jero87/Library/Android/sdk/platform-tools/adb"

if [ ! -f "$LOCAL_PATH" ]; then
    echo "❌ Le fichier $LOCAL_PATH n'existe pas."
    exit 1
fi

echo "📲 Injection du modèle $MODEL_FILE dans l'appareil Android..."

# 1. Pousser vers le répertoire temporaire
$ADB push "$LOCAL_PATH" /data/local/tmp/

# 2. Copier dans les fichiers privés de l'application
$ADB shell run-as com.karmicgochara.app cp "/data/local/tmp/$MODEL_FILE" "/data/data/com.karmicgochara.app/files/models/"

# 3. Nettoyer le dossier temporaire du téléphone
$ADB shell rm "/data/local/tmp/$MODEL_FILE"

echo "🎊 Modèle $MODEL_FILE injecté avec succès !"
