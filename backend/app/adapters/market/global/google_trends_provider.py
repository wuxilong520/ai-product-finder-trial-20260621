from __future__ import annotations

import json
from urllib.parse import quote

import httpx

from .global_market_base import GlobalMarketProvider, MarketSignal


class GoogleTrendsProvider(GlobalMarketProvider):
    source_name = "google"
    signal_type = "search_trend"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        geo = "" if str(country or "").upper() in {"GLOBAL", "WORLD"} else str(country or "US").upper()
        if geo == "UK":
            geo = "GB"
        try:
            request_payload = {
                "comparisonItem": [{"keyword": keyword, "geo": geo, "time": "today 3-m"}],
                "category": 0,
                "property": "",
            }
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                explore = await client.get(
                    f"https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req={quote(json.dumps(request_payload, separators=(',', ':')))}"
                )
                explore.raise_for_status()
                widgets = self._read_prefixed_json(explore.text).get("widgets", [])
                timeline_widget = next((item for item in widgets if item.get("id") == "TIMESERIES"), None)
                region_widget = next((item for item in widgets if item.get("id") == "GEO_MAP"), None)
                if not timeline_widget:
                    raise ValueError("missing timeline widget")
                timeline = await client.get(
                    f"https://trends.google.com/trends/api/widgetdata/multiline?hl=en-US&tz=0&req={quote(json.dumps(timeline_widget['request'], separators=(',', ':')))}&token={timeline_widget['token']}"
                )
                timeline.raise_for_status()
                timeline_data = self._read_prefixed_json(timeline.text).get("default", {}).get("timelineData", [])
                region_interest = []
                if region_widget:
                    region_resp = await client.get(
                        f"https://trends.google.com/trends/api/widgetdata/comparedgeo?hl=en-US&tz=0&req={quote(json.dumps(region_widget['request'], separators=(',', ':')))}&token={region_widget['token']}"
                    )
                    region_resp.raise_for_status()
                    region_interest = self._read_prefixed_json(region_resp.text).get("default", {}).get("geoMapData", [])
            if not timeline_data:
                raise ValueError("empty trend timeline")
            values = [float(item.get("value", [0])[0]) for item in timeline_data]
            current = values[-1]
            first = values[0]
            trend = "up" if current > first else "down" if current < first else "flat"
            return self.build_signal(
                keyword=keyword,
                country=country,
                value=current,
                trend=trend,
                confidence=0.82,
                data_status="real",
                metrics={
                    "google_trend_score": round(current, 2),
                    "trend_direction": trend,
                    "regional_interest": [
                        {
                            "location": str(item.get("geoName") or ""),
                            "value": float(item.get("value", [0])[0]) if item.get("value") else 0.0,
                        }
                        for item in region_interest[:10]
                    ],
                    "time_change": round(current - first, 2),
                },
            )
        except Exception as exc:
            return self.build_signal(
                keyword=keyword,
                country=country,
                value=0,
                trend="flat",
                confidence=0.2,
                data_status="fallback",
                metrics={},
                error_detail=f"Google Trends public failed: {exc}",
            )

    def _read_prefixed_json(self, text: str) -> dict:
        body = text.strip()
        if body.startswith(")]}',"):
            body = body[5:]
        return json.loads(body)
