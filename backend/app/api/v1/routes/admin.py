from typing import Literal, cast

from fastapi import APIRouter, Depends
from starlette import status

from app.api.schemas import AdminUserResponse, AdminUsersListResponse, UpdateUserStatusRequest
from app.core.auth import AuthenticatedUser, enforce_mfa_policy_for_role, get_current_user
from app.core.errors import AppError
from app.repositories.admin_user_repository import (
    AdminUserRecord,
    list_admin_users_for_tenant,
    update_admin_user_status,
    upsert_admin_user,
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


def _ensure_admin_or_author(current_user: AuthenticatedUser) -> None:
    if current_user.role not in {"admin", "author"}:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Admin or Author role required.",
        )
    enforce_mfa_policy_for_role(current_user)


def _to_admin_response(record: AdminUserRecord) -> AdminUserResponse:
    role: Literal["user", "admin", "author"] = cast(
        Literal["user", "admin", "author"],
        record["role"],
    )
    user_status: Literal["active", "suspended", "canceled"] = cast(
        Literal["active", "suspended", "canceled"],
        record["status"],
    )
    subscription_plan: Literal["free", "premium"] = cast(
        Literal["free", "premium"],
        record["subscription_plan"],
    )
    return AdminUserResponse(
        id=record["id"],
        email=record["email"],
        role=role,
        status=user_status,
        subscription_plan=subscription_plan,
        billing_exempt=record["billing_exempt"],
    )


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
    _ensure_admin_or_author(current_user)
    upsert_admin_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        role=current_user.role,
        status=current_user.status,
    )
    records = list_admin_users_for_tenant(tenant_id=current_user.tenant_id)
    return AdminUsersListResponse(items=[_to_admin_response(item) for item in records])


@router.patch(
    "/users/{id}/status",
    summary="Update user status (admin/author)",
    description="Allows admin/author to update account status: active, suspended, or canceled.",
    response_model=AdminUserResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Admin/author role and MFA are required."},
        422: {"description": "Validation error."},
    },
)
async def update_user_status(
    id: str,
    payload: UpdateUserStatusRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AdminUserResponse:
    _ensure_admin_or_author(current_user)
    record = update_admin_user_status(
        tenant_id=current_user.tenant_id,
        user_id=id,
        status=payload.status,
    )
    return _to_admin_response(record)
