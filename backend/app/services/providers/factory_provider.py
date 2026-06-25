from app.services.providers.base import SupplierProviderBase


class FactoryProvider(SupplierProviderBase):
    provider_code = "factory"
    provider_label = "工厂库"

    def search(self, keyword: str) -> list[dict]:
        return []
