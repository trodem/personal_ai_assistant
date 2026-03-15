"""Enforce append-only strategy for memory_versions.

Revision ID: 20260315_0006
Revises: 20260315_0005
Create Date: 2026-03-15
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260315_0006"
down_revision = "20260315_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_memory_versions_version_number_positive",
        "memory_versions",
        "version_number > 0",
    )
    op.create_unique_constraint(
        "uq_memory_versions_memory_id_version_number",
        "memory_versions",
        ["memory_id", "version_number"],
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_memory_versions_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'memory_versions is append-only';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_memory_versions_no_update
        BEFORE UPDATE ON memory_versions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_memory_versions_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_memory_versions_no_delete
        BEFORE DELETE ON memory_versions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_memory_versions_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_memory_versions_no_delete ON memory_versions;")
    op.execute("DROP TRIGGER IF EXISTS trg_memory_versions_no_update ON memory_versions;")
    op.execute("DROP FUNCTION IF EXISTS prevent_memory_versions_mutation();")
    op.drop_constraint("uq_memory_versions_memory_id_version_number", "memory_versions", type_="unique")
    op.drop_constraint("ck_memory_versions_version_number_positive", "memory_versions", type_="check")
