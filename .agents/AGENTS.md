# Règles Spécifiques au Projet Karmic Gochara

<RULE[capacitor_sync]>
## Déploiement et Synchronisation Automatique Capacitor

L'utilisateur teste l'application de façon continue via Android Studio avec un Google Pixel branché.

**Règle absolue :** 
À chaque fois que vous modifiez un fichier frontend dans le dossier `astro` (composants `.astro`, styles, scripts, pages), vous **DEVEZ IMPÉRATIVEMENT** exécuter la commande de build et de synchronisation Capacitor **avant de terminer votre tour**, sans attendre que l'utilisateur le demande.

Commande à exécuter :
```bash
cd astro && npm run sync:capacitor
```
</RULE[capacitor_sync]>

<RULE[check_logs]>
## Commande Raccourci "check logs"

Dès que l'utilisateur dit "check logs" ou demande d'analyser les logs, l'agent doit :
1. Exécuter le script `log2localIA` pour récupérer et analyser les logs récents de l'appareil Android :
   ```bash
   python3 /Users/jero87/.gemini/config/skills/log2localIA/scripts/analyze_logs.py --package com.karmicgochara.app --limit 100 --output scratch/local_ai_analysis.md
   ```
2. Attendre que l'analyse se termine, puis lire le rapport dans `scratch/local_ai_analysis.md`.
3. Mettre à jour la section "Bugs Restants" dans `ORCHESTRATOR_STATE.md` avec les anomalies trouvées.
4. Présenter le résumé à l'utilisateur et proposer les actions correctives.
</RULE[check_logs]>

<RULE[local_ai_first]>
## Délégation Prioritaire à l'IA Locale (oMLX)

**Règle absolue :** Avant d'effectuer soi-même une analyse
de logs, une correction de code, ou une synthèse technique,
l'agent doit **toujours vérifier si l'IA locale est disponible**
et lui déléguer la tâche si c'est le cas.

### Vérification disponibilité oMLX

```bash
curl -s -o /dev/null -w "%{http_code}" \
  http://127.0.0.1:8888/v1/models \
  -H "Authorization: Bearer omlx_12345678910111213abcDEF"
# 200 = UP → déléguer | autre = DOWN → analyser soi-même
```

### Délégation via le bridge

```bash
python3 /Users/jero87/karmic.gochara/scripts/query_local_ai.py \
  "[DONNÉES À ANALYSER]" \
  "Tu es un analyste technique senior. Sois concis, 200 mots max."
```

### Cas d'usage prioritaires pour oMLX

- Analyse de logs Android (logcat)
- Correction et refactoring de code
- Synthèse technique d'un état du système
- Reformatage ou documentation de code

### Si oMLX est DOWN

Continuer manuellement et noter dans `ORCHESTRATOR_STATE.md` :
`**IA Locale** : ❌ DOWN`.
</RULE[local_ai_first]>

<RULE[autonomous_ondevice_testing]>
## Tests Autonomes et Validation Visuelle Mobile

**Règle absolue :**
Ne demandez JAMAIS à l'utilisateur de tester, de déverrouiller l'écran, ou de vérifier un flux sur son appareil Google Pixel. Si vous rencontrez un obstacle (écran de verrouillage, délai réseau), trouvez un contournement ou réessayez plus tard, mais n'interrompez PAS votre flux pour solliciter l'utilisateur.

Pour chaque scénario de test d'interface ou de flux utilisateur :
1. Déployez et lancez l'application via Gradle et ADB.
2. Naviguez de façon autonome dans l'interface en simulant des clics tactiles (`adb shell input tap`) et des saisies clavier (`adb shell input text`).
3. Prenez régulièrement des captures d'écran de l'appareil (`adb shell screencap` puis `adb pull`) et analysez-les avec le visualiseur pour confirmer visuellement l'état de l'application et la réponse de l'interface ou des API.
4. Ajustez vos clics ou saisies en fonction des coordonnées réelles (ex: résolution 1080x2410).
5. Testez en boucle jusqu'à ce que le correctif soit intégralement prouvé visuellement. Ne retournez à l'utilisateur QUE lorsque le problème initial est 100% résolu (ou si une erreur fatale inédite bloque techniquement l'ADB).
</RULE[autonomous_ondevice_testing]>

