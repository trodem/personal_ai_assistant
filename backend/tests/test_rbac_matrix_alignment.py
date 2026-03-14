import unittest

from fastapi.testclient import TestClient

from app.core.auth import build_dev_token
from app.main import app


class RBACMatrixAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def _headers(
        self,
        *,
        user_id: str,
        role: str = "user",
        mfa_enabled: bool = False,
        account_status: str = "active",
        tenant_id: str = "tenant-a",
    ) -> dict[str, str]:
        token = build_dev_token(
            user_id,
            tenant_id=tenant_id,
            role=role,
            mfa_enabled=mfa_enabled,
            status=account_status,
        )
        return {"Authorization": f"Bearer {token}", "x-tenant-id": tenant_id}

    def test_user_denied_on_admin_users_endpoint(self) -> None:
        response = self.client.get("/api/v1/admin/users", headers=self._headers(user_id="user-alpha"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_admin_with_mfa_allowed_on_admin_users_endpoint(self) -> None:
        response = self.client.get(
            "/api/v1/admin/users",
            headers=self._headers(user_id="admin-alpha", role="admin", mfa_enabled=True),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())

    def test_author_with_mfa_allowed_on_admin_users_endpoint(self) -> None:
        response = self.client.get(
            "/api/v1/admin/users",
            headers=self._headers(user_id="author-alpha", role="author", mfa_enabled=True),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())

    def test_admin_without_mfa_blocked_on_admin_users_endpoint(self) -> None:
        response = self.client.get(
            "/api/v1/admin/users",
            headers=self._headers(user_id="admin-no-mfa", role="admin", mfa_enabled=False),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.mfa_required")

    def test_suspended_account_blocked_on_protected_endpoint(self) -> None:
        response = self.client.get(
            "/api/v1/memories",
            headers=self._headers(user_id="user-suspended", account_status="suspended"),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_canceled_account_blocked_on_protected_endpoint(self) -> None:
        response = self.client.get(
            "/api/v1/memories",
            headers=self._headers(user_id="user-canceled", account_status="canceled"),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_admin_and_author_are_billing_exempt_in_settings(self) -> None:
        admin_response = self.client.get(
            "/api/v1/me/settings",
            headers=self._headers(user_id="admin-settings", role="admin", mfa_enabled=True),
        )
        author_response = self.client.get(
            "/api/v1/me/settings",
            headers=self._headers(user_id="author-settings", role="author", mfa_enabled=True),
        )

        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(author_response.status_code, 200)

        admin_payload = admin_response.json()
        author_payload = author_response.json()
        self.assertTrue(admin_payload["billing_exempt"])
        self.assertTrue(author_payload["billing_exempt"])
        self.assertEqual(admin_payload["subscription_plan"], "premium")
        self.assertEqual(author_payload["subscription_plan"], "premium")
        self.assertFalse(admin_payload["payment_methods_enabled"])
        self.assertFalse(author_payload["payment_methods_enabled"])


if __name__ == "__main__":
    unittest.main()
