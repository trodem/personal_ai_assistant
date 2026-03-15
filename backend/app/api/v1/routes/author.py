from typing import Literal, cast

from fastapi import APIRouter, Depends
from starlette import status

from app.api.schemas import AdminUserResponse, AuthorDashboardResponse, UpdateUserRoleRequest
from app.core.auth import AuthenticatedUser, enforce_mfa_policy_for_role, get_current_user
from app.core.errors import AppError
from app.repositories.admin_user_repository import (
    AdminUserRecord,
    count_active_authors_for_tenant,
    list_admin_users_for_tenant,
    update_admin_user_role,
    upsert_admin_user,
)
from app.services.author_dashboard import build_author_dashboard

router = APIRouter(prefix="/api/v1/author", tags=["Author"])


def _ensure_author(current_user: AuthenticatedUser) -> None:
    if current_user.role != "author":
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Author role required.",
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


@router.patch(
    "/users/{id}/role",
    summary="Update user role (author only)",
    description=(
        "Author can promote/demote between user and admin. "
        "Self-role change is forbidden and last active author must be preserved."
    ),
    response_model=AdminUserResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Author role required or self-role-change attempt."},
        422: {"description": "Validation error or last active author protection."},
    },
)
async def update_user_role(
    id: str,
    payload: UpdateUserRoleRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AdminUserResponse:
    _ensure_author(current_user)
    upsert_admin_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        role=current_user.role,
        status=current_user.status,
    )

    if id == current_user.user_id:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Author cannot change own role.",
        )

    target_before = upsert_admin_user(
        tenant_id=current_user.tenant_id,
        user_id=id,
    )
    if target_before["role"] == "author" and payload.role in {"user", "admin"}:
        if count_active_authors_for_tenant(tenant_id=current_user.tenant_id) <= 1:
            raise AppError(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="auth.last_active_author_required",
                message="Operation would remove the last active author.",
            )

    updated = update_admin_user_role(
        tenant_id=current_user.tenant_id,
        user_id=id,
        role=payload.role,
    )
    return _to_admin_response(updated)


@router.get(
    "/dashboard",
    summary="Global supervision dashboard (author only)",
    description="Returns author-level global supervision metrics for the current tenant.",
    response_model=AuthorDashboardResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Author role required."},
    },
)
async def get_author_dashboard(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthorDashboardResponse:
    _ensure_author(current_user)
    upsert_admin_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        role=current_user.role,
        status=current_user.status,
    )
    records = list_admin_users_for_tenant(tenant_id=current_user.tenant_id)
    return build_author_dashboard(records)
