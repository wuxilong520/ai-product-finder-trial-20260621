"""add business truth decisions

Revision ID: 20260623_000006
Revises: 20260623_000005
Create Date: 2026-06-23 20:35:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260623_000006"
down_revision = "20260623_000005"
branch_labels = None
depends_on = None


def _json_type():
    return sa.JSON()


def upgrade() -> None:
    op.create_table(
        "business_truth_decisions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("real_market_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("market_price_min", sa.Numeric(12, 2), nullable=False),
        sa.Column("market_price_max", sa.Numeric(12, 2), nullable=False),
        sa.Column("demand_signal", sa.String(length=30), nullable=False),
        sa.Column("supplier_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("shipping_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("platform_fee", sa.Numeric(12, 2), nullable=False),
        sa.Column("packaging_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("exchange_rate", sa.Numeric(12, 4), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("profit", sa.Numeric(12, 2), nullable=False),
        sa.Column("profit_margin", sa.Numeric(7, 4), nullable=False),
        sa.Column("break_even_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("phase4_final_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("truth_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("truth_recommendation", sa.String(length=40), nullable=False),
        sa.Column("truth_level", sa.String(length=2), nullable=False),
        sa.Column("still_uses_simulated_data", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("simulated_dependencies", _json_type(), nullable=False),
        sa.Column("cost_breakdown", _json_type(), nullable=False),
        sa.Column("external_market_snapshot", _json_type(), nullable=False),
        sa.Column("reasons", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_business_truth_decisions_product_id", "business_truth_decisions", ["product_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_business_truth_decisions_product_id", table_name="business_truth_decisions")
    op.drop_table("business_truth_decisions")
