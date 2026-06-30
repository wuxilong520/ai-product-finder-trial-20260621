"""add auth code and challenge tables

Revision ID: 20260630_000014
Revises: 20260630_000013
Create Date: 2026-06-30 13:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260630_000014"
down_revision = "20260630_000013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_verification_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=30), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auth_verification_codes_email"), "auth_verification_codes", ["email"], unique=False)
    op.create_index(op.f("ix_auth_verification_codes_purpose"), "auth_verification_codes", ["purpose"], unique=False)
    op.create_index(op.f("ix_auth_verification_codes_expires_at"), "auth_verification_codes", ["expires_at"], unique=False)

    op.create_table(
        "auth_challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=30), nullable=False),
        sa.Column("challenge_token", sa.String(length=128), nullable=False),
        sa.Column("challenge_question", sa.Text(), nullable=False),
        sa.Column("answer_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auth_challenges_email"), "auth_challenges", ["email"], unique=False)
    op.create_index(op.f("ix_auth_challenges_purpose"), "auth_challenges", ["purpose"], unique=False)
    op.create_index(op.f("ix_auth_challenges_expires_at"), "auth_challenges", ["expires_at"], unique=False)
    op.create_index(op.f("ix_auth_challenges_challenge_token"), "auth_challenges", ["challenge_token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_challenges_challenge_token"), table_name="auth_challenges")
    op.drop_index(op.f("ix_auth_challenges_expires_at"), table_name="auth_challenges")
    op.drop_index(op.f("ix_auth_challenges_purpose"), table_name="auth_challenges")
    op.drop_index(op.f("ix_auth_challenges_email"), table_name="auth_challenges")
    op.drop_table("auth_challenges")

    op.drop_index(op.f("ix_auth_verification_codes_expires_at"), table_name="auth_verification_codes")
    op.drop_index(op.f("ix_auth_verification_codes_purpose"), table_name="auth_verification_codes")
    op.drop_index(op.f("ix_auth_verification_codes_email"), table_name="auth_verification_codes")
    op.drop_table("auth_verification_codes")
