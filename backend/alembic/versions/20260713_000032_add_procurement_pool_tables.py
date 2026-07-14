"""add procurement pool tables

Revision ID: 20260713_000032
Revises: 20260713_000031
Create Date: 2026-07-13 20:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_000032"
down_revision = "20260713_000031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("group_key", sa.String(length=120), nullable=False),
        sa.Column("canonical_keyword", sa.String(length=255), nullable=False),
        sa.Column("canonical_title", sa.Text(), nullable=False),
        sa.Column("representative_image", sa.Text(), nullable=True),
        sa.Column("similarity_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_product_groups_group_key", "product_groups", ["group_key"], unique=True)
    op.create_index("ix_product_groups_canonical_keyword", "product_groups", ["canonical_keyword"], unique=False)

    op.create_table(
        "procurement_pool_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_group_id", sa.Integer(), sa.ForeignKey("product_groups.id", ondelete="SET NULL"), nullable=True),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("image", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_platform", sa.String(length=50), nullable=False, server_default="1688"),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("supplier_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("min_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("max_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("avg_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("estimated_profit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("market_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="NEW"),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_procurement_pool_items_user_id", "procurement_pool_items", ["user_id"], unique=False)
    op.create_index("ix_procurement_pool_items_keyword", "procurement_pool_items", ["keyword"], unique=False)
    op.create_index("ix_procurement_pool_items_status", "procurement_pool_items", ["status"], unique=False)
    op.create_index("ix_procurement_pool_items_product_group_id", "procurement_pool_items", ["product_group_id"], unique=False)

    op.create_table(
        "procurement_supplier_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pool_item_id", sa.Integer(), sa.ForeignKey("procurement_pool_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("supplier_product_id", sa.Integer(), sa.ForeignKey("supplier_products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("moq", sa.Integer(), nullable=True),
        sa.Column("delivery_time", sa.Integer(), nullable=True),
        sa.Column("supplier_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("supplier_truth_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("source_type", sa.String(length=50), nullable=False, server_default="LOCAL_DATABASE"),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_procurement_supplier_items_pool_item_id", "procurement_supplier_items", ["pool_item_id"], unique=False)
    op.create_index("ix_procurement_supplier_items_supplier_id", "procurement_supplier_items", ["supplier_id"], unique=False)
    op.create_index("ix_procurement_supplier_items_supplier_product_id", "procurement_supplier_items", ["supplier_product_id"], unique=False)

    op.create_table(
        "supplier_reality_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("pool_item_id", sa.Integer(), sa.ForeignKey("procurement_pool_items.id", ondelete="CASCADE"), nullable=True),
        sa.Column("truth_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("price_truth_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("stability_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_supplier_reality_history_supplier_id", "supplier_reality_history", ["supplier_id"], unique=False)
    op.create_index("ix_supplier_reality_history_pool_item_id", "supplier_reality_history", ["pool_item_id"], unique=False)

    op.create_table(
        "procurement_analysis_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pool_item_id", sa.Integer(), sa.ForeignKey("procurement_pool_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("market_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("supplier_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("profit_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("recommendation", sa.String(length=40), nullable=False, server_default="谨慎观察"),
        sa.Column("reason", sa.JSON(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_procurement_analysis_history_pool_item_id", "procurement_analysis_history", ["pool_item_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_procurement_analysis_history_pool_item_id", table_name="procurement_analysis_history")
    op.drop_table("procurement_analysis_history")
    op.drop_index("ix_supplier_reality_history_pool_item_id", table_name="supplier_reality_history")
    op.drop_index("ix_supplier_reality_history_supplier_id", table_name="supplier_reality_history")
    op.drop_table("supplier_reality_history")
    op.drop_index("ix_procurement_supplier_items_supplier_product_id", table_name="procurement_supplier_items")
    op.drop_index("ix_procurement_supplier_items_supplier_id", table_name="procurement_supplier_items")
    op.drop_index("ix_procurement_supplier_items_pool_item_id", table_name="procurement_supplier_items")
    op.drop_table("procurement_supplier_items")
    op.drop_index("ix_procurement_pool_items_product_group_id", table_name="procurement_pool_items")
    op.drop_index("ix_procurement_pool_items_status", table_name="procurement_pool_items")
    op.drop_index("ix_procurement_pool_items_keyword", table_name="procurement_pool_items")
    op.drop_index("ix_procurement_pool_items_user_id", table_name="procurement_pool_items")
    op.drop_table("procurement_pool_items")
    op.drop_index("ix_product_groups_canonical_keyword", table_name="product_groups")
    op.drop_index("ix_product_groups_group_key", table_name="product_groups")
    op.drop_table("product_groups")
