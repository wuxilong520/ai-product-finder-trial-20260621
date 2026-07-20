from __future__ import annotations

import json
from statistics import mean
from urllib.parse import quote

import httpx

from app.adapters.market.v3 import MarketDataProvider, MarketSignal
from app.core.config import settings


class GoogleMarketProvider(MarketDataProvider):
    provider_name = "google"

    async def fetch_signal(
        self,
        *,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> MarketSignal:
        del category
        missing = self._missing_credentials()
        if missing:
            return self._config_required(
                keyword=keyword,
                region=region,
                missing_credentials=missing,
                error_detail="Google Ads Keyword Planner 需要完整 OAuth 和 developer token",
            )

        try:
            trends_metrics = await self._fetch_google_trends(keyword=keyword, region=region)
            planner_metrics = await self._fetch_keyword_planner(keyword=keyword, region=region)
            search_volume = float(planner_metrics.get("search_volume") or 0)
            keyword_growth = float(trends_metrics.get("keyword_growth") or 0)
            competition = float(planner_metrics.get("competition") or 0)
            value = max(
                0.0,
                min(
                    100.0,
                    (min(search_volume / 1000.0, 60.0) * 0.55)
                    + (max(0.0, min(100.0, 50 + keyword_growth)) * 0.30)
                    - (competition * 0.15),
                ),
            )
            confidence = 0.9 if search_volume > 0 else 0.55
            return self._signal(
                keyword=keyword,
                region=region,
                value=value,
                confidence=confidence,
                is_real=True,
                api_status="REAL",
                metrics={
                    **planner_metrics,
                    **trends_metrics,
                },
            )
        except Exception as exc:
            return self._unavailable(
                keyword=keyword,
                region=region,
                error_detail=f"Google provider 失败: {exc}",
            )

    def _missing_credentials(self) -> list[str]:
        required = {
            "GOOGLE_ADS_DEVELOPER_TOKEN": settings.google_ads_developer_token,
            "GOOGLE_ADS_CLIENT_ID": settings.google_ads_client_id,
            "GOOGLE_ADS_CLIENT_SECRET": settings.google_ads_client_secret,
            "GOOGLE_ADS_REFRESH_TOKEN": settings.google_ads_refresh_token,
            "GOOGLE_ADS_CUSTOMER_ID": settings.google_ads_customer_id,
        }
        return [key for key, value in required.items() if not str(value or "").strip()]

    async def _fetch_google_trends(self, *, keyword: str, region: str) -> dict:
        geo = self._normalize_geo(region)
        request_payload = {
            "comparisonItem": [{"keyword": keyword, "geo": geo, "time": "today 3-m"}],
            "category": 0,
            "property": "",
        }
        async with httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=20,
            follow_redirects=True,
        ) as client:
            explore = await client.get(
                f"https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req={quote(json.dumps(request_payload, separators=(',', ':')))}"
            )
            explore.raise_for_status()
            widgets = self._read_prefixed_json(explore.text).get("widgets", [])
            timeline_widget = next((item for item in widgets if item.get("id") == "TIMESERIES"), None)
            if not timeline_widget:
                raise ValueError("Google Trends 缺少 TIMESERIES widget")
            timeline = await client.get(
                f"https://trends.google.com/trends/api/widgetdata/multiline?hl=en-US&tz=0&req={quote(json.dumps(timeline_widget['request'], separators=(',', ':')))}&token={timeline_widget['token']}"
            )
            timeline.raise_for_status()
            timeline_points = self._read_prefixed_json(timeline.text).get("default", {}).get("timelineData", [])
            if not timeline_points:
                raise ValueError("Google Trends 没返回趋势点")
            values = [float(point.get("value", [0])[0]) for point in timeline_points]
            keyword_growth = round(values[-1] - values[0], 2) if len(values) >= 2 else 0.0
            seasonality = round(max(values) - min(values), 2) if values else 0.0
            return {
                "trend_curve": [
                    {
                        "date": str(point.get("formattedTime") or point.get("time") or ""),
                        "score": float(point.get("value", [0])[0]),
                    }
                    for point in timeline_points[-12:]
                ],
                "seasonality": seasonality,
                "keyword_growth": keyword_growth,
                "trend_score": round(values[-1], 2),
            }

    async def _fetch_keyword_planner(self, *, keyword: str, region: str) -> dict:
        token = await self._google_access_token()
        customer_id = str(settings.google_ads_customer_id or "").replace("-", "")
        endpoint = f"https://googleads.googleapis.com/v18/customers/{customer_id}:generateKeywordIdeas"
        payload = {
            "keywordSeed": {"keywords": [keyword]},
            "geoTargetConstants": self._geo_targets(region),
            "language": "languageConstants/1000",
            "includeAdultKeywords": False,
            "keywordPlanNetwork": "GOOGLE_SEARCH_AND_PARTNERS",
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "developer-token": str(settings.google_ads_developer_token or "").strip(),
            "Content-Type": "application/json",
        }
        login_customer_id = str(settings.google_ads_login_customer_id or "").strip().replace("-", "")
        if login_customer_id:
            headers["login-customer-id"] = login_customer_id
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            rows = list((response.json() or {}).get("results") or [])
        monthly = []
        competitions = []
        for row in rows[:20]:
            metrics = row.get("keywordIdeaMetrics") or {}
            monthly_searches = metrics.get("avgMonthlySearches")
            if monthly_searches is not None:
                monthly.append(float(monthly_searches))
            competition_text = str(metrics.get("competition") or "").upper()
            competition_index = metrics.get("competitionIndex")
            if competition_index is not None:
                competitions.append(min(100.0, float(competition_index)))
            elif competition_text:
                competitions.append({"LOW": 25.0, "MEDIUM": 55.0, "HIGH": 85.0}.get(competition_text, 50.0))
        search_volume = round(mean(monthly), 2) if monthly else 0.0
        competition = round(mean(competitions), 2) if competitions else 0.0
        return {
            "search_volume": search_volume,
            "competition": competition,
        }

    async def _google_access_token(self) -> str:
        payload = {
            "client_id": str(settings.google_ads_client_id or "").strip(),
            "client_secret": str(settings.google_ads_client_secret or "").strip(),
            "refresh_token": str(settings.google_ads_refresh_token or "").strip(),
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post("https://oauth2.googleapis.com/token", data=payload)
            response.raise_for_status()
            token = str((response.json() or {}).get("access_token") or "").strip()
        if not token:
            raise ValueError("Google OAuth 没拿到 access_token")
        return token

    def _normalize_geo(self, region: str) -> str:
        normalized = str(region or "US").strip().upper()
        if normalized == "UK":
            return "GB"
        if normalized in {"GLOBAL", "WORLD"}:
            return ""
        return normalized

    def _geo_targets(self, region: str) -> list[str]:
        mapping = {
            "US": "geoTargetConstants/2840",
            "UK": "geoTargetConstants/2826",
            "GB": "geoTargetConstants/2826",
            "EU": "geoTargetConstants/1000002",
            "GLOBAL": "geoTargetConstants/1000000",
        }
        normalized = str(region or "US").strip().upper()
        return [mapping.get(normalized, "geoTargetConstants/2840")]

    def _read_prefixed_json(self, text: str) -> dict:
        body = text.strip()
        if body.startswith(")]}',"):
            body = body[5:]
        return json.loads(body)
