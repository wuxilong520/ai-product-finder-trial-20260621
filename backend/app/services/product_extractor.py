from __future__ import annotations

from dataclasses import dataclass
import json
import re
from urllib.parse import urlparse

from app.core.runtime import log_error, log_info


BLOCKED_REASON = "captcha_or_login_or_invalid_page"


@dataclass
class ExtractorResult:
    status: str
    url: str | None = None
    platform: str | None = None
    title: str | None = None
    price: str | None = None
    rating: str | None = None
    review_count: str | None = None
    images: list[str] | None = None
    sales: str | None = None
    availability: str | None = None
    dom_parsed: bool = False
    entered_product_page: bool = False
    reason: str | None = None


def detect_public_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "1688.com" in host:
        return "1688"
    if "amazon." in host:
        return "amazon"
    if "aliexpress." in host:
        return "aliexpress"
    return "shopify"


async def extract_public_product_page(url: str) -> dict:
    try:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright.async_api import async_playwright
    except Exception as exc:
        log_error(f"PRODUCT_EXTRACTOR_IMPORT_FAIL | url={url} | error={exc}")
        raise RuntimeError("Playwright 不可用，当前无法进行公开商品页解析") from exc

    platform = detect_public_platform(url)
    log_info(f"PRODUCT_EXTRACT_START | url={url} | platform={platform}")

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            page = await browser.new_page()

            response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                log_info(f"PRODUCT_EXTRACT_NETWORKIDLE_TIMEOUT | url={url}")

            final_url = page.url
            html = await page.content()
            page_title = await page.title()

            blocked = _is_blocked_page(platform, final_url, page_title, html, response.status if response else None)
            if blocked:
                await browser.close()
                log_info(f"PRODUCT_EXTRACT_BLOCKED | url={url} | platform={platform}")
                return {
                    "status": "BLOCKED",
                    "reason": BLOCKED_REASON,
                }

            result = await _parse_platform_fields(page, platform, url, html)
            await browser.close()
            log_info(
                "PRODUCT_EXTRACT_OK | "
                f"url={url} | platform={platform} | title={result.get('title', '')[:80]}"
            )
            return result
    except Exception as exc:
        log_error(f"PRODUCT_EXTRACT_FAIL | url={url} | error={exc}")
        raise


def _is_blocked_page(platform: str, final_url: str, page_title: str, html: str, status_code: int | None) -> bool:
    title_text = (page_title or "").lower()
    html_text = (html or "").lower()
    final_url_text = (final_url or "").lower()

    if status_code == 404:
        return True
    if "404" in title_text or "404 not found" in html_text or "page not found" in html_text:
        return True

    if platform == "amazon":
        amazon_blockers = [
            "validatecaptcha",
            "opfcaptcha",
            "enter the characters you see below",
            "sorry, we just need to make sure you're not a robot",
        ]
        if any(marker in html_text for marker in amazon_blockers):
            return True
    if "captcha" in title_text or "captcha" in final_url_text:
        return True

    if "login" in final_url_text or "account/login" in final_url_text:
        return True

    strict_login_markers = [
        "form action=\"/account/login\"",
        "name=\"customer[email]\"",
        "type=\"password\"",
        "customer login",
        "please sign in to continue",
    ]
    if "sign in" in title_text and any(marker in html_text for marker in strict_login_markers):
        return True
    if any(marker in html_text for marker in strict_login_markers):
        return True

    return False


