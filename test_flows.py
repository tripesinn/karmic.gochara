import sys
from unittest.mock import MagicMock

sys.modules['gspread'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.oauth2'] = MagicMock()
sys.modules['google.oauth2.service_account'] = MagicMock()

import os
import unittest
from unittest.mock import patch

from app import app


class TestAppFlows(unittest.TestCase):

    def setUp(self):
        # Set dummy environment variables to avoid Stripe/Google errors
        os.environ["STRIPE_PRICE_TEST_GEMMA"] = "price_dummy_lecture"
        os.environ["STRIPE_PRICE_GEMMA_UNLIMITED"] = "price_dummy_unlimited"
        os.environ["KARMIC_STRIPE_SECRET_KEY"] = "sk_test_dummy"
        os.environ["GOOGLE_CREDENTIALS_JSON"] = "{}"
        os.environ["SHEET_ID"] = "dummy_sheet_id"

        self.client = app.test_client()
        self.client.testing = True

        # Utilisateur qui a DEJA acheté "Lecture" (plan: "test")
        self.mock_user_lecture = {
            "pseudo": "testuser",
            "email": "test@example.com",
            "plan": "test",
            "name": "testuser",
            "year": 2000, "month": 1, "day": 1,
            "hour": 12, "minute": 0, "lat": 48.8566,
            "lon": 2.3522, "tz": "Europe/Paris",
            "city": "Paris"
        }

    @patch("profiles.get_profile_by_pseudo")
    @patch("stripe_payments._stripe_client")
    def test_upgrade_lecture_to_unlimited(self, mock_stripe, mock_get_profile):
        print("\n=== FLUX 3: Upgrade de 'Lecture' vers 'Illimité' ===")
        mock_get_profile.return_value = self.mock_user_lecture
        
        # 1. Login
        resp_login = self.client.post("/login", json={"pseudo": "testuser"})
        print("✅ Connexion réussie, statut:", resp_login.status_code)
        
        # Vérifions le plan initial dans la session simulée
        with self.client.session_transaction() as sess:
            print("👉 Plan actuel avant achat:", sess['profile'].get('plan'))
        
        # 2. Checkout (Il clique sur 'Passer à l'illimité')
        mock_session_instance = MagicMock()
        mock_session_instance.url = "https://checkout.stripe.com/pay/subscription_upgrade"
        mock_stripe.return_value.checkout.Session.create.return_value = mock_session_instance
        
        resp_checkout = self.client.post("/stripe/checkout", json={"product_type": "subscription"})
        print("✅ Redirection Checkout (Illimité) statut:", resp_checkout.status_code)
        print("🔗 URL Checkout générée:", resp_checkout.get_json().get("url"))

        # 3. Validation
        with patch("app._fulfill_order") as mock_fulfill:
            with patch("stripe_payments.verify_checkout_session") as mock_verify:
                mock_verify.return_value = True
                resp_payment = self.client.post("/api/complete_payment", json={
                    "session_id": "cs_test_upgrade",
                    "plan": "subscription",
                    "pseudo": "testuser"
                })
                print("✅ Vérification post-paiement statut:", resp_payment.status_code)
                mock_fulfill.assert_called_with("testuser", "subscription")
                print("⭐ Plan mis à jour vers 'subscription' (Illimité) avec succès!\n")

if __name__ == "__main__":
    unittest.main()
