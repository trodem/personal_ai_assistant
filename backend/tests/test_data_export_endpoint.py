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
        other_user_token = build_dev_token(f"user-export-{uuid4()}", tenant_id="tenant-a", role="user")
        self.user_headers = {"Authorization": f"Bearer {user_token}", "x-tenant-id": "tenant-a"}
        self.other_user_headers = {"Authorization": f"Bearer {other_user_token}", "x-tenant-id": "tenant-a"}

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

    def test_get_data_export_status(self) -> None:
        created = self.client.post(
            "/api/v1/me/data-export",
            headers=self.user_headers,
            json={"format": "pdf"},
        )
        self.assertEqual(created.status_code, 200)
        job_id = created.json()["job_id"]

        response = self.client.get(
            f"/api/v1/me/data-export/{job_id}",
            headers=self.user_headers,
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["job_id"], job_id)
        self.assertEqual(payload["status"], "queued")
        self.assertIsNone(payload["download_url"])
        self.assertIsNone(payload["expires_at"])

    def test_get_data_export_status_requires_authentication(self) -> None:
        response = self.client.get(f"/api/v1/me/data-export/{uuid4()}")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_get_data_export_status_not_found(self) -> None:
        response = self.client.get(
            f"/api/v1/me/data-export/{uuid4()}",
            headers=self.user_headers,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")

    def test_get_data_export_status_is_user_scoped(self) -> None:
        created = self.client.post(
            "/api/v1/me/data-export",
            headers=self.user_headers,
            json={"format": "csv"},
        )
        self.assertEqual(created.status_code, 200)
        job_id = created.json()["job_id"]

        response = self.client.get(
            f"/api/v1/me/data-export/{job_id}",
            headers=self.other_user_headers,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")


if __name__ == "__main__":
    unittest.main()
