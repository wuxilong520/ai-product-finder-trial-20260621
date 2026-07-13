from __future__ import annotations

from pydantic import BaseModel, Field


class SupplyImportSupplier(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)


class SupplyImportPayload(BaseModel):
    source: str = Field(default="1688_extension")
    title: str = Field(..., min_length=1, max_length=1000)
    url: str = Field(..., min_length=1, max_length=2000)
    price_range: str = Field(default="", max_length=255)
    moq: str = Field(default="", max_length=255)
    supplier: SupplyImportSupplier
    images: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class SupplyExtensionCodeResponse(BaseModel):
    extension_code: str
    expires_in_seconds: int
    status: str
    platform: str


class SupplyExtensionSessionRequest(BaseModel):
    extension_code: str = Field(..., min_length=6, max_length=64)


class SupplyExtensionSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    platform: str = "1688_extension"
    status: str


class SupplyExtensionImportResponse(BaseModel):
    imported: bool
    source_type: str
    supplier_name: str | None = None
    product_title: str
    keyword: str
    import_id: int
