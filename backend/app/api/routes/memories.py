from fastapi import APIRouter, Depends

from app.api.schemas import MemoryListResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.repositories.memory_repository import list_memories_for_user

router = APIRouter(prefix="/api/v1", tags=["Memory"])

@router.get(
    "/memories",
    summary="List user memories",
    description="Returns only memories scoped to the authenticated user and tenant context.",
    response_model=MemoryListResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Missing tenant context or cross-tenant access attempt."},
    },
)
async def list_memories(current_user: AuthenticatedUser = Depends(get_current_user)) -> MemoryListResponse:
    scoped_memories = list_memories_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )
    items = [
        {
            "id": item["id"],
            "memory_type": item["memory_type"],
            "raw_text": item["raw_text"],
            "structured_data": item["structured_data"],
            "structured_data_schema_version": item.get("structured_data_schema_version", 1),
            "created_at": item["created_at"],
        }
        for item in scoped_memories
    ]
    return {"items": items}
