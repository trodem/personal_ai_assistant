"""Add foreign keys, constraints, and critical indexes.

Revision ID: 20260315_0005
Revises: 20260315_0004
Create Date: 2026-03-15
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260315_0005"
down_revision = "20260315_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key("fk_memories_user_id_users", "memories", "users", ["user_id"], ["id"])

    op.create_foreign_key(
        "fk_memory_versions_memory_id_memories",
        "memory_versions",
        "memories",
        ["memory_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_memory_versions_user_id_users",
        "memory_versions",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_attachments_memory_id_memories",
        "attachments",
        "memories",
        ["memory_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_attachments_user_id_users",
        "attachments",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_embeddings_memory_id_memories",
        "embeddings",
        "memories",
        ["memory_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_embeddings_user_id_users",
        "embeddings",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_qa_interactions_user_id_users",
        "qa_interactions",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_check_constraint(
        "ck_memories_memory_type_valid",
        "memories",
        "memory_type IN ('expense_event', 'inventory_event', 'loan_event', 'note', 'document')",
    )

    op.create_index("ix_memories_user_id_created_at", "memories", ["user_id", "created_at"])
    op.create_index("ix_memories_memory_type", "memories", ["memory_type"])

    op.create_index("ix_memory_versions_user_id_created_at", "memory_versions", ["user_id", "created_at"])
    op.create_index("ix_attachments_user_id_created_at", "attachments", ["user_id", "created_at"])
    op.create_index("ix_embeddings_user_id_created_at", "embeddings", ["user_id", "created_at"])
    op.create_index("ix_qa_interactions_user_id_created_at", "qa_interactions", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_qa_interactions_user_id_created_at", table_name="qa_interactions")
    op.drop_index("ix_embeddings_user_id_created_at", table_name="embeddings")
    op.drop_index("ix_attachments_user_id_created_at", table_name="attachments")
    op.drop_index("ix_memory_versions_user_id_created_at", table_name="memory_versions")
    op.drop_index("ix_memories_memory_type", table_name="memories")
    op.drop_index("ix_memories_user_id_created_at", table_name="memories")

    op.drop_constraint("ck_memories_memory_type_valid", "memories", type_="check")

    op.drop_constraint("fk_qa_interactions_user_id_users", "qa_interactions", type_="foreignkey")
    op.drop_constraint("fk_embeddings_user_id_users", "embeddings", type_="foreignkey")
    op.drop_constraint("fk_embeddings_memory_id_memories", "embeddings", type_="foreignkey")
    op.drop_constraint("fk_attachments_user_id_users", "attachments", type_="foreignkey")
    op.drop_constraint("fk_attachments_memory_id_memories", "attachments", type_="foreignkey")
    op.drop_constraint("fk_memory_versions_user_id_users", "memory_versions", type_="foreignkey")
    op.drop_constraint("fk_memory_versions_memory_id_memories", "memory_versions", type_="foreignkey")
    op.drop_constraint("fk_memories_user_id_users", "memories", type_="foreignkey")
