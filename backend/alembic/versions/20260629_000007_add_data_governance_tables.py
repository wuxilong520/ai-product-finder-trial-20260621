"""add data governance tables

Revision ID: 20260629_000007
Revises: 20260623_000006
Create Date: 2026-06-29 16:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260629_000007"
down_revision = "20260623_000006"
branch_labels = None
depends_on = None


def _json_type():
    return sa.JSON()


def upgrade() -> None:
    op.create_table(
        "data_source_registry",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_data_source_registry_source_type", "data_source_registry", ["source_type"], unique=False)
    op.create_index("ix_data_source_registry_provider_name", "data_source_registry", ["provider_name"], unique=False)

    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sync_jobs_job_type", "sync_jobs", ["job_type"], unique=False)
    op.create_index("ix_sync_jobs_status", "sync_jobs", ["status"], unique=False)

    op.create_table(
        "data_lineage_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=False),
        sa.Column("lineage_chain", _json_type(), nullable=False),
        sa.Column("transform_steps", _json_type(), nullable=False),
        sa.Column("created_at", sa.Text(), nullable=False),
    )
    op.create_index("ix_data_lineage_records_source_id", "data_lineage_records", ["source_id"], unique=False)

    op.create_table(
        "data_quality_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("data_id", sa.String(length=255), nullable=False),
        sa.Column("truth_level", sa.String(length=20), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("freshness_score", sa.Float(), nullable=False),
        sa.Column("reliability_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_data_quality_history_data_id", "data_quality_history", ["data_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_data_quality_history_data_id", table_name="data_quality_history")
    op.drop_table("data_quality_history")
    op.drop_index("ix_data_lineage_records_source_id", table_name="data_lineage_records")
    op.drop_table("data_lineage_records")
    op.drop_index("ix_sync_jobs_status", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_job_type", table_name="sync_jobs")
    op.drop_table("sync_jobs")
    op.drop_index("ix_data_source_registry_provider_name", table_name="data_source_registry")
    op.drop_index("ix_data_source_registry_source_type", table_name="data_source_registry")
    op.drop_table("data_source_registry")
