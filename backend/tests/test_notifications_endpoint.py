import sys
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.main import app
from app.services.notifications import add_notification_for_user, build_notification


class NotificationsEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        token = build_dev_token(f"user-notifications-{uuid4()}", tenant_id="tenant-a", role="user")
        self.headers = {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_notifications_requires_authentication(self) -> None:
        response = self.client.get("/api/v1/notifications")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_notifications_returns_user_feed(self) -> None:
        seeded_user = "user-notifications-seeded"
        seeded_token = build_dev_token(seeded_user, tenant_id="tenant-a", role="user")
        seeded_headers = {"Authorization": f"Bearer {seeded_token}", "x-tenant-id": "tenant-a"}

        add_notification_for_user(
            tenant_id="tenant-a",
            user_id=seeded_user,
            notification=build_notification(
                notification_id=f"notif-{uuid4()}",
                event_type="system_event",
                title="Welcome",
                body="Welcome to notifications.",
                read=False,
            ),
        )
        add_notification_for_user(
            tenant_id="tenant-a",
            user_id=seeded_user,
            notification=build_notification(
                notification_id=f"notif-{uuid4()}",
                event_type="billing_event",
                title="Billing update",
                body="Your billing status changed.",
                read=True,
            ),
        )

        response = self.client.get("/api/v1/notifications", headers=seeded_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("items", payload)
        self.assertEqual(len(payload["items"]), 2)

    def test_notifications_support_unread_only_and_limit(self) -> None:
        seeded_user = "user-notifications-filters"
        seeded_token = build_dev_token(seeded_user, tenant_id="tenant-a", role="user")
        seeded_headers = {"Authorization": f"Bearer {seeded_token}", "x-tenant-id": "tenant-a"}

        add_notification_for_user(
            tenant_id="tenant-a",
            user_id=seeded_user,
            notification=build_notification(
                notification_id=f"notif-{uuid4()}",
                event_type="security_event",
                title="Security check",
                body="Please review your settings.",
                read=False,
            ),
        )
        add_notification_for_user(
            tenant_id="tenant-a",
            user_id=seeded_user,
            notification=build_notification(
                notification_id=f"notif-{uuid4()}",
                event_type="system_event",
                title="Info",
                body="Generic info.",
                read=False,
            ),
        )
        add_notification_for_user(
            tenant_id="tenant-a",
            user_id=seeded_user,
            notification=build_notification(
                notification_id=f"notif-{uuid4()}",
                event_type="billing_event",
                title="Invoice",
                body="Invoice available.",
                read=True,
            ),
        )

        unread = self.client.get("/api/v1/notifications?unread_only=true", headers=seeded_headers)
        self.assertEqual(unread.status_code, 200)
        self.assertEqual(len(unread.json()["items"]), 2)

        limited = self.client.get("/api/v1/notifications?limit=1", headers=seeded_headers)
        self.assertEqual(limited.status_code, 200)
        self.assertEqual(len(limited.json()["items"]), 1)

    def test_mark_notification_as_read(self) -> None:
        seeded_user = "user-notifications-mark-read"
        seeded_token = build_dev_token(seeded_user, tenant_id="tenant-a", role="user")
        seeded_headers = {"Authorization": f"Bearer {seeded_token}", "x-tenant-id": "tenant-a"}

        notification_id = f"notif-{uuid4()}"
        add_notification_for_user(
            tenant_id="tenant-a",
            user_id=seeded_user,
            notification=build_notification(
                notification_id=notification_id,
                event_type="system_event",
                title="To read",
                body="Mark me as read.",
                read=False,
            ),
        )

        mark = self.client.post(f"/api/v1/notifications/{notification_id}/read", headers=seeded_headers)
        self.assertEqual(mark.status_code, 200)
        self.assertEqual(mark.json(), {"updated": True})

        unread = self.client.get("/api/v1/notifications?unread_only=true", headers=seeded_headers)
        self.assertEqual(unread.status_code, 200)
        self.assertEqual(len(unread.json()["items"]), 0)

    def test_mark_notification_as_read_requires_authentication(self) -> None:
        response = self.client.post(f"/api/v1/notifications/notif-{uuid4()}/read")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth.missing_token")

    def test_mark_notification_as_read_returns_404_for_unknown_id(self) -> None:
        response = self.client.post(
            f"/api/v1/notifications/notif-missing-{uuid4()}/read",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "memory.not_found")


if __name__ == "__main__":
    unittest.main()
