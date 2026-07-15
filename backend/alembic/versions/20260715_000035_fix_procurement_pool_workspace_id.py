"""fix procurement pool workspace columns

Revision ID: 20260715_000035
Revises: 20260715_000034
Create Date: 2026-07-15 13:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_000035"
down_revision = "20260715_000034"
branch_labels = None
depends_on = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    if not _column_exists(bind, "procurement_pool_items", "workspace_id"):
        op.add_column(
            "procurement_pool_items",
            sa.Column("workspace_id", sa.Integer(), nullable=True),
        )
    if not _index_exists(bind, "procurement_pool_items", "ix_procurement_pool_items_workspace_id"):
        op.create_index("ix_procurement_pool_items_workspace_id", "procurement_pool_items", ["workspace_id"], unique=False)
    op.execute(
        """
        UPDATE procurement_pool_items
        SET workspace_id = (
            SELECT users.workspace_id
            FROM users
            WHERE users.id = procurement_pool_items.user_id
        )
        WHERE workspace_id IS NULL
        """
    )

    if not _column_exists(bind, "procurement_supplier_items", "workspace_id"):
        op.add_column(
            "procurement_supplier_items",
            sa.Column("workspace_id", sa.Integer(), nullable=True),
        )
    if not _index_exists(bind, "procurement_supplier_items", "ix_procurement_supplier_items_workspace_id"):
        op.create_index("ix_procurement_supplier_items_workspace_id", "procurement_supplier_items", ["workspace_id"], unique=False)
    op.execute(
        """
        UPDATE procurement_supplier_items
        SET workspace_id = (
            SELECT procurement_pool_items.workspace_id
            FROM procurement_pool_items
            WHERE procurement_pool_items.id = procurement_supplier_items.pool_item_id
        )
        WHERE workspace_id IS NULL
        """
    )


def downgrade() -> None:
    bind = op.get_bind()

    if _index_exists(bind, "procurement_supplier_items", "ix_procurement_supplier_items_workspace_id"):
        op.drop_index("ix_procurement_supplier_items_workspace_id", table_name="procurement_supplier_items")
    if _column_exists(bind, "procurement_supplier_items", "workspace_id"):
        op.drop_column("procurement_supplier_items", "workspace_id")

    if _index_exists(bind, "procurement_pool_items", "ix_procurement_pool_items_workspace_id"):
        op.drop_index("ix_procurement_pool_items_workspace_id", table_name="procurement_pool_items")
    if _column_exists(bind, "procurement_pool_items", "workspace_id"):
        op.drop_column("procurement_pool_items", "workspace_id")
