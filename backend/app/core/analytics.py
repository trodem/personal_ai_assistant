import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.request_context import request_id_ctx_var, trace_id_ctx_var, user_id_ctx_var
from app.core.settings import get_settings


logger = logging.getLogger(__name__)

SNAKE_CASE_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

REQUIRED_COMMON_FIELDS = (
    "event_name",
    "event_version",
    "event_id",
    "occurred_at",
    "user_id",
    "session_id",
    "platform",
    "app_version",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_event(
    *,
    event_name: str,
    session_id: str,
    user_id: str | None,
    event_version: int = 1,
    extra_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not SNAKE_CASE_PATTERN.match(event_name):
        raise ValueError(f"Event name must be snake_case: {event_name}")

    payload: dict[str, Any] = {
        "event_name": event_name,
        "event_version": event_version,
        "event_id": str(uuid.uuid4()),
        "occurred_at": _utc_now_iso(),
        "user_id": user_id,
        "session_id": session_id,
        "platform": "backend",
        "app_version": get_settings().app_version,
        "request_id": request_id_ctx_var.get(),
        "trace_id": trace_id_ctx_var.get(),
    }
    if extra_payload:
        payload.update(extra_payload)
    return payload


def validate_event_schema(event: dict[str, Any]) -> bool:
    for field in REQUIRED_COMMON_FIELDS:
        if field not in event:
            return False
    if not isinstance(event.get("event_version"), int):
        return False
    if event.get("platform") != "backend":
        return False
    if not SNAKE_CASE_PATTERN.match(str(event.get("event_name", ""))):
        return False
    return True


def emit_operational_event(
    *,
    event_name: str,
    session_id: str,
    status_code: int,
    path: str,
) -> None:
    user = user_id_ctx_var.get()
    user_value = None if user == "-" else user
    event = build_event(
        event_name=event_name,
        session_id=session_id,
        user_id=user_value,
        extra_payload={"status_code": status_code, "path": path},
    )
    if not validate_event_schema(event):
        logger.warning("invalid_analytics_event_schema", extra={"event_name": event_name})
        return
    logger.info("analytics_event", extra={"analytics_event": event})
