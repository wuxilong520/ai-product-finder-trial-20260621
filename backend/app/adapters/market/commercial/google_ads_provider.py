from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.models.commercial_signal import CommercialSignal


class GoogleAdsProvider:
    source_name = "google_ads"

    async def fetch_signal(self, keyword: str, region: str) -> CommercialSignal:
        del keyword, region
        configured = all(
            [
                settings.google_ads_developer_token,
                settings.google_ads_client_id,
                settings.google_ads_client_secret,
                settings.google_ads_refresh_token,
                settings.google_ads_customer_id,
            ]
        )
        if not configured:
            return CommercialSignal(
                source=self.source_name,
                signal_type="keyword",
                score=0.0,
                reliability=0.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                is_real=False,
                status="not_configured",
                metadata={"message": "Google Ads 商业账号未配置，当前没有真实 Google Ads 商业数据。"},
            )
        return CommercialSignal(
            source=self.source_name,
            signal_type="keyword",
            score=0.0,
            reliability=0.0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            is_real=False,
            status="limited",
            metadata={"message": "Google Ads 配置已检测到，但当前代码未接入官方 SDK 调用。"},
        )

