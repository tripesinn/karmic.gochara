"""
blueprints/api.py — API endpoints : profil, plan_check, analyse karmique, prefetch année
"""
import time
from datetime import date, datetime, timedelta
import os

import pytz
from flask import Blueprint, current_app, jsonify, request, session

from app_common import (
    TRANSIT_LOC_DEFAULT,
    _enrich_profile_with_natal,
    _pending_plan_updates,
)

api_bp = Blueprint("api_bp", __name__, url_prefix="/api")


def _safe_tz(value: str, default: str = "Europe/Paris") -> str:
    """Retourne une timezone valide — sanitise 'undefined' et valeurs invalides."""
    if not value or str(value).strip().lower() in ("undefined", "none", ""):
        return default
    try:
        pytz.timezone(str(value))
        return str(value)
    except pytz.exceptions.UnknownTimeZoneError:
        return default


@api_bp.route("/profile")
def api_profile():
    """Retourne le profil de l'utilisateur connecté."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non authentifié"}), 401
    
    if "planets_info" not in profile:
        try:
            from datetime import date as _date
            from astro_calc import calculate_transits
            from app_common import _enrich_profile_with_natal
            
            _tz = _safe_tz(profile.get("tz"))
            natal_input = {
                "name": profile.get("name", ""),
                "year": int(profile.get("year", 1990)), "month": int(profile.get("month", 1)),
                "day": int(profile.get("day", 1)), "hour": int(profile.get("hour", 12)),
                "minute": int(profile.get("minute", 0)), "lat": float(profile.get("lat", 48.8566)),
                "lon": float(profile.get("lon", 2.3522)), "tz": _tz,
                "city": profile.get("city", ""),
            }
            today = _date.today()
            transit_loc = {
                "city": profile.get("city", ""), "lat": float(profile.get("lat", 48.8566)),
                "lon": float(profile.get("lon", 2.3522)), "tz": _tz,
            }
            natal_result = calculate_transits(natal_input, transit_loc,
                                              today.year, today.month, today.day, 12, 0)
            
            enriched = _enrich_profile_with_natal(profile, natal_result.get("natal", {}))
            profile = enriched
            session["profile"] = profile
        except Exception as e:
            current_app.logger.error("Erreur auto-hydratation profile : %s", e)

    from app_common import UNLIMITED_PSEUDOS
    if profile.get("pseudo", "").lower() in UNLIMITED_PSEUDOS:
        profile["plan"] = "illimite"

    return jsonify({"ok": True, "profile": profile})


@api_bp.route("/plan_check", methods=["POST"])
def api_plan_check():
    """
    Vérifie si un paiement est en attente pour ce pseudo (store mémoire).
    Appelé par le WebView au retour d'un navigateur externe après paiement.
    Met à jour la session si un plan en attente est trouvé.
    Body JSON : {"pseudo": "..."}
    """
    data   = request.get_json() or {}
    pseudo = (data.get("pseudo") or "").strip().lower()
    if not pseudo:
        return jsonify({"ok": False}), 400

    pending = _pending_plan_updates.pop(pseudo, None)
    if not pending or time.time() - pending["time"] >= 3600:
        return jsonify({"ok": False, "plan": None})

    plan = pending["plan"]
    # Mettre à jour la session courante si l'utilisateur est connecté
    if "profile" in session:
        session["profile"]["plan"] = plan
        session.modified = True
    current_app.logger.info("plan_check : plan '%s' appliqué pour %s", plan, pseudo)
    return jsonify({"ok": True, "plan": plan})


@api_bp.route("/v1/karmic-analysis", methods=["POST"])
def karmic_analysis_orchestrator():
    """
    Endpoint orchestrateur qui intègre les différentes logiques (astro, doctrine, paiement)
    pour fournir une analyse karmique complète.
    """
    from ai_interpret import get_synthesis
    from astro_calc import calculate_transits

    # 1. Vérification de la session utilisateur
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Utilisateur non authentifié"}), 401

    data = request.get_json() or {}
    user_query = data.get("user_query")
    if not user_query:
        return jsonify({"error": "Le paramètre 'user_query' est requis"}), 400

    # 2. Vérification du statut de paiement (logique de base)
    # Dans une implémentation réelle, on vérifierait un abonnement actif via Stripe.
    plan = profile.get("plan", "free").lower()
    if plan not in ["lecture", "illimité", "subscription", "test", "essential"]:
        return jsonify({
            "error": "Accès refusé",
            "message": "Cette fonctionnalité requiert un plan payant.",
            "recommendations": ["Veuillez souscrire à un plan pour continuer."]
        }), 403

    # 3. Calculs astrologiques
    try:
        # Utilise la date et le lieu de transit actuels du profil, ou la date du jour par défaut
        today = datetime.now(pytz.timezone(profile.get("transit_tz", "Europe/Paris")))
        date_str = profile.get("transit_date", today.strftime("%Y-%m-%d"))
        year, month, day = map(int, date_str.split("-"))
        hour = today.hour
        minute = today.minute

        natal_data = {k: profile.get(k) for k in ["name", "year", "month", "day", "hour", "minute", "lat", "lon", "tz", "city"]}
        transit_loc = {
            "city": profile.get("transit_city", natal_data["city"]),
            "lat":  profile.get("transit_lat", natal_data["lat"]),
            "lon":  profile.get("transit_lon", natal_data["lon"]),
            "tz":   profile.get("transit_tz", natal_data["tz"]),
        }

        astrological_data = calculate_transits(natal_data, transit_loc, year, month, day, hour, minute)
    except Exception as e:
        current_app.logger.error(f"Erreur de calcul astrologique: {e}", exc_info=True)
        return jsonify({"error": "Erreur lors du calcul astrologique."}), 500

    # 4. Interprétation basée sur la doctrine et la requête utilisateur
    try:
        # Enrichir le profil avec les données natales pour l'interprétation
        enriched_profile = _enrich_profile_with_natal(profile, astrological_data.get("natal", {}))

        # NOTE: La fonction get_synthesis est utilisée ici comme un analogue de l'agent de doctrine.
        # Idéalement, une nouvelle fonction serait créée, qui prendrait `user_query` en compte
        # pour une réponse plus ciblée. Pour l'instant, nous réutilisons la synthèse existante.
        lang = session.get("lang", "fr")
        karmic_analysis = get_synthesis(astrological_data, enriched_profile, lang=lang)

        # Recommandations statiques pour l'exemple
        recommendations = [
            "Méditez sur les aspects de votre Nœud Sud (Ketu) pour comprendre les schémas passés.",
            "Observez comment les transits actuels activent votre blessure originelle (Chiron).",
            "L'action consciente (Dharma) est la clé de la libération."
        ]
    except Exception as e:
        current_app.logger.error(f"Erreur d'interprétation de la doctrine: {e}", exc_info=True)
        return jsonify({"error": "Erreur lors de l'interprétation karmique."}), 500

    # 5. Réponse finale
    return jsonify({
        "karmic_analysis": karmic_analysis,
        "recommendations": recommendations,
        "astrological_context": {
            "transit_date": astrological_data.get("transit_date"),
            "sade_sati_status": astrological_data.get("sade_sati"),
            "active_dasha": astrological_data.get("dashas", [{}])[0].get("lord")
        }
    })


@api_bp.route("/prefetch_year", methods=["POST"])
def prefetch_year():
    """Précalcule et retourne tous les transits pour une année entière."""
    from astro_calc import calculate_transits

    data = request.get_json() or {}
    year = int(data.get("year", datetime.now().year))

    profile = session.get("profile")
    if not profile:
        natal = data.get("natal")
        if not natal:
            return jsonify({"error": "Non connecté ou coordonnées natales manquantes"}), 401
    else:
        natal = {
            "name":   profile.get("name", ""),
            "year":   profile["year"],
            "month":  profile["month"],
            "day":    profile["day"],
            "hour":   profile["hour"],
            "minute": profile["minute"],
            "lat":    profile["lat"],
            "lon":    profile["lon"],
            "tz":     profile["tz"],
            "city":   profile.get("city", ""),
        }

    transit_loc = data.get("transit_loc")
    if not transit_loc:
        transit_loc = TRANSIT_LOC_DEFAULT

    results = {}

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        try:
            res = calculate_transits(
                natal=natal,
                transit_loc=transit_loc,
                year=current_date.year,
                month=current_date.month,
                day=current_date.day,
                hour=12,
                minute=0
            )

            if profile:
                try:
                    from ai_interpret import build_prompt_only
                    enriched_profile = _enrich_profile_with_natal(profile, res.get("natal", {}))
                    prompts = build_prompt_only(res, enriched_profile, lang=session.get("lang", "fr"))
                    res["prompts"] = prompts
                except Exception:
                    pass

            date_key = current_date.strftime("%Y-%m-%d")
            results[date_key] = res
        except Exception:
            pass
        current_date += timedelta(days=1)

    return jsonify(results), 200


@api_bp.route("/vote", methods=["POST"])
def api_vote():
    """Enregistre un vote (1-5) pour une interprétation."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non authentifié"}), 401
    data = request.get_json() or {}
    rating = data.get("rating")
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"ok": False, "error": "Rating must be 1-5"}), 400
    provider = data.get("provider", "unknown")
    model = data.get("model", "unknown")
    pseudo = profile.get("pseudo", "anonymous")
    from profiles import save_vote
    ok = save_vote(pseudo, provider, model, rating)
    return jsonify({"ok": ok})


