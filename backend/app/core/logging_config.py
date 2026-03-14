import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from app.core.request_context import request_id_ctx_var, tenant_id_ctx_var, trace_id_ctx_var, user_id_ctx_var
from app.core.settings import get_settings


class JsonFormatter(logging.Formatter):
    RESERVED_FIELDS = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
    }
    SENSITIVE_KEY_HINTS = (
        "password",
        "secret",
        "token",
        "authorization",
        "api_key",
        "apikey",
        "cookie",
        "session",
    )
    BEARER_PATTERN = re.compile(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*")
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

    def _looks_sensitive_key(self, key: str | None) -> bool:
        if not key:
            return False
        lowered = key.lower()
        return any(hint in lowered for hint in self.SENSITIVE_KEY_HINTS)

    def _sanitize_string(self, value: str, key: str | None) -> str:
        if self._looks_sensitive_key(key):
            return "[REDACTED]"
        if self.BEARER_PATTERN.search(value):
            return self.BEARER_PATTERN.sub("Bearer [REDACTED]", value)
        if self.EMAIL_PATTERN.search(value):
            return self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)
        return value

    def _sanitize(self, value: Any, key: str | None = None) -> Any:
        if self._looks_sensitive_key(key):
            return "[REDACTED]"
        if isinstance(value, dict):
            return {k: self._sanitize(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [self._sanitize(item, key) for item in value]
        if isinstance(value, tuple):
            return tuple(self._sanitize(item, key) for item in value)
        if isinstance(value, str):
            return self._sanitize_string(value, key)
        return value

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx_var.get(),
            "trace_id": trace_id_ctx_var.get(),
            "user_id": user_id_ctx_var.get(),
            "tenant_id": tenant_id_ctx_var.get(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extra_payload = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self.RESERVED_FIELDS and not key.startswith("_")
        }
        if extra_payload:
            payload.update(extra_payload)
        sanitized_payload = self._sanitize(payload)
        return json.dumps(sanitized_payload, ensure_ascii=True)


def configure_logging() -> None:
    level_name = get_settings().log_level
    level = getattr(logging, level_name, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
