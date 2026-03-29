"""
app.py — Gochara Karmique
Application Flask — Astrologie védique karmique personnelle de Jérôme
"""

import os
from datetime import datetime

import pytz
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.secret_key = os.environ.get("SECRET_KEY", "gochara-karmique-secret-2024")

# ── Données fixes de Jérôme (valeurs par défaut) ──────────────────────────────
NATAL_DEFAULT = {
    "name":   "Jérôme",
    "year":   1974,
    "month":  10,
    "day":    31,
    "hour":   8,
    "minute": 0,
    "lat":    48.7053,
    "lon":    2.3936,
    "tz":     "Europe/Paris",
    "city":   "Athis-Mons, France",
}

TRANSIT_LOC = {
    "city": "Rochechouart, France",
    "lat":  45.8186,
    "lon":  0.8191,
    "tz":   "Europe/Paris",
}


def get_natal():
    """Retourne les données natales depuis la session, ou les valeurs par défaut."""
    if "natal" in session:
        return session["natal"]
    return NATAL_DEFAULT.copy()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    natal = get_natal()
    return render_template(
        "index.html",
        natal=natal,
        transit_city=TRANSIT_LOC["city"],
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
    )


@app.route("/update_natal", methods=["POST"])
def update_natal():
    """Met à jour les données natales dans la session."""
    data = request.get_json()
    try:
        name   = str(data.get("name", "")).strip() or "Jérôme"
        year   = int(data["year"])
        month  = int(data["month"])
        day    = int(data["day"])
        hour   = int(data.get("hour", 0))
        minute = int(data.get("minute", 0))
        lat    = float(data["lat"])
        lon    = float(data["lon"])
        city   = str(data.get("city", "")).strip()
        tz     = str(data.get("tz", "Europe/Paris")).strip()

        # Validation basique
        if not (1900 <= year <= 2100): raise ValueError("Année invalide")
        if not (1 <= month <= 12):     raise ValueError("Mois invalide")
        if not (1 <= day <= 31):       raise ValueError("Jour invalide")
        if not (0 <= hour <= 23):      raise ValueError("Heure invalide")
        if not (0 <= minute <= 59):    raise ValueError("Minute invalide")
        if not (-90 <= lat <= 90):     raise ValueError("Latitude invalide")
        if not (-180 <= lon <= 180):   raise ValueError("Longitude invalide")
        pytz.timezone(tz)  # valide le fuseau horaire

        session["natal"] = {
            "name":   name,
            "year":   year,
            "month":  month,
            "day":    day,
            "hour":   hour,
            "minute": minute,
            "lat":    lat,
            "lon":    lon,
            "tz":     tz,
            "city":   city,
        }
        return jsonify({"ok": True, "natal": session["natal"]})

    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/reset_natal", methods=["POST"])
def reset_natal():
    """Remet les données natales par défaut."""
    session.pop("natal", None)
    return jsonify({"ok": True, "natal": NATAL_DEFAULT})


@app.route("/calculate", methods=["POST"])
def calculate():
    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis, build_chart_context

    data = request.get_json()
    date_str = data.get("date", "")
    hour = int(data.get("hour", 12))
    minute = int(data.get("minute", 0))

    natal = get_natal()

    try:
        year, month, day = map(int, date_str.split("-"))
        result = calculate_transits(natal, TRANSIT_LOC, year, month, day, hour, minute)
        result["name"] = natal["name"]
        result["synthesis"] = get_synthesis(result)
        result["chart_context"] = build_chart_context(result)
        return jsonify(result)
    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    from ai_interpret import chat_response

    data = request.get_json()
    message = data.get("message", "").strip()
    history = data.get("history", [])
    chart_context = data.get("chart_context", "")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    try:
        response = chat_response(message, history, chart_context)
        return jsonify({"response": response})
    except Exception as exc:
        app.logger.error("Erreur chat : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
