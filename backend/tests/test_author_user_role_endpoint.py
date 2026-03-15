import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class AuthorUserRoleEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.author_user_id = f"author-role-{uuid4()}"
        author_token = build_dev_token(
            self.author_user_id,
            tenant_id="tenant-a",
            role="author",
            mfa_enabled=True,
        )
        admin_token = build_dev_token(
            f"admin-role-{uuid4()}",
            tenant_id="tenant-a",
            role="admin",
            mfa_enabled=True,
        )
        author_no_mfa_token = build_dev_token(
            f"author-no-mfa-role-{uuid4()}",
            tenant_id="tenant-a",
            role="author",
            mfa_enabled=False,
        )
        self.author_headers = {"Authorization": f"Bearer {author_token}", "x-tenant-id": "tenant-a"}
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": "tenant-a"}
        self.author_no_mfa_headers = {"Authorization": f"Bearer {author_no_mfa_token}", "x-tenant-id": "tenant-a"}
        self.target_user_id = f"target-role-user-{uuid4()}"

    def test_author_can_promote_and_demote_user(self) -> None:
        promoted = self.client.patch(
            f"/api/v1/author/users/{self.target_user_id}/role",
            headers=self.author_headers,
            json={"role": "admin"},
        )
        self.assertEqual(promoted.status_code, 200)
        promoted_payload = promoted.json()
        self.assertEqual(promoted_payload["role"], "admin")
        self.assertEqual(promoted_payload["subscription_plan"], "premium")
        self.assertTrue(promoted_payload["billing_exempt"])

        demoted = self.client.patch(
            f"/api/v1/author/users/{self.target_user_id}/role",
            headers=self.author_headers,
            json={"role": "user"},
        )
        self.assertEqual(demoted.status_code, 200)
        demoted_payload = demoted.json()
        self.assertEqual(demoted_payload["role"], "user")
        self.assertEqual(demoted_payload["subscription_plan"], "free")
        self.assertFalse(demoted_payload["billing_exempt"])

    def test_non_author_cannot_update_role(self) -> None:
        response = self.client.patch(
            f"/api/v1/author/users/{self.target_user_id}/role",
            headers=self.admin_headers,
            json={"role": "admin"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_author_without_mfa_cannot_update_role(self) -> None:
        response = self.client.patch(
            f"/api/v1/author/users/{self.target_user_id}/role",
            headers=self.author_no_mfa_headers,
            json={"role": "admin"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.mfa_required")

    def test_author_cannot_change_own_role(self) -> None:
        response = self.client.patch(
            f"/api/v1/author/users/{self.author_user_id}/role",
            headers=self.author_headers,
            json={"role": "admin"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")


if __name__ == "__main__":
    unittest.main()
