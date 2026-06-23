package com.karmicgochara.app;

import android.app.Activity;
import android.os.CancellationSignal;
import android.util.Log;

import androidx.credentials.ClearCredentialStateRequest;
import androidx.credentials.Credential;
import androidx.credentials.CredentialManager;
import androidx.credentials.CredentialManagerCallback;
import androidx.credentials.GetCredentialRequest;
import androidx.credentials.GetCredentialResponse;
import androidx.credentials.exceptions.GetCredentialException;
import androidx.credentials.exceptions.ClearCredentialException;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.google.android.libraries.identity.googleid.GetGoogleIdOption;
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential;

import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

@CapacitorPlugin(name = "KarmicGoogleAuth")
public class KarmicGoogleAuthPlugin extends Plugin {

    private static final String TAG = "KarmicGoogleAuth";
    private final Executor executor = Executors.newSingleThreadExecutor();

    private String getWebClientId() {
        String id = getConfig().getString("serverClientId", null);
        if (id == null || id.isEmpty() || id.equals("Your Web Client Key")) {
            try {
                id = this.getContext().getString(
                    this.getContext().getResources().getIdentifier(
                        "server_client_id", "string", this.getContext().getPackageName()
                    )
                );
            } catch (Exception e) {
                Log.e(TAG, "Failed to read server_client_id resource", e);
            }
        }
        return id;
    }

    @PluginMethod()
    public void initialize(PluginCall call) {
        JSObject ret = new JSObject();
        ret.put("webClientId", getWebClientId());
        call.resolve(ret);
    }

    @PluginMethod()
    public void signIn(PluginCall call) {
        Activity activity = getActivity();
        if (activity == null) {
            call.reject("Activity is not available");
            return;
        }

        String webClientId = getWebClientId();
        if (webClientId == null || webClientId.isEmpty() || webClientId.equals("Your Web Client Key")) {
            call.reject("Web Client ID not configured. Add serverClientId to capacitor.config.json");
            return;
        }

        CredentialManager credentialManager = CredentialManager.create(activity);
        // Phase 1: try already-authorized accounts (faster, skips Activity Controls check)
        trySignInPhase(activity, credentialManager, webClientId, true, call);
    }

    private void trySignInPhase(
        Activity activity,
        CredentialManager credentialManager,
        String webClientId,
        boolean filterByAuthorized,
        PluginCall call
    ) {
        GetGoogleIdOption googleIdOption = new GetGoogleIdOption.Builder()
            .setFilterByAuthorizedAccounts(filterByAuthorized)
            .setServerClientId(webClientId)
            .setAutoSelectEnabled(false)
            .build();

        GetCredentialRequest request = new GetCredentialRequest.Builder()
            .addCredentialOption(googleIdOption)
            .build();

        activity.runOnUiThread(() ->
            credentialManager.getCredentialAsync(
                activity,
                request,
                new CancellationSignal(),
                executor,
                new CredentialManagerCallback<>() {
                    @Override
                    public void onResult(GetCredentialResponse result) {
                        handleCredential(result.getCredential(), call);
                    }

                    @Override
                    public void onError(GetCredentialException e) {
                        if (filterByAuthorized) {
                            // Phase 1 failed (no cached account) → phase 2: all accounts
                            Log.i(TAG, "Phase 1 (authorized) failed, retrying with all accounts: "
                                + e.getMessage());
                            trySignInPhase(activity, credentialManager,
                                webClientId, false, call);
                        } else {
                            Log.e(TAG, "Credential Manager error (phase 2): " + e.getMessage());
                            call.reject("Sign-in failed: " + e.getMessage());
                        }
                    }
                }
            )
        );
    }

    private void handleCredential(Credential credential, PluginCall call) {
        // Try direct instance
        if (credential instanceof GoogleIdTokenCredential) {
            resolveGoogleIdToken((GoogleIdTokenCredential) credential, call);
            return;
        }

        // Try parsing from CustomCredential data (Android 14+ wraps it)
        try {
            GoogleIdTokenCredential googleCred = GoogleIdTokenCredential.createFrom(credential.getData());
            resolveGoogleIdToken(googleCred, call);
        } catch (Exception e) {
            Log.e(TAG, "Failed to parse credential: " + e.getMessage(), e);
            call.reject("Unsupported credential type: " + credential.getType());
        }
    }

    private void resolveGoogleIdToken(GoogleIdTokenCredential googleCred, PluginCall call) {
        try {
            String idToken = googleCred.getIdToken();
            JSObject ret = new JSObject();
            ret.put("idToken", idToken);
            JSObject profile = new JSObject();
            profile.put("id", googleCred.getId());
            profile.put("displayName", googleCred.getDisplayName() != null ? googleCred.getDisplayName() : "");
            profile.put("familyName", googleCred.getFamilyName() != null ? googleCred.getFamilyName() : "");
            profile.put("givenName", googleCred.getGivenName() != null ? googleCred.getGivenName() : "");
            profile.put("email", "");
            ret.put("profile", profile);
            call.resolve(ret);
        } catch (Exception e) {
            call.reject("Failed to extract Google ID token: " + e.getMessage());
        }
    }

    @PluginMethod()
    public void signOut(PluginCall call) {
        try {
            CredentialManager cm = CredentialManager.create(getContext());
            cm.clearCredentialStateAsync(
                new ClearCredentialStateRequest(),
                new CancellationSignal(),
                executor,
                new CredentialManagerCallback<>() {
                    @Override
                    public void onResult(Void v) {
                        call.resolve();
                    }
                    @Override
                    public void onError(ClearCredentialException e) {
                        call.resolve();
                    }
                });
        } catch (Exception e) {
            call.resolve();
        }
    }
}
