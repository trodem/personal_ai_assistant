import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionInventoryStateQueriesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-inventory-state-{uuid4()}"
        token = build_dev_token(f"user-inventory-state-{uuid4()}", tenant_id=self.tenant_id)
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def _save_inventory(self, *, item: str, quantity: int, action: str, where: str) -> None:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "inventory_event",
                "raw_text": f"{action} {quantity} {item} in {where}",
                "structured_data": {
                    "item": item,
                    "quantity": quantity,
                    "action": action,
                    "where": where,
                },
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_inventory_state_from_add_remove_events(self) -> None:
        self._save_inventory(item="peas", quantity=4, action="add", where="cellar")
        self._save_inventory(item="peas", quantity=2, action="remove", where="cellar")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How many peas are left in the cellar?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("2 peas in cellar", payload["answer"].lower())
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["source_memory_ids"]), 2)

    def test_inventory_state_filters_location(self) -> None:
        self._save_inventory(item="peas", quantity=4, action="add", where="cellar")
        self._save_inventory(item="peas", quantity=3, action="add", where="garage")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How many peas are left in the cellar?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("4 peas in cellar", payload["answer"].lower())
        self.assertNotIn("garage", payload["answer"].lower())

    def test_inventory_state_no_result_fallback(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How many peas are left in the cellar?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])
        self.assertIn("add memory", payload["answer"].lower())


if __name__ == "__main__":
    unittest.main()
