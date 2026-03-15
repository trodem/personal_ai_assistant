from fastapi import APIRouter, Depends

from app.api.schemas import DashboardResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.repositories.memory_repository import list_memories_for_user
from app.services.dashboard import build_dashboard_response

router = APIRouter(prefix="/api/v1", tags=["Dashboard"])


@router.get(
    "/dashboard",
    summary="Dashboard statistics",
    description="Returns user-scoped dashboard metrics derived from stored memories.",
    response_model=DashboardResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def get_dashboard(current_user: AuthenticatedUser = Depends(get_current_user)) -> DashboardResponse:
    scoped_memories = list_memories_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )
    return build_dashboard_response(scoped_memories)
