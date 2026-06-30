from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.runtime import (
    AppError,
    app_error_handler,
    ensure_log_dir,
    http_exception_handler,
    log_info,
    unhandled_exception_handler,
)
from app.core.startup_checks import collect_runtime_summary, validate_startup_env
from app.repositories.platform import platform_repository
from app.billing.service import billing_service
from app.billing import order as billing_order  # noqa: F401
from app.services.auth import auth_service
from app.services.task_status import task_status_service
from app.workspace.service import workspace_service
from app.models import analysis, auth_identity, business_truth, category, crawl_run, decision_recommendation, market_intelligence, platform, product, product_intelligence, supplier_match, user  # noqa: F401
from app.workspace import model as workspace_model  # noqa: F401
from app.api_key import model as api_key_model  # noqa: F401
from app.quota import model as quota_model  # noqa: F401
from app.billing import subscription as billing_subscription  # noqa: F401
from app.ws_manager import task_ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_sqlite_path()
    ensure_log_dir()
    runtime_env = validate_startup_env()
    log_info(
        "STARTUP_ENV | "
        f"env={runtime_env['app_env']} | "
        f"backend={runtime_env['backend_url']} | "
        f"frontend={runtime_env['frontend_url']} | "
        f"origin={runtime_env['frontend_origin']} | "
        f"ws={runtime_env['ws_url']}"
    )
    db = SessionLocal()
    try:
        _seed_platforms(db)
        admin = auth_service.ensure_default_admin(db)
        workspace = workspace_service.get_or_create_default(db, admin)
        billing_service.apply_plan_quota(db, workspace_id=workspace.id)
    finally:
        db.close()
    runtime_summary = collect_runtime_summary()
    log_info(
        "STARTUP_HEALTH | "
        f"status={runtime_summary['status']} | "
        f"db={runtime_summary['services']['database']} | "
        f"ai={runtime_summary['services']['ai']} | "
        f"crawler={runtime_summary['services']['crawler']}"
    )
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return collect_runtime_summary()


@app.get("/task-status/{task_name}")
def get_task_status(task_name: str):
    return task_status_service.get(task_name)


@app.websocket("/ws/{task_name}")
async def task_status_ws(websocket: WebSocket, task_name: str):
    await task_ws_manager.connect(task_name, websocket)
    try:
        await websocket.send_json(task_status_service.get(task_name))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        task_ws_manager.disconnect(task_name, websocket)


def _seed_platforms(db):
    platform_rows = [
        {"code": "amazon", "name": "Amazon", "platform_type": "marketplace", "homepage_url": "https://www.amazon.com"},
        {"code": "aliexpress", "name": "AliExpress", "platform_type": "marketplace", "homepage_url": "https://www.aliexpress.com"},
        {"code": "shopify", "name": "Shopify", "platform_type": "shop", "homepage_url": "https://www.shopify.com"},
        {"code": "1688", "name": "1688", "platform_type": "supplier", "homepage_url": "https://www.1688.com"},
        {"code": "pdd", "name": "拼多多", "platform_type": "supplier", "homepage_url": "https://www.pinduoduo.com"},
    ]
    for row in platform_rows:
        if not platform_repository.get_by_code(db, row["code"]):
            platform_repository.create(db, **row)


def _ensure_sqlite_path():
    if not settings.database_url.startswith("sqlite:///"):
        return
    db_file = Path(settings.database_url.replace("sqlite:///", "", 1))
    db_file.parent.mkdir(parents=True, exist_ok=True)
