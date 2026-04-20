# Skill: Android Build & Sync

Ce skill décrit les étapes pour synchroniser le code web vers Android et générer un build.

## Dépendances
- Node.js & npm
- Android Studio & SDK
- Capacitor CLI

## Étapes de Synchronisation
Pour mettre à jour le code Android après des modifications dans le dossier `www` :
1. **Build Web** (si applicable) :
   ```bash
   npm run build
   ```
2. **Capacitor Sync** :
   ```bash
   npx cap sync android
   ```

## Étapes de Build
Pour générer un APK ou un Bundle :
1. **Ouvrir le projet** : Ouvrir le dossier `android` dans Android Studio.
2. **Build via Gradle** (Ligne de commande) :
   ```bash
   cd android
   ./gradlew assembleDebug
   ```

## Automatisation
Utilisez ce skill quand l'utilisateur demande de "mettre à jour l'app sur son téléphone" ou "générer un installateur".
