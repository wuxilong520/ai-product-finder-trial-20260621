"""add market signal history

Revision ID: 20260709_000021
Revises: 20260709_000020
Create Date: 2026-07-09 14:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260709_000021"
down_revision = "20260709_000020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_signal_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("trend", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_market_signal_history_keyword", "market_signal_history", ["keyword"])
    op.create_index("ix_market_signal_history_region", "market_signal_history", ["region"])
    op.create_index("ix_market_signal_history_source", "market_signal_history", ["source"])


def downgrade() -> None:
    op.drop_index("ix_market_signal_history_source", table_name="market_signal_history")
    op.drop_index("ix_market_signal_history_region", table_name="market_signal_history")
    op.drop_index("ix_market_signal_history_keyword", table_name="market_signal_history")
    op.drop_table("market_signal_history")
