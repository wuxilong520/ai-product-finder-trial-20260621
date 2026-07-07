from __future__ import annotations

from app.adapters.execution.base import ExecutionAdapterBase
from app.core.contracts import ListingDraft, OAuthSession, PublishReceipt


class AmazonExecutionAdapter(ExecutionAdapterBase):
    adapter_name = "amazon_execution_placeholder"
    supported_channels = ("amazon",)

    def build_oauth_session(self, *, shop_domain: str) -> OAuthSession:
        return OAuthSession(channel="amazon", shop_domain=shop_domain, authorize_url="https://sellercentral.amazon.com", state="amazon-placeholder", connected=False)

    def exchange_oauth_code(self, *, shop_domain: str, code: str) -> OAuthSession:
        return OAuthSession(channel="amazon", shop_domain=shop_domain, authorize_url="https://sellercentral.amazon.com", state="amazon-placeholder", connected=True, access_token=f"amazon-{code[-4:]}")

    def publish_listing(self, *, shop_domain: str, listing: ListingDraft) -> PublishReceipt:
        return PublishReceipt(channel="amazon", status="placeholder", listing_id="amazon-placeholder-001", publish_url="https://sellercentral.amazon.com", message="未来 Amazon 发布适配器预留。")


class ShopeeExecutionAdapter(ExecutionAdapterBase):
    adapter_name = "shopee_execution_placeholder"
    supported_channels = ("shopee",)

    def build_oauth_session(self, *, shop_domain: str) -> OAuthSession:
        return OAuthSession(channel="shopee", shop_domain=shop_domain, authorize_url="https://open.shopee.com", state="shopee-placeholder", connected=False)

    def exchange_oauth_code(self, *, shop_domain: str, code: str) -> OAuthSession:
        return OAuthSession(channel="shopee", shop_domain=shop_domain, authorize_url="https://open.shopee.com", state="shopee-placeholder", connected=True, access_token=f"shopee-{code[-4:]}")

    def publish_listing(self, *, shop_domain: str, listing: ListingDraft) -> PublishReceipt:
        return PublishReceipt(channel="shopee", status="placeholder", listing_id="shopee-placeholder-001", publish_url="https://open.shopee.com", message="未来 Shopee 发布适配器预留。")


class TikTokExecutionAdapter(ExecutionAdapterBase):
    adapter_name = "tiktok_execution_placeholder"
    supported_channels = ("tiktok",)

    def build_oauth_session(self, *, shop_domain: str) -> OAuthSession:
        return OAuthSession(channel="tiktok", shop_domain=shop_domain, authorize_url="https://seller.tiktokglobalshop.com", state="tiktok-placeholder", connected=False)

    def exchange_oauth_code(self, *, shop_domain: str, code: str) -> OAuthSession:
        return OAuthSession(channel="tiktok", shop_domain=shop_domain, authorize_url="https://seller.tiktokglobalshop.com", state="tiktok-placeholder", connected=True, access_token=f"tiktok-{code[-4:]}")

    def publish_listing(self, *, shop_domain: str, listing: ListingDraft) -> PublishReceipt:
        return PublishReceipt(channel="tiktok", status="placeholder", listing_id="tiktok-placeholder-001", publish_url="https://seller.tiktokglobalshop.com", message="未来 TikTok Shop 发布适配器预留。")
