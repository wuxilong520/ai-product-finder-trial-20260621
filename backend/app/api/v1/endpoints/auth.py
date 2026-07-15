import os

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, get_request_context_no_quota
from app.api_key.service import api_key_service
from app.billing.plan import PLANS
from app.billing.service import billing_service
from app.core.config import settings
from app.core.runtime import AppError
from app.schemas.auth import (
    LoginResponse,
    LogoutRequest,
    PasswordResetRequest,
    TokenRefreshRequest,
    SendCodeRequest,
    SendCodeResponse,
    UserCreate,
    UserRead,
    UserRegisterRequest,
    VerifyChallengeRequest,
    VerifyCodeLoginRequest,
)
from app.services.auth import auth_service
from app.workspace.service import workspace_service


router = APIRouter()


def _build_store_link_status() -> dict:
    shopify_read_ready = bool(
        str(settings.shopify_store_base_url or "").strip()
        and str(settings.shopify_api_key or "").strip()
        and str(settings.shopify_api_secret or "").strip()
    )
    execution_mode = (os.getenv("SHOPIFY_EXECUTION_MODE") or "mock").strip().lower()
    publish_ready = execution_mode == "real"

    return {
        "shopify": {
            "store_base_url_configured": bool(str(settings.shopify_store_base_url or "").strip()),
            "admin_read_ready": shopify_read_ready,
            "execution_mode": execution_mode,
            "oauth_status": "reserved",
            "publish_ready": publish_ready,
            "status_text": (
                "已配置 Shopify 真实读取，可拉店铺商品"
                if shopify_read_ready
                else "还没配好 Shopify 真实读取参数"
            ),
            "publish_text": (
                "真实发布已开放"
                if publish_ready
                else "真实发布还没开放，当前仍是占位执行模式"
            ),
        }
    }


def _build_payment_status() -> dict:
    wechat_ready = bool(
        str(settings.wechat_pay_app_id or "").strip()
        and str(settings.wechat_pay_mch_id or "").strip()
        and str(settings.wechat_pay_api_v3_key or "").strip()
        and str(settings.wechat_pay_private_key or "").strip()
        and str(settings.wechat_pay_notify_url or "").strip()
    )
    return {
        "wechat_pay": {
            "configured": wechat_ready,
            "manual_confirm_enabled": False,
            "checkout_ready": wechat_ready,
            "status_text": (
                "微信支付参数已配置，可进入真实支付收口"
                if wechat_ready
                else "微信支付参数还没完整配齐，当前只能先创建订单"
            ),
        }
    }


@router.post("/register", response_model=UserRead)
def register(payload: UserRegisterRequest, db: Session = Depends(db_session)):
    return auth_service.register_user(db, payload)


@router.post("/send-code", response_model=SendCodeResponse)
def send_code(payload: SendCodeRequest, db: Session = Depends(db_session)):
    result = auth_service.send_verification_code(
        db,
        email=payload.email,
        purpose=payload.purpose,
        challenge_token=payload.challenge_token,
        challenge_answer=payload.challenge_answer,
    )
    return SendCodeResponse(**result)


@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_session)):
    user = auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise AppError("LOGIN_FAILED", "账号或密码错误", "auth", 401)

    tokens = auth_service.create_login_tokens(user)
    auth_service.issue_refresh_session(db, user, tokens["refresh_token"])
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.post("/login/code", response_model=LoginResponse)
def login_with_code(payload: VerifyCodeLoginRequest, db: Session = Depends(db_session)):
    user = auth_service.login_with_code(db, email=payload.email, code=payload.code)
    tokens = auth_service.create_login_tokens(user)
    auth_service.issue_refresh_session(db, user, tokens["refresh_token"])
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(db_session)):
    user, tokens = auth_service.refresh_login(db, payload.refresh_token)
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(db_session)):
    auth_service.logout(db, payload.refresh_token)
    return {"success": True}


@router.post("/password/reset")
def reset_password(payload: PasswordResetRequest, db: Session = Depends(db_session)):
    auth_service.reset_password(db, email=payload.email, code=payload.code, new_password=payload.new_password)
    return {"success": True, "message": "密码已重置，请使用新密码登录"}


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.get("/me/overview")
def me_overview(
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
    auth_context=Depends(get_request_context_no_quota),
):
    workspace = None
    if current_user.workspace_id:
        workspace = workspace_service.get_by_id(db, current_user.workspace_id)

    subscription = billing_service.get_or_create_subscription(db, workspace_id=auth_context.workspace_id)
    plan = PLANS.get(subscription.plan_name, PLANS["free"])
    orders = billing_service.list_orders(db, workspace_id=auth_context.workspace_id, limit=5)
    api_keys = api_key_service.list_by_user(db, user_id=current_user.id)
    active_keys = [item for item in api_keys if item.status == "active"]
    latest_key = api_keys[0] if api_keys else None

    return {
        "user": UserRead.model_validate(current_user).model_dump(mode="json"),
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "owner_id": workspace.owner_id,
            "created_at": workspace.created_at.isoformat(),
            "updated_at": workspace.updated_at.isoformat(),
        } if workspace else None,
        "billing": {
            "workspace_id": auth_context.workspace_id,
            "plan_name": subscription.plan_name,
            "status": subscription.status,
            "updated_at": subscription.updated_at.isoformat(),
            "allowed_ai_providers": plan.get("allowed_ai_providers", []),
            "allowed_ai_models": plan.get("allowed_ai_models", []),
            "ai_policy_note": plan.get("ai_policy_note", ""),
            "supports_custom_model": plan.get("supports_custom_model", False),
        },
        "recent_orders": [
            {
                "id": item.id,
                "workspace_id": item.workspace_id,
                "user_id": item.user_id,
                "plan_name": item.plan_name,
                "status": item.status,
                "amount_cents": item.amount_cents,
                "currency": item.currency,
                "provider_name": item.provider_name,
                "external_order_id": item.external_order_id,
                "note": item.note,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
            }
            for item in orders
        ],
        "api_key_summary": {
            "total_keys": len(api_keys),
            "active_keys": len(active_keys),
            "latest_key_created_at": latest_key.created_at.isoformat() if latest_key else None,
            "latest_key_status": latest_key.status if latest_key else None,
        },
        "store_links": _build_store_link_status(),
        "payment_status": _build_payment_status(),
    }
