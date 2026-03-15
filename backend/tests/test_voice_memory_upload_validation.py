import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.services.audio_upload import MAX_AUDIO_UPLOAD_BYTES


class VoiceMemoryUploadValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token("user-upload-validation", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_rejects_unsupported_audio_content_type(self) -> None:
        response = self.client.post(
            "/api/v1/voice/memory",
            headers=self.headers,
            files={"audio": ("note.txt", b"hello", "text/plain")},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "storage.unsupported_file_type")

    def test_rejects_empty_audio_payload(self) -> None:
        response = self.client.post(
            "/api/v1/voice/memory",
            headers=self.headers,
            files={"audio": ("empty.wav", b"", "audio/wav")},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.validation_failed")

    def test_rejects_audio_payload_over_size_limit(self) -> None:
        oversized = b"a" * (MAX_AUDIO_UPLOAD_BYTES + 1)
        response = self.client.post(
            "/api/v1/voice/memory",
            headers=self.headers,
            files={"audio": ("large.wav", oversized, "audio/wav")},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "memory.validation_failed")


if __name__ == "__main__":
    unittest.main()
