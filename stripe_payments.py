"""
stripe_payments.py — Karmic Gochara
Gestion des paiements Stripe :
  - Lecture     : 4,99 € one-time
  - Illimité    : 9,99 €/mois récurrent
"""

import os
import stripe

# ── Price IDs (renseignés via variables d'environnement Render) ───────────────
PRICE_LECTURE   = os.environ.get("STRIPE_PRICE_LECTURE",   "")
PRICE_UNLIMITED = os.environ.get("STRIPE_PRICE_UNLIMITED", "")

PLAN_LABELS = {
    "test":         "Lecture",
    "subscription": "Illimité",
    "free":         "Gratuit",
}


def _stripe_client():
    stripe.api_key = os.environ.get("KARMIC_STRIPE_SECRET_KEY", "")
    return stripe


def create_checkout_session(
    product_type: str,
    user_email: str,
    pseudo: str,
    base_url: str,
) -> str:
    """
    Crée une session Stripe Checkout et retourne l'URL de paiement.

    product_type : "test" | "subscription"
    base_url     : ex "https://karmicgochara.app"
    """
    s = _stripe_client()

    price_map = {
        "test":         PRICE_LECTURE,
        "subscription": PRICE_UNLIMITED,
    }
    mode_map = {
        "test":         "payment",
        "subscription": "subscription",
    }

    price_id = price_map.get(product_type)
    if not price_id:
        raise ValueError(
            f"product_type inconnu ou variable STRIPE_PRICE manquante pour '{product_type}'."
        )

    session = s.checkout.Session.create(
        customer_email=user_email,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode=mode_map[product_type],
        success_url=(
            f"{base_url}/stripe/success"
            f"?session_id={{CHECKOUT_SESSION_ID}}&plan={product_type}&pseudo={pseudo}"
        ),
        cancel_url=f"{base_url}/?payment=cancelled",
        metadata={"pseudo": pseudo, "plan": product_type},
    )
    return session.url


def verify_webhook(payload: bytes, sig_header: str) -> dict:
    """Vérifie la signature du webhook Stripe et retourne l'événement."""
    s = _stripe_client()
    secret = os.environ.get("KARMIC_STRIPE_WEBHOOK_SECRET", "")
    return s.Webhook.construct_event(payload, sig_header, secret)


def get_plan_from_price(price_id: str) -> str:
    """Retourne le plan correspondant à un Price ID Stripe."""
    mapping = {
        PRICE_LECTURE:   "test",
        PRICE_UNLIMITED: "subscription",
    }
    return mapping.get(price_id, "free")
