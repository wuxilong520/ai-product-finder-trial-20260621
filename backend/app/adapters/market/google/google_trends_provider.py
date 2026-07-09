from __future__ import annotations

import json
from urllib.parse import quote

import httpx

from app.adapters.market.base import MarketProvider


class GoogleTrendsProvider(MarketProvider):
    provider_name = "google"

    async def fetch_market_signal(
        self,
        keyword: str,
        region: str,
        category: str | None = None,
        time_range: str = "90d",
    ) -> dict:
        del category
        request_payload = {
            "comparisonItem": [
                {
                    "keyword": keyword,
                    "geo": self._normalize_geo(region),
                    "time": self._normalize_time_range(time_range),
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
                    return self._signal_envelope(
                        source=self.provider_name,
                        source_status="unavailable",
                        confidence=0.0,
                        signal={
                            "status": "unavailable",
                            "interest_score": 0.0,
                            "trend_direction": "flat",
                            "growth_rate": 0.0,
                            "related_queries": [],
                            "rising_queries": [],
                            "seasonality": "unknown",
                            "region_interest": {},
                            "time_range": time_range,
                            "reason": f"google_explore_{explore.status_code}",
                        },
                    )
                widgets = self._read_prefixed_json(explore.text).get("widgets", [])
                timeline_widget = next((item for item in widgets if item.get("id") == "TIMESERIES"), None)
                geo_widget = next((item for item in widgets if item.get("id") == "GEO_MAP"), None)
                related_widget = next((item for item in widgets if item.get("id") == "RELATED_QUERIES"), None)
                if not timeline_widget:
                    return self._unavailable(time_range=time_range, reason="google_timeseries_missing")

                timeline = await client.get(
                    f"https://trends.google.com/trends/api/widgetdata/multiline?hl=en-US&tz=0&req={quote(json.dumps(timeline_widget['request'], separators=(',', ':')))}&token={timeline_widget['token']}"
                )
                timeline_json = self._read_prefixed_json(timeline.text)
                timeline_points = timeline_json.get("default", {}).get("timelineData", [])
                if not timeline_points:
                    return self._unavailable(time_range=time_range, reason="google_timeline_empty")

                related_queries: list[str] = []
                rising_queries: list[str] = []
                if related_widget:
                    related = await client.get(
                        f"https://trends.google.com/trends/api/widgetdata/relatedsearches?hl=en-US&tz=0&req={quote(json.dumps(related_widget['request'], separators=(',', ':')))}&token={related_widget['token']}"
                    )
                    related_json = self._read_prefixed_json(related.text)
                    ranked = related_json.get("default", {}).get("rankedList", [])
                    if ranked:
                        top_ranked = ranked[0].get("rankedKeyword", [])
                        related_queries = [str(item.get("query") or "") for item in top_ranked if item.get("query")][:10]
                    if len(ranked) > 1:
                        top_rising = ranked[1].get("rankedKeyword", [])
                        rising_queries = [str(item.get("query") or "") for item in top_rising if item.get("query")][:10]

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
                interest_score = round(values[-1], 2)
                growth_rate = round(values[-1] - values[0], 2) if len(values) >= 2 else 0.0
                trend_direction = "up" if growth_rate > 0 else "down" if growth_rate < 0 else "flat"
                seasonality = self._seasonality(values)

                return self._signal_envelope(
                    source=self.provider_name,
                    source_status="real",
                    confidence=0.86,
                    signal={
                        "status": "real",
                        "interest_score": interest_score,
                        "trend_direction": trend_direction,
                        "growth_rate": growth_rate,
                        "related_queries": related_queries,
                        "rising_queries": rising_queries,
                        "seasonality": seasonality,
                        "region_interest": region_interest,
                        "time_range": time_range,
                        "trend_points": [
                            {
                                "date": str(point.get("formattedTime") or point.get("time") or ""),
                                "score": float(point.get("value", [0])[0]),
                            }
                            for point in timeline_points[-12:]
                        ],
                    },
                )
        except Exception as exc:
            return self._unavailable(time_range=time_range, reason=f"google_exception:{exc}")

    def _normalize_geo(self, region: str) -> str:
        normalized = str(region or "global").strip().upper()
        if normalized in {"GLOBAL", "WORLD", ""}:
            return ""
        if normalized == "UK":
            return "GB"
        if normalized == "EU":
            return ""
        return normalized

    def _normalize_time_range(self, time_range: str) -> str:
        normalized = str(time_range or "90d").strip().lower()
        mapping = {
            "7d": "now 7-d",
            "30d": "today 1-m",
            "90d": "today 3-m",
        }
        return mapping.get(normalized, "today 3-m")

    def _seasonality(self, values: list[float]) -> str:
        if len(values) < 4:
            return "unknown"
        spread = max(values) - min(values)
        if spread >= 35:
            return "seasonal"
        if spread <= 12:
            return "stable"
        return "mixed"

    def _read_prefixed_json(self, text: str) -> dict:
        body = text.strip()
        if body.startswith(")]}',"):
            body = body[5:]
        return json.loads(body)

    def _unavailable(self, *, time_range: str, reason: str) -> dict:
        return self._signal_envelope(
            source=self.provider_name,
            source_status="unavailable",
            confidence=0.0,
            signal={
                "status": "unavailable",
                "interest_score": 0.0,
                "trend_direction": "flat",
                "growth_rate": 0.0,
                "related_queries": [],
                "rising_queries": [],
                "seasonality": "unknown",
                "region_interest": {},
                "time_range": time_range,
                "reason": reason,
            },
        )
