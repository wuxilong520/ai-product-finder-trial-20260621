from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.billing.plan import PLANS
from app.billing.service import billing_service


router = APIRouter()


@router.get("/billing/plans")
def get_billing_plans():
    return {
        "plans": [
            {
                "plan_name": plan_name,
                "task_limit": config["task_limit"],
                "api_limit": config["api_limit"],
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
