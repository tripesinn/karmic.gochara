# Migration Flask → Astro + App Store iOS/Android — Karmic Gochara

**Goal :** Remplacer les templates Jinja + JS vanilla par Astro (SSG), tout en préparant iOS App Store + Android beta fermé **en parallèle**.

**Architecture :** 
- **Web :** Astro SSG sur `karmicgochara.app` (Cloudflare Pages)
- **API :** Flask REST sur `api.karmicgochara.app` (Cloud Run)
- **Mobile :** Capacitor (iOS + Android) embarquant `astro/dist/` → `www/`
- **Auth :** JWT côté Astro **+ refactor Flask** (`/auth/login` retourne tokens)

**Tech Stack :** Astro 5.x + Tailwind CSS v4 + TypeScript + Capacitor 6.x

---

## Phase 0 : Structure & Setup (Astro + Auth JWT)

### Task 0.0 — Backup & audit

**Fichiers à sauvegarder :** `templates/index.html`, `static/app.js`, `static/style.css`

**Dossier :** `/savepoint/2026-06-16_pre-astro/`

---

### Task 0.1 — Initialisation Astro

```bash
cd /Users/jero87/karmic.gochara
npm create astro@latest astro -- --template basics --typescript --no-install
cd astro && npm install
npx astro add tailwind
# Configurer astro.config.mjs pour output: 'static' (SSG)
npm run dev  # Vérifier page blanche
```

**Fichiers :**
- `astro/package.json`, `astro.config.mjs`, `tsconfig.json`, `src/env.d.ts`
- `astro/src/pages/404.astro` (créer custom)

---

### Task 0.2 — Thème Tailwind + assets

**Palette cosmic :**
```js
// tailwind.config.mjs
colors: {
  cosmic: {
    bg: '#0c0a08',
    gold: '#c9a84c',
    'gold-dim': '#8a6f30',
    text: '#f5f0e8',
    'text-dim': '#8a8678',
    border: '#2a2820',
    void: '#1a1410',
  }
}
fontFamily: {
  display: ['Cinzel', 'serif'],
  body: ['Cormorant Garamond', 'Georgia', 'serif'],
  mono: ['DM Mono', 'monospace'],
}
```

**Fichiers :**
- `astro/src/styles/global.css` (animations, dégradés, reset)
- `astro/public/static/manifest.json` (copie de Flask)
- `astro/public/static/icons/` (copie des icones)
- `astro/public/static/sw.js` (service worker)
- Google Fonts link dans `BaseLayout.astro`

---

### Task 0.3 — API Client Layer + JWT (⚠️ CRITIQUE)

**Fichiers :**
- Create: `astro/src/lib/api.ts`
- Create: `astro/src/lib/auth.ts`
- Create: `astro/src/lib/capacitor-bridge.ts`
- Create: `astro/src/lib/types.ts`

**api.ts — Structure:**
```typescript
const BASE = (() => {
  const isCapacitor = !!(window as any).Capacitor?.isNative;
  return isCapacitor
    ? 'https://gochara-api-732214018947.europe-west9.run.app'
    : import.meta.env.PUBLIC_API_URL || '';
})();

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options?.headers
    },
    credentials: 'include', // Fallback cookies (retrocomp)
    ...options,
  });
  if (res.status === 401) {
    // Tentative refresh_token
    const refreshed = await refreshAccessToken();
    if (!refreshed) window.location.href = '/';
    return request(path, options); // Retry
  }
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json();
}

export const api = {
  login: (pseudo: string) => request<{access_token: string, refresh_token: string}>('/auth/login', {...}),
  register: (data: RegisterData) => request<{access_token, refresh_token}>('/auth/register', {...}),
  calculate: (body: CalculateBody) => streamingRequest('/calculate', body), // SSE + fetch ReadableStream
  profile: () => request<UserProfile>('/api/profile'),
  stripeCheckout: (product_type: string) => request<{ok: boolean, beta: boolean}>('/stripe/checkout', {...}),
  // ... etc
};

async function refreshAccessToken(): Promise<boolean> {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh })
    });
    if (res.ok) {
      const { access_token } = await res.json();
      localStorage.setItem('access_token', access_token);
      return true;
    }
  } catch {}
  return false;
}

async function streamingRequest(path: string, body: object) {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    },
    credentials: 'include',
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.body!.getReader(); // ReturnReadableStreamDefaultReader pour SSE
}
```

