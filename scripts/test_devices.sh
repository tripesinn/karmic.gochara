#!/bin/bash
set -e

echo "=== 1. Pushing pending code ==="
cd /Users/jero87/karmic.gochara
git add .
git commit -m "Auto-commit avant déploiement multi-appareils" || true
git push origin HEAD || true

ADB=~/Library/Android/sdk/platform-tools/adb
echo "=== 2. Checking devices ==="
$ADB devices

echo "=== 3. Deploying to Pixel 10 (Dev) ==="
# S'assurer que le build Astro est en mode Dev
cd /Users/jero87/karmic.gochara/astro
PUBLIC_FIREBASE_EMULATOR=true npm run build
npm run sync:capacitor

# Ensure tunnels are active
$ADB -s 55161FDCH0004E reverse tcp:5001 tcp:5001 || true
$ADB -s 55161FDCH0004E reverse tcp:8080 tcp:8080 || true
$ADB -s 55161FDCH0004E reverse tcp:9099 tcp:9099 || true
$ADB -s 55161FDCH0004E reverse tcp:8888 tcp:8888 || true

export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"

cd /Users/jero87/karmic.gochara/android
./gradlew assembleDebug
$ADB -s 55161FDCH0004E install -r app/build/outputs/apk/debug/app-debug.apk || echo "Failed to install on Pixel 10"
$ADB -s 55161FDCH0004E shell am start -n com.karmicgochara.app/.MainActivity || true

echo "=== 4. Deploying to Huawei (Prod) ==="
cd /Users/jero87/karmic.gochara/astro
# Renommer .env.local pour ne pas qu'il force le mode Emulator
if [ -f ".env.local" ]; then
  mv .env.local .env.local.bak
fi

PUBLIC_FIREBASE_EMULATOR=false npm run build
npm run sync:capacitor

# Restaurer .env.local
if [ -f ".env.local.bak" ]; then
  mv .env.local.bak .env.local
fi

cd /Users/jero87/karmic.gochara/android
./gradlew assembleDebug
$ADB -s 22X7N19504005360 install -r app/build/outputs/apk/debug/app-debug.apk || echo "Failed to install on Huawei"
$ADB -s 22X7N19504005360 shell am start -n com.karmicgochara.app/.MainActivity || true

echo "=== Done ==="
