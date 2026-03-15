import json
import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QueryContractAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.tenant_id = f"tenant-query-contract-{uuid4()}"
        self.user_id = f"user-query-contract-{uuid4()}"
        token = build_dev_token(self.user_id, tenant_id=self.tenant_id, role="user")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": self.tenant_id}

    def _save_expense(self, amount: float, item: str, currency: str = "CHF") -> str:
        response = self.client.post(
            "/api/v1/memory",
            headers=self.headers,
            json={
                "memory_type": "expense_event",
                "raw_text": f"I bought {item} for {amount} {currency}",
                "structured_data": {"item": item, "amount": amount, "currency": currency},
                "confirmed": True,
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["id"]

    def _parse_sse(self, raw: str) -> list[tuple[str, dict[str, object]]]:
        events: list[tuple[str, dict[str, object]]] = []
        chunks = [part.strip() for part in raw.split("\n\n") if part.strip()]
        for chunk in chunks:
            lines = chunk.splitlines()
            event_name = ""
            data_payload = "{}"
            for line in lines:
                if line.startswith("event: "):
                    event_name = line[len("event: ") :]
                if line.startswith("data: "):
                    data_payload = line[len("data: ") :]
            events.append((event_name, json.loads(data_payload)))
        return events

    def test_ambiguous_last_query_returns_contract_error(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What was my last?"},
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "query.ambiguous_intent")

    def test_latest_query_uses_single_latest_source(self) -> None:
        self._save_expense(9.0, "coffee")
        latest_id = self._save_expense(19.0, "service")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much was my last service?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["source_memory_ids"], [latest_id])
        self.assertIn("19.00 CHF", payload["answer"])

    def test_multi_currency_totals_are_not_silently_converted(self) -> None:
        self._save_expense(10.0, "milk", "CHF")
        self._save_expense(25.5, "shoes", "EUR")

        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("10.00 CHF", payload["answer"])
        self.assertIn("25.50 EUR", payload["answer"])
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["source_memory_ids"]), 2)

    def test_no_result_returns_add_memory_suggestion(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])
        self.assertIn("add memory", payload["answer"].lower())

    def test_out_of_scope_query_returns_boundary_message(self) -> None:
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "What is the weather tomorrow?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["confidence"], "low")
        self.assertEqual(payload["source_memory_ids"], [])
        self.assertIn("outside mvp scope", payload["answer"].lower())

    def test_answer_language_fallback_uses_english_for_unsupported_preference(self) -> None:
        update = self.client.patch(
            "/api/v1/me/settings/profile",
            headers=self.headers,
            json={"preferred_language": "fr"},
        )
        self.assertEqual(update.status_code, 422)

        self._save_expense(7.0, "bread")
        response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("you spent", payload["answer"].lower())

    def test_stream_done_event_includes_confidence_and_sources(self) -> None:
        self._save_expense(12.0, "repair")
        response = self.client.post(
            "/api/v1/question/stream",
            headers=self.headers,
            json={"question": "How much was my last service?"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.text.strip())

        events = self._parse_sse(response.text)
        self.assertGreaterEqual(len(events), 2)
        self.assertEqual(events[-1][0], "done")
        self.assertIn("confidence", events[-1][1])
        self.assertIn("source_memory_ids", events[-1][1])


if __name__ == "__main__":
    unittest.main()
