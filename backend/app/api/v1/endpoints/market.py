import asyncio

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.market import MarketAnalyzeRequest, MarketAnalyzeResponse
from app.services.sync_runtime_service import sync_runtime_service
from app.services.task_controller import task_controller
from app.sync.execution_bridge import execution_bridge


router = APIRouter()


@router.post("/market/analyze", response_model=MarketAnalyzeResponse)
def analyze_market_keyword(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        task = task_controller.submit_task(
            db,
            job_type="market",
            job_key=f"market:{payload.keyword.strip()}",
            payload={"keyword": payload.keyword, "region": payload.region, "category": payload.category},
            auth_context=auth_context,
            runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
                task_db,
                task_id=task_id,
                job_type="market",
                payload={
                    "keyword": payload.keyword,
                    "region": payload.region,
                    "category": payload.category,
                    "workspace_id": auth_context.workspace_id,
                    "user_id": auth_context.user_id,
                },
            ),
        )
        result_wrapper = sync_runtime_service.get_task_result(task["task_id"])
        if not result_wrapper:
            result_wrapper = asyncio.run(sync_runtime_service.wait_for_result(task["task_id"], timeout=15))
        if not result_wrapper or result_wrapper.get("status") != "success":
            return error_response("MARKET_ANALYZE_PENDING", "市场分析任务仍在执行，请稍后重试。", "market", status.HTTP_202_ACCEPTED)
        result = result_wrapper["result"]
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_ANALYZE_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return MarketAnalyzeResponse(**result)


@router.post("/market/intelligence", response_model=MarketAnalyzeResponse)
def market_intelligence(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        result = market_intelligence_engine.analyze_keyword(
            db,
            payload.keyword,
            region=payload.region,
            category=payload.category,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_INTELLIGENCE_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return MarketAnalyzeResponse(**result)


@router.post("/market/radar", response_model=MarketAnalyzeResponse)
def market_radar(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        result = market_intelligence_engine.analyze_keyword(
            db,
            payload.keyword,
            region=payload.region,
            category=payload.category,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_RADAR_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return MarketAnalyzeResponse(**result)
