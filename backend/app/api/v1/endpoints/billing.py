from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.billing.alipay_gateway import alipay_gateway
from app.api.deps import db_session, get_request_context
from app.billing.plan import PLANS
from app.billing.service import billing_service
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
            }
            for plan_name, config in PLANS.items()
        ]
    }


@router.get("/billing/current")
def get_current_billing_status(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    subscription = billing_service.get_or_create_subscription(db, workspace_id=auth_context.workspace_id)
    return {
        "workspace_id": auth_context.workspace_id,
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "updated_at": subscription.updated_at.isoformat(),
    }


@router.post("/billing/checkout", response_model=BillingCheckoutResponse)
def create_checkout_order(
    payload: BillingCheckoutRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
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
        payment_message="支付订单已创建。" if payment_ready else "支付订单已创建，下一步接入你的支付宝 / 微信商户参数后即可发起真实扣款。",
        payment_payload=payment_payload,
    )


@router.get("/billing/orders")
def get_billing_orders(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    orders = billing_service.list_orders(db, workspace_id=auth_context.workspace_id)
    return {"orders": [BillingOrderRead.model_validate(item).model_dump(mode="json") for item in orders]}


@router.post("/billing/orders/{order_id}/confirm")
def confirm_billing_order(
    order_id: int,
    payload: BillingConfirmPaymentRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    order = billing_service.mark_order_paid(db, order_id=order_id)
    if order.workspace_id != auth_context.workspace_id:
        return {"success": False, "message": "订单不属于当前工作区"}
    return {
        "success": True,
        "message": "订单已确认支付，套餐和额度已更新",
        "order": BillingOrderRead.model_validate(order).model_dump(mode="json"),
    }


@router.post("/billing/orders/{order_id}/fail")
def fail_billing_order(
    order_id: int,
    payload: BillingConfirmPaymentRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    order = billing_service.mark_order_failed(db, order_id=order_id, note=payload.note)
    if order.workspace_id != auth_context.workspace_id:
        return {"success": False, "message": "订单不属于当前工作区"}
    return {
        "success": True,
        "message": "订单已更新为失败状态",
        "order": BillingOrderRead.model_validate(order).model_dump(mode="json"),
    }


@router.post("/billing/alipay/notify")
async def alipay_notify(
    request: Request,
    db: Session = Depends(db_session),
):
    body = (await request.body()).decode("utf-8")
    payload = dict(parse_qsl(body, keep_blank_values=True))
    sign = payload.pop("sign", "")
    payload.pop("sign_type", None)
    if not alipay_gateway.verify(payload, sign):
        return PlainTextResponse("failure", status_code=400)

    trade_status = payload.get("trade_status", "")
    external_order_id = payload.get("out_trade_no", "")
    if not external_order_id:
        return PlainTextResponse("failure", status_code=400)
    if trade_status in {"TRADE_SUCCESS", "TRADE_FINISHED"}:
        billing_service.mark_order_paid_by_external_id(
            db,
            external_order_id=external_order_id,
            note=f"支付宝通知成功，trade_no={payload.get('trade_no', '')}",
        )
    return PlainTextResponse("success")
