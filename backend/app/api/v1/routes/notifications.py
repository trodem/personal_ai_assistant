from fastapi import APIRouter, Depends, Query

from app.api.schemas import InAppNotificationsListResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.services.notifications import list_notifications_for_user

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get(
    "",
    summary="List in-app notifications",
    description="Returns in-app notifications for the authenticated user.",
    response_model=InAppNotificationsListResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def list_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> InAppNotificationsListResponse:
    items = list_notifications_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        unread_only=unread_only,
        limit=limit,
    )
    return InAppNotificationsListResponse(items=items)
