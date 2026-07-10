"""add business opportunity history

Revision ID: 20260710_000023
Revises: 20260710_000022
Create Date: 2026-07-10 13:10:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260710_000023"
down_revision: str | None = "20260710_000022"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "business_opportunity_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("market", sa.String(length=50), nullable=False),
        sa.Column("market_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("supplier_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("profit_margin", sa.Float(), nullable=False, server_default="0"),
        sa.Column("opportunity_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("decision", sa.String(length=20), nullable=False, server_default="WATCH"),
        sa.Column("execution_result", sa.String(length=50), nullable=True),
        sa.Column("shopify_action", sa.String(length=50), nullable=True),
        sa.Column("actual_result", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("snapshot", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_business_opportunity_history_keyword"), "business_opportunity_history", ["keyword"], unique=False)
    op.create_index(op.f("ix_business_opportunity_history_market"), "business_opportunity_history", ["market"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_business_opportunity_history_market"), table_name="business_opportunity_history")
    op.drop_index(op.f("ix_business_opportunity_history_keyword"), table_name="business_opportunity_history")
    op.drop_table("business_opportunity_history")
