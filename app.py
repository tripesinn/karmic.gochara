"""
app.py — Gochara Karmique
Application Flask — Architecture multi-utilisateurs avec Blueprints (v2)

3094 lignes -> ~50 lignes (create_app)
40 routes -> 12 blueprints
"""
import os

from dotenv import load_dotenv
from flask import Flask

from logging_config import request_middleware, setup_logging

load_dotenv(dotenv_path=".env")
setup_logging()


def create_app():
    """Factory: cree et configure l'application Flask avec tous les blueprints."""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "gochara-secret-2024")
    app.config["JSON_AS_ASCII"] = False
    request_middleware(app)

    # ── Enregistrement des Blueprints ──────────────────────────────────────
    from blueprints.public import public_bp
    from blueprints.auth import auth_bp
    from blueprints.astro import astro_bp
    from blueprints.chat import chat_bp
    from blueprints.alerts import alerts_bp
    from blueprints.calendar import calendar_bp
    from blueprints.cron import cron_bp
    from blueprints.email import email_bp
    from blueprints.payments import payments_bp
    from blueprints.api import api_bp
    from blueprints.data import data_bp
    from blueprints.geocode import geocode_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(astro_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(cron_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(geocode_bp)

    return app


# ── Instance pour usage direct (gunicorn, flask run, debug) ──────────────
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
