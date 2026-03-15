_VALID_COUPONS = {"WELCOME10", "SAVE20", "SPRING25"}
_APPLIED_COUPONS: dict[tuple[str, str], set[str]] = {}


def _settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def apply_coupon_for_user(*, tenant_id: str, user_id: str, code: str) -> bool:
    normalized = code.strip().upper()
    if normalized not in _VALID_COUPONS:
        return False
    key = _settings_key(tenant_id, user_id)
    applied = set(_APPLIED_COUPONS.get(key, set()))
    applied.add(normalized)
    _APPLIED_COUPONS[key] = applied
    return True
