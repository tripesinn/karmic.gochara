"""
blueprints/data.py — Data collection and public content routes
"""
import json as _json
import os
from datetime import date as date_cls
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
    request,
    session,
)

from ai_interpret import get_daily_signal
from app_common import TRANSIT_LOC_DEFAULT
from astro_calc import calculate_transits
from build_task_file import build_task_file, extract_dominant_transit, extract_natal_for_task

data_bp = Blueprint("data_bp", __name__)


@data_bp.route("/rate_synthesis", methods=["POST"])
def rate_synthesis():
    """
    Collecte le feedback utilisateur sur une synthèse.
    Body JSON : {
        "rating": 1 | -1,
        "consent": true | false,
        "synthesis": "texte complet",
        "date": "2026-04-17"
    }
    Stocke dans Google Sheets onglet 'dataset' si consent=true.
    Retourne toujours {"ok": True} (non bloquant).
    """
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    data     = request.get_json() or {}
    rating   = int(data.get("rating", 0))     # 1 = 👍  /  -1 = 👎
    consent  = bool(data.get("consent", False))
    synthesis = (data.get("synthesis") or "").strip()
    date_str  = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    if rating not in (1, -1):
        return jsonify({"ok": False, "error": "Rating invalide"}), 400

    # Positions natales anonymisées (sans nom ni email)
    positions = {
        "chandra_lagna": profile.get("chandra_lagna_sign", ""),
        "ketu":          f"{profile.get('ketu_sign','')} H{profile.get('ketu_house','')}",
        "rahu":          f"{profile.get('rahu_sign','')} H{profile.get('rahu_house','')}",
        "chiron":        f"{profile.get('chiron_sign','')} H{profile.get('chiron_house','')}",
        "lilith":        f"{profile.get('lilith_sign','')} H{profile.get('lilith_house','')}",
        "saturn":        f"{profile.get('saturn_sign','')} H{profile.get('saturn_house','')}",
        "jupiter":       f"{profile.get('jupiter_sign','')} H{profile.get('jupiter_house','')}",
        "porte_visible": f"{profile.get('porte_visible_sign','')} H{profile.get('porte_visible_house','')}",
        "porte_invisible":f"{profile.get('porte_invisible_sign','')} H{profile.get('porte_invisible_house','')}",
    }

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
        creds_dict = _json.loads(creds_json)
        creds      = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc         = gspread.authorize(creds)

        sheet_id   = os.environ.get("GOOGLE_SHEET_ID", "")
        wb         = gc.open_by_key(sheet_id)

        # Crée l'onglet 'dataset' s'il n'existe pas
        try:
            ws = wb.worksheet("dataset")
        except gspread.exceptions.WorksheetNotFound:
            ws = wb.add_worksheet(title="dataset", rows=1000, cols=6)
            ws.append_row(["date", "positions_json", "synthesis", "rating", "consent", "lang"])

        lang = session.get("lang", "fr")

        # N'enregistre la synthèse que si consent=True
        row = [
            date_str,
            _json.dumps(positions, ensure_ascii=False),
            synthesis if consent else "",
            rating,
            1 if consent else 0,
            lang,
        ]
        ws.append_row(row)
        current_app.logger.info("Dataset row ajoutée : pseudo=%s rating=%s consent=%s",
                                profile.get("pseudo", "?"), rating, consent)

    except Exception as exc:
        # Non bloquant — le feedback UX est déjà affiché
        current_app.logger.warning("Erreur dataset write : %s", exc)

    return jsonify({"ok": True})


@data_bp.route("/content/daily", methods=["GET"])
def content_daily():
    """
    Route publique : Météo Astrologique globale pour TikTok/Web.
    NE REQUIERT PAS de login. user_id ignoré si fourni.

    Paramètres :
      ?date=yyyy-mm-dd    (optionnel, défaut = aujourd'hui)
      ?lang=fr|en         (optionnel, défaut = fr)
    """
    transit_date  = request.args.get("date", str(date_cls.today()))
    lang_override = request.args.get("lang", "fr")

    signal_data = get_daily_signal(transit_date)

    if "error" in signal_data:
        return jsonify({"error": signal_data["error"]}), 400

    if lang_override == "en":
        signal_data["cta"]["text"]    = "And you, born under a Full Moon in Leo?"
        signal_data["cta"]["subtext"] = "Discover what it means for YOUR natal chart"

    return jsonify(signal_data), 200


@data_bp.route("/generate_task")
def generate_task():
    """Génère et retourne le fichier .task pour l'utilisateur connecté."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "not_authenticated"}), 401

    now = datetime.now()
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
        "city":   profile.get("city", ""),
    }

    try:
        calc_result = calculate_transits(
            natal=natal,
            transit_loc=TRANSIT_LOC_DEFAULT,
            year=now.year, month=now.month, day=now.day,
            hour=now.hour, minute=now.minute,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    user = {
        "name": profile.get("pseudo", profile.get("name", "")),
        "lang": session.get("lang", profile.get("lang", "fr")),
    }

    natal_data   = extract_natal_for_task(calc_result)
    transit_data = extract_dominant_transit(calc_result)
    task         = build_task_file(user, natal_data, transit_data)

    resp = make_response(_json.dumps(task, ensure_ascii=False, indent=2))
    resp.headers["Content-Type"] = "application/json"
    resp.headers["Content-Disposition"] = f'attachment; filename="karmic_{user["name"]}.task"'
    return resp
