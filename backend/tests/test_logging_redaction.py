import json
import logging
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.logging_config import JsonFormatter


class LoggingRedactionTests(unittest.TestCase):
    def test_sensitive_extra_fields_are_redacted(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="processing request",
            args=(),
            exc_info=None,
        )
        record.authorization = "Bearer very-secret-token"
        record.user_email = "john@example.com"
        record.payload = {"api_key": "top-secret", "nested": {"password": "pw"}}

        output = formatter.format(record)
        payload = json.loads(output)

        self.assertEqual(payload["authorization"], "[REDACTED]")
        self.assertEqual(payload["user_email"], "[REDACTED_EMAIL]")
        self.assertEqual(payload["payload"]["api_key"], "[REDACTED]")
        self.assertEqual(payload["payload"]["nested"]["password"], "[REDACTED]")

    def test_message_bearer_token_is_redacted(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=25,
            msg="Authorization: Bearer abc.def.ghi",
            args=(),
            exc_info=None,
        )
        payload = json.loads(formatter.format(record))
        self.assertIn("Bearer [REDACTED]", payload["message"])


if __name__ == "__main__":
    unittest.main()