async def _parse_platform_fields(page, platform: str, url: str, html: str) -> dict:
    schema = _extract_product_schema(html)

    if platform == "amazon":
        title = await _get_first_text(page, ["#productTitle", "span#productTitle", "#title span", "h1 span"])
        price = await _get_first_text(
            page,
            [
                ".a-price .a-offscreen",
                "#corePrice_feature_div .a-offscreen",
                "#corePriceDisplay_desktop_feature_div .a-offscreen",
            ],
        )
        rating = await _get_first_text(page, ["#acrPopover span.a-size-base", "span.a-icon-alt", "[data-hook='rating-out-of-text']"])
        review_count = await _get_first_text(page, ["#acrCustomerReviewText", "span[data-hook='total-review-count']"])
        images = await _get_images(
            page,
            ["#landingImage", "#imgTagWrapperId img", "#altImages img", "img[data-old-hires]"],
        )
        availability = await _get_first_text(page, ["#availability span", "#outOfStock span"])
        sales = None
    elif platform == "aliexpress":
        title = await _get_first_text(page, ["h1", "[data-pl='product-title']", "meta[property='og:title']"])
        price = await _get_first_text(
            page,
            [
                ".price--currentPriceText--V8_y_b5",
                "[class*='price--currentPriceText']",
                ".product-price-current",
            ],
        )
        rating = await _get_first_text(page, [".overview--rating--19l0s_DB", "[class*='overview--rating']"])
        review_count = await _get_first_text(page, [".overview--评价人数--z_VfxE8y", "[class*='overview--reviews']"])
        images = await _get_images(page, ["img[src*='alicdn']", ".images-view-item img", "img[class*='magnifier--image']"])
        availability = await _get_first_text(page, ["[class*='availability']", "[class*='quantity--info']"])
        sales = await _get_first_text(page, ["[class*='trade']", "[class*='sold']", "[class*='orders']"])
    elif platform == "1688":
        final_url = page.url.lower()
        title_text = (await page.title() or "").lower()
        html_text = html.lower()
        if "_____tmd_____" in final_url or "x5secdata=" in final_url or "\"action\":\"captcha\"" in html_text or "captcha" in title_text:
            return {
                "status": "BLOCKED",
                "reason": BLOCKED_REASON,
            }

        title = await _get_first_text(page, ["h1", ".d-title", ".title-text", "[class*='title']"])
        price = await _get_first_text(page, [".price-now", ".price", "[class*='price']"])
        rating = ""
        review_count = ""
        images = await _get_images(page, ["img[src*='alicdn.com']", "img[data-src*='alicdn.com']", ".detail-gallery img"])
        availability = ""
        sales = ""
    else:
        title = await _get_first_text(page, ["h1", "[data-product-title]", "title"])
        price = await _get_first_text(
            page,
            [
                "[data-product-price]",
                "[data-testid='price']",
                "[data-product-blocks-price]",
                "product-info .price",
                "price-list .price",
                ".price-item--sale",
                ".price-item",
                ".product__price",
                "[class*='product-price']",
            ],
        )
        rating = await _get_first_text(page, ["[data-rating]", ".jdgm-prev-badge__stars", ".spr-starrating"])
        review_count = await _get_first_text(page, ["[data-review-count]", ".jdgm-prev-badge__text", ".spr-badge-caption", "[data-testid='review-count']"])
        images = await _get_images(page, ["img[src*='cdn.shopify.com']", ".product__media img", ".product-gallery img", "[data-product-media] img"])
        availability = await _get_first_text(page, ["[data-availability]", "[class*='stock']", "[class*='availability']", "button[name='add']"])
        sales = await _get_first_text(page, ["[class*='sold']", "[class*='sales']", "[data-sales]"])

    title = _pick_clean_text(title, schema.get("title"))
    price = _pick_clean_text(_normalize_price_text(price), _normalize_price_text(schema.get("price")))
    rating = _pick_clean_text(_normalize_rating_text(rating), _normalize_rating_text(schema.get("rating")))
    review_count = _pick_clean_text(_normalize_review_text(review_count), _normalize_review_text(schema.get("review_count")))
    availability = _pick_clean_text(_normalize_availability_text(availability), _normalize_availability_text(schema.get("availability")))

    if schema.get("images"):
        images = _merge_images(images, schema.get("images") or [])

    return {
        "status": "OK",
        "url": url,
        "platform": platform,
        "title": title or "",
        "price": price or "",
        "rating": rating or "",
        "review_count": review_count or "",
        "images": images,
        "sales": sales or None,
        "availability": availability or None,
        "dom_parsed": True,
        "entered_product_page": bool(title or price or images),
    }


