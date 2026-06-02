"""
blueprints/api.py — API endpoints : profil, plan_check, analyse karmique, prefetch année
"""
import time
from datetime import date, datetime, timedelta

import pytz
from flask import Blueprint, current_app, jsonify, request, session

from app_common import (
    TRANSIT_LOC_DEFAULT,
    _enrich_profile_with_natal,
    _pending_plan_updates,
)

api_bp = Blueprint("api_bp", __name__, url_prefix="/api")


@api_bp.route("/profile")
def api_profile():
    """Retourne le profil de l'utilisateur connecté."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non authentifié"}), 401
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
