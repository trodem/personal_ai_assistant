import json
import sys
import urllib.request
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token


class ApiBackwardCompatibilityTests(unittest.TestCase):
    def test_only_v1_api_paths_are_published(self) -> None:
        with urllib.request.urlopen("http://localhost:8000/openapi.json", timeout=5) as response:
            self.assertEqual(response.status, 200)
            schema = json.loads(response.read().decode("utf-8"))

        api_paths = [path for path in schema["paths"].keys() if path.startswith("/api/")]
        self.assertTrue(api_paths, "No /api paths were found in OpenAPI schema.")
        self.assertTrue(all(path.startswith("/api/v1/") for path in api_paths))

    def test_memories_response_keeps_previous_required_fields(self) -> None:
        token = build_dev_token("user-alpha", tenant_id="tenant-a")
        request = urllib.request.Request("http://localhost:8000/api/v1/memories")
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("x-tenant-id", "tenant-a")

        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(response.status, 200)
            payload = json.loads(response.read().decode("utf-8"))

        self.assertIn("items", payload)
        self.assertTrue(len(payload["items"]) > 0)
        required_fields_for_previous_clients = {
            "id",
            "memory_type",
            "raw_text",
            "structured_data",
            "created_at",
        }
        self.assertTrue(required_fields_for_previous_clients.issubset(set(payload["items"][0].keys())))

    def test_admin_users_response_keeps_previous_required_fields(self) -> None:
        token = build_dev_token("admin-1", tenant_id="tenant-a", role="admin", mfa_enabled=True)
        request = urllib.request.Request("http://localhost:8000/api/v1/admin/users")
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("x-tenant-id", "tenant-a")

        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(response.status, 200)
            payload = json.loads(response.read().decode("utf-8"))

        self.assertIn("items", payload)
        self.assertTrue(len(payload["items"]) > 0)
        required_fields_for_previous_clients = {"id", "role"}
        self.assertTrue(required_fields_for_previous_clients.issubset(set(payload["items"][0].keys())))


if __name__ == "__main__":
    unittest.main()
