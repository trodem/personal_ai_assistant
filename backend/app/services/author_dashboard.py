from collections import Counter

from app.api.schemas import AuthorDashboardResponse
from app.repositories.admin_user_repository import AdminUserRecord


def build_author_dashboard(records: list[AdminUserRecord]) -> AuthorDashboardResponse:
    by_role: Counter[str] = Counter()
    by_status: Counter[str] = Counter()
    by_plan: Counter[str] = Counter()
    active_authors = 0

    for item in records:
        role = item["role"]
        user_status = item["status"]
        plan = item["subscription_plan"]
        by_role[role] += 1
        by_status[user_status] += 1
        by_plan[plan] += 1
        if role == "author" and user_status == "active":
            active_authors += 1

    return AuthorDashboardResponse(
        total_users=len(records),
        users_by_role=dict(by_role),
        users_by_status=dict(by_status),
        users_by_plan=dict(by_plan),
        active_authors=active_authors,
    )
