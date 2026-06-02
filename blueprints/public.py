"""
blueprints/public.py — Routes publiques (index, service worker, privacy, assetlinks)
"""
import os
import pytz
from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    make_response,
    render_template,
    request,
    send_from_directory,
    session,
)

from app_common import UNLIMITED_PSEUDOS
from i18n import LANGS, get_lang

public_bp = Blueprint("public_bp", __name__)


@public_bp.route("/")
def index():
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    user = session.get("profile")
    lang = get_lang()

    # Retour depuis Stripe : appliquer le plan si la session en a gardé la trace.
    if request.args.get("payment") == "success":
        payment_info = session.get("payment_completed")
        if payment_info and user and user.get("pseudo") == payment_info.get("pseudo"):
            user["plan"] = payment_info["plan"]
            session["profile"] = user
            session.modified = True

    # Injecte 'illimite' si le pseudo est dans la liste VIP
    display_user = dict(user) if user else {}
    if display_user.get("pseudo", "").lower() in UNLIMITED_PSEUDOS:
        display_user["plan"] = "illimite"

    return render_template(
        "index.html",
        user=display_user,
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
        lang=lang,
        ui=lang,  # On utilise 'lang' pour remplir 'ui'
        langs=LANGS,  # On envoie le dictionnaire complet pour la boucle for
        session_user=session.get('pseudo', ''),
        session_profile=session.get('profile', {}),
        enable_local_ai=os.environ.get('ENABLE_LOCAL_AI', '').lower() in ('1', 'true'),
        enable_features=os.environ.get('ENABLE_FEATURES', '').lower() in ('1', 'true'),
    )


@public_bp.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")


@public_bp.route("/privacy")
def privacy():
    return render_template("privacy-policy.html")


@public_bp.route("/.well-known/assetlinks.json")
def assetlinks():
    """Android App Links — permet au système de vérifier le domaine et rouvrir l'app."""
    data = [{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.karmicgochara.app",
            "sha256_cert_fingerprints": [
                "93:2B:A1:79:9C:2E:D7:BF:86:B2:2F:86:46:09:56:80:A8:5C:AD:56:D0:27:4D:DE:6F:53:C9:02:00:A1:DF:FE"
            ]
        }
    }]
    resp = make_response(jsonify(data))
    resp.headers["Content-Type"] = "application/json"
    return resp
