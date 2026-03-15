from app.core.i18n import DEFAULT_LANGUAGE, normalize_preferred_language

_USER_PROFILE_LANGUAGE: dict[tuple[str, str], str] = {}
_USER_NOTIFICATION_PREFERENCES: dict[tuple[str, str], dict[str, bool]] = {}

_DEFAULT_NOTIFICATION_PREFERENCES: dict[str, bool] = {"in_app": True, "push": False, "email": True}


def settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def set_preferred_language(tenant_id: str, user_id: str, language: str) -> None:
    _USER_PROFILE_LANGUAGE[settings_key(tenant_id, user_id)] = normalize_preferred_language(language)


def get_preferred_language(tenant_id: str, user_id: str) -> str:
    value = _USER_PROFILE_LANGUAGE.get(settings_key(tenant_id, user_id), DEFAULT_LANGUAGE)
    return normalize_preferred_language(value)


def set_notification_preferences(tenant_id: str, user_id: str, preferences: dict[str, bool]) -> None:
    _USER_NOTIFICATION_PREFERENCES[settings_key(tenant_id, user_id)] = {
        "in_app": bool(preferences["in_app"]),
        "push": bool(preferences["push"]),
        "email": bool(preferences["email"]),
    }


def get_notification_preferences(tenant_id: str, user_id: str) -> dict[str, bool]:
    stored = _USER_NOTIFICATION_PREFERENCES.get(settings_key(tenant_id, user_id))
    if stored is None:
        return dict(_DEFAULT_NOTIFICATION_PREFERENCES)
    return {
        "in_app": bool(stored["in_app"]),
        "push": bool(stored["push"]),
        "email": bool(stored["email"]),
    }
