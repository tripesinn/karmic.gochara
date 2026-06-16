# Migration Flask → Astro — Karmic Gochara

**Goal:** Remplacer les templates Jinja + JS vanilla par Astro (SSG + composants modernes), tout en gardant Flask comme API backend.

**Architecture :** Astro côté front-end (build statique deployé sur Cloudflare Pages ou Vercel), Flask maintenu comme REST API. Les deux coexistants dans le même repo sous `astro/`. Capacitor pointe vers `astro/dist/` au lieu de `www/`.

**Tech Stack :** Astro 5.x + Tailwind CSS v4 + TypeScript + Astro Islands (client:load)

---

## Phase 0 : Structure & Setup

### Task 0.0 — Audit final + backup des fichiers critique

**Prérequis :** Snapshots de `templates/index.html`, `static/app.js`, `static/style.css` avant transformation.

**Fichier :** `/savepoint/2026-06-16_pre-astro/`

---

### Task 0.1 — Initialisation du projet Astro

**Objectif :** Créer la structure `astro/` avec Tailwind CSS v4, TypeScript, et la config de base.

**Fichiers :**
- Create: `astro/package.json`
- Create: `astro/astro.config.mjs`
- Create: `astro/tsconfig.json`
- Create: `astro/src/env.d.ts`

**Étapes :**
1. `cd /Users/jero87/karmic.gochara`
2. `npm create astro@latest astro -- --template basics --typescript --no-install`
3. `cd astro && npm install`
4. Installer Tailwind : `npx astro add tailwind`
5. Configurer `astro.config.mjs` pour `output: 'static'` (SSG)
6. Vérifier : `npm run dev` → page blanche OK

**Base URL API :** via variable d'env `PUBLIC_API_URL` (Vite), défaut = `/api` (même origine en dev, URL distante en prod mobile)

---

### Task 0.2 — Thème global dark gold + assets

**Objectif :** Migrer le thème visuel existant dans la configuration Tailwind + assets statiques.

**Fichiers :**
- Create: `astro/src/styles/global.css`
- Create: `astro/public/static/manifest.json` (copie de `static/manifest.json`)
- Create: `astro/public/static/icons/` (copie des icônes)
- Create: `astro/public/static/sw.js` (service worker)

**Palette Tailwind :**
```js
// tailwind.config.mjs (ou via CSS @theme si v4)
export default {
  theme: {
    extend: {
      colors: {
        cosmic: {
          bg: '#0c0a08',
          gold: '#c9a84c',
          'gold-dim': '#8a6f30',
          text: '#f5f0e8',
          'text-dim': '#8a8678',
          border: '#2a2820',
          void: '#1a1410',
          glyph: 'rgba(201,168,76,0.18)',
          mist: 'rgba(201,168,76,0.06)',
        }
      },
      fontFamily: {
        display: ['Cinzel', 'serif'],
        body: ['Cormorant Garamond', 'Georgia', 'serif'],
        mono: ['DM Mono', 'monospace'],
      }
    }
  }
}
```

