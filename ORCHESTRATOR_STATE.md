# Karmic Gochara — État Orchestrateur

> Fichier de persistance inter-sessions.
> Mis à jour par la skill `karmic-orchestrator` à chaque session.
> TOUJOURS lire ce fichier en premier.

---

## État Actuel

**Dernière mise à jour** : 2026-07-01T08:41 (session orchestrateur)

**Build Astro** : ✅ OK
**Capacitor Sync** : ✅ OK
**APK Debug** : ✅ Installé sur Pixel 10
**Deploy Cloud Run** : ✅ Live (commit 63fff38)
**IA Locale (port 8888)** : ✅ UP — gemma-4-E2B-it-qat-oQ4-fp16

---

## Bugs Résolus ✅

| ID | Description | Fix | Commit |
|----|-------------|-----|--------|
| BUG-001 | `Unable to open asset URL: /app/chat/index.html` | Créé `astro/src/pages/app/chat.astro` | 69f9f67 |
| BUG-002 | LoginCard boucle sur `/register` | Guard `_path.includes('/register')` ligne 35 | 69f9f67 |
| BUG-003 | Assets Capacitor stale | Rebuild Astro + sync Capacitor | 69f9f67 |
| BUG-GIT | `scratch/gemma-4-E2B-it-web.task` (1.9GB) dans git | Ajouté `scratch/` au `.gitignore` | 69f9f67 amendé |
| BUG-006 | Carte Astrale vide (données astrologiques manquantes) | Enrichissement profil ajouté dans `api.py` (`login_firebase`) | a8a81dd |
| BUG-008 | `ConnectException` 127.0.0.1 depuis l'app Android | Modification de `getBaseUrl` dans `api.ts` pour pointer vers l'API Cloud sur Capacitor natif | a8a81dd |
| BUG-009 | Sign-in failed combination conflict | Retrait de GetSignInWithGoogleOption dans KarmicGoogleAuthPlugin | 63fff38 |
| BUG-004 | `lecture.astro` — timeout au téléchargement du modèle Gemma | `readTimeout` passé à 0 (illimité) dans `GemmaSynthesisPlugin.java` | (en cours) |

---

## Bugs Restants

Aucun bug actif identifié.

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

1. [x] Ajouter les fichiers `carte.astro` à git
2. [x] Build Astro et Sync Capacitor
3. [x] Déployer la correction de la carte astrale (`api.py`)
4. [ ] BUG-004 : Investiguer `lecture.astro` (Gemma local)
5. [x] Vérification Pixel 10

---

## Historique

### 2026-06-30 — Session orchestrateur (Carte Astrale)
- Phase 0 : Diagnostic via IA Locale (UP). Fichiers manquants identifiés (`carte.astro`).
- Phase 1 : BUG-006 corrigé (logique `login_firebase` alignée avec auth classique).
- Phase 2 : Build & Sync (OK)
- Phase 3 : Deploy (Commit & Push OK)
- Phase 4 : Pixel 10 (Install APK succès)

### 2026-06-30 — Session orchestrateur (Restauration chat)
- Phase 0 : Diagnostic IA locale indique l'absence de `chat.astro` dans le build (P2).
- Phase 1 : Restauration de `chat.astro` depuis l'historique git.
- Phase 2 : Build Astro & Sync Capacitor (OK, `chat` est bien présent dans `www/app/`).
