"""add amazon opportunity tables

Revision ID: 20260710_000022
Revises: 20260709_000021
Create Date: 2026-07-10 11:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260710_000022"
down_revision: str | None = "20260709_000021"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("suppliers", sa.Column("supplier_verified", sa.Boolean(), nullable=False, server_default=sa.text("0")))
    op.add_column("suppliers", sa.Column("product_url", sa.Text(), nullable=True))
    op.add_column("suppliers", sa.Column("factory_level", sa.String(length=100), nullable=True))
    op.add_column("suppliers", sa.Column("delivery_score", sa.Float(), nullable=False, server_default="0"))
    op.add_column("suppliers", sa.Column("price_history", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("suppliers", sa.Column("verification_status", sa.String(length=50), nullable=False, server_default="unverified"))

    op.create_table(
        "amazon_market_signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("marketplace", sa.String(length=50), nullable=False),
        sa.Column("bsr_rank", sa.Integer(), nullable=True),
        sa.Column("category_rank", sa.Integer(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating", sa.Float(), nullable=False, server_default="0"),
        sa.Column("seller_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price_min", sa.Float(), nullable=False, server_default="0"),
        sa.Column("price_max", sa.Float(), nullable=False, server_default="0"),
        sa.Column("price_average", sa.Float(), nullable=False, server_default="0"),
        sa.Column("competition_density", sa.Float(), nullable=False, server_default="0"),
        sa.Column("demand_signal", sa.Float(), nullable=False, server_default="0"),
        sa.Column("captured_at", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="partial"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_amazon_market_signals_keyword"), "amazon_market_signals", ["keyword"], unique=False)
    op.create_index(op.f("ix_amazon_market_signals_marketplace"), "amazon_market_signals", ["marketplace"], unique=False)

    op.create_table(
        "amazon_market_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("marketplace", sa.String(length=50), nullable=False),
        sa.Column("bsr", sa.Integer(), nullable=True),
        sa.Column("reviews", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("seller_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_amazon_market_history_keyword"), "amazon_market_history", ["keyword"], unique=False)
    op.create_index(op.f("ix_amazon_market_history_marketplace"), "amazon_market_history", ["marketplace"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_amazon_market_history_marketplace"), table_name="amazon_market_history")
    op.drop_index(op.f("ix_amazon_market_history_keyword"), table_name="amazon_market_history")
    op.drop_table("amazon_market_history")

    op.drop_index(op.f("ix_amazon_market_signals_marketplace"), table_name="amazon_market_signals")
    op.drop_index(op.f("ix_amazon_market_signals_keyword"), table_name="amazon_market_signals")
    op.drop_table("amazon_market_signals")

    op.drop_column("suppliers", "verification_status")
    op.drop_column("suppliers", "price_history")
    op.drop_column("suppliers", "delivery_score")
    op.drop_column("suppliers", "factory_level")
    op.drop_column("suppliers", "product_url")
    op.drop_column("suppliers", "supplier_verified")
