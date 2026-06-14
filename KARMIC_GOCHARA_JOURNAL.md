# Journal de Projet : Karmic Gochara (Gochara App)

## 1. Métadonnées du Projet

*   **Nom du Projet** : Karmic Gochara (Gochara App)
*   **Hébergement API** : Google Cloud Run (service `gochara-api`)
*   **Builds Mobiles** : iOS (Capacitor) & Android (Capacitor)
*   **Version / Date** : Mai 2026


## 2. Stack Technique du Projet

*   **Backend** : Python Flask (`app.py`), sqlite3 / structures locales
*   **Frontend** : HTML5, CSS Vanilla (Thème astrologique sombre et or)
*   **Mobile Framework** : Capacitor.js (Synchronisation du dossier `www`)
*   **Moteur d'IA** :
    *   **Cloud** : Google Gemini / Anthropic Claude / Groq
    *   **IA Locale** : Modèle `phi-4` s'exécutant sur le Mac de l'utilisateur via vLLM
    *   **Pont Cloud-Local** : URL de tunnel ngrok saisie par l'utilisateur


## 3. Changements Majeurs Récents

### Paramètres de l'IA Personnelle & de Routage
*   **Sauvegarde & Clés Personnelles** :
    - Restauration complète des champs d'édition d'IA (Serveur Local, Gemini, Claude, Groq, OpenRouter) dans le modal de paramètres.
    - Correction de la persistance locale (`KarmicStore`) pour les clés d'API et les modèles personnalisés.

*   **Routage Individuel & Isolation des Coûts** :
    - Mise à jour de la fonction de routage pour préserver à 100% les clés et modèles personnalisés des utilisateurs PRO.
    - Blocage du repli (fallback) invisible sur le compte payant du serveur. Si la clé personnelle de l'utilisateur ou sa connexion locale échoue, l'application renvoie un message explicatif clair au lieu d'impacter le budget cloud du serveur.

### Correctifs de la Version Mobile (Capacitor Build)
*   **Affichage Unconditionnel des Paramètres** :
    - Retrait complet des restrictions Jinja (`{% if session_profile %}`) autour de l'icône de paramètres `⚙️` et de l'option de téléchargement hors-ligne dans `templates/index.html`.
    - Les fonctionnalités sont désormais visibles et fonctionnelles pour les utilisateurs de l'application statique/mobile (qui n'ont pas de session serveur Jinja active).

*   **Intégration du Dossier Statique dans le Dossier de Build (`www/`)** :
    - Résolution d'un bug critique où le dossier `/static` (contenant `app.js` et `style.css`) n'était pas présent dans le dossier de build `www/`.
    - Mise à jour de `render_static.py` pour copier automatiquement et de manière robuste le dossier `/static` vers `www/static`.
    - Permet le chargement complet des scripts et styles indispensables dans les environnements mobiles et résout le dysfonctionnement silencieux d'actions comme `openSettings()`.


## 4. État des Livraisons (Git Commits & Push)

*   **Statut Local** : Propre.
*   **Dépôt Distant (Origin)** : Tous les commits locaux poussés sur branche `main`.


## 5. Prochaines Étapes Planifiées

*   **Validation Mobile** :
    - Tester l'ouverture du modal de paramètres et le chargement des styles CSS sur un simulateur iOS/Android après compilation de Capacitor.

*   **Optimisation Hors-Ligne** :
    - Valider le bon fonctionnement du téléchargement des années de calcul astronomique locales (`Mode Hors-Ligne`) sur mobile sans connexion internet.


## 6. Session Hermes — 31 Mai 2026

Première session de travail avec l'agent Hermes (DeepSeek v4 Pro).
Objectif : analyse proactive + nettoyage + industrialisation du projet.

