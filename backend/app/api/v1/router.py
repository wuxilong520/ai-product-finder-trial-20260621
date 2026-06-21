from fastapi import APIRouter

from app.api.v1.endpoints import analyze, auth, products


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(analyze.router, tags=["一键分析"])
api_router.include_router(products.router, prefix="/products", tags=["商品"])
