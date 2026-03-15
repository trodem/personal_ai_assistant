from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


EmbeddingRecord = dict[str, Any]

_EMBEDDING_RECORDS: list[EmbeddingRecord] = []


def _require_scope(*, tenant_id: str, user_id: str) -> None:
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required for embedding repository queries")
    if not user_id or not user_id.strip():
        raise ValueError("user_id is required for embedding repository queries")


def insert_embedding_record(record: EmbeddingRecord) -> EmbeddingRecord:
    tenant_id = str(record.get("tenant_id", ""))
    user_id = str(record.get("user_id", ""))
    _require_scope(tenant_id=tenant_id, user_id=user_id)
    record.setdefault("id", str(uuid4()))
    record.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    _EMBEDDING_RECORDS.append(record)
    return record


def list_embeddings_for_user(*, tenant_id: str, user_id: str) -> list[EmbeddingRecord]:
    _require_scope(tenant_id=tenant_id, user_id=user_id)
    return [
        item
        for item in _EMBEDDING_RECORDS
        if item.get("tenant_id") == tenant_id and item.get("user_id") == user_id
    ]
