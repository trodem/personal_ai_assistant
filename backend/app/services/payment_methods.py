from app.api.schemas import PaymentMethodRecord

_PAYMENT_METHODS: dict[tuple[str, str], list[PaymentMethodRecord]] = {}


def _settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def list_payment_methods_for_user(*, tenant_id: str, user_id: str) -> list[PaymentMethodRecord]:
    return list(_PAYMENT_METHODS.get(_settings_key(tenant_id, user_id), []))


def create_setup_intent_client_secret(*, tenant_id: str, user_id: str) -> str:
    return f"seti_{tenant_id}_{user_id}_secret"


def add_payment_method_for_user(
    *,
    tenant_id: str,
    user_id: str,
    payment_method: PaymentMethodRecord,
) -> None:
    key = _settings_key(tenant_id, user_id)
    existing = list(_PAYMENT_METHODS.get(key, []))
    existing = [item for item in existing if item.id != payment_method.id]
    existing.append(payment_method)
    _PAYMENT_METHODS[key] = existing


def set_default_payment_method_for_user(
    *,
    tenant_id: str,
    user_id: str,
    payment_method_id: str,
) -> bool:
    key = _settings_key(tenant_id, user_id)
    existing = list(_PAYMENT_METHODS.get(key, []))
    if not any(item.id == payment_method_id for item in existing):
        return False

    updated: list[PaymentMethodRecord] = []
    for item in existing:
        updated.append(item.model_copy(update={"is_default": item.id == payment_method_id}))
    _PAYMENT_METHODS[key] = updated
    return True


def remove_payment_method_for_user(
    *,
    tenant_id: str,
    user_id: str,
    payment_method_id: str,
) -> bool:
    key = _settings_key(tenant_id, user_id)
    existing = list(_PAYMENT_METHODS.get(key, []))
    if not any(item.id == payment_method_id for item in existing):
        return False

    remaining = [item for item in existing if item.id != payment_method_id]
    if remaining and not any(item.is_default for item in remaining):
        first = remaining[0]
        remaining[0] = first.model_copy(update={"is_default": True})
    _PAYMENT_METHODS[key] = remaining
    return True
