# Karmic Gochara — État Orchestrateur

> Fichier de persistance inter-sessions.
> Mis à jour par la skill `karmic-orchestrator` à chaque session.
> TOUJOURS lire ce fichier en premier.

📄 **Référence Flow Utilisateur** : voir [user_flow.md](file:///Users/jero87/.gemini/antigravity-ide/brain/f06fa751-4d4b-4993-92a7-13f639b093b6/user_flow.md)

---

## État Actuel

**Dernière mise à jour** : 2026-07-13T21:58 (Modèles locaux restructurés)
**Build Astro** : ✅ OK (www/ à jour et resynchronisé Capacitor)
**Environnement & Modèles** :
- **Node.js** : `v20.12.2` (via NVM)
- **Firebase CLI** : `v13.6.0`
- **Android Studio** : SDK Platform-Tools installés (adb fonctionnel)
- **IA Locale** : ✅ UP (oMLX port 8889)
- **Architecture Modèles** :
  - **Hermes (Agent)** : Principal + délégation = `Hermes-3` local (non-reasoning) → 0 cloud pour le bulk.
  - **agy-cli** : Gemini primaire + `Qwen3.5-9B-4bit` local fallback (`base_url = http://127.0.0.1:8889/v1` avec `enable_thinking = false` pour éliminer le thinking-leak).
  - **R1 (DeepSeek)** : Démonté/désactivé partout (thinking-leak & raisonnement excessif inadapté aux subagents).
- **Émulateur Firebase** : ✅ Actif (9099, 8080)
- **Serveur Flask (API)** : ✅ Actif (5001, relancé dans .venv)
- **ADB Reverse** : ✅ Actif (5001, 8080, 9099, 8889)
- **Pixel 10 ADB** : ✅ Connecté (55161FDCH0004E)
- **Huawei ADB** : ✅ Connecté (22X7N19504005360)

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
| BUG-004 | `lecture.astro` — timeout au téléchargement/génération du modèle Gemma | `readTimeout` passé à 0 dans `GemmaSynthesisPlugin.java` | ✅ Résolu |
| BUG-010 | `invalid literal for int()` dans `/calculate` quand `date` est vide | Fallback `date.today()` dans `astro.py` L105 | 492f579 |
| BUG-015 | Redirection /app échouée sur Android WebView | Redirection explicite vers `/app/index.html` dans `RegisterForm.astro` L316 | ✅ Résolu |
| BUG-018 | Crash NoSuchMethodError au démarrage (SendChannel.close) | Force-downgrade de kotlinx-coroutines à 1.7.3 dans build.gradle | ✅ Résolu |
| BUG-019 | Signature de sauvegarde incompatible | Clean uninstall / reinstall sur le Pixel 10 | ✅ Résolu |
| BUG-020 | Blocage de l'app par la carte de téléchargement locale | Bypass si localMode est cloud ou non native | ✅ Résolu |
| BUG-022 | Blocage de la lecture quotidienne (SSE) sous Capacitor | Désactivation de global CapacitorHttp dans `capacitor.config.json` | ✅ Résolu |

---

## Bugs Restants

| ID | Priorité | Description | Statut |
|----|----------|-------------|--------|
| BUG-011 | P3 | `PUBLIC_REVENUECAT_ANDROID_KEY` manquante → monétisation bloquée | ⏸️ Reporté (Testeurs Pro auto) |
| BUG-012 | P2 | `pVM is not available` dans `IsolatedStorageServiceM` (bug OS Pixel) | ⚠️ Ignorable (bug OS Pixel) |
| BUG-013 | P3 | `App-specific configuration not found` (PackageConfigPersister) | ⚠️ Ignorable (Warning OS/Capacitor) |
| BUG-014 | P3 | Spanner: `No data was found...` | ⚠️ Ignorable (Warning Google Play Services) |
| BUG-016 | P2 | DNS: `Failed to resolve using system DNS resolver` | ⚠️ Ignorable (Pas d'internet) |
| BUG-017 | P3 | Permission: `UID 10074 has no location permission` (`com.huawei.hwid`) | ⚠️ Ignorable (Warning système Huawei, pas de localisation requise) |
| BUG-021 | P2 | FileUtils: `android.system.ErrnoException` dans les logs | ⚠️ En cours d'analyse |


---

## Fichiers à Nettoyer (identifiés par oMLX)

- `astro/src/pages/app/lecture.astro.bak` → supprimé ✅
- `www/_astro/carte.DFdCE7f_.css` → supprimé (D dans git) ✅
- `www/_astro/lecture.astro_astro_type_script_index_0_lang.CkcOIWIc.js` → supprimé ✅
- `www/_astro/carte._a9JUIDq.css` → untracked, sera commité au prochain push
- `www/_astro/lecture.astro_astro_type_script_index_0_lang.B2S5Gxd6.js` → untracked, sera commité

> ⚠️ Les fichiers `??` (untracked) dans `www/_astro/` sont normaux
> après un rebuild Astro — ils seront inclus au prochain commit.

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

1. [x] Gérer l'erreur 429 (bouton Stripe visible dans lecture.astro)
2. [x] **Configurer Firebase Auth Emulator** (Mode test pour tester comme un nouvel utilisateur)
3. [x] **Injecter `PUBLIC_REVENUECAT_ANDROID_KEY`** (Reporté, testeurs Pro auto)
4. [x] Supprimer `lecture.astro.bak`
5. [x] **Commit** des modifications non commités (lecture.astro, apply_local_ai.py, www/)
6. [x] BUG-004 : Résolu (Gemma local fonctionnel, confirmé par accès au chat)
7. [ ] Diagnostiquer `pVM is not available` dans `IsolatedStorageServiceM`

---

## Checklist de Test AAB (à valider avant chaque release)

- [x] Connexion Google → /app (pas de crash, pas de boucle)
- [x] Nouveau compte → /register → géocode → submit → /app/index.html
- [x] Dashboard : pseudo affiché, 3 cartes visibles
- [ ] Lecture plan free : erreur 429 + bouton Stripe visible
- [ ] Lecture plan payant : texte généré, bouton copier actif
- [x] Chat : question → réponse reçue
- [x] Carte Astrale : tableau planètes + SVG chargés
- [ ] Agenda : lien iCal disponible si plan payant

---

## Historique

### 2026-07-12 — Session orchestrateur (Amélioration X Bot)
- oMLX : ✅ UP (gemma-4-E2B-it-qat-oQ4-fp16)
- **Modifications** :
  - **astro_calc.py** : Ajout du calcul dynamique (appliquant/séparant) via projection de la vitesse des planètes.
  - **karmic_lite.py** : Ajout de tags d'intensité (Crise aiguë, Processus actif, Travail de fond) et de phase (Appliquant/Séparant) en fonction de la valeur de l'orbe.
  - **x_grok_bot.py** : Refonte du prompt pour éliminer le ton couperet, exploiter les tags d'intensité et adopter une approche bienveillante axée sur la durée (Graine / Chemin / Horizon).
- Test IA : Génération d'un message très pertinent et adouci testé avec succès sur l'IA locale.
- Prochaine session : Déploiement du X Bot ou suite des corrections mineures (P3).

### 2026-07-11 — Session orchestrateur (check logs manuelle)
- oMLX : ❌ DOWN (Analyse manuelle car connexion refusée)
- **Phase 0** : Lecture des logs via adb. Aucune exception ou crash détecté pour com.karmicgochara.app.
- L'avertissement "App-specific configuration not found" (BUG-013) a été remarqué mais est déjà répertorié.
- **Prochaine étape** : L'application semble stable, attente des instructions.

### 2026-07-11 — Session orchestrateur (Phase 0)
- oMLX : ✅ UP (Relancé suite au timeout)
- **Phase 0** : Diagnostic effectué. Aucun bug critique détecté dans l'état actuel de l'application. Astro pages et www/app intacts. Build Cloud Run succès. 
- **Prochaine étape** : Reprendre avec la configuration du bot X (`x_grok_bot.py`) ou toute autre instruction.

### 2026-07-11 — Session orchestrateur (X Bot)
- oMLX : ✅ UP (Analyse réussie)
- **Phase 0** : Diagnostic effectué. Correction de la syntaxe de `query_local_ai.py`.
- **Bot X.com** : Configuration de `grok-4.3`, résolution des conflits de tokens `.env`, ajout de `user_auth=True` pour régler le bug `401 Unauthorized` de Tweepy.
- **Prochaine étape** : Tâche terminée, le X Bot tourne en tâche de fond (ou est prêt à être lancé par l'utilisateur).

### 2026-07-11 — Session orchestrateur (Landing Page)
- oMLX : ✅ UP (port 8889)
- **Refonte Landing Page** :
  - Création d'une interface en deux colonnes pour `index.astro`.
  - Intégration d'un mockup de téléphone 100% CSS avec effet *Glassmorphism*.
  - Mise à jour de l'accroche : "Ton agent astrologue".
- Build : ✅ OK (Astro + Capacitor Sync)
- Deploy : En attente
- Prochaine session : Configurer le X Bot (`x_grok_bot.py`).

### 2026-07-09 — Session Initiale
- **Diagnostic Phase 0** :
  - oMLX : ❌ DOWN (Erreur 404 sur le port 8888).
  - Git : Fichiers sources propres, quelques fichiers untracked/logs générés.
  - Build Astro : OK.
- **Prochaine étape** : En attente d'instructions de l'utilisateur (ex: résoudre BUG-012, analyser les logs, ou implémenter une nouvelle fonctionnalité).

### 2026-07-06 — Session orchestrateur (Problème Réseau)
- **Analyse** : Les tunnels ADB Reverse avaient "sauté" (probablement déconnexion USB ou crash ADB), causant l'impossibilité pour le téléphone de joindre l'API locale (`127.0.0.1:5001`), l'IA locale (`8888`) et Firebase Emulators.
- **Action** : Restauration des tunnels réseaux (tcp:5001, tcp:8080, tcp:9099, tcp:8888).
- oMLX : ✅ UP (port 8888).
- **Prochaine étape** : L'utilisateur peut retester l'application sur le Pixel 10.

### 2026-07-05 — Session Analyse Logs Huawei (via IA locale)
- oMLX : ✅ UP (Analyse réussie)
- Logs Huawei (22X7N19504005360) analysés : 
  - **BUG-016** : Résolution DNS (✅ Écarté, le téléphone n'était initialement pas connecté à internet).
  - **BUG-017** : Violation de permission de localisation par `com.huawei.hwid` (⚠️ Ignorable, composant système Huawei appelé indirectement sans impact sur notre app).
  - **Conclusion** : Après reconnexion à internet et relance des logs, aucune erreur ou crash de `com.karmicgochara.app` n'a été détecté. L'application est stable sur le Huawei.

### 2026-07-05 — Session Analyse Logs (Firebase OK)
- oMLX : ❌ DOWN (Erreur de connexion port 8888, analyse via logcat manuelle)
- Firebase Emulators & Flask API relancés sur le host, tunnels ADB Reverse validés.
- Logs Pixel 10 analysés : Le problème "Firebase Error" est ✅ RÉSOLU. L'application se connecte bien à l'API (`/register` et `/api/profile` renvoient 200 OK) et à l'émulateur Firebase Auth.
- Seules les erreurs bénignes de connexion au port 8888/11434 pour l'IA locale sont présentes.

### 2026-07-05 — Session Restauration Commit
- oMLX : ✅ UP (Analyse réussie)
- Bugs corrigés :
  - **Git (P1)** : Les fichiers sources n'étaient pas commités.
  - **Rebuild** : Astro a été recompilé et Capacitor synchronisé.
  - **Perte de documentation** : Restauration de l'historique complet des fichiers `.md` supprimés par inadvertance.
- Build : OK (Astro + Capacitor Sync)
- Deploy : commit `dfa284d` → Cloud Run live
- Pixel 10 : OK (Logs valides, aucun asset manquant)
- Prochaine session : Continuer avec BUG-011 ou les problèmes P3 restants.

### 2026-07-03 (Session 2) — Intégration Réglages & Correctif Synthèse
- oMLX : ✅ UP (oMLX port 8888)
- ✅ **Correction Permission Android Scoped Storage** : Remplacé le répertoire public `Downloads` par le répertoire privé de l'application `getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)` dans [GemmaSynthesisPlugin.java](file:///Users/jero87/karmic.gochara/android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java). Cela évite les erreurs Android `PERMISSION_DENIED: open() failed` lors de la lecture du fichier du modèle Gemma local.
- ✅ **Intégration du SettingsModal** : Importé et rendu le modal de paramètres dans `AppLayout.astro`, et ajouté un bouton accessible `⚙️ Réglages & IA` sur le tableau de bord pour permettre d'activer/désactiver l'IA locale (oMLX) en un clic.
- ✅ **Correction Refus LLM Synthèse** : Remplacé les contraintes négatives absolues dans `ai_interpret.py` par une consigne positive et constructive. Cette modification a été poussée sur `main` pour mettre à jour la production via Google Cloud Build.
- ✅ **Validation sur Appareil** : Construit et installé le build mis à jour sur le Pixel 10. Testé l'affichage du modal de paramètres et le basculement avec succès de l'IA locale.

### 2026-07-03 — Session Validation Production sur Appareil
- oMLX : ✅ UP (oMLX port 8888)
- ✅ **Lancement des Services locaux** : Démarrage des émulateurs Firebase (Auth + Firestore) et du serveur Flask API sur les ports correspondants.
- ✅ **Redirection ADB Reverse** : Activation des tunnels réseaux pour le Pixel 10.
- ✅ **Correction Scripts Astro** : Ajout de scripts explicites `build:prod` et `sync:prod` pour forcer `PUBLIC_FIREBASE_EMULATOR=false` lors de la génération d'assets de production.
- ✅ **Validation sur Appareil** : Compilation, désinstallation de l'ancienne version incompatible, puis installation et démarrage réussi en mode production. L'authentification Google s'est effectuée instantanément et a chargé avec succès la page "Carte Astrale" et ses données.

### 2026-07-02 — Session Déploiement Production (Correctif Émulateur & RAG OKF)
- oMLX : ✅ UP (oMLX port 8888)
- ✅ **Correction de la Pollution Émulateur** : Nettoyage du dossier `www/` en compilant Astro en mode production pure (`PUBLIC_FIREBASE_EMULATOR=false npm run build`), évitant que la prod ne pointe vers `127.0.0.1`.
- ✅ **Intégration OKF en Production** : Forcé l'ajout du dossier `karmic_vault/okf/` dans git (auparavant bloqué par le `.gitignore` du dossier parent `karmic_vault/`).
- ✅ **Support multilingue des planètes** : Ajout d'une table de traduction dans `load_okf_file` pour mapper les clés de planètes en anglais (ex: Saturn, Moon) vers les fiches OKF françaises (saturne, lune).
- ✅ **Pipeline CI/CD** : Poussé les modifications sur `main` pour déclencher le déploiement sur Google Cloud Run.
- ✅ **Vérification** : Validation du chargement sélectif des fiches OKF confirmée localement via `test_okf_vault.py`.

### 2026-07-02 — Optimisation RAG OKF (Open Knowledge Format)
- oMLX : ✅ UP (oMLX port 8888)
- ✅ **Migration OKF** : Conversion des mots-clés de planètes/aspects/nakshatras de formats legacy bruts vers des fiches Markdown + YAML frontmatter normalisées OKF sous `karmic_vault/okf/`.
- ✅ **Chargement sélectif dans l'API** : Modification de `_load_vault` dans `ai_interpret.py` pour analyser le thème natal (`user`) et les transits/aspects actifs (`chart_data`), et charger uniquement les fiches OKF correspondantes.
- ✅ **Réduction des tokens** : Économie de plus de 50% de prompt tokens par rapport à la méthode legacy (~2 300 tokens au lieu de ~5 500 tokens).
- ✅ **Validation** : Test unitaire et fonctionnel validé via `test_okf_vault.py`.


### 2026-07-01 — Session orchestrateur (check logs local IA)
- oMLX : ✅ UP (Analyse des logs réussie)
- Logs Pixel 10 analysés :
  - **BUG-013** : `App-specific configuration not found` (PackageConfigPersister).
  - **BUG-014** : Spanner : `No data was found for the table autofill-domain-predictions-prod-spanner`.
  - Le bug `pVM is not available` (BUG-012) est toujours présent.

### 2026-07-01 — Session orchestrateur (Registration & UI Fix)
- ✅ L'application était bloquée sur l'écran de login suite à la création du compte à cause d'une désynchronisation de Capacitor.
- L'exécution de `npm run sync:capacitor` et le redéploiement d'Android ont résolu ce problème. La redirection fonctionne désormais.
- ✅ Le menu de navigation du haut a été corrigé pour corriger la tautologie `Gochara` et rendre le lien "Chat Karmique" visible. ("Tableau" -> "Accueil", "Lecture" -> "Gochara").
- ✅ L'accès aux pages *Carte Astrale* et *Chat Karmique* a été vérifié manuellement (et visuellement par ADB) et fonctionne avec succès.
- Le fichier `lecture.astro.bak` a été supprimé.
- ✅ Analyse des logs (manuelle car IA Locale ❌ DOWN) : Aucun crash ou anomalie récent détecté. L'application est stable.
- Il reste à faire :
  1. Résoudre BUG-011 (RevenueCat) - (L'utilisateur a précisé que ce n'est pas urgent).
  2. Tester le profil/lecture.

### 2026-07-01 — Session update orchestrateur
- oMLX : ✅ UP (gemma-4-E2B-it-qat-oQ4-fp16)
- Diagnostic complet réalisé (Phase 0)
- Fichiers modifiés non commités : lecture.astro, apply_local_ai.py, www/*
- Priorité suivante : clé RevenueCat (P1)
- Pixel 10 : connecté (55161FDCH0004E)

### 2026-07-01 — Session orchestrateur (check logs)
- oMLX : ❌ DOWN (Analyse logs échouée, fallback manuel effectué)
- Logs Pixel 10 analysés : Aucun crash critique de l'application. Le bug mineur `pVM is not available` (BUG-012, P2) persiste sans gravité. Le statut du remplacement d'app (REPLACED/REMOVED) est normal suite aux builds et installs successifs.
- Build actuel Astro : ✅ Intact (`www/app/` contient bien carte, chat, lecture, miroir).
- Pistes d'actions confirmées :
  1. Résoudre BUG-011 (Clé RevenueCat manquante).
  2. Nettoyer `lecture.astro.bak`.
  3. Reprendre BUG-004 sur `lecture.astro`.

### 2026-07-01 — Session orchestrateur (fix BUG-010)
- BUG-010 résolu : fallback `date.today()` dans `astro.py`
- Deploy : commit 492f579 → Cloud Run live

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

**IA Locale** : ✅ UP (port 8889)

### 2026-07-12 — Session Restauration après Crash (Conversation 34af16e0)
- **IA Locale (oMLX)** : ✅ UP (Modèle: `gemma-4-E2B-it-qat-oQ4-fp16` sur port 8889 testé avec succès).
- **Nettoyage de fichiers** :
  - Suppression de tous les anciens logs volumineux dans `scratch/`.
  - Nettoyage des captures d'écran et médias de la conversation plantée `34af16e0` (55 Mo libérés).
- **Services locaux** :
  - Relance réussie de l'API Flask sur le port 5001 (exécuté dans l'environnement virtuel `.venv`).
  - Validation du bon fonctionnement des émulateurs Firebase (Auth et Firestore sur 9099 / 8080).
  - Setup des redirections de ports ADB (`adb reverse`) pour le Pixel 10 et le Huawei.
- **Frontend** :
  - Recompilation complète d'Astro et synchronisation Capacitor effectuée (`npm run sync:capacitor`).
  - Lancement réussi de l'application sur le Pixel 10 (MainActivity démarrée, aucun crash).

### 2026-07-13 — Session de Résolution de Bugs (Bypass IA Locale & Test Buttons)
- **IA Locale (oMLX)** : ✅ UP (port 8889)
- **Modifications** :
  - **LoginCard.astro** : Restauration des boutons de "Mode Test" en mode émulateur pour permettre l'authentification hors-ligne sans nécessiter de comptes Google actifs sur l'appareil.
  - **lecture.astro** : Correction du bug de blocage de l'application natif par la carte de téléchargement du modèle local Gemma 4 (2.58 Go). Désormais, si l'IA locale n'est pas configurée en mode `native` (le mode par défaut étant `cloud`), l'utilisateur accède directement à la page de génération de lectures quotidiennes via l'API réseau/Cloud.
- **Déploiement et Validation** :
  - Exécuté `npm run sync:emulator` pour compiler l'application en mode émulateur et synchroniser les ressources de Capacitor.
  - Désinstallé l'ancienne version défectueuse (`INSTALL_FAILED_UPDATE_INCOMPATIBLE`) et installé proprement le nouvel APK via gradle sur le Pixel 10 Pro.
  - Effectué un reverse des ports adb (5001, 8080, 9099, 8889) pour s'assurer que le Pixel 10 Pro communique correctement avec les émulateurs locaux et l'API Flask.
  - Testé visuellement via ADB le flux complet : création d'un compte test, connexion instantanée, et affichage réussi de la lecture du jour sans blocage.

### 2026-07-14 — Session de Diagnostic & Résolution du Streaming (SSE)
- **IA Locale (oMLX)** : ✅ UP (port 8889)
- **Modifications** :
  - **.env.local** : Changé `PUBLIC_FIREBASE_EMULATOR=true` pour restaurer les boutons de test et l'authentification locale pour l'émulateur sur le Pixel 10.
  - **capacitor.config.json** : Désactivé le proxy global de `CapacitorHttp` (`enabled: false`) pour empêcher l'interception et le buffering automatique des requêtes de streaming SSE (Server-Sent Events) par le natif, tout en conservant l'usage explicite de `CapacitorHttp.request` pour les appels REST de l'API.
- **Déploiement et Validation** :
  - Recompilé le frontend Astro et resynchronisé Capacitor (`npm run sync:capacitor`).
  - Désinstallé l'ancienne version incompatible sur le Pixel 10 puis réinstallé proprement le nouvel APK compilé.
  - Testé de bout en bout via ADB : connexion avec le compte test, navigation vers le dashboard, clic sur l'onglet Gochara.
  - **Résultat** : La lecture quotidienne s'affiche et se met à jour en temps réel par streaming SSE sur l'écran du Pixel sans blocage.


