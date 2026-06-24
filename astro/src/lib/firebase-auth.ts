// src/lib/firebase-auth.ts — Firebase Auth (Google Sign-In + Firestore profile)
import {
  GoogleAuthProvider,
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  signInWithCredential,
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
import { GoogleAuth } from '@codetrix-studio/capacitor-google-auth';

const googleProvider = new GoogleAuthProvider();

// Initialize GoogleAuth for native environments
if (typeof window !== 'undefined' && !!(window as any).Capacitor?.isNative) {
  GoogleAuth.initialize({
    clientId: '732214018947-ee5v5hi70fer05edbti3hjig22knngb8.apps.googleusercontent.com',
    scopes: ['profile', 'email'],
    grantOfflineAccess: true,
  });
}

// ── Google Sign-In ─────────────────────────────────

/**
 * Sign in with Google. Uses popup on desktop,
 * Capacitor GoogleAuth plugin on native.
 */
export async function signInWithGoogle(): Promise<User> {
  const isNative = !!(window as any).Capacitor?.isNative;

  if (isNative) {
    try {
      const googleUser = await GoogleAuth.signIn();
      const idToken = googleUser.authentication.idToken;
      const credential = GoogleAuthProvider.credential(idToken);
      const result = await signInWithCredential(auth, credential);
      await ensureUserProfile(result.user);
      return result.user;
    } catch (error) {
      console.error('Erreur Google Auth natif:', error);
      throw new Error('Connexion Google native annulée ou échouée.');
    }
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
  const isNative = !!(window as any).Capacitor?.isNative;
  if (isNative) {
    // Native now uses direct async/await via GoogleAuth plugin, no redirect needed
    return null;
  }

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
  const isNative = !!(window as any).Capacitor?.isNative;
  if (isNative) {
    try {
      await GoogleAuth.signOut();
    } catch (e) {
      console.error(e);
    }
  }
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
