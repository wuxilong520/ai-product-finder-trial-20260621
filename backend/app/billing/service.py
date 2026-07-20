from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.billing.plan import PLANS
from app.billing.subscription import WorkspaceSubscription
from app.core.audit_logger import audit_logger
from app.core.config_center import config_center
from app.core.runtime import AppError
from app.quota.service import quota_service
from app.repositories.billing_order import billing_order_repository


class BillingService:
    def _build_external_order_id(self, *, order_id: int, workspace_id: int) -> str:
        stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"SHAI{workspace_id}{order_id}{stamp}"

    def _build_payment_payload(self, *, order, provider_name: str, plan: dict):
        payment_config = config_center.payment()
        is_wechat_ready = (
            bool(payment_config["wechat_pay_app_id"])
            and bool(payment_config["wechat_pay_mch_id"])
            and bool(payment_config["wechat_pay_api_v3_key"])
            and bool(payment_config["wechat_pay_private_key"])
        )
        return is_wechat_ready, {
            "provider_name": provider_name,
            "order_id": order.id,
            "plan_name": order.plan_name,
            "amount_cents": order.amount_cents,
            "currency": order.currency,
            "display_price": plan["display_price"],
            "status": "ready" if is_wechat_ready else "pending_config",
            "pay_url": None,
            "qr_code_url": None,
        }

    def get_or_create_subscription(self, db: Session, *, workspace_id: int) -> WorkspaceSubscription:
        stmt = select(WorkspaceSubscription).where(WorkspaceSubscription.workspace_id == workspace_id)
        record = db.scalar(stmt)
        if record:
            return record
        record = WorkspaceSubscription(workspace_id=workspace_id, plan_name="free", status="active")
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def apply_plan_quota(self, db: Session, *, workspace_id: int) -> WorkspaceSubscription:
        subscription = self.get_or_create_subscription(db, workspace_id=workspace_id)
        plan = PLANS.get(subscription.plan_name, PLANS["free"])
        quota = quota_service.get_or_create(
            db,
            workspace_id=workspace_id,
            daily_task_limit=plan["task_limit"],
            daily_api_limit=plan["api_limit"],
        )
        quota.daily_task_limit = plan["task_limit"]
        quota.daily_api_limit = plan["api_limit"]
        db.add(quota)
        db.commit()
        return subscription

    def create_checkout_order(
        self,
        db: Session,
        *,
        workspace_id: int,
        user_id: int | None,
        plan_name: str,
        provider_name: str,
    ):
        if plan_name not in PLANS:
            raise AppError("PLAN_NOT_FOUND", "没有找到这个套餐", "billing", 404)
        if provider_name != "wechat_pay":
            raise AppError("PAYMENT_PROVIDER_INVALID", "当前只保留微信支付通道", "billing", 400)
        if plan_name == "free":
            raise AppError("FREE_PLAN_NOT_PAYABLE", "免费版不需要购买", "billing", 400)

        plan = PLANS[plan_name]
        order = billing_order_repository.create(
            db,
            workspace_id=workspace_id,
            user_id=user_id,
            plan_name=plan_name,
            amount_cents=plan["price_cents"],
            currency="CNY",
            provider_name=provider_name,
            status="pending",
            note="等待微信支付参数配置完成后发起真实扣款",
        )
        order = billing_order_repository.update_status(
            db,
            record=order,
            status="pending",
            external_order_id=self._build_external_order_id(order_id=order.id, workspace_id=workspace_id),
        )
        payment_ready, payment_payload = self._build_payment_payload(order=order, provider_name=provider_name, plan=plan)
        audit_logger.write(
            user_id=user_id,
            action="payment_order_created",
            payload={
                "workspace_id": workspace_id,
                "order_id": order.id,
                "plan_name": plan_name,
                "provider_name": provider_name,
                "status": order.status,
            },
        )
        return order, payment_ready, payment_payload

    def mark_order_paid(self, db: Session, *, order_id: int):
        raise AppError(
            "PAYMENT_CONFIRM_DISABLED",
            "禁止直接修改订单为已支付。现在只能通过微信支付回调更新订单状态。",
            "billing",
            403,
        )

    def mark_order_paid_by_external_id(
        self,
        db: Session,
        *,
        external_order_id: str,
        note: str | None = None,
    ):
        order = billing_order_repository.get_by_external_order_id(db, external_order_id)
        if not order:
            raise AppError("ORDER_NOT_FOUND", "没有找到这个订单", "billing", 404)
        if order.status == "paid":
            return order
        billing_order_repository.update_status(
            db,
            record=order,
            status="paid",
            note=note or "微信支付异步通知确认成功",
        )
        subscription = self.get_or_create_subscription(db, workspace_id=order.workspace_id)
        subscription.plan_name = order.plan_name
        subscription.status = "active"
        db.add(subscription)
        db.commit()
        self.apply_plan_quota(db, workspace_id=order.workspace_id)
        audit_logger.write(
            user_id=order.user_id,
            action="payment_order_paid",
            payload={
                "workspace_id": order.workspace_id,
                "order_id": order.id,
                "external_order_id": external_order_id,
                "plan_name": order.plan_name,
            },
        )
        return order

    def mark_order_failed(self, db: Session, *, order_id: int, note: str | None = None):
        order = billing_order_repository.get_by_id(db, order_id)
        if not order:
            raise AppError("ORDER_NOT_FOUND", "没有找到这个订单", "billing", 404)
        return billing_order_repository.update_status(
            db,
            record=order,
            status="failed",
            note=note or "支付失败或支付被取消",
        )

    def list_orders(self, db: Session, *, workspace_id: int, limit: int = 20):
        return billing_order_repository.list_by_workspace(db, workspace_id=workspace_id, limit=limit)


billing_service = BillingService()
