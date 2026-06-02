"""
blueprints/alerts.py — Alertes transit : préférences, historique, déclenchement, test
"""
from datetime import date

from flask import Blueprint, current_app, jsonify, request, session

from app_common import _enrich_profile_with_natal
from email_formatter import format_alert_email
from profiles import get_profile_by_pseudo, set_alerts
from transit_alerts import detect_transit_events, generate_transit_alert, send_alert_email

alerts_bp = Blueprint("alerts_bp", __name__)


@alerts_bp.route("/api/v1/user/alert-preferences", methods=["PATCH"])
def alert_preferences():
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}
    enabled = data.get("enabled", False)

    success = set_alerts(profile["pseudo"], enabled)
    if success:
        # Update session
        session["profile"]["alerts_enabled"] = enabled
        session.modified = True
        return jsonify({"ok": True, "alerts_enabled": enabled})
    else:
        return jsonify({"error": "profile_not_found"}), 404


@alerts_bp.route("/api/v1/user/alerts/history", methods=["GET"])
def alert_history():
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "unauthorized"}), 401

    # Placeholder: In a real implementation, you would fetch this from a database.
    # The Google Sheet would have a new column for alert history (JSON string or similar).
    return jsonify({
        "history": [
            {"date": "2026-05-07", "narrative": "Placeholder: Saturne a activé votre Lune natale...", "urgency": "medium"},
            {"date": "2026-04-20", "narrative": "Placeholder: Un trigone de Jupiter a ouvert une opportunité...", "urgency": "low"}
        ]
    })


@alerts_bp.route("/api/v1/transit-alert", methods=["POST"])
def trigger_transit_alert():
    """Admin route to trigger a test alert for a user."""
    data = request.get_json() or {}
    pseudo = data.get("pseudo")
    if not pseudo:
        return jsonify({"error": "pseudo_required"}), 400

    # In a real app, this should be protected by an admin check
    # if session.get("user_role") != "admin":
    #     return jsonify({"error": "forbidden"}), 403

    user_profile = get_profile_by_pseudo(pseudo)
    if not user_profile:
        return jsonify({"error": "user_not_found"}), 404

    # Generate alert
    alert_data = generate_transit_alert(
        user_id=pseudo,
        birth_data=user_profile,
        current_date=date.today(),
        subscription_status=user_profile.get("plan", "free")
    )

    if not alert_data:
        return jsonify({"message": "No major transit event for this user today."})

    # Format email
    email_data = format_alert_email(
        alert_narrative=alert_data["analysis"],
        premium_teaser=alert_data["premium_teaser"],
        cta_text=alert_data["cta_button_text"],
        upgrade_link="https://karmicgochara.app/?open=synthesis&source=alert",
        user_name=user_profile.get("name", pseudo),
        urgency=alert_data["urgency"]
    )

    # In a real implementation, you would send the email here
    # send_email(user_profile['email'], email_data['subject_line'], email_data['html_email'])

    return jsonify({
        "message": "Test alert generated and formatted.",
        "alert_data": alert_data,
        "email_subject": email_data["subject_line"],
        # "html_email": email_data["html_email"] # Potentially large, returning only subject for brevity
    })


@alerts_bp.route("/toggle_alerts", methods=["POST"])
def toggle_alerts():
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    data    = request.get_json() or {}
    enabled = bool(data.get("enabled", False))
    pseudo  = profile.get("pseudo", "")

    email = (profile.get("email") or "").strip()
    if enabled and not email:
        return jsonify({"ok": False, "error": "Un email est requis pour activer les alertes."}), 400

    ok = set_alerts(pseudo, enabled)
    if ok:
        profile["alerts_enabled"] = int(enabled)
        session["profile"] = profile
    return jsonify({"ok": ok, "alerts_enabled": int(enabled)})


@alerts_bp.route("/alert/test", methods=["POST"])
def alert_test():
    """Envoie un email d'alerte test à l'utilisateur connecté (transits réels ou synthétiques)."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    email = (profile.get("email") or "").strip()
    if not email:
        return jsonify({"error": "Aucun email enregistré sur ce compte."}), 400

    enriched = _enrich_profile_with_natal(profile, {})

    try:
        events = detect_transit_events(enriched)
    except Exception as exc:
        current_app.logger.error("alert/test detect error: %s", exc, exc_info=True)
        events = []

    if not events:
        # Événement synthétique pour valider le canal email
        events = [{
            "type":    "debut",
            "kind":    "nakshatra",
            "transit": "Saturne ♄",
            "natal":   "Ketu",
            "nakshatra": "Mula",
            "lord":    "Ketu",
            "interpretation": "ROM_oppression",
        }]

    sent = send_alert_email(enriched, events)
    if sent:
        return jsonify({"ok": True, "email": email, "events": len(events)})
    return jsonify({"error": "Échec envoi email (vérifier RESEND_API_KEY)."}), 500
