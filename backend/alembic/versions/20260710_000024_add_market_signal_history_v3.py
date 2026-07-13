"""add market_signal_history_v3

Revision ID: 20260710_000024
Revises: 20260710_000023
Create Date: 2026-07-10 13:50:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_000024"
down_revision = "20260710_000023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_signal_history_v3",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("market_score", sa.Float(), nullable=False),
        sa.Column("trend_direction", sa.String(length=50), nullable=False, server_default="flat"),
        sa.Column("real_data_ratio", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_market_signal_history_v3_keyword", "market_signal_history_v3", ["keyword"])
    op.create_index("ix_market_signal_history_v3_region", "market_signal_history_v3", ["region"])


def downgrade() -> None:
    op.drop_index("ix_market_signal_history_v3_region", table_name="market_signal_history_v3")
    op.drop_index("ix_market_signal_history_v3_keyword", table_name="market_signal_history_v3")
    op.drop_table("market_signal_history_v3")
