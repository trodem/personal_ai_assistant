import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class MfaRolePolicyEnforcementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def _headers(
        self,
        *,
        role: str,
        mfa_enabled: bool,
        tenant_id: str,
        user_id: str,
    ) -> dict[str, str]:
        token = build_dev_token(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            mfa_enabled=mfa_enabled,
        )
        return {"Authorization": f"Bearer {token}", "x-tenant-id": tenant_id}

    def test_admin_cannot_disable_2fa(self) -> None:
        tenant_id = f"tenant-admin-mfa-{uuid4()}"
        headers = self._headers(
            role="admin",
            mfa_enabled=True,
            tenant_id=tenant_id,
            user_id=f"admin-disable-{uuid4()}",
        )
        response = self.client.patch(
            "/api/v1/me/settings/security",
            headers=headers,
            json={"action": "disable_2fa"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.mfa_required")

    def test_author_cannot_disable_2fa(self) -> None:
        tenant_id = f"tenant-author-mfa-{uuid4()}"
        headers = self._headers(
            role="author",
            mfa_enabled=True,
            tenant_id=tenant_id,
            user_id=f"author-disable-{uuid4()}",
        )
        response = self.client.patch(
            "/api/v1/me/settings/security",
            headers=headers,
            json={"action": "disable_2fa"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "auth.mfa_required")

    def test_user_can_access_normal_endpoint_without_2fa(self) -> None:
        tenant_id = f"tenant-user-mfa-{uuid4()}"
        headers = self._headers(
            role="user",
            mfa_enabled=False,
            tenant_id=tenant_id,
            user_id=f"user-no-mfa-{uuid4()}",
        )
        response = self.client.get("/api/v1/memories", headers=headers)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()