### Audit & Nettoyage
*   **Nettoyage du workspace** :
    - 16 scripts expérimentaux archivés dans `.archive/scratch_20260531/`
    - 16 fichiers supprimés de la racine (test_*.py obsolètes, karmic_prompt_*.txt, cookie.txt, Procfile.txt, gunicorn_test.log)
    - Conservé : `test_flows.py` (vrai test unitaire Flask)
*   **Bugs corrigés dans `app.py`** (détectés par ruff) :
    - `import json` manquant au module level → ajouté
    - `stream_synthesis` non importé → `from ai_interpret import stream_synthesis` ajouté
    - `Response`, `stream_with_context` absents de l'import Flask → ajoutés
    - Clé `pillar3_title` en double dans le dict EN → supprimée
    - `user_lang` → `session.get("lang", "fr")` dans la fonction register
    - Variables inutilisées retirées (`last_exc`, `hook_model`, `mars_t`, etc.)
    - Variable `exc` correctement capturée dans la closure `err_stream()`

### Industrialisation
*   **CI/CD** : `.github/workflows/ci.yml` créé
    - Déclencheurs : push + PR sur main
    - Job lint : ruff --select F (bloquant) + ruff complet (info) + mypy (info)
    - Job test : pytest sur test_flows.py
*   **Formatters / Linters** : `pyproject.toml` enrichi
    - ruff configuré (py312, line=120, sélection E/F/I/UP/B/SIM)
    - mypy configuré (implicit_optional, ignore_missing_imports)
*   **Logging structuré** : `logging_config.py` créé
    - Format JSON natif Cloud Run (CloudRunJsonFormatter)
    - Middleware Flask de timing HTTP (méthode, chemin, statut, durée)
    - Intégré dans app.py (3 lignes)
    - Zéro dépendance externe
*   **Package Python** : projet rendu pip-installable
    - `__init__.py` à la racine, dans `karmic_vault/`, dans `scripts/`
    - `pyproject.toml` : sections [project], [build-system], [project.urls]
    - `pip install -e .` fonctionnel
*   **Dépendances** :
    - `requirements.txt` : versions pinnées (== au lieu de >=)
    - `requirements_bot.txt` fusionné
    - `.env.example` : 14 → 33 variables documentées (+LOG_LEVEL)
    - `requirements_bot.txt` conservé mais redondant

### Session du 01/06/2026 — Configuration Hermes Agent + Skill Routeur Hybride

*   **Optimisation DeepSeek (config.yaml)** :
    - `enable_context_caching: true` — cache contextuel serveur activé
    - `context_length: 32768` — fenêtre glissante 32k tokens
    - `max_tokens: 4096` — limite par requête
    - `tool_output.max_lines: 100` — sortie terminal plafonnée
    - `browser.mode: markdown_only` — extraction texte seul (pas de HTML)
