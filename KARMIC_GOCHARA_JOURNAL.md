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
*   **Dépôt Distant (Origin)** : Tous les commits locaux (incluant l'intégration `localV1`, les correctifs de modal de paramètres, et l'intégration mobile des assets statiques) ont été poussés sur la branche `main` avec succès.


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

### Prochaines étapes
*   [ ] Refactorer `app.py` en blueprints Flask (3081 lignes → modules)
*   [ ] Commiter et pusher les changements de cette session
*   [ ] Audit Osteo 4D (projet secondaire)