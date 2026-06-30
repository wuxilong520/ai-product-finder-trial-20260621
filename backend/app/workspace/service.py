from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.workspace.model import Workspace


class WorkspaceService:
    def get_by_id(self, db: Session, workspace_id: int) -> Workspace | None:
        return db.get(Workspace, workspace_id)

    def get_default_for_user(self, db: Session, user: User) -> Workspace | None:
        stmt = select(Workspace).where(Workspace.owner_id == user.id).order_by(Workspace.id.asc())
        return db.scalar(stmt)

    def get_or_create_default(self, db: Session, user: User) -> Workspace:
        existing = self.get_default_for_user(db, user)
        if existing:
            return existing
        workspace = Workspace(name=f"{user.email.split('@')[0]} workspace", owner_id=user.id)
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return workspace

    def user_has_access(self, db: Session, *, user: User, workspace_id: int) -> bool:
        workspace = self.get_by_id(db, workspace_id)
        if not workspace:
            return False
        return bool(user.is_superuser or workspace.owner_id == user.id)


workspace_service = WorkspaceService()
