from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from difflib import SequenceMatcher

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.schemas import SupplierOfferSchema
from app.models.product import Product
from app.services.crawler import build_source_links


class SupplierProviderBase(ABC):
    provider_name = "base_supplier_provider"
    platform_label = ""

    @abstractmethod
    def search_suppliers(self, db: Session, keyword: str) -> list[SupplierOfferSchema]:
        raise NotImplementedError

    @abstractmethod
    def get_supplier_details(self, supplier_id: str) -> dict:
        raise NotImplementedError


class MockSupplierProvider(SupplierProviderBase):
    provider_name = "mock_supplier_provider"
    platform_label = "Mock"

    def search_suppliers(self, db: Session, keyword: str) -> list[SupplierOfferSchema]:
        candidates = self._find_products(db, keyword)
        generated = self._build_generated_offers(keyword, candidates)
        return generated

    def get_supplier_details(self, supplier_id: str) -> dict:
        return {"id": supplier_id, "status": "mock_detail_placeholder"}

    def _find_products(self, db: Session, keyword: str) -> list[Product]:
        pattern = f"%{keyword}%"
        stmt = (
            select(Product)
            .options(
                selectinload(Product.sourcing_links),
                selectinload(Product.category),
            )
            .where(
                or_(
                    Product.title.ilike(pattern),
                    Product.title_zh.ilike(pattern),
                    Product.description_text.ilike(pattern),
                )
            )
            .order_by(Product.updated_at.desc())
        )
        return list(db.scalars(stmt))

    def _build_generated_offers(self, keyword: str, products: list[Product]) -> list[SupplierOfferSchema]:
        grouped: dict[str, list[SupplierOfferSchema]] = defaultdict(list)
        for product in products:
            links = list(product.sourcing_links or [])
            if not links:
                generated_links = build_source_links(keyword)
                links = []
                if generated_links.get("1688_url"):
                    links.append(type("GeneratedLink", (), {"search_url": generated_links["1688_url"], "keyword_text": keyword})())
                if generated_links.get("pdd_url"):
                    links.append(type("GeneratedLink", (), {"search_url": generated_links["pdd_url"], "keyword_text": keyword})())

            for link in links:
                platform = self._platform_from_url(link.search_url)
                if not platform:
                    continue
                keyword_source = getattr(link, "keyword_text", None) or product.title_zh or product.title
                title_similarity = SequenceMatcher(None, keyword.lower(), keyword_source.lower()).ratio()
                category_bonus = 0.15 if product.category and keyword.lower() in product.category.name.lower() else 0
                price_reference = float(product.original_price or product.current_price) if (product.original_price or product.current_price) else None
                price_bonus = 0.10 if price_reference else 0.0
                match_score = max(0.0, min(1.0, 0.22 + (title_similarity * 0.55) + category_bonus + price_bonus))
                profit_estimate = None
                if product.current_price and price_reference:
                    profit_estimate = round(max(float(product.current_price) - float(price_reference), 0), 2)
                grouped[platform].append(
                    SupplierOfferSchema(
                        id=f"{platform}:{product.id}:{abs(hash(link.search_url))}",
                        product_keyword=keyword,
                        supplier_name="1688 搜索入口" if platform == "1688" else "拼多多 搜索入口",
                        platform="1688" if platform == "1688" else "PDD",
                        price=price_reference if price_reference is not None else (float(product.current_price) if product.current_price else None),
                        moq=1,
                        shipping_time="待确认",
                        location=product.category.name if product.category else None,
                        rating=float(product.rating) if product.rating is not None else None,
                        match_score=round(match_score * 100, 2),
                        profit_estimate=profit_estimate,
                        supplier_title=getattr(link, "keyword_text", None) or product.title,
                        supplier_url=link.search_url,
                        availability="search_link_ready",
                        currency=product.currency_code,
                        product_id=product.id,
                        source_type="mock",
                        source_id=f"{platform}:{product.id}",
                        truth_level="semi_real",
                        sync_status="success",
                        provider_name=self.provider_name,
                        lineage_chain=[self.provider_name],
                        transform_steps=["product_match_scan", "supplier_offer_build"],
                    )
                )
        offers = grouped.get("1688", []) + grouped.get("pdd", [])
        offers.sort(key=lambda item: item.match_score, reverse=True)
        return offers[:12]

    def _platform_from_url(self, url: str) -> str | None:
        if "1688.com" in url:
            return "1688"
        if "yangkeduo.com" in url or "pinduoduo.com" in url:
            return "pdd"
        return None


class Provider1688(MockSupplierProvider):
    provider_name = "provider_1688"
    platform_label = "1688"


class ProviderPDD(MockSupplierProvider):
    provider_name = "provider_pdd"
    platform_label = "PDD"


class ProviderFactoryDirect(MockSupplierProvider):
    provider_name = "provider_factory_direct"
    platform_label = "Factory"