*   **Skill hybrid-local-router** (~/.hermes/skills/mlops/hybrid-local-router/) :
    - Adapté depuis le plugin Antigravity 2.0 (https://github.com/tripesinn/hybrid-local-router)
    - Route proactivement les tâches lourdes (refactoring, synthèse, traduction, parsing, doc) vers le LLM local Qwen3.5-9B-MLX (port 8000)
    - Fallback automatique vers DeepSeek Cloud si serveur local indisponible
    - Script `query_local_llm.py` inclus dans `references/`
*   **Bug découvert** : `hermes config set` écrase tout le fichier au lieu de merger → règle : ouvrir Xcode pour toute modif de config

### 6 Juin 2026 — Optimisation LLM Local + Routeur 3 Tiers + agent-router

*   **Problème découvert** : le proxy `ollama_proxy.py` sur port 8000 traduisait `phi-4-4bit` → `Qwen2.5-Coder` au lieu du vrai modèle phi-4 (depuis des mois)
*   **Correction** : `ollama_proxy.py` → `phi-4-4bit` → `phi4` (Ollama, 9.1GB, réel)
*   **Modèles Ollama** : Qwen2.5-Coder + mistral-nemo arrêtés, plus que **phi4 seul** chargé (économie ~12GB RAM)
*   **mlx_lm.server** tenté mais ne charge pas correctement (auth HF, temps morts) — reste sur Ollama + proxy
*   **Skill `hybrid-local-router` patché** : simplifié, méthodes unifiées, references mises à jour
*   **Ollama Cloud API key** sauvegardée dans `.env` (`OLLAMA_CLOUD_API_KEY`)
*   **Routeur 3 tiers activé** dans le prefill profil dev :
    1. **phi4 local** (proxy 8000, gratuit)
    2. **Ollama Cloud** (gratuit, 5M tokens/sem) — DeepSeek v4 Flash pour quotidien
    3. **OpenRouter** (payant) — backup + modèles chers (DS v4 Pro, Gemini pour Android)
*   **agent-router** (`~/bin/agent-router`) : script pour appeler local/cloud/pro/gemini/hermes avec la bonne API
*   **token-tracker** (`~/bin/token-tracker`) : DB SQLite de suivi conso tokens, avec `token-tracker report 7|30`
*   **Cron hebdo** : rapport conso tokens chaque lundi 9h
*   **À faire** : `ollama signin` sur le Mac pour activer le compte cloud, tester l'URL exacte de l'API, modifier `agent-router` pour auto-logger les appels dans token-tracker

### Prochaines étapes
*   [ ] `ollama signin` + tester endpoint Ollama Cloud
*   [ ] Modifier `agent-router` pour auto-logger dans `token-tracker`
*   [ ] Audit Osteo 4D
*   [x] Refactorer `app.py` en blueprints Flask (3081 lignes → modules)
*   [ ] Commiter et pusher les changements de cette session
*   [ ] Audit Osteo 4D (projet secondaire)

### 2 Juin 2026 — Deploy API pour Hybrid Local Router
*   **Pushé sur** `tripesinn/hybrid-local-router` (commits `cb4fff3` + `643fc25`)
*   **`scripts/deploy_api.sh`** : déploiement multi-backend du serveur LLM local (oMLX, Ollama, vLLM)
*   **`skills/hybrid-local-router/SKILL.md`** : remplacé par la version Hermes v2.0.2 (124 lignes au lieu de 47)
    - Routing Hermes natif (terminal+curl), multi-provider, provider babaudus, pitfalls
*   **`.env.example`** mis à jour, **README.md** modernisé (titre, overview, features)
*   Push via clé SSH `id_hybrid_router`

### 2 Juin 2026 — Refactoring Blueprints (app.py 3094 → 60 lignes)
*   **`i18n.py`** créé : LANGS multilingues extrait (fr/en/es/pt/de/nl/it, 674 lignes)
*   **`app_common.py`** créé : helpers partagés (TRANSIT_LOC_DEFAULT, _SIGNS_FR, UNLIMITED_PSEUDOS, _pending_plan_updates, get_lang, _enrich_profile_with_natal, _fulfill_order, get_hook_cta)
*   **12 blueprints Flask** créés dans `blueprints/` :
    - `public.py` (/, /sw.js, /privacy, /assetlinks.json)
    - `auth.py` (/login, /register, /logout, /set_lang)
    - `astro.py` (/calculate, /v2/calculate, /chart/*, /hook/transit, /synthesis/prompt)
    - `chat.py` (/chat/status, /chat/ask, /chat/summarize)
    - `alerts.py` (/toggle_alerts, /alert/*, /api/v1/alert*)
    - `calendar.py` (/calendar, /report/annual)
    - `cron.py` (/cron/daily)
    - `email.py` (/send_synthesis, /save_email, /expand)
    - `payments.py` (/stripe/*, /api/complete_payment)
    - `api.py` (/api/profile, /plan_check, /v1/karmic-analysis, /prefetch_year)
    - `data.py` (/rate_synthesis, /content/daily, /generate_task)
    - `geocode.py` (/geocode)
*   **`app.py`** réécrit : 3094 → 60 lignes (create_app() + 12 register_blueprint)
*   `app.logger` → `current_app.logger` dans tous les blueprints
*   `ANALYSE_BLUEPRINTS.md` conservé comme documentation du plan de découpage
*   **Bug `run_daily_alerts` corrigé** : la fonction avait été supprimée de `transit_alerts.py` par le commit `71ed65a` (mai 2026) mais la route `/cron/daily` y référençait toujours. L'import lazy dans l'ancien `app.py` masquait l'erreur ; le passage en top-level dans le blueprint l'a révélée. Restauré depuis l'historique git + import lazy dans `cron.py`.

### Prochaines étapes
*   [x] Commiter et pusher les changements de cette session (refactoring + fix)
*   [ ] Audit Osteo 4D (projet secondaire)

### 2 Juin 2026 — Hotfix Render : gunicorn introuvable
*   **Bug** : `karmicgochara.app` retournait 500 ("error finding executable 'gunicorn' in PATH")
*   **Cause** :
    1. `render.yaml` utilisait `gunicorn app:app` (bare) — Render native Python ne résolvait pas le PATH du venv
    2. `requirements.txt` et fichiers projet en CRLF (`\r\n`) — pip pouvait échouer silencieusement sur Render Linux
*   **Correctifs** :
    - `render.yaml` : `gunicorn` → `python -m gunicorn` (startCommand)
    - `requirements.txt`, `render.yaml`, `astro_calc.py` : convertis CRLF → LF
    - Commit 704d574 pushé sur `origin/main`
*   **Note** : Le commit 704d574 a trigger un build Cloud Run (gochara-api europe-west1)
    mais 503 — vrai bug : Python 3.10 (Dockerfile) vs `datetime.UTC` (Python 3.11+)

### 2 Juin 2026 — Hotfix Cloud Run : Python 3.10 → 3.12
*   **Vrai bug** (Cloud Run logs) : `ImportError: cannot import name 'UTC' from 'datetime'` — `datetime.UTC` n'existe qu'à partir de Python 3.11
*   **Cause** : Dockerfile utilisait `python:3.10-slim` mais `logging_config.py` (session 31 mai) importe `from datetime import UTC`
*   **Correctif** : Dockerfile → `python:3.12-slim`
*   **Commit** `7d8e75c` — Cloud Build rebuild auto
*   **Résultat** : gochara-api (europe-west1) ✅ HTTP 200

### 2 Juin 2026 — Optimisation Cloud Build : layer caching
*   **Trigger auto-généré** GCP utilisait `--no-cache` → builds de ~15 min
*   **Nouveau trigger** Cloud Build avec `--cache-from` (Artifact Registry) + machine E2_HIGHCPU_8
    - Build step : pull `:latest` comme cache, build avec cache, tag `$COMMIT_SHA` + `:latest`
    - Push + Deploy steps
    - Builds estimés à ~2-3 min (au lieu de 15)
*   **`cloudbuild.yaml`** commit `b074ece` dans le repo (documentation)
*   **Ancien trigger** avec `--no-cache` supprimé

### 2 Juin 2026 — Benchmark IA Astrologique Multi-Provider

*   **Nouveau bot** `x_benchmark_bot.py` :
    - Parse les mentions X.com au format `@bot MM/DD/YYYY HH:MM Ville` (réutilise le parsing existant)
    - Calcule le thème karmique via `astro_calc.py`
    - Appelle **Gemini / Claude / Grok / phi-4 local en parallèle** (threading)
    - Envoie les 3-4 interprétations en DM avec labels A/B/C/D
    - Collecte les votes des utilisateurs (réponse A/B/C)
    - Sauvegarde dans `benchmark_votes.json`
    - Génère une page HTML statique dans `benchmark_results/index.html`
    - Mode continu ou `--once` (cron)
*   **Route Flask** `/benchmark` dans `blueprints/public.py`
*   **Template** `templates/benchmark.html` (fallback + SEO: meta, OG)
*   **Cron Hermes** toutes les 5min (`Benchmark IA Bot X`) pour exécuter le bot en continu
*   **Migration locale** : phi-4-4bit activé dans oMLX (memory guard désactivé), provider `babaudus` mis à jour dans `config.yaml`, modèle par défaut dans `ai_interpret.py` corrigé
*   **Bug phi-4-4bit corrigé** : `ai_interpret.py` avait un if inversé qui choisissait Qwen même quand phi-4 était sélectionné. Le modèle dans la liste de sélection utilisait `mlx-community/phi-4-4bit` au lieu de `phi-4-4bit` (nom oMLX)
*   **Skills mis à jour** : `hybrid-local-router`, `cost-aware-orchestration`, `karmic-orchestrator` référencent maintenant `phi-4-4bit`

### 2 Juin 2026 — Sécurisation + Migration Hermes sur GCE

*   **Audit sécurité GCP** : découvert que `jerome@jeromemalige.fr` est **owner** du projet — blast radius total si Hermes compromis
*   **Profil `dev` créé** : clone du default avec terminal + cron réactivés. Le profil default a maintenant terminal et cron **désactivés** par défaut
*   **VM GCE créée** : `hermes-agent` (e2-micro, europe-west9-a, sans IP publique)
*   **Cloud NAT** configuré pour l'accès internet de la VM
*   **Hermes v0.15.2** installé via pip dans `~/hermes-venv/`
*   **Service Account dédié** : `sa-hermes-agent` avec rôles `logging.logWriter` + `artifactregistry.reader` (scope minimal)
*   **Cron benchmark migré** : supprimé du Mac, recréé sur la VM (toutes les 5min)
*   **Gateway installé** sur la VM (systemd user service, linger activé)
*   **WhatsApp bridge** : session et bridge copiés sur la VM — Hermes répond via WhatsApp

### Prochaines étapes
*   [x] ~~Déployer le benchmark bot sur un serveur (GCE) pour qu'il tourne 24/7~~
*   [ ] Promouvoir le bot X avec un tweet de lancement du benchmark
*   [x] ~~Audit Osteo 4D (projet secondaire)~~
*   [ ] Désinstaller Hermes du Mac (optionnel, VM opérationnelle)
*   [ ] Régénérer OAuth 1.0a tokens X.com (expirés → 401)
*   [ ] Ajouter knowledge_base.json étoffée pour Osteo 4D
*   [ ] Dockeriser Osteo 4D + déploiement Cloud Run

### 3 Juin 2026 — Reprise : X Auth + Audit Osteo 4D

#### X.com Benchmark Bot — Diagnostic
*   `_test_x_creds.py` → **401 Unauthorized** sur les OAuth 1.0a tokens (expirés/révoqués)
*   `_test_bearer2.py` → **OK** (OAuth 2.0 app-only auth fonctionne)
*   `xurl` : app `karmic-gochara-bot` enregistrée mais **aucun token sauvegardé**
*   **Conséquence** : le bot peut lire les mentions (bearer OK) mais **pas envoyer de DMs ni tweeter** (besoin OAuth 1.0a user context)
*   **4 fichiers test** créés puis archivés dans `.archive/`
*   `scripts/query_local_ai.py` : basculé sur Ollama (11434, mistral-nemo) pour test local
*   `astro_calc.py` : fix `datetime.UTC` → `timezone.utc` (Python 3.10 compat)

#### Audit Osteo 4D — Terminé
*   **Projet** : FastAPI + RAG simple (Gemini via `google-genai` SDK)
*   **Structure** : `main.py` (21 lignes), `rag_engine.py` (77 lignes), `knowledge_base.json` (5 entrées), `requirements.txt` (5 déps)
*   **Stack** : FastAPI + uvicorn + google-cloud-aiplatform + python-dotenv
*   **RAG** : matching par intersection de mots (basique), pas de vectorisation
*   **KB** : 5 concepts ostéo (MRP, fascias, biotenségrité, dysfonction, attracteur de Cantor)
*   **Déploiement** : aucun — tourne en local uniquement
*   **Points d'amélioration** : RAG à vectoriser (ChromaDB), KB à étoffer, Docker + Cloud Run

## Session 2026-06-06 — Routage hybride Hermes, Ollama Cloud Enterré

### Constats
- **phi4 jamais utilisé réellement** — bug proxy `ollama_proxy.py` traduisait `phi-4-4bit` → `Qwen2.5-Coder` depuis des mois. Patché.
- **Ollama Cloud Free = inutile** — `deepseek-v4-flash:cloud` → 403 (paywall Pro $20/mo). Pas de modèles utiles accessibles en Free. GPU-time vague, pas des tokens. Clé gardée dans `.env`, enterrée.
- **Ollama Pro $20/mo** = boîte noire (usage GPU, pas de décompte tokens). OpenRouter plus transparent (~$0.15/M tokens).
- **Free tiers cloud** (RelayFreeLLM, Ollama Cloud) → fragiles, quota ridicules, pas fiables en production.
- **30M tokens cramés sur 1 bug** (Antigravity 2.0) — confirmation que free tiers = piège.

### Changements
- **RAM libérée** : Qwen2.5-Coder + mistral-nemo arrêtés, plus que phi4 seul (~7.7GB, OK pour 16GB)
- **Skills mis à jour** :
  - `hybrid-local-router` v3.2.0-wip : strat par domaine (Xai/Google/local/OpenRouter), Ollama Cloud en urgence
  - `cost-aware-orchestration` v3.0.0-wip : idem, marqué WIP
  - `prefill.md` (profil dev) : free tiers = piège
- **agent-router** (`~/bin/agent-router`) — CLI pour appeler local/cloud/pro/gemini
- **token-tracker** (`~/bin/token-tracker`) — DB SQLite suivi conso, cron rapport hebdo
- **Ollama Cloud signé** — user `confident_hopper_582`, clé dans `.env`, base URL commentée (invalide)

### VM (e2-micro)
- Rôle confirmé : **benchmark X** (toutes les 5min) + **WhatsApp bridge** + **isolation sécurité**
- **Ne gère pas** Cloud Run (GitHub → Cloud Build, pas la VM)
- SA limité : `logging.logWriter` + `artifactregistry.reader`
- Pas de LLM local possible sur 1GB RAM
- Astro interpretations des testeurs → **Cloud Run + OpenRouter**, pas la VM

### À faire (quand devant le Mac)
- [ ] Tester que `agent-router local` fonctionne (phi4 en RAM)
- [ ] Premier `token-tracker report 7` dans ~1 semaine
- [ ] Trouver endpoint Xai Grok pour dédier à X.com
- [ ] Trouver endpoint Google Workspace Gemini
- [ ] Ajouter colonne `provider` au token-tracker pour distinguer local/OpenRouter/Xai/Google

---

## 9. Session Benchmark IA — 06/06/2026

Benchmark de 8 modèles sur les prompts DK (Doctrine Évolutive Synthétique).
Même thème (Jérôme, DK ayanamsa, CL Bélier Ashwini), 2 dates (06-07/06/2026).

### Classement final

| # | Modèle | Note | Point fort |
|---|---|---|---|
| 1 | Claude Haiku 4.5 | ★★★★★ | Seul à inférer la vie réelle du thème |
| 2 | gemma4:31b cloud | ★★★★★ | Doctrinal pur, format parfait |
| 3 | minimax-m3 | ★★★★☆ | Meilleure plume, images poétiques |
| 4 | Gemini 3.5 Flash | ★★★★☆ | Structuré, actionnable |
| 5 | Grok | ★★★★ | Solide, sans originalité |
| 6 | ChatGPT | ★★★★ | Bon mais générique sans historique |
| 7 | phi4 local | ★★★★ | 80% gemma, 1'39", local gratuit |
| 8 | Mistral Vibe | ★★★★ | Rapide, concis, sans faute |
| 9 | mistral-nemo | ★★☆ | Généralités, invente des planètes |

### Découvertes clés
- **Prompt lite (450 tok)** → seul gemma4 tient le format. Les autres dérivent.
- **Prompt cloud (~3000 tok)** → déverrouille tous les modèles. Plus contraint, meilleur suivi.
- **Règle "Traduction Obligatoire" + exemples** dans le vault → fait la différence sur le zéro-signes.
- **minimax-m3** : refuse sur lite, excellent sur cloud. Guardrails contournés par le format long.
- **Bug** : `_enrich_profile_with_natal()` utilise des maisons hardcodées. Toujours recalculer via Chandra Lagna.

### Site mis à jour
- Panneau benchmark → Claude Haiku 4.5 en tête, Ollama Cloud ajouté
- Fichier benchmark → `_prompts_gemma4_jero.md` (tableau complet + liens)
- Prompt cloud 07/06 → `_prompt_cloud_jero_0706.md`

### 7 Juin 2026 — Page benchmark enrichie + 3 tweets postés
- **Page /benchmark** réécrite : 9 modèles listés avec classement, notes, détails, découvertes clés (au lieu du template vide "en attente des votes")
- **Gemini corrigé** : 2.0 Flash → 3.5 Flash (index.html + www/index.html + benchmark.html)
- **X API OAuth2** configurée via token utilisateur @siderealAstro13 (droit écriture)
- **3 tweets postés** : classement général, surprise minimax-m3, pépite gemma4:31b cloud
- **Réponse détaillée** en reply avec les points forts des modèles

### 10 Juin 2026 — Session planning #1 (sponsor) + #2 (X bot GO-LIVE)

**Contexte** : Jérôme (siderealAstro13) veut transformer karmic.gochara en machine d'acquisition. Deux chantiers parallèles définis en début de soirée.

**État actuel** :
- Page karmicgochara.app/benchmark revenue au template vide (En attente des premiers votes, 0 votes) — pipeline de votes ne tourne pas
- xurl auth configurée dans le shell dev (sourcing /Users/jero87/karmic.gochara/.env) mais **API X renvoie 401** — OAuth1 user context expiré/révoqué
- X bot benchmark existe (x_benchmark_bot.py, 553+ lignes) mais le flow public "Tweet @karmicgochara DD/MM/YYYY HH:MM Ville → 3 DMs → vote → page" pas encore go-live

**#1 — Système sponsor** (pour testeurs app + users web, Jérôme paye, pub via X) :
- "Compte pro" existe déjà (blueprints/auth.py) mais logique inverse : user met SA clé
- Faut ajouter flag `users.sponsored` + override `ai_interpret.py` pour forcer clés serveur
- Surface : app Android en test fermé (≠ karmic-fdroid qui est F-Droid) + site karmicgochara.app
- À cadrer demain : nom exact du package Android test fermé

**#2 — X bot GO-LIVE** : lancé via delegate_task ce soir
- Audit x_benchmark_bot.py + VM/cron + tokens
- Fix 401 tokens
- Test end-to-end mention → DM → vote → page

**TODO créés** : 8 items (1, 1a-c, 2, 2a-c) — voir todo list session.

**Note de Jérôme** : "karmic-fdroid n'est pas l'app android en test fermé" — à investiguer ~/karmic.gochara/android/ pour le bon package.

**Prochaines étapes** (à l'aube des résultats delegate_task) :
- [ ] Review du rapport GOAL-2 (X bot) demain matin
- [ ] Confirmer nom package Android test fermé → finaliser wording GOAL-1
- [ ] Lancer GOAL-1 sponsor une fois wording validé

### 10 Juin 2026 (suite) — delegate_task GOAL-2 PARTIEL (timeout 600s)

**Statut** : subagent timeout après 37 calls et 600s. Pas de rapport final retourné. **Mais modifications code bien faites** (à reviewer et committer) :

**Changements détectés** (git status, en M, **PAS encore commités**) :
- `x_benchmark_bot.py` (+22 lignes) : ajout génération Bearer Token à partir de X_API_KEY/SECRET via POST /oauth2/token (OAuth2 client_credentials flow) — fallback si tokens user context 401
- `astro_calc.py` (+4) : probablement fix Python 3.10 compat (UTC)
- `scripts/query_local_ai.py` (+4) : idem
- `templates/benchmark.html` (+79) : enrichissement page benchmark
- `templates/index.html` (+40) : modifs UI
- `www/index.html` (+2) : sync
- `KARMIC_GOCHARA_JOURNAL.md` (+184) : cette entrée

**Fichiers archivés par subagent** (.archive/) :
- `_check_deps.py`, `_test_bearer.py`, `_test_bearer2.py`, `_test_x_creds.py` (tests exploratoires)

**Identifié** :
- App Android en test fermé = **`com.karmicgochara.app`** (appName "Karmic Gochara", Capacitor) dans `/Users/jero87/karmic.gochara/android/`
- `karmic-fdroid/` (workspace ~/) = F-Droid repo, bien différent

**Blockers restants** :
|- gcloud non auth dans ce shell (sheets-gochara SA, pas owner)
|- Tokens X toujours 401
|- Cron VM non audité
|- Flow end-to-end pas testé

---

## 12 Juin 2026 — Config Hermes + Tailscale VM↔Mac

**Infra / Config :**
- IAM SA `sa-hermes-agent` : ajouté `artifactregistry.reader` + `run.developer`
- `config.yaml` restructuré : provider `mlx-local` proprement défini dans `providers:` avec `type: openai` + `base_url`
- `model.default` corrigé → `mlx-community/Qwen3.5-4B-MLX-4bit` (match MLX exact)
- Web backends configurés : `portal` (backend), `firecrawl` (search/extract)
- `timezone: Europe/Paris`, `tirith_fail_open: false`
- Delegation : `nous` / `deepseek/deepseek-v4-flash` (Portal OAuth)
- `hermes config set` maintenant safe (bug fixé PR #27539)
- `mlx-server` script modifié : `--host 0.0.0.0` pour accès Tailscale

**Tailscale VM GCE ↔ Mac Mini :**
- Mac : `100.89.101.99`, VM hermes-agent : `100.123.177.38`
- MLX du Mac accessible depuis VM via `http://100.89.101.99:8888/v1`
- Auth VM : `sudo tailscale up` dans `tmux` pour survivre aux déconnexions SSH
- VM pourra utiliser MLX local comme provider délégué ou fallback

**Skills mises à jour :**
- `local-inference-setup` : config provider nommé, delegation Nous Portal, Tailscale
- `hermes-gce-deployment` : Tailscale setup + VM delegation xAI/Grok

**À faire demain matin (résumé) — Jérôme valide** :
1. `git diff` complet des modifs subagent → review + commit
2. Retester `x_benchmark_bot.py` avec nouveau bearer flow
3. SSH VM GCE (via IAP ou autre) → vérifier cron + gateway
4. Régénérer tokens X user context via dev.x.com si 401 persiste
5. Test mention réelle (compte test) → DM → vote → page
6. Wording final GOAL-1 : "Mode sponsor com.karmicgochara.app (Android test fermé) + karmicgochara.app (web), override ai_interpret.py pour forcer clés serveur, UI toggle + rate-limit"
7. Lancer GOAL-1 sponsor en parallèle de la suite GOAL-2

