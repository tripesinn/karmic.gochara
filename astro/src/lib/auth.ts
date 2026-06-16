// src/lib/auth.ts — Helper auth : login, logout, isAuthenticated
// Utilise les sessions Flask (cookies) — pas de JWT localStorage
import { api } from './api';

export async function login(pseudo: string): Promise<{ ok: boolean; pseudo?: string; profile?: any; error?: string }> {
  const resp = await api.login(pseudo);
  if (!resp.ok) throw new Error(resp.error || 'Identifiants invalides');
  return resp;
}

export async function register(data: {
  pseudo: string;
  email: string;
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  city: string;
  lat: number;
  lon: number;
  tz: string;
}): Promise<{ ok: boolean; pseudo?: string; profile?: any; error?: string }> {
  const resp = await api.register(data);
  if (!resp.ok) throw new Error(resp.error || "Erreur lors de la création du profil");
  return resp;
}

export async function logout(): Promise<void> {
  await api.logout();
  window.location.href = '/';
}

export async function isAuthenticated(): Promise<boolean> {
  try {
    const user = await api.profile();
    return !!user;
  } catch {
    return false;
  }
}
