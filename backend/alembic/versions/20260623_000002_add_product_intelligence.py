"""add product intelligence

Revision ID: 20260623_000002
Revises: 20260620_000001
Create Date: 2026-06-23 17:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260623_000002"
down_revision = "20260620_000001"
branch_labels = None
depends_on = None


def _json_type():
    return sa.JSON()


def upgrade() -> None:
    op.create_table(
        "product_intelligence",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("market_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("competition_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("profit_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendation_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendation", sa.String(length=20), nullable=False),
        sa.Column("reasons", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_product_intelligence_product_id", "product_intelligence", ["product_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_product_intelligence_product_id", table_name="product_intelligence")
    op.drop_table("product_intelligence")
