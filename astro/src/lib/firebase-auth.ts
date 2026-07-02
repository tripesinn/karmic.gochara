// src/lib/firebase-auth.ts — Auth ONLY (Firestore handled by Flask)
import { registerPlugin, Capacitor } from '@capacitor/core';
import {
  GoogleAuthProvider,
  signInWithCredential,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  type User,
} from '@firebase/auth';
import { auth } from './firebase';

interface KarmicGoogleAuthPlugin {
  initialize(): Promise<{ webClientId: string }>;
  signIn(): Promise<{ idToken: string; profile?: Record<string, string>; serverAuthCode?: string }>;
  signOut(): Promise<void>;
}

const KarmicGoogleAuth = registerPlugin<KarmicGoogleAuthPlugin>('KarmicGoogleAuth');

if (Capacitor.isNativePlatform()) {
  KarmicGoogleAuth.initialize().catch(e => console.warn('KarmicGoogleAuth.init skipped:', e));
}

export async function signInWithGoogle(): Promise<User> {
  if (Capacitor.isNativePlatform()) {
    const result = await KarmicGoogleAuth.signIn();
    if (!result.idToken) throw new Error('Google Sign-In annulé.');
    const credential = GoogleAuthProvider.credential(result.idToken);
    const userCredential = await signInWithCredential(auth, credential);
    return userCredential.user;
  } else {
    const provider = new GoogleAuthProvider();
    const userCredential = await signInWithPopup(auth, provider);
    return userCredential.user;
  }
}

/**
 * 🧪 TEST ONLY — Connexion avec un user fictif dans l'émulateur Firebase Auth.
 * Crée le compte s'il n'existe pas, le réutilise sinon.
 * Utiliser un email unique (ex: avec timestamp) pour simuler un NOUVEL utilisateur.
 *
 * Prérequis :
 *   1. firebase emulators:start --only auth (sur le Mac)
 *   2. adb reverse tcp:9099 tcp:9099 (pour que le Pixel accède au Mac)
 *   3. PUBLIC_FIREBASE_EMULATOR=true dans l'env de build
 */
export async function signInTestUser(email?: string): Promise<User> {
  const testEmail = email ?? `test-${Date.now()}@karmic.dev`;
  const testPassword = 'KarmicTest2026!';

  try {
    // Essai : créer un nouveau compte (= nouvel utilisateur)
    const cred = await createUserWithEmailAndPassword(auth, testEmail, testPassword);
    console.info('🧪 [TEST] Nouvel utilisateur créé :', testEmail);
    return cred.user;
  } catch (err: any) {
    if (err.code === 'auth/email-already-in-use') {
      // Le compte existe → connexion normale (= utilisateur existant)
      const cred = await signInWithEmailAndPassword(auth, testEmail, testPassword);
      console.info('🧪 [TEST] Utilisateur existant récupéré :', testEmail);
      return cred.user;
    }
    throw err;
  }
}

export async function signOutUser(): Promise<void> {
  if (Capacitor.isNativePlatform()) {
    try { await KarmicGoogleAuth.signOut(); } catch (e) {}
  }
  await firebaseSignOut(auth);
}

export function onAuthChange(callback: (user: User | null) => void): () => void {
  return onAuthStateChanged(auth, callback);
}

