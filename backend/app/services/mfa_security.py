from typing import Literal

from app.core.errors import AppError

SettingsKey = tuple[str, str]

_MFA_ENABLED_OVERRIDES: dict[SettingsKey, bool] = {}
_PENDING_MFA_CHALLENGE: dict[SettingsKey, Literal["enable_2fa", "disable_2fa"]] = {}

# Development baseline TOTP value for MVP local flow tests.
DEV_TOTP_CODE = "123456"


def _settings_key(tenant_id: str, user_id: str) -> SettingsKey:
    return (tenant_id, user_id)


def get_effective_mfa_enabled(*, tenant_id: str, user_id: str, token_mfa_enabled: bool) -> bool:
    return _MFA_ENABLED_OVERRIDES.get(_settings_key(tenant_id, user_id), token_mfa_enabled)


def start_enable_2fa(*, tenant_id: str, user_id: str, current_enabled: bool) -> None:
    if current_enabled:
        return
    _PENDING_MFA_CHALLENGE[_settings_key(tenant_id, user_id)] = "enable_2fa"


def start_disable_2fa(*, tenant_id: str, user_id: str, current_enabled: bool) -> None:
    if not current_enabled:
        raise AppError(
            status_code=422,
            code="memory.validation_failed",
            message="Two-factor authentication is not enabled.",
        )
    _PENDING_MFA_CHALLENGE[_settings_key(tenant_id, user_id)] = "disable_2fa"


def verify_2fa_challenge(*, tenant_id: str, user_id: str, totp_code: str) -> bool:
    key = _settings_key(tenant_id, user_id)
    pending = _PENDING_MFA_CHALLENGE.get(key)
    if pending is None:
        raise AppError(
            status_code=422,
            code="memory.validation_failed",
            message="No pending 2FA challenge found.",
        )
    if totp_code.strip() != DEV_TOTP_CODE:
        raise AppError(
            status_code=422,
            code="memory.validation_failed",
            message="Invalid 2FA verification code.",
        )

    if pending == "enable_2fa":
        _MFA_ENABLED_OVERRIDES[key] = True
    else:
        _MFA_ENABLED_OVERRIDES[key] = False
    _PENDING_MFA_CHALLENGE.pop(key, None)
    return _MFA_ENABLED_OVERRIDES[key]

