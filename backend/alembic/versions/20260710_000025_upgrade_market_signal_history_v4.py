"""upgrade market_signal_history v4

Revision ID: 20260710_000025
Revises: 20260710_000024
Create Date: 2026-07-10 18:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_000025"
down_revision = "20260710_000024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("market_signal_history", sa.Column("confidence", sa.Float(), nullable=False, server_default="0"))
    op.add_column("market_signal_history", sa.Column("signal_strength", sa.Float(), nullable=False, server_default="0"))
    op.add_column("market_signal_history", sa.Column("change_rate", sa.Float(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("market_signal_history", "change_rate")
    op.drop_column("market_signal_history", "signal_strength")
    op.drop_column("market_signal_history", "confidence")
