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
- 🔧 Fix : chemins BaseLayout — apple-touch-icon `/icons/`→`/static/icons/`, SW register `/sw.js`→`/static/sw.js`
- ✅ Build Astro OK (527ms, 2 pages)