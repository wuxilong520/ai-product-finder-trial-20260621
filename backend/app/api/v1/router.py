from fastapi import APIRouter

from app.api.v1.endpoints import analyze, auth, business_truth, dashboard, decision, market, p5, products, suppliers


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(analyze.router, tags=["一键分析"])
api_router.include_router(dashboard.router, tags=["新版看板"])
api_router.include_router(decision.router, tags=["决策中心"])
api_router.include_router(business_truth.router, tags=["商业真实性增强层"])
api_router.include_router(market.router, tags=["市场情报"])
api_router.include_router(suppliers.router, tags=["供应链匹配"])
api_router.include_router(products.router, prefix="/products", tags=["商品"])
api_router.include_router(p5.router, tags=["P5 全局决策"])
