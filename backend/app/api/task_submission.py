from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.schemas.decision import DecisionRecommendRequest
from app.schemas.market import MarketAnalyzeRequest
from app.schemas.supplier import SupplierMatchRequest
from app.schemas.task import TaskSubmitRequest
from app.services.task_controller import task_controller
from app.sync.execution_bridge import execution_bridge


router = APIRouter(tags=["任务提交"])


@router.post("/tasks/market-analysis")
def submit_market_analysis_task(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return task_controller.submit_task(
        db,
        job_type="market",
        job_key=f"market:{payload.keyword.strip()}",
        payload={"keyword": payload.keyword},
        auth_context=auth_context,
        runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
            task_db,
            task_id=task_id,
            job_type="market",
            payload={"keyword": payload.keyword},
        ),
    )


@router.post("/tasks/supplier-match")
def submit_supplier_match_task(
    payload: SupplierMatchRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return task_controller.submit_task(
        db,
        job_type="supplier",
        job_key=f"supplier:{payload.keyword.strip()}",
        payload={"keyword": payload.keyword},
        auth_context=auth_context,
        runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
            task_db,
            task_id=task_id,
            job_type="supplier",
            payload={"keyword": payload.keyword},
        ),
    )


@router.post("/tasks/decision")
def submit_decision_task(
    payload: DecisionRecommendRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return task_controller.submit_task(
        db,
        job_type="decision",
        job_key=f"decision:{payload.product_id}",
        payload={"product_id": payload.product_id},
        auth_context=auth_context,
        runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
            task_db,
            task_id=task_id,
            job_type="decision",
            payload={"product_id": payload.product_id},
        ),
    )


@router.post("/task/submit")
def submit_structured_task(
    payload: TaskSubmitRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    normalized_keyword = payload.keyword.strip()
    try:
        product_id = int(normalized_keyword)
    except ValueError:
        product_id = 1

    return task_controller.submit_task(
        db,
        job_type="decision",
        job_key=f"decision:{product_id}:{payload.market_type}:{payload.decision_mode}",
        payload={
            "product_id": product_id,
            "keyword": payload.keyword,
            "market_type": payload.market_type,
            "supplier_strategy": payload.supplier_strategy,
            "cost_mode": payload.cost_mode,
            "decision_mode": payload.decision_mode,
            "user_id": auth_context.user_id,
            "workspace_id": auth_context.workspace_id,
            "api_key_id": auth_context.api_key_id,
        },
        auth_context=auth_context,
        runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
            task_db,
            task_id=task_id,
            job_type="decision",
            payload={
                "product_id": product_id,
                "keyword": payload.keyword,
                "market_type": payload.market_type,
                "supplier_strategy": payload.supplier_strategy,
                "cost_mode": payload.cost_mode,
                "decision_mode": payload.decision_mode,
                "user_id": auth_context.user_id,
                "workspace_id": auth_context.workspace_id,
                "api_key_id": auth_context.api_key_id,
            },
        ),
    )


@router.post("/task/retry/{task_id}")
def retry_task(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    existing_record = task_controller.get_task_record(db, task_id)
    existing_payload = (existing_record.result_payload or {}) if existing_record else {}
    task_input = existing_payload.get("task_input", {}) if isinstance(existing_payload.get("task_input", {}), dict) else {}
    return task_controller.retry_task(
        db,
        task_id=task_id,
        runner_factory=lambda retry_task_id, task_db: lambda: execution_bridge.execute(
            task_db,
            task_id=retry_task_id,
            job_type="decision",
            payload={
                "product_id": task_input.get("product_id", 1),
                "keyword": task_input.get("keyword", ""),
                "market_type": task_input.get("market_type", "amazon"),
                "supplier_strategy": task_input.get("supplier_strategy", "balanced"),
                "cost_mode": task_input.get("cost_mode", "estimated"),
                "decision_mode": task_input.get("decision_mode", "deep"),
                "user_id": auth_context.user_id,
                "workspace_id": auth_context.workspace_id,
                "api_key_id": auth_context.api_key_id or (existing_record.api_key_id if existing_record else None),
            },
        ),
    )
