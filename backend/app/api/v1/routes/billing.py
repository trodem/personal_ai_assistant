from fastapi import APIRouter, Depends

from app.api.schemas import (
    CancelPreviewRequest,
    CancelPreviewResponse,
    CancelSubscriptionRequest,
    ChangePlanRequest,
    UserSettingsResponse,
)
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.billing_retention import build_cancel_preview
from app.services.subscription_plans import set_subscription_plan_for_user
from app.services.user_settings_view import build_user_settings_response

router = APIRouter(prefix="/api/v1/billing/subscription", tags=["Billing"])


@router.post(
    "/change-plan",
    summary="Change user subscription plan",
    description="Allows `user` role to switch between free and premium plans.",
    response_model=UserSettingsResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Plan is locked by role policy."},
        422: {"description": "Validation error."},
    },
)
async def change_subscription_plan(
    payload: ChangePlanRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserSettingsResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Subscription plan is locked by role policy.",
        )
    set_subscription_plan_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        plan=payload.plan,
    )
    return build_user_settings_response(current_user)


@router.post(
    "/cancel-preview",
    summary="Preview cancellation outcomes and retention options",
    description="Returns cancellation impact and retention alternatives before final cancel.",
    response_model=CancelPreviewResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Plan is locked by role policy."},
        422: {"description": "Validation error."},
    },
)
async def cancel_subscription_preview(
    payload: CancelPreviewRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> CancelPreviewResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Subscription plan is locked by role policy.",
        )
    return build_cancel_preview(reason=payload.reason)


@router.post(
    "/cancel",
    summary="Cancel subscription",
    description="Cancels user subscription with mandatory reason capture.",
    response_model=UserSettingsResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Plan is locked by role policy."},
        422: {"description": "Validation error."},
    },
)
async def cancel_subscription(
    payload: CancelSubscriptionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserSettingsResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Subscription plan is locked by role policy.",
        )
    _ = payload
    set_subscription_plan_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        plan="free",
    )
    return build_user_settings_response(current_user)
