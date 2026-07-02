// src/lib/firebase.ts — Firebase Auth only (Firestore via REST, no WebChannel)
// IMPORTANT: On importe les modules SÉPARÉMENT, pas le bundle monolithique 'firebase'
// Cela empêche le SDK Firestore Web de s'auto-enregistrer et de lancer le Listen stream
import { initializeApp } from '@firebase/app';
import { getAuth, connectAuthEmulator } from '@firebase/auth';

// PATCH: Force REST API and disable WebChannel for Firestore
// (Même si on utilise firestore-rest.ts, cette sécurité évite tout auto-load)
if (typeof window !== 'undefined') {
  (window as any).goog = (window as any).goog || {};
  (window as any).goog.net = (window as any).goog.net || {};
  (window as any).goog.net.WebChannel = null;
}


const firebaseConfig = {
  apiKey: 'AIzaSyCbJo81VBW9r2HaR6b5xwta3nFYV4txQns',
  authDomain: 'karmic-gochara-cloud.firebaseapp.com',
  projectId: 'karmic-gochara-cloud',
  storageBucket: 'karmic-gochara-cloud.firebasestorage.app',
  messagingSenderId: '732214018947',
  appId: '1:732214018947:android:64629c73dbe5c05661ecb6',
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// Mode émulateur — activé uniquement si PUBLIC_FIREBASE_EMULATOR=true
// Sur Android Pixel (USB), l'émulateur Mac est accessible via ADB reverse :
//   adb reverse tcp:9099 tcp:9099
const isEmulator = (import.meta as any).env?.PUBLIC_FIREBASE_EMULATOR === 'true';
if (isEmulator && typeof window !== 'undefined') {
  // disableWarnings=true supprime le bandeau jaune dans l'UI
  connectAuthEmulator(auth, 'http://127.0.0.1:9099', { disableWarnings: true });
  console.info('🧪 [Firebase] Auth connecté à l\'émulateur 127.0.0.1:9099');
}

// Firestore n'est PLUS initialisé via le SDK Web
// Toutes les lectures/écritures passent par firestore-rest.ts (API REST)
// Cela élimine les erreurs WebChannelConnection sur Android

export default app;

