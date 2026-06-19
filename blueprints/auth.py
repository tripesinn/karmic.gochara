from flask import Blueprint, jsonify, request, session
from flask import current_app
import time
import re
from datetime import datetime
from i18n import LANGS
from app_common import _enrich_profile_with_natal, _pending_plan_updates
from jwt_auth import create_tokens, refresh_access_token

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/set_lang', methods=['POST'])
def set_lang():
    data = request.get_json() or {}
    code = data.get("lang", "fr")
    if code in LANGS:
        session["lang"] = code
    return jsonify({"ok": True, "lang": code})


@auth_bp.route('/login', methods=['POST'])
def login():
    from profiles import get_profile_by_pseudo
    data = request.get_json() or {}
    pseudo = (data.get("pseudo") or "").strip()
    if not pseudo:
        return jsonify({"ok": False, "error": "Pseudo requis"}), 400
    try:
        profile = get_profile_by_pseudo(pseudo)
    except Exception as exc:
        current_app.logger.error("Erreur Sheets login : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500
    if not profile:
        return jsonify({"ok": False, "error": f"Pseudo '{pseudo}' introuvable. Crée ton profil d'abord."}), 404
    if not profile.get("email") and not profile.get("year"):
        return jsonify({"ok": False, "error": "Profil incomplet. Email requis."}), 403
    # ── Contournement de la latence Sheets après paiement ────────────────────
    # 1. Store en mémoire (cas navigateur externe — session différente)
    pending = _pending_plan_updates.pop(pseudo.strip().lower(), None)
    if pending and time.time() - pending["time"] < 3600:
        profile["plan"] = pending["plan"]
        current_app.logger.info("Login post-paiement (store mémoire) : plan '%s' pour %s", pending["plan"], pseudo)
    # 2. Drapeau de session (cas WebView — même session)
    elif session.get("payment_completed"):
        payment_info = session.pop("payment_completed", None)
        if payment_info and payment_info.get("pseudo") == pseudo:
            profile["plan"] = payment_info.get("plan", profile["plan"])
            current_app.logger.info("Login post-paiement (session) : plan '%s' pour %s", profile["plan"], pseudo)

    session["profile"] = profile
    session["pseudo"] = pseudo

    # ── Hook natal : généré au login depuis données Sheets ───────────────────
    hook_natal = ""
    user_lang = session.get("lang", "fr")
    cache_key = f"hook_natal_{pseudo}_{user_lang}"
    if session.get(cache_key):
        hook_natal = session[cache_key]

    # Toujours recalculer natal_positions en session (non stocké dans le Sheet)
    try:
        from datetime import date as _date

        from ai_interpret import get_hook_natal
        from astro_calc import calculate_transits
        from profiles import save_natal_to_sheet

        natal_input = {
            "name": profile["name"],
            "year": profile["year"], "month": profile["month"],
            "day": profile["day"], "hour": profile["hour"],
            "minute": profile["minute"], "lat": profile["lat"],
            "lon": profile["lon"], "tz": profile["tz"],
            "city": profile["city"],
        }
        today = _date.today()
        transit_loc = {
            "city": profile["city"], "lat": profile["lat"],
            "lon": profile["lon"], "tz": profile["tz"],
        }
        natal_result = calculate_transits(natal_input, transit_loc,
                                          today.year, today.month, today.day, 12, 0)

        enriched = _enrich_profile_with_natal(profile, natal_result.get("natal", {}))

        user_key = data.get("user_key")
        user_model = data.get("user_model")
        user_provider = data.get("user_provider")
        if user_key: enriched["user_key"] = user_key
        if user_model: enriched["user_model"] = user_model
        if user_provider: enriched["user_provider"] = user_provider

        if not profile.get("chandra_lagna_sign"):
            save_natal_to_sheet(pseudo, enriched)

        profile = enriched
        if not hook_natal and profile.get("plan", "free") != "free":
            hook_natal = get_hook_natal(profile, lang=user_lang)
            session[cache_key] = hook_natal

        # Mais on retire les positions lourdes pour le stockage en session (cookie 4KB)
        profile_session = profile.copy()
        profile_session.pop("natal_positions", None)
        profile_session.pop("user_key", None)
        profile_session.pop("user_model", None)
        profile_session.pop("user_provider", None)
        session["profile"] = profile_session
    except Exception as exc:
        current_app.logger.warning("Hook natal login échoué : %s", exc)

    return jsonify({
        "ok": True, "pseudo": pseudo, "profile": profile,
        "hook_natal": hook_natal, "hook_engine": "claude",
        **create_tokens(pseudo),
    })


@auth_bp.route('/register', methods=['POST'])
def register():
    from profiles import create_profile, get_profile_by_email, pseudo_exists
    data = request.get_json() or {}
    pseudo = (data.get("pseudo") or "").strip()
    if not pseudo:
        return jsonify({"ok": False, "error": "Pseudo requis"}), 400

    current_app.logger.info("REGISTER data reçue: %s", data)

    # 1. Validation des données d'inscription
    email = (data.get("email") or "").strip().lower()
    pseudo = (data.get("pseudo") or "").strip()

    if not pseudo:
        return jsonify({"ok": False, "error": "Pseudo requis"}), 400

    # Validation Email
    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"ok": False, "error": "Format email invalide."}), 400

    # Validation Date de Naissance
    birth_date_str = data.get("birth_date")
    if birth_date_str:
        try:
            datetime.strptime(birth_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"ok": False, "error": "Format date de naissance invalide. Utilisez YYYY-MM-DD."}), 400

    # Normalise : parse birth_date / birth_time si envoyés comme strings
    if "birth_date" in data and "year" not in data:
        try:
            parts = str(data["birth_date"]).split("-")
            data["year"] = int(parts[0])
            data["month"] = int(parts[1])
            data["day"] = int(parts[2])
        except Exception as e:
            current_app.logger.warning("Parse birth_date échoué: %s", e)

    if "birth_time" in data and "hour" not in data:
        try:
            time_parts = str(data["birth_time"]).split(":")
            data["hour"] = int(time_parts[0])
            data["minute"] = int(time_parts[1] if len(time_parts) > 1 else 0)
        except Exception as e:
            current_app.logger.warning("Parse birth_time échoué: %s", e)

    # Valeurs par défaut obligatoires
    data.setdefault("name", pseudo)
    data.setdefault("city", data.get("birth_city", ""))
    data.setdefault("lat", 48.8566)
    data.setdefault("lon", 2.3522)
    data.setdefault("tz", "Europe/Paris")
    # Transit = lieu natal par défaut
    data.setdefault("transit_city", data.get("city", ""))
    data.setdefault("transit_lat", data.get("lat", 48.8566))
    data.setdefault("transit_lon", data.get("lon", 2.3522))
    data.setdefault("transit_tz", data.get("tz", "Europe/Paris"))

    try:
        if pseudo_exists(pseudo):
            return jsonify({"ok": False, "error": "Pseudo déjà pris"}), 409
        email = (data.get("email") or "").strip().lower()
        if email and get_profile_by_email(email):
            return jsonify({"ok": False, "error": "Email déjà enregistré"}), 409

        # 1. Create basic profile in sheet
        profile = create_profile(data)
        session["pseudo"] = pseudo
        session["profile"] = profile
    except Exception as exc:
        current_app.logger.error("Erreur Sheets register : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500

    # 2. Try to calculate natal and enrich
    hook_natal = ""
    try:
        from datetime import date as _date

        from ai_interpret import get_hook_natal
        from astro_calc import calculate_transits
        from profiles import save_natal_to_sheet

        natal_input = {
            "name": profile["name"],
            "year": profile["year"], "month": profile["month"],
            "day": profile["day"], "hour": profile["hour"],
            "minute": profile["minute"], "lat": profile["lat"],
            "lon": profile["lon"], "tz": profile["tz"],
            "city": profile["city"],
        }
        today = _date.today()
        transit_loc = {
            "city": profile["city"], "lat": profile["lat"],
            "lon": profile["lon"], "tz": profile["tz"],
        }
        natal_result = calculate_transits(natal_input, transit_loc,
                                          today.year, today.month, today.day, 12, 0)

        # Verify result content before enriching
        if not natal_result.get("natal"):
            current_app.logger.error("Calcul natal a retourné un résultat vide pour %s", pseudo)
        else:
            enriched_profile = _enrich_profile_with_natal(profile, natal_result.get("natal", {}))

            # 3. Save natal info to sheet and update session
            user_key = data.get("user_key")
            user_model = data.get("user_model")
            user_provider = data.get("user_provider")

            if user_key: enriched_profile["user_key"] = user_key
            if user_model: enriched_profile["user_model"] = user_model
            if user_provider: enriched_profile["user_provider"] = user_provider

            if save_natal_to_sheet(pseudo, enriched_profile):
                profile = enriched_profile
                # On retire les positions lourdes pour le stockage en session (cookie 4KB)
                profile_session = profile.copy()
                profile_session.pop("natal_positions", None)
                profile_session.pop("user_key", None)
                profile_session.pop("user_model", None)
                profile_session.pop("user_provider", None)
                session["profile"] = profile_session
                current_app.logger.info("Profil enrichi et sauvegardé pour %s", pseudo)
            else:
                current_app.logger.error("Échec de save_natal_to_sheet pour %s", pseudo)

            # 4. Generate hook only if pro
            if profile.get("plan", "free") != "free":
                hook_natal = get_hook_natal(profile, lang=session.get("lang", "fr"))
    except Exception as exc:
        current_app.logger.error("Calcul natal register échoué pour %s : %s", pseudo, exc, exc_info=True)

    return jsonify({
        "ok": True, "pseudo": pseudo, "profile": profile,
        "hook_natal": hook_natal, "hook_engine": "claude",
        **create_tokens(pseudo),
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    lang = session.get("lang", "fr")
    session.clear()
    session["lang"] = lang
    return jsonify({"ok": True})


# ── JWT Token lifecycle ──────────────────────────────────────────────────────

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Échange un refresh_token contre un nouveau jeu de tokens."""
    data = request.get_json() or {}
    token = data.get("refresh_token", "")
    if not token:
        # Fallback: Authorization header
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()

    if not token:
        return jsonify({"ok": False, "error": "refresh_token requis"}), 400

    tokens = refresh_access_token(token)
    if not tokens:
        return jsonify({"ok": False, "error": "refresh_token invalide ou expiré"}), 401

    return jsonify({"ok": True, **tokens})
