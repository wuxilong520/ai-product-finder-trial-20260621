from __future__ import annotations

from importlib import import_module


BingMarketProvider = import_module("app.adapters.market.global.bing_market_provider").BingMarketProvider


class BingSearchRealityProvider(BingMarketProvider):
    pass
