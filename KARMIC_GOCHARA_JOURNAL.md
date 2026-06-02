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

### Prochaines étapes (fin mai)
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
*   **Note** : Cloud Run `gochara-api` est down (404). Render est l'hôte actif de karmicgochara.app derrière Cloudflare.

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

### Prochaines étapes
*   [ ] Déployer le benchmark bot sur le serveur (Render/Cloud Run) pour qu'il tourne 24/7
*   [ ] Promouvoir le bot X avec un tweet de lancement du benchmark
*   [ ] Audit Osteo 4D (projet secondaire)
