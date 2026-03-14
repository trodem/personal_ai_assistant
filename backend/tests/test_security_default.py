import json
import sys
import urllib.error
import urllib.request
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token


class SecurityDefaultTests(unittest.TestCase):
    def test_memories_requires_token(self) -> None:
        request = urllib.request.Request("http://localhost:8000/api/v1/memories")
        with self.assertRaises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(request, timeout=5)
        self.assertEqual(exc.exception.code, 401)
        payload = json.loads(exc.exception.read().decode("utf-8"))
        self.assertEqual(payload["error"]["code"], "auth.missing_token")

    def test_memories_rejects_invalid_token(self) -> None:
        request = urllib.request.Request("http://localhost:8000/api/v1/memories")
        request.add_header("Authorization", "Bearer invalid.token")
        with self.assertRaises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(request, timeout=5)
        self.assertEqual(exc.exception.code, 401)
        payload = json.loads(exc.exception.read().decode("utf-8"))
        self.assertEqual(payload["error"]["code"], "auth.invalid_token")

    def test_memories_are_user_scoped(self) -> None:
        token = build_dev_token("user-alpha")
        request = urllib.request.Request("http://localhost:8000/api/v1/memories")
        request.add_header("Authorization", f"Bearer {token}")

        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(response.status, 200)
            payload = json.loads(response.read().decode("utf-8"))

        self.assertIn("items", payload)
        self.assertEqual(len(payload["items"]), 1)
        self.assertIn("alpha", payload["items"][0]["raw_text"])
        self.assertNotIn("beta", payload["items"][0]["raw_text"])


if __name__ == "__main__":
    unittest.main()
