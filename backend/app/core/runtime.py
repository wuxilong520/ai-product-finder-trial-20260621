from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import PROJECT_ROOT


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


def log_info(message: str) -> None:
    runtime_logger.info(message)


def log_error(message: str) -> None:
    runtime_logger.exception(message)


def error_response(error_code: str, message: str, stage: str, status_code: int = 500) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": message,
            "stage": stage,
        },
    )


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    log_error(f"APP_ERROR | stage={exc.stage} | code={exc.error_code} | message={exc.message}")
    return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    log_error(f"HTTP_ERROR | status={exc.status_code} | detail={exc.detail}")
    return error_response("HTTP_ERROR", str(exc.detail), "db", exc.status_code)


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    log_error(f"UNHANDLED_ERROR | message={exc}")
    return error_response("INTERNAL_SERVER_ERROR", "系统发生未处理错误", "db", 500)
