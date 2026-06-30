from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class BillingOrder(TimestampMixin, Base):
    __tablename__ = "billing_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    plan_name: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    amount_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="CNY")
    provider_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
