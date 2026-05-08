
import unittest
from unittest.mock import patch, MagicMock
from app import app

class MarieAccessTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_marie_unlimited_access(self):
        # The profile for 'Marie'
        marie_profile = {
            'pseudo': 'Marie',
            'name': 'Marie',
            'year': 1990,
            'month': 1,
            'day': 1,
            'hour': 12,
            'minute': 0,
            'lat': 48.8566,
            'lon': 2.3522,
            'tz': 'Europe/Paris',
            'city': 'Paris, France',
            'plan': 'free'  # Even with a 'free' plan, she should have unlimited access
        }

        with self.app as client:
            # First, we need to log in 'Marie' to establish a session
            with client.session_transaction() as sess:
                sess['profile'] = marie_profile

            # Try to access chat status
            response = client.get('/chat/status')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            # Since Marie is in UNLIMITED_PSEUDOS, remaining should be 999
            self.assertEqual(data.get("remaining"), 999)
            self.assertEqual(data.get("plan"), "subscription")

if __name__ == '__main__':
    unittest.main()
