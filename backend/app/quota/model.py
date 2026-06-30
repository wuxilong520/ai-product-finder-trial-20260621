from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class WorkspaceQuota(TimestampMixin, Base):
    __tablename__ = "workspace_quotas"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    daily_task_limit: Mapped[int] = mapped_column(nullable=False, default=10)
    daily_api_limit: Mapped[int] = mapped_column(nullable=False, default=100)
    used_task: Mapped[int] = mapped_column(nullable=False, default=0)
    used_api: Mapped[int] = mapped_column(nullable=False, default=0)
