# Karmic Gochara — État Orchestrateur

> Fichier de persistance inter-sessions.
> Mis à jour par la skill `karmic-orchestrator` à chaque session.
> TOUJOURS lire ce fichier en premier.

---

## État Actuel

**Dernière mise à jour** : 2026-06-30T10:39 (session orchestrateur)

**Build Astro** : ⏳ En attente de rebuild pour intégrer carte.astro
**Capacitor Sync** : ⏳ En attente
**Pixel 10** : ⏳ À vérifier
**Deploy Cloud Run** : ⏳ En attente de commit
**IA Locale (port 8888)** : ✅ UP — gemma-4-E2B-it-qat-oQ4-fp16 (Analyse réussie)

---

## Bugs Résolus ✅

| ID | Description | Fix | Commit |
|----|-------------|-----|--------|
| BUG-001 | `Unable to open asset URL: /app/chat/index.html` | Créé `astro/src/pages/app/chat.astro` | 69f9f67 |
| BUG-002 | LoginCard boucle sur `/register` | Guard `_path.includes('/register')` ligne 35 | 69f9f67 |
| BUG-003 | Assets Capacitor stale | Rebuild Astro + sync Capacitor | 69f9f67 |
| BUG-GIT | `scratch/gemma-4-E2B-it-web.task` (1.9GB) dans git | Ajouté `scratch/` au `.gitignore` | 69f9f67 amendé |
| BUG-006 | Carte Astrale vide (données astrologiques manquantes) | Enrichissement profil ajouté dans `api.py` (`login_firebase`) | (en cours) |

---

## Bugs Restants

| ID | Priorité | Description | Fichier |
|----|----------|-------------|---------|
| BUG-004 | P2 | `lecture.astro` ne déclenche pas le modèle Gemma | `astro/src/pages/app/lecture.astro` |
| BUG-007 | P3 | Intégration structurelle `carte.astro` (fichiers non suivis) | `astro/src/pages/app/carte.astro` |

---

## Architecture Confirmée

```
capacitor.config.json → webDir: "www"         ✅
astro/src/pages/app/  → index, lecture, miroir, chat, carte  ✅
www/app/              → index.html, lecture/, miroir/, chat/, carte/  ✅
android/assets/       → synced ✅
scratch/              → gitignored ✅ (contient modèles >100MB)
```

**JAVA_HOME** (pour Gradle) :
`/Applications/Android Studio.app/Contents/jbr/Contents/Home`

**ADB** : `~/Library/Android/sdk/platform-tools/adb`

---

## Prochaine Session — Actions

1. [ ] Ajouter les fichiers `carte.astro` à git
2. [ ] Build Astro et Sync Capacitor
3. [ ] Déployer la correction de la carte astrale (`api.py`)
4. [ ] BUG-004 : Investiguer `lecture.astro` (Gemma local)
5. [ ] Vérification Pixel 10

---

## Historique

### 2026-06-30 — Session orchestrateur (Carte Astrale)
- Phase 0 : Diagnostic via IA Locale (UP). Fichiers manquants identifiés (`carte.astro`).
- Phase 1 : BUG-006 corrigé (logique `login_firebase` alignée avec auth classique).
- Phase 2 : En attente (Build & Sync)
- Phase 3 : En attente (Deploy)
- Phase 4 : En attente (Pixel 10)
