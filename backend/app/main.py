from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.runtime import (
    AppError,
    app_error_handler,
    ensure_log_dir,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.repositories.platform import platform_repository
from app.services.auth import auth_service
from app.models import analysis, category, crawl_run, platform, product, user  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_sqlite_path()
    ensure_log_dir()
    db = SessionLocal()
    try:
        _seed_platforms(db)
        auth_service.ensure_default_admin(db)
    finally:
        db.close()
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
    return {"ok": True}


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
