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

### IA Locale (oMLX — port 8888)
- **Endpoint** : `http://127.0.0.1:8888/v1/chat/completions`
- **Modèle actif** : `gemma-4-E2B-it-qat-oQ4-fp16`
  _(2B params quantisé QAT — tient en mémoire contrairement
  au modèle 4B qui causait des 507 OOM)_
- **Auth** : `Bearer omlx_12345678910111213abcDEF`
- **Script bridge** : `scripts/query_local_ai.py`
  - Retry automatique sur 507 (1024 → 512 → 256 tokens)
  - Support system prompt : 2e argument optionnel
  - Timeout : 120s

### Infra
- **Backend** : Flask · `app.py` · port 5000 (local)
- **Frontend** : Astro · `astro/` · build → `www/`
- **Deploy** : GitHub push → Cloud Build → Cloud Run
- **État persistant** : `ORCHESTRATOR_STATE.md`
- **JAVA_HOME** (Gradle) :
  `/Applications/Android Studio.app/Contents/jbr/Contents/Home`
- **ADB** : `~/Library/Android/sdk/platform-tools/adb`

---

## PHASE 0 — Diagnostic (Déléguée à l'IA Locale)

> **RÈGLE** : Ne jamais modifier de code avant la Phase 0.

### 0.0 — Toujours lire l'état persistant en premier

```bash
cat /Users/jero87/karmic.gochara/ORCHESTRATOR_STATE.md
```

### 0.1 — Vérifier si oMLX est disponible

```bash
curl -s -o /dev/null -w "%{http_code}" \
  http://127.0.0.1:8888/v1/models \
  -H "Authorization: Bearer omlx_12345678910111213abcDEF"
# 200 = disponible, autre = redémarrer oMLX
```

Si oMLX est DOWN → continuer le diagnostic manuellement
(Phase 0.2 uniquement) puis noter dans ORCHESTRATOR_STATE.md.

### 0.2 — Collecte des données brutes

```bash
# État git
git -C /Users/jero87/karmic.gochara status --short
git -C /Users/jero87/karmic.gochara log --oneline -5

# Pages Astro
ls /Users/jero87/karmic.gochara/astro/src/pages/app/

# Dernier build
ls /Users/jero87/karmic.gochara/www/app/ 2>/dev/null \
  || echo "AUCUN BUILD"

# Routes Flask
grep -n "@.*route" \
  /Users/jero87/karmic.gochara/blueprints/*.py | head -40

# Logs build récents
tail -15 /Users/jero87/karmic.gochara/build.log 2>/dev/null
```

### 0.3 — Déléguer l'analyse à l'IA locale

Formate les données collectées, puis appelle le bridge :

```bash
python3 /Users/jero87/karmic.gochara/scripts/query_local_ai.py \
  "Analyse cet état technique de Karmic Gochara et retourne :
  1. BUGS ACTIFS (priorité P1/P2/P3)
  2. FICHIERS MANQUANTS
  3. ORDRE DE CORRECTION OPTIMAL
  4. RISQUES
  [DONNÉES : colle ici les sorties de 0.2]" \
  "Tu es un analyste technique senior. Sois concis, 200 mots max."
```

**Comportement sur erreur** :
- 507 OOM → le script retente automatiquement avec moins
  de tokens (1024 → 512 → 256). Pas besoin d'intervenir.
- `connexion refusée` → oMLX DOWN, continuer sans IA locale.

### 0.4 — Mise à jour de l'état persistant

Mettre à jour `ORCHESTRATOR_STATE.md` avec les conclusions.

---

## PHASE 1 — Corrections Séquentielles

> Un bug = une correction = une vérification.

### Bugs récurrents connus (référence)

