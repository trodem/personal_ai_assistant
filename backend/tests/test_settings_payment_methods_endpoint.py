import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.api.schemas import PaymentMethodRecord
from app.services.payment_methods import add_payment_method_for_user


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

    def test_user_can_create_payment_method_setup_intent(self) -> None:
        response = self.client.post("/api/v1/me/settings/payment-methods/setup-intent", headers=self.user_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("client_secret", payload)
        self.assertTrue(payload["client_secret"].startswith("seti_"))

    def test_setup_intent_is_blocked_for_admin_role(self) -> None:
        response = self.client.post("/api/v1/me/settings/payment-methods/setup-intent", headers=self.admin_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_payment_methods_requires_authentication(self) -> None:
        response = self.client.get("/api/v1/me/settings/payment-methods")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_setup_intent_requires_authentication(self) -> None:
        response = self.client.post("/api/v1/me/settings/payment-methods/setup-intent")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_user_can_set_default_payment_method(self) -> None:
        method_a = PaymentMethodRecord(
            id=f"pm-a-{uuid4()}",
            brand="visa",
            last4="4242",
            exp_month=12,
            exp_year=2030,
            is_default=False,
        )
        method_b = PaymentMethodRecord(
            id=f"pm-b-{uuid4()}",
            brand="mastercard",
            last4="4444",
            exp_month=11,
            exp_year=2031,
            is_default=True,
        )
        seeded_user = "user-payment-methods-seeded"
        seeded_token = build_dev_token(seeded_user, tenant_id="tenant-a", role="user")
        seeded_headers = {"Authorization": f"Bearer {seeded_token}", "x-tenant-id": "tenant-a"}
        add_payment_method_for_user(tenant_id="tenant-a", user_id=seeded_user, payment_method=method_a)
        add_payment_method_for_user(tenant_id="tenant-a", user_id=seeded_user, payment_method=method_b)

        response = self.client.post(
            f"/api/v1/me/settings/payment-methods/{method_a.id}/default",
            headers=seeded_headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"updated": True})

        listed = self.client.get("/api/v1/me/settings/payment-methods", headers=seeded_headers)
        self.assertEqual(listed.status_code, 200)
        methods = listed.json()["items"]
        defaults = [item for item in methods if item["is_default"]]
        self.assertEqual(len(defaults), 1)
        self.assertEqual(defaults[0]["id"], method_a.id)

    def test_set_default_returns_404_for_unknown_method(self) -> None:
        response = self.client.post(
            f"/api/v1/me/settings/payment-methods/pm-missing-{uuid4()}/default",
            headers=self.user_headers,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")

    def test_set_default_is_blocked_for_admin_role(self) -> None:
        response = self.client.post(
            f"/api/v1/me/settings/payment-methods/pm-any-{uuid4()}/default",
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_set_default_requires_authentication(self) -> None:
        response = self.client.post(f"/api/v1/me/settings/payment-methods/pm-any-{uuid4()}/default")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_user_can_delete_payment_method(self) -> None:
        method_a = PaymentMethodRecord(
            id=f"pm-del-a-{uuid4()}",
            brand="visa",
            last4="4242",
            exp_month=12,
            exp_year=2030,
            is_default=True,
        )
        method_b = PaymentMethodRecord(
            id=f"pm-del-b-{uuid4()}",
            brand="mastercard",
            last4="4444",
            exp_month=11,
            exp_year=2031,
            is_default=False,
        )
        seeded_user = "user-payment-methods-delete-seeded"
        seeded_token = build_dev_token(seeded_user, tenant_id="tenant-a", role="user")
        seeded_headers = {"Authorization": f"Bearer {seeded_token}", "x-tenant-id": "tenant-a"}
        add_payment_method_for_user(tenant_id="tenant-a", user_id=seeded_user, payment_method=method_a)
        add_payment_method_for_user(tenant_id="tenant-a", user_id=seeded_user, payment_method=method_b)

        response = self.client.delete(
            f"/api/v1/me/settings/payment-methods/{method_a.id}",
            headers=seeded_headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"deleted": True})

        listed = self.client.get("/api/v1/me/settings/payment-methods", headers=seeded_headers)
        self.assertEqual(listed.status_code, 200)
        methods = listed.json()["items"]
        self.assertEqual(len(methods), 1)
        self.assertEqual(methods[0]["id"], method_b.id)
        self.assertTrue(methods[0]["is_default"])

    def test_delete_payment_method_returns_404_for_unknown_method(self) -> None:
        response = self.client.delete(
            f"/api/v1/me/settings/payment-methods/pm-missing-{uuid4()}",
            headers=self.user_headers,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")

    def test_delete_payment_method_is_blocked_for_admin_role(self) -> None:
        response = self.client.delete(
            f"/api/v1/me/settings/payment-methods/pm-any-{uuid4()}",
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_delete_payment_method_requires_authentication(self) -> None:
        response = self.client.delete(f"/api/v1/me/settings/payment-methods/pm-any-{uuid4()}")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")


if __name__ == "__main__":
    unittest.main()
