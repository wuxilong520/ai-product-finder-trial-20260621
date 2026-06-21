from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.platform import Platform


class PlatformRepository:
    def get_by_code(self, db: Session, code: str) -> Platform | None:
        return db.scalar(select(Platform).where(Platform.code == code))

    def list_all(self, db: Session) -> list[Platform]:
        return list(db.scalars(select(Platform).order_by(Platform.id.asc())))

    def create(self, db: Session, **kwargs) -> Platform:
        platform = Platform(**kwargs)
        db.add(platform)
        db.commit()
        db.refresh(platform)
        return platform


platform_repository = PlatformRepository()
