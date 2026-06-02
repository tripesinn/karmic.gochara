# Analyse de app.py (3094 lignes) — Plan de découpage en Blueprints Flask
# Projet Karmic Gochara
# Date: 2026-06-02

================================================================================
1. LISTE EXHAUSTIVE DES ROUTES FLASK (40 routes)
================================================================================

Lignes   Méthode  Chemin                                Handler
------   ------   ------                                -------
 L805    GET      /sw.js                                service_worker
 L810    GET      /privacy                              privacy
 L815    GET      /.well-known/assetlinks.json           assetlinks
 L833    GET      /                                     index
 L868    POST     /set_lang                             set_lang
 L877    POST     /login                                login
 L970    POST     /register                             register
L1083    GET      /chart/karmic.svg                     karmic_chart_svg
L1144    POST     /chart/interpret                      interpret_chart
L1211    POST     /logout                               logout
L1219    GET      /geocode                              geocode
L1257    POST     /v2/calculate                         calculate_v2
L1389    POST     /calculate                            calculate
L1549    POST     /hook/transit                         hook_transit
L1778    POST     /send_synthesis                       send_synthesis
L1873    POST     /synthesis/prompt                     synthesis_prompt
L2085    PATCH    /api/v1/user/alert-preferences        alert_preferences
L2104    GET      /api/v1/user/alerts/history           alert_history
L2119    POST     /api/v1/transit-alert                 trigger_transit_alert
L2173    GET      /chat/status                          chat_status
L2186    POST     /chat/ask                             chat_ask
L2272    POST     /toggle_alerts                        toggle_alerts
L2295    GET      /calendar                             calendar_route
L2318    GET      /report/annual                        annual_report
L2344    POST     /cron/daily                           cron_daily
L2365    POST     /alert/test                           alert_test
L2405    POST     /save_email                           save_email
L2429    POST     /expand                               expand
L2518    POST     /summarize_chat                       summarize_chat
L2577    POST     /stripe/checkout                      stripe_checkout
L2610    GET      /stripe/success                       stripe_success
L2620    POST     /api/complete_payment                 api_complete_payment
L2657    POST     /api/plan_check                       api_plan_check
L2683    GET      /api/profile                          api_profile
L2693    POST     /api/v1/karmic-analysis               karmic_analysis_orchestrator
L2778    POST     /stripe/webhook                       stripe_webhook
L2860    POST     /rate_synthesis                       rate_synthesis
L2946    GET      /content/daily                        content_daily
L2975    GET      /generate_task                        generate_task
L3023    POST     /api/prefetch_year                    prefetch_year


================================================================================
2. REGROUPEMENT PAR DOMAINE FONCTIONNEL
================================================================================

─── DOMAINE A : PAGES PUBLIQUES / STATIQUES (3 routes) ───
/                        GET     Page d'accueil (index.html)
/sw.js                   GET     Service Worker PWA
/privacy                 GET     Page politique de confidentialité
/.well-known/assetl...   GET     Android App Links (Deep Link)

─── DOMAINE B : AUTHENTIFICATION / SESSION (4 routes) ───
/login                   POST    Connexion par pseudo (crée une session)
/register                POST    Création de profil karmique
/logout                  POST    Déconnexion (vide la session)
/set_lang                POST    Changement de langue (fr/en/nl/it)

─── DOMAINE C : CALCUL ASTROLOGIQUE & SYNTHÈSE (4 routes) ───
/calculate               POST    Calcul + synthèse karmique (legacy, bloquant)
/v2/calculate            POST    Calcul + synthèse avec streaming SSE (optimisé)
/chart/karmic.svg        GET     Génération du thème natal SVG
/chart/interpret         POST    Interprétation IA de la carte karmique (PRO)

─── DOMAINE D : HOOK TRANSIT / STREAMING (1 route) ───
/hook/transit            POST    Hook 4 phrases en streaming SSE
                                 (Mirror → Wound → Friction → Open Door)

