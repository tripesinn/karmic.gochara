// src/lib/firebase-auth.ts — Firebase Auth (Google Sign-In + Firestore profile)
import {
  GoogleAuthProvider,
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
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

const googleProvider = new GoogleAuthProvider();

// ── Google Sign-In ─────────────────────────────────

/**
 * Sign in with Google. Uses popup on desktop,
 * redirect on Capacitor native (WebView popup issues).
 */
export async function signInWithGoogle(): Promise<User> {
  const isNative = !!(window as any).Capacitor?.isNative;

  if (isNative) {
    // Redirect flow for Capacitor WebView
    await signInWithRedirect(auth, googleProvider);
    // After redirect, getRedirectResult picks up the result
    const result = await getRedirectResult(auth);
    if (!result) throw new Error('Connexion Google annulée');
    await ensureUserProfile(result.user);
    return result.user;
  } else {
    // Popup flow for web
    const result = await signInWithPopup(auth, googleProvider);
    await ensureUserProfile(result.user);
    return result.user;
  }
}

/**
 * Check for redirect result on page load
 * (needed for Capacitor redirect flow).
 */
export async function handleRedirectResult(): Promise<User | null> {
  try {
    const result = await getRedirectResult(auth);
    if (result?.user) {
      await ensureUserProfile(result.user);
      return result.user;
    }
  } catch (err) {
    console.error('Redirect result error:', err);
  }
  return null;
}

// ── Sign Out ───────────────────────────────────────

export async function signOutUser(): Promise<void> {
  await firebaseSignOut(auth);
}

// ── Auth State ─────────────────────────────────────

/**
 * Subscribe to auth state changes.
 * Returns an unsubscribe function.
 */
export function onAuthChange(
  callback: (user: User | null) => void
): () => void {
  return onAuthStateChanged(auth, callback);
}

/**
 * Get the current user (may be null if not yet resolved).
 */
export function getCurrentUser(): User | null {
  return auth.currentUser;
}

// ── Firestore User Profile ─────────────────────────

/**
 * Create a Firestore profile for the user if it
 * doesn't exist yet. Update displayName/photoURL
 * if changed.
 */
async function ensureUserProfile(user: User): Promise<void> {
  const userRef = doc(db, 'users', user.uid);
  const snap = await getDoc(userRef);

  if (!snap.exists()) {
    // First sign-in: create profile
    await setDoc(userRef, {
      uid: user.uid,
      displayName: user.displayName || 'Utilisateur',
      email: user.email || '',
      photoURL: user.photoURL || '',
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
    });
  } else {
    // Returning user: sync display info
    const data = snap.data();
    const updates: Record<string, any> = {
      updatedAt: serverTimestamp(),
    };
    if (user.displayName && user.displayName !== data.displayName) {
      updates.displayName = user.displayName;
    }
    if (user.photoURL && user.photoURL !== data.photoURL) {
      updates.photoURL = user.photoURL;
    }
    if (Object.keys(updates).length > 1) {
      await updateDoc(userRef, updates);
    }
  }
}
