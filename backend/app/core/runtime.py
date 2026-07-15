from __future__ import annotations

from datetime import UTC, datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import traceback

from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import PROJECT_ROOT
from app.core.request_context import get_endpoint, get_method, get_request_id, get_user_id, get_workspace_id


LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "truth_runtime.log"


class AppError(Exception):
    def __init__(self, error_code: str, message: str, stage: str, status_code: int = 500):
        self.error_code = error_code
        self.message = message
        self.stage = stage
        self.status_code = status_code
        super().__init__(message)


def ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.touch(exist_ok=True)


def get_runtime_logger() -> logging.Logger:
    ensure_log_dir()
    logger = logging.getLogger("truth_runtime")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


runtime_logger = get_runtime_logger()


SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "authorization", "cookie", "secret"}


def _sanitize(value):
    if isinstance(value, dict):
        return {key: ("***" if key.lower() in SENSITIVE_KEYS else _sanitize(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize(item) for item in value)
    return value


def _format_fields(fields: dict) -> str:
    clean_fields = _sanitize(fields)
    ordered = {
        "request_id": clean_fields.pop("request_id", get_request_id()),
        "user_id": clean_fields.pop("user_id", get_user_id()),
        "workspace_id": clean_fields.pop("workspace_id", get_workspace_id()),
        "endpoint": clean_fields.pop("endpoint", get_endpoint()),
        "method": clean_fields.pop("method", get_method()),
        **clean_fields,
    }
    return " | ".join(f"{key}={value}" for key, value in ordered.items() if value not in {None, ""})


def log_event(level: int, event: str, **fields) -> None:
    suffix = _format_fields(fields)
    runtime_logger.log(level, f"{event}" if not suffix else f"{event} | {suffix}")


def log_info(message: str, **fields) -> None:
    if fields:
        log_event(logging.INFO, message, **fields)
        return
    runtime_logger.info(message)


def log_warning(message: str, **fields) -> None:
    if fields:
        log_event(logging.WARNING, message, **fields)
        return
    runtime_logger.warning(message)


def log_error(message: str, **fields) -> None:
    if fields:
        log_event(logging.ERROR, message, **fields)
        return
    runtime_logger.error(message)


def error_response(
    error_code: str,
    message: str,
    stage: str,
    status_code: int = 500,
    request: Request | None = None,
) -> JSONResponse:
    request_id = getattr(getattr(request, "state", None), "request_id", None) or get_request_id()
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": message,
            "stage": stage,
            "request_id": request_id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    log_event(level, "APP_ERROR", stage=exc.stage, code=exc.error_code, message=exc.message, status_code=exc.status_code)
    return error_response(exc.error_code, exc.message, exc.stage, exc.status_code, request=request)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    log_event(level, "HTTP_ERROR", status_code=exc.status_code, detail=str(exc.detail))
    return error_response("HTTP_ERROR", str(exc.detail), "http", exc.status_code, request=request)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log_event(
        logging.ERROR,
        "UNHANDLED_ERROR",
        exception_type=exc.__class__.__name__,
        message=str(exc),
        traceback=traceback.format_exc(limit=8),
    )
    return error_response("INTERNAL_SERVER_ERROR", "系统发生未处理错误", "server", 500, request=request)
