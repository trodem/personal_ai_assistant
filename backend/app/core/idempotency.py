import hashlib
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IdempotencyRecord:
    payload_hash: str
    response_payload: dict[str, Any]


_IDEMPOTENCY_STORE: dict[tuple[str, str, str, str], IdempotencyRecord] = {}


def build_payload_hash(payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_idempotency_record(
    *,
    tenant_id: str,
    user_id: str,
    path: str,
    idempotency_key: str,
) -> IdempotencyRecord | None:
    key = (tenant_id, user_id, path, idempotency_key)
    return _IDEMPOTENCY_STORE.get(key)


def save_idempotency_record(
    *,
    tenant_id: str,
    user_id: str,
    path: str,
    idempotency_key: str,
    payload_hash: str,
    response_payload: dict[str, Any],
) -> None:
    key = (tenant_id, user_id, path, idempotency_key)
    _IDEMPOTENCY_STORE[key] = IdempotencyRecord(
        payload_hash=payload_hash,
        response_payload=response_payload,
    )


def reset_idempotency_store() -> None:
    _IDEMPOTENCY_STORE.clear()
