"""add governance fields to decision tables

Revision ID: 20260629_000008
Revises: 20260629_000007
Create Date: 2026-06-29 18:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260629_000008"
down_revision = "20260629_000007"
branch_labels = None
depends_on = None


def _json_type():
    return sa.JSON()


def upgrade() -> None:
    op.add_column("decision_recommendations", sa.Column("source_id", sa.String(length=255), nullable=True))
    op.add_column("decision_recommendations", sa.Column("source_type", sa.String(length=50), nullable=True))
    op.add_column("decision_recommendations", sa.Column("lineage_chain", _json_type(), nullable=False, server_default="[]"))
    op.add_column("decision_recommendations", sa.Column("truth_level", sa.String(length=20), nullable=True))
    op.add_column("decision_recommendations", sa.Column("confidence_score", sa.Numeric(6, 4), nullable=True))
    op.add_column("decision_recommendations", sa.Column("freshness_score", sa.Numeric(6, 4), nullable=True))
    op.add_column("decision_recommendations", sa.Column("market_fit_score", sa.Numeric(5, 2), nullable=True))
    op.add_column("decision_recommendations", sa.Column("supplier_fit_score", sa.Numeric(5, 2), nullable=True))

    op.add_column("business_truth_decisions", sa.Column("source_id", sa.String(length=255), nullable=True))
    op.add_column("business_truth_decisions", sa.Column("source_type", sa.String(length=50), nullable=True))
    op.add_column("business_truth_decisions", sa.Column("lineage_chain", _json_type(), nullable=False, server_default="[]"))
    op.add_column("business_truth_decisions", sa.Column("confidence_score", sa.Numeric(6, 4), nullable=True))
    op.add_column("business_truth_decisions", sa.Column("freshness_score", sa.Numeric(6, 4), nullable=True))


def downgrade() -> None:
    op.drop_column("business_truth_decisions", "freshness_score")
    op.drop_column("business_truth_decisions", "confidence_score")
    op.drop_column("business_truth_decisions", "lineage_chain")
    op.drop_column("business_truth_decisions", "source_type")
    op.drop_column("business_truth_decisions", "source_id")

    op.drop_column("decision_recommendations", "supplier_fit_score")
    op.drop_column("decision_recommendations", "market_fit_score")
    op.drop_column("decision_recommendations", "freshness_score")
    op.drop_column("decision_recommendations", "confidence_score")
    op.drop_column("decision_recommendations", "truth_level")
    op.drop_column("decision_recommendations", "lineage_chain")
    op.drop_column("decision_recommendations", "source_type")
    op.drop_column("decision_recommendations", "source_id")
