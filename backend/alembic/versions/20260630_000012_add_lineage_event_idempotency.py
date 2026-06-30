"""add lineage event idempotency

Revision ID: 20260630_000012
Revises: 20260629_000011
Create Date: 2026-06-30 00:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260630_000012"
down_revision = "20260629_000011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = "data_lineage_records"
    with op.batch_alter_table(table) as batch_op:
        batch_op.add_column(sa.Column("event_id", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("event_key", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("event_stage", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("api_key_id", sa.Integer(), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(sa.text(f"""
        SELECT id, task_id, node_type
        FROM {table}
        ORDER BY id
    """)).fetchall()

    seen: set[str] = set()
    duplicate_ids: list[int] = []
    for row in rows:
        event_key = f"{row.task_id or 'unknown'}:{row.node_type}:{row.node_type}_result_persist"
        if event_key in seen:
            duplicate_ids.append(row.id)
        else:
            seen.add(event_key)
            conn.execute(
                sa.text(f"""
                    UPDATE {table}
                    SET event_id = :event_id,
                        event_key = :event_key,
                        event_stage = :event_stage
                    WHERE id = :id
                """),
                {
                    "id": row.id,
                    "event_id": event_key,
                    "event_key": event_key,
                    "event_stage": f"{row.node_type}_result_persist",
                },
            )

    if duplicate_ids:
        conn.execute(
            sa.text(f"DELETE FROM {table} WHERE id IN ({','.join(str(item) for item in duplicate_ids)})")
        )

    conn.execute(
        sa.text(f"""
            UPDATE {table}
            SET event_id = COALESCE(event_id, printf('%s:%s:%s', COALESCE(task_id, 'unknown'), node_type, node_type || '_result_persist')),
                event_key = COALESCE(event_key, printf('%s:%s:%s', COALESCE(task_id, 'unknown'), node_type, node_type || '_result_persist')),
                event_stage = COALESCE(event_stage, node_type || '_result_persist')
        """)
    )

    with op.batch_alter_table(table) as batch_op:
        batch_op.alter_column("event_id", existing_type=sa.String(length=255), nullable=False)
        batch_op.alter_column("event_key", existing_type=sa.String(length=255), nullable=False)
        batch_op.create_index("ix_data_lineage_records_event_id", ["event_id"], unique=False)
        batch_op.create_index("ix_data_lineage_records_event_key", ["event_key"], unique=True)
        batch_op.create_index("ix_data_lineage_records_event_stage", ["event_stage"], unique=False)


def downgrade() -> None:
    table = "data_lineage_records"
    with op.batch_alter_table(table) as batch_op:
        batch_op.drop_index("ix_data_lineage_records_event_stage")
        batch_op.drop_index("ix_data_lineage_records_event_key")
        batch_op.drop_index("ix_data_lineage_records_event_id")
        batch_op.drop_column("api_key_id")
        batch_op.drop_column("event_stage")
        batch_op.drop_column("event_key")
        batch_op.drop_column("event_id")
