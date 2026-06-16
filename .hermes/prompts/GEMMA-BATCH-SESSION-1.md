# Gemma Batch Session 1 — Prompts Boilerplate Astro

**Stratégie :** 5 prompts courts (~10-15 min total), auto-suffisants. Copie-colle chaque prompt dans Gemma local, récupère les blocs de code générés.

**⏱️ Durée :** 10-15 min par session Gemma (RAM M4 limité)

---

## Prompt 1 : BaseLayout + global CSS (5 min)

```
Crée une app Astro pour Karmic Gochara (astrologie védique). Thème sombre et mystique.

Génère ces 2 fichiers COMPLETS prêts à copier :

1. src/layouts/BaseLayout.astro
   - Layout principal avec <slot />
   - Meta viewport, PWA manifest (/static/manifest.json)
   - Apple touch icon (/static/icons/icon-192.png)
   - Google Fonts : Cinzel, Cormorant Garamond, DM Mono
   - Titre + meta description depuis props
   - Service worker registration

2. src/styles/global.css
   - Reset CSS minimal (*, body, h1-h6)
   - Couleurs : --bg: #0c0a08, --gold: #c9a84c, --text: #f5f0e8, --border: #2a2820
   - @keyframes fadeUp (opacity + translateY)
   - Corps : background #0c0a08, color var(--text)
   - Scrollbar customisé (dark mode, gold thumb)
   - Dégradé subtil background (--gold opacity 0.06 en bas)

Retourne UNIQUEMENT les 2 fichiers, pas d'explications.
```

---

## Prompt 2 : Tailwind config + astro.config (5 min)

```
Fichiers de config Astro + Tailwind v4.

Génère COMPLETS :

1. tailwind.config.mjs
   - theme.extend.colors.cosmic : bg (#0c0a08), gold (#c9a84c), gold-dim (#8a6f30), text (#f5f0e8), text-dim (#8a8678), border (#2a2820), void (#1a1410)
   - fontFamily : display: Cinzel, body: Cormorant Garamond, mono: DM Mono
   - plugins: []

2. astro.config.mjs
   - output: 'static' (SSG)
   - integrations: [tailwind()]
   - vite: { define: { 'import.meta.env.PUBLIC_API_URL': ... } }
   - build: { outDir: '../www' } (pour Capacitor sync)

Retourne UNIQUEMENT les 2 fichiers JS.
```

---

## Prompt 3 : Pages statiques (landing + 404) (4 min)

```
Pages Astro statiques (pas de logique complexe).

Génère COMPLETS :

1. src/pages/index.astro (landing)
   - Import BaseLayout
   - Hero section : titre "✦ Karmic Gochara", subtitle "Ta carte karmique en transit"
   - Sigil SVG emoji (optionnel)
   - Scroll CTA vers login
   - Pas de login card (sera client:load séparé)

2. src/pages/404.astro
   - Message "Page mystère..."
   - Lien vers home
   - Thème cosmic

Retourne UNIQUEMENT les 2 fichiers .astro.
```

---

## Prompt 4 : Types + Env (3 min)

```
Types TypeScript + Astro env.

Génère COMPLETS :

1. src/types.ts
   - type User = { id: string, pseudo: string, plan: 'free' | 'pro', ... }
   - type SynthesisResponse = { ok: boolean, synthesis: string, fullText: string, ... }
   - type LoginResponse = { ok: boolean, access_token: string, refresh_token: string, ... }
   - type RegisterData = { pseudo, email, year, month, day, hour, minute, city, lat, lon, tz }
   - type CalculateBody = { pseudo, transit_date, transit_time, transit_location }
   - Export tous les types.

2. src/env.d.ts
   - Astro ambient declarations
   - Type PUBLIC_API_URL env var

Retourne UNIQUEMENT les 2 fichiers .ts.
```

---

## Prompt 5 : Composants statiques (login/register cards layout) (4 min)

```
Composants layout Astro (HTML + Tailwind, pas de logique JS).

Génère COMPLETS :

1. src/components/HeroSection.astro
   - Texte "✦ KARMIC GOCHARA" (Cinzel font-display)
   - Sous-titre (Cormorant)
   - 2-3 lignes de teaser
   - Bouton "S'identifier" (astro:navigate vers #login)
   - Tailwind cosmic colors

2. src/components/LoginCardLayout.astro (layout seulement, pas de client:load yet)
   - Input pseudo (dark input, gold border on focus)
   - Bouton login (gold background, cosmic-bg text)
   - Error div (empty)
   - Register toggle button
   - NO JavaScript — sera wrap en client:load plus tard

Retourne UNIQUEMENT les 2 fichiers .astro, très clean.
```

---

## Prompt 6 (Optionnel) : Package.json + .env.example (2 min)

```
Fichiers de projet.

Génère COMPLETS :

1. astro/package.json
   - name: karmic-gochara-astro
   - version: 0.1.0
   - scripts: dev, build, preview, sync:capacitor
   - deps: astro@latest, tailwindcss, typescript
   - devDeps: @types/node, etc.
   - "sync:capacitor": "cp -r dist/* ../www/ && npx cap sync"

2. astro/.env.example
   - PUBLIC_API_URL=https://gochara-api-drln4gv4fa-ew.a.run.app
   - PUBLIC_CAPACITOR_API_URL=https://gochara-api-drln4gv4fa-ew.a.run.app
   - # Local dev default = /api (same origin)

Retourne les 2 fichiers `.json` et `.env.example`.
```

---

## 📋 Checklist Exécution

- [ ] Prompt 1 lancé (~5 min) → fichiers copiés dans `astro/src/layouts/` et `astro/src/styles/`
- [ ] Prompt 2 lancé (~5 min) → fichiers copiés dans `astro/`
- [ ] Prompt 3 lancé (~4 min) → fichiers copiés dans `astro/src/pages/`
- [ ] Prompt 4 lancé (~3 min) → fichiers copiés dans `astro/src/`
- [ ] Prompt 5 lancé (~4 min) → fichiers copiés dans `astro/src/components/`
- [ ] Prompt 6 opt lancé (~2 min) → fichiers copiés en `astro/`

**Total Gemma :** 15-20 min (pause RAM entre deux si besoin)

---

## 📝 Parallèle (moi — Claude)

Pendant que Gemma roule :
- [ ] `astro/src/lib/api.ts` (JWT + streamingRequest)
- [ ] `astro/src/lib/auth.ts` (login/logout/refresh)
- [ ] `astro/src/lib/capacitor-bridge.ts` (plugins bridge)
- [ ] Flask refactor : `/auth/login`, `/auth/refresh`, `@token_required` middleware
- [ ] `astro/src/components/LoginCard.astro` (client:load logic)
- [ ] Tests auth end-to-end doc

**Fusion jour 4-5 :** Assemblage + validation ensemble.
