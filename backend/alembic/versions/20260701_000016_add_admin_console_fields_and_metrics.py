"""add admin console fields and metrics

Revision ID: 20260701_000016
Revises: 20260630_000015
Create Date: 2026-07-01 16:40:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260701_000016"
down_revision: str | None = "20260630_000015"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "request_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_request_metrics_created_at"), "request_metrics", ["created_at"], unique=False)
    op.create_index(op.f("ix_request_metrics_method"), "request_metrics", ["method"], unique=False)
    op.create_index(op.f("ix_request_metrics_path"), "request_metrics", ["path"], unique=False)
    op.create_index(op.f("ix_request_metrics_status_code"), "request_metrics", ["status_code"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_request_metrics_status_code"), table_name="request_metrics")
    op.drop_index(op.f("ix_request_metrics_path"), table_name="request_metrics")
    op.drop_index(op.f("ix_request_metrics_method"), table_name="request_metrics")
    op.drop_index(op.f("ix_request_metrics_created_at"), table_name="request_metrics")
    op.drop_table("request_metrics")
    op.drop_column("users", "last_login_at")
