from fastapi import APIRouter, Depends

from app.api.schemas import ApplyCouponRequest, UserSettingsResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.coupons import apply_coupon_for_user
from app.services.user_settings_view import build_user_settings_response

router = APIRouter(prefix="/api/v1/billing/coupons", tags=["Billing"])


@router.post(
    "/apply",
    summary="Apply coupon code",
    description="Applies an eligible coupon for the authenticated user.",
    response_model=UserSettingsResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Not eligible or role-locked policy."},
        422: {"description": "Validation error."},
    },
)
async def apply_coupon(
    payload: ApplyCouponRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserSettingsResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Coupon application is unavailable for billing-exempt roles.",
        )
    accepted = apply_coupon_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        code=payload.code,
    )
    if not accepted:
        raise AppError(
            status_code=422,
            code="billing.coupon_invalid",
            message="Coupon code is invalid or not eligible.",
        )
    return build_user_settings_response(current_user)
