from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context_no_quota
from app.billing.plan import PLANS
from app.billing.service import billing_service
from app.core.runtime import AppError
from app.schemas.billing import BillingCheckoutRequest, BillingCheckoutResponse, BillingConfirmPaymentRequest, BillingOrderRead


router = APIRouter()


@router.get("/billing/plans")
def get_billing_plans():
    return {
        "plans": [
            {
                "plan_name": plan_name,
                "task_limit": config["task_limit"],
                "api_limit": config["api_limit"],
                "price_cents": config["price_cents"],
                "display_price": config["display_price"],
                "allowed_ai_providers": config.get("allowed_ai_providers", []),
                "allowed_ai_models": config.get("allowed_ai_models", []),
                "ai_policy_note": config.get("ai_policy_note", ""),
                "supports_custom_model": config.get("supports_custom_model", False),
            }
            for plan_name, config in PLANS.items()
        ]
    }


@router.get("/billing/current")
def get_current_billing_status(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context_no_quota),
):
    subscription = billing_service.get_or_create_subscription(db, workspace_id=auth_context.workspace_id)
    plan = PLANS.get(subscription.plan_name, PLANS["free"])
    return {
        "workspace_id": auth_context.workspace_id,
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "updated_at": subscription.updated_at.isoformat(),
        "allowed_ai_providers": plan.get("allowed_ai_providers", []),
        "allowed_ai_models": plan.get("allowed_ai_models", []),
        "ai_policy_note": plan.get("ai_policy_note", ""),
        "supports_custom_model": plan.get("supports_custom_model", False),
    }


@router.post("/billing/checkout", response_model=BillingCheckoutResponse)
def create_checkout_order(
    payload: BillingCheckoutRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context_no_quota),
):
    order, payment_ready, payment_payload = billing_service.create_checkout_order(
        db,
        workspace_id=auth_context.workspace_id,
        user_id=auth_context.user_id,
        plan_name=payload.plan_name,
        provider_name=payload.provider_name,
    )
    return BillingCheckoutResponse(
        order=BillingOrderRead.model_validate(order),
        payment_ready=payment_ready,
        payment_message="支付订单已创建。" if payment_ready else "支付订单已创建，等微信支付商户参数配置完成后就能发起真实扣款。",
        payment_payload=payment_payload,
    )


@router.get("/billing/orders")
def get_billing_orders(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context_no_quota),
):
    orders = billing_service.list_orders(db, workspace_id=auth_context.workspace_id)
    return {"orders": [BillingOrderRead.model_validate(item).model_dump(mode="json") for item in orders]}


@router.post("/billing/orders/{order_id}/confirm")
def confirm_billing_order(
    order_id: int,
    payload: BillingConfirmPaymentRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context_no_quota),
):
    raise AppError(
        "PAYMENT_CONFIRM_DISABLED",
        "手动确认支付接口已关闭。现在只能通过微信支付回调通知更新订单状态。",
        "billing",
        403,
    )


@router.post("/billing/orders/{order_id}/fail")
def fail_billing_order(
    order_id: int,
    payload: BillingConfirmPaymentRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context_no_quota),
):
    order = billing_service.mark_order_failed(db, order_id=order_id, note=payload.note)
    if order.workspace_id != auth_context.workspace_id:
        return {"success": False, "message": "订单不属于当前工作区"}
    return {
        "success": True,
        "message": "订单已更新为失败状态",
        "order": BillingOrderRead.model_validate(order).model_dump(mode="json"),
    }

