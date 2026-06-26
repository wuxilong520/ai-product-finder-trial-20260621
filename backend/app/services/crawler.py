from __future__ import annotations

import asyncio
import json
import random
import re
from urllib.parse import quote, urlparse

from app.core.runtime import AppError, log_info
from app.schemas.product import CrawlPreview, CrawlResult


USER_AGENTS = [
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
]
SCRAPE_RETRY_TIMES = 3
SCRAPE_TIMEOUT_MS = 18000
FAST_BLOCK_TIMEOUT_MS = 7000


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "1688.com" in host:
        return "1688"
    if "amazon." in host:
        return "amazon"
    if "aliexpress." in host:
        return "aliexpress"
    return "shopify"


async def crawl_product(url: str) -> CrawlPreview:
    platform = detect_platform(url)
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        raise AppError("REAL_SCRAPE_FAILED", "Playwright 不可用，无法进行真实采集", "scrape", 500) from exc

    last_error: Exception | None = None
    for attempt in range(1, SCRAPE_RETRY_TIMES + 1):
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    locale="en-US",
                    viewport={
                        "width": random.randint(1280, 1600),
                        "height": random.randint(720, 980),
                    },
                )
                page = await context.new_page()
                await _apply_stealth(page)
                await _load_page(page, url, platform)
                if platform != "1688":
                    await _human_delay()

                if platform == "amazon":
                    data = await _parse_amazon(page, url)
                elif platform == "1688":
                    if await _looks_like_1688_blocked(page):
                        raise AppError("REAL_SCRAPE_FAILED", "1688 当前触发了校验页，公网环境暂时拿不到真实商品详情", "scrape", 500)
                    data = await _parse_1688(page, url)
                elif platform == "aliexpress":
                    data = await _parse_aliexpress(page, url)
                else:
                    data = await _parse_shopify(page, url)

                await context.close()
                await browser.close()

                if not data.title or data.title == "未识别标题":
                    raise AppError("REAL_SCRAPE_FAILED", "页面打开了，但没有拿到商品标题", "scrape", 500)

                log_info(f"SCRAPE_OK | url={url} | platform={platform} | title={data.title}")
                return data
        except Exception as exc:
            last_error = exc
            log_info(f"SCRAPE_RETRY | url={url} | platform={platform} | attempt={attempt} | error={exc}")
            if attempt < SCRAPE_RETRY_TIMES:
                await asyncio.sleep(min(attempt, 2))

    reason = str(last_error) if last_error else "未知采集错误"
    raise AppError("REAL_SCRAPE_FAILED", reason, "scrape", 500) from last_error


def _to_float(value: str | None) -> float | None:
    if not value:
        return None
    text = value.replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    return float(match.group(1))


async def _get_first_text(page, selectors: list[str]) -> str:
    for selector in selectors:
        locator = page.locator(selector)
        try:
            await locator.first.wait_for(state="visible", timeout=2500)
        except Exception:
            pass
        if await locator.count() > 0:
            text = (await locator.first.text_content() or "").strip()
            if text:
                return text
    return ""


async def _get_first_attr(page, selectors: list[str], attr: str) -> str:
    for selector in selectors:
        locator = page.locator(selector)
        try:
            await locator.first.wait_for(state="attached", timeout=2500)
        except Exception:
            pass
        if await locator.count() > 0:
            value = await locator.first.get_attribute(attr)
            if value:
                return value.strip()
    return ""


async def _get_images(page, selectors: list[str], attr: str = "src", limit: int = 8) -> list[str]:
    images: list[str] = []
    for selector in selectors:
        locator = page.locator(selector)
        try:
            await locator.first.wait_for(state="attached", timeout=2500)
        except Exception:
            pass
        count = await locator.count()
        if count == 0:
            continue
        for index in range(min(count, limit)):
            value = await locator.nth(index).get_attribute(attr)
            if value and value not in images:
                images.append(value)
        if images:
            break
    return images


async def _extract_shopify_schema(page) -> dict:
    script_locators = [
        "script[type='application/ld+json']",
        "script[data-product-json]",
        "script[id*='ProductJson']",
    ]

    for selector in script_locators:
        locator = page.locator(selector)
        count = await locator.count()
        for index in range(count):
            raw_text = (await locator.nth(index).text_content() or "").strip()
            if not raw_text:
                continue
            try:
                payload = json.loads(raw_text)
            except Exception:
                continue
            parsed = _parse_schema_payload(payload)
            if parsed.get("title") or parsed.get("price_text"):
                return parsed
    return {}