**auth.ts :**
```typescript
export async function login(pseudo: string) {
  const { access_token, refresh_token } = await api.login(pseudo);
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
  return { ok: true };
}

export async function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/';
}

export function getToken(): string | null {
  return localStorage.getItem('access_token');
}

export async function isAuthenticated(): Promise<boolean> {
  try {
    await api.profile();
    return true;
  } catch {
    return false;
  }
}
```

**capacitor-bridge.ts :**
```typescript
export const capacitorBridge = {
  isNative: () => !!(window as any).Capacitor?.isNative,
  // GemmaSynthesis plugin
  callPlugin: async (name: string, method: string, args: any) => {
    if (!capacitorBridge.isNative()) return null;
    const plugin = (window as any).Capacitor.Plugins[name];
    if (!plugin) throw new Error(`Plugin ${name} not found`);
    return plugin[method](args);
  }
};
```

**types.ts :** Tous les types TypeScript pour les réponses API.

---

### Task 0.4 — Flask refactor (JWT + refresh)

**À faire côté Flask :**
```python
from datetime import datetime, timedelta
import jwt

SECRET = os.getenv('JWT_SECRET', 'dev-secret')

@app.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.json
    pseudo = data.get('pseudo')
    user = User.query.filter_by(pseudo=pseudo).first()
    if not user:
        return {'ok': False, 'error': 'Pseudo not found'}, 401
    
    access_token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},
        SECRET, algorithm='HS256'
    )
    refresh_token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=7)},
        SECRET, algorithm='HS256'
    )
    return {
        'ok': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'pseudo': pseudo
    }

@app.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    data = request.json
    refresh = data.get('refresh_token')
    try:
        payload = jwt.decode(refresh, SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        access_token = jwt.encode(
            {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=24)},
            SECRET, algorithm='HS256'
        )
        return {'ok': True, 'access_token': access_token}
    except:
        return {'ok': False, 'error': 'Invalid refresh token'}, 401

# Middleware : extraire token + vérifier
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return {'error': 'Missing token'}, 401
        token = auth.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            request.user_id = payload['user_id']
        except:
            return {'error': 'Invalid token'}, 401
        return f(*args, **kwargs)
    return decorated

# Tous les endpoints sensibles : @token_required
@app.route('/api/profile')
@token_required
def profile():
    user = User.query.get(request.user_id)
    return {'user': user.to_dict()}
```

**CORS :**
```python
from flask_cors import CORS
CORS(app, 
     origins=['https://karmicgochara.app', 'https://app.karmicgochara.app', 'capacitor://localhost'],
     supports_credentials=True)
```

**Env :** Ajouter `JWT_SECRET` à `.env` (Cloud Run secrets).

---

## Phase 0.75 : Tests auth (validation critique)

### Task 0.75 — End-to-end auth test

1. **Astro dev :** Login → check localStorage JWT
2. **Astro dev :** Logout → localStorage cleared
3. **Astro dev :** Refresh page après login → `/api/profile` fetch avec JWT → dashboard charges
4. **Astro dev :** Call `/calculate` avec JWT + monitoring → works
5. **Curl tests :** Vérifier que Flask accept `Authorization: Bearer xxx`

**Blockers :** Si auth échoue ici, rien après ne fonctionnaire.

---

## Phase 1 : Layout & Landing

### Task 1.1 — BaseLayout.astro

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
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#0c0a08" />
  
  <!-- PWA -->
  <link rel="manifest" href="/static/manifest.json" />
  <link rel="apple-touch-icon" href="/static/icons/icon-192.png" />
  <link rel="icon" href="/favicon.ico" />
  
  <!-- Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital@0;1&family=DM+Mono&display=swap" rel="stylesheet" />
  
  <!-- Meta -->
  <title>{title}</title>
  <meta name="description" content={description} />
  <meta property="og:title" content={title} />
  <meta property="og:image" content={ogImage} />
  
  <slot name="head" />
</head>
<body class="bg-cosmic-bg text-cosmic-text font-body min-h-screen flex flex-col">
  <slot />
  <script src="/static/sw.js"></script>
