from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class DataConnection(TimestampMixin, Base):
    __tablename__ = "data_connections"
    __table_args__ = (
        UniqueConstraint("user_id", "platform", name="uq_data_connections_user_platform"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="EXPIRED")
    encrypted_access_token: Mapped[str] = mapped_column(Text, nullable=False, default="")
    encrypted_refresh_token: Mapped[str] = mapped_column(Text, nullable=False, default="")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    permission_scope: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    shop_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    external_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    connection_meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
