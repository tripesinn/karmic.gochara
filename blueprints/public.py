"""
blueprints/public.py — Routes publiques (index, service worker, privacy, assetlinks)
"""
import os
from datetime import datetime

import pytz
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


@public_bp.route("/terms")
def terms():
    """Conditions générales d'utilisation — requis par Google Play Console."""
    return render_template("terms.html")


@public_bp.route("/benchmark")
def benchmark():
    """Page publique du Benchmark IA Astrologique — alimentée par x_benchmark_bot.py"""
    bench_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "benchmark_results", "index.html")
    if os.path.exists(bench_path):
        return make_response(open(bench_path).read())
    # Fallback si le bot n'a pas encore généré la page
    return render_template("benchmark.html",
                           total_votes=0,
                           stats_html="<p style='color:var(--text-dim);'>En attente des premiers votes...</p>",
                           recent_html="")


@public_bp.route("/.well-known/assetlinks.json")
def assetlinks():
    """Android App Links — permet au système de vérifier le domaine et rouvrir l'app."""
    data = [{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.karmicgochara.app",
            "sha256_cert_fingerprints": [
                "06:E5:4A:A8:5B:5F:58:D7:EA:27:6F:71:AF:18:CC:83:43:78:B4:52:4E:49:25:E9:E2:FC:06:E8:BE:CD:D1:EF"
            ]
        }
    }]
    resp = make_response(jsonify(data))
    resp.headers["Content-Type"] = "application/json"
    return resp


@public_bp.route("/biorhythm/<filename>")
def public_biorhythm_file(filename):
    """Proxy pour servir les images du biorythme depuis le bucket GCS public."""
    # Sécurise le nom de fichier pour éviter les injections de chemin
    filename = os.path.basename(filename)
    gcs_url = f"https://storage.googleapis.com/karmic-gochara-public/biorhythm/{filename}"
    
    import requests
    from flask import Response
    try:
        resp = requests.get(gcs_url, timeout=5)
        if resp.status_code == 404:
            return jsonify({"error": "Fichier non trouvé"}), 404
        if resp.status_code != 200:
            return jsonify({"error": f"Erreur GCS: {resp.status_code}"}), resp.status_code
            
        content_type = resp.headers.get("Content-Type", "image/png")
        return Response(resp.content, mimetype=content_type)
    except requests.RequestException as e:
        return jsonify({"error": f"Erreur de connexion au stockage : {str(e)}"}), 502
