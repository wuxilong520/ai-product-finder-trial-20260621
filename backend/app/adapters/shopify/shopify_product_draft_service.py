from __future__ import annotations

from app.adapters.execution.shopify_adapter import ShopifyExecutionAdapter
from app.core.contracts import ListingDraft


class ShopifyProductDraftService:
    def __init__(self) -> None:
        self.adapter = ShopifyExecutionAdapter()

    def create_draft(
        self,
        *,
        shop_domain: str,
        listing: dict,
        supplier_reference: str,
        cost: float,
        margin: float,
        access_token: str | None = None,
    ) -> dict:
        draft = ListingDraft.model_validate(listing)
        result = self.adapter.create_product(
            shop_domain=shop_domain,
            listing=draft,
            access_token=access_token,
            draft_mode=True,
            extra_metafields={
                "supplier_reference": supplier_reference,
                "cost": str(cost),
                "margin": str(margin),
            },
        )
        return result


shopify_product_draft_service = ShopifyProductDraftService()