</body>
</html>
```

### Task 1.2 — Landing page (index.astro)

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import HeroSection from '../components/HeroSection.astro';
import LoginCard from '../components/LoginCard.astro';

// Check if already authenticated
import { isAuthenticated } from '../lib/auth';
const authed = await isAuthenticated() ? true : false;
if (authed) return Astro.redirect('/app');
---

<BaseLayout title="Karmic Gochara — Ta carte karmique en transit">
  <HeroSection />
  <LoginCard client:load />
</BaseLayout>
```

### Task 1.3 — HeroSection.astro

Titre "✦ Karmic Gochara", subtitle "Ta carte karmique en transit", scroll CTA vers login.

---

## Phase 2 : Auth Flow (JWT)

### Task 2.1 — LoginCard.astro (client:load)

```astro
---
// Static part
---
<div class="max-w-sm mx-auto p-6">
  <h2 class="text-2xl gold mb-4">✦ ENTRER</h2>
  <input id="pseudo-input" type="text" placeholder="Pseudo" class="input" />
  <button id="login-btn" onclick="handleLogin()" class="btn-primary">✦ CONNEXION</button>
  <div id="login-error" class="error"></div>
</div>

<script>
  import { login } from '../lib/auth';

  window.handleLogin = async () => {
    const pseudo = document.getElementById('pseudo-input').value.trim();
    const errorDiv = document.getElementById('login-error');
    if (!pseudo) { errorDiv.textContent = 'Pseudo requis'; return; }
    
    try {
      errorDiv.textContent = 'Connexion...';
      await login(pseudo);
      window.location.href = '/app';
    } catch (e) {
      errorDiv.textContent = (e as Error).message;
    }
  };
</script>
```

### Task 2.2 — RegisterForm.astro (client:load)

Champs date/heure/ville + fetch `/geocode` pour autocomplétion.

### Task 2.3 — AppLayout.astro

Layout protégé with auth check. Header + nav.

### Task 2.4 — /app/index.astro

Page connectée (redirect si pas auth).

---

## Phase 3 : Composants Métier

### Task 3.1 — DailyReading.astro (client:load)

**Critique :** Utiliser `fetch + ReadableStream` pour SSE, PAS `EventSource`.

```typescript
async function* streamCalculate(body: object) {
  const reader = await api.streamingRequest('/calculate', body);
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const text = decoder.decode(value);
    for (const line of text.split('\n')) {
      if (line.startsWith('data: ')) {
        yield JSON.parse(line.slice(6));
      }
    }
  }
}
```

### Task 3.2–3.5 — ProUpgrade, KarmicChart, ChatBox, SettingsModal

(Copier structures du plan original.)

---

## Phase 4 : Capacitor & Build → App Store iOS/Android (⚠️ NOUVEAU)

### Task 4.0 — Prépa Capacitor + versioning

**Capacitor config :**
```json
{
  "appName": "Karmic Gochara",
  "appId": "com.karmicgochara.app",
  "webDir": "../astro/dist",
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000
    },
    "StatusBar": {
      "backgroundColor": "#0c0a08",
      "style": "DARK"
    }
  }
}
```

**Versioning :** Store version in `package.json` + sync Capacitor.
```bash
npm version patch
# Update capacitor.config.json + ios/Podfile + android/build.gradle
npx cap sync
```

### Task 4.1 — Build automation

**`astro/package.json` post-build :**
```json
{
  "scripts": {
    "build": "astro build && npm run sync:capacitor",
    "sync:capacitor": "cp -r dist/* ../www/ && npx cap sync"
  }
}
```

### Task 4.2 — iOS Cert + Provisioning

1. Apple Developer Account (si pas déjà fait)
2. Create signing certificate (iOS Development)
3. Register device (UDID des testeurs)
4. Create provisioning profile
5. Xcode : organizer → profiles → import

### Task 4.3 — iOS build + TestFlight

```bash
cd ios
# Ouvrir dans Xcode
xcodebuild -workspace KarmicGochara.xcworkspace -scheme KarmicGochara \
  -configuration Release -derivedDataPath build \
  -archivePath build/KarmicGochara.xcarchive archive

# Uploader sur TestFlight
xcrun altool --upload-app --type ios \
  --file build/KarmicGochara.ipa \
  --username jero@email.com \
  --password @keychain:notarize-password
```