async def _parse_amazon(page, url: str) -> CrawlPreview:
    title = await _get_first_text(page, ["#productTitle", "span#productTitle", "h1 span", "#title span"])
    price = await _get_first_text(
        page,
        [
            ".a-price .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-offscreen",
            "#corePrice_feature_div .a-offscreen",
            "span[data-a-color='price'] .a-offscreen",
        ],
    )
    rating = await _get_first_text(page, ["span.a-icon-alt", "#acrPopover span.a-size-base", "[data-hook='rating-out-of-text']"])
    reviews = await _get_first_text(page, ["#acrCustomerReviewText", "span[data-hook='total-review-count']", "#reviewsMedley span"])
    images = await _get_images(page, ["#landingImage", "#imgTagWrapperId img", "#altImages img", "img[data-old-hires]"], attr="src")

    return CrawlPreview(
        source_platform="amazon",
        source_url=url,
        title=title or "未识别标题",
        image_url=images[0] if images else None,
        image_urls=images,
        price=_to_float(price),
        original_price=None,
        currency="USD",
        review_count=int(_to_float(reviews) or 0) or None,
        rating=_to_float(rating),
        category=None,
        raw_price=price,
        raw_rating=rating,
        raw_reviews=reviews,
    )


async def _parse_aliexpress(page, url: str) -> CrawlPreview:
    title = await _get_first_text(page, ["h1", "meta[property='og:title']", "[data-pl='product-title']"])
    price = await _get_first_text(
        page,
        [
            ".price--currentPriceText--V8_y_b5",
            ".product-price-current",
            "[class*='price--currentPriceText']",
            "[class*='uniform-banner-box-price']",
        ],
    )
    rating = await _get_first_text(page, [".overview--rating--19l0s_DB", "[class*='overview--rating']", "[data-pl='product-reviewer-rating']"])
    reviews = await _get_first_text(page, [".overview--评价人数--z_VfxE8y", "[class*='overview--reviews']", "[data-pl='product-reviewer-reviews']"])
    images = await _get_images(page, ["img.magnifier--image--L4hZ4dC", "img[src*='alicdn']", ".images-view-item img", "img[class*='images-view-item']"])

    return CrawlPreview(
        source_platform="aliexpress",
        source_url=url,
        title=title or "未识别标题",
        image_url=images[0] if images else None,
        image_urls=images,
        price=_to_float(price),
        original_price=None,
        currency="USD",
        review_count=int(_to_float(reviews) or 0) or None,
        rating=_to_float(rating),
        category=None,
        raw_price=price,
        raw_rating=rating,
        raw_reviews=reviews,
    )


async def _parse_1688(page, url: str) -> CrawlPreview:
    final_url = page.url.lower()
    title_text = (await page.title() or "").lower()
    html = (await page.content() or "").lower()

    if "_____tmd_____" in final_url or "x5secdata=" in final_url or "\"action\":\"captcha\"" in html or "captcha" in title_text:
        raise AppError("REAL_SCRAPE_FAILED", "1688 当前触发了校验页，公网环境暂时拿不到真实商品详情", "scrape", 500)

    title = await _get_first_text(
        page,
        [
            "h1",
            ".d-title",
            ".title-text",
            "[class*='title']",
        ],
    )
    price = await _get_first_text(
        page,
        [
            ".price-now",
            ".price",
            "[class*='price']",
            "[data-testid='price']",
        ],
    )
    images = await _get_images(
        page,
        [
            "img[src*='alicdn.com']",
            "img[data-src*='alicdn.com']",
            ".vertical-img img",
            ".detail-gallery img",
        ],
    )

    clean_title = (title or "").strip()
    if not clean_title or clean_title == "义乌趣织饰品有限公司":
        raise AppError("REAL_SCRAPE_FAILED", "1688 页面没有拿到真实商品标题，当前更像是店铺页或校验页", "scrape", 500)

    return CrawlPreview(
        source_platform="1688",
        source_url=url,
        title=clean_title,
        image_url=images[0] if images else None,
        image_urls=images,
        price=_to_float(price),
        original_price=None,
        currency="CNY",
        review_count=None,
        rating=None,
        category=None,
        raw_price=price,
        raw_rating="",
        raw_reviews="",
    )


async def _parse_shopify(page, url: str) -> CrawlPreview:
    schema = await _extract_shopify_schema(page)
    title = await _get_first_text(page, ["h1", "[data-product-title]"])
    price = await _get_first_text(
        page,
        [
            "[data-product-price] .money",
            ".price .money",
            ".price__current",
            ".product-price .money",
            "[class*='price']",
            "[data-product-price]",
            ".price-item--sale",
            ".price-item",
            "[data-sale-price]",
        ],
    )
    rating = await _get_first_text(page, ["[data-rating]", ".jdgm-prev-badge__text", ".spr-badge-caption"])
    reviews = await _get_first_text(page, ["[data-review-count]", ".jdgm-prev-badge__text", ".spr-badge-caption"])
    images = await _get_images(page, ["img[src*='cdn.shopify.com']", ".product__media img", ".product-gallery img", "[data-product-media] img"])

    clean_title = _clean_title(title or schema.get("title") or "")
    clean_price = _normalize_currency_text(price or schema.get("price_text") or "")
    clean_rating = _normalize_rating_value(rating or schema.get("rating_text") or "")
    clean_reviews = _normalize_review_count(reviews or schema.get("review_count_text") or "")

    return CrawlPreview(
        source_platform="shopify",
        source_url=url,
        title=clean_title or "未识别标题",
        image_url=images[0] if images else None,
        image_urls=images,
        price=_to_float(clean_price),
        original_price=None,
        currency="USD",
        review_count=int(clean_reviews.replace(",", "")) if clean_reviews else None,
        rating=float(clean_rating) if clean_rating else None,
        category=None,
        raw_price=clean_price,
        raw_rating=clean_rating,
        raw_reviews=clean_reviews,
    )


