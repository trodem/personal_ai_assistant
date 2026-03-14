import unittest
from pathlib import Path
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.services.attachments import get_attachment


class AttachmentFlowE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.user_id = f"user-attachment-e2e-{uuid4()}"
        self.token = build_dev_token(self.user_id, tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": "tenant-a"}

    def test_receipt_upload_to_confirmed_persistence_with_authorized_signed_url(self) -> None:
        upload = self.client.post(
            "/api/v1/attachments",
            headers=self.headers,
            files={"file": ("receipt.jpg", b"I bought bread for 3 chf", "image/jpeg")},
        )
        self.assertEqual(upload.status_code, 200)
        attachment_payload = upload.json()
        self.assertEqual(attachment_payload["status"], "proposal_ready")
        self.assertEqual(attachment_payload["ocr_status"], "completed")
        self.assertIn("memory_proposal", attachment_payload)
        self.assertEqual(attachment_payload["memory_proposal"]["memory_type"], "expense_event")
        signed_url = attachment_payload["file_url"]

        tampered_url = signed_url.replace("sig=", "sig=tampered")
        rejected = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "Receipt memory",
                "structured_data": {"item": "bread", "amount": 3.0, "attachment_url": tampered_url},
                "confirmed": True,
            },
        )
        self.assertEqual(rejected.status_code, 403)
        self.assertEqual(rejected.json()["error"]["code"], "auth.forbidden")

        accepted = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": "Receipt memory",
                "structured_data": {"item": "bread", "amount": 3.0, "attachment_url": signed_url},
                "confirmed": True,
            },
        )
        self.assertEqual(accepted.status_code, 200)
        saved = accepted.json()
        attachment_id = saved["structured_data"]["attachment_id"]
        self.assertTrue(attachment_id)

        persisted_attachment = get_attachment(attachment_id)
        self.assertIsNotNone(persisted_attachment)
        self.assertEqual(persisted_attachment.status, "persisted")

    def test_attachment_rejects_pdf_and_non_images(self) -> None:
        upload = self.client.post(
            "/api/v1/attachments",
            headers=self.headers,
            files={"file": ("receipt.pdf", b"%PDF", "application/pdf")},
        )
        self.assertEqual(upload.status_code, 422)
        self.assertEqual(upload.json()["error"]["code"], "storage.unsupported_file_type")


if __name__ == "__main__":
    unittest.main()