**Ou simplement :** Xcode → Product → Archive → Distribute → TestFlight.

### Task 4.4 — Android beta fermé (maintenant)

```bash
cd android
./gradlew bundleRelease
# Fichier : android/app/build/outputs/bundle/release/app-release.aab

# Google Play Console → Internal testing (testeurs fermés)
# Upload AAB + fill store listing
```

**OU :** Si tu veux APK direct pour testeurs (plus rapide) :
```bash
./gradlew assembleRelease
# Fichier : android/app/build/outputs/apk/release/app-release.apk
# Distribute via email ou Firebase App Distribution
```

---

## Phase 5 : Pages additionnelles

- Privacy policy
- Benchmark page
- Stripe success/cancel
- 404

---

## Phase 6 : Déploiement web

- Astro → Cloudflare Pages
- Flask → Cloud Run (déjà fait)
- DNS + routing

---

## Phase 7 : App Store final

### Task 7.1 — iOS App Store submission

1. Create App Store Connect record
2. Fills screenshots, description, privacy policy, keywords
3. Submit for review (Apple takes 24–48h)
4. Address any rejections (usually privacy/payment)

### Task 7.2 — Android Play Store submission

1. Remplir app listing (screenshots, descriptions, permissions)
2. Set beta tester group
3. Submit to Play Store (Google takes ~2h for first APK, internal testing is instant)

---

## Timeline révisée (avec App Store)

| Phase | Tâches | Sessions | Notes |
|-------|--------|----------|-------|
| 0 | Astro init + JWT Flask + Capacitor bridge | 2 | **Critique** |
| 0.75 | Auth end-to-end tests | 1 | **Blockers here** |
| 1 | Landing + BaseLayout | 1 | |
| 2 | Auth flow (login/register) | 1-2 | |
| 3 | DailyReading, ProUpgrade, Chart, Chat | 2 | SSE critical |
| 4 | Capacitor + Android beta NOW | 1 | **Testeurs occupés** |
| 5 | Pages additionnelles | 1 | |
| 6 | Web deploy (karmicgochara.app) | 1 | |
| 7 | iOS App Store + Play Store listings | 1 | Marketing materials |

**Total :** 12–14 sessions. **Parallèle :** Android beta après Phase 4.1–4.4 (semaine 2), iOS TestFlight après Phase 4.2–4.3 (semaine 3).

---

## Pièges & solutions

| Faille | Risque | Solution |
|--------|--------|----------|
| JWT + localStorage | localStorage peut être vidé | Ajouter refresh_token + `/auth/refresh` |
| iOS localStorage | Peut être persisté session-only | Utiliser Keychain plugin pour tokens |
| SSE + EventSource | N'accepte pas `Authorization` header | Utiliser fetch + ReadableStream (Task 3.1) |
| Capacitor plugins | Appels natifs oubliés | Proxy via `capacitor-bridge.ts` (Task 0.3) |
| i18n | Langue perdue après reload | localStorage + `/set_lang` persist |
| Build → www/ | Cache, oublis | Automatiser avec post-build script |
| CORS + JWT | Cookies bloqués si différent domaine | JWT résout ça, CORS pour préflights |
| App Store review | Rejections possibles | Passer au design review / privacy expert |
| Versioning mobile | Build numérotation confuse | Sync version npm → Capacitor → app stores |
| Race conditions UI | Flash login/app | Pre-check session avec loading state |

---

## Ordre exact = TODO

1. ✅ **Validé plan** (tu es ici)
2. **Phase 0.0–0.4 :** JWT + Astro init (start cette session ou prochaine)
3. **Phase 0.75 :** Tests auth (valider avant phase 1)
4. **Phase 4.1–4.4 :** Android beta build (après phase 3, testeurs commencent)
5. **Phases 1–3 :** Web frontend cœur
6. **Phase 4.2–4.3 :** iOS TestFlight (après web stable)
7. **Phases 5–7 :** Pages + déploiement final

**Vraie question :** Tu veux que je lance **Phase 0.1 maintenant** (Astro init) ou tu vas chercher Gemma local d'abord ?
