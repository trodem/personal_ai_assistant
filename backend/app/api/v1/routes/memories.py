from fastapi import APIRouter, Depends
from starlette import status

from app.api.schemas import DeleteMemoryResponse, MemoryListResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.repositories.memory_repository import list_memories_for_user, soft_delete_memory_for_user
from app.services.semantic_cache import invalidate_user_cache

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


@router.delete(
    "/memory/{id}",
    summary="Delete memory",
    description="Soft-deletes a memory record scoped to the authenticated user and tenant.",
    response_model=DeleteMemoryResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        404: {"description": "Memory not found."},
    },
)
async def delete_memory(
    id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DeleteMemoryResponse:
    deleted = soft_delete_memory_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        memory_id=id,
    )
    if not deleted:
        raise AppError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="memory.not_found",
            message="Memory not found.",
        )
    invalidate_user_cache(current_user.tenant_id, current_user.user_id)
    return DeleteMemoryResponse(deleted=True)