─── DOMAINE E : SYNTHÈSE / PROMPTS POUR IA LOCALE (1 route) ───
/synthesis/prompt        POST    Construit system+user prompts pour inférence
                                 locale (Gemma/Edge AI). Contextes: synthesis,
                                 natal, conscience, signal

─── DOMAINE F : CHATBOT (3 routes) ───
/chat/status             GET     Quota et plan chatbot de l'utilisateur
/chat/ask                POST    Question chatbot (consomme quota, retourne
                                 prompts pour Gemma local)
/summarize_chat          POST    Résumé IA d'une conversation (plan Illimité)

─── DOMAINE G : ALERTES TRANSIT (5 routes) ───
/api/v1/user/alert-preferences  PATCH   Modifier les préférences d'alertes
/api/v1/user/alerts/history     GET     Historique des alertes reçues
/toggle_alerts                  POST    Activer/désactiver les alertes
/api/v1/transit-alert           POST    Admin : déclencher une alerte test
/alert/test                     POST    Test d'envoi d'alerte email

─── DOMAINE H : CALENDRIER & RAPPORT (2 routes) ───
/calendar                GET     Calendrier mensuel des transits (JSON)
/report/annual           GET     Rapport PDF annuel

─── DOMAINE I : CRON / TÂCHES PLANIFIÉES (1 route) ───
/cron/daily              POST    Exécution quotidienne des alertes transit
                                 (protégé par CRON_SECRET)

─── DOMAINE J : EMAIL (2 routes) ───
/send_synthesis          POST    Envoi de la synthèse par email (Resend)
/save_email              POST    Sauvegarde de l'email utilisateur

─── DOMAINE K : EXPAND (1 route) ───
/expand                  POST    "Alternative de Conscience" (1 clic gratuit,
                                 limité à 1/session)

─── DOMAINE L : PAIEMENT STRIPE (4 routes) ───
/stripe/checkout         POST    Créer une session Stripe Checkout
/stripe/success          GET     Page de succès après paiement
/api/complete_payment    POST    Vérifier et finaliser un paiement
/stripe/webhook          POST    Webhook Stripe (fallback si nav fermée)

─── DOMAINE M : API UTILITAIRES (4 routes) ───
/api/profile             GET     Profil utilisateur connecté
/api/plan_check          POST    Vérifier si un plan est en attente (cross-session)
/api/v1/karmic-analysis  POST    Orchestrateur d'analyse karmique complète
/api/prefetch_year       POST    Précalculer tous les transits d'une année

─── DOMAINE N : DATA / FEEDBACK / CONTENU (3 routes) ───
/rate_synthesis          POST    Notation 👍/👎 des synthèses (stockage Google Sheets)
/content/daily           GET     Signal du jour public (météo astrologique TikTok/Web)
/generate_task           GET     Générer un fichier .task JSON pour l'utilisateur


================================================================================
3. PLAN DE DÉCOUPAGE EN BLUEPRINTS
================================================================================

