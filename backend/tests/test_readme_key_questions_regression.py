import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class ReadmeKeyQuestionsRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-readme-reg-{uuid4()}"
        token = build_dev_token(f"user-readme-reg-{uuid4()}", tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def _save_memory(self, *, memory_type: str, raw_text: str, structured_data: dict[str, object]) -> str:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": memory_type,
                "raw_text": raw_text,
                "structured_data": structured_data,
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["id"]

    def test_key_questions_from_readme_are_regression_covered(self) -> None:
        last_year = datetime.now(timezone.utc).replace(
            year=datetime.now(timezone.utc).year - 1,
            month=5,
            day=10,
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        self._save_memory(
            memory_type="expense_event",
            raw_text="I spent 150 francs on the motorcycle: chain, oil and maintenance.",
            structured_data={
                "item": "motorcycle",
                "amount": 150.0,
                "currency": "CHF",
                "when": last_year.isoformat(),
            },
        )
        self._save_memory(
            memory_type="loan_event",
            raw_text="I lent money to Marco.",
            structured_data={
                "person": "Marco",
                "amount": 80.0,
                "currency": "CHF",
                "action": "lend",
            },
        )
        self._save_memory(
            memory_type="note",
            raw_text="I bought shoes in Rome and paid 25 francs.",
            structured_data={"content": "I bought shoes in Rome and paid 25 francs.", "where": "Rome"},
        )
        self._save_memory(
            memory_type="inventory_event",
            raw_text="I stored four boxes of peas in the cellar.",
            structured_data={"item": "peas", "quantity": 4, "action": "add", "where": "cellar"},
        )

        q1 = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend on the motorcycle last year?"},
        )
        self.assertEqual(q1.status_code, 200)
        p1 = q1.json()
        self.assertIn("150.00 CHF", p1["answer"])
        self.assertEqual(p1["confidence"], "high")
        self.assertTrue(p1["source_memory_ids"])

        q2 = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What did I buy in Rome?"},
        )
        self.assertEqual(q2.status_code, 200)
        p2 = q2.json()
        self.assertIn("rome", p2["answer"].lower())
        self.assertIn(p2["confidence"], {"medium", "high"})
        self.assertTrue(p2["source_memory_ids"])

        q3 = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "Who owes me money?"},
        )
        self.assertEqual(q3.status_code, 200)
        p3 = q3.json()
        self.assertIn("marco", p3["answer"].lower())
        self.assertIn("owes", p3["answer"].lower())
        self.assertEqual(p3["confidence"], "high")
        self.assertTrue(p3["source_memory_ids"])

        q4 = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What did I store in the cellar?"},
        )
        self.assertEqual(q4.status_code, 200)
        p4 = q4.json()
        self.assertIn("peas", p4["answer"].lower())
        self.assertIn("cellar", p4["answer"].lower())
        self.assertEqual(p4["confidence"], "high")
        self.assertTrue(p4["source_memory_ids"])


if __name__ == "__main__":
    unittest.main()
