"""add api_key_id to decision tables

Revision ID: 20260630_000013
Revises: 20260630_000012
Create Date: 2026-06-30 02:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260630_000013"
down_revision = "20260630_000012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ["decision_recommendations", "business_truth_decisions"]:
        with op.batch_alter_table(table) as batch_op:
            batch_op.add_column(sa.Column("api_key_id", sa.Integer(), nullable=True))
            batch_op.create_index(f"ix_{table}_api_key_id", ["api_key_id"], unique=False)


def downgrade() -> None:
    for table in ["business_truth_decisions", "decision_recommendations"]:
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_index(f"ix_{table}_api_key_id")
            batch_op.drop_column("api_key_id")
