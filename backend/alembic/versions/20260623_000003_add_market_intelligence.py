"""add market intelligence

Revision ID: 20260623_000003
Revises: 20260623_000002
Create Date: 2026-06-23 18:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260623_000003"
down_revision = "20260623_000002"
branch_labels = None
depends_on = None


def _json_type():
    return sa.JSON()


def upgrade() -> None:
    op.create_table(
        "market_intelligence",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("trend_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("demand_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("competition_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("opportunity_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendation_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendation", sa.String(length=20), nullable=False),
        sa.Column("reasons", _json_type(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_market_intelligence_keyword", "market_intelligence", ["keyword"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_market_intelligence_keyword", table_name="market_intelligence")
    op.drop_table("market_intelligence")
