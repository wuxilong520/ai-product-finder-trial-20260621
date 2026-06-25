from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.analysis import AIAnalysisResult
from app.models.category import Category
from app.models.crawl_run import CrawlRun
from app.models.platform import Platform
from app.models.product import Product
from app.repositories.platform import platform_repository
from app.schemas.dashboard import (
    DashboardCategorySnapshot,
    DashboardLatestProduct,
    DashboardRecentRun,
    DashboardSourceState,
    DashboardSourcesResponse,
    DashboardStatCard,
    DashboardStorageState,
    DashboardSummaryResponse,
    DashboardTaskState,
    DashboardTasksResponse,
    DashboardTrendPoint,
    DashboardTrendSeries,
    DashboardTrendsResponse,
)
from app.services.dashboard_cache import dashboard_cache
from app.services.task_status import task_status_service


def _now() -> datetime:
    return datetime.now(UTC)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _to_price(value: Decimal | float | int | None) -> str:
    if value is None:
        return "—"
    return f"${float(value):,.2f}"


class DashboardService:
    def summary(self, db: Session) -> DashboardSummaryResponse:
        return dashboard_cache.get_or_set("dashboard_summary", 5, lambda: self._build_summary(db))

    def trends(self, db: Session) -> DashboardTrendsResponse:
        return dashboard_cache.get_or_set("dashboard_trends", 30, lambda: self._build_trends(db))

    def tasks(self, db: Session) -> DashboardTasksResponse:
        return self._build_tasks(db)

    def sources(self, db: Session) -> DashboardSourcesResponse:
        return dashboard_cache.get_or_set("dashboard_sources", 10, lambda: self._build_sources(db))

    def _build_summary(self, db: Session) -> DashboardSummaryResponse:
        now = _now()
        seven_days_ago = now - timedelta(days=7)
        previous_week = seven_days_ago - timedelta(days=7)

        total_products = db.scalar(select(func.count(Product.id))) or 0
        active_products = db.scalar(select(func.count(Product.id)).where(Product.is_active.is_(True))) or 0
        total_runs = db.scalar(select(func.count(CrawlRun.id))) or 0
        total_analyses = db.scalar(select(func.count(AIAnalysisResult.id))) or 0
        recent_products = db.scalar(select(func.count(Product.id)).where(Product.created_at >= seven_days_ago)) or 0
        previous_recent_products = db.scalar(
            select(func.count(Product.id)).where(Product.created_at >= previous_week, Product.created_at < seven_days_ago)
        ) or 0

        cards = [
            DashboardStatCard(
                key="products",
                label="商品总数",
                value=total_products,
                delta_text=f"近7天 +{recent_products}",
                trend="up" if recent_products > 0 else "flat",
            ),
            DashboardStatCard(
                key="active_products",
                label="启用商品",
                value=active_products,
                delta_text=f"占比 {round((active_products / total_products) * 100)}%" if total_products else "占比 0%",
                trend="up" if active_products else "flat",
            ),
            DashboardStatCard(
                key="crawl_runs",
                label="采集任务",
                value=total_runs,
                delta_text=f"本周新增 {recent_products}",
                trend="up" if total_runs else "flat",
            ),
            DashboardStatCard(
                key="analyses",
                label="分析结果",
                value=total_analyses,
                delta_text=f"较上周 {recent_products - previous_recent_products:+d}",
                trend="up" if recent_products >= previous_recent_products else "down",
            ),
        ]

        latest_products_query = (
            select(Product, Platform.name, Category.name)
            .join(Platform, Platform.id == Product.platform_id)
            .outerjoin(Category, Category.id == Product.category_id)
            .order_by(desc(Product.created_at))
            .limit(5)
        )
        latest_products = [
            DashboardLatestProduct(
                id=product.id,
                title=product.title,
                platform_name=platform_name,
                price=_to_price(product.current_price),
                category_name=category_name,
                created_at=product.created_at,
            )
            for product, platform_name, category_name in db.execute(latest_products_query).all()
        ]

        category_rows = (
            db.execute(
                select(Category.name, func.count(Product.id))
                .join(Product, Product.category_id == Category.id)
                .group_by(Category.name)
                .order_by(desc(func.count(Product.id)))
                .limit(6)
            ).all()
        )
        top_categories = [
            DashboardCategorySnapshot(name=name, product_count=count)
            for name, count in category_rows
        ]

        return DashboardSummaryResponse(
            cards=cards,
            latest_products=latest_products,
            top_categories=top_categories,
            generated_at=now,
        )

    def _build_trends(self, db: Session) -> DashboardTrendsResponse:
        now = _now()
        start_date = (now - timedelta(days=6)).date()
        rows = db.execute(
            select(func.date(Product.created_at), func.count(Product.id))
            .where(Product.created_at >= start_date)
            .group_by(func.date(Product.created_at))
            .order_by(func.date(Product.created_at))
        ).all()

        count_map = {str(day): count for day, count in rows}
        points: list[DashboardTrendPoint] = []
        peak_value = 0
        for offset in range(7):
            current_day = start_date + timedelta(days=offset)
            current_day_str = current_day.isoformat()
            value = int(count_map.get(current_day_str, 0))
            peak_value = max(peak_value, value)
            points.append(DashboardTrendPoint(date=current_day_str, product_count=value))

        return DashboardTrendsResponse(
            series=DashboardTrendSeries(period="7d", points=points, peak_value=peak_value),
            generated_at=now,
        )

    def _build_tasks(self, db: Session) -> DashboardTasksResponse:
        now = _now()
        crawl_state = task_status_service.get("crawl")
        analyze_state = task_status_service.get("analyze")
        states = [
            DashboardTaskState(
                key="crawl",
                label="采集任务",
                status=crawl_state["status"],
                message=crawl_state["message"],
                error_reason=crawl_state.get("error_reason"),
                updated_at=crawl_state["updated_at"],
            ),
            DashboardTaskState(
                key="analyze",
                label="分析任务",
                status=analyze_state["status"],
                message=analyze_state["message"],
                error_reason=analyze_state.get("error_reason"),
                updated_at=analyze_state["updated_at"],
            ),
        ]

        recent_runs_query = (
            select(CrawlRun, Platform.name)
            .join(Platform, Platform.id == CrawlRun.platform_id)
            .order_by(desc(CrawlRun.crawled_at))
            .limit(6)
        )
        recent_runs = [
            DashboardRecentRun(
                id=run.id,
                request_url=run.request_url,
                status=run.status,
                platform_name=platform_name,
                crawled_at=run.crawled_at,
            )
            for run, platform_name in db.execute(recent_runs_query).all()
        ]
        return DashboardTasksResponse(states=states, recent_runs=recent_runs, generated_at=now)

    def _build_sources(self, db: Session) -> DashboardSourcesResponse:
        now = _now()
        platforms = platform_repository.list_all(db)
        product_counts = dict(
            db.execute(
                select(Product.platform_id, func.count(Product.id))
                .group_by(Product.platform_id)
            ).all()
        )
        latest_runs = defaultdict(lambda: None)
        for run, platform_name in db.execute(
            select(CrawlRun, Platform.name)
            .join(Platform, Platform.id == CrawlRun.platform_id)
            .order_by(desc(CrawlRun.crawled_at))
        ).all():
            if latest_runs[run.platform_id] is None:
                latest_runs[run.platform_id] = (run, platform_name)

        source_states: list[DashboardSourceState] = []
        for platform in platforms:
            latest = latest_runs.get(platform.id)
            health = "ok"
            last_activity_text = "暂无采集"
            if latest:
                run, _ = latest
                if run.status in {"failed", "error"}:
                    health = "error"
                elif run.status in {"blocked", "paused"}:
                    health = "warning"
                crawled_at = _ensure_utc(run.crawled_at)
                delta_minutes = max(int((now - crawled_at).total_seconds() // 60), 0)
                last_activity_text = f"{delta_minutes} 分钟前"
            source_states.append(
                DashboardSourceState(
                    platform_code=platform.code,
                    platform_name=platform.name,
                    health=health,
                    last_activity_text=last_activity_text,
                    product_count=int(product_counts.get(platform.id, 0)),
                )
            )

        total_products = db.scalar(select(func.count(Product.id))) or 0
        total_runs = db.scalar(select(func.count(CrawlRun.id))) or 0
        used_percent = min(100, int((total_products / 1000) * 100)) if total_products else 0

        return DashboardSourcesResponse(
            sources=source_states,
            storage=DashboardStorageState(
                used_percent=used_percent,
                total_products=total_products,
                total_runs=total_runs,
            ),
            generated_at=now,
        )


dashboard_service = DashboardService()
