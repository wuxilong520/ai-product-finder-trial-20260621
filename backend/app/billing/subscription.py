from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class WorkspaceSubscription(TimestampMixin, Base):
    __tablename__ = "workspace_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    plan_name: Mapped[str] = mapped_column(String(30), nullable=False, default="free")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
