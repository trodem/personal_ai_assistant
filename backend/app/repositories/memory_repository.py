from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


MemoryRecord = dict[str, Any]

_MEMORY_RECORDS: list[MemoryRecord] = [
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-a",
        "user_id": "user-alpha",
        "memory_type": "note",
        "raw_text": "Private note for alpha",
        "structured_data": {"topic": "alpha"},
        "structured_data_schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-a",
        "user_id": "user-beta",
        "memory_type": "note",
        "raw_text": "Private note for beta",
        "structured_data": {"topic": "beta"},
        "structured_data_schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-b",
        "user_id": "user-alpha",
        "memory_type": "note",
        "raw_text": "Private note for alpha in tenant-b",
        "structured_data": {"topic": "alpha-tenant-b"},
        "structured_data_schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-default",
        "user_id": "user-alpha",
        "memory_type": "note",
        "raw_text": "Private note for alpha in default tenant",
        "structured_data": {"topic": "alpha-default"},
        "structured_data_schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
]


def _require_scope(*, tenant_id: str, user_id: str) -> None:
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required for repository queries")
    if not user_id or not user_id.strip():
        raise ValueError("user_id is required for repository queries")


def list_memories_for_user(*, tenant_id: str, user_id: str) -> list[MemoryRecord]:
    _require_scope(tenant_id=tenant_id, user_id=user_id)
    return [
        item
        for item in _MEMORY_RECORDS
        if item["tenant_id"] == tenant_id
        and item["user_id"] == user_id
        and item.get("deleted_at") is None
    ]


def insert_memory_record(record: MemoryRecord) -> None:
    _require_scope(tenant_id=str(record.get("tenant_id", "")), user_id=str(record.get("user_id", "")))
    record.setdefault("structured_data_schema_version", 1)
    _MEMORY_RECORDS.append(record)


def soft_delete_memory_for_user(*, tenant_id: str, user_id: str, memory_id: str) -> bool:
    _require_scope(tenant_id=tenant_id, user_id=user_id)
    if not memory_id or not memory_id.strip():
        raise ValueError("memory_id is required for repository queries")
    for item in _MEMORY_RECORDS:
        if (
            item.get("id") == memory_id
            and item.get("tenant_id") == tenant_id
            and item.get("user_id") == user_id
            and item.get("deleted_at") is None
        ):
            item["deleted_at"] = datetime.now(timezone.utc).isoformat()
            return True
    return False
