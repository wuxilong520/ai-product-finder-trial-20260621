"""add data_connections v5

Revision ID: 20260710_000026
Revises: 20260710_000025
Create Date: 2026-07-10 20:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_000026"
down_revision = "20260710_000025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False, server_default=""),
        sa.Column("refresh_token", sa.Text(), nullable=False, server_default=""),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("permission_scope", sa.JSON(), nullable=False),
        sa.Column("shop_domain", sa.String(length=255), nullable=True),
        sa.Column("external_account_id", sa.String(length=255), nullable=True),
        sa.Column("connection_meta", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("user_id", "platform", name="uq_data_connections_user_platform"),
    )
    op.create_index("ix_data_connections_user_id", "data_connections", ["user_id"])
    op.create_index("ix_data_connections_platform", "data_connections", ["platform"])
    op.create_index("ix_data_connections_shop_domain", "data_connections", ["shop_domain"])


def downgrade() -> None:
    op.drop_index("ix_data_connections_shop_domain", table_name="data_connections")
    op.drop_index("ix_data_connections_platform", table_name="data_connections")
    op.drop_index("ix_data_connections_user_id", table_name="data_connections")
    op.drop_table("data_connections")
