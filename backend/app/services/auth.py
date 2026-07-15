from datetime import UTC, datetime, timedelta
import random
import secrets
import re

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.audit_logger import audit_logger
from app.core.runtime import AppError
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.api_key.service import api_key_service
from app.repositories.auth_identity import auth_identity_repository
from app.repositories.auth_session import auth_session_repository
from app.repositories.user import user_repository
from app.schemas.auth import AuthChallengeResponse, UserCreate, UserRegisterRequest
from app.billing.service import billing_service
from app.services.email_service import email_service
from app.workspace.service import workspace_service


class AuthService:
    login_failure_limit = 5

    def _is_user_active(self, user) -> bool:
        return bool(getattr(user, "is_active", False)) and str(getattr(user, "status", "active")).lower() == "active"

    def _resolve_registration_role(self, *, requested_role: str | None = None, system_init: bool = False) -> str:
        role = (requested_role or "user").strip().lower()
        if role == "owner" and not system_init:
            raise PermissionError("owner 只能由系统初始化创建")
        if not system_init:
            return "member"
        return role

    def _resolve_username(self, email: str, username: str | None = None) -> str:
        candidate = str(username or "").strip()
        if candidate:
            return candidate[:80]
        local_part = email.split("@", 1)[0]
        normalized = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fa5]+", "_", local_part).strip("_")
        return (normalized or local_part or "member")[:80]

    def _resolve_unique_username(self, db: Session, email: str, username: str | None = None) -> str:
        base = self._resolve_username(email, username)
        candidate = base
        suffix = 2
        while user_repository.get_by_username(db, candidate):
            tail = f"_{suffix}"
            candidate = f"{base[: max(1, 80 - len(tail))]}{tail}"
            suffix += 1
        return candidate

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
            username=self._resolve_unique_username(db, payload.email, getattr(payload, "username", None)),
            password_hash=get_password_hash(payload.password),
            full_name=payload.full_name,
            role=self._resolve_registration_role(system_init=False),
            status="active",
            is_active=True,
            is_superuser=False,
            failed_login_attempts=0,
            locked_until=None,
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
        if user.locked_until and user.locked_until > datetime.now(UTC):
            raise AppError("LOGIN_LOCKED", "账号暂时被锁定，请稍后再试", "auth", 403)
        if not verify_password(password, user.password_hash):
            self._record_failed_login(db, user)
            return None
        if not self._is_user_active(user):
            raise AppError("USER_BANNED", "你的账号已被封号，请联系团队处理", "auth", 403)
        self._clear_failed_login(db, user)
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
        if not self._is_user_active(user):
            raise AppError("USER_BANNED", "你的账号已被封号，请联系团队处理", "auth", 403)
        self._clear_failed_login(db, user)
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
        self._clear_failed_login(db, user)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create_login_tokens(self, user) -> dict:
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
            extra_payload={
                "workspace_id": user.workspace_id,
                "role": getattr(user, "role", "user"),
                "status": getattr(user, "status", "active"),
            },
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            extra_payload={
                "workspace_id": user.workspace_id,
                "role": getattr(user, "role", "member"),
                "status": getattr(user, "status", "active"),
            },
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    def issue_refresh_session(self, db: Session, user, refresh_token: str) -> None:
        payload = self._decode_token(refresh_token)
        auth_session_repository.create(
            db,
            user_id=user.id,
            workspace_id=user.workspace_id,
            token_jti=str(payload.get("jti") or ""),
            token=refresh_token,
            expires_at=datetime.fromtimestamp(int(payload["exp"]), tz=UTC),
        )

    def refresh_login(self, db: Session, refresh_token: str):
        payload = self._decode_token(refresh_token)
        if payload.get("token_type") != "refresh":
            raise AppError("TOKEN_INVALID", "刷新令牌无效", "auth", 401)
        token_jti = str(payload.get("jti") or "")
        record = auth_session_repository.get_active_by_jti(db, token_jti)
        if not record:
            raise AppError("TOKEN_INVALID", "刷新令牌已失效", "auth", 401)
        user = user_repository.get_by_id(db, int(payload.get("sub") or 0))
        if not user or not self._is_user_active(user):
            raise AppError("AUTH_USER_INVALID", "用户不存在或已停用", "auth", 401)
        auth_session_repository.touch(db, record)
        tokens = self.create_login_tokens(user)
        self.issue_refresh_session(db, user, tokens["refresh_token"])
        return user, tokens

    def logout(self, db: Session, refresh_token: str | None):
        if refresh_token:
            auth_session_repository.revoke_by_token(db, refresh_token)

    def _decode_token(self, token: str) -> dict:
        from app.core.security import decode_access_token

        return decode_access_token(token)

    def _record_failed_login(self, db: Session, user) -> None:
        user.failed_login_attempts = int(getattr(user, "failed_login_attempts", 0)) + 1
        if user.failed_login_attempts >= self.login_failure_limit:
            user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
        user_repository.save(db, user)

    def _clear_failed_login(self, db: Session, user) -> None:
        if int(getattr(user, "failed_login_attempts", 0)) == 0 and getattr(user, "locked_until", None) is None:
            return
        user.failed_login_attempts = 0
        user.locked_until = None
        user_repository.save(db, user)

    def ensure_default_admin(self, db: Session):
        existing = user_repository.get_by_email(db, settings.first_superuser_email)
        if existing:
            return existing
        user = user_repository.create(
            db,
            email=settings.first_superuser_email,
            username=self._resolve_unique_username(db, settings.first_superuser_email, "admin"),
            password_hash=get_password_hash(settings.first_superuser_password),
            full_name="System Admin",
            role=self._resolve_registration_role(requested_role="owner", system_init=True),
            status="active",
            is_active=True,
            is_superuser=True,
            failed_login_attempts=0,
            locked_until=None,
        )
        workspace = workspace_service.get_or_create_default(db, user)
        user.workspace_id = workspace.id
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


auth_service = AuthService()
