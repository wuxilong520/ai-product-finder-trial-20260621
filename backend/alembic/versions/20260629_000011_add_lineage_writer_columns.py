"""add lineage writer columns

Revision ID: 20260629_000011
Revises: 20260629_000010
Create Date: 2026-06-29 20:50:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260629_000011"
down_revision = "20260629_000010"
branch_labels = None
depends_on = None


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
    table = "data_lineage_records"
    if not _column_exists(table, "task_id"):
        op.add_column(table, sa.Column("task_id", sa.Integer(), nullable=True))
    if not _column_exists(table, "user_id"):
        op.add_column(table, sa.Column("user_id", sa.Integer(), nullable=True))
    if not _column_exists(table, "node_type"):
        op.add_column(table, sa.Column("node_type", sa.String(length=30), nullable=False, server_default="trace"))
    if not _column_exists(table, "payload_json"):
        op.add_column(table, sa.Column("payload_json", sa.JSON(), nullable=True))
    if not _index_exists(table, "ix_data_lineage_records_task_id"):
        op.create_index("ix_data_lineage_records_task_id", table, ["task_id"], unique=False)
    if not _index_exists(table, "ix_data_lineage_records_user_id"):
        op.create_index("ix_data_lineage_records_user_id", table, ["user_id"], unique=False)
    if not _index_exists(table, "ix_data_lineage_records_node_type"):
        op.create_index("ix_data_lineage_records_node_type", table, ["node_type"], unique=False)


def downgrade() -> None:
    table = "data_lineage_records"
    op.drop_index("ix_data_lineage_records_node_type", table_name=table)
    op.drop_index("ix_data_lineage_records_user_id", table_name=table)
    op.drop_index("ix_data_lineage_records_task_id", table_name=table)
    op.drop_column(table, "payload_json")
    op.drop_column(table, "node_type")
    op.drop_column(table, "user_id")
    op.drop_column(table, "task_id")
