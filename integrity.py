"""
integrity.py — Vérification Play Integrity (server-side) pour gochara-api

Flux :
  L'app Android génère un integrity_token (StandardIntegrityManager) et le poste
  au login. Ce token est opaque : le backend l'envoie à l'API Google
  decodeIntegrityToken pour obtenir le verdict (appIntegrity / deviceIntegrity / ...).

Identité : compte de service dédié `play-integrity-decoder` (rôle Play Integrity API Admin).
Clé JSON fournie via env PLAY_INTEGRITY_SERVICE_ACCOUNT_JSON (ou chemin fichier
PLAY_INTEGRITY_SERVICE_ACCOUNT_FILE).

Désactivable à chaud via PLAY_INTEGRITY_ENABLED (défaut "false") — le closed test
tourne sans, la prod active.

Design : fail-closed quand activé (token manquant ou verdict invalide -> rejet),
car c'est un contrôle de sécu. Aucun impact si flag off.
"""

import json
import os
import time
from typing import Optional

import requests
from google.oauth2 import service_account

# ── Config ───────────────────────────────────────────────────────────────────
_PLAY_INTEGRITY_SCOPE = "https://www.googleapis.com/auth/playintegrity"
_DECODE_URL = "https://playintegrity.googleapis.com/v1/{package_name}:decodeIntegrityToken"

# Cache du token OAuth (1h d'usage, refresh à 50 min)
_TOKEN_CACHE = {"token": None, "exp": 0}

# SHA256 du certificat d'upload (karmic-key / alias key0) — renseigner en prod pour
# durcir la vérif appIntegrity. Vide = on se contente de packageName + deviceIntegrity.
_EXPECTED_UPLOAD_CERT_SHA256 = os.environ.get("PLAY_INTEGRITY_UPLOAD_CERT_SHA256", "").strip()


def is_enabled() -> bool:
    return os.environ.get("PLAY_INTEGRITY_ENABLED", "false").lower() in ("1", "true", "yes", "on")


def _load_credentials():
    raw = os.environ.get("PLAY_INTEGRITY_SERVICE_ACCOUNT_JSON", "").strip()
    path = os.environ.get("PLAY_INTEGRITY_SERVICE_ACCOUNT_FILE", "").strip()
    if not raw and path:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    if not raw:
        return None
    info = json.loads(raw)
    return service_account.Credentials.from_service_account_info(
        info, scopes=[_PLAY_INTEGRITY_SCOPE]
    )


def _get_access_token() -> Optional[str]:
    creds = _load_credentials()
    if creds is None:
        return None
    now = time.time()
    if _TOKEN_CACHE["token"] and _TOKEN_CACHE["exp"] > now + 60:
        return _TOKEN_CACHE["token"]
    if not creds.valid or creds.expired:
        import google.auth.transport.requests as gtransport
        creds.refresh(gtransport.Request())
    _TOKEN_CACHE["token"] = creds.token
    _TOKEN_CACHE["exp"] = now + 3000  # ~50 min
    return creds.token


def verify_integrity_token(integrity_token: str, package_name: str = "com.karmicgochara.app") -> dict:  # noqa: E501
    """
    Décode et vérifie un integrity_token.

    Retourne un dict :
      {"ok": bool, "reason": str, "verdict": <payload brut ou None>}
    """
    if not integrity_token:
        return {"ok": False, "reason": "integrity_token manquant", "verdict": None}

    try:
        access_token = _get_access_token()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "reason": f"échec auth service account: {exc}", "verdict": None}
    if not access_token:
        return {"ok": False, "reason": "compte de service Play Integrity non configuré", "verdict": None}

    url = _DECODE_URL.format(package_name=package_name)
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {access_token}",
                     "Content-Type": "application/json"},
            json={"integrityToken": integrity_token},
            timeout=8,
        )
    except requests.RequestException as exc:
        return {"ok": False, "reason": f"erreur réseau decodeIntegrityToken: {exc}", "verdict": None}

    if resp.status_code != 200:
        return {"ok": False,
                "reason": f"decodeIntegrityToken {resp.status_code}: {resp.text[:300]}",
                "verdict": None}

    payload = resp.json().get("tokenPayloadExternal", {})

    # ── appIntegrity : package + certificat ──
    app = payload.get("appIntegrity", {})
    pkg = app.get("packageName", "")
    if pkg != package_name:
        return {"ok": False,
                "reason": f"packageName mismatch ({pkg} != {package_name})",
                "verdict": payload}

    if _EXPECTED_UPLOAD_CERT_SHA256:
        cert = app.get("certificateSha256Digest", "")
        if cert and cert.lower() != _EXPECTED_UPLOAD_CERT_SHA256.lower():
            return {"ok": False,
                    "reason": "certificat d'upload ne matche pas (app non officielle ?)",
                    "verdict": payload}

    # ── deviceIntegrity : au moins un verdict connu ──
    dev = payload.get("deviceIntegrity", {})
    verdicts = dev.get("deviceRecognitionVerdict", [])
    if not verdicts:
        return {"ok": False,
                "reason": "deviceIntegrity vide (appareil non reconnu)",
                "verdict": payload}

    return {"ok": True, "reason": "ok", "verdict": payload}


def check_login_integrity(integrity_token: Optional[str], package_name: str = "com.karmicgochara.app") -> dict:  # noqa: E501
    """
    Point d'entrée pour login_firebase. Flag-protected.
    Si désactivé -> always ok (closed test). Si activé -> vérifie.
    """
    if not is_enabled():
        return {"ok": True, "reason": "désactivé", "verdict": None}
    return verify_integrity_token(integrity_token or "", package_name)
