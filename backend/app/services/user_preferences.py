from app.core.i18n import DEFAULT_LANGUAGE, normalize_preferred_language

_USER_PROFILE_LANGUAGE: dict[tuple[str, str], str] = {}


def settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def set_preferred_language(tenant_id: str, user_id: str, language: str) -> None:
    _USER_PROFILE_LANGUAGE[settings_key(tenant_id, user_id)] = normalize_preferred_language(language)


def get_preferred_language(tenant_id: str, user_id: str) -> str:
    value = _USER_PROFILE_LANGUAGE.get(settings_key(tenant_id, user_id), DEFAULT_LANGUAGE)
    return normalize_preferred_language(value)
