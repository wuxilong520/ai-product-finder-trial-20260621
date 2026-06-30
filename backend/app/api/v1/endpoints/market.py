import asyncio

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
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
    current_user=Depends(get_current_user),
):
    try:
        task = task_controller.submit_task(
            db,
            job_type="market",
            job_key=f"market:{payload.keyword.strip()}",
            payload={"keyword": payload.keyword},
            runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
                task_db,
                task_id=task_id,
                job_type="market",
                payload={"keyword": payload.keyword},
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
