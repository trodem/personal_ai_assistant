import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class SettingsNotificationsEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token(f"user-settings-notifications-{uuid4()}", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_notifications_update_persists_preferences(self) -> None:
        response = self.client.patch(
            "/api/v1/me/settings/notifications",
            headers=self.headers,
            json={"preferences": {"in_app": False, "push": True, "email": False}},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["notification_preferences"],
            {"in_app": False, "push": True, "email": False},
        )

        fetched = self.client.get("/api/v1/me/settings", headers=self.headers)
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(
            fetched.json()["notification_preferences"],
            {"in_app": False, "push": True, "email": False},
        )

    def test_notifications_update_requires_authentication(self) -> None:
        response = self.client.patch(
            "/api/v1/me/settings/notifications",
            json={"preferences": {"in_app": False, "push": True, "email": False}},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_notifications_update_rejects_invalid_payload(self) -> None:
        response = self.client.patch(
            "/api/v1/me/settings/notifications",
            headers=self.headers,
            json={"preferences": {"in_app": False, "push": True}},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.missing_required_fields")


if __name__ == "__main__":
    unittest.main()
