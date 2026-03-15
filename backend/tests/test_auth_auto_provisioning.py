import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.repositories.admin_user_repository import get_admin_user_for_tenant


class AuthAutoProvisioningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_first_authenticated_access_auto_provisions_user_record(self) -> None:
        tenant_id = f"tenant-auto-provision-{uuid4()}"
        user_id = f"user-auto-provision-{uuid4()}"
        token = build_dev_token(user_id=user_id, tenant_id=tenant_id, role="user")
        headers = {"Authorization": f"Bearer {token}", "x-tenant-id": tenant_id}

        before = get_admin_user_for_tenant(tenant_id=tenant_id, user_id=user_id)
        self.assertIsNone(before)

        response = self.client.get("/api/v1/memories", headers=headers)
        self.assertEqual(response.status_code, 200)

        after = get_admin_user_for_tenant(tenant_id=tenant_id, user_id=user_id)
        self.assertIsNotNone(after)
        assert after is not None
        self.assertEqual(after["role"], "user")
        self.assertEqual(after["status"], "active")
        self.assertEqual(after["subscription_plan"], "free")
        self.assertFalse(after["billing_exempt"])

    def test_single_tenant_token_auto_provisions_default_tenant_record(self) -> None:
        user_id = f"user-default-tenant-{uuid4()}"
        token = build_dev_token(user_id=user_id, tenant_id=None, role="user")
        headers = {"Authorization": f"Bearer {token}"}

        before = get_admin_user_for_tenant(tenant_id="tenant-default", user_id=user_id)
        self.assertIsNone(before)

        response = self.client.get("/api/v1/memories", headers=headers)
        self.assertEqual(response.status_code, 200)

        after = get_admin_user_for_tenant(tenant_id="tenant-default", user_id=user_id)
        self.assertIsNotNone(after)
        assert after is not None
        self.assertEqual(after["tenant_id"], "tenant-default")


if __name__ == "__main__":
    unittest.main()

