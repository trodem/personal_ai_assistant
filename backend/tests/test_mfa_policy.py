import json
import sys
import urllib.error
import urllib.request
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token


class MfaPolicyTests(unittest.TestCase):
    def test_user_role_forbidden_on_admin_endpoint(self) -> None:
        token = build_dev_token("user-alpha", tenant_id="tenant-a")
        request = urllib.request.Request("http://localhost:8000/api/v1/admin/users")
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("x-tenant-id", "tenant-a")
        with self.assertRaises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(request, timeout=5)
        self.assertEqual(exc.exception.code, 403)
        payload = json.loads(exc.exception.read().decode("utf-8"))
        self.assertEqual(payload["error"]["code"], "auth.forbidden")

    def test_admin_without_mfa_is_blocked(self) -> None:
        token = build_dev_token("admin-1", tenant_id="tenant-a", role="admin", mfa_enabled=False)
        request = urllib.request.Request("http://localhost:8000/api/v1/admin/users")
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("x-tenant-id", "tenant-a")
        with self.assertRaises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(request, timeout=5)
        self.assertEqual(exc.exception.code, 403)
        payload = json.loads(exc.exception.read().decode("utf-8"))
        self.assertEqual(payload["error"]["code"], "auth.mfa_required")

    def test_admin_with_mfa_is_allowed(self) -> None:
        token = build_dev_token("admin-2", tenant_id="tenant-a", role="admin", mfa_enabled=True)

        request = urllib.request.Request("http://localhost:8000/api/v1/admin/users")
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("x-tenant-id", "tenant-a")
        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(response.status, 200)
            payload = json.loads(response.read().decode("utf-8"))
        self.assertIn("items", payload)


if __name__ == "__main__":
    unittest.main()
