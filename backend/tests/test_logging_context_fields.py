import json
import logging
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.logging_config import JsonFormatter
from app.core.request_context import request_id_ctx_var, tenant_id_ctx_var, trace_id_ctx_var, user_id_ctx_var


class LoggingContextFieldTests(unittest.TestCase):
    def test_formatter_includes_request_and_user_context(self) -> None:
        formatter = JsonFormatter()

        req_token = request_id_ctx_var.set("req-123")
        trace_token = trace_id_ctx_var.set("trace-123")
        user_token = user_id_ctx_var.set("user-123")
        tenant_token = tenant_id_ctx_var.set("tenant-123")
        try:
            record = logging.LogRecord(
                name="test.logger",
                level=logging.INFO,
                pathname=__file__,
                lineno=25,
                msg="request complete",
                args=(),
                exc_info=None,
            )
            payload = json.loads(formatter.format(record))
            self.assertEqual(payload["request_id"], "req-123")
            self.assertEqual(payload["trace_id"], "trace-123")
            self.assertEqual(payload["user_id"], "user-123")
            self.assertEqual(payload["tenant_id"], "tenant-123")
        finally:
            request_id_ctx_var.reset(req_token)
            trace_id_ctx_var.reset(trace_token)
            user_id_ctx_var.reset(user_token)
            tenant_id_ctx_var.reset(tenant_token)

    def test_formatter_uses_default_user_placeholder_when_missing(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=47,
            msg="request complete",
            args=(),
            exc_info=None,
        )
        payload = json.loads(formatter.format(record))
        self.assertEqual(payload["user_id"], "-")


if __name__ == "__main__":
    unittest.main()
