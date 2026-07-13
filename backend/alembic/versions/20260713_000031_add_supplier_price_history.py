"""add supplier price history

Revision ID: 20260713_000031
Revises: 20260713_000030
Create Date: 2026-07-13 18:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_000031"
down_revision = "20260713_000030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supplier_price_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("supplier_products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("moq", sa.Integer(), nullable=True),
        sa.Column("record_source", sa.String(length=50), nullable=False, server_default="cache_database"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_supplier_price_history_supplier_id", "supplier_price_history", ["supplier_id"], unique=False)
    op.create_index("ix_supplier_price_history_product_id", "supplier_price_history", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_supplier_price_history_product_id", table_name="supplier_price_history")
    op.drop_index("ix_supplier_price_history_supplier_id", table_name="supplier_price_history")
    op.drop_table("supplier_price_history")
