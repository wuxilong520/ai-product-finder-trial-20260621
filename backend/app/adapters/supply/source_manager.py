from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy.orm import Session

from app.adapters.supply.alibaba_1688_adapter import Alibaba1688Provider, AlibabaQuery
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
        self.alibaba_provider = Alibaba1688Provider()

    async def collect(self, db: Session, *, query: AlibabaQuery) -> dict[str, dict]:
        database_adapter = SupplierDatabaseAdapter(db)
        return {
            SupplySource.ALIBABA_API.value: await self.alibaba_provider.fetch_api(query),
            SupplySource.MERCHANT_AUTHORIZED.value: await database_adapter.fetch_by_source_types(
                keyword=query.keyword,
                source_types=[SupplySource.MERCHANT_AUTHORIZED.value],
                category=query.category,
            ),
            SupplySource.BROWSER_EXTENSION.value: await database_adapter.fetch_by_source_types(
                keyword=query.keyword,
                source_types=[SupplySource.BROWSER_EXTENSION.value],
                category=query.category,
            ),
            SupplySource.CSV_IMPORT.value: await database_adapter.fetch_by_source_types(
                keyword=query.keyword,
                source_types=[SupplySource.CSV_IMPORT.value],
                category=query.category,
            ),
            SupplySource.MANUAL_INPUT.value: await database_adapter.fetch_by_source_types(
                keyword=query.keyword,
                source_types=[SupplySource.MANUAL_INPUT.value],
                category=query.category,
            ),
            SupplySource.CACHE_DATABASE.value: await database_adapter.fetch_by_source_types(
                keyword=query.keyword,
                source_types=[SupplySource.CACHE_DATABASE.value, "cached"],
                category=query.category,
            ),
            SupplySource.PUBLIC_PAGE.value: await self.alibaba_provider.fetch_public_page(query),
        }


source_manager = SupplySourceManager()
