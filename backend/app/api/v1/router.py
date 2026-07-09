from fastapi import APIRouter

from app.api import result_query, task_submission
from app.api.v1.endpoints import admin, analyze, api_keys, auth, billing, business_truth, dashboard, decision, decision_explain, deploy, governance, listing, market, p5, products, publish, suppliers, supply


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(api_keys.router, tags=["API Key"])
api_router.include_router(admin.router, tags=["后台管理"])
api_router.include_router(billing.router, tags=["订阅套餐"])
api_router.include_router(analyze.router, tags=["一键分析"])
api_router.include_router(dashboard.router, tags=["新版看板"])
api_router.include_router(decision.router, tags=["决策中心"])
api_router.include_router(decision_explain.router, tags=["决策解释"])
api_router.include_router(listing.router, tags=["上架文案"])
api_router.include_router(publish.router, tags=["发布执行"])
api_router.include_router(deploy.router, tags=["生产部署"])
api_router.include_router(business_truth.router, tags=["商业真实性增强层"])
api_router.include_router(governance.router, tags=["数据治理"])
api_router.include_router(market.router, tags=["市场情报"])
api_router.include_router(suppliers.router, tags=["供应链匹配"])
api_router.include_router(supply.router, tags=["供应链智能"])
api_router.include_router(products.router, prefix="/products", tags=["商品"])
api_router.include_router(p5.router, tags=["P5 全局决策"])
api_router.include_router(task_submission.router, tags=["任务提交"])
api_router.include_router(result_query.router, tags=["任务结果"])
