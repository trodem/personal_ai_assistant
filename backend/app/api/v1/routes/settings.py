from typing import Literal, cast

from fastapi import APIRouter, Depends

from app.api.schemas import (
    AcceptedResponse,
    NotificationPreferences,
    PaymentMethodSetupIntentResponse,
    PaymentMethodsListResponse,
    UpdateNotificationPreferencesRequest,
    UpdateProfileRequest,
    UpdateSecurityRequest,
    UserSettingsResponse,
)
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.user_preferences import (
    get_notification_preferences,
    get_preferred_language,
    set_notification_preferences,
    set_preferred_language,
)
from app.services.payment_methods import create_setup_intent_client_secret, list_payment_methods_for_user

router = APIRouter(prefix="/api/v1/me/settings", tags=["Settings"])

def _build_settings_response(user: AuthenticatedUser) -> UserSettingsResponse:
    effective_language = get_preferred_language(user.tenant_id, user.user_id)
    billing_exempt = user.role in {"admin", "author"}
    role: Literal["user", "admin", "author"] = cast(Literal["user", "admin", "author"], user.role)
    status: Literal["active", "suspended", "canceled"] = cast(
        Literal["active", "suspended", "canceled"], user.status
    )
    return UserSettingsResponse(
        user_id=user.user_id,
        email="",
        preferred_language=effective_language,
        auth_provider="password",
        role=role,
        status=status,
        mfa_enabled=user.mfa_enabled,
        subscription_plan="premium" if billing_exempt else "free",
        billing_exempt=billing_exempt,
        payment_methods_enabled=not billing_exempt,
        default_payment_method=None,
        notification_preferences=NotificationPreferences(
            **get_notification_preferences(user.tenant_id, user.user_id)
        ),
    )


@router.get(
    "",
    summary="Get current user settings",
    description="Returns user settings including preferred language with fallback to English.",
    response_model=UserSettingsResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def get_my_settings(current_user: AuthenticatedUser = Depends(get_current_user)) -> UserSettingsResponse:
    return _build_settings_response(current_user)


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
    return _build_settings_response(current_user)


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
    _ = payload
    _ = current_user
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
    return _build_settings_response(current_user)


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
