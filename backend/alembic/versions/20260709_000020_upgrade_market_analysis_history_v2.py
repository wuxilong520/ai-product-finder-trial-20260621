"""upgrade market analysis history v2

Revision ID: 20260709_000020
Revises: 20260709_000019
Create Date: 2026-07-09 12:55:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260709_000020"
down_revision: str | None = "20260709_000019"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("market_analysis_history", sa.Column("previous_score", sa.Float(), nullable=True))
    op.add_column("market_analysis_history", sa.Column("current_score", sa.Float(), nullable=True))
    op.add_column("market_analysis_history", sa.Column("change_rate", sa.Float(), nullable=True))
    op.add_column("market_analysis_history", sa.Column("trend_direction", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("market_analysis_history", "trend_direction")
    op.drop_column("market_analysis_history", "change_rate")
    op.drop_column("market_analysis_history", "current_score")
    op.drop_column("market_analysis_history", "previous_score")
