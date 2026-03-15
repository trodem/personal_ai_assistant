"""Prepare tenant-ready schema baseline.

Revision ID: 20260315_0007
Revises: 20260315_0006
Create Date: 2026-03-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260315_0007"
down_revision = "20260315_0006"
branch_labels = None
depends_on = None


def _add_tenant_column(table_name: str) -> None:
    op.add_column(
        table_name,
        sa.Column(
            "tenant_id",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'tenant-default'"),
        ),
    )
    op.create_check_constraint(
        f"ck_{table_name}_tenant_id_non_empty",
        table_name,
        "length(tenant_id) > 0",
    )
    op.create_index(f"ix_{table_name}_tenant_id", table_name, ["tenant_id"])


def _drop_tenant_column(table_name: str) -> None:
    op.drop_index(f"ix_{table_name}_tenant_id", table_name=table_name)
    op.drop_constraint(f"ck_{table_name}_tenant_id_non_empty", table_name, type_="check")
    op.drop_column(table_name, "tenant_id")


def upgrade() -> None:
    _add_tenant_column("users")
    _add_tenant_column("memories")
    _add_tenant_column("memory_versions")
    _add_tenant_column("attachments")
    _add_tenant_column("embeddings")
    _add_tenant_column("qa_interactions")


def downgrade() -> None:
    _drop_tenant_column("qa_interactions")
    _drop_tenant_column("embeddings")
    _drop_tenant_column("attachments")
    _drop_tenant_column("memory_versions")
    _drop_tenant_column("memories")
    _drop_tenant_column("users")
