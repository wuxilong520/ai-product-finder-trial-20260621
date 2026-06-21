from __future__ import annotations

import asyncio
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


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
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
                await _load_page(page, url)
                await _human_delay()

                if platform == "amazon":
                    data = await _parse_amazon(page, url)
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


async def _parse_shopify(page, url: str) -> CrawlPreview:
    title = await _get_first_text(page, ["h1", "[data-product-title]", "title"])
    price = await _get_first_text(
        page,
        [
            "[class*='price']",
            "[data-product-price]",
            ".price-item--sale",
            ".price-item",
            "[data-sale-price]",
        ],
    )
    rating = await _get_first_text(page, ["[data-rating]", ".jdgm-prev-badge__stars", ".spr-starrating", "[class*='rating']"])
    reviews = await _get_first_text(page, ["[data-review-count]", ".jdgm-prev-badge__text", ".spr-badge-caption", "[class*='review']"])
    images = await _get_images(page, ["img[src*='cdn.shopify.com']", ".product__media img", ".product-gallery img", "[data-product-media] img"])

    return CrawlPreview(
        source_platform="shopify",
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


async def _load_page(page, url: str) -> None:
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=SCRAPE_TIMEOUT_MS)
        await page.wait_for_load_state("networkidle", timeout=SCRAPE_TIMEOUT_MS)
    except Exception:
        await page.goto(url, wait_until="load", timeout=SCRAPE_TIMEOUT_MS)
        await page.wait_for_timeout(1200)


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
