"""upgrade supply intelligence v2

Revision ID: 20260709_000019
Revises: 20260708_000018
Create Date: 2026-07-09 10:20:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260709_000019"
down_revision: str | None = "20260708_000018"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("suppliers", sa.Column("certification", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("delivery_time_days", sa.Integer(), nullable=True))
    op.add_column("suppliers", sa.Column("source_type", sa.String(length=50), nullable=False, server_default="cache_database"))
    op.add_column("suppliers", sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"))
    op.add_column("suppliers", sa.Column("is_authorized", sa.Boolean(), nullable=False, server_default=sa.text("0")))
    op.add_column("suppliers", sa.Column("last_feedback", sa.Text(), nullable=True))

    op.add_column("supplier_products", sa.Column("images", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("supplier_products", sa.Column("source_type", sa.String(length=50), nullable=False, server_default="cache_database"))
    op.add_column("supplier_products", sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"))

    op.create_table(
        "supply_supplier_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("product_title", sa.Text(), nullable=False),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("price_min", sa.Float(), nullable=True),
        sa.Column("price_max", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("min_order_quantity", sa.Integer(), nullable=True),
        sa.Column("gross_profit", sa.Float(), nullable=True),
        sa.Column("net_profit", sa.Float(), nullable=True),
        sa.Column("margin_rate", sa.Float(), nullable=True),
        sa.Column("stock_change", sa.String(length=50), nullable=True),
        sa.Column("feedback_status", sa.String(length=100), nullable=True),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_supply_supplier_history_supplier_name"), "supply_supplier_history", ["supplier_name"], unique=False)
    op.create_index(op.f("ix_supply_supplier_history_platform"), "supply_supplier_history", ["platform"], unique=False)
    op.create_index(op.f("ix_supply_supplier_history_keyword"), "supply_supplier_history", ["keyword"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_supply_supplier_history_keyword"), table_name="supply_supplier_history")
    op.drop_index(op.f("ix_supply_supplier_history_platform"), table_name="supply_supplier_history")
    op.drop_index(op.f("ix_supply_supplier_history_supplier_name"), table_name="supply_supplier_history")
    op.drop_table("supply_supplier_history")

    op.drop_column("supplier_products", "confidence_score")
    op.drop_column("supplier_products", "source_type")
    op.drop_column("supplier_products", "images")

    op.drop_column("suppliers", "last_feedback")
    op.drop_column("suppliers", "is_authorized")
    op.drop_column("suppliers", "confidence_score")
    op.drop_column("suppliers", "source_type")
    op.drop_column("suppliers", "delivery_time_days")
    op.drop_column("suppliers", "certification")
