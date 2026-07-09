from __future__ import annotations

import json
from urllib.parse import quote

import httpx

from app.adapters.market.market_base import MarketDataAdapter


class GoogleTrendsAdapter(MarketDataAdapter):
    source_name = "google_trends"

    async def fetch(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
    ) -> dict:
        del category
        geo = self._normalize_geo(region)
        request_payload = {
            "comparisonItem": [
                {
                    "keyword": keyword,
                    "geo": geo,
                    "time": "today 3-m",
                }
            ],
            "category": 0,
            "property": "",
        }
        try:
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=20,
                follow_redirects=True,
            ) as client:
                explore = await client.get(
                    f"https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req={quote(json.dumps(request_payload, separators=(',', ':')))}"
                )
                if explore.status_code != 200:
                    return self._fallback(keyword=keyword, region=region, reason=f"google_explore_{explore.status_code}")
                widgets = self._read_prefixed_json(explore.text).get("widgets", [])
                if not widgets:
                    return self._fallback(keyword=keyword, region=region, reason="google_widgets_empty")

                timeline_widget = next((item for item in widgets if item.get("id") == "TIMESERIES"), None)
                geo_widget = next((item for item in widgets if item.get("id") == "GEO_MAP"), None)
                related_widget = next((item for item in widgets if item.get("id") == "RELATED_QUERIES"), None)
                if not timeline_widget:
                    return self._fallback(keyword=keyword, region=region, reason="google_timeseries_missing")

                timeline = await client.get(
                    f"https://trends.google.com/trends/api/widgetdata/multiline?hl=en-US&tz=0&req={quote(json.dumps(timeline_widget['request'], separators=(',', ':')))}&token={timeline_widget['token']}"
                )
                timeline_json = self._read_prefixed_json(timeline.text)
                timeline_points = timeline_json.get("default", {}).get("timelineData", [])
                if not timeline_points:
                    return self._fallback(keyword=keyword, region=region, reason="google_timeline_empty")

                related_keywords: list[str] = []
                if related_widget:
                    related = await client.get(
                        f"https://trends.google.com/trends/api/widgetdata/relatedsearches?hl=en-US&tz=0&req={quote(json.dumps(related_widget['request'], separators=(',', ':')))}&token={related_widget['token']}"
                    )
                    related_json = self._read_prefixed_json(related.text)
                    ranked = related_json.get("default", {}).get("rankedList", [])
                    if ranked:
                        related_keywords = [
                            item.get("query", "")
                            for item in ranked[0].get("rankedKeyword", [])
                            if item.get("query")
                        ][:8]

                region_interest: dict[str, float] = {}
                if geo_widget:
                    geo_response = await client.get(
                        f"https://trends.google.com/trends/api/widgetdata/comparedgeo?hl=en-US&tz=0&req={quote(json.dumps(geo_widget['request'], separators=(',', ':')))}&token={geo_widget['token']}"
                    )
                    geo_json = self._read_prefixed_json(geo_response.text)
                    for item in geo_json.get("default", {}).get("geoMapData", [])[:10]:
                        if item.get("geoName") and item.get("value"):
                            region_interest[str(item["geoName"])] = float(item["value"][0])

                values = [float(point.get("value", [0])[0]) for point in timeline_points]
                trend_score = round(values[-1], 2)
                growth_rate = round(values[-1] - values[0], 2) if len(values) >= 2 else 0.0
                trend_points = [
                    {
                        "date": str(point.get("formattedTime") or point.get("time") or ""),
                        "score": float(point.get("value", [0])[0]),
                    }
                    for point in timeline_points[-12:]
                ]
                return self._envelope(
                    source=f"{self.source_name}_real",
                    data={
                        "trend_score": trend_score,
                        "growth_rate": growth_rate,
                        "related_keywords": related_keywords,
                        "region_interest": region_interest,
                        "trend_points": trend_points,
                    },
                    confidence=0.82,
                    is_mock=False,
                    source_status="real",
                )
        except Exception as exc:
            return self._fallback(keyword=keyword, region=region, reason=f"google_exception:{exc}")

    def _normalize_geo(self, region: str) -> str:
        normalized = str(region or "global").strip().upper()
        if normalized in {"GLOBAL", "WORLD", ""}:
            return ""
        if normalized == "US":
            return "US"
        if normalized == "UK":
            return "GB"
        if normalized == "EU":
            return ""
        return normalized

    def _read_prefixed_json(self, text: str) -> dict:
        body = text.strip()
        if body.startswith(")]}',"):
            body = body[5:]
        return json.loads(body)

    def _fallback(self, *, keyword: str, region: str, reason: str) -> dict:
        return self._envelope(
            source=f"{self.source_name}_mock",
            data={
                "trend_value": 61.0,
                "trend_direction": "up",
                "trend_score": 61.0,
                "growth_rate": 17.0,
                "confidence": 0.3,
                "source_status": "fallback_cache",
                "related_keywords": [keyword, f"{keyword} review", f"best {keyword}"],
                "region_interest": {str(region or 'global').upper(): 61.0},
                "trend_points": [
                    {"date": "week-4", "score": 44.0},
                    {"date": "week-3", "score": 49.0},
                    {"date": "week-2", "score": 54.0},
                    {"date": "week-1", "score": 58.0},
                    {"date": "now", "score": 61.0},
                ],
                "fallback_reason": reason,
            },
            confidence=0.3,
            is_mock=True,
            source_status="fallback_mock",
        )
