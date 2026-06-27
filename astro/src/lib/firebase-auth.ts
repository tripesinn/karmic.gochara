// src/lib/firebase-auth.ts — Auth ONLY (Firestore handled by Flask)
import { registerPlugin, Capacitor } from '@capacitor/core';
import {
  GoogleAuthProvider,
  signInWithCredential,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  signInWithPopup,
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

export async function signOutUser(): Promise<void> {
  if (Capacitor.isNativePlatform()) {
    try { await KarmicGoogleAuth.signOut(); } catch (e) {}
  }
  await firebaseSignOut(auth);
}

export function onAuthChange(callback: (user: User | null) => void): () => void {
  return onAuthStateChanged(auth, callback);
}
