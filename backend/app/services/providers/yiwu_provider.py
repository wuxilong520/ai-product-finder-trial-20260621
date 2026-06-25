from app.services.providers.base import SupplierProviderBase


class YiwuProvider(SupplierProviderBase):
    provider_code = "yiwu"
    provider_label = "义乌"

    def search(self, keyword: str) -> list[dict]:
        return []
