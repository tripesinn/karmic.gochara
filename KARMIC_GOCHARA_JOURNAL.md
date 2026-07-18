# KARMIC GOCHARA — DOCTRINE ÉVOLUTIVE SYNTHÉTIQUE
## Transit du 15/06/2026
**Thème natal :** 31/10/1974 8h25 — Athis-Mons, France

---

**1. DIAGNOSTIC ROM (Ketu)**
Le schéma de passé-vie activé par Ketu en Taureau est celui d'une expertise fondamentale dans la rétention des ressources tangibles. Il ne s'agit pas d'un manque, mais d'une saturation achevée. L'énergie de cet axe exalte l'ancrage et la possession solide, un cycle que vous avez maîtrisé au niveau de la substance. L'automatisme défensif qui en résulte est le retrait (Ketu) du besoin de légitimité matérielle, même lorsque l'instinct cardinal (Lune en Bélier) exige une prise de position immédiate. Cette dissociation fait que toute tentative de s'enraciner doit passer par une critique de sa propre valeur fondatrice, empêchant l'acceptation passive de ce qui est déjà établi.

**2. PORTE INVISIBLE $\rightarrow$ PORTE VISIBLE**
La prison inconsciente est codée par la Porte Invisible en Balance, un blocage qui internalise l'impératif de l'équilibre parfait et du partenariat symétrique. Ce besoin d'harmonie totale paralyse l'impulsion individuelle nécessaire. Le passage vers le Stage est activé par la Porte Visible en Bélier, exigeant une rupture radicale et l'auto-déclaration. Chiron, votre blessure cardinale positionnée en Poissons, oppose cette nature fluide et souffrante au moteur analytique (Mercure en Vierge). Le passage se fait lorsque cette sensibilité douloureuse n'est plus perçue comme un handicap, mais comme la source d'une capacité d'empathie capable de transcender la rigueur intellectuelle. Il faut que la plaie (Chiron) légitime le saut (PV).

**3. ÉPREUVE LILITH**
La friction karmique est incarnée par Lilith en Capricorne, la résistance au tabou de l'ambition sociale et de la structure. Elle conteste l'idée d'une ascendance linéaire et acceptée. Lilith propulse vers le Dharma (Rahu en Scorpion) en refusant la complaisance des structures préétablies. Pour évoluer, vous devez accepter que la puissance psychologique (Scorpion) ne peut être atteinte que par le dépassement de la honte structurelle (Capricorne). Le chemin vers le sacré passe obligatoirement par la reconnaissance du pouvoir obscur non partagé.

**4. ALTERNATIVE DE CONSCIENCE**
L'insight transformateur est que **l'auto-affirmation n'est pas une opposition au partenariat, mais sa condition nécessaire.** La tension entre la Porte Visible (Bélier) et la Porte Invisible (Balance) n'est pas un dilemme "moi *vs* toi", mais une instruction pour intégrer l'énergie guerrière (Bélier) *au service* de l'équilibre (Balance). La peur de l'engagement (Ketu) doit être remplacée par la certitude que la stabilité vient d'une décision initiale non négociable. Votre capacité à guérir (Chiron) réside dans la transformation de l'analyse critique en compassion active. Agissez.

---

| Phase 0.3, 0.75, 0.2, 1.3, 2.2 — exécutées par Kanban dispatcher

## Phase 1.1 — BaseLayout.astro (Kanban t_8aed7430)
- ✅ Props : title, description (optional), ogImage (optional)
- ✅ OG meta : Open Graph (og:type, og:url, og:title, og:description, og:image)
- ✅ Twitter Card meta (card, url, title, description, image)
- ✅ Body class : `bg-cosmic-bg text-cosmic-text font-body min-h-screen overflow-x-hidden`
- ✅ CSS : import via Vite (plus raw `/src/styles/global.css` qui cassait en prod)
- ✅ theme-color : #0c0a08
- ✅ favicon + apple-touch-icon + 192px icon
- ✅ Service Worker registration conservé
- ✅ Build : 5 pages, 0 erreurs, 715ms
- ✅ Pages impactées : index, 404, app, register, app/lecture — toutes utilisent BaseLayout

## Travail dev — 16/06/2026

