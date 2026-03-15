from typing import Literal, cast

from app.api.schemas import NotificationPreferences, UserSettingsResponse
from app.core.auth import AuthenticatedUser
from app.services.subscription_plans import get_effective_subscription_plan
from app.services.user_preferences import get_notification_preferences, get_preferred_language


def build_user_settings_response(user: AuthenticatedUser) -> UserSettingsResponse:
    effective_language = get_preferred_language(user.tenant_id, user.user_id)
    billing_exempt = user.role in {"admin", "author"}
    role: Literal["user", "admin", "author"] = cast(Literal["user", "admin", "author"], user.role)
    status: Literal["active", "suspended", "canceled"] = cast(
        Literal["active", "suspended", "canceled"],
        user.status,
    )
    subscription_plan = get_effective_subscription_plan(
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        role=user.role,
    )
    return UserSettingsResponse(
        user_id=user.user_id,
        email="",
        preferred_language=effective_language,
        auth_provider="password",
        role=role,
        status=status,
        mfa_enabled=user.mfa_enabled,
        subscription_plan=subscription_plan,
        billing_exempt=billing_exempt,
        payment_methods_enabled=not billing_exempt,
        default_payment_method=None,
        notification_preferences=NotificationPreferences(
            **get_notification_preferences(user.tenant_id, user.user_id)
        ),
    )
