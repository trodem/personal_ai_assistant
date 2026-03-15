import sys
import unittest
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class DataExportEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        user_token = build_dev_token(f"user-export-{uuid4()}", tenant_id="tenant-a", role="user")
        self.user_headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": "tenant-a"}

    def test_start_data_export_job(self) -> None:
        response = self.client.post(
            "/api/v1/me/data-export",
            headers=self.user_headers,
            json={"format": "json"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "queued")
        UUID(payload["job_id"])

    def test_start_data_export_requires_authentication(self) -> None:
        response = self.client.post("/api/v1/me/data-export", json={"format": "csv"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_start_data_export_rejects_invalid_format(self) -> None:
        response = self.client.post(
            "/api/v1/me/data-export",
            headers=self.user_headers,
            json={"format": "xml"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.missing_required_fields")


if __name__ == "__main__":
    unittest.main()
