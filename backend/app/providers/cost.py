from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.schemas import CostModelSchema, SupplierOfferSchema


class CostProviderBase(ABC):
    provider_name = "base_cost_provider"

    @abstractmethod
    def calculate_cost(self, product: dict) -> CostModelSchema:
        raise NotImplementedError

    @abstractmethod
    def get_shipping_cost(self, region: str) -> float:
        raise NotImplementedError


class MockCostProvider(CostProviderBase):
    provider_name = "mock_cost_provider"

    def calculate_cost(self, product: dict) -> CostModelSchema:
        suppliers: list[SupplierOfferSchema] = product.get("suppliers", [])
        selling_price = float(product.get("selling_price") or 0)
        package_weight_kg = float(product.get("package_weight_kg") or 0.45)
        currency = product.get("currency") or "USD"

        supplier_prices = [float(item.price or 0) for item in suppliers if item.price]
        product_cost = min(supplier_prices) if supplier_prices else round(max(selling_price * 0.42, 1), 2)
        shipping_cost = round(4.8 + package_weight_kg * 6.5, 2)
        platform_fee = round(selling_price * 0.15, 2)
        ads_cost = round(max(selling_price * 0.08, 0.5), 2) if selling_price else 0.5
        packaging_cost = 0.8
        total_cost = round(product_cost + shipping_cost + platform_fee + ads_cost + packaging_cost, 2)

        return CostModelSchema(
            product_cost=round(product_cost, 2),
            shipping_cost=round(shipping_cost, 2),
            platform_fee=round(platform_fee, 2),
            ads_cost=round(ads_cost, 2),
            packaging_cost=round(packaging_cost, 2),
            total_cost=round(total_cost, 2),
            currency=currency,
            source_type="estimated",
            source_id=f"mock_cost:{currency}:{round(selling_price, 2)}",
            truth_level="simulated" if not supplier_prices else "semi_real",
            sync_status="success",
            provider_name=self.provider_name,
            lineage_chain=[self.provider_name],
            transform_steps=["supplier_price_pick", "cost_formula_apply"],
        )

    def get_shipping_cost(self, region: str) -> float:
        return 7.73 if region == "amazon_us" else 5.89


class LogisticsAPIProvider(CostProviderBase):
    provider_name = "logistics_api_provider"

    def calculate_cost(self, product: dict) -> CostModelSchema:
        return MockCostProvider().calculate_cost(product)

    def get_shipping_cost(self, region: str) -> float:
        return MockCostProvider().get_shipping_cost(region)
