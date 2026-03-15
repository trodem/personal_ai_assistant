from typing import Literal

_USER_SUBSCRIPTION_PLANS: dict[tuple[str, str], Literal["free", "premium"]] = {}


def _settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def get_effective_subscription_plan(
    *,
    tenant_id: str,
    user_id: str,
    role: str,
) -> Literal["free", "premium"]:
    if role in {"admin", "author"}:
        return "premium"
    return _USER_SUBSCRIPTION_PLANS.get(_settings_key(tenant_id, user_id), "free")


def set_subscription_plan_for_user(
    *,
    tenant_id: str,
    user_id: str,
    plan: Literal["free", "premium"],
) -> None:
    _USER_SUBSCRIPTION_PLANS[_settings_key(tenant_id, user_id)] = plan
