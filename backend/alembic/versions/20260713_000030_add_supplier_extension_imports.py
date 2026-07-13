"""add supplier extension imports

Revision ID: 20260713_000030
Revises: 20260713_000029
Create Date: 2026-07-13 16:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260713_000030"
down_revision = "20260713_000029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supplier_extension_imports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="1688_extension"),
        sa.Column("product_title", sa.Text(), nullable=False),
        sa.Column("supplier_name", sa.String(length=255), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_supplier_extension_imports_user_id", "supplier_extension_imports", ["user_id"], unique=False)
    op.create_index("ix_supplier_extension_imports_supplier_name", "supplier_extension_imports", ["supplier_name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_supplier_extension_imports_supplier_name", table_name="supplier_extension_imports")
    op.drop_index("ix_supplier_extension_imports_user_id", table_name="supplier_extension_imports")
    op.drop_table("supplier_extension_imports")
