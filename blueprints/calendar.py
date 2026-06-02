"""
blueprints/calendar.py — Calendrier mensuel des transits & rapport PDF annuel
"""
from datetime import date as _date

from flask import Blueprint, Response, current_app, jsonify, request, session

from annual_report import generate_annual_pdf
from calendar_calc import get_monthly_transits

calendar_bp = Blueprint("calendar_bp", __name__)


@calendar_bp.route("/calendar")
def calendar_route():
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    today = _date.today()
    year  = int(request.args.get("year",  today.year))
    month = int(request.args.get("month", today.month))

    try:
        data = get_monthly_transits(profile, year, month)
        return jsonify({"ok": True, "year": year, "month": month, "days": data})
    except Exception as exc:
        current_app.logger.error("Erreur calendrier : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@calendar_bp.route("/report/annual")
def annual_report():
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    lang = session.get("lang", "fr")
    try:
        pdf_bytes = generate_annual_pdf(profile, lang=lang)
        from datetime import date as _date
        filename  = f"karmic_gochara_{profile.get('pseudo', 'rapport')}_{_date.today().year}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        current_app.logger.error("Erreur rapport PDF : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500
