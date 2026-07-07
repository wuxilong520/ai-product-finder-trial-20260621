from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.contracts import ListingDraft, OAuthSession, PublishReceipt


class ExecutionAdapterBase(ABC):
    adapter_name: str
    supported_channels: tuple[str, ...]

    @abstractmethod
    def build_oauth_session(self, *, shop_domain: str) -> OAuthSession:
        raise NotImplementedError

    @abstractmethod
    def exchange_oauth_code(self, *, shop_domain: str, code: str) -> OAuthSession:
        raise NotImplementedError

    @abstractmethod
    def publish_listing(self, *, shop_domain: str, listing: ListingDraft) -> PublishReceipt:
        raise NotImplementedError

    def create_product(self, *, shop_domain: str, listing: ListingDraft, access_token: str | None = None) -> dict:
        raise NotImplementedError

    def update_product(self, *, shop_domain: str, product_id: str, listing: ListingDraft, access_token: str | None = None) -> dict:
        raise NotImplementedError

    def fetch_product(self, *, shop_domain: str, product_id: str, access_token: str | None = None) -> dict:
        raise NotImplementedError
