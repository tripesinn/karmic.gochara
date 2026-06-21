// src/lib/firebase-auth.ts — Google Sign-In via custom KarmicGoogleAuth (Credential Manager) + Firebase Auth
import { registerPlugin } from '@capacitor/core';
import {
  GoogleAuthProvider,
  signInWithCredential,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  type User,
} from 'firebase/auth';
import {
  doc,
  getDoc,
  setDoc,
  updateDoc,
  serverTimestamp,
} from 'firebase/firestore';
import { auth, db } from './firebase';

// ── Custom Capacitor plugin (Credential Manager) ──

interface KarmicGoogleAuthPlugin {
  initialize(): Promise<{ webClientId: string }>;
  signIn(): Promise<{ idToken: string; profile?: Record<string, string>; serverAuthCode?: string }>;
  signOut(): Promise<void>;
}

const KarmicGoogleAuth = registerPlugin<KarmicGoogleAuthPlugin>('KarmicGoogleAuth');

// ── Init ──────────────────────────────────────────

KarmicGoogleAuth.initialize().catch(e => console.warn('KarmicGoogleAuth.init skipped:', e));

// ── Google Sign-In (native Credential Manager) ────

export async function signInWithGoogle(): Promise<User> {
  const result = await KarmicGoogleAuth.signIn();
  if (!result.idToken) {
    throw new Error('Google Sign-In annulé ou idToken manquant.');
  }

  // Exchange the native Google idToken for a Firebase credential
  const credential = GoogleAuthProvider.credential(result.idToken);
  const userCredential = await signInWithCredential(auth, credential);
  await ensureUserProfile(userCredential.user);
  return userCredential.user;
}

/**
 * No-op: redirect flow not needed with native plugin.
 */
export async function handleRedirectResult(): Promise<User | null> {
  return null;
}

// ── Sign Out ───────────────────────────────────────

export async function signOutUser(): Promise<void> {
  try { await KarmicGoogleAuth.signOut(); } catch (e) { /* native only */ }
  await firebaseSignOut(auth);
}

// ── Auth State ─────────────────────────────────────

export function onAuthChange(
  callback: (user: User | null) => void
): () => void {
  return onAuthStateChanged(auth, callback);
}

export function getCurrentUser(): User | null {
  return auth.currentUser;
}

// ── Firestore User Profile ─────────────────────────

async function ensureUserProfile(user: User): Promise<void> {
  const userRef = doc(db, 'users', user.uid);
  const snap = await getDoc(userRef);

  if (!snap.exists()) {
    await setDoc(userRef, {
      uid: user.uid,
      displayName: user.displayName || 'Utilisateur',
      email: user.email || '',
      photoURL: user.photoURL || '',
      plan: 'free',
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
  } else {
    const data = snap.data();
    const updates: Record<string, any> = { updatedAt: serverTimestamp() };
    if (user.displayName && user.displayName !== data.displayName) updates.displayName = user.displayName;
    if (user.photoURL && user.photoURL !== data.photoURL) updates.photoURL = user.photoURL;
    if (Object.keys(updates).length > 1) await updateDoc(userRef, updates);
  }
}
