from typing import Literal, cast

from fastapi import APIRouter, Depends

from app.api.schemas import UpdateProfileRequest, UserSettingsResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.services.user_preferences import get_preferred_language, set_preferred_language

router = APIRouter(prefix="/api/v1/me/settings", tags=["Settings"])

def _build_settings_response(user: AuthenticatedUser) -> UserSettingsResponse:
    effective_language = get_preferred_language(user.tenant_id, user.user_id)
    billing_exempt = user.role in {"admin", "author"}
    role: Literal["user", "admin", "author"] = cast(Literal["user", "admin", "author"], user.role)
    return UserSettingsResponse(
        user_id=user.user_id,
        email="",
        preferred_language=effective_language,
        auth_provider="password",
        role=role,
        status="active",
        mfa_enabled=user.mfa_enabled,
        subscription_plan="premium" if billing_exempt else "free",
        billing_exempt=billing_exempt,
        payment_methods_enabled=not billing_exempt,
        default_payment_method=None,
        notification_preferences={"in_app": True, "push": False, "email": True},
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
