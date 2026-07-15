"""add user auth refresh tokens

Revision ID: 20260714_000033
Revises: 20260713_000032
Create Date: 2026-07-14 10:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260714_000033"
down_revision = "20260713_000032"
branch_labels = None
depends_on = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    if not _column_exists(bind, "users", "username"):
        op.add_column("users", sa.Column("username", sa.String(length=80), nullable=True))
    if not _column_exists(bind, "users", "status"):
        op.add_column("users", sa.Column("status", sa.String(length=20), nullable=False, server_default="active"))
    if not _column_exists(bind, "users", "failed_login_attempts"):
        op.add_column("users", sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"))
    if not _column_exists(bind, "users", "locked_until"):
        op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))

    user_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("email", sa.String()),
        sa.column("username", sa.String()),
        sa.column("status", sa.String()),
        sa.column("failed_login_attempts", sa.Integer()),
    )
    rows = bind.execute(sa.select(user_table.c.id, user_table.c.email, user_table.c.username).order_by(user_table.c.id.asc())).all()
    used_usernames: set[str] = set()
    for row in rows:
        preferred = str(row.username or "").strip() or str(row.email or "").split("@", 1)[0].strip() or f"user{row.id}"
        username = preferred[:80]
        suffix = 2
        while username in used_usernames:
            base = preferred[: max(1, 80 - len(f"_{suffix}"))]
            username = f"{base}_{suffix}"
            suffix += 1
        used_usernames.add(username)
        bind.execute(
            sa.update(user_table)
            .where(user_table.c.id == row.id)
            .values(
                username=username[:80],
                status="active",
                failed_login_attempts=0,
            )
        )

    if not _index_exists(bind, "users", "ix_users_username"):
        op.create_index("ix_users_username", "users", ["username"], unique=True)
    if _column_exists(bind, "users", "username") and bind.dialect.name != "sqlite":
        op.alter_column("users", "username", nullable=False)

    if not _column_exists(bind, "products", "workspace_id"):
        if bind.dialect.name == "sqlite":
            op.add_column("products", sa.Column("workspace_id", sa.Integer(), nullable=True))
        else:
            op.add_column(
                "products",
                sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True),
            )

    product_table = sa.table(
        "products",
        sa.column("id", sa.Integer()),
        sa.column("created_by_user_id", sa.Integer()),
        sa.column("workspace_id", sa.Integer()),
    )
    user_table_for_products = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("workspace_id", sa.Integer()),
    )
    user_workspace_map = {
        row.id: row.workspace_id
        for row in bind.execute(sa.select(user_table_for_products.c.id, user_table_for_products.c.workspace_id)).all()
    }
    product_rows = bind.execute(sa.select(product_table.c.id, product_table.c.created_by_user_id, product_table.c.workspace_id).order_by(product_table.c.id.asc())).all()
    for row in product_rows:
        if row.workspace_id is not None:
            continue
        workspace_id = user_workspace_map.get(row.created_by_user_id)
        if workspace_id is None:
            continue
        bind.execute(
            sa.update(product_table)
            .where(product_table.c.id == row.id)
            .values(workspace_id=workspace_id)
        )
    if not _index_exists(bind, "products", "ix_products_workspace_id"):
        op.create_index("ix_products_workspace_id", "products", ["workspace_id"], unique=False)

    if not _table_exists(bind, "auth_refresh_tokens"):
        op.create_table(
            "auth_refresh_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True),
            sa.Column("token_jti", sa.String(length=128), nullable=False),
            sa.Column("token_hash", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_auth_refresh_tokens_user_id", "auth_refresh_tokens", ["user_id"], unique=False)
        op.create_index("ix_auth_refresh_tokens_workspace_id", "auth_refresh_tokens", ["workspace_id"], unique=False)
        op.create_index("ix_auth_refresh_tokens_token_jti", "auth_refresh_tokens", ["token_jti"], unique=True)
        op.create_index("ix_auth_refresh_tokens_status", "auth_refresh_tokens", ["status"], unique=False)
        op.create_index("ix_auth_refresh_tokens_expires_at", "auth_refresh_tokens", ["expires_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "auth_refresh_tokens"):
        op.drop_index("ix_auth_refresh_tokens_expires_at", table_name="auth_refresh_tokens")
        op.drop_index("ix_auth_refresh_tokens_status", table_name="auth_refresh_tokens")
        op.drop_index("ix_auth_refresh_tokens_token_jti", table_name="auth_refresh_tokens")
        op.drop_index("ix_auth_refresh_tokens_workspace_id", table_name="auth_refresh_tokens")
        op.drop_index("ix_auth_refresh_tokens_user_id", table_name="auth_refresh_tokens")
        op.drop_table("auth_refresh_tokens")

    if _index_exists(bind, "users", "ix_users_username"):
        op.drop_index("ix_users_username", table_name="users")
    if _index_exists(bind, "products", "ix_products_workspace_id"):
        op.drop_index("ix_products_workspace_id", table_name="products")
    if _column_exists(bind, "products", "workspace_id"):
        op.drop_column("products", "workspace_id")
    if _column_exists(bind, "users", "locked_until"):
        op.drop_column("users", "locked_until")
    if _column_exists(bind, "users", "failed_login_attempts"):
        op.drop_column("users", "failed_login_attempts")
    if _column_exists(bind, "users", "status"):
        op.drop_column("users", "status")
    if _column_exists(bind, "users", "username"):
        op.drop_column("users", "username")
