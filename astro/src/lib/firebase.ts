// src/lib/firebase.ts — Firebase Auth only (Firestore via REST, no WebChannel)
// IMPORTANT: On importe les modules SÉPARÉMENT, pas le bundle monolithique 'firebase'
// Cela empêche le SDK Firestore Web de s'auto-enregistrer et de lancer le Listen stream
import { initializeApp } from '@firebase/app';
import { getAuth } from '@firebase/auth';

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

// Firestore n'est PLUS initialisé via le SDK Web
// Toutes les lectures/écritures passent par firestore-rest.ts (API REST)
// Cela élimine les erreurs WebChannelConnection sur Android

export default app;
