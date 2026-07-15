"""add production reliability tables

Revision ID: 20260715_000034
Revises: 20260714_000033
Create Date: 2026-07-15 11:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260715_000034"
down_revision = "20260714_000033"
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "request_metrics"):
        if not _column_exists(bind, "request_metrics", "request_id"):
            op.add_column("request_metrics", sa.Column("request_id", sa.String(length=64), nullable=True))
        if not _column_exists(bind, "request_metrics", "user_id"):
            op.add_column("request_metrics", sa.Column("user_id", sa.Integer(), nullable=True))
        if not _column_exists(bind, "request_metrics", "workspace_id"):
            op.add_column("request_metrics", sa.Column("workspace_id", sa.Integer(), nullable=True))
        if not _index_exists(bind, "request_metrics", "ix_request_metrics_request_id"):
            op.create_index("ix_request_metrics_request_id", "request_metrics", ["request_id"], unique=False)
        if not _index_exists(bind, "request_metrics", "ix_request_metrics_user_id"):
            op.create_index("ix_request_metrics_user_id", "request_metrics", ["user_id"], unique=False)
        if not _index_exists(bind, "request_metrics", "ix_request_metrics_workspace_id"):
            op.create_index("ix_request_metrics_workspace_id", "request_metrics", ["workspace_id"], unique=False)

    if not _table_exists(bind, "user_activity_logs"):
        op.create_table(
            "user_activity_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("request_id", sa.String(length=64), nullable=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True),
            sa.Column("action", sa.String(length=120), nullable=False),
            sa.Column("method", sa.String(length=10), nullable=False),
            sa.Column("path", sa.String(length=255), nullable=False),
            sa.Column("status_code", sa.Integer(), nullable=False, server_default="200"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_user_activity_logs_request_id", "user_activity_logs", ["request_id"], unique=False)
        op.create_index("ix_user_activity_logs_user_id", "user_activity_logs", ["user_id"], unique=False)
        op.create_index("ix_user_activity_logs_workspace_id", "user_activity_logs", ["workspace_id"], unique=False)
        op.create_index("ix_user_activity_logs_action", "user_activity_logs", ["action"], unique=False)
        op.create_index("ix_user_activity_logs_created_at", "user_activity_logs", ["created_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "user_activity_logs"):
        op.drop_index("ix_user_activity_logs_created_at", table_name="user_activity_logs")
        op.drop_index("ix_user_activity_logs_action", table_name="user_activity_logs")
        op.drop_index("ix_user_activity_logs_workspace_id", table_name="user_activity_logs")
        op.drop_index("ix_user_activity_logs_user_id", table_name="user_activity_logs")
        op.drop_index("ix_user_activity_logs_request_id", table_name="user_activity_logs")
        op.drop_table("user_activity_logs")

    if _table_exists(bind, "request_metrics"):
        if _index_exists(bind, "request_metrics", "ix_request_metrics_workspace_id"):
            op.drop_index("ix_request_metrics_workspace_id", table_name="request_metrics")
        if _index_exists(bind, "request_metrics", "ix_request_metrics_user_id"):
            op.drop_index("ix_request_metrics_user_id", table_name="request_metrics")
        if _index_exists(bind, "request_metrics", "ix_request_metrics_request_id"):
            op.drop_index("ix_request_metrics_request_id", table_name="request_metrics")
        if _column_exists(bind, "request_metrics", "workspace_id"):
            op.drop_column("request_metrics", "workspace_id")
        if _column_exists(bind, "request_metrics", "user_id"):
            op.drop_column("request_metrics", "user_id")
        if _column_exists(bind, "request_metrics", "request_id"):
            op.drop_column("request_metrics", "request_id")
