from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from statistics import mean

import httpx

from app.adapters.market.v3 import MarketDataProvider, MarketSignal
from app.core.config import settings


class AmazonMarketProviderV3(MarketDataProvider):
    provider_name = "amazon"

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
                error_detail="Amazon Product Advertising API 凭证不完整",
            )
        try:
            payload = await self._search_items(keyword=keyword)
            items = list(((payload.get("SearchResult") or {}).get("Items")) or [])
            if not items:
                return self._unavailable(
                    keyword=keyword,
                    region=region,
                    error_detail="Amazon PA API 没返回商品结果",
                )
            price_values = []
            rating_values = []
            review_counts = []
            sales_ranks = []
            for item in items:
                offer = (((item.get("OffersV2") or {}).get("Listings") or [{}])[0]) if item.get("OffersV2") else (((item.get("Offers") or {}).get("Listings") or [{}])[0])
                display_amount = (
                    (((offer.get("Price") or {}).get("Amount")) or 0)
                )
                if display_amount:
                    price_values.append(float(display_amount))
                rating = ((((item.get("ItemInfo") or {}).get("ContentInfo") or {}).get("AdultProduct")) or 0)
                if rating:
                    rating_values.append(float(rating))
                customer_reviews = (((item.get("ItemInfo") or {}).get("ByLineInfo") or {}).get("Contributors")) or []
                if customer_reviews:
                    review_counts.append(float(len(customer_reviews)))
                browse_nodes = ((((item.get("BrowseNodeInfo") or {}).get("BrowseNodes")) or []))
                if browse_nodes:
                    rank = (browse_nodes[0].get("SalesRank") or 0)
                    if rank:
                        sales_ranks.append(float(rank))
            total_results = float((payload.get("SearchResult") or {}).get("TotalResultCount") or len(items))
            average_price = round(mean(price_values), 2) if price_values else 0.0
            review_count = round(mean(review_counts), 2) if review_counts else 0.0
            rating = round(mean(rating_values), 2) if rating_values else 0.0
            avg_sales_rank = round(mean(sales_ranks), 2) if sales_ranks else 0.0
            demand_score = max(
                0.0,
                min(
                    100.0,
                    (min(total_results / 100.0, 40.0) * 0.35)
                    + (max(0.0, 100 - min(avg_sales_rank / 5000.0, 70.0)) * 0.35)
                    + (min(review_count / 10.0, 20.0) * 0.15)
                    + (min(rating * 20.0, 20.0) * 0.15),
                ),
            )
            competition_level = "high" if total_results >= 5000 else "medium" if total_results >= 1000 else "low"
            return self._signal(
                keyword=keyword,
                region=region,
                value=demand_score,
                confidence=0.88,
                is_real=True,
                api_status="REAL",
                metrics={
                    "search_results": total_results,
                    "category_rank": avg_sales_rank,
                    "price_range": {
                        "min": round(min(price_values), 2) if price_values else 0.0,
                        "max": round(max(price_values), 2) if price_values else 0.0,
                        "average": average_price,
                    },
                    "seller_count": len(items),
                    "review_count": review_count,
                    "rating": rating,
                    "sales_rank": avg_sales_rank,
                    "competition_level": competition_level,
                    "competition_score": round(min(total_results / 100.0, 100.0), 2),
                    "review_density": review_count,
                    "amazon_demand_score": round(demand_score, 2),
                    "source_type": "amazon_paapi",
                },
            )
        except Exception as exc:
            return self._unavailable(
                keyword=keyword,
                region=region,
                error_detail=f"Amazon provider 失败: {exc}",
            )

    def _missing_credentials(self) -> list[str]:
        required = {
            "AMAZON_PAAPI_ACCESS_KEY": settings.amazon_paapi_access_key,
            "AMAZON_PAAPI_SECRET_KEY": settings.amazon_paapi_secret_key,
            "AMAZON_PAAPI_PARTNER_TAG": settings.amazon_paapi_partner_tag,
            "AMAZON_PAAPI_REGION": settings.amazon_paapi_region,
            "AMAZON_PAAPI_HOST": settings.amazon_paapi_host,
        }
        return [key for key, value in required.items() if not str(value or "").strip()]

    async def _search_items(self, *, keyword: str) -> dict:
        host = str(settings.amazon_paapi_host or "").strip()
        region = str(settings.amazon_paapi_region or "").strip()
        payload = {
            "Keywords": keyword,
            "SearchIndex": "All",
            "ItemCount": 10,
            "PartnerTag": str(settings.amazon_paapi_partner_tag or "").strip(),
            "PartnerType": "Associates",
            "Marketplace": f"https://{host}",
            "Resources": [
                "BrowseNodeInfo.BrowseNodes",
                "ItemInfo.Title",
                "OffersV2.Listings.Price",
            ],
        }
        body = json.dumps(payload, separators=(",", ":"))
        amz_date = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        date_stamp = datetime.now(UTC).strftime("%Y%m%d")
        canonical_headers = (
            f"content-encoding:amz-1.0\n"
            f"content-type:application/json; charset=utf-8\n"
            f"host:{host}\n"
            f"x-amz-date:{amz_date}\n"
            f"x-amz-target:com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems\n"
        )
        signed_headers = "content-encoding;content-type;host;x-amz-date;x-amz-target"
        payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        canonical_request = "\n".join([
            "POST",
            "/paapi5/searchitems",
            "",
            canonical_headers,
            signed_headers,
            payload_hash,
        ])
        credential_scope = f"{date_stamp}/{region}/ProductAdvertisingAPI/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ])
        signature = self._signature(date_stamp=date_stamp, region=region, string_to_sign=string_to_sign)
        authorization = (
            f"AWS4-HMAC-SHA256 Credential={settings.amazon_paapi_access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        headers = {
            "Content-Encoding": "amz-1.0",
            "Content-Type": "application/json; charset=utf-8",
            "Host": host,
            "X-Amz-Date": amz_date,
            "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
            "Authorization": authorization,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"https://{host}/paapi5/searchitems", content=body, headers=headers)
            response.raise_for_status()
            return response.json() or {}

    def _signature(self, *, date_stamp: str, region: str, string_to_sign: str) -> str:
        secret = f"AWS4{settings.amazon_paapi_secret_key}".encode("utf-8")
        date_key = hmac.new(secret, date_stamp.encode("utf-8"), hashlib.sha256).digest()
        region_key = hmac.new(date_key, region.encode("utf-8"), hashlib.sha256).digest()
        service_key = hmac.new(region_key, b"ProductAdvertisingAPI", hashlib.sha256).digest()
        signing_key = hmac.new(service_key, b"aws4_request", hashlib.sha256).digest()
        return hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
