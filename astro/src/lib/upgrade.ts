import { Capacitor } from '@capacitor/core';
import { api } from './api';
import { purchaseProPlan } from './revenuecat';

export async function triggerUpgrade(productType: string = 'pro') {
  if (Capacitor.isNativePlatform()) {
    const result = await purchaseProPlan();
    if (result) {
      window.location.reload();
    }
    return;
  }
  
  // Web fallback to Stripe
  const checkout = await api.stripeCheckout(productType);
  if (checkout.ok && checkout.checkout_url) {
    window.location.href = checkout.checkout_url;
  } else {
    throw new Error(checkout.beta ? "Bêta — la facturation n'est pas encore active." : "Erreur Stripe");
  }
}
