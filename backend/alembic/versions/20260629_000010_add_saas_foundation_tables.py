"""add saas foundation tables

Revision ID: 20260629_000010
Revises: 20260629_000009
Create Date: 2026-06-29 22:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260629_000010"
down_revision = "20260629_000009"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    if not _table_exists("workspaces"):
        op.create_table(
            "workspaces",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        )
    if not _index_exists("workspaces", "ix_workspaces_name"):
        op.create_index("ix_workspaces_name", "workspaces", ["name"], unique=False)
    if not _index_exists("workspaces", "ix_workspaces_owner_id"):
        op.create_index("ix_workspaces_owner_id", "workspaces", ["owner_id"], unique=False)

    if not _column_exists("users", "role"):
        op.add_column("users", sa.Column("role", sa.String(length=20), nullable=False, server_default="owner"))
    if not _column_exists("users", "workspace_id"):
        op.add_column("users", sa.Column("workspace_id", sa.Integer(), nullable=True))
    if not _index_exists("users", "ix_users_workspace_id"):
        op.create_index("ix_users_workspace_id", "users", ["workspace_id"], unique=False)

    if not _table_exists("api_keys"):
        op.create_table(
            "api_keys",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("key", sa.String(length=255), nullable=False),
            sa.Column("workspace_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    if not _index_exists("api_keys", "ix_api_keys_key"):
        op.create_index("ix_api_keys_key", "api_keys", ["key"], unique=True)
    if not _index_exists("api_keys", "ix_api_keys_workspace_id"):
        op.create_index("ix_api_keys_workspace_id", "api_keys", ["workspace_id"], unique=False)
    if not _index_exists("api_keys", "ix_api_keys_user_id"):
        op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"], unique=False)

    if not _table_exists("workspace_quotas"):
        op.create_table(
            "workspace_quotas",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("workspace_id", sa.Integer(), nullable=False),
            sa.Column("daily_task_limit", sa.Integer(), nullable=False, server_default="10"),
            sa.Column("daily_api_limit", sa.Integer(), nullable=False, server_default="100"),
            sa.Column("used_task", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("used_api", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("workspace_id"),
        )
    if not _index_exists("workspace_quotas", "ix_workspace_quotas_workspace_id"):
        op.create_index("ix_workspace_quotas_workspace_id", "workspace_quotas", ["workspace_id"], unique=True)

    if not _table_exists("workspace_subscriptions"):
        op.create_table(
            "workspace_subscriptions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("workspace_id", sa.Integer(), nullable=False),
            sa.Column("plan_name", sa.String(length=30), nullable=False, server_default="free"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("workspace_id"),
        )
    if not _index_exists("workspace_subscriptions", "ix_workspace_subscriptions_workspace_id"):
        op.create_index("ix_workspace_subscriptions_workspace_id", "workspace_subscriptions", ["workspace_id"], unique=True)

    for table in ["sync_jobs", "decision_recommendations", "business_truth_decisions", "data_source_registry", "data_lineage_records", "data_quality_history"]:
        if table == "sync_jobs":
            if not _column_exists(table, "user_id"):
                op.add_column(table, sa.Column("user_id", sa.Integer(), nullable=True))
            if not _column_exists(table, "workspace_id"):
                op.add_column(table, sa.Column("workspace_id", sa.Integer(), nullable=True))
            if not _column_exists(table, "api_key_id"):
                op.add_column(table, sa.Column("api_key_id", sa.Integer(), nullable=True))
            if not _index_exists(table, "ix_sync_jobs_user_id"):
                op.create_index("ix_sync_jobs_user_id", table, ["user_id"], unique=False)
            if not _index_exists(table, "ix_sync_jobs_workspace_id"):
                op.create_index("ix_sync_jobs_workspace_id", table, ["workspace_id"], unique=False)
            if not _index_exists(table, "ix_sync_jobs_api_key_id"):
                op.create_index("ix_sync_jobs_api_key_id", table, ["api_key_id"], unique=False)
        elif table in {"decision_recommendations", "business_truth_decisions"}:
            if not _column_exists(table, "workspace_id"):
                op.add_column(table, sa.Column("workspace_id", sa.Integer(), nullable=True))
            if not _column_exists(table, "user_id"):
                op.add_column(table, sa.Column("user_id", sa.Integer(), nullable=True))
            if not _index_exists(table, f"ix_{table}_workspace_id"):
                op.create_index(f"ix_{table}_workspace_id", table, ["workspace_id"], unique=False)
            if not _index_exists(table, f"ix_{table}_user_id"):
                op.create_index(f"ix_{table}_user_id", table, ["user_id"], unique=False)
        else:
            if not _column_exists(table, "workspace_id"):
                op.add_column(table, sa.Column("workspace_id", sa.Integer(), nullable=True))
            if not _index_exists(table, f"ix_{table}_workspace_id"):
                op.create_index(f"ix_{table}_workspace_id", table, ["workspace_id"], unique=False)


def downgrade() -> None:
    for table in ["data_quality_history", "data_lineage_records", "data_source_registry"]:
        op.drop_index(f"ix_{table}_workspace_id", table_name=table)
        op.drop_column(table, "workspace_id")

    for table in ["business_truth_decisions", "decision_recommendations"]:
        op.drop_index(f"ix_{table}_user_id", table_name=table)
        op.drop_index(f"ix_{table}_workspace_id", table_name=table)
        op.drop_column(table, "user_id")
        op.drop_column(table, "workspace_id")

    op.drop_index("ix_sync_jobs_api_key_id", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_workspace_id", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_user_id", table_name="sync_jobs")
    op.drop_column("sync_jobs", "api_key_id")
    op.drop_column("sync_jobs", "workspace_id")
    op.drop_column("sync_jobs", "user_id")

    op.drop_index("ix_workspace_subscriptions_workspace_id", table_name="workspace_subscriptions")
    op.drop_table("workspace_subscriptions")

    op.drop_index("ix_workspace_quotas_workspace_id", table_name="workspace_quotas")
    op.drop_table("workspace_quotas")

    op.drop_index("ix_api_keys_user_id", table_name="api_keys")
    op.drop_index("ix_api_keys_workspace_id", table_name="api_keys")
    op.drop_index("ix_api_keys_key", table_name="api_keys")
    op.drop_table("api_keys")

    op.drop_constraint("fk_users_workspace_id", "users", type_="foreignkey")
    op.drop_index("ix_users_workspace_id", table_name="users")
    op.drop_column("users", "workspace_id")
    op.drop_column("users", "role")

    op.drop_index("ix_workspaces_owner_id", table_name="workspaces")
    op.drop_index("ix_workspaces_name", table_name="workspaces")
    op.drop_table("workspaces")
