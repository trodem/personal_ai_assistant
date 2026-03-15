import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class SettingsPaymentMethodsEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        user_token = build_dev_token(f"user-payment-methods-{uuid4()}", tenant_id="tenant-a", role="user")
        admin_token = build_dev_token(
            f"admin-payment-methods-{uuid4()}",
            tenant_id="tenant-a",
            role="admin",
            mfa_enabled=True,
        )
        self.user_headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": "tenant-a"}
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": "tenant-a"}

    def test_user_can_list_payment_methods(self) -> None:
        response = self.client.get("/api/v1/me/settings/payment-methods", headers=self.user_headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIsInstance(response.json()["items"], list)

    def test_admin_role_is_blocked_by_plan_lock(self) -> None:
        response = self.client.get("/api/v1/me/settings/payment-methods", headers=self.admin_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_payment_methods_requires_authentication(self) -> None:
        response = self.client.get("/api/v1/me/settings/payment-methods")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")


if __name__ == "__main__":
    unittest.main()
