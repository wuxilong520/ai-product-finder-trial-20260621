"""add supply intelligence tables

Revision ID: 20260708_000018
Revises: 20260708_000017
Create Date: 2026-07-08 19:35:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_000018"
down_revision: str | None = "20260708_000017"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("supplier_type", sa.String(length=50), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("product_category", sa.String(length=255), nullable=True),
        sa.Column("min_order_quantity", sa.Integer(), nullable=True),
        sa.Column("price_range", sa.JSON(), nullable=False),
        sa.Column("transaction_score", sa.Float(), nullable=False),
        sa.Column("factory_score", sa.Float(), nullable=False),
        sa.Column("trust_score", sa.Float(), nullable=False),
        sa.Column("last_verified_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_suppliers_name"), "suppliers", ["name"], unique=False)
    op.create_index(op.f("ix_suppliers_platform"), "suppliers", ["platform"], unique=False)

    op.create_table(
        "supplier_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("product_title", sa.Text(), nullable=False),
        sa.Column("product_image", sa.Text(), nullable=True),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("price_min", sa.Float(), nullable=True),
        sa.Column("price_max", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("factory_info", sa.Text(), nullable=True),
        sa.Column("transaction_info", sa.Text(), nullable=True),
        sa.Column("raw_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_supplier_products_keyword"), "supplier_products", ["keyword"], unique=False)
    op.create_index(op.f("ix_supplier_products_supplier_id"), "supplier_products", ["supplier_id"], unique=False)

    op.create_table(
        "supply_analysis_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("target_market", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("supplier_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("is_mock", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_supply_analysis_history_keyword"), "supply_analysis_history", ["keyword"], unique=False)
    op.create_index(op.f("ix_supply_analysis_history_target_market"), "supply_analysis_history", ["target_market"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_supply_analysis_history_target_market"), table_name="supply_analysis_history")
    op.drop_index(op.f("ix_supply_analysis_history_keyword"), table_name="supply_analysis_history")
    op.drop_table("supply_analysis_history")
    op.drop_index(op.f("ix_supplier_products_supplier_id"), table_name="supplier_products")
    op.drop_index(op.f("ix_supplier_products_keyword"), table_name="supplier_products")
    op.drop_table("supplier_products")
    op.drop_index(op.f("ix_suppliers_platform"), table_name="suppliers")
    op.drop_index(op.f("ix_suppliers_name"), table_name="suppliers")
    op.drop_table("suppliers")
