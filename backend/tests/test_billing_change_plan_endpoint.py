import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class BillingChangePlanEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        user_token = build_dev_token(f"user-billing-{uuid4()}", tenant_id="tenant-a", role="user")
        admin_token = build_dev_token(f"admin-billing-{uuid4()}", tenant_id="tenant-a", role="admin")
        author_token = build_dev_token(f"author-billing-{uuid4()}", tenant_id="tenant-a", role="author")
        self.user_headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": "tenant-a"}
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": "tenant-a"}
        self.author_headers = {"Authorization": f"Bearer {author_token}", "x-tenant-id": "tenant-a"}

    def test_user_can_change_plan_to_premium_and_back_to_free(self) -> None:
        upgrade = self.client.post(
            "/api/v1/billing/subscription/change-plan",
            headers=self.user_headers,
            json={"plan": "premium"},
        )
        self.assertEqual(upgrade.status_code, 200)
        self.assertEqual(upgrade.json()["subscription_plan"], "premium")
        self.assertFalse(upgrade.json()["billing_exempt"])

        downgrade = self.client.post(
            "/api/v1/billing/subscription/change-plan",
            headers=self.user_headers,
            json={"plan": "free"},
        )
        self.assertEqual(downgrade.status_code, 200)
        self.assertEqual(downgrade.json()["subscription_plan"], "free")
        self.assertFalse(downgrade.json()["billing_exempt"])

    def test_change_plan_is_locked_for_admin(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/change-plan",
            headers=self.admin_headers,
            json={"plan": "free"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_change_plan_is_locked_for_author(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/change-plan",
            headers=self.author_headers,
            json={"plan": "free"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_change_plan_requires_authentication(self) -> None:
        response = self.client.post("/api/v1/billing/subscription/change-plan", json={"plan": "premium"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_change_plan_rejects_invalid_plan(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/change-plan",
            headers=self.user_headers,
            json={"plan": "enterprise"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.missing_required_fields")

    def test_user_can_get_cancel_preview(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/cancel-preview",
            headers=self.user_headers,
            json={"reason": "too_expensive"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("can_pause", payload)
        self.assertIn("can_downgrade", payload)
        self.assertIn("suggested_offer", payload)
        self.assertIn("impact_summary", payload)

    def test_cancel_preview_is_locked_for_admin(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/cancel-preview",
            headers=self.admin_headers,
            json={"reason": "too_expensive"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_cancel_preview_is_locked_for_author(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/cancel-preview",
            headers=self.author_headers,
            json={"reason": "low_value"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_cancel_preview_requires_authentication(self) -> None:
        response = self.client.post("/api/v1/billing/subscription/cancel-preview", json={"reason": "other"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_cancel_preview_rejects_invalid_reason(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/cancel-preview",
            headers=self.user_headers,
            json={"reason": "invalid_reason"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.missing_required_fields")

    def test_user_can_cancel_subscription(self) -> None:
        # ensure user is on premium first
        self.client.post(
            "/api/v1/billing/subscription/change-plan",
            headers=self.user_headers,
            json={"plan": "premium"},
        )
        response = self.client.post(
            "/api/v1/billing/subscription/cancel",
            headers=self.user_headers,
            json={"reason": "too_expensive", "comment": "Need to cut costs"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["subscription_plan"], "free")
        self.assertFalse(response.json()["billing_exempt"])

    def test_cancel_subscription_is_locked_for_admin(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/cancel",
            headers=self.admin_headers,
            json={"reason": "other"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_cancel_subscription_is_locked_for_author(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/cancel",
            headers=self.author_headers,
            json={"reason": "other"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_cancel_subscription_requires_authentication(self) -> None:
        response = self.client.post("/api/v1/billing/subscription/cancel", json={"reason": "other"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_cancel_subscription_rejects_invalid_reason(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/cancel",
            headers=self.user_headers,
            json={"reason": "invalid_reason"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.missing_required_fields")


if __name__ == "__main__":
    unittest.main()