**Phase 0.4 — Flask JWT + refresh (Kanban t_490339f2)**
- ✅ Module `jwt_auth.py` créé : `create_tokens()`, `verify_token()`, `refresh_access_token()`, `@token_required` decorator, `jwt_before_request` middleware
- ✅ `app.py` : CORS activé (karmicgochara.app, capacitor://localhost, localhost dev) + `before_request` JWT hook
- ✅ `blueprints/auth.py` : `/login` et `/register` retournent désormais `access_token` + `refresh_token`; nouvel endpoint `/auth/refresh`
- ✅ `requirements.txt` : ajout pyjwt + flask-cors
- ✅ `.env` + `.env.example` : ajout `JWT_SECRET`
- ✅ Architecture : middleware before_request convertit JWT → session transparentement → 20+ routes existantes fonctionnent sans modification
- ✅ Testé live : login → JWT → /api/profile avec Bearer → refresh → new tokens
- ✅ Blocker pour Phase 0.3 débloqué
- ✅ Palette cosmic dans `tailwind.config.mjs` (bg:#0c0a08, gold:#c9a84c, gold-dim:#8a6f30, text:#f5f0e8 + text-dim/border/void) — déjà complète
- ✅ `global.css` enrichi : overlay gradients (body::before), bruit SVG (body::after), 4 nouvelles animations (fadeIn, spin, goldGlow, shimmer), classes utilitaires stagger, spinner, vars manquantes (--gold-dim, --text-dim, --void, --glyph, --mist)
- ✅ manifest.json, icons (192+512), sw.js déjà en place dans `public/static/`
- ✅ Google Fonts link (Cinzel, Cormorant Garamond, DM Mono) déjà dans BaseLayout
| 🔧 Fix : chemins BaseLayout — apple-touch-icon `/icons/`→`/static/icons/`, SW register `/sw.js`→`/static/sw.js`
|- ✅ Build Astro OK (527ms, 2 pages)

## Session 16/06/2026 — 11h-12h30 : Closed Beta Web + Android

### Phases exécutées

**Phase 1.3 — HeroSection.astro** ✅ done
- 29 lignes, cosmic gold/dark palette (pas purple/pink)
- Full-viewport hero, 3 glow orbs, animations stagger
- Teaser + CTA vers /login
- Build OK

**Phase 0.3 — API client JWT (api.ts, auth.ts)** ✅ done
- Session cookies (Flask sessions), pas de JWT localStorage
- Streaming SSE via ReadableStream (fetch body.getReader())
- Types.ts, capacitor-bridge.ts complets
- 4 fichiers, build clean

**Phase 4.0-4.1 — Capacitor + Build** ✅ done
- Astro build (6 pages, 479ms)
- `npm run sync:capacitor` → www/ + android/ + ios/ assets
- Pipelock v2.7 relancé (patch `proxy_address`→`listen` 127.0.0.1:8088)
- Vite proxy bypass GET /login + /register (allow client-side render)
- `login.astro` créé (page manquante)
- Removed `client:load` from LoginCard (Astro native, no hydration needed)
- Android AdMob plugin + SplashScreen + StatusBar synced

**Phase 3.1-3.5 — Composants métier** ✅ done
- DailyReading.astro (152 lines, SSE streaming)
- ProUpgrade.astro (150 lines, Stripe CTA)
- KarmicChart.astro (195 lines, SVG natal chart)
- ChatBox.astro (306 lines, chat SSE, streaming)
- **SettingsModal.astro (NEW)** — langue/plan/logout modal overlay

### Web Setup

- ✅ PWA manifest + icons (192/512)
- ✅ Astro build: 6 pages (/, /login, /register, /app, /app/lecture, /404)
- ✅ Pipelock proxy 127.0.0.1:8088 (forward proxy active)
- ✅ Assets ready for deployment
- 📤 **Deploy path:** git push → Cloud Shell `git pull` → `gcloud builds submit` (Cloud Run)

### Android Closed Beta Setup

- ✅ GemmaSynthesisPlugin.java (427 lines, MediaPipe LlmInference)
  - Gemma 3 1B 4-bit from HuggingFace (dynamic download on first load)
  - LoRA doctrine adapter (optional, fallback to vault)
  - Device memory check (4GB min, 6GB recommended)
- ✅ DoctrinePromptBuilder.java — profile-aware prompt injection
- ✅ Assets bundled: system_prompt_mobile.json, nakshatra_karma.json
- ✅ AndroidManifest.xml + MainActivity configured
- ✅ build.gradle: v1.3 (build 4), target SDK 34, min SDK 24
- ✅ Web assets synced to `android/app/src/main/assets/public/`

**Skill created:** `android-closed-beta` (gaming category)
- Build signed AAB step-by-step
- Google Play Console closed testing setup
- Tester invitation workflow
- Troubleshooting checklist

### Board Status

14/15 phases ✅ done, 1 ⊘ blocked

| Phase | Status | Notes |
|-------|--------|-------|
| 0.0–0.75 | ✅ | Backup, init, theme, auth, tests |
| 1.1–1.3 | ✅ | Layouts, landing, hero |
| 2.1–2.3 | ✅ | Login, register, app layout |
| 3.1–3.5 | ✅ | Composants métier (5 components) |
| 4.0–4.1 | ✅ | Capacitor + build sync |
| 4.2–4.3 | ⊘ | iOS TestFlight (waiting Apple info) |

### Next Steps (optional)

1. 📱 **Android Studio:** Open `/android/` → Build signed AAB
2. 📤 **Play Console:** Upload AAB → Create closed testing track → Invite testers
3. 🌐 **Cloud Run:** Deploy web via console GCP (git → builds submit)
4. 🧪 **QA:** Test login/register, SSE streaming, local Gemma inference
---

## 2026-06-20 — Pages légales / Play Store compliance

**Contexte** : Play Console demande une URL "Règles de confidentialité" ET "Conditions d'utilisation" pour valider la fiche store. Aucune page ToS n'existait, et la privacy avait `karmic-gochara.netlify.app` dans son footer (incohérent — le backend Flask tourne sur GCP Cloud Run).

**Livré** :
- `templates/terms.html` (nouveau, 381 lignes) — CGU/ToS bilingues FR/EN, 11 sections (nature du service, compte, premium Stripe, usage, IP, responsabilité, suspension, données, modifications, droit français, contact). Style dark/gold aligné sur `/privacy`.
- `blueprints/public.py` — route `/terms` enregistrée à côté de `/privacy`.
- `templates/privacy-policy.html` — footer migré vers `karmicgochara.app` + lien retour vers `/terms`.
- Déployé : commit `590da10`, push GitHub → Cloud Build `ec9c850f` SUCCESS (~4 min) → Cloud Run `gochara-api` revision live.
- Vérif prod : `https://karmicgochara.app/terms` → HTTP 200 (19.6 KB), `https://karmicgochara.app/privacy` → HTTP 200 (22.6 KB).

**Pour Play Console** :
- Règles de confidentialité : `https://karmicgochara.app/privacy`
- Conditions d'utilisation : `https://karmicgochara.app/terms`

**Pas touché** : `blueprints/auth.py` (modifié hors session, hors scope), `astro/`, `android/` (pas lié au store pour cette tâche).

---

## 2026-06-20 — Orchestration karmic-mcp MCP Server

**Objectif** : Déployer un serveur MCP (Model Context Protocol) pour Karmic Gochara exposant 3 tools astrologique.

**Livré** :

1. **server.py** (~290 lignes, stdlib only — pas de dépendances externes)
   - HTTPServer natif + BaseHTTPRequestHandler (compatible Python 3.9+)
   - Endpoints : `GET /health`, `GET /mcp/tools` (MCP schema), `POST /mcp/call`
   - Intégration : `astro_calc.calculate_transits()` + `doctrine.NAKSHATRA_KARMA` + `VAULT_CORE`

2. **3 MCP Tools** (tous testés, JSON parseable, status=ok)
   - `get_natal_chart(birth_date, birth_time, birth_place)` → birth data structure
   - `get_transits_today(natal_data)` → Transit aspects + Nakshatra synthesis
   - `get_doctrine_reading(natal_data, transits_data)` → Full interpretation + synthesis

3. **test_mcp.py** (~180 lignes)
   - Séquence de validation : natal → transits → doctrine
   - Test case : Jérôme (1974-10-31 08:25 Athis-Mons)
   - Résultat : ✅ All 3 tools PASS, JSON parseable

4. **MCP_VALIDATION_REPORT.json**
   - Certifications : diagnostic ✅, tools validation ✅, Edge Gallery compatibility ✅
   - Schema MCP conforme
   - Prêt pour Hermes registration

**Déploiement** :
- Server tourne : `.venv/bin/python3 ~/karmic.gochara/server.py`
- Commandes de test : `curl http://localhost:8000/{health,mcp/tools}`
- Hermes registration : `hermes mcp add karmic-gochara --url http://127.0.0.1:8000/mcp/call`
- All 3 tools disponibles immédiatement après registration

**Détails techniques** :
- Architecture : HTTP only (pas FastAPI — Python 3.9 system compatibility)
- Logging : JSON per-event (timestamp + metadata)
- Error handling : graceful fallback, 0 external deps in server.py
- Tools calls : sequential chaining compatible (each tool can use previous output)

**Pas touché** : Hermes config, Capacitor build, GCP infrastructure.


---

## 🗓️ 6 Juillet 2026 — Création de la skill `agent-astrologue`

**Contexte :** Lancement du profil `astro` (agent astrologue). L'utilisateur a demandé la mise en place de la première compétence de l'agent.

**Livré :**
* Skill `agent-astrologue` (`~/.hermes/profiles/astro/skills/agent-astrologue/SKILL.md`, 6.7 Ko)
  * Cœur métier : Doctrine Évolutive Synthétique (DES) — 4 piliers (natal / transits / lecture karmique / voie évolutive)
  * Source de vérité : karmic-mcp (prod `http://34.163.125.49:8000`) — endpoints `/transits/today` + `/doctrine/reading`
  * Référence ayanamsa DK Djwhal Khul, Chandra Lagna calculé par décalage depuis la Lune
  * Templates de réponse (transit court / analyse DES complète)
  * **Économie tokens :** délégation à oMLX (127.0.0.1:8888) via `delegate_task` pour analyses > 500 mots

**Smoke-test validé (chaîne complète) :**
1. karmic-mcp prod health → 200 OK ✅
2. Transit pour DOB Jero (1974-10-31) → `{"date":"2026-06-20","planet_positions":{"sun":"Cancer","moon":"Gemini"}}` ✅
3. Doctrine reading → réponse mockée (état connu, `karmic_lite.py` réel pas encore branché) ✅
4. Génération analyse FR via omlx gemma-4-E2B-it-qat → 400 tokens en 8.8s, 0 cloud token ✅

**Décisions clés :**
* Skill **interne** (consommée par l'agent), pas distribuable — donc pas dans `wellness/` (qui est pour Edge Gallery) mais en top-level `agent-astrologue/`
* Honneur aux sources : position API mockée signalée explicitement à l'utilisateur
* Bug `_enrich_profile_with_natal` documenté pour ne pas le re-réenventer

**Pas touché :** karmic-mcp dev-vm (injoignable depuis ce poste, à vérifier côté VM), `wellness/karmic-gochara` (skill de distribution, hors scope).

**Next steps possibles :**
* Skill B (routage auto local/omlx) — utile si l'agent astro a beaucoup de sous-tâches répétitives
* Brancher le vrai `karmic_lite.py` (mocké actuellement) côté dev-vm
* Skill D wrapper (routage + calcul + rédaction combinés)

---

## 🗓️ 11 Juillet 2026 — Configuration X Bot & Pause Prompt Engineering

**Contexte :** Finalisation de la plomberie technique pour le bot X (Grok) et préparation au lancement. L'utilisateur prend la main sur l'affinement du prompt.

**Livré :**
* **Connexion X (Twitter) :** Résolution des erreurs `401 Unauthorized` avec l'API OAuth 1.0a (ajout de `user_auth=True` dans Tweepy).
* **Intégration Grok :** Migration vers le modèle `grok-4.3`. 
* **Nettoyage du code :** Suppression des instructions en dur dans `karmic_lite.py` qui entraient en conflit avec les consignes de `x_grok_bot.py`.
* **Clean-up dossier :** Suppression des anciens fichiers de log `karmic_prompt_*.txt` générés par l'algorithme, afin de désencombrer l'espace de travail.
* **Formatage du Prompt (Doctrine Évolutive) :** Refonte du prompt système dans `x_grok_bot.py` pour garantir une réponse brute, tranchante, et sans jargon (pas d'horoscope). Sélection de l'aspect avec l'orbe le plus proche de 0.00°. Remplacement du terme "Deadline" par "L'Ouverture".

**Décision en cours：**
* L'utilisateur met en pause le développement technique ("2 mois que je suis sur du dev") pour se concentrer sur son cœur de métier : l'astrologie et la doctrine.
* Le système est opérationnel, le prompt actuel dans `x_grok_bot.py` donne d'excellents résultats ("tranchant"), mais l'utilisateur va continuer de le peaufiner manuellement pour s'assurer qu'il garde l'axe et la philosophie des anciens prompts.

**Prochaine étape post-pause：**
* Lancer et maintenir le bot en production une fois le prompt définitivement validé par l'utilisateur.

---

## 🗓️ 11 Juillet 2026 — Déploiement vidéo & QA Android

**Contexte :** Finalisation de la présentation de l'application sur la landing page. L'utilisateur souhaitait remplacer les images statiques par une vidéo dynamique démontrant le fonctionnement réel de l'appli.

**Livré :**
* **Build et Sync Capacitor :** Restauration du composant `index.astro` et exécution de `npx cap sync android` puis `npx cap run android` (avec configuration de `JAVA_HOME`).
* **Automatisation de capture (`karmic-app-showcase`) :** Création d'une skill pour documenter l'enregistrement vidéo autonome via ADB.
* **Enregistrement sur Device :** Capture vidéo de 12 secondes avec scrolls simulés (`adb input swipe`) directement sur le Pixel 10 Pro connecté.
* **Intégration HTML5 :** Remplacement de l'image statique par une balise `<video autoplay loop muted playsinline>` dans `templates/index.html`.
* **Support Multilingue :** Duplication du fichier `demo_app_fr.mp4` (`en`, `it`, `nl`) pour le routing Jinja.
* **Clean-up :** Nettoyage de ~150 screenshots temporaires obsolètes.
* **Déploiement :** Commit et push sur GitHub, déclenchant le workflow Google Cloud Build.

**Décision en cours :**
* En attente de la validation Play Store pour générer des assets définitifs si besoin, la vidéo actuelle faisant très bien le travail pour l'instant.

**Prochaine étape :** 
* Recette visuelle sur `karmicgochara.app` post-déploiement.

---

## 🗓️ 12 Juillet 2026 — Session X-Bot : prompt universel Inertie/Alignement + portage prod + guard dataset

**Contexte :** Optimisation du prompt du bot X (Grok/xAI), cible grand public, zéro jargon astro.
Sandbox local (`sandbox_test_prompt.py`) prêt + `prompt_xbot_v2.py` comme source unique lisible par AGY.
Validation Grok réelle à chaque étape ; portage prod sur GO explicite de Jérôme. **Canal = 100% MP** (pas de génération Grok en tweet public).

**Itérations terrain de jeu (`prompt_xbot_v2.py`) :**
1. `DOMI_HINTS` réécrit : 12 maisons polarisées ROM (piège) vs Stage (éveil) — input NotebookLM doctrine.
2. Format 3 lignes développées → **1 phrase unique** (fin du filler, Grok ≤200 natif).
3. Marqueur `🗝️` ouvert testé → **collision Chiron ⚷** détectée (🗝️ = symbole de Chiron) → revert label fermé `🗝️ Miroir de l'âme :`.
4. Anti-jargon renforcé (planètes + aspects + "horoscope" + "blocage de fond").
5. **Correction conceptuelle (coquille Jérôme)** : ROM/RAM/Stage sont des forces *personnelles* du consultant (Ketu/Chiron/Porte Visible), PAS des propriétés de maison. → `DOMI_HINTS` passé en vocabulaire **universel Inertie (tendance inconsciente) vs Alignement (maîtrise consciente)** ; ROM/RAM/Stage **se plaquent dynamiquement** sur ces versants. Plus d'empreinte natale, diagnostic impeccable pour tous thèmes.

**Rendu Grok final validé (live, 5.4s, 199 chars) :**
> 🗝️ Miroir de l'âme : Ton réflexe de t'affirmer par l'image défensive fige ta valeur, cette tension croissante expose la dépendance aux validations extérieures, et seule l'action de te déposer dans la vulnérabilité pure libère ta souveraineté.

*Jérôme : "grandiose ! un vrai miroir de l'âme !"*

**Portage prod (`x_grok_bot.py`) — GO donné :**
* `system_instruction` = version sandbox validée : maisons universelles Inertie/Alignement + plaquage dynamique ROM/RAM/Stage, 1 phrase `🗝️ Miroir de l'âme :`, **max 200** (était 280), supprimé l'ancien format 3-lignes (`🌑 L'Ombre:` / `🗝️ L'Évolution:`).
* Ajout `_is_valid_training_sample()` : garde-fou strict avant écriture JSONL — label, ≤200, ponctuation finale, zéro `…`, zéro jargon, **plancher 40 chars** (rejette "Cesse de."). Rejeté → log, pas d'écriture.

**Dataset (`dataset_finetuning.jsonl`) :**
* Ligne 2 toxique (`🗝️ Miroir de l'âme: Cesse de.`) **retirée** → 1 ligne propre.
* Ré-empoisonnement fermé par le guard prod.

**Canal MP (décision finale) :**
* 100% MP. Le DM avale 10k → **aucune troncature** de la réponse Grok (l'utilisateur lit le texte complet).
* Le `truncated=True` du sandbox est un *simulacre* de contrainte tweet (what-if), sans objet en MP.
* Tweet public = annonce statique SEO ("DM envoyé 🌌✨ #tags"), pas la génération Grok. `max_tokens=800` conservé (pas de baisse nécessaire).

**Vérif :** Ad-hoc (scripts jetables `hermes-verify-*.py`, /tmp) — 10/10 PASS playground+prod, `py_compile` OK. Pas de suite CI (projet sans test command).

**Notes / hors scope :**
* Pyright warning pré-existant ligne 182 (`strip` on None) — NON introduit cette session.
* `karmic_lite.py` L213 affiche `orbe < 3°` mais filtre X Bot coupe à `< 1.0°` (libellé trompeur) — connu.

**Prochaine étape :** Aucune (session validée). Fine-tuning futur : guard prod déjà protecteur.

---

## 🗓️ 12 Juillet 2026 (suite) — Matrice Kālapurusha + allègement + banlist auto

**Contexte :** Suite de la session du matin. Input de Jérôme depuis un autre agent : ajouter la matrice Kālapurusha (référentiel des thèmes de vie par maison) comme fond structurel du diagnostic.

**Changements terrain de jeu (`prompt_xbot_v2.py`) :**
1. **Matrice KĀLAPURUSHA ajoutée** (thèmes-only, SANS signes ni planètes — car `SYSTEM_INSTRUCTION` interdit le jargon). Branchée sur les maisons numérotées (M1=élan vital, M2=valeurs… M12=Moksha). Injectée dans le point 3.
2. **Point 3 reformulé en directive de croisement** : *"Croise la MAISON CHANDRA LAGNA (posture : Inertie/Alignement via `DOMI_INJECT`) avec la thématique de fond de cette maison (`KALAPURUSHA`). Diagnostique Inertie (ROM/RAM) vs Alignement (Stage)."* — **sans le mot "signe"** (cohérent avec Kālapurusha=maisons + anti-jargon).
3. **Allègement prompt** : retrait de "expert en Doctrine Évolutive" (label creux sans fine-tune) → persona *"miroir psychologique tranchant, pas un devin"*. `DOMI_HINTS` complet retiré de l'injection ; remplacé par `DOMI_INJECT` (déf + 2 exemples). **Effet mesurable : Grok sort sous 200 natif (`truncated=False`, 179 chars) pour la 1re fois.**
4. **Reword point 4** : `(appliquant, tension croissante)` → `(tension croissante)`. Corrige à la source la fuite "appliquante" (terme de mécanique d'aspect) que Grok avait échoée.

**Dataset rafraîchi (`dataset_finetuning.jsonl`) :** 1 ligne propre = **NOUVEAU prompt** (persona miroir + 1-phrase) + exemple 🗝️ validé (sans "appliquante"). L'ancienne ligne (prompt 3-lignes + Doctrine Évolutive) était stale/contre-productive pour le fine-tune → écrasée.

**DÉCISION BANLIST AUTO (rappel Jérôme) :** *"banlist non. ça doit etre automatique sinon ce sera une liste infinie."* → Les 5 ajouts manuels (`appliquant/appliquante/séparant/séparante/orbe`) ont été **revertés**. Le leak est géré par reword, pas par whack-a-mole. **TODO séparé : reformuler la règle anti-jargon en catégorielle** (couvre la famille aspect + astres sans liste finie). À faire dans une prochaine session dédiée.

**Rendu Grok final validé (live, 3.6s, 179 chars, `truncated=False`) :**
> 🗝️ Miroir de l'âme : Ton rôle défensif figé dans l'affirmation de soi étouffe l'élan vital brut, la tension croissante force la rupture radicale pour incarner ta souveraineté nue.

**Portage prod (`x_grok_bot.py`) : À FAIRE** — le prod n'a pas encore : reword point 4 (encore "appliquant"), banlist/guard étendus (TODO auto), ni le prompt miroir/DOMI_INJECT. À porter sur GO explicite de Jérôme dans une prochaine session (le dataset est déjà partagé/rafraîchi).

**Vérif :** Ad-hoc (scripts jetables `hermes-verify-*.py`) — playground 9/9 PASS après revert, `py_compile` OK. Pas de suite CI.

**Notes :**
* Playground et prod sont DÉSYNCHRONISÉS : playground = prompt final ; prod = encore ancien (3-lignes + Doctrine + "appliquant"). Sync prod en attente de GO.
* Pyright warning L182 pré-existant (`strip` on None) inchangé.

---

## 🗓️ 13 Juillet 2026 — 100% EN + portage prod

**Contexte :** Jérôme veut Grok en anglais (X traduit auto). On bascule le playground ET le prod en EN, on corrige un bug de guard (marqueur EN rejecté), et on porte tout dans `x_grok_bot.py`. Ce profil AGY dédié à cette tâche.

**Playground (`prompt_xbot_v2.py`) — 100% EN :**
1. Traduction EN de l'enveloppe : corps `build_system_instruction`, `PONDÉRATION` (20/50/30), `STYLE_NO_VERBATIM`, `FORMAT`, `build_ton_posture` (clés FR de Dasha conservées pour le match).
2. Blocs universels RÉUTILISÉS tels quels (DRY) : `DOMI_HINTS`, `KALAPURUSHA`, `NAKSHATRA_RULES` (pas de langue).
3. **Bug guard corrigé** : le `validate_response` exigeait le marqueur FR `🗝️ Miroir de l'âme` → en `--en` toutes les réponses EN étaient techniquement REJET (invisible avant). Marqueur basculé sur `MIRROR OF THE SOUL`.
4. **Prefix obligatoire** ajouté (`MANDATORY PREFIX: "MIRROR OF THE SOUL : "`) — Grok avait zappé le label au 1er run EN.
5. Sandbox `--en` retiré → EN par défaut. User/data prompt reste FR (Grok parse).

**Rendu Grok EN validé (live, 188 chars, GUARD ✅, truncated=False) :**
> MIRROR OF THE SOUL : Although your incarnational reflex is to rush impatiently away from depth, networks now rip defensive hoarding apart and force the concrete rhythm of shared abundance.

**Portage prod (`x_grok_bot.py`) — GO Jérôme :**
- System inline FR (3-lignes + Doctrine + "Miroir de l'âme") → import du `build_system_instruction` EN. Plus de duplication `KALAPURUSHA`/`DOMI_HINTS` inline.
- Banlist manuelle `_is_valid_training_sample` **supprimée** → `validate_response` catégoriel (même guard que playground).
- **Écriture `dataset_finetuning.jsonl` live RETIRÉE** — guard read-only + log VALIDE/REJET.
- `call_grok(prompt)` → `call_grok(prompt, data)` : injection chirurgicale (moon_nak Lune natale consultant, transit_nak planète la + tendue, `transit_house = cl_house(...)`, `_sade_sati`, Dasha courant → TON).
- Temp 0.7 → 0.5, max_tokens 800 → 300.

**Vérif :**
- Playground : ad-hoc temp-file (TMPDIR) PASS — compile + airgap (MAISON 11 + "surgical lightning bolt" injectés, leak+prefix rejetés). Live Grok EN ✅.
- Prod : ad-hoc structural PASS (compile + assertions : pas de FR, pas de dataset write, call_grok(data), guard live, temp 0.5). **Runtime end-to-end IMPOSSIBLE dans ce sandbox** : `tweepy`→`urllib3` cassé sous Python 3.11 Hermes, et `.venv` a `pydantic_core` natif manquant (via openai). Env defect, pas code. 1er run live = lancement local Jérôme.

**Notes / hors scope :**
- Skill `karmic-gochara-xbot-prompt` PAS encore figé avec EN+portage (en attente du run runtime local de Jérôme, puis freeze).
- Pyright L182 pré-existant inchangé.

---

## 🗓️ 13 Juillet 2026 (suite 2) — `🗝️ Soul Debug :` + rebuild xurl + cronjob live + E2E prouvé

**Contexte :** Jérôme valide le marqueur `🗝️ Soul Debug :` (identité cyber-karmique ROM/RAM). Le bot tweepy ne peut pas tourner dans le sandbox (env cassé) → rebuild en **cronjob Hermes via `xurl` CLI** (contourne tweepy). Auth OAuth1 finalisée (port 8080 était occupé par un Java Firebase emulator → bascule OAuth1a).

**Marqueur (`prompt_xbot_v2.py`) :** `🗝️ Miroir de l'âme :` → `🗝️ Soul Debug :` partout (FORMAT, MANDATORY PREFIX, `validate_response`, comment L228). Rendu live 160 chars, GUARD ✅.

**Rebuild bot (`x_bot_xurl.py`) — tweepy supprimé :**
- Tout passe par `xurl` subprocess (`mentions`, `dm`, `reply`, `delete`, `read`, `whoami`). OpenAI SDK pour Grok (marche en `.venv` pyenv 3.12).
- Garde-fou renforcé : `call_grok` retourne `None` sur REJET → **aucun DM foireux envoyé** (répond au risque soulevé).
- `main()` : `--once` (1 poll puis exit) pour cron-friendly ; daemon `while True` toujours dispo sans flag.
- `e2e_test_harness.py` (standalone) : importe le bot (single source), DRY_RUN=1 par défaut (safe), écrit via `xurl reply` seulement sous DRY_RUN=0.

**Auth X :** `xurl auth oauth1` (OAuth 1.0a, tokens depuis Developer Console) → `xurl whoami` = `@siderealAstro13`. Le vieux bot `x_grok_bot.py` (FR, tweepy) de il y a 1 mois a répondu une fois avec erreur FR puis est mort (aucun lanceur persistant : pas de launchd/crontab).

**Cronjob Hermes `9c9f30bbaad8` (every 2m, one-shot, skills xurl + karmic-gochara-xbot-prompt) :** tourne depuis Hermes, poll propre, exit clean. Plus de daemon concurrent (race `last_seen_id.txt` évitée).

**E2E RÉELLEMENT PROUVÉ (pas juste structural) :**
1. `xurl delete 2076466143510884816` → `{"deleted":true}` (vieux reply FR supprimé).
2. `DRY_RUN=0 e2e_test_harness.py 2076465504215073140` → reply posté sur X :
   > 🗝️ Soul Debug : Although your reflex bolts from depth in impatience, collective networks now strip defensive hoarding, forcing measured sharing that unlocks shared gain.
3. Screenshot X confirmant la reply live (engagement présent). Tweet de test laissé en place (Jérôme : « ça donne l'idée »).

**Vérif :** Ad-hoc temp-file TMPDIR PASS (x_bot_xurl + e2e_test_harness). Runtime E2E réel exécuté sur X.com ✅.

**Env note :** `.venv/bin/python3` → pyenv 3.12 (openai+geopy+timezonefinder OK). Le `PYTHONPATH` du terminal Hermes pointe vers le venv agent 3.11 cassé → il faut `env -i PATH="$PWD/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin" HOME="$HOME" .venv/bin/python3` pour lancer le bot proprement.

## 🗓️ 13 Juillet 2026 (suite 3) — Levier2 VOCABULARY + recall hook reply + E2E DM réel

**Contexte :** Jérôme valide l'idée de simplifier le vocabulaire Grok (lisibilité X scroll) + ajouter un hook de rappel dans la reply publique (funnel fil, DM trop peu visible).

**Levier2 (VOCABULARY RULE) — `prompt_xbot_v2.py` :**
- Ajout d'une clause EN dans `build_system_instruction` (après MANDATORY PREFIX) : *« use plain, raw, visceral everyday English… prefer 'clinging' over 'hoarding', 'old habit' over 'incarnational reflex', 'rush' over 'bolt from depth' »*.
- Levier1 (réécrire les 27 Nakshatra/DOMI) rejeté = surkill (STYLE_NO_VERBATIM + PONDÉRATION font déjà la digestion).
- Test sandbox temp 0.5 : *« Although your reflex is to rush ahead and dodge depth, daily exchanges now rip that old shortcut open and force measured words that build steady courage on the spot. »* (181/200) — plus lisible.
- **Porté en prod sans duplication** : `x_bot_xurl.py` importe `build_system_instruction` du single-source (lignes 32-33, appel 156). Édition terrain = live.

**Recall hook — `x_bot_xurl.py` public reply :**
- Ancien wording statique → nouveu : `Your karmic Soul Debug just landed in your DMs 🌌✨` + `Your next shift peaks ~<date> — DM me your city+time that day for a fresh one.` + lien + 3 hashtags.
- **Hook VA DANS LA REPLY, JAMAIS le DM** (DM guard-locké ≤200/no `\n`/anti-jargon). `<date>` = placeholder tant que forward-ephemeris (AGY) absent.
- DM Soul Debug inchangé (guard intact).

**Vérif :** script skill `hermes_verify_playground.py` PASS (14 checks) ; assertion reply mise à jour (`Soul Debug` + `next shift peaks`). Tempfile TMPDIR laissé en place pour satisfaire le garde-fou ad-hoc.

**E2E DM réel PROUVÉ :** test via rollback `last_seen_id.txt` (1 sous l'ID de la mention du 2nd compte `@lovesNhappiness`) + run `--once` enchaîné en 1 shell (anti-race cron). Résultat : `✓ GUARD VALIDE (181 chars) / ✓ Réponse publique postée / ✓ DM envoyé`. DM `🗝️ Soul Debug :` reçu par Jérôme sur le 2nd compte → **confirme single-source live en prod** (enterre le doute 🛠️/🗝️ de la capture initiale, qui venait d'une version antérieure).

**Alertes notées :**
- 🔎 Capture initiale `🛠️ Soul Debug` ≠ `🗝️` → version prod périmée au moment du screenshot ; résolu par ce run.
- ⚠️ Risque cron fantôme : si un cron Hermes relance `--once` pendant la lecture, la reply (nouveau texte) diffère de l'ancienne → X l'accepte → double reply. Mitigé par rollback+run en 1 shell, mais cron externe non contrôlable.
- ⚠️ B proactif (DM déclenché par transit, sans mention) : rejeté comme modèle lourd (persistance + forward-ephemeris + rate-limit X). Modèle retenu = funnel réactif (tweet Jérôme → user répond → DM), l'user ayant déjà ouvert le fil → MP ouvert → 0 échec silencieux.

## 🗓️ 13 Juillet 2026 (suite 4) — `<date>` = PEAK detection + DOMIFICATION (AD-HOC vérif + E2E réel)

**Contexte :** Jérôme GO (#1a #1b #2) pour remplir `<date>` via forward-ephemeris, puis « Sep 09 Jupiter entre Ashlesha = impersonnel » → ajouter la **domification** (croiser le chart natal).

**v1 (1er-jour-futur) — root-cause + rejet :**
- `get_monthly_transits` ignorait ASC/MC/Lilith → élargi `TARGET_NATAL` ← +`ASC ↑`, `MC ↑`, `Lilith ⚸`.
- `next_shift_date` v1 sortait `Jul 14` (début d'aspect demain) → « ça fait short » → rejeté.

**v2 (PEAK detection) — retenu :**
- `find_next_peak()` dans `transit_alerts.py` : orbe **minimale** (périgée = hit exact), aspects *applying* only. Réutilisable par l'app.

**v3 (A+B domification) — LIVRÉ :**
- **A)** `find_next_peak` ajoute la **maison natale** (Chandra Lagna via `cl_house` de `prompt_xbot_v2`, importé ; Nœud Sud dérive son display via `lon_to_display` car `_calc` ne le calcule pas). Label : `Chiron × ASC ↑ (H1)`.
- **B)** Nouveau `find_next_nak_shift()` : planète lente **entre un nakshatra GLOBAL**, croisé avec TES points natals (Ketu/Rahu/Chiron/ASC/MC/Lilith via `_NATAL_NAK_POINTS`). Ne garde QUE si un de tes points y est → perso. Label : `Ketu (Nœud Sud) enters Magha (your MC)`.
- `next_shift_date` choisit le **plus proche** des deux (B bat A ici).
- Imports `transit_alerts.py` ← `lon_to_display, lon_to_nakshatra` (astro_calc) + `cl_house, SIGNS` (prompt_xbot_v2).

**AD-HOC vérif (tempfile `hermes-verify-dom-fresh.py`, écrit+run+nettoiyé) : 15/15 PASS.**
- A : `Nov 14` `Chiron × ASC ↑ (H1)` (maison OK).
- B : `Oct 11` `Ketu (Nœud Sud) enters Magha (your MC)` — ton exemple `Sep 09 Jupiter Ashlesha` (global) devient **perso** (ton MC est dans Magha).
- `next_shift_date` → `Oct 11` (B wins). Incomplet → `(None,None,None)`.

**E2E RÉEL PROUVÉ (run `--once` ciblé, rollback last_seen + 1 shell anti-race) :** `✓ GUARD VALIDE (141 chars) / ✓ Réponse publique postée / ✓ DM envoyé`. Vue 2nd compte (`@lovesNhappiness`) confirme reply live `Your next shift peaks ~Oct 11 — DM me your city+time…` → **domification live en prod**.

**Notes :**
- DM reçu = ancien wording `Although you bolt to dodge depth…` (pre-Levier2) sur ce run → nuance wording, PAS un bug du `<date>`. Guard valide (141 chars). À investiguer séparément si Jérôme veut.
- Handle `@tripesinnj` = `@siderealAstro13` (même compte).
- Double-reply sur MÊME mention = artéfact de runs manuels ; steady-state cron = 1 mention / 1 reply.

**Prochaine étape (ouverte) :** alerte prochaine (modèle B proactif) si Jérôme veut explorer ; sinon funnel réactif live est complet.

## 🗓️ 13 Juillet 2026 (suite 5) — BIORYTHME LUNAIRE (Chandra Lagna) : axe unique + live

**Contexte :** Jérôme veut que le filtre perso `min_conj=2` (= Win3.1) devienne un **axe unique** réutilisable : `natal_density` (nb points natals touchés par la Lune en aspect conj/sextile/square/trine/opp, orb 3°) + `has_node` (Rahu/Ketu parmi eux). Puis **biorythme lunaire** = courbe sur 90j, affichable en tweet public (perso mais non-sensible, signature `@siderealAstro`), et l'user **choisit son jour** → DM Soul Debug ciblé.

**Couche A (`transit_alerts.py`) — LIVRÉ + 13/13 ad-hoc :**
- `chandra_biorhythm(profile, days=90)` = courbe brute (tous jours, sans filtre). Sur Jérôme : 91 jours, density 0→7, cloche pic d=4 (11 jours), 6 jours `has_node` tous density≥4.
- `biorhythm_at(profile, target)` = point à date précise (None si passé).
- `next_peak_biorhythm(profile)` = prochain sommet (has_node prioritaire, sinon density max) → `2026-09-22 H10 d=7 ◆`.
- `list_chandra_lagna_events` refondu : `min_conj` → `min_density` (axe unique, même seuil 2).

**Couche B (`biorhythm_fmt.py`, nouveau) — LIVRÉ + 15/15 ad-hoc :**
- `parse_target_date(text)` : regex `JJ mois`/`Mon JJ`/`mon pic du JJ Mois` → date (None si passé/rien). FR+EN.
- `build_biorhythm_tweet(curve)` : 280c, signature `@siderealAstro`, pics listés (top = node), lien+tags. 203c sur Jérôme.
- `build_biorhythm_hint(point)` : hint court pour `transit_hint` du DM (pas texte brut).

**Couche C (`x_bot_xurl.py`) — LIVRÉ + 9/9 dry-run + LIVE :**
- `--tweet-biorhythm` → `tweet_biorhythm()` poste le biorythme de Jérôme (chart `NATAL`).
- **BUG live trouvé + corrigé :** `xurl("tweet", ...)` n'existe pas → `Error: request failed`. Fix : `xurl("post", ...)`. Re-test → tweet LIVE posté (203c).

**Couche D (`x_bot_xurl.py`) — LIVRÉ + 10/10 unit + 5/5 intégration + LIVE :**
- `call_grok(prompt, kdata, biorhythm_hint=None)` injecte le hint dans `transit_hint`.
- `process_mentions` : `parse_target_date(mention)` → `biorhythm_at` (jour choisi) OU `next_peak_biorhythm` (sommet auto) → `build_biorhythm_hint` → `call_grok`.
- **E2E LIVE (mention @lovesNhappiness `10/31/1974 08:25 PARIS`) :** `✓ GUARD VALIDE (189 chars) / 🌊 Sommet auto 2026-09-22 injecté / ✓ DM envoyé`. Reply a échoué (duplicate — mention déjà traitée avant) mais DM ciblé est parti. → **flux biorythme live en prod**.

**Analyse karmique (single-source, à garder hors code) :**
- Stellium solaire en Balance (☀♀♂♅, Swati) = Soi planté dans le Miroir ; ♆☊ conjoints Anuradha (Scorpion) = nœud karmique dissous. Boucle ROM↔RAM : on cherche l'autre (Balance) pour dissoudre ce qu'on n'ose transformer seul (Scorpion).
- `has_node` coïncide avec les sommets de density → marqueur fiable, pas de règle empilée.

**Garde-fous respectés :** axe unique (pas de flags infinis), DM guard-locké ≤200, tweet public non-sensible (courbe lunaire, jamais ville/heure naissance), parsing léger (regex, pas de LLM pour la date).

**Prochaine étape (ouverte) :** cron quotidien `--tweet-biorhythm` si Jérôme veut automatiser ; sinon flux manuel prêt.

## 🗓️ 14 Juillet 2026 — BIO IMAGE (matplotlib) + HÉBERGEMENT GCS (option B live)

**Contexte :** X API Free refuse les media sur les posts (`media IDs are invalid`, confirmé via raw `/2/tweets` aussi) → option A (texte seul) ou B (héberger l'image + lien). Jérôme choisit **B** : serveur qui héberge `karmicgochara.app` + stocker `dataset_finetuning.jsonl`.

**Impl :**
- `pip install matplotlib` dans `.venv` (local, 0€). `build_biorhythm_image(curve)` dans `biorhythm_fmt.py` → PNG fond sombre, courbe dorée, losanges rouges Rahu/Ketu, signature `@siderealAstro13` en footer (validé visuellement).
- `x_bot_xurl.py` : `upload_to_gcs(local, key)` (utilise `GOOGLE_CREDENTIALS_JSON` du `.env`, retourne URL `storage.googleapis.com/<bucket>/<key>`). `tweet_biorhythm` : génère image → upload `biorhythm/biorhythm_AAAA-MM-JJ.png` → poste tweet + lien (fallback texte seul si bucket vide/échec).
- `_SIGN` corrigé `@siderealAstro` → `@siderealAstro13` (handle réel). Tweet corps sans `@` (compte = signature).
- `GCS_PUBLIC_BUCKET` env documenté.

**BUCKET (agent GCS) :** `gs://karmic-gochara-public` (europe-west1), uniform public-read (`allUsers` objectViewer), URL test 200. `.env` → `GCS_PUBLIC_BUCKET=karmic-gochara-public`.

**AD-HOC vérif (tempfile `hermes-verify-gcs.py`, écrit+run+nettoiyé) : 9/9 PASS** (upload_to_gcs, URL, empty-bucket fallback, tweet+lien).

**E2E LIVE PROUVÉ :**
- Dataset → `https://storage.googleapis.com/karmic-gochara-public/dataset_finetuning.jsonl` (HTTP 200).
- Tweet biorythme + image → `https://storage.googleapis.com/karmic-gochara-public/biorhythm/biorhythm_2026-07-14.png` (HTTP 200, lien dans le tweet live `t.co/ynAzB6Z2uu`). Contourne la limite media X.
- Image validée visuellement (courbe + ◆ + signature).

**Garde-fous respectés :** 0€ (matplotlib local + GCS existant), image non-sensible (courbe lunaire + handle public, jamais ville/heure naissance), fallback texte si GCS KO.

**Prochaine étape (ouverte) :** cron quotidien `--tweet-biorhythm` (Hermes cron 2min ou matin) si Jérôme veut automatiser ; sinon flux manuel prêt.

## 🗓️ 14 Juillet 2026 (suite) — BUG X-BOT : silence total des mentions (crash plomberie)

**Symptôme :** une mention valide `@lovesNhappiness → @siderealAstro13 10/31/1974 08:25 PARIS` n'a déclenché AUCUNE génération (ni DM ni reply). `last_seen_id.txt` bloqué à `999` (jamais écrasé par un vrai ID 20 chiffres) → preuve que `save_last_seen_id` (dernière ligne) n'était jamais atteinte.

**Cause racine (plomberie, PAS le prompt) :** `main()` appelait `process_mentions(None)`. Or `process_mentions` fait `if fb != 0 and my_handle.lower() in ...` (ligne 311) → `my_handle` = `None` → `AttributeError: 'NoneType' object has no attribute 'lower'`. Le bot lit les mentions à l'envers (anciennes d'abord) ; dès qu'une mention-bruit contenait un mot-clé feedback (`up`/`no`/`good`/`yes`/`bad`/`fix`/`meh` + emojis) → `fb != 0` → court-circuit désactivé → crash **avant** d'atteindre la mention valide.

**Pourquoi l'E2E du 13 juil avait passé :** le harness/test ne contenait pas de mot-clé feedback → le crash ne se déclenchait pas. En prod (cron `every 2m` sur le flux réel) n'importe quelle mention « good/no/up » tuait le bot à chaque tick.

**Fix (2 endroits, lint OK) :**
- `process_mentions(my_handle)` : `my_handle = (my_handle or "").lower()` en garde défensif (début de fonction).
- `main()` : `uname = setup_x()` puis `process_mentions(uname)` (les 2 appels : `--once` + boucle `while`).

**Vérifié en réel :** run `--once` a traité faria + 3 autres mentions `10/31/1974 08:25 PARIS` → chacune a reçu DM 🗝️ Soul Debug (148–193 chars, GUARD VALIDE) + reply publique. `last_seen_id.txt` = `2076968066265542728` (vrai ID). Cron `9c9f30bbaad8` relancé (pause le temps du debug pour éviter double-envoi).

**AD-HOC vérif (tempfile `hermes-verify-*.py`, écrit+run+nettoyé, pas de suite CI) :** PASS — `py_compile` clean ; source asserts (guard + `process_mentions(uname)`) ; intégration `process_mentions(None)` sans crash, mention `good stuff` skipée, mention `10/31/1974 08:25 Paris` → DM+reply ; marker `🗝️ Soul Debug : ` confirmé.

**Garde-fous respectés :** prompt single-source NON touché (edge Jérôme intact) ; fix plomberie uniquement ; cron sain.



## Session 16/07/2026 (soir → nuit) — Fix ANR Gemma + fallback Soul Debug local

**Contexte :** Pixel 10 Pro surchauffe/freeze pendant `generate` → ANR. Root cause : `GemmaHelper.kt` utilisait `sendMessageAsync().collect{}` dans un `runBlocking` (bug LiteRT-LM #2718, thread Capacitor bloqué). Fix : `conversation.sendMessage(prompt)` synchrone.

**Commits (GitHub `tripesinn/karmic.gochara`, main) :**
- `16db6e3` — fix(gemma): sendMessage synchrone (ANR). Fichiers : `GemmaHelper.kt`, `build.gradle` (v32/1.9.13), `AndroidManifest.xml`, `GemmaSynthesisPlugin.java`. Déployé via GitLab CI (build 21:18, SUCCESS).
- `6085785` — feat(soul_debug): fallback Gemma local si `localMode==='native'` & Grok down. Fichiers : `blueprints/api.py` (+ endpoint `/api/soul_debug_prompt`, parité Grok, unauth 401) + `astro/src/pages/app/index.astro` (.catch fallback). Déployé via GitLab CI (endpoint live vérif : HTTP 401 sur requête non-auth).

**Décisions user (Q1-Q4) :** fallback local UNIQUEMENT si `localMode==='native'` ; même prompt système que Grok (via DoctrinePromptBuilder, transits calculés côté serveur) ; `localStorage` suffit (pas persistance profil) ; Miroir du jour généré au lancement seulement (1re génération via Grok).

**Vérifs ad-hoc (tempfiles, run+supprimés, pas de suite CI) — tout PASS :**
- `api.py` `/api/soul_debug_prompt` : Flask test client → 200 + {ok, system, user, lang} ; FR/EN variants ; byte-parité avec `system_instruction` Grok ; unauth → 401.
- `index.astro` fallback : Astro `npm run build` green (TS compile) + port Node du .catch → gates corrects (native+platform ⇒ local calls ; cloud/web ⇒ cloud error).
- `GemmaHelper.kt` (plus tôt dans la soirée) : Java port du corps synchrone → termine + flatten `Message.contents.contents` correct.

**État device (Pixel 55161FDCH0004E, branché, utilisateur endormi) :**
- App v32 installée clean (uninstall v25 signature mismatch → reinstall clé `key0`). Fallback frontend embarqué (grep `Oracle local` = 1 dans l'AAB).
- Backend `/api/soul_debug_prompt` live (Cloud Run `gochara-api`).
- **E2E réel NON exécuté** : nécessite action manuelle user = « mode native » dans Réglages de l'app, puis relancement (Grok down → fallback Gemma local via Edge Gallery). Bloqué sur input user.

**Bloquant restant :** test E2E on-device (déclenchement du fallback) — à faire demain matin par Jérôme (1 tap Réglages + open app). Tout le reste (code, build, deploy, vérifs) est terminé et vert.

## Session 16/07/2026 (23:47) — Fix MODE TEST en prod

**Bug repéré (user) :** l'écran de login prod affichait les boutons « MODE TEST » (Test: Nouvel Utilisateur / User Existant). Root cause : `PUBLIC_FIREBASE_EMULATOR=true` dans `.env.local` est embeddé par Astro dans tous les builds ; `isEmulator = import.meta.env.PUBLIC_FIREBASE_EMULATOR==='true'` → vrai même en prod.

**Fix (option 2 user) :** gate dev-only. `isEmulator = import.meta.env.DEV && PUBLIC_FIREBASE_EMULATOR==='true'` dans 4 fichiers : `LoginCard.astro`, `firebase.ts`, `firestore-rest.ts`, `api.ts`. En prod build `DEV`=false → boutons TEST + routing émulateur (Flask local 127.0.0.1:5001, Firestore 8080) jamais actifs ; prod utilise Cloud Run live. Note : en prod le fallback Soul Debug appelle donc `/api/soul_debug_prompt` sur Cloud Run (live) — conforme.

**Commit :** `6fa7e01` — pushé origin main. GitLab CI redéploie frontend web.

**Vérifié en réel :** Astro `npm run build` green + `grep "Mode Test"` sur bundle prod = absent. Rebuild AAB v32 + reinstall Pixel (clé `key0`, upgrade OK). Capture écran Pixel confirmée : login ne montre plus que « Continuer avec Google » + branding, MODE TEST disparu.

**État final :** v32 sur Pixel = fix ANR + fallback Soul Debug local + login prod propre. E2E fallback toujours en attente (1 tap « mode native » Réglages demain).



---

## 2026-07-18 — Chat local 100% + nettoyage bench + AAB v61

**Contexte :** débloquer le chat local (bug « serveur non configuré ») + mesurer plafond contexte (bench) + nettoyer pour release.

**Correctifs chat local (sources) :**
- `lecture.astro` v53 : `localMode` lu depuis `karmic_ai_settings` → bloc native Gemma.
- `ChatBox.astro` v56 : force le local si `capacitorBridge.isNative()` (comme le Miroir force `wantLocal=true`). Répare le chat Gochara qui basculait au cloud.
- Versions : v55 1.9.36 (chat), v56 1.9.37 (bench natif), v57-60 bench hook, v61 1.9.42 (cleanup).

**Validé en réel (Jérôme, device Pixel) :** Soul Debug + Gochara + 1 réponse chat générés EN LOCAL. Chat local fonctionne.

**Bench context (mesure plafond) :** `benchContext` natif + `getBenchFlag` + hook dashboard + `bench.html`. Résultat : timeout tour 1 (prompt 1431c, >180s) = BUG DU BENCH (appelle `generateSync` direct au lieu du chemin `generate` validé), PAS un plafond réel. Chat normal marche. → bench retiré en v61 (code mort).

**TPU :** abandon définitif. Edge Gallery bundle un split `google_tensor_runtime` (lib EDGETPU) absent de KG. LiteRT-LM 0.14.0 seul → SIGABRT NPU. CPU = seul backend fonctionnel.

**Modèle :** Gemma E2B générique 2.58GB (2588147712 o) sur device, backend CPU.

**Nettoyage v61 :** retiré `benchContext`/`getBenchFlag` (plugin), hook bench (`index.astro`), `bench.html`. Bump 61/1.9.42. Build natif vert, APK/AAB installés, pas de crash.

**Artifacts release :** `android/app/build/outputs/bundle/release/app-release.aab` (30.1MB, v61), `release_notes_v61.txt` (FR/EN bref).

**Numéros version :** Play Store actuel = 25 (1.9.6). Nouveau .aab = 61 (1.9.42) → Play accepte (compteur croissant 61 > 25). Saut debug→prod (47-60 jamais publiés).

**Vision future (discussion à venir) :** « Miroir de l'Âme mémoire » = historique des générations (Soul Debug + Gochara + chats) → RAG local (SQLite) + feedback loop → OKF (fine-tune server-side périodique, puis modèle redescendu). Niveau 1 réalisable now (historique + RAG contexte persistant). Niveau 2 (fine-tune on-device) impossible sur Pixel CPU.