┌─────────────────────┬─────────────┬──────────────────────────────────────────┐
│ BLUEPRINT           │ Préfixe URL │ Routes                                    │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ public_bp           │ /           │ GET /, /sw.js, /privacy,                 │
│                     │             │ /.well-known/assetlinks.json              │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ auth_bp             │ /           │ POST /login, /register, /logout,         │
│                     │             │ /set_lang                                 │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ astro_bp            │ /           │ POST /calculate, /v2/calculate,          │
│                     │             │ GET /chart/karmic.svg,                   │
│                     │             │ POST /chart/interpret,                   │
│                     │             │ POST /hook/transit,                      │
│                     │             │ POST /synthesis/prompt                   │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ chat_bp             │ /chat       │ GET  /chat/status                        │
│                     │             │ POST /chat/ask                           │
│                     │             │ POST /chat/summarize (ex /summarize_chat) │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ alerts_bp           │ /           │ PATCH /api/v1/user/alert-preferences     │
│                     │             │ GET   /api/v1/user/alerts/history        │
│                     │             │ POST  /api/v1/transit-alert              │
│                     │             │ POST  /toggle_alerts                     │
│                     │             │ POST  /alert/test                        │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ calendar_bp         │ /           │ GET  /calendar                           │
│                     │             │ GET  /report/annual                      │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ cron_bp             │ /cron       │ POST /cron/daily                         │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ email_bp            │ /           │ POST /send_synthesis                     │
│                     │             │ POST /save_email                         │
│                     │             │ POST /expand                             │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ payments_bp         │ /stripe     │ POST /stripe/checkout                    │
│                     │             │ GET  /stripe/success                     │
│                     │             │ POST /stripe/webhook                     │
│                     │ (api)       │ POST /api/complete_payment               │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ api_bp              │ /api        │ GET  /api/profile                        │
│                     │             │ POST /api/plan_check                     │
│                     │             │ POST /api/v1/karmic-analysis             │
│                     │             │ POST /api/prefetch_year                  │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ data_bp             │ /           │ POST /rate_synthesis                     │
│                     │             │ GET  /content/daily                      │
│                     │             │ GET  /generate_task                      │
├─────────────────────┼─────────────┼──────────────────────────────────────────┤
│ geocode_bp          │ /           │ GET  /geocode                            │
└─────────────────────┴─────────────┴──────────────────────────────────────────┘

Total : 12 blueprints

Note : les routes /api/complete_payment et /api/plan_check pourraient être
rattachées à payments_bp ou api_bp. Le choix ici est payments_bp pour
/complete_payment (car logique Stripe) et api_bp pour /plan_check
(car logique session cross-navigateur). À discuter.


================================================================================
4. DÉPENDANCES DE CHAQUE BLUEPRINT
================================================================================

BLUEPRINT         MODULES IMPORTÉS (dans les handlers)
─────────         ────────────────────────────────────
public_bp         Flask (render_template, send_from_directory)
                  LANGS (dict local), get_lang()

auth_bp           profiles (get_profile_by_pseudo, create_profile,
                  get_profile_by_email, pseudo_exists)
                  Flask (session, request, jsonify)

astro_bp          astro_calc (calculate_transits)
                  ai_interpret (get_synthesis, stream_synthesis, generate_ai,
                  _build_natal_context, build_prompt_only, build_prompt_natal,
                  build_prompt_conscience, build_prompt_signal, get_daily_signal,
                  HOOK_MODEL, _aspects_to_text)
                  svg_chart (implicite, via /chart/karmic.svg)
                  output_validator (SynthesisValidator)
                  profiles (consume_plan_synthesis, check_and_consume_daily_signal)
                  _enrich_profile_with_natal (helper local)

chat_bp           ai_interpret (build_prompt_chat, generate_ai)
                  profiles (get_chat_quota, consume_chat_question)

alerts_bp         transit_alerts (detect_transit_events, send_alert_email,
                  run_daily_alerts, find_next_major_transit_event,
                  send_next_event_alert_email)
                  profiles (set_alerts, get_profile_by_pseudo)

calendar_bp       calendar_calc (get_monthly_transits)
                  annual_report (generate_annual_pdf)

cron_bp           transit_alerts (run_daily_alerts)

email_bp          ai_interpret (_build_natal_context, generate_ai, HOOK_MODEL)
                  profiles (save_email_by_pseudo)
                  requests (Resend API)

payments_bp       stripe_payments (create_checkout_session,
                  verify_checkout_session, verify_webhook)
                  profiles (upgrade_plan, get_profile_by_pseudo)
                  transit_alerts (find_next_major_transit_event,
                  send_next_event_alert_email)
                  _fulfill_order (helper local)

api_bp            astro_calc (calculate_transits)
                  ai_interpret (get_synthesis, build_prompt_only)
                  profiles (implicite via session)
                  _enrich_profile_with_natal (helper local)

data_bp           ai_interpret (get_daily_signal)
                  astro_calc (calculate_transits)
                  build_task_file (build_task_file, extract_dominant_transit,
                  extract_natal_for_task)
                  gspread + google.oauth2 (Google Sheets)

geocode_bp        requests (Nominatim / Photon API)


