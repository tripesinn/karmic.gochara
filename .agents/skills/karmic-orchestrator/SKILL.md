---
name: karmic-orchestrator
description: >
  Agent orchestrateur principal pour Karmic Gochara.
  Maintient un état persistant entre sessions, diagnostique
  les problèmes systémiques (via IA locale port 8888),
  applique les corrections dans le bon ordre, build et déploie,
  puis vérifie l'installation sur Pixel 10.
  À activer en début de session ou quand plusieurs bugs
  coexistent et que les corrections au coup par coup échouent.
---

# Karmic Gochara — Orchestrateur Principal

## Vue d'ensemble

Cet orchestrateur est le **chef de projet technique**.
Il ne corrige jamais un bug isolément sans avoir d'abord
établi l'état complet du système.

---

## Références rapides

- **IA locale** : `http://127.0.0.1:8888/v1/chat/completions`
  - Modèle : `unsloth--gemma-4-E4B-it-UD-MLX-4bit`
  - Auth : `Bearer omlx_12345678910111213abcDEF`
  - Script bridge : `scripts/query_local_ai.py`
- **Backend** : Flask · `app.py` · port 5000 (local)
- **Frontend** : Astro · `astro/` · build → `www/`
- **Deploy** : GitHub push → Cloud Build → Cloud Run
- **État persistant** : `ORCHESTRATOR_STATE.md`

---

## PHASE 0 — Diagnostic (Déléguée à l'IA Locale)

> **RÈGLE** : Ne jamais modifier de code avant la Phase 0.

### 0.1 — Collecte des données brutes

Exécute ces commandes pour récolter le contexte :

```bash
# État git
git -C /Users/jero87/karmic.gochara status --short
git -C /Users/jero87/karmic.gochara log --oneline -5

# Pages Astro
ls /Users/jero87/karmic.gochara/astro/src/pages/
ls /Users/jero87/karmic.gochara/astro/src/pages/app/ 2>/dev/null

# Dernier build
ls /Users/jero87/karmic.gochara/astro/dist/app/ 2>/dev/null \
  || echo "AUCUN BUILD"

# Routes Flask
grep -n "@.*route" \
  /Users/jero87/karmic.gochara/blueprints/*.py | head -40

# Logs build récents
tail -20 /Users/jero87/karmic.gochara/build.log 2>/dev/null
```

### 0.2 — Analyse déléguée à l'IA locale

Formate les données de 0.1 dans un prompt et exécute :

```bash
python3 /Users/jero87/karmic.gochara/scripts/query_local_ai.py \
  "Tu es analyste technique senior pour Karmic Gochara.
  Données système : [INSÈRE LES SORTIES 0.1]
  Retourne :
  1. BUGS ACTIFS
  2. FICHIERS MANQUANTS
  3. ROUTES CASSÉES
  4. ORDRE DE CORRECTION OPTIMAL
  5. RISQUES
  Sois concis et technique."
```

### 0.3 — Mise à jour de l'état persistant

Mettre à jour `ORCHESTRATOR_STATE.md` avec les conclusions.

---

## PHASE 1 — Corrections Séquentielles

> Un bug = une correction = une vérification.

### Bugs récurrents connus

```
BUG-001 : Page /app/chat manquante
  → Créer astro/src/pages/app/chat.astro
  → Vérifier route Flask si /chat/ask existe

BUG-002 : LoginCard boucle sur /register
  → Ajouter guard explicite pour la route /register
  → Fichier : astro/src/components/LoginCard.astro

BUG-003 : Assets Capacitor non trouvés
  → Vérifier capacitor.config.json (webDir = "www")
  → Re-sync après build
```

---

## PHASE 2 — Build & Sync

```bash
# 2.1 Build Astro
cd /Users/jero87/karmic.gochara/astro
npm run build
# Vérifier : 0 errors

# 2.2 Sync Capacitor
npm run sync:capacitor

# 2.3 Vérifier les pages dans dist/
ls /Users/jero87/karmic.gochara/astro/dist/app/
```

Si build échoue → retour Phase 1. Ne pas déployer avec erreurs.

---

## PHASE 3 — Déploiement Cloud

```bash
cd /Users/jero87/karmic.gochara
git add .
git commit -m "fix(orchestrator): [RÉSUMÉ Phase 1]"
git push origin main
```

Informer l'utilisateur :
> Push effectué. Cloud Build déclenché. Délai ~3-5 min.
> URL prod : https://karmicgochara.app

### Test routes critiques prod

```bash
for path in "/" "/register" "/terms" "/privacy"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://karmicgochara.app$path")
  echo "$path → $code"
done
```

---

## PHASE 4 — Vérification Pixel 10

### 4.1 Vérifier appareil connecté

```bash
adb devices
# Attendu : "SERIAL  device"
```

### 4.2 Build et déployer APK debug

```bash
cd /Users/jero87/karmic.gochara/android
./gradlew assembleDebug && \
  adb install -r \
    app/build/outputs/apk/debug/app-debug.apk
```

### 4.3 Lancer l'app et capturer les logs

```bash
# Lancer l'app
adb shell monkey -p com.karmicgochara.app \
  -c android.intent.category.LAUNCHER 1

# Logs Capacitor (30 secondes)
timeout 30 adb logcat -s \
  "Capacitor" "CapacitorWebView" "KarmicApp" \
  | grep -E "request|asset|Unable|ERROR"
```

### 4.4 Critères de succès

- ✅ Aucun `Unable to open asset URL`
- ✅ `/` → 200 dans les logs Capacitor
- ✅ `/register` → pas de boucle
- ✅ `/app/` → charge correctement

Si `Unable to open asset URL` → Phase 2 (re-sync Capacitor).

---

## PHASE 5 — Journal de session

Après chaque session, écrire dans `ORCHESTRATOR_STATE.md` :

```markdown
## Session [DATE]
- Bugs corrigés : [liste]
- Build : OK/FAIL
- Deploy : commit [hash] → Cloud Run live
- Pixel 10 : OK/FAIL
- Prochaine session : [problèmes restants]
```

---

## Règles d'Or

1. Lire `ORCHESTRATOR_STATE.md` en PREMIER à chaque session.
2. Déléguer le diagnostic à l'IA locale (port 8888).
3. Ordre 0→1→2→3→4 — ne jamais sauter une phase.
4. Un bug = une correction = une vérification.
5. Build cassé → STOP, pas de déploiement.
