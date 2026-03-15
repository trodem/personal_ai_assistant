import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.repositories.admin_user_repository import get_admin_user_for_tenant


class NegativeAuthContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-negative-auth-{uuid4()}"

        self.user_id = f"user-negative-{uuid4()}"
        self.other_user_id = f"user-negative-other-{uuid4()}"
        self.admin_id = f"admin-negative-{uuid4()}"
        self.author_id = f"author-negative-{uuid4()}"

        user_token = build_dev_token(self.user_id, tenant_id=self.tenant_id, role="user")
        other_user_token = build_dev_token(self.other_user_id, tenant_id=self.tenant_id, role="user")
        admin_token = build_dev_token(
            self.admin_id,
            tenant_id=self.tenant_id,
            role="admin",
            mfa_enabled=True,
        )
        admin_no_mfa_token = build_dev_token(
            f"admin-no-mfa-{uuid4()}",
            tenant_id=self.tenant_id,
            role="admin",
            mfa_enabled=False,
        )
        author_token = build_dev_token(
            self.author_id,
            tenant_id=self.tenant_id,
            role="author",
            mfa_enabled=True,
        )

        self.user_headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": self.tenant_id}
        self.other_user_headers = {"Authorization": f"Bearer {other_user_token}", "x-tenant-id": self.tenant_id}
        self.admin_headers = {"Authorization": f"Bearer {admin_token}", "x-tenant-id": self.tenant_id}
        self.admin_no_mfa_headers = {"Authorization": f"Bearer {admin_no_mfa_token}", "x-tenant-id": self.tenant_id}
        self.author_headers = {"Authorization": f"Bearer {author_token}", "x-tenant-id": self.tenant_id}

    def _create_memory(self, headers: dict[str, str], item: str) -> str:
        response = self.client.post(
            "/api/v1/memory",
            headers=headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I bought {item} for 3 CHF",
                "structured_data": {"item": item, "amount": 3.0, "currency": "CHF"},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["id"]

    def test_missing_token_is_rejected(self) -> None:
        response = self.client.get("/api/v1/memories")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_expired_token_is_rejected(self) -> None:
        expired = build_dev_token(
            f"user-expired-{uuid4()}",
            tenant_id=self.tenant_id,
            role="user",
            ttl_seconds=-1,
        )
        response = self.client.get(
            "/api/v1/memories",
            headers={"Authorization": f"Bearer {expired}", "x-tenant-id": self.tenant_id},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.invalid_token")

    def test_missing_2fa_code_on_sensitive_security_action_is_rejected(self) -> None:
        start = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.user_headers,
            json={"action": "enable_2fa"},
        )
        self.assertEqual(start.status_code, 200)

        verify_without_code = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.user_headers,
            json={"action": "verify_2fa"},
        )
        self.assertEqual(verify_without_code.status_code, 422)
        self.assertEqual(verify_without_code.json()["error"]["code"], "memory.missing_required_fields")

    def test_invalid_2fa_code_on_sensitive_security_action_is_rejected(self) -> None:
        start = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.user_headers,
            json={"action": "enable_2fa"},
        )
        self.assertEqual(start.status_code, 200)

        verify_with_invalid_code = self.client.patch(
            "/api/v1/me/settings/security",
            headers=self.user_headers,
            json={"action": "verify_2fa", "totp_code": "000000"},
        )
        self.assertEqual(verify_with_invalid_code.status_code, 422)
        self.assertEqual(verify_with_invalid_code.json()["error"]["code"], "memory.validation_failed")

    def test_admin_with_2fa_disabled_is_blocked_on_privileged_access(self) -> None:
        response = self.client.get("/api/v1/admin/users", headers=self.admin_no_mfa_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.mfa_required")

    def test_cross_user_resource_access_is_rejected(self) -> None:
        memory_id = self._create_memory(self.user_headers, "tea")
        response = self.client.delete(f"/api/v1/memory/{memory_id}", headers=self.other_user_headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")

    def test_suspended_user_access_is_blocked(self) -> None:
        target_user_id = f"user-suspended-{uuid4()}"
        target_token = build_dev_token(target_user_id, tenant_id=self.tenant_id, role="user")
        target_headers = {"Authorization": f"Bearer {target_token}", "x-tenant-id": self.tenant_id}

        updated = self.client.patch(
            f"/api/v1/admin/users/{target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "suspended"},
        )
        self.assertEqual(updated.status_code, 200)

        blocked = self.client.get("/api/v1/memories", headers=target_headers)
        self.assertEqual(blocked.status_code, 403)
        self.assertEqual(blocked.json()["error"]["code"], "auth.forbidden")

    def test_canceled_user_access_is_blocked(self) -> None:
        target_user_id = f"user-canceled-{uuid4()}"
        target_token = build_dev_token(target_user_id, tenant_id=self.tenant_id, role="user")
        target_headers = {"Authorization": f"Bearer {target_token}", "x-tenant-id": self.tenant_id}

        updated = self.client.patch(
            f"/api/v1/admin/users/{target_user_id}/status",
            headers=self.admin_headers,
            json={"status": "canceled"},
        )
        self.assertEqual(updated.status_code, 200)

        blocked = self.client.get("/api/v1/memories", headers=target_headers)
        self.assertEqual(blocked.status_code, 403)
        self.assertEqual(blocked.json()["error"]["code"], "auth.forbidden")

    def test_non_admin_access_is_blocked_on_admin_routes(self) -> None:
        response = self.client.get("/api/v1/admin/users", headers=self.user_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_non_author_access_is_blocked_on_author_routes(self) -> None:
        response = self.client.get("/api/v1/author/dashboard", headers=self.admin_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_admin_cannot_change_roles(self) -> None:
        response = self.client.patch(
            f"/api/v1/author/users/{self.user_id}/role",
            headers=self.admin_headers,
            json={"role": "admin"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.forbidden")

    def test_role_change_to_admin_enforces_premium_and_billing_exemption(self) -> None:
        target_user_id = f"user-promoted-{uuid4()}"
        promoted = self.client.patch(
            f"/api/v1/author/users/{target_user_id}/role",
            headers=self.author_headers,
            json={"role": "admin"},
        )
        self.assertEqual(promoted.status_code, 200)
        payload = promoted.json()
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["subscription_plan"], "premium")
        self.assertTrue(payload["billing_exempt"])

    def test_role_assignment_to_author_enforces_premium_and_billing_exemption(self) -> None:
        author_only_id = f"author-provisioned-{uuid4()}"
        token = build_dev_token(
            author_only_id,
            tenant_id=self.tenant_id,
            role="author",
            mfa_enabled=True,
        )
        headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

        response = self.client.get("/api/v1/memories", headers=headers)
        self.assertEqual(response.status_code, 200)

        record = get_admin_user_for_tenant(tenant_id=self.tenant_id, user_id=author_only_id)
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record["role"], "author")
        self.assertEqual(record["subscription_plan"], "premium")
        self.assertTrue(record["billing_exempt"])


if __name__ == "__main__":
    unittest.main()
