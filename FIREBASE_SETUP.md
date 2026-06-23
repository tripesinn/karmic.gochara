# Firebase Setup — Karmic GoChara

> Documentation de référence pour la stack Firebase en production.
> À jour au : 20 juin 2026 (session Pixel 10)

---

## Vue d'ensemble

| Élément | Valeur |
|---|---|
| **Project ID** | `karmic-gochara-cloud` |
| **Project Number** | `732214018947` |
| **Display Name** | `karmic gochara cloud` |
| **Region Firestore** | `europe-west1` (Belgique) |
| **Plan Firebase** | Pay-as-you-go (Blaze/GCP default) |
| **Android package** | `com.karmicgochara.app` |
| **SHA-1 release** | `7A:96:C6:1E:E5:ED:B3:EC:84:67:59:26:4E:05:D1:7A:EA:81:0E:85` |
| **SHA-256 release** | `80:46:D9:FC:C8:C1:18:C9:31:FD:08:1E:EE:93:63:39:2E:15:9B:4F:78:F9:56:91:22:73:4A:40:D4:C0:08:6E` |
| **SHA-1 debug** | `9E:F5:FB:96:E3:69:D9:F4:DE:67:21:AC:F9:B2:27:74:92:66:28:AE` |
| **SHA-256 debug** | `1C:1D:3B:12:9F:F2:06:B3:88:AC:22:2C:14:9D:1E:4F:38:04:EA:A6:52:F7:B1:57:45:F7:1D:4D:41:F2:C5:5F` |

---

## Clés API & Client OAuth

| Champ | Valeur |
|---|---|
| **apiKey (Web/Browser)** | `AIzaSyAr2JW-mbg8ZQJof7U76Xe2m9DibrVBB6M` |
| **apiKey (Android)** | `AIzaSyCbJo81VBW9r2HaR6b5xwta3nFYV4txQns` |
| **OAuth Client (Web)** | `732214018947-ee5v5hi70fer05edbti3hjig22knngb8.apps.googleusercontent.com` |
| **OAuth Client (Android)** | `732214018947-ma2fi67soi8d6bt5toevq7rto85474ac.apps.googleusercontent.com` |

---

## Domaines autorisés

### Firebase Auth (authorizedDomains)

```
karmic-gochara-cloud.firebaseapp.com
karmic-gochara-cloud.web.app
localhost
capacitorio-plugins-capacitor-google-auth.appspot.com
```

> ⚠️ Si un nouveau redirect OAuth échoue avec "The requested action is invalid",
> c'est souvent qu'un domaine manque ici. Ajouter via :
>
> ```bash
> curl -X PATCH -H "X-Goog-User-Project: karmic-gochara-cloud" \
>   -H "Authorization: Bearer $(gcloud auth print-access-token)" \
>   -H "Content-Type: application/json" \
>   -d '{"authorizedDomains": ["karmic-gochara-cloud.firebaseapp.com", "karmic-gochara-cloud.web.app", "localhost", "capacitorio-plugins-capacitor-google-auth.appspot.com"]}' \
>   "https://identitytoolkit.googleapis.com/v2/projects/karmic-gochara-cloud/config?updateMask=authorizedDomains"
> ```

### Google Cloud API Key — Restrictions HTTP (Browser key)

```
capacitor://localhost
http://localhost
https://karmicgochara.app/*
https://karmic-gochara-cloud.firebaseapp.com/*
```

> Ces restrictions empêchent l'usage non-autorisé de la clé API.
> Modifier via Google Cloud Console → API & Services → Credentials.

### Google Cloud API Key — Services autorisés

```
identitytoolkit.googleapis.com    (Firebase Auth)
securetoken.googleapis.com       (Firebase Token Service)
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│            Pixel 10 (Android)                   │
│  ┌──────────────────────────────────────────┐   │
│  │  Capacitor WebView                       │   │
│  │  https://karmicgochara.app (via Astro)   │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                       │
                       │ Firebase JS SDK (signInWithRedirect)
                       ▼
 ┌─────────────────────────────────────────────────┐
 │  Firebase Auth                                  │
 │  karmic-gochara-cloud.firebaseapp.com           │
 │  → redirect vers accounts.google.com            │
 │  → Google OAuth consent (displayName:           │
 │    "Karmic GoChara")                            │
 └─────────────────────────────────────────────────┘
                       │
                       │ create profile in
                       ▼
 ┌─────────────────────────────────────────────────┐
 │  Firestore (europe-west1)                       │
 │  Collection: users/{uid}                        │
 │  {                                              │
 │    uid: "abc123",                               │
 │    displayName: "Jérôme Malige",                │
 │    email: "jerome@jeromemalige.fr",             │
 │    photoURL: "https://lh3.googleusercontent...",│
 │    createdAt: <serverTimestamp>,                │
 │    updatedAt: <serverTimestamp>,                │
 │    plan: "free",                                │
 │    pseudo: "jero87"  (optionnel, futur)         │
 │    birthDate: "1987-...",                       │
 │    birthPlace: "Paris, FR"                      │
 │  }                                              │
 └─────────────────────────────────────────────────┘
 ```

---

## Fichiers du projet

| Fichier | Rôle |
|---|---|
| `astro/src/lib/firebase.ts` | Initialisation Firebase (modular SDK) |
| `astro/src/lib/firebase-auth.ts` | `signInWithGoogle()`, `handleRedirectResult()`, `ensureUserProfile()` |
| `astro/src/components/LoginCard.astro` | UI : bouton Google + lien register |
| `android/app/google-services.json` | Config Android (SHA-1 vérifié) |
| `android/app/build.gradle` | Deps : firebase-bom, firebase-auth, firebase-firestore, googleid, credentials |

---

## Règles Firestore

Règles déployées via `firestore.rules` :

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own profile
    match /users/{uid} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

---

## Checklist nouveau dev

Pour ajouter un nouveau développeur ou tester sur un autre device :

1. **Récupérer SHA-1** du keystore de dev :
   ```bash
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android
   ```
2. **Ajouter le SHA-1** dans Firebase Console → Settings → Fingerprints
3. **Se connecter** avec Google → le profil est créé automatiquement

---

## Troubleshooting courant

| Erreur | Cause probable | Fix |
|---|---|---|
| "The requested action is invalid" | `localhost` ou `capacitorio-plugins-*.appspot.com` manque dans `authorizedDomains` | Ajouter via `gcloud` API (voir ci-dessus) |
| "API key not valid" | Clé API Android utilisée au lieu de la clé Web (ou inversement) | Vérifier `firebase.ts` et `google-services.json` ont la même clé |
| "signInWithRedirect not supported" | Domaine `capacitor://localhost` non autorisé sur la clé API Web | Ajouter dans Google Cloud Console → API Key restrictions |
| Popup bloqué en WebView | `signInWithPopup()` ne marche pas dans Capacitor | Utiliser `signInWithRedirect()` (déjà le cas dans `firebase-auth.ts`) |