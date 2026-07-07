from __future__ import annotations

from pydantic import BaseModel


class ProductState(BaseModel):
    system_stage: str
    commercial_ready: bool
    billing_ready: bool
    execution_ready: bool
    data_maturity: str
    risk_status: str
