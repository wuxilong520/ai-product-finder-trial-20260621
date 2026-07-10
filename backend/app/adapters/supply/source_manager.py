from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy.orm import Session

from app.adapters.supply.alibaba_1688_adapter import AlibabaQuery
from app.adapters.supply.alibaba1688_provider_v2 import Alibaba1688ProviderV2
from app.adapters.supply.supplier_database_adapter import SupplierDatabaseAdapter


class SupplySource(StrEnum):
    ALIBABA_API = "alibaba_api"
    MERCHANT_AUTHORIZED = "merchant_authorized"
    BROWSER_EXTENSION = "browser_extension"
    CSV_IMPORT = "csv_import"
    MANUAL_INPUT = "manual_input"
    CACHE_DATABASE = "cache_database"
    PUBLIC_PAGE = "public_page"


@dataclass(frozen=True)
class SourceDescriptor:
    source: SupplySource
    priority: int
    enabled: bool = True


class SupplySourceManager:
    def __init__(self) -> None:
        self.alibaba_provider = Alibaba1688ProviderV2()

    async def collect(self, db: Session, *, query: AlibabaQuery) -> dict[str, dict]:
        database_adapter = SupplierDatabaseAdapter(db)
        return {
            SupplySource.ALIBABA_API.value: await self.alibaba_provider.fetch_api(query),
            SupplySource.MERCHANT_AUTHORIZED.value: await self.alibaba_provider.fetch_merchant_authorized(db, query),
            SupplySource.BROWSER_EXTENSION.value: await self.alibaba_provider.fetch_browser_extension(db, query),
            SupplySource.CSV_IMPORT.value: await self.alibaba_provider.fetch_user_upload(db, query),
            SupplySource.MANUAL_INPUT.value: await database_adapter.fetch_by_source_types(
                keyword=query.keyword,
                source_types=[SupplySource.MANUAL_INPUT.value],
                category=query.category,
            ),
            SupplySource.CACHE_DATABASE.value: await self.alibaba_provider.fetch_cache(db, query),
            SupplySource.PUBLIC_PAGE.value: {
                "source": "public_page_disabled",
                "data": {"keyword": query.keyword, "suppliers": []},
                "timestamp": "",
                "confidence": 0.0,
                "is_mock": False,
                "source_status": "unavailable",
            },
        }


source_manager = SupplySourceManager()