def _extract_product_schema(html: str) -> dict:
    results = {
        "title": None,
        "price": None,
        "rating": None,
        "review_count": None,
        "availability": None,
        "images": [],
    }
    script_matches = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for raw in script_matches:
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue

        for item in _iter_schema_items(payload):
            item_type = str(item.get("@type", "")).lower()
            if "product" not in item_type:
                continue
            results["title"] = item.get("name") or results["title"]
            image_value = item.get("image")
            if isinstance(image_value, str):
                results["images"].append(image_value)
            elif isinstance(image_value, list):
                results["images"].extend([image for image in image_value if isinstance(image, str)])

            aggregate = item.get("aggregateRating") or {}
            if isinstance(aggregate, dict):
                results["rating"] = str(aggregate.get("ratingValue") or results["rating"] or "")
                results["review_count"] = str(
                    aggregate.get("reviewCount")
                    or aggregate.get("ratingCount")
                    or results["review_count"]
                    or ""
                )

            offers = item.get("offers")
            if isinstance(offers, dict):
                results["price"] = str(offers.get("price") or results["price"] or "")
                results["availability"] = str(offers.get("availability") or results["availability"] or "")
            elif isinstance(offers, list):
                for offer in offers:
                    if not isinstance(offer, dict):
                        continue
                    if not results["price"] and offer.get("price"):
                        results["price"] = str(offer.get("price"))
                    if not results["availability"] and offer.get("availability"):
                        results["availability"] = str(offer.get("availability"))

    results["images"] = _merge_images([], results["images"])
    return results


def _iter_schema_items(payload):
    if isinstance(payload, list):
        for item in payload:
            yield from _iter_schema_items(item)
        return
    if isinstance(payload, dict):
        if "@graph" in payload and isinstance(payload["@graph"], list):
            for item in payload["@graph"]:
                yield from _iter_schema_items(item)
        yield payload


def _pick_clean_text(primary: str | None, fallback: str | None) -> str:
    value = (primary or "").strip()
    if value:
        return value
    return (fallback or "").strip()


def _normalize_price_text(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    match = re.search(r"([$€£]\s?\d[\d,]*(?:\.\d{1,2})?|\d[\d,]*(?:\.\d{1,2})?\s?(?:usd|eur|gbp))", text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _normalize_rating_text(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    match = re.search(r"(\d(?:\.\d)?)", text)
    return match.group(1) if match else ""


def _normalize_review_text(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    match = re.search(r"([\d,]+)", text)
    return match.group(1) if match else ""


def _normalize_availability_text(value: str | None) -> str:
    text = " ".join((value or "").split()).strip()
    if not text:
        return ""
    if len(text) > 80:
        if "add to cart" in text.lower():
            return "Add to cart"
        return ""
    if text.startswith("http"):
        return text.rsplit("/", 1)[-1]
    return text


def _merge_images(current: list[str], extra: list[str]) -> list[str]:
    merged: list[str] = []
    for value in [*current, *extra]:
        if value and value not in merged:
            merged.append(value)
    return merged


async def _get_first_text(page, selectors: list[str]) -> str:
    for selector in selectors:
        if selector.startswith("meta["):
            locator = page.locator(selector)
            if await locator.count() > 0:
                value = await locator.first.get_attribute("content")
                if value and value.strip():
                    return value.strip()
            continue

        locator = page.locator(selector)
        try:
            await locator.first.wait_for(state="attached", timeout=2000)
        except Exception:
            pass
        if await locator.count() > 0:
            text = (await locator.first.text_content() or "").strip()
            if text:
                return text
    return ""


async def _get_images(page, selectors: list[str], limit: int = 20) -> list[str]:
    results: list[str] = []
    for selector in selectors:
        locator = page.locator(selector)
        try:
            await locator.first.wait_for(state="attached", timeout=2000)
        except Exception:
            pass
        count = await locator.count()
        if count == 0:
            continue

        for index in range(min(count, limit)):
            node = locator.nth(index)
            for attr in ("src", "data-src", "data-old-hires"):
                value = await node.get_attribute(attr)
                if value and value not in results:
                    results.append(value)
                    break
        if results:
            break
    return results
