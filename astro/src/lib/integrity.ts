// src/lib/integrity.ts — Génère un Play Integrity token (natif) à poster au login.
import { Capacitor } from '@capacitor/core';

interface IntegrityResult {
  token: string;
}

/**
 * Demande un StandardIntegrityToken au plugin natif PlayIntegrity.
 * Sur web (non natif) ou si le provider n'est pas prêt, renvoie '' (backend ignore si flag off).
 */
export async function getIntegrityToken(): Promise<string> {
  if (!Capacitor.isNativePlatform()) return '';
  try {
    const plugin = (window as any).Capacitor?.Plugins?.PlayIntegrity;
    if (!plugin) {
      console.warn('[integrity] plugin PlayIntegrity introuvable');
      return '';
    }
    const result = await plugin.getIntegrityToken() as IntegrityResult;
    return result?.token || '';
  } catch (e) {
    console.warn('[integrity] échec getIntegrityToken:', e);
    return '';
  }
}
