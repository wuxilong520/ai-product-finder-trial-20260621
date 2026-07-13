"""upgrade v5.1 shopify oauth

Revision ID: 20260710_000027
Revises: 20260710_000026
Create Date: 2026-07-10 21:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_000027"
down_revision = "20260710_000026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("data_connections", sa.Column("encrypted_access_token", sa.Text(), nullable=False, server_default=""))
    op.add_column("data_connections", sa.Column("encrypted_refresh_token", sa.Text(), nullable=False, server_default=""))
    op.add_column("data_connections", sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("data_connections", sa.Column("last_sync_error", sa.Text(), nullable=True))
    op.execute("UPDATE data_connections SET encrypted_access_token = access_token, encrypted_refresh_token = refresh_token")
    op.drop_column("data_connections", "access_token")
    op.drop_column("data_connections", "refresh_token")
    op.add_column("sync_jobs", sa.Column("platform", sa.String(length=30), nullable=True))
    op.add_column("sync_jobs", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sync_jobs", sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_sync_jobs_platform", "sync_jobs", ["platform"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sync_jobs_platform", table_name="sync_jobs")
    op.drop_column("sync_jobs", "finished_at")
    op.drop_column("sync_jobs", "started_at")
    op.drop_column("sync_jobs", "platform")
    op.add_column("data_connections", sa.Column("refresh_token", sa.Text(), nullable=False, server_default=""))
    op.add_column("data_connections", sa.Column("access_token", sa.Text(), nullable=False, server_default=""))
    op.execute("UPDATE data_connections SET access_token = encrypted_access_token, refresh_token = encrypted_refresh_token")
    op.drop_column("data_connections", "last_sync_error")
    op.drop_column("data_connections", "last_synced_at")
    op.drop_column("data_connections", "encrypted_refresh_token")
    op.drop_column("data_connections", "encrypted_access_token")
