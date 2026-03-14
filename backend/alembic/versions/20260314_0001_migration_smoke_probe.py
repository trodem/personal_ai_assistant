"""Create migration smoke probe table.

Revision ID: 20260314_0001
Revises:
Create Date: 2026-03-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260314_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alembic_smoke_probe",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("alembic_smoke_probe")
