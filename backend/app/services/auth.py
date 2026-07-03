from datetime import UTC, datetime, timedelta
import random
import secrets

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.audit_logger import audit_logger
from app.core.runtime import AppError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.api_key.service import api_key_service
from app.repositories.auth_identity import auth_identity_repository
from app.repositories.user import user_repository
from app.schemas.auth import AuthChallengeResponse, UserCreate, UserRegisterRequest
from app.billing.service import billing_service
from app.services.email_service import email_service
from app.workspace.service import workspace_service


class AuthService:
    def _resolve_registration_role(self, *, requested_role: str | None = None, system_init: bool = False) -> str:
        role = (requested_role or "user").strip().lower()
        if role == "owner" and not system_init:
            raise PermissionError("owner 只能由系统初始化创建")
        if not system_init:
            return "user"
        return role

    def _generate_code(self) -> str:
        return f"{random.randint(100000, 999999)}"

    def _should_require_challenge(self, db: Session, email: str, purpose: str) -> bool:
        existing = auth_identity_repository.get_latest_active_challenge_by_email(db, email, purpose)
        if existing:
            return True
        return random.random() < settings.auth_challenge_rate

    def _build_challenge(self, db: Session, email: str, purpose: str) -> AuthChallengeResponse:
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        answer = str(a + b)
        record = auth_identity_repository.create_challenge(
            db,
            email=email,
            purpose=purpose,
            challenge_token=secrets.token_urlsafe(24),
            challenge_question=f"为了确认是你本人，请回答：{a} + {b} = ?",
            answer_hash=get_password_hash(answer),
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.auth_challenge_expire_minutes),
        )
        return AuthChallengeResponse(
            challenge_token=record.challenge_token,
            challenge_question=record.challenge_question,
            expires_in_seconds=settings.auth_challenge_expire_minutes * 60,
        )

    def register_user(self, db: Session, payload: UserCreate | UserRegisterRequest):
        if isinstance(payload, UserRegisterRequest):
            self.verify_code(db, email=payload.email, code=payload.verification_code, purpose="register")
        existing = user_repository.get_by_email(db, payload.email)
        if existing:
            raise AppError("EMAIL_EXISTS", "邮箱已经注册过了", "auth", 400)

        user = user_repository.create(
            db,
            email=payload.email,
            password_hash=get_password_hash(payload.password),
            full_name=payload.full_name,
            role=self._resolve_registration_role(system_init=False),
            is_active=True,
            is_superuser=False,
        )
        workspace = workspace_service.get_or_create_default(db, user)
        user.workspace_id = workspace.id
        db.add(user)
        db.commit()
        db.refresh(user)
        api_key_service.create_key(db, workspace_id=workspace.id, user_id=user.id)
        billing_service.apply_plan_quota(db, workspace_id=workspace.id)
        return user

    def send_verification_code(self, db: Session, email: str, purpose: str, challenge_answer: str | None = None, challenge_token: str | None = None):
        challenge_verified = False
        if challenge_token and challenge_answer:
            self.verify_challenge(db, challenge_token, challenge_answer)
            challenge_verified = True

        if not challenge_verified and self._should_require_challenge(db, email, purpose):
            return {
                "success": False,
                "message": "需要先完成安全验证",
                "challenge": self._build_challenge(db, email, purpose),
            }

        auth_identity_repository.purge_codes(db, email, purpose)
        code = self._generate_code()
        auth_identity_repository.create_code(
            db,
            email=email,
            purpose=purpose,
            code_hash=get_password_hash(code),
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.auth_code_expire_minutes),
        )
        delivery_result = email_service.send_verification_code(email, code, purpose)
        return {
            "success": True,
            "message": delivery_result.get("message", f"验证码已发送到 {email}"),
            "challenge": None,
        }

    def verify_code(self, db: Session, email: str, code: str, purpose: str):
        record = auth_identity_repository.get_latest_active_code(db, email, purpose)
        if not record:
            raise AppError("CODE_NOT_FOUND", "验证码不存在或已过期，请重新获取", "auth", 400)
        auth_identity_repository.touch_code_attempt(db, record)
        if not verify_password(code, record.code_hash):
            raise AppError("CODE_INVALID", "验证码不正确", "auth", 400)
        auth_identity_repository.mark_code_used(db, record)
        return True

    def verify_challenge(self, db: Session, challenge_token: str, answer: str):
        record = auth_identity_repository.get_active_challenge(db, challenge_token)
        if not record:
            raise AppError("CHALLENGE_NOT_FOUND", "当前验证已失效，请重新获取验证码", "auth", 400)
        auth_identity_repository.touch_challenge_attempt(db, record)
        if not verify_password(answer.strip(), record.answer_hash):
            raise AppError("CHALLENGE_INVALID", "安全验证答案不正确", "auth", 400)
        auth_identity_repository.resolve_challenge(db, record)
        return True

    def authenticate_user(self, db: Session, email: str, password: str):
        user = user_repository.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            raise AppError("USER_BANNED", "你的账号已被封号，请联系团队处理", "auth", 403)
        user.last_login_at = datetime.now(UTC)
        user_repository.save(db, user)
        audit_logger.write(
            user_id=user.id,
            action="user_login_password",
            payload={"email": user.email, "workspace_id": user.workspace_id},
        )
        return user

    def login_with_code(self, db: Session, email: str, code: str):
        self.verify_code(db, email=email, code=code, purpose="login")
        user = user_repository.get_by_email(db, email)
        if not user:
            raise AppError("USER_NOT_FOUND", "这个邮箱还没有注册，请先注册", "auth", 404)
        if not user.is_active:
            raise AppError("USER_BANNED", "你的账号已被封号，请联系团队处理", "auth", 403)
        user.last_login_at = datetime.now(UTC)
        user_repository.save(db, user)
        audit_logger.write(
            user_id=user.id,
            action="user_login_code",
            payload={"email": user.email, "workspace_id": user.workspace_id},
        )
        return user

    def reset_password(self, db: Session, email: str, code: str, new_password: str):
        self.verify_code(db, email=email, code=code, purpose="reset_password")
        user = user_repository.get_by_email(db, email)
        if not user:
            raise AppError("USER_NOT_FOUND", "这个邮箱还没有注册", "auth", 404)
        user.password_hash = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create_login_token(self, user) -> str:
        return create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
            extra_payload={
                "workspace_id": user.workspace_id,
                "role": getattr(user, "role", "user"),
            },
        )

    def ensure_default_admin(self, db: Session):
        existing = user_repository.get_by_email(db, settings.first_superuser_email)
        if existing:
            return existing
        user = user_repository.create(
            db,
            email=settings.first_superuser_email,
            password_hash=get_password_hash(settings.first_superuser_password),
            full_name="System Admin",
            role=self._resolve_registration_role(requested_role="owner", system_init=True),
            is_active=True,
            is_superuser=True,
        )
        workspace = workspace_service.get_or_create_default(db, user)
        user.workspace_id = workspace.id
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


auth_service = AuthService()
