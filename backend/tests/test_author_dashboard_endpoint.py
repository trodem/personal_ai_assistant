import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class AuthorDashboardEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.author_user_id = f"author-dashboard-{uuid4()}"
        author_token = build_dev_token(
            self.author_user_id,
            tenant_id="tenant-a",
            role="author",
            mfa_enabled=True,
        )
        admin_token = build_dev_token(
            f"admin-dashboard-{uuid4()}",
            tenant_id="tenant-a",
            role="admin",
            mfa_enabled=True,
        )
        author_no_mfa_token = build_dev_token(
            f"author-no-mfa-dashboard-{uuid4()}",
            tenant_id="tenant-a",
            role="author",
            mfa_enabled=False,
        )
        self.author_headers = {"Authorization": f"Bearer {author_token}", "x-tenant-id": "tenant-a"}
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": "tenant-a"}
        self.author_no_mfa_headers = {"Authorization": f"Bearer {author_no_mfa_token}", "x-tenant-id": "tenant-a"}
        self.target_user_id = f"target-dashboard-user-{uuid4()}"

    def test_author_dashboard_returns_global_metrics(self) -> None:
        self.client.patch(
            f"/api/v1/author/users/{self.target_user_id}/role",
            headers=self.author_headers,
            json={"role": "admin"},
        )
        self.client.patch(
            f"/api/v1/admin/users/{self.target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "suspended"},
        )

        response = self.client.get("/api/v1/author/dashboard", headers=self.author_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("total_users", payload)
        self.assertIn("users_by_role", payload)
        self.assertIn("users_by_status", payload)
        self.assertIn("users_by_plan", payload)
        self.assertIn("active_authors", payload)
        self.assertGreaterEqual(payload["total_users"], 1)
        self.assertGreaterEqual(payload["active_authors"], 1)

    def test_non_author_cannot_access_author_dashboard(self) -> None:
        response = self.client.get("/api/v1/author/dashboard", headers=self.admin_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_author_without_mfa_cannot_access_author_dashboard(self) -> None:
        response = self.client.get("/api/v1/author/dashboard", headers=self.author_no_mfa_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.mfa_required")


if __name__ == "__main__":
    unittest.main()
