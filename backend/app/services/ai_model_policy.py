from __future__ import annotations

from sqlalchemy.orm import Session

from app.billing.plan import PLANS
from app.billing.service import billing_service
from app.core.runtime import AppError


class AIModelPolicyService:
    def get_plan_name(self, db: Session, *, workspace_id: int | None) -> str:
        if not workspace_id:
            return "free"
        subscription = billing_service.get_or_create_subscription(db, workspace_id=workspace_id)
        if subscription.plan_name in PLANS:
            return subscription.plan_name
        return "free"

    def get_plan_config(self, db: Session, *, workspace_id: int | None) -> dict:
        plan_name = self.get_plan_name(db, workspace_id=workspace_id)
        return {
            "plan_name": plan_name,
            **PLANS.get(plan_name, PLANS["free"]),
        }

    def get_allowed_provider_ids(self, db: Session, *, workspace_id: int | None) -> list[str]:
        config = self.get_plan_config(db, workspace_id=workspace_id)
        return list(config.get("allowed_ai_providers") or [])

    def get_allowed_model_names(self, db: Session, *, workspace_id: int | None) -> list[str]:
        config = self.get_plan_config(db, workspace_id=workspace_id)
        return list(config.get("allowed_ai_models") or [])

    def ensure_provider_allowed(
        self,
        db: Session,
        *,
        workspace_id: int | None,
        provider_id: str | None,
    ) -> None:
        if not provider_id:
            return
        allowed_provider_ids = self.get_allowed_provider_ids(db, workspace_id=workspace_id)
        if provider_id not in allowed_provider_ids:
            plan_name = self.get_plan_name(db, workspace_id=workspace_id)
            raise AppError(
                "AI_MODEL_PLAN_DENIED",
                f"当前套餐 {plan_name} 不能使用 {provider_id}，请先升级套餐。",
                "ai",
                403,
            )

    def ensure_model_allowed(
        self,
        db: Session,
        *,
        workspace_id: int | None,
        model_name: str | None,
    ) -> None:
        if not model_name:
            return
        allowed_model_names = self.get_allowed_model_names(db, workspace_id=workspace_id)
        if model_name not in allowed_model_names:
            plan_name = self.get_plan_name(db, workspace_id=workspace_id)
            raise AppError(
                "AI_MODEL_PLAN_DENIED",
                f"当前套餐 {plan_name} 不能使用 {model_name}，请先升级套餐。",
                "ai",
                403,
            )


ai_model_policy_service = AIModelPolicyService()
