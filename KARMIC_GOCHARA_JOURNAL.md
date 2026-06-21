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
