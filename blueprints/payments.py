"""
blueprints/payments.py — Stripe checkout, success, webhook & payment completion
"""
import os

from flask import Blueprint, current_app, jsonify, render_template, request, session

from app_common import _fulfill_order

payments_bp = Blueprint("payments_bp", __name__)


@payments_bp.route("/stripe/checkout", methods=["POST"])
def stripe_checkout():
    """
    Crée une session Stripe Checkout.
    Body JSON : {"product_type": "test"|"subscription"}
    Retourne  : {"url": "https://checkout.stripe.com/..."}
    """
    from stripe_payments import create_checkout_session

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    data         = request.get_json() or {}
    product_type = data.get("product_type", "")
    if product_type not in ("test", "subscription"):
        return jsonify({"error": "product_type invalide"}), 400

    email  = profile.get("email", "")
    pseudo = profile.get("pseudo", "")
    if not email:
        return jsonify({"error": "Email requis pour le paiement"}), 400

    base_url = os.environ.get("DEEP_LINK_BASE_URL") or request.host_url.rstrip("/")
    try:
        url = create_checkout_session(product_type, email, pseudo, base_url)
        return jsonify({"url": url})
    except Exception as exc:
        current_app.logger.error("Stripe checkout error : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Stripe : succès paiement (page de transition) ──────────────────────────────
@payments_bp.route("/stripe/success")
def stripe_success():
    """
    Affiche une page de transition pendant que le paiement est vérifié
    et que la session utilisateur est mise à jour.
    """
    return render_template("payment_success.html")


# ── API : validation post-paiement ───────────────────────────────────────────
@payments_bp.route("/api/complete_payment", methods=["POST"])
def api_complete_payment():
    """
    Vérifie la session de paiement Stripe et met à jour le profil utilisateur.
    Appelé par le script sur la page /stripe/success.
    """
    from stripe_payments import verify_checkout_session

    data = request.get_json() or {}
    session_id = data.get("session_id")
    plan = data.get("plan")
    pseudo = data.get("pseudo")

    if not all([session_id, plan, pseudo]):
        return jsonify({"ok": False, "error": "Paramètres manquants"}), 400

    if not verify_checkout_session(session_id):
        current_app.logger.warning("Échec de vérification pour session Stripe : %s", session_id)
        return jsonify({"ok": False, "error": "Session de paiement invalide"}), 403

    try:
        _fulfill_order(pseudo, plan)

        # Mettre le plan directement en session sans relire Sheets (évite la latence de propagation).
        if "profile" in session:
            session["profile"]["plan"] = plan

        # Drapeau de secours pour le prochain login (si la session est perdue sur mobile).
        session["payment_completed"] = {"pseudo": pseudo, "plan": plan}
        session.modified = True

        return jsonify({"ok": True, "plan": plan})
    except Exception as exc:
        current_app.logger.error("Erreur api_complete_payment pour %s : %s", pseudo, exc)
        return jsonify({"ok": False, "error": "Erreur interne"}), 500


# ── Stripe Webhook ────────────────────────────────────────────────────────────
@payments_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """
    Reçoit les événements Stripe et met à jour le plan utilisateur.
    C'est la méthode de garantie si l'utilisateur ferme son navigateur.
    """
    from stripe_payments import verify_webhook

    payload    = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = verify_webhook(payload, sig_header)
    except Exception as exc:
        current_app.logger.warning("Webhook Stripe invalide : %s", exc)
        return jsonify({"error": "Signature invalide"}), 400

    if event["type"] == "checkout.session.completed":
        obj_raw  = event["data"]["object"]
        obj      = obj_raw.to_dict() if hasattr(obj_raw, "to_dict") else dict(obj_raw)
        metadata = obj.get("metadata") or {}
        pseudo   = metadata.get("pseudo", "")
        plan     = metadata.get("plan", "")
        customer = obj.get("customer", "") or ""

        if pseudo and plan:
            _fulfill_order(pseudo, plan, stripe_customer_id=customer)
            if plan == "test": # "test" corresponds to the "lecture" plan
                try:
                    from profiles import get_profile_by_pseudo
                    from transit_alerts import find_next_major_transit_event, send_next_event_alert_email
                    profile = get_profile_by_pseudo(pseudo)
                    if profile:
                        next_event = find_next_major_transit_event(profile)
                        if next_event:
                            send_next_event_alert_email(profile, next_event)
                except Exception as e:
                    current_app.logger.error(f"Failed to send next event alert for {pseudo}: {e}")

    elif event["type"] == "customer.subscription.deleted":
        obj_raw = event["data"]["object"]
        obj     = obj_raw.to_dict() if hasattr(obj_raw, "to_dict") else dict(obj_raw)
        customer_id = obj.get("id", "")
        if customer_id:
            try:
                # La logique pour retrouver un profil par customer_id doit être implémentée
                # dans profiles.py si nécessaire. Pour l'instant, on log.
                current_app.logger.info("Abonnement annulé pour customer_id: %s", customer_id)
                # downgrade_plan_by_customer_id(customer_id)
            except Exception as exc:
                current_app.logger.error("Erreur downgrade plan : %s", exc)

    return jsonify({"ok": True})
