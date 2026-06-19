"""
jwt_auth.py — JWT authentication helpers + @token_required decorator

Deux modes coexistants :
  1. JWT (Authorization: Bearer <token>) — pour l'API Capacitor / Astro frontend
  2. Flask session (cookie) — rétrocompatibilité existante

Le decorator @token_required vérifie JWT en priorité, puis session.
"""

import os
import time
from functools import wraps

import jwt
from flask import g, jsonify, request, session

# ── Configuration ─────────────────────────────────────────────────────────────

_JWT_SECRET = None  # loaded lazy depuis .env
_ACCESS_TTL = 3600          # 1h
_REFRESH_TTL = 2592000      # 30j


def _get_secret() -> str:
    global _JWT_SECRET
    if _JWT_SECRET is None:
        _JWT_SECRET = os.environ.get("JWT_SECRET")
        if not _JWT_SECRET:
            # Fallback vers SECRET_KEY (pas idéal, mais fonctionnel)
            _JWT_SECRET = os.environ.get("SECRET_KEY", "fallback-dev-secret")
    return _JWT_SECRET


# ── Token creation ────────────────────────────────────────────────────────────

def create_tokens(pseudo: str) -> dict:
    """Crée un access_token (1h) + refresh_token (30j) pour un pseudo."""
    now = int(time.time())
    secret = _get_secret()

    access_token = jwt.encode(
        {
            "sub": pseudo,
            "type": "access",
            "iat": now,
            "exp": now + _ACCESS_TTL,
        },
        secret,
        algorithm="HS256",
    )

    refresh_token = jwt.encode(
        {
            "sub": pseudo,
            "type": "refresh",
            "iat": now,
            "exp": now + _REFRESH_TTL,
        },
        secret,
        algorithm="HS256",
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": _ACCESS_TTL,
    }


# ── Token verification ────────────────────────────────────────────────────────

def verify_token(token: str) -> str | None:
    """Vérifie un JWT et retourne le pseudo. None si invalide/expiré."""
    try:
        payload = jwt.decode(
            token,
            _get_secret(),
            algorithms=["HS256"],
            options={"require": ["sub", "type", "exp"]},
        )
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def refresh_access_token(refresh_token: str) -> dict | None:
    """Échange un refresh_token valide contre un nouveau access_token."""
    pseudo = verify_token(refresh_token) if is_refresh_token(refresh_token) else None
    if not pseudo:
        return None
    return create_tokens(pseudo)


def is_refresh_token(token: str) -> bool:
    """Vérifie qu'un token existe et est de type refresh (sans expirer)."""
    try:
        payload = jwt.decode(
            token,
            _get_secret(),
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        return payload.get("type") == "refresh"
    except jwt.InvalidTokenError:
        return False


# ── Route decorator (@token_required) ─────────────────────────────────────────

def token_required(f):
    """
    Decorator qui protège une route Flask.
    Vérifie Authorization: Bearer <JWT> en priorité,
    puis session.get('profile') en fallback.

    Usage :
        @auth_bp.route('/secret')
        @token_required
        def my_route():
            profile = g.profile  # fourni par le decorator
            return jsonify({"ok": True})
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        profile = _resolve_profile()
        if profile is None:
            return jsonify({"ok": False, "error": "Non authentifié"}), 401
        g.profile = profile
        g.pseudo = profile.get("pseudo", "")
        return f(*args, **kwargs)

    return decorated


# ── Before-request middleware (transparent compatibility) ─────────────────────

def jwt_before_request():
    """
    Intercepte chaque requête. Si un header Authorization: Bearer <token>
    est présent, vérifie le JWT et hydrate session['profile'] / g.profile
    pour que les routes existantes basées sur session.get('profile')
    fonctionnent sans modification.
    """
    auth_header = request.headers.get("Authorization", "").strip()
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
        pseudo = verify_token(token)
        if pseudo:
            # Hydrate g pour le decorator @token_required
            g.pseudo = pseudo
            g.token_authenticated = True
            # Hydrate aussi session['profile'] pour les routes existantes
            if "profile" not in session or session.get("pseudo") != pseudo:
                try:
                    from profiles import get_profile_by_pseudo
                    profile = get_profile_by_pseudo(pseudo)
                    if profile:
                        session["pseudo"] = pseudo
                        session["profile"] = profile
                except Exception:
                    pass
            # Fallback : si get_profile_by_pseudo échoue, on crée un profil minimal
            if "profile" not in session:
                session["pseudo"] = pseudo
                session["profile"] = {"pseudo": pseudo, "name": pseudo, "plan": "free"}
        else:
            # Token invalide mais présent → on refuse silencieusement
            # (le endpoint retournera 401 si besoin)
            pass


def _resolve_profile() -> dict | None:
    """Retourne le profil depuis g, session, ou None si non auth."""
    # Déjà résolu dans g (via decorator ou before_request)
    if hasattr(g, "profile") and g.profile:
        return g.profile

    # Session Flask
    profile = session.get("profile")
    if profile:
        g.profile = profile
        g.pseudo = profile.get("pseudo", "")
        return profile

    return None
