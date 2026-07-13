"""add market reality history v6

Revision ID: 20260710_000028
Revises: 20260710_000027
Create Date: 2026-07-10 19:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_000028"
down_revision = "20260710_000027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_reality_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("market_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("consumer_interest", sa.Float(), nullable=False, server_default="0"),
        sa.Column("commercial_intent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("competition_pressure", sa.Float(), nullable=False, server_default="0"),
        sa.Column("trend_stage", sa.String(length=30), nullable=False, server_default="stable"),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_market_reality_history_keyword", "market_reality_history", ["keyword"], unique=False)
    op.create_index("ix_market_reality_history_region", "market_reality_history", ["region"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_market_reality_history_region", table_name="market_reality_history")
    op.drop_index("ix_market_reality_history_keyword", table_name="market_reality_history")
    op.drop_table("market_reality_history")
