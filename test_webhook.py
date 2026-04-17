"""
test_webhook.py — Crée une vraie Stripe checkout session de test.
Usage : python test_webhook.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Supporte STRIPE_SECRET_KEY et KARMIC_STRIPE_SECRET_KEY
secret_key = os.environ.get("STRIPE_SECRET_KEY") or os.environ.get("KARMIC_STRIPE_SECRET_KEY")
if not secret_key:
    raise SystemExit("Erreur : STRIPE_SECRET_KEY ou KARMIC_STRIPE_SECRET_KEY manquant dans .env")

import stripe
stripe.api_key = secret_key

from stripe_payments import PRICE_ESSENTIAL

session = stripe.checkout.Session.create(
    customer_email="test@example.com",
    payment_method_types=["card"],
    line_items=[{"price": PRICE_ESSENTIAL, "quantity": 1}],
    mode="payment",
    success_url="https://karmicgochara.app/stripe/success?session_id={CHECKOUT_SESSION_ID}&plan=essential&pseudo=jero",
    cancel_url="https://karmicgochara.app/?payment=cancelled",
    metadata={"pseudo": "jero", "plan": "essential"},
)

print(f"\nCheckout URL :\n{session.url}\n")
print(f"Session ID : {session.id}")
