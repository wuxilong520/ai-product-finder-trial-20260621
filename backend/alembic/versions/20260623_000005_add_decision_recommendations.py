"""add decision recommendations

Revision ID: 20260623_000005
Revises: 20260623_000004
Create Date: 2026-06-23 19:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260623_000005"
down_revision = "20260623_000004"
branch_labels = None
depends_on = None


def _json_type():
    return sa.JSON()


def upgrade() -> None:
    op.create_table(
        "decision_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("intelligence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("market_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("supplier_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("profit_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("final_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendation", sa.String(length=30), nullable=False),
        sa.Column("recommendation_level", sa.String(length=2), nullable=False),
        sa.Column("reasons", _json_type(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_decision_recommendations_product_id", "decision_recommendations", ["product_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_decision_recommendations_product_id", table_name="decision_recommendations")
    op.drop_table("decision_recommendations")
