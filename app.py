"""
app.py — Gochara Karmique
Application Flask — Architecture multi-utilisateurs
"""

import os
from datetime import datetime

import pytz
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gochara-secret-2024")
app.config["JSON_AS_ASCII"] = False

TRANSIT_LOC_DEFAULT = {
    "city": "Paris, France",
    "lat":  48.8566,
    "lon":  2.3522,
    "tz":   "Europe/Paris",
}


# ── Routes publiques ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    user = session.get("profile")
    return render_template(
        "index.html",
        user=user,
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
    )


@app.route("/login", methods=["POST"])
def login():
    from profiles import get_profile_by_email
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email requis"}), 400
    try:
        profile = get_profile_by_email(email)
    except Exception as exc:
        app.logger.error("Erreur Sheets login : %s", exc)
        return jsonify({"error": str(exc)}), 500
    if not profile:
        return jsonify({"error": "Profil introuvable. Crée ton compte."}), 404
    session["profile"] = profile
    return jsonify({"ok": True, "profile": profile})


@app.route("/register", methods=["POST"])
def register():
    from profiles import get_profile_by_email, pseudo_exists, create_profile
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    pseudo = (data.get("pseudo") or "").strip()
    if not email or not pseudo:
        return jsonify({"error": "Email et pseudo requis"}), 400
    try:
        if get_profile_by_email(email):
            return jsonify({"error": "Email déjà enregistré"}), 409
        if pseudo_exists(pseudo):
            return jsonify({"error": "Pseudo déjà pris"}), 409
        profile = create_profile(data)
    except Exception as exc:
        app.logger.error("Erreur Sheets register : %s", exc)
        return jsonify({"error": str(exc)}), 500
    session["profile"] = profile
    return jsonify({"ok": True, "profile": profile})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/geocode")
def geocode():
    import time, requests as req
    q = request.args.get("q", "")
    if not q:
        return jsonify([])
    try:
        r = req.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5},
            headers={"User-Agent": "GocharaKarmique/1.0"},
            timeout=5,
        )
        time.sleep(1)
        return jsonify(r.json())
    except Exception as exc:
        try:
            r2 = req.get(
                "https://photon.komoot.io/api/",
                params={"q": q, "limit": 5},
                headers={"User-Agent": "GocharaKarmique/1.0"},
                timeout=5,
            )
            features = r2.json().get("features", [])
            results = []
            for f in features:
                p = f.get("properties", {})
                g = f.get("geometry", {}).get("coordinates", [None, None])
                results.append({
                    "display_name": f"{p.get('name','')}, {p.get('country','')}",
                    "lat": str(g[1]), "lon": str(g[0]),
                })
            return jsonify(results)
        except Exception as exc2:
            return jsonify({"error": str(exc2)}), 500


# ── Routes protégées ──────────────────────────────────────────────────────────
@app.route("/calculate", methods=["POST"])
def calculate():
    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis, build_chart_context

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    natal = {
        "name":   profile["name"],
        "year":   profile["year"],
        "month":  profile["month"],
        "day":    profile["day"],
        "hour":   profile["hour"],
        "minute": profile["minute"],
        "lat":    profile["lat"],
        "lon":    profile["lon"],
        "tz":     profile["tz"],
        "city":   profile["city"],
    }

    transit_loc = {
        "city": profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
        "lat":  float(profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"])),
        "lon":  float(profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"])),
        "tz":   profile.get("transit_tz", TRANSIT_LOC_DEFAULT["tz"]),
    }

    data = request.get_json()
    date_str = data.get("date", "")
    hour = int(data.get("hour", 12))
    minute = int(data.get("minute", 0))

    try:
        year, month, day = map(int, date_str.split("-"))
        result = calculate_transits(natal, transit_loc, year, month, day, hour, minute)
        result["synthesis"] = get_synthesis(result)
        result["chart_context"] = build_chart_context(result)
        return jsonify(result)
    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    from ai_interpret import chat_response

    if not session.get("profile"):
        return jsonify({"error": "Non connecté"}), 401

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
```

Aussi, ajoute `requests` dans `requirements.txt` :
```
requests>=2.31.0
