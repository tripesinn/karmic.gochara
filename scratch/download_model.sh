#!/bin/bash
# scratch/download_model.sh — Télécharge le modèle Gemma3 depuis HF et l'injecte dans le téléphone
# Usage : ./scratch/download_model.sh <VOTRE_HF_TOKEN>

TOKEN=$1
if [ -z "$TOKEN" ]; then
    echo "Usage : ./scratch/download_model.sh <HF_TOKEN>"
    exit 1
fi

MODEL_FILE="gemma-4-E2B-it-web.task"
LOCAL_PATH="scratch/$MODEL_FILE"
URL="https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm/resolve/main/$MODEL_FILE"

echo "📥 Téléchargement de Gemma4 E2B-IT depuis Hugging Face..."
curl -L -H "Authorization: Bearer $TOKEN" "$URL" -o "$LOCAL_PATH"

if [ ! -f "$LOCAL_PATH" ] || [ ! -s "$LOCAL_PATH" ]; then
    echo "❌ Échec du téléchargement (vérifiez votre token et les conditions d'accès)."
    exit 1
fi

echo "✅ Téléchargement réussi."

echo "📲 Injection du modèle dans l'appareil Android..."
# 1. Pousser vers le répertoire temporaire
/Users/jero87/Library/Android/sdk/platform-tools/adb push "$LOCAL_PATH" /data/local/tmp/

# 2. Copier dans les fichiers privés de l'application
/Users/jero87/Library/Android/sdk/platform-tools/adb shell run-as com.karmicgochara.app cp "/data/local/tmp/$MODEL_FILE" "/data/data/com.karmicgochara.app/files/"

# 3. Nettoyer le dossier temporaire du téléphone
/Users/jero87/Library/Android/sdk/platform-tools/adb shell rm "/data/local/tmp/$MODEL_FILE"

echo "🎊 Modèle injecté avec succès ! Relancez la Lecture du Jour."
