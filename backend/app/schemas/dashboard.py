from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DashboardStatCard(BaseModel):
    key: str
    label: str
    value: int | float | str
    delta_text: str | None = None
    trend: Literal["up", "down", "flat"] = "flat"


class DashboardLatestProduct(BaseModel):
    id: int
    title: str
    platform_name: str
    price: str
    category_name: str | None = None
    created_at: datetime


class DashboardCategorySnapshot(BaseModel):
    name: str
    product_count: int


class DashboardSummaryResponse(BaseModel):
    cards: list[DashboardStatCard]
    latest_products: list[DashboardLatestProduct]
    top_categories: list[DashboardCategorySnapshot]
    generated_at: datetime


class DashboardTrendPoint(BaseModel):
    date: str
    product_count: int


class DashboardTrendSeries(BaseModel):
    period: str
    points: list[DashboardTrendPoint]
    peak_value: int


class DashboardTrendsResponse(BaseModel):
    series: DashboardTrendSeries
    generated_at: datetime


class DashboardTaskState(BaseModel):
    key: str
    label: str
    status: Literal["pending", "running", "success", "error", "blocked", "unknown"]
    message: str
    error_reason: str | None = None
    updated_at: str


class DashboardRecentRun(BaseModel):
    id: int
    request_url: str
    status: str
    platform_name: str
    crawled_at: datetime


class DashboardTasksResponse(BaseModel):
    states: list[DashboardTaskState]
    recent_runs: list[DashboardRecentRun]
    generated_at: datetime


class DashboardSourceState(BaseModel):
    platform_code: str
    platform_name: str
    health: Literal["ok", "warning", "error"]
    last_activity_text: str
    product_count: int


class DashboardStorageState(BaseModel):
    used_percent: int
    total_products: int
    total_runs: int


class DashboardSourcesResponse(BaseModel):
    sources: list[DashboardSourceState]
    storage: DashboardStorageState
    generated_at: datetime

