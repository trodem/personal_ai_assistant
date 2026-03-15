import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.repositories.admin_user_repository import upsert_admin_user


class PrivilegedPolicyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-privileged-{uuid4()}"
        self.author_user_id = f"author-policy-{uuid4()}"
        self.target_user_id = f"target-policy-{uuid4()}"

        author_token = build_dev_token(
            self.author_user_id,
            tenant_id=self.tenant_id,
            role="author",
            mfa_enabled=True,
        )
        admin_token = build_dev_token(
            f"admin-policy-{uuid4()}",
            tenant_id=self.tenant_id,
            role="admin",
            mfa_enabled=True,
        )
        self.author_headers = {"Authorization": f"Bearer {author_token}", "x-tenant-id": self.tenant_id}
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": self.tenant_id}

    def test_last_active_author_protection_blocks_role_change(self) -> None:
        # Seed a non-active author target so active-author count remains 1 (the current author).
        upsert_admin_user(
            tenant_id=self.tenant_id,
            user_id=self.target_user_id,
            role="author",
            status="suspended",
        )

        response = self.client.patch(
            f"/api/v1/author/users/{self.target_user_id}/role",
            headers=self.author_headers,
            json={"role": "admin"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "auth.last_active_author_required")

    def test_self_role_change_is_forbidden(self) -> None:
        response = self.client.patch(
            f"/api/v1/author/users/{self.author_user_id}/role",
            headers=self.author_headers,
            json={"role": "admin"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_billing_plan_locked_by_role_for_admin(self) -> None:
        response = self.client.post(
            "/api/v1/billing/subscription/change-plan",
            headers=self.admin_headers,
            json={"plan": "free"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "billing.plan_locked_by_role")

    def test_author_cannot_suspend_or_cancel_own_account(self) -> None:
        suspended = self.client.patch(
            f"/api/v1/admin/users/{self.author_user_id}/status",
            headers=self.author_headers,
            json={"status": "suspended"},
        )
        self.assertEqual(suspended.status_code, 403)
        self.assertEqual(suspended.json()["error"]["code"], "auth.forbidden")

        canceled = self.client.patch(
            f"/api/v1/admin/users/{self.author_user_id}/status",
            headers=self.author_headers,
            json={"status": "canceled"},
        )
        self.assertEqual(canceled.status_code, 403)
        self.assertEqual(canceled.json()["error"]["code"], "auth.forbidden")

    def test_last_active_author_protection_blocks_status_demotion(self) -> None:
        # Seed a single active author in tenant and attempt to suspend it.
        upsert_admin_user(
            tenant_id=self.tenant_id,
            user_id=self.target_user_id,
            role="author",
            status="active",
        )

        response = self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "suspended"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "auth.last_active_author_required")


if __name__ == "__main__":
    unittest.main()
