"""add async task fields and result payloads

Revision ID: 20260629_000009
Revises: 20260629_000008
Create Date: 2026-06-29 19:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260629_000009"
down_revision = "20260629_000008"
branch_labels = None
depends_on = None


def _json_type():
    return sa.JSON()


def upgrade() -> None:
    op.add_column("sync_jobs", sa.Column("result_payload", _json_type(), nullable=True))

    op.add_column("decision_recommendations", sa.Column("task_id", sa.Integer(), nullable=True))
    op.add_column("decision_recommendations", sa.Column("result_json", _json_type(), nullable=True))

    op.add_column("business_truth_decisions", sa.Column("task_id", sa.Integer(), nullable=True))
    op.add_column("business_truth_decisions", sa.Column("decision_json", _json_type(), nullable=True))

    op.create_index("ix_decision_recommendations_task_id", "decision_recommendations", ["task_id"], unique=False)
    op.create_index("ix_business_truth_decisions_task_id", "business_truth_decisions", ["task_id"], unique=False)

    op.drop_index("ix_decision_recommendations_product_id", table_name="decision_recommendations")
    op.create_index("ix_decision_recommendations_product_id", "decision_recommendations", ["product_id"], unique=False)

    op.drop_index("ix_business_truth_decisions_product_id", table_name="business_truth_decisions")
    op.create_index("ix_business_truth_decisions_product_id", "business_truth_decisions", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_business_truth_decisions_product_id", table_name="business_truth_decisions")
    op.create_index("ix_business_truth_decisions_product_id", "business_truth_decisions", ["product_id"], unique=True)

    op.drop_index("ix_decision_recommendations_product_id", table_name="decision_recommendations")
    op.create_index("ix_decision_recommendations_product_id", "decision_recommendations", ["product_id"], unique=True)

    op.drop_index("ix_business_truth_decisions_task_id", table_name="business_truth_decisions")
    op.drop_index("ix_decision_recommendations_task_id", table_name="decision_recommendations")

    op.drop_column("business_truth_decisions", "decision_json")
    op.drop_column("business_truth_decisions", "task_id")

    op.drop_column("decision_recommendations", "result_json")
    op.drop_column("decision_recommendations", "task_id")

    op.drop_column("sync_jobs", "result_payload")
