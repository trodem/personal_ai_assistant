from typing import Literal, cast

from fastapi import APIRouter, Depends

from app.api.schemas import UpdateProfileRequest, UserSettingsResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.i18n import DEFAULT_LANGUAGE, normalize_preferred_language

router = APIRouter(prefix="/api/v1/me/settings", tags=["Settings"])

_USER_PROFILE_LANGUAGE: dict[tuple[str, str], str] = {}


def _settings_key(user: AuthenticatedUser) -> tuple[str, str]:
    return (user.tenant_id, user.user_id)


def _build_settings_response(user: AuthenticatedUser) -> UserSettingsResponse:
    language = _USER_PROFILE_LANGUAGE.get(_settings_key(user), DEFAULT_LANGUAGE)
    effective_language = normalize_preferred_language(language)
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
    _USER_PROFILE_LANGUAGE[_settings_key(current_user)] = payload.preferred_language
    return _build_settings_response(current_user)
