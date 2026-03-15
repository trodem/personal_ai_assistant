"""Add structured_data_schema_version for forward-compatible payload evolution.

Revision ID: 20260315_0009
Revises: 20260315_0008
Create Date: 2026-03-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260315_0009"
down_revision = "20260315_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "memories",
        sa.Column(
            "structured_data_schema_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.create_check_constraint(
        "ck_memories_structured_data_schema_version_positive",
        "memories",
        "structured_data_schema_version >= 1",
    )

    op.add_column(
        "memory_versions",
        sa.Column(
            "structured_data_schema_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.create_check_constraint(
        "ck_memory_versions_structured_data_schema_version_positive",
        "memory_versions",
        "structured_data_schema_version >= 1",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_memory_versions_structured_data_schema_version_positive",
        "memory_versions",
        type_="check",
    )
    op.drop_column("memory_versions", "structured_data_schema_version")

    op.drop_constraint(
        "ck_memories_structured_data_schema_version_positive",
        "memories",
        type_="check",
    )
    op.drop_column("memories", "structured_data_schema_version")
