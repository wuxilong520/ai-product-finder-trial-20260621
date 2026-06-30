"""add billing orders table

Revision ID: 20260630_000015
Revises: 20260630_000014
Create Date: 2026-06-30 14:35:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260630_000015"
down_revision = "20260630_000014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "billing_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("plan_name", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("amount_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="CNY"),
        sa.Column("provider_name", sa.String(length=50), nullable=True),
        sa.Column("external_order_id", sa.String(length=100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_billing_orders_workspace_id"), "billing_orders", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_billing_orders_user_id"), "billing_orders", ["user_id"], unique=False)
    op.create_index(op.f("ix_billing_orders_plan_name"), "billing_orders", ["plan_name"], unique=False)
    op.create_index(op.f("ix_billing_orders_status"), "billing_orders", ["status"], unique=False)
    op.create_index(op.f("ix_billing_orders_external_order_id"), "billing_orders", ["external_order_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_billing_orders_external_order_id"), table_name="billing_orders")
    op.drop_index(op.f("ix_billing_orders_status"), table_name="billing_orders")
    op.drop_index(op.f("ix_billing_orders_plan_name"), table_name="billing_orders")
    op.drop_index(op.f("ix_billing_orders_user_id"), table_name="billing_orders")
    op.drop_index(op.f("ix_billing_orders_workspace_id"), table_name="billing_orders")
    op.drop_table("billing_orders")
