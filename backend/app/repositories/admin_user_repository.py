from typing import TypedDict


class AdminUserRecord(TypedDict):
    id: str
    tenant_id: str
    email: str
    role: str
    status: str
    subscription_plan: str
    billing_exempt: bool


_ADMIN_USER_RECORDS: list[AdminUserRecord] = []


def _require_tenant_id(tenant_id: str) -> None:
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id is required for repository queries")


def _default_plan_for_role(role: str) -> tuple[str, bool]:
    if role in {"admin", "author"}:
        return "premium", True
    return "free", False


def upsert_admin_user(
    *,
    tenant_id: str,
    user_id: str,
    role: str = "user",
    status: str = "active",
    email: str = "",
) -> AdminUserRecord:
    _require_tenant_id(tenant_id)
    for item in _ADMIN_USER_RECORDS:
        if item["tenant_id"] == tenant_id and item["id"] == user_id:
            item["role"] = role
            item["status"] = status
            item["email"] = email
            plan, billing_exempt = _default_plan_for_role(role)
            item["subscription_plan"] = plan
            item["billing_exempt"] = billing_exempt
            return item

    plan, billing_exempt = _default_plan_for_role(role)
    record: AdminUserRecord = {
        "id": user_id,
        "tenant_id": tenant_id,
        "email": email,
        "role": role,
        "status": status,
        "subscription_plan": plan,
        "billing_exempt": billing_exempt,
    }
    _ADMIN_USER_RECORDS.append(record)
    return record


def list_admin_users_for_tenant(*, tenant_id: str) -> list[AdminUserRecord]:
    _require_tenant_id(tenant_id)
    return [item for item in _ADMIN_USER_RECORDS if item["tenant_id"] == tenant_id]


def update_admin_user_status(
    *,
    tenant_id: str,
    user_id: str,
    status: str,
) -> AdminUserRecord:
    _require_tenant_id(tenant_id)
    for item in _ADMIN_USER_RECORDS:
        if item["tenant_id"] == tenant_id and item["id"] == user_id:
            item["status"] = status
            return item

    return upsert_admin_user(
        tenant_id=tenant_id,
        user_id=user_id,
        status=status,
    )


def update_admin_user_role(
    *,
    tenant_id: str,
    user_id: str,
    role: str,
) -> AdminUserRecord:
    _require_tenant_id(tenant_id)
    for item in _ADMIN_USER_RECORDS:
        if item["tenant_id"] == tenant_id and item["id"] == user_id:
            item["role"] = role
            plan, billing_exempt = _default_plan_for_role(role)
            item["subscription_plan"] = plan
            item["billing_exempt"] = billing_exempt
            return item

    return upsert_admin_user(
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
    )


def count_active_authors_for_tenant(*, tenant_id: str) -> int:
    _require_tenant_id(tenant_id)
    return sum(
        1
        for item in _ADMIN_USER_RECORDS
        if item["tenant_id"] == tenant_id and item["role"] == "author" and item["status"] == "active"
    )
