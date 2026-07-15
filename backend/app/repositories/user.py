from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.scalar(select(User).where(User.username == username))

    def list_all(self, db: Session) -> list[User]:
        return list(db.scalars(select(User).order_by(User.created_at.desc())))

    def create(self, db: Session, **kwargs) -> User:
        user = User(**kwargs)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def save(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository()
