import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

import app as lab_app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = lab_app.app.test_client()

    def test_chat_returns_fallback_when_api_key_missing(self):
        response = self.client.post(
            "/chat",
            json={"message": "Hello"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "demo")
        self.assertIn("API key", payload["response"])


if __name__ == "__main__":
    unittest.main()
