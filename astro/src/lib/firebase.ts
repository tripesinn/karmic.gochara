// src/lib/firebase.ts — Firebase initialization (modular SDK)
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: 'AIzaSyAr2JW-mbg8ZQJof7U76Xe2m9DibrVBB6M',
  authDomain: 'karmic-gochara-cloud.firebaseapp.com',
  projectId: 'karmic-gochara-cloud',
  storageBucket: 'karmic-gochara-cloud.firebasestorage.app',
  messagingSenderId: '732214018947',
  appId: '1:732214018947:web:c115b66fbaa637e961ecb6',
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export default app;
