import asyncio

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError, error_response
from app.schemas.decision import DecisionRecommendRequest, DecisionRecommendResponse
from app.services.sync_runtime_service import sync_runtime_service
from app.services.task_controller import task_controller
from app.sync.execution_bridge import execution_bridge


router = APIRouter()


@router.post("/decision/recommend", response_model=DecisionRecommendResponse)
def recommend_decision(
    payload: DecisionRecommendRequest,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    try:
        task = task_controller.submit_task(
            db,
            job_type="decision",
            job_key=f"decision:{payload.product_id}",
            payload={"product_id": payload.product_id},
            runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
                task_db,
                task_id=task_id,
                job_type="decision",
                payload={"product_id": payload.product_id},
            ),
        )
        result_wrapper = sync_runtime_service.get_task_result(task["task_id"])
        if not result_wrapper:
            result_wrapper = asyncio.run(sync_runtime_service.wait_for_result(task["task_id"], timeout=15))
        if not result_wrapper or result_wrapper.get("status") != "success":
            return error_response("DECISION_PENDING", "决策任务仍在执行，请稍后重试。", "decision", status.HTTP_202_ACCEPTED)
        result = result_wrapper["result"]["decision_result"] if "decision_result" in result_wrapper.get("result", {}) else result_wrapper["result"]
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("DECISION_ENGINE_FAILED", str(exc), "decision", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return DecisionRecommendResponse(**result)
