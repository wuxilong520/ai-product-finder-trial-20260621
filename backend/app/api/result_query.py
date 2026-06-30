from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError
from app.repositories.data_governance import sync_job_repository
from app.services.task_controller import task_controller


router = APIRouter(tags=["任务结果"])


@router.get("/task/list")
def get_task_list(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return task_controller.list_tasks(db, auth_context=auth_context)


@router.get("/task/{task_id}")
def get_task_status(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    record = sync_job_repository.get_by_id(db, task_id)
    if not record or record.workspace_id != auth_context.workspace_id:
        raise AppError("TASK_NOT_FOUND", "没有找到这个任务", "task", 404)
    return task_controller.get_task_status(db, task_id)


@router.get("/tasks/{task_id}/result")
def get_task_result(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    record = sync_job_repository.get_by_id(db, task_id)
    if not record or record.workspace_id != auth_context.workspace_id:
        raise AppError("TASK_NOT_FOUND", "没有找到这个任务", "task", 404)
    result = task_controller.get_task_result(db, task_id)
    if not result:
        raise AppError("TASK_RESULT_NOT_FOUND", "还没有查到这个任务结果", "task", 404)
    return {
        "task_id": task_id,
        "status": result.get("status"),
        "result": result.get("result"),
    }


@router.get("/task/{task_id}/result")
def get_task_result_compat(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return get_task_result(task_id=task_id, db=db, auth_context=auth_context)


@router.get("/tasks/{task_id}/explain")
def get_task_explain(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    record = sync_job_repository.get_by_id(db, task_id)
    if not record or record.workspace_id != auth_context.workspace_id:
        raise AppError("TASK_NOT_FOUND", "没有找到这个任务", "task", 404)
    result = task_controller.get_task_result(db, task_id)
    if not result:
        raise AppError("TASK_EXPLAIN_NOT_FOUND", "还没有查到这个任务解释", "task", 404)
    result_payload = result.get("result", {})
    return {
        "task_id": task_id,
        "status": result.get("status"),
        "explain_result": result_payload.get("explain_result", {}),
    }


@router.get("/task/{task_id}/explain")
def get_task_explain_compat(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return get_task_explain(task_id=task_id, db=db, auth_context=auth_context)


@router.get("/tasks/{task_id}/trace")
def get_task_trace(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    record = sync_job_repository.get_by_id(db, task_id)
    if not record or record.workspace_id != auth_context.workspace_id:
        raise AppError("TASK_NOT_FOUND", "没有找到这个任务", "task", 404)
    result = task_controller.get_task_result(db, task_id)
    if not result:
        raise AppError("TASK_TRACE_NOT_FOUND", "还没有查到这个任务链路", "task", 404)
    result_payload = result.get("result", {})
    return {
        "task_id": task_id,
        "status": result.get("status"),
        "governance_trace": result_payload.get("governance_trace", {}),
    }


@router.get("/task/{task_id}/trace")
def get_task_trace_compat(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    return get_task_trace(task_id=task_id, db=db, auth_context=auth_context)


@router.get("/task/{task_id}/full")
def get_task_full(
    task_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    record = sync_job_repository.get_by_id(db, task_id)
    if not record or record.workspace_id != auth_context.workspace_id:
        raise AppError("TASK_NOT_FOUND", "没有找到这个任务", "task", 404)
    status_payload = task_controller.get_task_status(db, task_id)
    result = task_controller.get_task_result(db, task_id)
    if not result:
        raise AppError("TASK_RESULT_NOT_FOUND", "还没有查到这个任务结果", "task", 404)
    result_payload = result.get("result", {})
    return {
        "task": status_payload,
        "result": result_payload,
        "explain": result_payload.get("explain_result", {}),
        "trace": result_payload.get("governance_trace", {}),
    }
