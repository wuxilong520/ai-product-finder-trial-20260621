from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    url: str = Field(
        ...,
        description="商品页面链接",
        examples=["https://example-store.com/products/example-product"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example-store.com/products/example-product"
            }
        }
    }


class PublicProductExtractRequest(BaseModel):
    url: str = Field(
        ...,
        description="公开商品页面链接",
        examples=["https://www.amazon.com/dp/B0EXAMPLE123"],
    )


class PublicProductExtractBlocked(BaseModel):
    status: Literal["BLOCKED"]
    reason: Literal["captcha_or_login_or_invalid_page"]


class PublicProductExtractResponse(BaseModel):
    status: Literal["OK"]
    url: str
    platform: Literal["amazon", "aliexpress", "shopify"]
    title: str
    price: str
    rating: str
    review_count: str
    images: list[str]
    sales: str | None = None
    availability: str | None = None
    dom_parsed: bool
    entered_product_page: bool


class CrawlResult(BaseModel):
    product_id: int | None = None
    title: str
    price: str
    images: list[str]
    rating: str
    reviews: str
    url: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": 1,
                "title": "Example Product Title",
                "price": "0.00",
                "images": [
                    "https://example.com/images/product.jpg"
                ],
                "rating": "0.0",
                "reviews": "0",
                "url": "https://example-store.com/products/example-product",
            }
        }
    }


class AnalyzeRequest(BaseModel):
    product_id: int | None = None
    title: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1,
                    "title": None,
                },
                {
                    "product_id": None,
                    "title": "Example Product Title",
                },
            ]
        }
    }


class AnalyzeFullRequest(BaseModel):
    url: str = Field(
        ...,
        description="公开商品页面链接",
        examples=["https://kyliecosmetics.com/products/matte-lip-kit"],
    )
    lang: Literal["zh", "en"] = Field(default="zh", description="返回语言")


class AnalyzeResult(BaseModel):
    title_zh: str
    core_keywords: list[str]
    selling_points: list[str]
    sourcing_keywords: list[str]
    source_links: dict[str, str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "title_zh": "示例商品中文标题",
                "core_keywords": ["示例关键词1", "示例关键词2", "示例关键词3"],
                "selling_points": ["示例卖点1", "示例卖点2", "示例卖点3"],
                "sourcing_keywords": ["示例采购词1", "示例采购词2", "示例采购词3"],
                "source_links": {
                    "1688_url": "https://s.1688.com/selloffer/offer_search.htm?keywords=%E7%A4%BA%E4%BE%8B%E9%87%87%E8%B4%AD%E8%AF%8D",
                    "pdd_url": "https://mobile.yangkeduo.com/search_result.html?search_key=%E7%A4%BA%E4%BE%8B%E9%87%87%E8%B4%AD%E8%AF%8D",
                },
            }
        }
    }


class ProductIntelligenceResult(BaseModel):
    product_score: int
    profit_estimate: str
    competition_level: Literal["low", "medium", "high"]
    selling_potential: Literal["weak", "ok", "strong"]
    recommendation: Literal["sell", "monitor", "ignore"]
    reason: list[str]


class ProductImageRead(BaseModel):
    id: int
    image_url: str
    sort_order: int
    is_primary: bool

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    title: str
    title_zh: str | None = None
    source_url: str
    description_text: str | None = None
    currency_code: str | None = None
    current_price: float | None = None
    original_price: float | None = None
    review_count: int = 0
    rating: float | None = None


class ProductRead(ProductBase):
    id: int
    platform_id: int
    category_id: int | None = None
    external_product_id: str | None = None
    is_active: bool
    last_crawled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageRead] = []

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    total: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "platform_id": 3,
                        "category_id": None,
                        "external_product_id": None,
                        "title": "Example Product Title",
                        "title_zh": "示例商品中文标题",
                        "source_url": "https://example-store.com/products/example-product",
                        "description_text": None,
                        "currency_code": "CNY",
                        "current_price": 0.0,
                        "original_price": 0.0,
                        "review_count": 0,
                        "rating": 0.0,
                        "is_active": True,
                        "last_crawled_at": "2026-06-20T10:10:00+08:00",
                        "created_at": "2026-06-20T10:10:00+08:00",
                        "updated_at": "2026-06-20T10:10:00+08:00",
                        "images": [
                            {
                                "id": 1,
                                "image_url": "https://example.com/images/product.jpg",
                                "sort_order": 0,
                                "is_primary": True,
                            }
                        ],
                    }
                ],
                "total": 1,
            }
        }
    }


