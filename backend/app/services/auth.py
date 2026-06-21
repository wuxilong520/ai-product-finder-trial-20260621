from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.runtime import AppError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.user import user_repository
from app.schemas.auth import UserCreate


class AuthService:
    def register_user(self, db: Session, payload: UserCreate):
        existing = user_repository.get_by_email(db, payload.email)
        if existing:
            raise AppError("EMAIL_EXISTS", "邮箱已经注册过了", "auth", 400)

        return user_repository.create(
            db,
            email=payload.email,
            password_hash=get_password_hash(payload.password),
            full_name=payload.full_name,
            is_active=True,
            is_superuser=False,
        )

    def authenticate_user(self, db: Session, email: str, password: str):
        user = user_repository.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_login_token(self, user) -> str:
        return create_access_token(subject=user.id, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))

    def ensure_default_admin(self, db: Session):
        existing = user_repository.get_by_email(db, settings.first_superuser_email)
        if existing:
            return existing
        return user_repository.create(
            db,
            email=settings.first_superuser_email,
            password_hash=get_password_hash(settings.first_superuser_password),
            full_name="System Admin",
            is_active=True,
            is_superuser=True,
        )


auth_service = AuthService()
