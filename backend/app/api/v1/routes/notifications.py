from fastapi import APIRouter, Depends, Query

from app.api.schemas import InAppNotificationsListResponse, UpdatedResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.notifications import (
    list_notifications_for_user,
    mark_notification_as_read_for_user,
)

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


@router.post(
    "/{id}/read",
    summary="Mark in-app notification as read",
    description="Marks a notification as read for the authenticated user.",
    response_model=UpdatedResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        404: {"description": "Notification not found."},
    },
)
async def mark_notification_as_read(
    id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UpdatedResponse:
    updated = mark_notification_as_read_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        notification_id=id,
    )
    if not updated:
        raise AppError(
            status_code=404,
            code="memory.not_found",
            message="Notification not found.",
        )
    return UpdatedResponse(updated=True)
