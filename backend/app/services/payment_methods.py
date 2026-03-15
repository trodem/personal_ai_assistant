from app.api.schemas import PaymentMethodRecord

_PAYMENT_METHODS: dict[tuple[str, str], list[PaymentMethodRecord]] = {}


def _settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def list_payment_methods_for_user(*, tenant_id: str, user_id: str) -> list[PaymentMethodRecord]:
    return list(_PAYMENT_METHODS.get(_settings_key(tenant_id, user_id), []))
