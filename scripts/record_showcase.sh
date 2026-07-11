#!/bin/bash
export ADB=~/Library/Android/sdk/platform-tools/adb
echo "Lancement de l'enregistrement pour 25 secondes... Naviguez dans l'application !"
$ADB shell screenrecord --time-limit 25 /sdcard/demo_app.mp4
echo "Récupération de la vidéo..."
$ADB pull /sdcard/demo_app.mp4 static/img/demo_app_fr.mp4
$ADB shell rm /sdcard/demo_app.mp4
echo "Vidéo prête ! L'agent l'a déjà intégrée dans le HTML."
