#!/bin/bash

# Script d'automatisation pour Karmic Gochara
# Usage: ./ship.sh

echo "🚀 [1/3] Construction de l'interface Astro..."
cd astro && npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build Astro réussi."
    echo "📡 [2/3] Synchronisation avec Capacitor Android..."
    cd ..
    npx cap sync android

    if [ $? -eq 0 ]; then
        echo "✅ Synchronisation réussie."
        echo "📱 [3/3] Prêt pour Android Studio !"
        echo "👉 Cliquez sur la FLECHE VERTE dans Android Studio pour lancer l'app."
    else
        echo "❌ Erreur lors de la synchronisation Capacitor."
        exit 1
    fi
else
    echo "❌ Erreur lors du build Astro."
    exit 1
fi
