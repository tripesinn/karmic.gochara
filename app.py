"""
app.py — Gochara Karmique
Architecture multi-utilisateurs — Login / Inscription / Calcul
"""

import os
from datetime import datetime, timedelta

import pytz
from flask import (Flask, jsonify, render_template, request,
                   session, redirect, url_for)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gochara-dev-secret-change-me")
app.config["JSON_AS_ASCII"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)


# ── Helpers session ───────────────────────────────────────────────────────────
def get_current_user() -> dict | None:
    return session.get("user")

def login_user(profile: dict):
    session.permanent = True
    session["user"] = profile

def logout_user():
    session.pop("user", None)


# ── Routes publiques ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    tz = pytz.timezone(user.get("transit_tz", "Europe/Paris"))
    now = datetime.now(tz)
    return render_template(
        "index.html",
        natal=user,
        transit_city=user.get("transit_city", ""),
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json(silent=True) or {}
    email  = data.get("email", "").strip().lower()
    pseudo = data.get("pseudo", "").strip().lower()

    if not email and not pseudo:
        return jsonify({"error": "Email ou pseudo requis."}), 400

    try:
        from profiles import get_profile_by_email, get_profile_by_pseudo
        profile = (get_profile_by_email(email) if email
                   else get_profile_by_pseudo(pseudo))
    except Exception as exc:
        app.logger.error("Erreur Sheets login : %s", exc)
        return jsonify({"error": f"Erreur serveur : {exc}"}), 500

    if not profile:
        return jsonify({"error": "Profil introuvable. Crée ton compte."}), 404

    login_user(profile)
    return jsonify({"ok": True, "name": profile["name"]})


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json(silent=True) or {}

    # Validation minimale
    required = ["pseudo", "email", "name", "year", "month", "day",
                "hour", "minute", "lat", "lon", "tz", "city",
                "transit_city", "transit_lat", "transit_lon", "transit_tz"]
    missing = [f for f in required if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400

    try:
        from profiles import get_profile_by_email, pseudo_exists, create_profile
        if get_profile_by_email(data["email"].strip().lower()):
            return jsonify({"error": "Cet email est déjà enregistré."}), 409
        if pseudo_exists(data["pseudo"].strip().lower()):
            return jsonify({"error": "Ce pseudo est déjà pris."}), 409
        profile = create_profile(data)
    except Exception as exc:
        app.logger.error("Erreur Sheets register : %s", exc)
        return jsonify({"error": f"Erreur serveur : {exc}"}), 500

    login_user(profile)
    return jsonify({"ok": True, "name": profile["name"]})


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "GET":
        return jsonify(user)

    # POST — mise à jour
    data = request.get_json(silent=True) or {}
    try:
        from profiles import update_profile
        updated = update_profile(user["email"], data)
        if updated:
            login_user(updated)
            return jsonify({"ok": True})
        return jsonify({"error": "Profil introuvable."}), 404
    except Exception as exc:
        app.logger.error("Erreur update profile : %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── Routes de calcul (protégées) ─────────────────────────────────────────────
@app.route("/calculate", methods=["POST"])
def calculate():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Non connecté."}), 401

    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis, build_chart_context

    data = request.get_json()
    date_str = data.get("date", "")
    hour   = int(data.get("hour",   12))
    minute = int(data.get("minute",  0))

    transit_loc = {
        "city": user.get("transit_city", ""),
        "lat":  float(user.get("transit_lat", 48.8566)),
        "lon":  float(user.get("transit_lon",  2.3522)),
        "tz":   user.get("transit_tz", "Europe/Paris"),
    }

    try:
        year, month, day = map(int, date_str.split("-"))
        result = calculate_transits(user, transit_loc, year, month, day, hour, minute)
        result["synthesis"]     = get_synthesis(result, user)
        result["chart_context"] = build_chart_context(result, user)
        return jsonify(result)
    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Non connecté."}), 401

    from ai_interpret import chat_response

    data          = request.get_json()
    message       = data.get("message", "").strip()
    history       = data.get("history", [])
    chart_context = data.get("chart_context", "")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    try:
        response = chat_response(message, history, chart_context, user)
        return jsonify({"response": response})
    except Exception as exc:
        app.logger.error("Erreur chat : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Geocoding proxy ───────────────────────────────────────────────────────────
import time as _time
_last_geocode = 0

@app.route("/geocode")
def geocode():
    import urllib.request, urllib.parse, urllib.error, json as _json

    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Paramètre q manquant"}), 400

    global _last_geocode
    elapsed = _time.time() - _last_geocode
    if elapsed < 1.0:
        _time.sleep(1.0 - elapsed)
    _last_geocode = _time.time()

    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": q, "format": "json", "limit": 5, "addressdetails": 1
    })
    req = urllib.request.Request(url, headers={"User-Agent": "GocharaKarmique/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            results = _json.loads(resp.read().decode())
        return jsonify(results)
    except Exception as exc:
        app.logger.error("Geocode error: %s", exc)
        return jsonify({"error": str(exc)}), 500


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
