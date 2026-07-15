from contextlib import asynccontextmanager
from pathlib import Path
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.request_context import bind_request_context, bind_user_context, reset_context
from app.core.runtime import (
    AppError,
    app_error_handler,
    error_response,
    ensure_log_dir,
    http_exception_handler,
    log_info,
    log_warning,
    unhandled_exception_handler,
)
from app.core.startup_checks import collect_runtime_summary, validate_startup_env
from app.core.production_detector import production_detector
from app.repositories.platform import platform_repository
from app.billing.service import billing_service
from app.billing import order as billing_order  # noqa: F401
from app.services.auth import auth_service
from app.services.task_status import task_status_service
from app.workspace.service import workspace_service
from app.models import analysis, auth_identity, business_truth, category, crawl_run, decision_recommendation, market_analysis_history, market_intelligence, market_signal_history, platform, procurement, product, product_intelligence, request_metric, supplier, supplier_match, user  # noqa: F401
from app.workspace import model as workspace_model  # noqa: F401
from app.api_key import model as api_key_model  # noqa: F401
from app.quota import model as quota_model  # noqa: F401
from app.billing import subscription as billing_subscription  # noqa: F401
from app.ws_manager import task_ws_manager
from app.models.request_metric import RequestMetricRecord
from app.models.user_activity_log import UserActivityLog


RATE_LIMIT_STORE: dict[tuple[str, str], list[float]] = {}


def _client_ip(request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded_for:
        return forwarded_for
    return getattr(getattr(request, "client", None), "host", "unknown")


def _resolve_rate_limit(request) -> tuple[str, int]:
    if request.url.path.startswith("/api/v1/auth/"):
        return "auth", settings.auth_rate_limit_per_minute
    if request.url.path.startswith("/api/"):
        return "api", settings.api_rate_limit_per_minute
    return "page", settings.api_rate_limit_per_minute


def _is_rate_limited(request, now_ts: float) -> tuple[bool, int]:
    scope, limit = _resolve_rate_limit(request)
    key = (scope, _client_ip(request))
    bucket = RATE_LIMIT_STORE.setdefault(key, [])
    cutoff = now_ts - 60
    while bucket and bucket[0] < cutoff:
        bucket.pop(0)
    if len(bucket) >= limit:
        return True, limit
    bucket.append(now_ts)
    return False, limit


def _activity_action(request, response) -> str | None:
    explicit = getattr(request.state, "activity_action", None)
    if explicit:
        return explicit
    mapping = {
        ("POST", "/api/v1/auth/login"): "user_login",
        ("POST", "/api/v1/auth/login/code"): "user_login_code",
        ("POST", "/api/v1/auth/logout"): "user_logout",
        ("POST", "/api/v1/products/crawl"): "product_create",
        ("POST", "/api/v1/products/analyze"): "product_analyze",
        ("POST", "/api/v1/analyze/full"): "product_analyze_full",
        ("POST", "/api/v1/market/intelligence"): "market_analyze",
        ("GET", "/api/v1/procurement/pool"): "procurement_pool_view",
        ("POST", "/api/v1/procurement/favorite"): "procurement_favorite",
        ("POST", "/api/v1/market/connect/shopify"): "shopify_connect_start",
    }
    action = mapping.get((request.method.upper(), request.url.path))
    if action:
        return action
    if request.method.upper() == "POST" and request.url.path.startswith("/api/v1/procurement/analyze/"):
        return "procurement_analyze"
    return None


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
    production_status = production_detector.detect()
    log_info(
        "STARTUP_HEALTH | "
        f"status={runtime_summary['status']} | "
        f"db={runtime_summary['services']['database']} | "
        f"ai={runtime_summary['services']['ai']} | "
        f"crawler={runtime_summary['services']['crawler']} | "
        f"production_env={production_status['environment']} | "
        f"payment={production_status['payment_configured']} | "
        f"email={production_status['email_configured']} | "
        f"ssl={production_status['ssl_enabled']}"
    )
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.middleware("http")
async def record_request_metric(request, call_next):
    request_id = request.headers.get("X-Request-ID", "").strip() or str(uuid4())
    request.state.request_id = request_id
    request_tokens = bind_request_context(request_id=request_id, endpoint=request.url.path, method=request.method.upper())
    user_tokens = bind_user_context(
        user_id=getattr(request.state, "user_id", None),
        workspace_id=getattr(request.state, "workspace_id", None),
    )
    started_at = time.perf_counter()
    response = None
    try:
        limited, limit = _is_rate_limited(request, time.time())
        if limited:
            response = error_response(
                "RATE_LIMITED",
                f"请求太频繁了，请稍后再试。当前每分钟上限 {limit} 次。",
                "gateway",
                429,
                request=request,
            )
        else:
            response = await call_next(request)
        return response
    finally:
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        if response is not None:
            user_id = getattr(request.state, "user_id", None)
            workspace_id = getattr(request.state, "workspace_id", None)
            status_code = getattr(response, "status_code", 500)
            response.headers["X-Request-ID"] = request_id
            log_info(
                "REQUEST",
                request_id=request_id,
                user_id=user_id,
                workspace_id=workspace_id,
                endpoint=request.url.path,
                method=request.method.upper(),
                status_code=status_code,
                response_time_ms=duration_ms,
                client_ip=_client_ip(request),
            )
            if duration_ms >= settings.slow_api_threshold_ms:
                log_warning(
                    "SLOW_REQUEST",
                    request_id=request_id,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    endpoint=request.url.path,
                    method=request.method.upper(),
                    status_code=status_code,
                    response_time_ms=duration_ms,
                )
            if request.url.path.startswith("/api/") or request.url.path == "/health":
                db = SessionLocal()
                try:
                    db.add(
                        RequestMetricRecord(
                            request_id=request_id,
                            path=request.url.path,
                            method=request.method.upper(),
                            user_id=user_id,
                            workspace_id=workspace_id,
                            status_code=status_code,
                            duration_ms=duration_ms,
                        )
                    )
                    action = _activity_action(request, response)
                    if action:
                        db.add(
                            UserActivityLog(
                                request_id=request_id,
                                user_id=user_id,
                                workspace_id=workspace_id,
                                action=action,
                                method=request.method.upper(),
                                path=request.url.path,
                                status_code=status_code,
                            )
                        )
                    db.commit()
                except Exception as exc:
                    db.rollback()
                    log_warning("METRIC_WRITE_FAILED", request_id=request_id, message=str(exc))
                finally:
                    db.close()
        reset_context(user_tokens)
        reset_context(request_tokens)


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
