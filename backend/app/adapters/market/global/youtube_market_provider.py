from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from .global_market_base import GlobalMarketProvider, MarketSignal


class YouTubeMarketProvider(GlobalMarketProvider):
    source_name = "youtube"
    signal_type = "video_interest"

    async def fetch_signal(self, keyword: str, country: str) -> MarketSignal:
        url = f"https://www.youtube.com/results?search_query={quote_plus(keyword)}"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            html = response.text
            lowered = html.lower()
            video_hits = html.count("videoRenderer") + html.count("gridVideoRenderer")
            comment_mentions = lowered.count("comment")
            keyword_hits = lowered.count(keyword.lower())
            recency_hits = lowered.count("publishedtimetext") + lowered.count("upcomingeventdata")
            view_hits = lowered.count("viewcounttext")
            if video_hits <= 0:
                raise ValueError("youtube video results empty")
            interest_score = min(
                100.0,
                22
                + video_hits * 1.6
                + min(comment_mentions, 80) * 0.35
                + min(keyword_hits, 30) * 0.3
                + min(view_hits, 25) * 0.45,
            )
            content_growth = min(100.0, 18 + video_hits * 1.4 + min(recency_hits, 20) * 0.8)
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=interest_score,
                trend="up" if content_growth >= 20 else "flat",
                confidence=0.74,
                data_status="real",
                metrics={
                    "youtube_interest_score": round(interest_score, 2),
                    "content_growth": round(content_growth, 2),
                    "video_count": video_hits,
                    "comment_heat": comment_mentions,
                    "keyword_presence": keyword_hits,
                    "recent_upload_proxy": recency_hits,
                    "view_signal": view_hits,
                },
            )
        except Exception as exc:
            indexed_signal = await self._fetch_bing_index_signal(keyword=keyword, country=country, error=exc)
            if indexed_signal is not None:
                return indexed_signal
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=0,
                trend="flat",
                confidence=0.2,
                data_status="fallback",
                error_detail=f"YouTube public search failed: {exc}",
            )

    async def _fetch_bing_index_signal(self, *, keyword: str, country: str, error: Exception) -> MarketSignal | None:
        mkt = "en-US" if str(country or "US").upper() == "US" else "en-GB"
        query = f"site:youtube.com {keyword}"
        url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=en-US&mkt={mkt}"
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"},
                timeout=20,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
            response.raise_for_status()
            html = response.text.lower()
            youtube_mentions = html.count("youtube.com")
            keyword_hits = html.count(keyword.lower())
            video_terms = sum(html.count(term) for term in ["watch", "video", "review", "comparison", "unboxing"])
            if youtube_mentions <= 0:
                return None
            interest_score = min(100.0, 18 + youtube_mentions * 4.2 + min(keyword_hits, 25) * 0.9 + min(video_terms, 12) * 1.2)
            growth_score = min(100.0, 16 + youtube_mentions * 3.6 + min(video_terms, 12) * 1.5)
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=interest_score,
                trend="up" if growth_score >= 28 else "flat",
                confidence=0.46,
                data_status="limited",
                metrics={
                    "youtube_interest_score": round(interest_score, 2),
                    "content_growth": round(growth_score, 2),
                    "indexed_youtube_mentions": youtube_mentions,
                    "indexed_keyword_hits": keyword_hits,
                    "indexed_video_terms": video_terms,
                    "api_mode": "search_index_limited",
                    "note": "YouTube direct access failed; using public search index evidence",
                },
                error_detail=f"youtube direct unreachable; downgraded to indexed public evidence: {error}",
            )
        except Exception:
            return None
