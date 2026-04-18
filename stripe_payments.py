"""
stripe_payments.py — Karmic Gochara
Gestion des paiements Stripe : nouveau pricing
  - Test Gemma     : 4,99 € one-time
  - Gemma Illimité : 9,99 €/mois récurrent
"""

import os
import stripe

# ── Price IDs (renseignés via variables d'environnement) ─────────────────────
PRICE_TEST_GEMMA      = os.environ.get("STRIPE_PRICE_TEST_GEMMA",      "")
PRICE_GEMMA_UNLIMITED = os.environ.get("STRIPE_PRICE_GEMMA_UNLIMITED", "")

# Plans → nombre de synthèses accordées (999 = illimité managé côté chatbot)
PLAN_SYNTHESES = {
    "test":         1,
    "subscription": 999,
    "free":         0,
}

PLAN_LABELS = {
    "test":         "Test Gemma",
    "subscription": "Chatbot Gemma Illimité",
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

    product_type : "test_gemma" | "gemma_unlimited"
    base_url     : ex "https://karmicgochara.app"
    """
    s = _stripe_client()

    price_map = {
        "test_gemma":      PRICE_TEST_GEMMA,
        "gemma_unlimited": PRICE_GEMMA_UNLIMITED,
    }
    plan_map = {
        "test_gemma":      "test",
        "gemma_unlimited": "subscription",
    }

    price_id = price_map.get(product_type)
    if not price_id:
        raise ValueError(
            f"product_type inconnu ou STRIPE_PRICE_{product_type.upper()} manquant."
        )

    plan = plan_map[product_type]
    mode = "subscription" if product_type == "gemma_unlimited" else "payment"

    session = s.checkout.Session.create(
        customer_email=user_email,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode=mode,
        success_url=(
            f"{base_url}/stripe/success"
            f"?session_id={{CHECKOUT_SESSION_ID}}&plan={plan}&pseudo={pseudo}"
        ),
        cancel_url=f"{base_url}/?payment=cancelled",
        metadata={"pseudo": pseudo, "plan": plan},
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
        PRICE_TEST_GEMMA:      "test",
        PRICE_GEMMA_UNLIMITED: "subscription",
    }
    return mapping.get(price_id, "free")
