"""
blueprints/cron.py — Scheduled tasks (daily alerts)
"""
import os

from flask import Blueprint, current_app, jsonify, request

cron_bp = Blueprint("cron_bp", __name__, url_prefix="/cron")


@cron_bp.route("/daily", methods=["POST"])
def cron_daily():
    from transit_alerts import run_daily_alerts

    secret = os.environ.get("CRON_SECRET", "")
    if secret:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {secret}":
            return jsonify({"error": "Non autorisé"}), 401

    try:
        results = run_daily_alerts()
        current_app.logger.info("Cron alertes : %s", results)
        return jsonify({"ok": True, **results})
    except Exception as exc:
        current_app.logger.error("Erreur cron daily : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500
