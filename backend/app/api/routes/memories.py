from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/api/v1", tags=["Memory"])

_MEMORY_FIXTURES = [
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-a",
        "user_id": "user-alpha",
        "memory_type": "note",
        "raw_text": "Private note for alpha",
        "structured_data": {"topic": "alpha"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-a",
        "user_id": "user-beta",
        "memory_type": "note",
        "raw_text": "Private note for beta",
        "structured_data": {"topic": "beta"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-b",
        "user_id": "user-alpha",
        "memory_type": "note",
        "raw_text": "Private note for alpha in tenant-b",
        "structured_data": {"topic": "alpha-tenant-b"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid4()),
        "tenant_id": "tenant-default",
        "user_id": "user-alpha",
        "memory_type": "note",
        "raw_text": "Private note for alpha in default tenant",
        "structured_data": {"topic": "alpha-default"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
]


@router.get("/memories")
async def list_memories(current_user: AuthenticatedUser = Depends(get_current_user)) -> dict[str, list[dict[str, object]]]:
    items = [
        {
            "id": item["id"],
            "memory_type": item["memory_type"],
            "raw_text": item["raw_text"],
            "structured_data": item["structured_data"],
            "created_at": item["created_at"],
        }
        for item in _MEMORY_FIXTURES
        if item["user_id"] == current_user.user_id and item["tenant_id"] == current_user.tenant_id
    ]
    return {"items": items}
