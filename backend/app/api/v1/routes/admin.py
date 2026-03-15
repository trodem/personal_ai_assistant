from fastapi import APIRouter, Depends
from starlette import status

from app.api.schemas import AdminUsersListResponse
from app.core.auth import AuthenticatedUser, enforce_mfa_policy_for_role, get_current_user
from app.core.errors import AppError

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get(
    "/users",
    summary="List users (admin/author)",
    description="Returns user list for privileged roles. Admin and author roles require MFA enabled.",
    response_model=AdminUsersListResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Insufficient role, missing tenant context, or MFA required."},
    },
)
async def list_users(current_user: AuthenticatedUser = Depends(get_current_user)) -> AdminUsersListResponse:
    if current_user.role not in {"admin", "author"}:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Admin or Author role required.",
        )
    enforce_mfa_policy_for_role(current_user)

    return {"items": [{"id": current_user.user_id, "role": current_user.role}]}
