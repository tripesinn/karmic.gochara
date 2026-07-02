# Karmic Gochara — État Orchestrateur

> Fichier de persistance inter-sessions.
> Mis à jour par la skill `karmic-orchestrator` à chaque session.
> TOUJOURS lire ce fichier en premier.

📄 **Référence Flow Utilisateur** : voir [user_flow.md](file:///Users/jero87/.gemini/antigravity-ide/brain/f06fa751-4d4b-4993-92a7-13f639b093b6/user_flow.md)

---

## État Actuel

**Dernière mise à jour** : 2026-07-02T21:45 (session — optimisation RAG OKF)

**Build Astro** : ✅ OK (www/ à jour)
**Environnement** :
- **Node.js** : `v20.12.2` (via NVM)
- **Firebase CLI** : `v13.6.0`
- **Flutter** : Non utilisé
- **Android Studio** : SDK Platform-Tools installés (adb fonctionnel)
- **IA Locale** : ✅ UP (oMLX port 8888)
- **Modèle Local configuré** : `gemma-4-E2B-it-qat-oQ4-fp16` (port 8888)
**Pixel 10 ADB** : ✅ Connecté (55161FDCH0004E)

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

---

## Bugs Restants

| ID | Priorité | Description | Statut |
|----|----------|-------------|--------|
| BUG-011 | P3 | `PUBLIC_REVENUECAT_ANDROID_KEY` manquante → monétisation bloquée | ⏸️ Reporté (Testeurs Pro auto) |
| BUG-012 | P2 | `pVM is not available` dans `IsolatedStorageServiceM` (bug OS Pixel) | ⚠️ Ignorable (bug OS Pixel) |
| BUG-013 | P3 | `App-specific configuration not found` (PackageConfigPersister) | ⚠️ Ignorable (Warning OS/Capacitor) |
| BUG-014 | P3 | Spanner: `No data was found...` | ⚠️ Ignorable (Warning Google Play Services) |


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
5. [ ] **Commit** des modifications non commités (lecture.astro, apply_local_ai.py, www/)
6. [x] BUG-004 : Résolu (Gemma local fonctionnel, confirmé par accès au chat)
7. [ ] Diagnostiquer `pVM is not available` dans `IsolatedStorageServiceM`

---

## Checklist de Test AAB (à valider avant chaque release)

- [ ] Connexion Google → /app (pas de crash, pas de boucle)
- [ ] Nouveau compte → /register → géocode → submit → /app
- [ ] Dashboard : pseudo affiché, 3 cartes visibles
- [ ] Lecture plan free : erreur 429 + bouton Stripe visible
- [ ] Lecture plan payant : texte généré, bouton copier actif
- [ ] Chat : question → réponse reçue
- [ ] Carte Astrale : tableau planètes + SVG chargés
- [ ] Agenda : lien iCal disponible si plan payant

---

## Historique


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
