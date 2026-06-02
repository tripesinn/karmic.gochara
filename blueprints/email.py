"""
blueprints/email.py — Email & expand endpoints
"""
import os

from flask import Blueprint, current_app, jsonify, request, session

from i18n import get_lang

email_bp = Blueprint("email_bp", __name__)


@email_bp.route("/send_synthesis", methods=["POST"])
def send_synthesis():
    """Envoie la synthèse karmique par email via Resend."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    email = (profile.get("email") or "").strip()
    if not email:
        return jsonify({"ok": False, "error": "Aucun email dans ton profil"}), 400

    data      = request.get_json() or {}
    synthesis = (data.get("synthesis") or "").strip()
    date_str  = data.get("date", "")
    if not synthesis:
        return jsonify({"ok": False, "error": "Aucune synthèse à envoyer"}), 400

    resend_key = os.environ.get("RESEND_API_KEY", "")
    if not resend_key:
        return jsonify({"ok": False, "error": "Resend non configuré (RESEND_API_KEY manquant)"}), 500

    lang   = get_lang()
    pseudo = profile.get("pseudo") or profile.get("name", "")

    # Corps HTML de l'email
    html_body = f"""
<!DOCTYPE html>
<html lang="{lang['code']}">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; background: #0a0a1a; color: #e8e0d0; margin: 0; padding: 20px; }}
  .container {{ max-width: 680px; margin: 0 auto; background: #0f0f2a; border: 1px solid #4b0082;
                border-radius: 4px; padding: 30px; }}
  h1 {{ color: #d4a017; font-size: 20px; border-bottom: 1px solid #4b0082; padding-bottom: 10px; }}
  .meta {{ color: #9090b0; font-size: 12px; margin-bottom: 20px; }}
  .synthesis {{ white-space: pre-wrap; line-height: 1.7; font-size: 14px; color: #e0d8f0; }}
  .synthesis h2 {{ color: #d4a017; font-size: 16px; margin-top: 24px; }}
  .synthesis h3 {{ color: #c090e0; font-size: 14px; }}
  .footer {{ margin-top: 30px; padding-top: 16px; border-top: 1px solid #4b0082;
             font-size: 11px; color: #606080; text-align: center; }}
  .support {{ margin-top: 20px; text-align: center; }}
  .support a {{
    background: #d4a017; color: #000; text-decoration: none;
    padding: 8px 20px; border-radius: 4px; font-weight: bold; font-size: 13px;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>✦ Karmic Gochara — @siderealAstro13</h1>
  <div class="meta">
    {pseudo} · {date_str} · Jyotish · Djwhal Khul · Chandra Lagna · Whole sign
  </div>
  <div class="synthesis">{synthesis}</div>
  <div class="support">
    <a href="https://buymeacoffee.com/jerome6">☕ {lang['support_label']}</a>
  </div>
  <div class="footer">
    Généré par Karmic Gochara · karmic.gochara.onrender.com<br>
    Ayanamsa Djwhal Khul · Chandra Lagna · True Nodes · Whole sign
  </div>
</div>
</body>
</html>
"""

    import requests as req
    try:
        r = req.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json",
            },
           json={
                "from": "Gochara Karmique <karmic.gochara@astro.jeromemalige.fr>",
                "reply_to": "astro@jeromemalige.fr",
                "to": [email],
                "subject": f"✦ Karmic Gochara Synthesis {date_str}",
                "html": html_body,
            },
            timeout=10,
        )
        if r.status_code in (200, 201):
            return jsonify({"ok": True})
        else:
            current_app.logger.error("Resend error %s : %s", r.status_code, r.text)
            return jsonify({"ok": False, "error": f"Resend {r.status_code}"}), 500
    except Exception as exc:
        current_app.logger.error("Resend exception : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500


@email_bp.route("/save_email", methods=["POST"])
def save_email():
    from profiles import save_email_by_pseudo
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401
    data  = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    if not email or "@" not in email:
        return jsonify({"ok": False, "error": "Email invalide"}), 400
    try:
        pseudo = profile.get("pseudo", "")
        ok = save_email_by_pseudo(pseudo, email)
        if ok:
            profile["email"] = email
            session["profile"] = profile
            session.modified = True
        return jsonify({"ok": ok})
    except Exception as exc:
        current_app.logger.error("Erreur save_email : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500


# ── Expand : Alternative de Conscience (1 clic gratuit) ──────────────────────
@email_bp.route("/expand", methods=["POST"])
def expand():
    """
    Expansion gratuite unique — topic: alternative_conscience uniquement.
    Limité à 1 appel par session (session['expand_used']).
    """
    from ai_interpret import _build_natal_context

    data   = request.get_json() or {}
    topic  = data.get("topic", "")
    pseudo = data.get("pseudo", "")

    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    # Sécurité : 1 seul expand gratuit par session, sauf si clé perso fournie ou utilisateur illimité
    from app_common import UNLIMITED_PSEUDOS
    is_unlimited = pseudo.lower() in UNLIMITED_PSEUDOS
    if session.get("expand_used") and not user_key and not is_unlimited:
        return jsonify({"content": ""}), 429

    if topic != "alternative_conscience":
        return jsonify({"content": ""}), 403

    # Récupère le profil depuis la session (ou par pseudo)
    profile = session.get("profile")
    if not profile and pseudo:
        try:
            from profiles import get_profile_by_pseudo
            profile = get_profile_by_pseudo(pseudo)
        except Exception:
            pass

    if not profile:
        return jsonify({"content": "Profil introuvable."}), 404

    natal_ctx = _build_natal_context(profile)
    name      = profile.get("name", "")

    system = (
        "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
        "Style : chirurgical, dense, percutant. Tutoiement. "
        "INTERDIT ABSOLU : noms de signes zodiacaux. "
        "Utilise uniquement maisons (H1, H3…) et noms de planètes."
    )
    prompt = (
        f"Thème natal de {name} :\n{natal_ctx}\n\n"
        f"En 100 mots maximum, révèle L'Alternative de Conscience de {name}.\n"
        f"C'est l'insight transformateur central — le pivot entre la prison "
        f"de la Porte Invisible et la libération de la Porte Visible.\n"
        f"Sois chirurgical, personnel, percutant.\n"
        f"Aucun lien. Aucun titre. Texte seul."
    )

    try:
        from ai_interpret import HOOK_MODEL, generate_ai
        # Default to HOOK_MODEL if no user_model provided, so it correctly routes to Claude instead of Gemini (which lacks the server key)
        user_params = {
            "user_provider": user_provider,
            "user_key": user_key,
            "user_model": user_model or HOOK_MODEL
        }
        content = generate_ai(system, prompt, user=user_params, max_tokens=1024)

        # On ne marque 'utilisé' que si l'appel a réussi (et on ne bloque pas les illimités)
        if not is_unlimited:
            session["expand_used"] = True
            session.modified = True

        return jsonify({"content": content})
    except Exception as exc:
        current_app.logger.error("Erreur expand : %s", exc)
        return jsonify({"content": ""}), 500
