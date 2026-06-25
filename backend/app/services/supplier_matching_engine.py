from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product, SourcingLink
from app.repositories.supplier_match import supplier_match_repository
from app.services.crawler import build_source_links
from app.services.providers import Alibaba1688Provider, FactoryProvider, PddProvider, YiwuProvider
from app.services.providers.base import SupplierProviderCandidate


class SupplierMatchingEngine:
    def match(self, db: Session, keyword: str) -> dict:
        normalized_keyword = keyword.strip()
        products = self._find_products(db, normalized_keyword)
        provider_candidates = self._collect_candidates(normalized_keyword, products)
        providers = self._build_providers(provider_candidates)

        matches: list[dict] = []
        for provider in providers:
            matches.extend(provider.search(normalized_keyword))

        matches.sort(key=lambda item: item["match_score"], reverse=True)
        unique_matches = self._deduplicate(matches)
        supplier_match_repository.upsert_many(db, unique_matches)
        return {"suppliers": unique_matches}

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

    def _collect_candidates(self, keyword: str, products: list[Product]) -> dict[str, list[SupplierProviderCandidate]]:
        candidates: dict[str, list[SupplierProviderCandidate]] = defaultdict(list)
        for product in products:
            if product.sourcing_links:
                for link in product.sourcing_links:
                    platform_code = self._platform_code_from_url(link.search_url)
                    if not platform_code:
                        continue
                    candidates[platform_code].append(
                        SupplierProviderCandidate(
                            product_id=product.id,
                            title=product.title,
                            title_zh=product.title_zh,
                            category_name=product.category.name if product.category else None,
                            keyword_text=link.keyword_text,
                            supplier_url=link.search_url,
                            current_price=float(product.current_price) if product.current_price is not None else None,
                            original_price=float(product.original_price) if product.original_price is not None else None,
                            currency_code=product.currency_code,
                        )
                    )
            else:
                generated_links = build_source_links(keyword)
                candidates["1688"].append(
                    SupplierProviderCandidate(
                        product_id=product.id,
                        title=product.title,
                        title_zh=product.title_zh,
                        category_name=product.category.name if product.category else None,
                        keyword_text=keyword,
                        supplier_url=generated_links["1688_url"],
                        current_price=float(product.current_price) if product.current_price is not None else None,
                        original_price=float(product.original_price) if product.original_price is not None else None,
                        currency_code=product.currency_code,
                    )
                )
                candidates["pdd"].append(
                    SupplierProviderCandidate(
                        product_id=product.id,
                        title=product.title,
                        title_zh=product.title_zh,
                        category_name=product.category.name if product.category else None,
                        keyword_text=keyword,
                        supplier_url=generated_links["pdd_url"],
                        current_price=float(product.current_price) if product.current_price is not None else None,
                        original_price=float(product.original_price) if product.original_price is not None else None,
                        currency_code=product.currency_code,
                    )
                )
        return candidates

    def _build_providers(self, candidates: dict[str, list[SupplierProviderCandidate]]):
        return [
            Alibaba1688Provider(candidates.get("1688", [])),
            PddProvider(candidates.get("pdd", [])),
            YiwuProvider(candidates.get("yiwu", [])),
            FactoryProvider(candidates.get("factory", [])),
        ]

    def _platform_code_from_url(self, url: str) -> str | None:
        if "1688.com" in url:
            return "1688"
        if "yangkeduo.com" in url or "pinduoduo.com" in url:
            return "pdd"
        return None

    def _deduplicate(self, matches: list[dict]) -> list[dict]:
        seen: set[tuple[int | None, str, str]] = set()
        unique: list[dict] = []
        for item in matches:
            key = (item.get("product_id"), item["platform"], item["supplier_url"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique[:8]


supplier_matching_engine = SupplierMatchingEngine()
