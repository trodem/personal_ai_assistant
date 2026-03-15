from datetime import UTC, datetime

from app.api.schemas import InAppNotificationRecord

_NOTIFICATIONS: dict[tuple[str, str], list[InAppNotificationRecord]] = {}


def _settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def list_notifications_for_user(
    *,
    tenant_id: str,
    user_id: str,
    unread_only: bool,
    limit: int,
) -> list[InAppNotificationRecord]:
    key = _settings_key(tenant_id, user_id)
    items = list(_NOTIFICATIONS.get(key, []))
    if unread_only:
        items = [item for item in items if not item.read]
    return items[:limit]


def add_notification_for_user(
    *,
    tenant_id: str,
    user_id: str,
    notification: InAppNotificationRecord,
) -> None:
    key = _settings_key(tenant_id, user_id)
    existing = list(_NOTIFICATIONS.get(key, []))
    existing = [item for item in existing if item.id != notification.id]
    existing.append(notification)
    existing.sort(key=lambda item: item.created_at, reverse=True)
    _NOTIFICATIONS[key] = existing


def build_notification(
    *,
    notification_id: str,
    event_type: str,
    title: str,
    body: str,
    read: bool = False,
) -> InAppNotificationRecord:
    return InAppNotificationRecord(
        id=notification_id,
        event_type=event_type,
        title=title,
        body=body,
        read=read,
        created_at=datetime.now(UTC).isoformat(),
    )
