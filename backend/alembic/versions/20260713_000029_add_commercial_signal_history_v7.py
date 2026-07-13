"""add commercial signal history v7

Revision ID: 20260713_000029
Revises: 20260710_000028
Create Date: 2026-07-13 14:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_000029"
down_revision = "20260710_000028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "commercial_signal_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("signal_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="fallback"),
        sa.Column("reliability", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_commercial_signal_history_keyword", "commercial_signal_history", ["keyword"], unique=False)
    op.create_index("ix_commercial_signal_history_region", "commercial_signal_history", ["region"], unique=False)
    op.create_index("ix_commercial_signal_history_source", "commercial_signal_history", ["source"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_commercial_signal_history_source", table_name="commercial_signal_history")
    op.drop_index("ix_commercial_signal_history_region", table_name="commercial_signal_history")
    op.drop_index("ix_commercial_signal_history_keyword", table_name="commercial_signal_history")
    op.drop_table("commercial_signal_history")
