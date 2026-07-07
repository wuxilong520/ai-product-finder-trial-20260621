from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.database import SessionLocal
from app.core.runtime import AppError, error_response
from app.core.security import decode_access_token
from app.repositories.user import user_repository
from app.schemas.dashboard import (
    DashboardSourcesResponse,
    DashboardSummaryResponse,
    DashboardTasksResponse,
    DashboardTrendsResponse,
)
from app.services.dashboard_service import dashboard_service
from app.core.execution_log_layer import execution_log_layer
from app.core.execution_insight_layer import execution_insight_layer
from app.core.execution_queue import execution_queue
from app.core.feedback_loop_v2 import feedback_loop_v2
from app.core.commercial_readiness_engine import commercial_readiness_engine


router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return dashboard_service.summary(db)


@router.get("/dashboard/trends", response_model=DashboardTrendsResponse)
def get_dashboard_trends(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return dashboard_service.trends(db)


@router.get("/dashboard/tasks", response_model=DashboardTasksResponse)
def get_dashboard_tasks(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return dashboard_service.tasks(db)


@router.get("/dashboard/sources", response_model=DashboardSourcesResponse)
def get_dashboard_sources(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return dashboard_service.sources(db)


def _authenticate_dashboard_stream(token: str, db: Session):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AppError("AUTH_INVALID", "登录信息无效", "auth", 401)
    user = user_repository.get_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise AppError("AUTH_USER_INVALID", "用户不存在或已停用", "auth", 401)
    return user


@router.get("/stream/dashboard")
async def stream_dashboard(
    token: str = Query(..., description="前端登录 token"),
    db: Session = Depends(db_session),
):
    try:
        _authenticate_dashboard_stream(token, db)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)

    async def event_generator():
        last_summary = ""
        last_tasks = ""
        while True:
            loop_db = SessionLocal()
            try:
                summary = dashboard_service.summary(loop_db).model_dump(mode="json")
                tasks = dashboard_service.tasks(loop_db).model_dump(mode="json")
            finally:
                loop_db.close()
            summary_json = json.dumps(summary, ensure_ascii=False, sort_keys=True)
            tasks_json = json.dumps(tasks, ensure_ascii=False, sort_keys=True)

            if summary_json != last_summary:
                yield f"event: summary\ndata: {summary_json}\n\n"
                last_summary = summary_json

            if tasks_json != last_tasks:
                yield f"event: tasks\ndata: {tasks_json}\n\n"
                last_tasks = tasks_json

            yield "event: ping\ndata: keepalive\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/dashboard/execution")
def get_execution_dashboard(auth_context=Depends(get_request_context)):
    logs = execution_log_layer.list_logs()
    insight = execution_insight_layer.summarize()
    return {
        "records": logs,
        "insight": insight,
        "growth_metrics": feedback_loop_v2.metrics(),
        "queue_snapshot": execution_queue.snapshot(),
    }


@router.get("/dashboard/product")
def get_product_dashboard(auth_context=Depends(get_request_context)):
    return commercial_readiness_engine.evaluate()
