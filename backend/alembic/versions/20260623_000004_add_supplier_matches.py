"""add supplier matches

Revision ID: 20260623_000004
Revises: 20260623_000003
Create Date: 2026-06-23 18:45:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260623_000004"
down_revision = "20260623_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supplier_matches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=True),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("supplier_title", sa.Text(), nullable=False),
        sa.Column("supplier_url", sa.Text(), nullable=False),
        sa.Column("supplier_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("match_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("availability", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_supplier_matches_product_id", "supplier_matches", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_supplier_matches_product_id", table_name="supplier_matches")
    op.drop_table("supplier_matches")
