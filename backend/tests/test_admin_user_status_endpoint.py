import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class AdminUserStatusEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        admin_token = build_dev_token(f"admin-status-{uuid4()}", tenant_id="tenant-a", role="admin", mfa_enabled=True)
        user_token = build_dev_token(f"user-status-{uuid4()}", tenant_id="tenant-a", role="user")
        admin_no_mfa_token = build_dev_token(
            f"admin-no-mfa-status-{uuid4()}",
            tenant_id="tenant-a",
            role="admin",
            mfa_enabled=False,
        )
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": "tenant-a"}
        self.user_headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": "tenant-a"}
        self.admin_no_mfa_headers = {"Authorization": f"Bearer {admin_no_mfa_token}", "x-tenant-id": "tenant-a"}
        self.target_user_id = f"target-user-{uuid4()}"

    def test_admin_can_suspend_reactivate_and_cancel_user(self) -> None:
        suspended = self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "suspended"},
        )
        self.assertEqual(suspended.status_code, 200)
        self.assertEqual(suspended.json()["status"], "suspended")

        reactivated = self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "active"},
        )
        self.assertEqual(reactivated.status_code, 200)
        self.assertEqual(reactivated.json()["status"], "active")

        canceled = self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "canceled"},
        )
        self.assertEqual(canceled.status_code, 200)
        self.assertEqual(canceled.json()["status"], "canceled")

    def test_updated_status_is_visible_in_admin_users_list(self) -> None:
        self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "suspended"},
        )
        listed = self.client.get("/api/v1/admin/users", headers=self.admin_headers)
        self.assertEqual(listed.status_code, 200)
        items = listed.json()["items"]
        target = next(item for item in items if item["id"] == self.target_user_id)
        self.assertEqual(target["status"], "suspended")

    def test_non_privileged_user_cannot_update_status(self) -> None:
        response = self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.user_headers,
            json={"status": "suspended"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_admin_without_mfa_cannot_update_status(self) -> None:
        response = self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.admin_no_mfa_headers,
            json={"status": "suspended"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.mfa_required")


if __name__ == "__main__":
    unittest.main()
