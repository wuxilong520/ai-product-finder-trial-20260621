from collections.abc import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.api_key.validator import api_key_validator
from app.core.database import get_db
from app.core.runtime import AppError
from app.core.security import decode_access_token
from app.middleware.auth_middleware import RequestAuthContext
from app.models.user import User
from app.quota.service import quota_service
from app.repositories.user import user_repository
from app.workspace.service import workspace_service

def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(db_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("AUTH_MISSING", "缺少登录信息", "auth", 401)
    token = authorization.removeprefix("Bearer ").strip()
    if token.startswith("cbp_"):
        key_record = api_key_validator.validate(db, token)
        if not key_record:
            raise AppError("API_KEY_INVALID", "API Key 无效", "auth", 401)
        user = user_repository.get_by_id(db, key_record.user_id)
        if not user or not user.is_active:
            raise AppError("AUTH_USER_INVALID", "用户不存在或已停用", "auth", 401)
        return user

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AppError("AUTH_INVALID", "登录信息无效", "auth", 401)

    user = user_repository.get_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise AppError("AUTH_USER_INVALID", "用户不存在或已停用", "auth", 401)
    return user


def get_request_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_session),
    authorization: str | None = Header(default=None),
) -> RequestAuthContext:
    workspace = workspace_service.get_or_create_default(db, current_user)
    api_key_id = None
    if authorization and authorization.startswith("Bearer cbp_"):
        raw_key = authorization.removeprefix("Bearer ").strip()
        key_record = api_key_validator.validate(db, raw_key)
        if not key_record:
            raise AppError("API_KEY_INVALID", "API Key 无效", "auth", 401)
        if key_record.workspace_id != workspace.id and not current_user.is_superuser:
            raise AppError("WORKSPACE_DENIED", "你没有这个工作区的权限", "auth", 403)
        api_key_id = key_record.id
    from app.billing.service import billing_service

    billing_service.apply_plan_quota(db, workspace_id=workspace.id)
    quota_service.consume_api(db, workspace_id=workspace.id)
    return RequestAuthContext(
        user_id=current_user.id,
        workspace_id=workspace.id,
        role=getattr(current_user, "role", "owner"),
        api_key_id=api_key_id,
    )
