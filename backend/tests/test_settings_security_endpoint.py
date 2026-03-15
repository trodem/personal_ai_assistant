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

    def test_enable_and_verify_2fa_flow_updates_settings_state(self) -> None:
        start = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "enable_2fa"},
        )
        self.assertEqual(start.status_code, 200)
        self.assertEqual(start.json(), {"accepted": True})

        missing_code = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "verify_2fa"},
        )
        self.assertEqual(missing_code.status_code, 422)
        self.assertEqual(missing_code.json()["error"]["code"], "memory.missing_required_fields")

        invalid_code = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "verify_2fa", "totp_code": "000000"},
        )
        self.assertEqual(invalid_code.status_code, 422)
        self.assertEqual(invalid_code.json()["error"]["code"], "memory.validation_failed")

        verify = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "verify_2fa", "totp_code": "123456"},
        )
        self.assertEqual(verify.status_code, 200)
        self.assertEqual(verify.json(), {"accepted": True})

        settings = self.client.get("/api/v1/me/settings", headers=self.headers)
        self.assertEqual(settings.status_code, 200)
        self.assertTrue(settings.json()["mfa_enabled"])

    def test_disable_and_verify_2fa_flow_updates_settings_state(self) -> None:
        enable = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "enable_2fa"},
        )
        self.assertEqual(enable.status_code, 200)
        verify_enable = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "verify_2fa", "totp_code": "123456"},
        )
        self.assertEqual(verify_enable.status_code, 200)

        disable = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "disable_2fa"},
        )
        self.assertEqual(disable.status_code, 200)
        verify_disable = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "verify_2fa", "totp_code": "123456"},
        )
        self.assertEqual(verify_disable.status_code, 200)

        settings = self.client.get("/api/v1/me/settings", headers=self.headers)
        self.assertEqual(settings.status_code, 200)
        self.assertFalse(settings.json()["mfa_enabled"])

    def test_disable_2fa_without_enabled_state_is_rejected(self) -> None:
        response = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.headers,
            json={"action": "disable_2fa"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.validation_failed")


if __name__ == "__main__":
    unittest.main()
