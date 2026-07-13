from __future__ import annotations

from importlib import import_module
from statistics import mean
from urllib.parse import quote_plus

import httpx


GlobalMarketProvider = import_module("app.adapters.market.global.global_market_base").GlobalMarketProvider


class RedditOfficialProvider(GlobalMarketProvider):
    source_name = "reddit"
    signal_type = "discussion"

    async def fetch_signal(self, keyword: str, country: str):
        del country
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            async with httpx.AsyncClient(headers=headers, timeout=20, follow_redirects=True) as client:
                direct_signal = await self._fetch_direct_reddit_signal(client, keyword)
                if direct_signal is not None:
                    return direct_signal

                indexed_signal = await self._fetch_indexed_reddit_signal(client, keyword)
                if indexed_signal is not None:
                    return indexed_signal

                raise ValueError("reddit direct api blocked and indexed signal unavailable")
        except Exception as exc:
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=0,
                trend="flat",
                confidence=0.15,
                data_status="fallback",
                error_detail=f"Reddit official API failed: {exc}",
            )

    async def _fetch_direct_reddit_signal(self, client: httpx.AsyncClient, keyword: str):
        urls = [
            f"https://api.reddit.com/search.json?q={quote_plus(keyword)}&sort=relevance&t=month&limit=25&raw_json=1",
            f"https://www.reddit.com/search.json?q={quote_plus(keyword)}&sort=relevance&t=month&limit=25&raw_json=1",
        ]
        for url in urls:
            try:
                response = await client.get(url)
            except Exception:
                continue
            if response.status_code >= 400:
                continue
            payload = response.json() or {}
            children = (((payload.get("data") or {}).get("children")) or [])
            posts = [item.get("data") or {} for item in children if isinstance(item, dict)]
            if not posts:
                continue
            mentions = len(posts)
            comment_volume = sum(int(item.get("num_comments") or 0) for item in posts[:25])
            score = min(100.0, mentions * 4 + min(comment_volume, 400) * 0.12 + 14)
            sentiment_proxy = []
            for item in posts[:12]:
                title = f"{item.get('title') or ''} {item.get('selftext') or ''}".lower()
                if any(word in title for word in ["love", "best", "worth", "recommend", "great"]):
                    sentiment_proxy.append(1)
                elif any(word in title for word in ["bad", "avoid", "worst", "issue", "problem"]):
                    sentiment_proxy.append(-1)
                else:
                    sentiment_proxy.append(0)
            sentiment = round(mean(sentiment_proxy), 2) if sentiment_proxy else 0.0
            return self.build_signal(
                keyword=keyword,
                country="global",
                value=score,
                trend="up" if mentions >= 8 else "flat",
                confidence=0.72,
                data_status="limited",
                metrics={
                    "discussion_volume": mentions,
                    "subreddit_mentions": mentions,
                    "comment_volume": comment_volume,
                    "sentiment": sentiment,
                    "api_mode": "official_limited",
                },
            )
        return None

    async def _fetch_indexed_reddit_signal(self, client: httpx.AsyncClient, keyword: str):
        query = f"site:reddit.com {keyword}"
        url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=en-US&mkt=en-US"
        response = await client.get(url)
        response.raise_for_status()
        html = response.text.lower()
        reddit_mentions = html.count("reddit.com")
        keyword_hits = html.count(keyword.lower())
        discussion_terms = sum(html.count(term) for term in ["recommend", "best", "review", "worth", "vs"])
        if reddit_mentions <= 0:
            return None
        score = min(100.0, 18 + reddit_mentions * 4 + keyword_hits * 3 + min(discussion_terms, 8) * 1.5)
        return self.build_signal(
            keyword=keyword,
            country="global",
            value=score,
            trend="up" if reddit_mentions >= 5 else "flat",
            confidence=0.46,
            data_status="limited",
            metrics={
                "discussion_volume": reddit_mentions,
                "indexed_keyword_hits": keyword_hits,
                "discussion_term_hits": discussion_terms,
                "api_mode": "search_index_limited",
                "note": "Reddit direct public endpoint blocked; using public search index evidence",
            },
            error_detail="reddit direct endpoint blocked; downgraded to indexed public evidence",
        )
