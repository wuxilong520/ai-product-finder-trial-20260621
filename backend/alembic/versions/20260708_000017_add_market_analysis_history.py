"""add market analysis history

Revision ID: 20260708_000017
Revises: 20260701_000016
Create Date: 2026-07-08 18:55:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_000017"
down_revision: str | None = "20260701_000016"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "market_analysis_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("trend", sa.Float(), nullable=False),
        sa.Column("competition", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("is_mock", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_market_analysis_history_keyword"), "market_analysis_history", ["keyword"], unique=False)
    op.create_index(op.f("ix_market_analysis_history_region"), "market_analysis_history", ["region"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_market_analysis_history_region"), table_name="market_analysis_history")
    op.drop_index(op.f("ix_market_analysis_history_keyword"), table_name="market_analysis_history")
    op.drop_table("market_analysis_history")
