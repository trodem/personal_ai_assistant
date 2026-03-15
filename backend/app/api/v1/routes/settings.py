from fastapi import APIRouter, Depends

from app.api.schemas import (
    AcceptedResponse,
    DeleteMemoryResponse,
    PaymentMethodSetupIntentResponse,
    PaymentMethodsListResponse,
    UpdatedResponse,
    UpdateNotificationPreferencesRequest,
    UpdateProfileRequest,
    UpdateSecurityRequest,
    UserSettingsResponse,
)
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.user_settings_view import build_user_settings_response
from app.services.user_preferences import (
    set_notification_preferences,
    set_preferred_language,
)
from app.services.payment_methods import (
    create_setup_intent_client_secret,
    list_payment_methods_for_user,
    remove_payment_method_for_user,
    set_default_payment_method_for_user,
)
from app.services.mfa_security import (
    start_disable_2fa,
    start_enable_2fa,
    verify_2fa_challenge,
)

router = APIRouter(prefix="/api/v1/me/settings", tags=["Settings"])


@router.get(
    "",
    summary="Get current user settings",
    description="Returns user settings including preferred language with fallback to English.",
    response_model=UserSettingsResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def get_my_settings(current_user: AuthenticatedUser = Depends(get_current_user)) -> UserSettingsResponse:
    return build_user_settings_response(current_user)


@router.patch(
    "/profile",
    summary="Update profile settings",
    description="Updates profile settings. Preferred language supports en/it/de.",
    response_model=UserSettingsResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Validation error."},
    },
)
async def update_profile_settings(
    payload: UpdateProfileRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserSettingsResponse:
    set_preferred_language(current_user.tenant_id, current_user.user_id, payload.preferred_language)
    return build_user_settings_response(current_user)


@router.patch(
    "/security",
    summary="Trigger security-sensitive settings change",
    description="Starts security flow for email/password/2FA changes.",
    response_model=AcceptedResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Validation error."},
    },
)
async def update_security_settings(
    payload: UpdateSecurityRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AcceptedResponse:
    if payload.action == "enable_2fa":
        start_enable_2fa(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            current_enabled=current_user.mfa_enabled,
        )
    elif payload.action == "disable_2fa":
        if current_user.role in {"admin", "author"}:
            raise AppError(
                status_code=403,
                code="auth.mfa_required",
                message="Admin and Author roles must keep 2FA enabled.",
            )
        start_disable_2fa(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            current_enabled=current_user.mfa_enabled,
        )
    elif payload.action == "verify_2fa":
        if not payload.totp_code or not payload.totp_code.strip():
            raise AppError(
                status_code=422,
                code="memory.missing_required_fields",
                message="Missing required field for 2FA verification.",
                details={"missing_required_fields": ["totp_code"]},
            )
        verify_2fa_challenge(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            totp_code=payload.totp_code,
        )
    return AcceptedResponse(accepted=True)


@router.patch(
    "/notifications",
    summary="Update notification preferences",
    description="Updates in-app, push, and email notification preferences for the authenticated user.",
    response_model=UserSettingsResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Validation error."},
    },
)
async def update_notification_settings(
    payload: UpdateNotificationPreferencesRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserSettingsResponse:
    set_notification_preferences(
        current_user.tenant_id,
        current_user.user_id,
        {
            "in_app": payload.preferences.in_app,
            "push": payload.preferences.push,
            "email": payload.preferences.email,
        },
    )
    return build_user_settings_response(current_user)


@router.get(
    "/payment-methods",
    summary="List user payment methods",
    description="Returns masked payment methods for authenticated user role.",
    response_model=PaymentMethodsListResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Billing plan is locked by role policy."},
    },
)
async def list_payment_methods(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PaymentMethodsListResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Payment methods are unavailable for billing-exempt roles.",
        )

    items = list_payment_methods_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )
    return PaymentMethodsListResponse(items=items)


@router.post(
    "/payment-methods/setup-intent",
    summary="Create setup intent for payment method",
    description="Creates provider setup intent client secret to add or update payment method.",
    response_model=PaymentMethodSetupIntentResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Billing plan is locked by role policy."},
    },
)
async def create_payment_method_setup_intent(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PaymentMethodSetupIntentResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Payment methods are unavailable for billing-exempt roles.",
        )
    client_secret = create_setup_intent_client_secret(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )
    return PaymentMethodSetupIntentResponse(client_secret=client_secret)


@router.post(
    "/payment-methods/{id}/default",
    summary="Set default payment method",
    description="Marks a payment method as default for the authenticated user.",
    response_model=UpdatedResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Billing plan is locked by role policy."},
        404: {"description": "Payment method not found."},
    },
)
async def set_default_payment_method(
    id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UpdatedResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Payment methods are unavailable for billing-exempt roles.",
        )
    updated = set_default_payment_method_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        payment_method_id=id,
    )
    if not updated:
        raise AppError(
            status_code=404,
            code="memory.not_found",
            message="Payment method not found.",
        )
    return UpdatedResponse(updated=True)


@router.delete(
    "/payment-methods/{id}",
    summary="Remove payment method",
    description="Removes a payment method for the authenticated user.",
    response_model=DeleteMemoryResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        403: {"description": "Forbidden. Billing plan is locked by role policy."},
        404: {"description": "Payment method not found."},
    },
)
async def delete_payment_method(
    id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DeleteMemoryResponse:
    if current_user.role in {"admin", "author"}:
        raise AppError(
            status_code=403,
            code="billing.plan_locked_by_role",
            message="Payment methods are unavailable for billing-exempt roles.",
        )
    deleted = remove_payment_method_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        payment_method_id=id,
    )
    if not deleted:
        raise AppError(
            status_code=404,
            code="memory.not_found",
            message="Payment method not found.",
        )
    return DeleteMemoryResponse(deleted=True)
