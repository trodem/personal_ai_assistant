import json
import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app


class QuestionStreamingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = build_dev_token(f"user-question-stream-{uuid4()}", tenant_id="tenant-a")
        self.headers = {"Authorization": f"Bearer {self.token}", "x-tenant-id": "tenant-a"}

    def _save_expense(self, amount: float, item: str, currency: str = "CHF") -> None:
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

    def _parse_sse_events(self, response_text: str) -> list[tuple[str, dict[str, object]]]:
        events = [event for event in response_text.split("\n\n") if event.strip()]
        parsed: list[tuple[str, dict[str, object]]] = []
        for event_blob in events:
            lines = event_blob.splitlines()
            event_name = lines[0].replace("event: ", "", 1).strip()
            data_json = lines[1].replace("data: ", "", 1).strip()
            parsed.append((event_name, json.loads(data_json)))
        return parsed

    def test_stream_endpoint_emits_chunk_events_then_done(self) -> None:
        self._save_expense(12.0, "milk")
        self._save_expense(5.5, "bread")

        response = self.client.post(
            "/api/v1/question/stream",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/event-stream"))

        parsed = self._parse_sse_events(response.text)
        self.assertGreaterEqual(len(parsed), 2)

        self.assertEqual(parsed[-1][0], "done")
        self.assertIn("confidence", parsed[-1][1])
        self.assertIn("source_memory_ids", parsed[-1][1])
        for name, payload in parsed[:-1]:
            self.assertEqual(name, "chunk")
            self.assertIn("text", payload)

    def test_stream_chunk_order_reconstructs_same_answer_as_non_stream(self) -> None:
        self._save_expense(8.0, "eggs")
        self._save_expense(2.0, "coffee")

        stream_response = self.client.post(
            "/api/v1/question/stream",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(stream_response.status_code, 200)
        parsed = self._parse_sse_events(stream_response.text)
        self.assertGreaterEqual(len(parsed), 2)

        done_events = [event for event in parsed if event[0] == "done"]
        self.assertEqual(len(done_events), 1)
        self.assertEqual(parsed[-1][0], "done")

        chunk_text = "".join(str(payload["text"]) for name, payload in parsed if name == "chunk")
        non_stream_response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(non_stream_response.status_code, 200)
        self.assertEqual(chunk_text, non_stream_response.json()["answer"])

    def test_stream_endpoint_returns_503_when_streaming_disabled(self) -> None:
        headers = dict(self.headers)
        headers["x-stream-disabled"] = "true"
        response = self.client.post(
            "/api/v1/question/stream",
            headers=headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "ai.provider_unavailable")

    def test_stream_failure_supports_fallback_to_non_stream_endpoint(self) -> None:
        self._save_expense(3.0, "bread")
        headers = dict(self.headers)
        headers["x-stream-disabled"] = "true"
        stream_response = self.client.post(
            "/api/v1/question/stream",
            headers=headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(stream_response.status_code, 503)
        self.assertEqual(stream_response.json()["error"]["code"], "ai.provider_unavailable")

        fallback_response = self.client.post(
            "/api/v1/question",
            headers=self.headers,
            json={"question": "How much did I spend?"},
        )
        self.assertEqual(fallback_response.status_code, 200)
        self.assertIn("answer", fallback_response.json())


if __name__ == "__main__":
    unittest.main()