================================================================================
5. CODE PARTAGÉ → MODULE COMMUN
================================================================================

Fichier proposé : app_common.py (ou core.py)

Contenu à extraire d'app.py :

  1. TRANSIT_LOC_DEFAULT (dict)      — Coordonnées par défaut (Paris)
  2. _SIGNS_FR (list)                — Noms des signes en français
  3. UNLIMITED_PSEUDOS (set)         — Pseudos sans limite de quota
  4. _pending_plan_updates (dict)    — Store mémoire cross-session paiements
  5. get_lang()                      — Négociation langue Accept-Language
  6. _enrich_profile_with_natal()    — Enrichissement profil avec données natales
  7. _fulfill_order()                — Mise à jour plan après paiement
  8. LANGS (dict)                    — Labels multilingues (fr/en/nl/it)
     → Alternative : dans un module i18n.py dédié

Ces helpers sont utilisés par 80% des handlers et doivent être importés
par tous les blueprints.


================================================================================
6. DÉPENDANCES EXTERNES GLOBALES (tous blueprints)
================================================================================

Tous les blueprints ont besoin de :
  - flask (Flask, request, session, jsonify, Response, render_template, ...)
  - logging_config (via app.logger)
  - os.environ (variables d'environnement)
  - pytz (timezone)

Tous les blueprints utilisent session['profile'] comme source de vérité
utilisateur. La session est gérée par Flask, pas par un blueprint spécifique.


================================================================================
7. POINTS D'ATTENTION POUR LE REFACTORING
================================================================================

A. SESSION PARTAGÉE
   Tous les handlers lisent/écrivent session['profile'], session['lang'],
   session['expand_used'], session['payment_completed'].
   → Le découpage en blueprints ne change rien (Flask session est globale).

B. IMPORT LAZY (dans les handlers)
   De nombreux handlers font `from profiles import ...` ou
   `from ai_interpret import ...` à l'intérieur de la fonction.
   → À conserver pour éviter les imports circulaires, ou à déplacer
   en haut du fichier blueprint si pas de circularité.

C. ROUTES EN DOUBLON
   /calculate et /v2/calculate font la même chose (calcul + synthèse).
   /v2/calculate est la version optimisée avec streaming.
   → À terme, supprimer /calculate ou le rediriger vers /v2/calculate.

D. ROUTE /generate_task EN DOUBLE
   La route existe dans app.py (L2975) ET dans build_task_file.py (L412).
   → Vérifier laquelle est réellement utilisée, supprimer le doublon.

E. STRIPE WEBHOOK — CODE MORT
   Le code après L2830 (return) n'est jamais atteint.
   → Nettoyer lors du refactoring.

F. TAILLE DU FICHIER
   LANGS (dict) occupe ~700 lignes (L116-L788).
   → À externaliser dans i18n.py.

G. DÉCOUPAGE SUGGÉRÉ DE L'ARBORESCENCE
   karmic.gochara/
   ├── app.py                    # ~50 lignes : create_app(), register blueprints
   ├── app_common.py             # Helpers partagés
   ├── i18n.py                   # LANGS dict
   ├── blueprints/
   │   ├── __init__.py
   │   ├── public.py
   │   ├── auth.py
   │   ├── astro.py
   │   ├── chat.py
   │   ├── alerts.py
   │   ├── calendar_bp.py
   │   ├── cron_bp.py
   │   ├── email_bp.py
   │   ├── payments.py
   │   ├── api.py
   │   ├── data.py
   │   └── geocode.py
   ├── [modules existants inchangés]
   │   ├── astro_calc.py
   │   ├── ai_interpret.py
   │   ├── profiles.py
   │   ├── transit_alerts.py
   │   ├── stripe_payments.py
   │   ├── calendar_calc.py
   │   ├── annual_report.py
   │   ├── svg_chart.py
   │   ├── synthesis_pipeline.py
   │   ├── output_validator.py
   │   ├── build_task_file.py
   │   ├── logging_config.py
   │   └── ...
   └── templates/                # Jinja2 templates