**Google Fonts :** Charger dans `BaseLayout.astro` via `<link>` (mêmes fonts qu'avant)

**global.css :** Contiendra les animations (`@keyframes fadeUp`), les dégradés de fond (`body::before`, `body::after`), et les styles globaux hérités.

**Service Worker :** Copier `static/sw.js` dans `astro/public/static/sw.js`

---

### Task 0.3 — API Client Layer

**Objectif :** Créer une couche d'appel API unifiée côté Astro, remplaçant les fetch() éparpillés.

**Fichiers :**
- Create: `astro/src/lib/api.ts`
- Create: `astro/src/lib/auth.ts`
- Create: `astro/src/types.ts`

**api.ts :**
```typescript
const BASE = import.meta.env.PUBLIC_API_URL || '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    credentials: 'include', // cookies Flask
    ...options,
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json();
}

export const api = {
  login: (pseudo: string) => request<LoginResponse>('/login', { method: 'POST', body: JSON.stringify({ pseudo }) }),
  register: (data: RegisterData) => request<RegisterResponse>('/register', { method: 'POST', body: JSON.stringify(data) }),
  calculate: (body: CalculateBody) => request<SynthesisResponse>('/calculate', { method: 'POST', body: JSON.stringify(body) }),
  hookTransit: (body: HookBody) => fetch(`${BASE}/hook/transit`, { method: 'POST', body: JSON.stringify(body), credentials: 'include' }), // SSE
  stripeCheckout: (body: { product_type: string }) => request<StripeResponse>('/stripe/checkout', { method: 'POST', body: JSON.stringify(body) }),
  profile: () => request<UserProfile>('/api/profile'),
  // ... etc
};
```

**types.ts :** Tous les types TypeScript pour les réponses API.

---

## Phase 1 : Layout & Landing

### Task 1.1 — BaseLayout.astro

**Fichier :** Create: `astro/src/layouts/BaseLayout.astro`

Reprendre le fichier généré par Gemma, mais avec :
- Tailwind CSS classes (pas de `<style>` inline)
- Google Fonts + meta PWA
- Slot pour le contenu
- Composant `<SEO>` pour meta OG

```astro
---
import '../../public/static/manifest.json' with { type: 'json' };
export interface Props {
  title: string;
  description?: string;
  ogImage?: string;
}
const { title, description, ogImage } = Astro.props;
---
<!DOCTYPE html>
<html lang="fr">
<head>
  <!-- ... meta, PWA, fonts, global.css, manifest, icons -->
</head>
<body class="bg-cosmic-bg text-cosmic-text font-body">
  <slot />
</body>
</html>
```

### Task 1.2 — Landing Page (index.astro)

**Fichier :** Create: `astro/src/pages/index.astro`

- Hero section : sigil, titre "✦ Karmic Gochara", sous-titre "Ta carte karmique en transit"
- Si déjà connecté (vérification cookie session) → redirect vers `/app`
- Bouton "S'identifier" → scroll vers login card
- Login card avec champ pseudo + bouton "✦ ENTRER"
- Register card (expandable) avec champs date/heure/ville

**Composants :**
- `src/components/HeroSection.astro`
- `src/components/LoginCard.astro` (îlot client:load)
- `src/components/RegisterForm.astro` (îlot client:load)

---

## Phase 2 : Auth Flow

### Task 2.1 — Login island (interactif)

**Fichier :** Create: `astro/src/components/LoginCard.astro` (client:load)

- Champ pseudo + bouton "✦ ENTRER"
- Fetch POST `/login` → si ok, `window.location.href = '/app'`
- Gestion erreur : pseudo inconnu, erreur réseau
- Spinner pendant l'appel
- State : `{ pseudo: string, loading: boolean, error: string | null }`

### Task 2.2 — Register island (interactif)

**Fichier :** Create: `astro/src/components/RegisterForm.astro` (client:load)

- Champs : date naissance, heure, ville (avec autocomplétion)
- Fetch autocomplétion ville via `/geocode`
- Fetch POST `/register` → si ok, `window.location.href = '/app'`
- Validation coté client avant envoi
- Mêmes states que Login

### Task 2.3 — App Layout (protégé)

**Fichier :**
- Create: `astro/src/layouts/AppLayout.astro`
- Create: `astro/src/pages/app.astro` (ou `/app/index.astro`)

Layout connecté avec :
- Header "✦ Karmic Gochara" + plan badge + logout
- Navigation (Daily Reading, Carte, Chat, PRO Upgrade)
- Slot pour le contenu

Page `/app` vérifie la session (fetch `/api/profile`), si pas connecté → redirect `/`

---

## Phase 3 : Composants Métier

### Task 3.1 — DailyReading island

**Fichier :** Create: `astro/src/components/DailyReading.astro` (client:load)

Reprendre le fichier Gemma mais avec Tailwind + types TypeScript.

**Comportement :**
- Affiche la date du jour
- Bouton "◆ LIRE LE SIGNAL"
- Fetch POST `/calculate` (ou `/hook/transit` pour la version gratuite) avec spinner
- Affiche le résultat dans une card formatée (Markdown → HTML via `marked`)
- Rating bar après résultat (👍/👎 + consent modal)
- Gère le bouton "EXPAND" pour approfondir un sujet
- Gère le flux SSE `/hook/transit` (streaming)

### Task 3.2 — ProUpgrade island

**Fichier :** Create: `astro/src/components/ProUpgrade.astro` (client:load)

Reprendre le fichier Gemma avec Tailwind + types.

**Comportement :**
- Card "GOCHARA PRO — Offert Beta"
- Bouton "Activer PRO"
- Fetch POST `/stripe/checkout` → si `data.ok && data.beta` → reload
- Gère le retour de Stripe (vérification `plan_check` après redirect)
- État : `{ loading, status, error }`

### Task 3.3 — KarmicChart component

**Fichier :** Create: `astro/src/components/KarmicChart.astro` (client:load)

- Affiche l'image SVG : `POST /chart/karmic.svg?pseudo=xxx`
- Zone cliquable → fetch `/chart/interpret` → affiche interprétation
- Modal interprétation avec fermeture

### Task 3.4 — Chat island

**Fichier :** Create: `astro/src/components/ChatBox.astro` (client:load)

- Vérification quota via `/chat/status`
- Input + historique scrollable
- Fetch POST `/chat/ask`
- Sauvegarde historique localStorage

### Task 3.5 — Settings/Providers modal

**Fichier :** Create: `astro/src/components/SettingsModal.astro` (client:load)

- Sélecteur provider IA (OpenRouter, Claude, Gemini, local)
- Inputs clé API / model
- Sauvegarde localStorage
- Panel benchmark IA (fetch `/api/benchmark`, POST `/api/vote`)

---

## Phase 4 : Capacitor & Mobile Sync

### Task 4.1 — Build output → Capacitor webDir

**Objectif :** Rediriger le build Astro vers `www/` pour Capacitor.

**Config :** Modifier `capacitor.config.json` > `webDir` pour pointer vers `astro/dist/` (ou garder `www/` et copier le build).

Alternative : `astro build` → `astro/dist/` et faire un symlink ou copie vers `www/`.

**Fichiers Capacitor à préserver :**
- `capacitor.config.json` (appId, plugins AdMob/SplashScreen/StatusBar)
- `android/` et `ios/` (projets natifs + plugins Java/Swift)
- `www/` peut être remplacé par `astro/dist/`

### Task 4.2 — Conditional API URL for Capacitor

**Dans api.ts :**
```typescript
const isCapacitor = !!(window as any).Capacitor?.isNative;
const BASE = isCapacitor
  ? 'https://gochara-api-732214018947.europe-west9.run.app'
  : import.meta.env.PUBLIC_API_URL || '';
```

---

## Phase 5 : Pages additionnelles

### Task 5.1 — Privacy Policy

**Fichier :** Create: `astro/src/pages/privacy.astro`

Reprendre `templates/privacy-policy.html` en pure Astro (statique, bilingue).

### Task 5.2 — Benchmark page

**Fichier :** Create: `astro/src/pages/benchmark.astro`

Reprendre `templates/benchmark.html` avec data fetchée depuis `/api/benchmark` (îlot client:load).

### Task 5.3 — Payment success

**Fichier :** Create: `astro/src/pages/success.astro`

Page de transition Stripe avec spinner + fetch `/api/plan_check` puis redirect vers `/`.

### Task 5.4 — Delete account

**Fichier :** Create: `astro/src/pages/delete-account.astro`

Formulaire de suppression.

### Task 5.5 — 404

**Fichier :** Create: `astro/src/pages/404.astro`

Page 404 custom.

---

## Phase 6 : Déploiement

### Task 6.1 — Déploiement Astro (Cloudflare Pages ou Vercel)

**Option A — Cloudflare Pages (recommandé)** :
- Build command : `npm run build` (cd astro/)
- Output dir : `dist/`
- Domaine : `app.karmicgochara.app` ou garder `karmicgochara.app`
- API backend : `api.karmicgochara.app` (Cloud Run)

**Option B — Vercel** :
- Framework preset : Astro
- Build + output : same

**Option C — Cloud Run + Nginx** :
- Servir `astro/dist/` via Nginx depuis le même conteneur que Flask (proxy /api → Flask)
- Avantage : même domaine, pas de CORS
- Inconvénient : plus lourd que Cloudflare Pages

### Task 6.2 — CORS config sur Flask

**Objectif :** Si Astro et Flask sont sur des domaines différents, ajouter CORS.

Dans `app.py` ou via extension `flask-cors` :
```python
from flask_cors import CORS
CORS(app, origins=['https://app.karmicgochara.app', 'capacitor://localhost'])
```

---

## Architecture finale

```
karmic.gochara/
├── app.py                  # Flask API (inchangé)
├── blueprints/             # Routes API (inchangées)
├── astro_calc.py           # Moteur astro (inchangé)
├── ai_interpret.py         # IA (inchangé)
├── ...
├── astro/                  # NOUVEAU : Projet Astro
│   ├── package.json
│   ├── astro.config.mjs
│   ├── tailwind.config.mjs
│   ├── tsconfig.json
│   ├── public/
│   │   ├── static/
│   │   │   ├── manifest.json
│   │   │   ├── sw.js
│   │   │   └── icons/
│   └── src/
│       ├── layouts/
│       │   ├── BaseLayout.astro
│       │   └── AppLayout.astro
│       ├── pages/
│       │   ├── index.astro       # Landing + Login
│       │   ├── app.astro         # App connectée
│       │   ├── privacy.astro
│       │   ├── benchmark.astro
│       │   ├── success.astro
│       │   ├── delete-account.astro
│       │   └── 404.astro
│       ├── components/
│       │   ├── HeroSection.astro
│       │   ├── LoginCard.astro       (client:load)
│       │   ├── RegisterForm.astro    (client:load)
│       │   ├── DailyReading.astro    (client:load)
│       │   ├── ProUpgrade.astro      (client:load)
│       │   ├── KarmicChart.astro     (client:load)
│       │   ├── ChatBox.astro         (client:load)
│       │   ├── SettingsModal.astro   (client:load)
│       │   ├── RatingBar.astro       (client:load)
│       │   └── ExpandCTA.astro       (client:load)
│       ├── lib/
│       │   ├── api.ts
│       │   ├── auth.ts
│       │   └── types.ts
│       └── styles/
│           └── global.css
├── android/                 # Capacitor (inchangé)
├── ios/                     # Capacitor (inchangé)
├── capacitor.config.json    # webDir → astro/dist (ou www copié)
└── www/                     # Optionnel : backup de l'ancienne app statique
```

---

## Ordre d'exécution conseillé

1. **Phase 0** : Setup Astro + Tailwind + API client + thème (1 session)
2. **Phase 1** : Layout + Landing page fonctionnelle (1 session)
3. **Phase 2** : Auth flow complet (1-2 sessions)
4. **Phase 3.1** : DailyReading + ProUpgrade (1 session)
5. **Phase 3.2-3.5** : Chart, Chat, Settings, Expand (1 session)
6. **Phase 4** : Capacitor sync (1 session)
7. **Phase 5** : Pages additionnelles (1 session)
8. **Phase 6** : Déploiement + CORS (1 session)

**Total estimé :** 8-10 sessions de travail

---

## Pièges & Risques

- **Cookies Flask + domaines séparés** : Si Astro est sur un sous-domaine, les cookies Flask ne seront pas envoyés → besoin de JWT ou de config SameSite=None + Secure + HTTPS
- **SSE streaming** : `/hook/transit` utilise SSE. Astro en SSG ne peut pas streamer nativement → le composant DailyReading doit fetch l'endpoint Flask directement depuis le navigateur
- **i18n** : Actuellement injectée côté serveur. En Astro, soit inclure toutes les traductions dans le JS client, soit charger depuis un endpoint `/api/lang`
- **Monkey-patch fetch** : `window.fetch` est patché pour ajouter les clés API utilisateur → à reproduire dans le client API layer
- **Capacitor plugins natifs** : Les plugins Java/Swift (GemmaSynthesisPlugin, NativeAIPlugin) ne sont pas impactés mais la communication Astro → Capacitor bridge doit être maintenue via `window.Capacitor`
- **Cache navigateur** : Les cookies de session existants continueront de fonctionner sur le même domaine
