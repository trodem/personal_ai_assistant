import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class SettingsSecurityEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token(f"user-settings-security-{uuid4()}", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_security_update_accepts_supported_action(self) -> None:
        response = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "change_password", "password": "new-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"accepted": True})

    def test_security_update_requires_authentication(self) -> None:
        response = self.client.patch(
            "/api/v1/me/settings/security",
            json={"action": "change_email", "email": "new@example.com"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_security_update_rejects_invalid_action(self) -> None:
        response = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "reset_all"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.missing_required_fields")


if __name__ == "__main__":
    unittest.main()
