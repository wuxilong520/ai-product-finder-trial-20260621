from datetime import datetime

from pydantic import BaseModel, Field


class BillingCheckoutRequest(BaseModel):
    plan_name: str = Field(..., min_length=1, description="要购买的套餐")
    provider_name: str = Field(..., min_length=1, description="支付方式：wechat_pay")


class BillingOrderRead(BaseModel):
    id: int
    workspace_id: int
    user_id: int | None = None
    plan_name: str
    status: str
    amount_cents: int
    currency: str
    provider_name: str | None = None
    external_order_id: str | None = None
    note: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BillingCheckoutResponse(BaseModel):
    order: BillingOrderRead
    payment_ready: bool
    payment_message: str
    payment_payload: dict


class BillingConfirmPaymentRequest(BaseModel):
    external_order_id: str | None = None
    note: str | None = None