class CrawlResponse(BaseModel):
    product_id: int | None = None
    title: str
    price: str
    images: list[str]
    rating: str
    reviews: str
    url: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Example Product Title",
                "product_id": 1,
                "price": "0.00",
                "images": [
                    "https://example.com/images/product.jpg"
                ],
                "rating": "0.0",
                "reviews": "0",
                "url": "https://example-store.com/products/example-product",
            }
        }
    }


class AnalyzeResponse(BaseModel):
    product: ProductRead
    analysis: AnalyzeResult
    intelligence: ProductIntelligenceResult

    model_config = {
        "json_schema_extra": {
            "example": {
                "product": {
                    "id": 1,
                    "platform_id": 3,
                    "category_id": None,
                    "external_product_id": None,
                    "title": "Example Product Title",
                    "title_zh": "示例商品中文标题",
                    "source_url": "https://example-store.com/products/example-product",
                    "description_text": None,
                    "currency_code": "CNY",
                    "current_price": 0.0,
                    "original_price": 0.0,
                    "review_count": 0,
                    "rating": 0.0,
                    "is_active": True,
                    "last_crawled_at": "2026-06-20T10:10:00+08:00",
                    "created_at": "2026-06-20T10:10:00+08:00",
                    "updated_at": "2026-06-20T10:12:00+08:00",
                    "images": [
                        {
                            "id": 1,
                            "image_url": "https://example.com/images/product.jpg",
                            "sort_order": 0,
                            "is_primary": True,
                        }
                    ],
                },
                "analysis": {
                    "title_zh": "示例商品中文标题",
                    "core_keywords": ["示例关键词1", "示例关键词2", "示例关键词3"],
                    "selling_points": ["示例卖点1", "示例卖点2", "示例卖点3"],
                    "sourcing_keywords": ["示例采购词1", "示例采购词2", "示例采购词3"],
                    "source_links": {
                        "1688_url": "https://s.1688.com/selloffer/offer_search.htm?keywords=%E7%A4%BA%E4%BE%8B%E9%87%87%E8%B4%AD%E8%AF%8D",
                        "pdd_url": "https://mobile.yangkeduo.com/search_result.html?search_key=%E7%A4%BA%E4%BE%8B%E9%87%87%E8%B4%AD%E8%AF%8D",
                    },
                },
                "intelligence": {
                    "product_score": 78,
                    "profit_estimate": "按公开售价估算，拿货成本约 12.25，可留利润约 15.75",
                    "competition_level": "medium",
                    "selling_potential": "strong",
                    "recommendation": "sell",
                    "reason": [
                        "利润潜力：客单价中等，仍有利润空间；商品类型明确，便于找货源",
                        "竞争强度：评论量中等，竞争中等；品牌压制感不强，更适合中小卖家切入"
                    ]
                }
            }
        }
    }


class AnalyzeFullBlockedResponse(BaseModel):
    status: Literal["BLOCKED"]
    lang: Literal["zh", "en"]
    message: str


class AnalyzeFullResponse(BaseModel):
    status: Literal["OK", "FALLBACK"]
    lang: Literal["zh", "en"]
    platform: Literal["amazon", "aliexpress", "shopify"]
    title: str
    title_zh: str
    price: str
    image: str = ""
    score: int
    product_score: int
    recommendation: str
    recommendation_key: Literal["sell", "monitor", "ignore"]
    profit_estimate: str
    competition_level: str
    competition_level_key: Literal["low", "medium", "high"]
    source_links: dict[str, str]
    core_keywords: list[str]
    selling_points: list[str]
    reason: list[str]
    fallback_score: int | None = None
    ai_unavailable: bool = False


class CrawlPreview(BaseModel):
    source_platform: Literal["amazon", "aliexpress", "shopify"]
    source_url: str
    title: str
    image_url: str | None = None
    image_urls: list[str] = []
    price: float | None = None
    original_price: float | None = None
    currency: str | None = None
    review_count: int | None = None
    rating: float | None = None
    category: str | None = None
    raw_price: str = ""
    raw_rating: str = ""
    raw_reviews: str = ""
