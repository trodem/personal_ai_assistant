"""Enable pgvector extension.

Revision ID: 20260315_0002
Revises: 20260314_0001
Create Date: 2026-03-15
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260315_0002"
down_revision = "20260314_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector;")