def build_source_links(keyword: str) -> dict[str, str]:
    encoded = quote(keyword)
    return {
        "keyword": keyword,
        "1688_url": f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded}",
        "pdd_url": f"https://mobile.yangkeduo.com/search_result.html?search_key={encoded}",
    }


def to_crawl_result(preview: CrawlPreview) -> CrawlResult:
    return CrawlResult(
        title=preview.title,
        price=preview.raw_price or (str(preview.price) if preview.price is not None else ""),
        images=preview.image_urls,
        rating=preview.raw_rating or (str(preview.rating) if preview.rating is not None else ""),
        reviews=preview.raw_reviews or (str(preview.review_count) if preview.review_count is not None else ""),
        url=preview.source_url,
    )


async def _load_page(page, url: str, platform: str) -> None:
    try:
        timeout = FAST_BLOCK_TIMEOUT_MS if platform == "1688" else SCRAPE_TIMEOUT_MS
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        if platform != "1688":
            await page.wait_for_load_state("networkidle", timeout=SCRAPE_TIMEOUT_MS)
    except Exception:
        timeout = FAST_BLOCK_TIMEOUT_MS if platform == "1688" else SCRAPE_TIMEOUT_MS
        await page.goto(url, wait_until="load", timeout=timeout)
        if platform != "1688":
            await page.wait_for_timeout(1200)


async def _looks_like_1688_blocked(page) -> bool:
    try:
        final_url = (page.url or "").lower()
        title_text = (await page.title() or "").lower()
        html = (await page.content() or "").lower()
    except Exception:
        return True
    return (
        "_____tmd_____" in final_url
        or "x5secdata=" in final_url
        or "\"action\":\"captcha\"" in html
        or "captcha" in title_text
        or "rgv587_flag:sm" in html
    )


async def _human_delay() -> None:
    await asyncio.sleep(random.uniform(1.0, 3.0))


async def _apply_stealth(page) -> None:
    await page.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        window.chrome = { runtime: {} };
        """
    )


def _parse_schema_payload(payload: object) -> dict:
    result = {
        "title": "",
        "price_text": "",
        "rating_text": "",
        "review_count_text": "",
    }

    def visit(item: object) -> None:
        if isinstance(item, list):
            for child in item:
                visit(child)
            return
        if not isinstance(item, dict):
            return
        item_type = str(item.get("@type", "")).lower()
        if "product" in item_type:
            result["title"] = result["title"] or str(item.get("name") or "")
            offers = item.get("offers")
            if isinstance(offers, dict):
                price = offers.get("price")
                currency = offers.get("priceCurrency")
                if price:
                    result["price_text"] = _normalize_currency_text(f"{currency or '$'} {price}")
            aggregate = item.get("aggregateRating")
            if isinstance(aggregate, dict):
                result["rating_text"] = _normalize_rating_value(str(aggregate.get("ratingValue") or ""))
                result["review_count_text"] = _normalize_review_count(
                    str(aggregate.get("reviewCount") or aggregate.get("ratingCount") or "")
                )
        if "@graph" in item:
            visit(item["@graph"])

    visit(payload)
    return result


def _clean_title(value: str) -> str:
    return " ".join(value.split()).strip()


def _normalize_currency_text(value: str | None) -> str:
    text = " ".join((value or "").split()).strip()
    if not text:
        return ""
    for pattern in [
        r"([$€£]\s?\d[\d,]*(?:\.\d{1,2})?)",
        r"(\d[\d,]*(?:\.\d{1,2})?\s?(?:USD|EUR|GBP))",
    ]:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _normalize_rating_value(value: str | None) -> str:
    text = " ".join((value or "").split()).strip()
    if not text:
        return ""
    match = re.search(r"(\d(?:\.\d+)?)", text)
    if not match:
        return ""
    rating = float(match.group(1))
    if 0 <= rating <= 5:
        return f"{rating:.1f}".rstrip("0").rstrip(".")
    return ""


def _normalize_review_count(value: str | None) -> str:
    text = " ".join((value or "").split()).strip()
    if not text:
        return ""
    match = re.search(r"([\d,]+)", text)
    return match.group(1) if match else ""