```
BUG-001 [RÉSOLU] : Page /app/chat manquante
  Fix : astro/src/pages/app/chat.astro créé (commit 14f44d9)

BUG-002 [RÉSOLU] : LoginCard boucle sur /register
  Fix : guard _path.includes('/register') (LoginCard.astro L35)

BUG-003 [RÉSOLU] : Assets Capacitor stale
  Fix : Rebuild Astro + sync Capacitor (commit 14f44d9)

BUG-004 [ACTIF P2] : lecture.astro ne déclenche pas Gemma
  Fichier : astro/src/pages/app/lecture.astro
  À investiguer : appel au plugin GemmaSynthesis

BUG-GIT [ACTIF P1] : scratch/ contient des fichiers >100MB
  Fix : scratch/ dans .gitignore ✅
  Problème : commit 14f44d9 contient encore le blob
  Solution : git filter-branch ou BFG Repo Cleaner
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

# 2.3 Vérifier les pages dans www/
ls /Users/jero87/karmic.gochara/www/app/
```

Build cassé → retour Phase 1. Ne pas déployer avec erreurs.

---

## PHASE 3 — Déploiement Cloud

```bash
cd /Users/jero87/karmic.gochara
git add .
git commit -m "fix(orchestrator): [RÉSUMÉ Phase 1]"
git push origin main
```

> ⚠️ Si push rejeté (fichier >100MB) :
> ```bash
> # Identifier le fichier problématique
> git show --stat HEAD | grep -v "^$" | awk '{print $1, $NF}' \
>   | sort -rh | head -5
> # Retirer du staging et amender
> git restore --staged <fichier>
> git commit --amend --no-edit
> ```

### Test routes critiques prod

```bash
for path in "/" "/register" "/terms" "/app/chat/"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://karmicgochara.app$path")
  echo "$path → $code"
done
```

---

## PHASE 4 — Vérification Pixel 10

### 4.1 Vérifier l'appareil

```bash
ADB=~/Library/Android/sdk/platform-tools/adb
$ADB devices
# Attendu : "55161FDCH0004E  device"
```

### 4.2 Build et déployer APK debug

```bash
export JAVA_HOME=\
  "/Applications/Android Studio.app/Contents/jbr/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"

cd /Users/jero87/karmic.gochara/android
./gradlew assembleDebug && \
  ~/Library/Android/sdk/platform-tools/adb install -r \
    app/build/outputs/apk/debug/app-debug.apk
```

### 4.3 Vérifier les logs Capacitor

```bash
ADB=~/Library/Android/sdk/platform-tools/adb
$ADB logcat -c
$ADB shell am force-stop com.karmicgochara.app
sleep 1
$ADB shell am start -n com.karmicgochara.app/.MainActivity
sleep 8
$ADB logcat -d \
  | grep -iE "local request|Unable to open|asset URL|chat" \
  | head -20
```

### 4.4 Critères de succès

- ✅ Zéro `Unable to open asset URL`
- ✅ `/` → `Handling local request`
- ✅ `/app/chat/` → chargé sans erreur
- ✅ `/register` → pas de boucle

---

## PHASE 5 — Journal de session

Mettre à jour `ORCHESTRATOR_STATE.md` :

```markdown
## Session [DATE]
- oMLX : UP/DOWN (modèle: gemma-4-E2B-it-qat-oQ4-fp16)
- Bugs corrigés : [liste]
- Build : OK/FAIL
- Deploy : commit [hash] → Cloud Run live
- Pixel 10 : OK/FAIL
- Prochaine session : [problèmes restants]
```

---

## Règles d'Or

1. Lire `ORCHESTRATOR_STATE.md` en PREMIER à chaque session.
2. Vérifier la disponibilité oMLX (curl port 8888) avant usage.
3. Le script `query_local_ai.py` gère les 507 OOM seul.
4. Ordre 0→1→2→3→4 — ne jamais sauter une phase.
5. Un bug = une correction = une vérification.
6. Build cassé → STOP, pas de déploiement.
7. Push rejeté (>100MB) → identifier et exclure le fichier.
