"""Add user billing-policy constraints.

Revision ID: 20260315_0004
Revises: 20260315_0003
Create Date: 2026-03-15
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260315_0004"
down_revision = "20260315_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_users_role_valid",
        "users",
        "role IN ('user', 'admin', 'author')",
    )
    op.create_check_constraint(
        "ck_users_subscription_plan_valid",
        "users",
        "subscription_plan IN ('free', 'premium')",
    )
    op.create_check_constraint(
        "ck_users_billing_policy_by_role",
        "users",
        "("
        "(role = 'user' AND billing_exempt = false) OR "
        "(role IN ('admin', 'author') AND billing_exempt = true AND subscription_plan = 'premium')"
        ")",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_billing_policy_by_role", "users", type_="check")
    op.drop_constraint("ck_users_subscription_plan_valid", "users", type_="check")
    op.drop_constraint("ck_users_role_valid", "users", type_="check")
