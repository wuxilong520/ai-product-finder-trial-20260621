from __future__ import annotations

from importlib import import_module


YouTubeMarketProvider = import_module("app.adapters.market.global.youtube_market_provider").YouTubeMarketProvider


class YouTubeRealityProvider(YouTubeMarketProvider):
    pass
