import { Capacitor } from '@capacitor/core';
import { Purchases, LOG_LEVEL } from '@revenuecat/purchases-capacitor';

export async function initRevenueCat(pseudo: string) {
  if (!Capacitor.isNativePlatform()) return;

  try {
    await Purchases.setLogLevel({ level: LOG_LEVEL.DEBUG });

    const apiKey = (import.meta as any).env.PUBLIC_REVENUECAT_ANDROID_KEY;
    if (!apiKey) {
      console.warn("⚠️ Clé RevenueCat manquante (PUBLIC_REVENUECAT_ANDROID_KEY)");
      return;
    }

    if (Capacitor.getPlatform() === 'android') {
      await Purchases.configure({ apiKey: apiKey, appUserID: pseudo });
    }
    
    console.log("✅ [RevenueCat] Initialisé avec pseudo:", pseudo);
  } catch (e) {
    console.error("❌ [RevenueCat] Erreur d'initialisation:", e);
  }
}

export async function purchaseProPlan() {
  if (!Capacitor.isNativePlatform()) return null;

  try {
    const result = await Purchases.purchaseProduct({ productIdentifier: 'pro_lifetime_access' });
    console.log("✅ [RevenueCat] Achat réussi:", result);
    return result;
  } catch (error: any) {
    if (!error.userCancelled) {
      console.error("❌ [RevenueCat] Erreur d'achat:", error);
      throw error;
    }
    return null;
  }
}
