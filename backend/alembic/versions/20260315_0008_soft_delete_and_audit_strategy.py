"""Add soft-delete and audit-trail schema baseline for memories.

Revision ID: 20260315_0008
Revises: 20260315_0007
Create Date: 2026-03-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260315_0008"
down_revision = "20260315_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("memories", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("memories", sa.Column("deleted_by_user_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("memories", sa.Column("delete_reason", sa.Text(), nullable=True))
    op.create_foreign_key(
        "fk_memories_deleted_by_user_id_users",
        "memories",
        "users",
        ["deleted_by_user_id"],
        ["id"],
    )
    op.create_index("ix_memories_deleted_at", "memories", ["deleted_at"])

    op.create_table(
        "memory_audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.Text(), nullable=False, server_default=sa.text("'tenant-default'")),
        sa.Column("memory_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("previous_version_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("new_version_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_foreign_key("fk_memory_audit_log_memory_id_memories", "memory_audit_log", "memories", ["memory_id"], ["id"])
    op.create_foreign_key(
        "fk_memory_audit_log_actor_user_id_users",
        "memory_audit_log",
        "users",
        ["actor_user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_memory_audit_log_previous_version_id_memory_versions",
        "memory_audit_log",
        "memory_versions",
        ["previous_version_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_memory_audit_log_new_version_id_memory_versions",
        "memory_audit_log",
        "memory_versions",
        ["new_version_id"],
        ["id"],
    )
    op.create_check_constraint(
        "ck_memory_audit_log_action_valid",
        "memory_audit_log",
        "action IN ('update', 'delete', 'restore')",
    )
    op.create_check_constraint(
        "ck_memory_audit_log_tenant_id_non_empty",
        "memory_audit_log",
        "length(tenant_id) > 0",
    )
    op.create_index("ix_memory_audit_log_tenant_id", "memory_audit_log", ["tenant_id"])
    op.create_index("ix_memory_audit_log_memory_id_created_at", "memory_audit_log", ["memory_id", "created_at"])
    op.create_index(
        "ix_memory_audit_log_actor_user_id_created_at",
        "memory_audit_log",
        ["actor_user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_memory_audit_log_actor_user_id_created_at", table_name="memory_audit_log")
    op.drop_index("ix_memory_audit_log_memory_id_created_at", table_name="memory_audit_log")
    op.drop_index("ix_memory_audit_log_tenant_id", table_name="memory_audit_log")
    op.drop_constraint("ck_memory_audit_log_tenant_id_non_empty", "memory_audit_log", type_="check")
    op.drop_constraint("ck_memory_audit_log_action_valid", "memory_audit_log", type_="check")
    op.drop_constraint(
        "fk_memory_audit_log_new_version_id_memory_versions",
        "memory_audit_log",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_memory_audit_log_previous_version_id_memory_versions",
        "memory_audit_log",
        type_="foreignkey",
    )
    op.drop_constraint("fk_memory_audit_log_actor_user_id_users", "memory_audit_log", type_="foreignkey")
    op.drop_constraint("fk_memory_audit_log_memory_id_memories", "memory_audit_log", type_="foreignkey")
    op.drop_table("memory_audit_log")

    op.drop_index("ix_memories_deleted_at", table_name="memories")
    op.drop_constraint("fk_memories_deleted_by_user_id_users", "memories", type_="foreignkey")
    op.drop_column("memories", "delete_reason")
    op.drop_column("memories", "deleted_by_user_id")
    op.drop_column("memories", "deleted_at")