@api_bp.route("/benchmark")
def api_benchmark():
    """Retourne les stats benchmark public."""
    from profiles import get_benchmark
    data = get_benchmark()
    return jsonify({"ok": True, "benchmark": data})


@api_bp.route('/login_firebase', methods=['POST'])
def login_firebase():
    from profiles import get_profile_by_email
    import requests

    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    id_token = data.get("idToken")

    if id_token:
        try:
            # 🧪 Si l'émulateur Firebase Auth est configuré, on extrait l'email sans vérifier la signature en ligne
            emulator_host = os.environ.get("FIREBASE_AUTH_EMULATOR_HOST")
            if emulator_host:
                import jwt
                # Les tokens Firebase Emulator sont des JWT standards signés avec une clé de test 'none' ou autre.
                # On décode sans vérifier la signature pour le mode local.
                token_info = jwt.decode(id_token, options={"verify_signature": False})
                verified_email = token_info.get("email", "").strip().lower()
                if verified_email:
                    email = verified_email
                    current_app.logger.info("🧪 [EMULATEUR] ID Token extrait avec succès pour %s", email)
            else:
                from google.oauth2 import id_token as google_id_token
                from google.auth.transport import requests as google_requests
                try:
                    # Try Firebase token verification first (for Firebase ID tokens)
                    request_adapter = google_requests.Request()
                    token_info = google_id_token.verify_firebase_token(
                        id_token,
                        request_adapter,
                        audience="karmic-gochara-cloud"
                    )
                    verified_email = token_info.get("email", "").strip().lower()
                    if verified_email:
                        email = verified_email
                        current_app.logger.info("Firebase ID Token vérifié avec succès pour %s", email)
                except Exception as firebase_err:
                    current_app.logger.info("Vérification Firebase ID Token échouée ou sautée: %s. Tentative via Google tokeninfo...", firebase_err)
                    # Fallback to Google OAuth2 tokeninfo (for direct Google ID tokens)
                    verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
                    resp = requests.get(verify_url, timeout=5)
                    if resp.status_code == 200:
                        token_info = resp.json()
                        verified_email = token_info.get("email", "").strip().lower()
                        if verified_email:
                            email = verified_email
                            current_app.logger.info("Google ID Token vérifié avec succès via tokeninfo pour %s", email)
                        else:
                            return jsonify({"ok": False, "error": "Token Google valide mais email manquant"}), 400
                    else:
                        current_app.logger.warning("Vérification ID Token échouée (Firebase + Google tokeninfo): %s", resp.text)
                        return jsonify({"ok": False, "error": "Token invalide ou expiré"}), 401
        except Exception as exc:
            current_app.logger.error("Erreur lors de la validation du jeton: %s", exc)
            if not current_app.debug:
                return jsonify({"ok": False, "error": "Erreur de validation de jeton"}), 500

    if not email:
        return jsonify({"ok": False, "error": "Email requis"}), 400

    try:
        profile = get_profile_by_email(email)
    except Exception as exc:
        current_app.logger.error("Erreur Sheets login_firebase : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500

    if not profile:
        return jsonify({
            "ok": False,
            "needs_register": True,
            "error": "Profil inexistant. Veuillez créer un profil."
        }), 404

    pseudo = profile.get("pseudo")
    session["pseudo"] = pseudo

    # ── Hook natal : généré au login depuis données Sheets ───────────────────
    hook_natal = ""
    user_lang = session.get("lang", "fr")
    cache_key = f"hook_natal_{pseudo}_{user_lang}"
    if session.get(cache_key):
        hook_natal = session[cache_key]

    try:
        from datetime import date as _date
        from ai_interpret import get_hook_natal
        from astro_calc import calculate_transits
        from profiles import save_natal_to_sheet

        _tz = _safe_tz(profile.get("tz"))
        natal_input = {
            "name": profile.get("name", ""),
            "year": int(profile.get("year", 1990)), "month": int(profile.get("month", 1)),
            "day": int(profile.get("day", 1)), "hour": int(profile.get("hour", 12)),
            "minute": int(profile.get("minute", 0)), "lat": float(profile.get("lat", 48.8566)),
            "lon": float(profile.get("lon", 2.3522)), "tz": _tz,
            "city": profile.get("city", ""),
        }
        today = _date.today()
        transit_loc = {
            "city": profile.get("city", ""), "lat": float(profile.get("lat", 48.8566)),
            "lon": float(profile.get("lon", 2.3522)), "tz": _tz,
        }
        natal_result = calculate_transits(natal_input, transit_loc,
                                          today.year, today.month, today.day, 12, 0)

        enriched = _enrich_profile_with_natal(profile, natal_result.get("natal", {}))

        if not profile.get("chandra_lagna_sign"):
            save_natal_to_sheet(pseudo, enriched)

        profile = enriched
        if not hook_natal and profile.get("plan", "free") != "free":
            hook_natal = get_hook_natal(profile, lang=user_lang)
            session[cache_key] = hook_natal

        from app_common import UNLIMITED_PSEUDOS
        if pseudo.lower() in UNLIMITED_PSEUDOS:
            profile["plan"] = "illimite"

        profile_session = profile.copy()
        profile_session.pop("natal_positions", None)
        profile_session.pop("user_key", None)
        profile_session.pop("user_model", None)
        profile_session.pop("user_provider", None)
        session["profile"] = profile_session
    except Exception as exc:
        current_app.logger.warning("Hook natal login_firebase échoué : %s", exc)
        session["profile"] = profile

    from jwt_auth import create_tokens

    return jsonify({
        "ok": True,
        "pseudo": pseudo,
        "profile": profile,
        "hook_natal": hook_natal,
        "hook_engine": "claude",
        **create_tokens(pseudo)
    })


@api_bp.route("/calendar/<pseudo>.ics", methods=["GET"])
def get_calendar_ics(pseudo):
    from profiles import get_profile_by_pseudo
    from transit_alerts import (
        _positions_for_day,
        _active_conjunctions,
        detect_lunation_events,
        _active_nak_activations,
        PLANET_LABELS,
        NATAL_LABELS,
    )
    from flask import Response
    import hashlib

    profile = get_profile_by_pseudo(pseudo)
    if not profile:
        return "Profil non trouvé", 404

    year = date.today().year
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Karmic Gochara//NONSGML Calendar Feed//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Gochara Karmique - {profile.get('name', pseudo)}",
        "X-WR-TIMEZONE:Europe/Paris",
    ]

    current_date = start_date
    while current_date <= end_date:
        try:
            natal_pos, transit_pos = _positions_for_day(profile, current_date)
            
            # 1. Conjunctions
            conjs = _active_conjunctions(natal_pos, transit_pos)
            for pair in conjs:
                t_label = PLANET_LABELS.get(pair[0], pair[0])
                n_label = NATAL_LABELS.get(pair[1], pair[1])
                date_str = current_date.strftime("%Y%m%d")
                uid_seed = f"{pseudo}_{date_str}_{pair[0]}_{pair[1]}"
                uid = hashlib.md5(uid_seed.encode()).hexdigest() + "@karmicgochara.app"
                
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART;VALUE=DATE:{date_str}",
                    f"SUMMARY:✦ {t_label} conj. {n_label}",
                    f"DESCRIPTION:Alignement karmique de {t_label} sur {n_label}. Pic exact.",
                    "END:VEVENT"
                ])
                
            # 2. Lunations
            lunes = detect_lunation_events(profile, natal_pos, transit_pos)
            for e in lunes:
                t_label = e["transit"]
                n_label = e.get("interpretation", "Cycle lunaire")
                date_str = current_date.strftime("%Y%m%d")
                uid_seed = f"{pseudo}_{date_str}_lune_{t_label}"
                uid = hashlib.md5(uid_seed.encode()).hexdigest() + "@karmicgochara.app"
                
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART;VALUE=DATE:{date_str}",
                    f"SUMMARY:✦ {t_label}",
                    f"DESCRIPTION:{n_label} dans le nakshatra {e.get('nakshatra','')}.",
                    "END:VEVENT"
                ])
                
            # 3. Nakshatra activations
            natal_naks = {
                "Ketu":   profile.get("ketu_nakshatra", ""),
                "Rahu":   profile.get("rahu_nakshatra", ""),
                "Chiron": profile.get("chiron_nakshatra", ""),
            }
            naks = _active_nak_activations(natal_naks, transit_pos)
            for key, info in naks.items():
                t_name, point_key = key
                t_label = PLANET_LABELS.get(t_name, t_name)
                date_str = current_date.strftime("%Y%m%d")
                uid_seed = f"{pseudo}_{date_str}_nak_{t_name}_{point_key}"
                uid = hashlib.md5(uid_seed.encode()).hexdigest() + "@karmicgochara.app"
                
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART;VALUE=DATE:{date_str}",
                    f"SUMMARY:✦ Ingress {t_label} en {info['nakshatra']}",
                    f"DESCRIPTION:{t_label} traverse {info['nakshatra']} ({info['lord']}) - active {point_key} natal.",
                    "END:VEVENT"
                ])
        except Exception as e:
            current_app.logger.warning("Erreur calendar date %s : %s", current_date, e)
            
        current_date += timedelta(days=1)

    ics_lines.append("END:VCALENDAR")
    
    return Response(
        "\r\n".join(ics_lines),
        mimetype="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={pseudo}_gochara.ics"}
    )
