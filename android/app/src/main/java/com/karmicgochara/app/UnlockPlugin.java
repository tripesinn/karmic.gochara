package com.karmicgochara.app;

import android.content.SharedPreferences;

import androidx.annotation.NonNull;

import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.PurchasesUpdatedListener;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.Collections;
import java.util.List;

/**
 * UnlockPlugin — Achat "Supprimer les pubs" via Google Play Billing
 *
 * Produit Play Console à créer :
 *   Type    : Achat unique (one-time)
 *   ID      : remove_ads
 *   Prix    : €2,99
 *
 * Une fois acheté, le flag est stocké localement + vérifié via Play Billing.
 */
@CapacitorPlugin(name = "Unlock")
public class UnlockPlugin extends Plugin implements PurchasesUpdatedListener {

    private static final String PRODUCT_ID   = "remove_ads";
    private static final String PREFS_NAME   = "karmic_unlock";
    private static final String PREFS_KEY    = "is_unlocked";

    private BillingClient billingClient;
    private PluginCall    pendingCall = null;


    @Override
    public void load() {
        billingClient = BillingClient.newBuilder(getContext())
                .setListener(this)
                .enablePendingPurchases()
                .build();
    }


    // ── isUnlocked : vérifie le statut (local d'abord, puis Play) ────────────
    @PluginMethod
    public void isUnlocked(PluginCall call) {
        boolean local = getPrefs().getBoolean(PREFS_KEY, false);
        if (local) {
            call.resolve(unlockResult(true));
            return;
        }
        // Vérifie aussi côté Play Billing (au cas où réinstall)
        connectAndCheck(call);
    }


    // ── purchase : lance le flux d'achat Play Billing ────────────────────────
    @PluginMethod
    public void purchase(PluginCall call) {
        pendingCall = call;
        connectThenPurchase();
    }


    // ── restore : restaure un achat existant (réinstallation) ────────────────
    @PluginMethod
    public void restore(PluginCall call) {
        pendingCall = call;
        connectAndCheck(call);
    }


    // ── Connexion + vérification des achats existants ─────────────────────────
    private void connectAndCheck(PluginCall call) {
        billingClient.startConnection(new BillingClientStateListener() {
            @Override
            public void onBillingSetupFinished(@NonNull BillingResult result) {
                if (result.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                    call.resolve(unlockResult(false));
                    return;
                }
                billingClient.queryPurchasesAsync(
                    QueryPurchasesParams.newBuilder()
                        .setProductType(BillingClient.ProductType.INAPP)
                        .build(),
                    (br, purchases) -> {
                        boolean found = false;
                        for (Purchase p : purchases) {
                            if (p.getProducts().contains(PRODUCT_ID)
                                    && p.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
                                found = true;
                                acknowledgePurchase(p);
                                break;
                            }
                        }
                        if (found) setUnlocked(true);
                        call.resolve(unlockResult(found || getPrefs().getBoolean(PREFS_KEY, false)));
                    }
                );
            }
            @Override
            public void onBillingServiceDisconnected() {
                call.resolve(unlockResult(getPrefs().getBoolean(PREFS_KEY, false)));
            }
        });
    }


    // ── Connexion + lancement du flux d'achat ────────────────────────────────
    private void connectThenPurchase() {
        billingClient.startConnection(new BillingClientStateListener() {
            @Override
            public void onBillingSetupFinished(@NonNull BillingResult result) {
                if (result.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                    if (pendingCall != null) pendingCall.reject("BILLING_UNAVAILABLE");
                    return;
                }
                QueryProductDetailsParams params = QueryProductDetailsParams.newBuilder()
                    .setProductList(Collections.singletonList(
                        QueryProductDetailsParams.Product.newBuilder()
                            .setProductId(PRODUCT_ID)
                            .setProductType(BillingClient.ProductType.INAPP)
                            .build()
                    )).build();

                billingClient.queryProductDetailsAsync(params, (br, productDetailsList) -> {
                    if (productDetailsList == null || productDetailsList.isEmpty()) {
                        if (pendingCall != null) pendingCall.reject("PRODUCT_NOT_FOUND");
                        return;
                    }
                    ProductDetails product = productDetailsList.get(0);
                    BillingFlowParams flowParams = BillingFlowParams.newBuilder()
                        .setProductDetailsParamsList(Collections.singletonList(
                            BillingFlowParams.ProductDetailsParams.newBuilder()
                                .setProductDetails(product)
                                .build()
                        )).build();
                    getActivity().runOnUiThread(() ->
                        billingClient.launchBillingFlow(getActivity(), flowParams)
                    );
                });
            }
            @Override
            public void onBillingServiceDisconnected() {
                if (pendingCall != null) pendingCall.reject("BILLING_DISCONNECTED");
            }
        });
    }


    // ── Callback achat ────────────────────────────────────────────────────────
    @Override
    public void onPurchasesUpdated(@NonNull BillingResult result, List<Purchase> purchases) {
        if (result.getResponseCode() == BillingClient.BillingResponseCode.OK && purchases != null) {
            for (Purchase purchase : purchases) {
                if (purchase.getProducts().contains(PRODUCT_ID)
                        && purchase.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
                    acknowledgePurchase(purchase);
                    setUnlocked(true);
                    if (pendingCall != null) {
                        pendingCall.resolve(unlockResult(true));
                        pendingCall = null;
                    }
                }
            }
        } else if (result.getResponseCode() == BillingClient.BillingResponseCode.USER_CANCELED) {
            if (pendingCall != null) { pendingCall.reject("USER_CANCELED"); pendingCall = null; }
        } else {
            if (pendingCall != null) { pendingCall.reject("PURCHASE_FAILED"); pendingCall = null; }
        }
    }


    // ── Helpers ───────────────────────────────────────────────────────────────
    private void acknowledgePurchase(Purchase purchase) {
        if (purchase.isAcknowledged()) return;
        AcknowledgePurchaseParams params = AcknowledgePurchaseParams.newBuilder()
                .setPurchaseToken(purchase.getPurchaseToken()).build();
        billingClient.acknowledgePurchase(params, br -> {});
    }

    private void setUnlocked(boolean value) {
        getPrefs().edit().putBoolean(PREFS_KEY, value).apply();
    }

    private SharedPreferences getPrefs() {
        return getContext().getSharedPreferences(PREFS_NAME, android.content.Context.MODE_PRIVATE);
    }

    private JSObject unlockResult(boolean unlocked) {
        JSObject r = new JSObject();
        r.put("unlocked", unlocked);
        return r;
    }
}
