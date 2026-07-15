from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.runtime import AppError, log_info
from app.models.product import Product
from app.repositories.analysis import analysis_repository
from app.repositories.crawl_run import crawl_run_repository
from app.repositories.platform import platform_repository
from app.repositories.product import product_repository
from app.schemas.product import AnalyzeRequest, AnalyzeResult, CrawlResult, ProductIntelligenceResult
from app.services.ai import analyze_title_with_ai
from app.services.crawler import build_source_links, crawl_product, detect_platform, to_crawl_result
from app.services.product_extractor import extract_public_product_page
from app.services.product_intelligence import analyze_product_intelligence
from app.services.task_status import task_status_service


class ProductService:
    async def crawl_and_save(self, db: Session, url: str, user_id: int, workspace_id: int | None = None) -> CrawlResult:
        await task_status_service.update("crawl", "pending", "采集任务已创建", {"url": url})
        await task_status_service.update("crawl", "running", "正在采集商品页面", {"url": url})
        platform_code = detect_platform(url)
        platform = platform_repository.get_by_code(db, platform_code)
        if not platform:
            await task_status_service.update("crawl", "error", "当前平台暂不支持", {"url": url}, "unsupported_platform")
            raise AppError("UNSUPPORTED_PLATFORM", "暂不支持这个平台", "scrape", 400)

        try:
            preview = await crawl_product(url)
        except Exception as exc:
            await task_status_service.update("crawl", "error", "采集失败", {"url": url}, str(exc))
            crawl_run_repository.create(
                db,
                product_id=None,
                platform_id=platform.id,
                request_url=url,
                status="failed",
                http_status=None,
                error_message=str(exc),
                raw_payload=None,
            )
            log_info(f"SCRAPE_FAIL | url={url} | platform={platform_code} | error={exc}")
            if isinstance(exc, AppError):
                raise exc
            raise AppError("REAL_SCRAPE_FAILED", f"采集失败：{exc}", "scrape", 500) from exc

        product = product_repository.get_by_source_url(db, preview.source_url, workspace_id=workspace_id)
        if product:
            product.title = preview.title
            product.current_price = preview.price
            product.original_price = preview.original_price
            product.currency_code = preview.currency
            product.review_count = preview.review_count or 0
            product.rating = preview.rating
            product.last_crawled_at = datetime.now(UTC)
            product_repository.save(db, product)
        else:
            try:
                product = product_repository.create(
                    db,
                    platform_id=platform.id,
                    created_by_user_id=user_id,
                    workspace_id=workspace_id,
                    source_url=preview.source_url,
                    title=preview.title,
                    current_price=preview.price,
                    original_price=preview.original_price,
                    currency_code=preview.currency,
                    review_count=preview.review_count or 0,
                    rating=preview.rating,
                    description_text=None,
                    last_crawled_at=datetime.now(UTC),
                )
            except Exception as exc:
                raise AppError("DB_WRITE_FAILED", f"保存商品失败：{exc}", "db", 500) from exc

        product_repository.replace_images(db, product, preview.image_urls)
        crawl_run_repository.create(
            db,
            product_id=product.id,
            platform_id=platform.id,
            request_url=url,
            status="success",
            http_status=200,
            error_message=None,
            raw_payload=preview.model_dump(),
        )
        result = to_crawl_result(preview)
        result.product_id = product.id
        await task_status_service.update("crawl", "success", "采集完成", {"url": url, "product_id": product.id})
        return result

    def analyze_product(
        self,
        db: Session,
        payload: AnalyzeRequest,
        user_id: int | None,
        *,
        workspace_id: int | None = None,
    ) -> tuple[Product, AnalyzeResult, ProductIntelligenceResult]:
        product = None
        if payload.product_id is not None:
            product = product_repository.get_by_id(db, payload.product_id, workspace_id=workspace_id)
        elif payload.title:
            shopify_platform = platform_repository.get_by_code(db, "shopify")
            if not shopify_platform:
                raise AppError("PLATFORM_INIT_FAILED", "平台初始化不完整", "db", 500)
            existing_product = product_repository.get_by_source_url(db, f"manual://{workspace_id or 0}/{payload.title}", workspace_id=workspace_id)
            if existing_product:
                product = existing_product
            else:
                try:
                    product = product_repository.create(
                        db,
                        platform_id=shopify_platform.id,
                        created_by_user_id=user_id,
                        workspace_id=workspace_id,
                        source_url=f"manual://{workspace_id or 0}/{payload.title}",
                        title=payload.title,
                        review_count=0,
                    )
                except Exception as exc:
                    raise AppError("DB_WRITE_FAILED", f"创建待分析商品失败：{exc}", "db", 500) from exc

        if not product:
            raise AppError("PRODUCT_NOT_FOUND", "没找到这个商品", "db", 404)

        ai_result = analyze_title_with_ai(db, product.title, workspace_id=workspace_id)
        product.title_zh = ai_result.get("title_zh")
        try:
            product_repository.save(db, product)
        except Exception as exc:
            raise AppError("DB_WRITE_FAILED", f"保存 AI 标题失败：{exc}", "db", 500) from exc

        try:
            analysis = analysis_repository.create(
                db,
                product_id=product.id,
                model_name=ai_result.get("model_name") or settings.openai_model,
                prompt_version="v1",
                title_zh=ai_result.get("title_zh"),
                core_keywords=ai_result.get("core_keywords") or [],
                selling_points=ai_result.get("selling_points") or [],
                sourcing_keywords=ai_result.get("sourcing_keywords") or [],
                raw_response=ai_result,
            )
        except Exception as exc:
            raise AppError("DB_WRITE_FAILED", f"保存 AI 分析结果失败：{exc}", "db", 500) from exc

        grouped_keywords = {
            "core_keyword": ai_result.get("core_keywords") or [],
            "selling_point": ai_result.get("selling_points") or [],
            "sourcing_keyword": ai_result.get("sourcing_keywords") or [],
        }
        try:
            product_repository.replace_keywords(db, product, analysis.id, grouped_keywords)
        except Exception as exc:
            raise AppError("DB_WRITE_FAILED", f"保存关键词失败：{exc}", "db", 500) from exc

        sourcing_keyword = (ai_result.get("sourcing_keywords") or [product.title_zh or product.title])[0]
        link_map = build_source_links(sourcing_keyword)
        platform_1688 = platform_repository.get_by_code(db, "1688")
        platform_pdd = platform_repository.get_by_code(db, "pdd")
        links = []
        if platform_1688:
            links.append(
                {
                    "source_platform_id": platform_1688.id,
                    "keyword_text": sourcing_keyword,
                    "search_url": link_map["1688_url"],
                }
            )
        if platform_pdd:
            links.append(
                {
                    "source_platform_id": platform_pdd.id,
                    "keyword_text": sourcing_keyword,
                    "search_url": link_map["pdd_url"],
                }
            )
        try:
            product_repository.replace_sourcing_links(db, product, analysis.id, links)
        except Exception as exc:
            raise AppError("DB_WRITE_FAILED", f"保存采购链接失败：{exc}", "db", 500) from exc

        refreshed_product = product_repository.get_by_id(db, product.id)
        analysis_result = AnalyzeResult(
            title_zh=ai_result.get("title_zh") or "",
            core_keywords=ai_result.get("core_keywords") or [],
            selling_points=ai_result.get("selling_points") or [],
            sourcing_keywords=ai_result.get("sourcing_keywords") or [],
            source_links={
                "1688_url": link_map["1688_url"],
                "pdd_url": link_map["pdd_url"],
            },
        )
        intelligence_payload = analyze_product_intelligence(
            db,
            title=refreshed_product.title,
            price=refreshed_product.current_price,
            images=[image.image_url for image in refreshed_product.images],
            rating=refreshed_product.rating,
            review_count=refreshed_product.review_count,
            source_url=refreshed_product.source_url,
            workspace_id=workspace_id,
        )
        intelligence_result = ProductIntelligenceResult(**intelligence_payload)
        log_info(f"ANALYZE_OK | product_id={product.id} | title={product.title} | sourcing_keyword={sourcing_keyword}")
        refreshed_product = product_repository.get_by_id(db, product.id, workspace_id=workspace_id) or refreshed_product
        return refreshed_product, analysis_result, intelligence_result

    async def analyze_full(
        self,
        db: Session,
        url: str,
        user_id: int | None,
        lang: str = "zh",
        *,
        workspace_id: int | None = None,
    ) -> dict:
        await task_status_service.update("analyze", "pending", "分析任务已创建", {"url": url, "lang": lang})
        try:
            await task_status_service.update("analyze", "running", "正在抓页面并准备分析", {"url": url, "lang": lang})
            extracted = await extract_public_product_page(url)
            if extracted.get("status") == "BLOCKED":
                await task_status_service.update(
                    "analyze",
                    "blocked",
                    "页面被拦住了，不能直接分析",
                    {"url": url},
                    "captcha_or_login_or_invalid_page",
                )
                return {
                    "status": "BLOCKED",
                    "lang": lang,
                    "message": "这个页面现在不适合直接分析，可能是登录页、验证码页，或者不是有效商品页。"
                    if lang == "zh"
                    else "This page cannot be analyzed right now. It may be a login page, captcha page, or invalid product page.",
                }

            title = extracted.get("title") or ""
            if not title:
                await task_status_service.update("analyze", "error", "没有拿到商品标题", {"url": url}, "missing_title")
                raise AppError("REAL_SCRAPE_FAILED", "没有拿到商品标题，暂时无法分析", "scrape", 500)

            try:
                product, analysis_result, intelligence_result = self.analyze_product(
                    db,
                    AnalyzeRequest(title=title),
                    user_id,
                    workspace_id=workspace_id,
                )
                result = {
                    "status": "OK",
                    "lang": lang,
                    "platform": extracted.get("platform") or "shopify",
                    "title": extracted.get("title") or "",
                    "title_zh": analysis_result.title_zh,
                    "price": extracted.get("price") or "",
                    "image": (extracted.get("images") or [""])[0],
                    "score": intelligence_result.product_score,
                    "product_score": intelligence_result.product_score,
                    "recommendation": self._translate_recommendation(intelligence_result.recommendation, lang),
                    "recommendation_key": intelligence_result.recommendation,
                    "profit_estimate": intelligence_result.profit_estimate,
                    "competition_level": self._translate_competition(intelligence_result.competition_level, lang),
                    "competition_level_key": intelligence_result.competition_level,
                    "source_links": analysis_result.source_links,
                    "core_keywords": analysis_result.core_keywords,
                    "selling_points": analysis_result.selling_points,
                    "reason": self._translate_reason_list(intelligence_result.reason, lang),
                    "fallback_score": None,
                    "ai_unavailable": False,
                }
            except AppError as exc:
                if exc.stage != "ai":
                    raise
                log_info(f"ANALYZE_FALLBACK | url={url} | title={title}")
                result = self._build_ai_fallback_result(extracted, lang)

            await task_status_service.update(
                "analyze",
                "success",
                "分析完成",
                {
                    "url": url,
                    "title": extracted.get("title") or "",
                    "score": result.get("product_score"),
                    "status": result.get("status"),
                },
            )
            return result
        except AppError as exc:
            await task_status_service.update(
                "analyze",
                "error",
                "分析失败",
                {"url": url, "stage": exc.stage},
                exc.message,
            )
            raise
        except Exception as exc:
            await task_status_service.update(
                "analyze",
                "error",
                "分析失败",
                {"url": url},
                str(exc),
            )
            raise

    def list_products(self, db: Session, search: str | None, skip: int, limit: int, workspace_id: int | None = None):
        return product_repository.list(db, search, skip, limit, workspace_id=workspace_id)

    def get_product(self, db: Session, product_id: int, workspace_id: int | None = None):
        return product_repository.get_by_id(db, product_id, workspace_id=workspace_id)

    def delete_product(self, db: Session, product_id: int, workspace_id: int | None = None) -> bool:
        product = product_repository.get_by_id(db, product_id, workspace_id=workspace_id)
        if not product:
            return False
        product_repository.delete(db, product)
        return True

    def batch_delete_products(self, db: Session, product_ids: list[int], workspace_id: int | None = None) -> list[int]:
        existing_products = []
        for product_id in product_ids:
            product = product_repository.get_by_id(db, product_id, workspace_id=workspace_id)
            if product:
                existing_products.append(product)
        if not existing_products:
            return []
        return product_repository.delete_many(db, existing_products)

    def _translate_recommendation(self, value: str, lang: str) -> str:
        if lang == "en":
            mapping = {
                "sell": "🔥 Good to sell",
                "monitor": "⚠️ Monitor",
                "ignore": "❌ Avoid",
            }
        else:
            mapping = {
                "sell": "🔥 推荐销售",
                "monitor": "⚠️ 继续观察",
                "ignore": "❌ 暂不建议",
            }
        return mapping.get(value, value)

    def _build_ai_fallback_result(self, extracted: dict, lang: str) -> dict:
        title = extracted.get("title") or ""
        price = extracted.get("price") or ""
        review_count = extracted.get("review_count") or ""
        recommendation_key, score, competition_key, reasons = self._pick_rule_based_recommendation(
            price=price,
            review_count=review_count,
            lang=lang,
        )

        return {
            "status": "FALLBACK",
            "lang": lang,
            "platform": extracted.get("platform") or "shopify",
            "title": title,
            "title_zh": title,
            "price": price,
            "image": (extracted.get("images") or [""])[0],
            "score": score,
            "product_score": score,
            "recommendation": "AI暂不可用，基于规则模型输出结果" if lang == "zh" else "AI unavailable, using rule-based result",
            "recommendation_key": recommendation_key,
            "profit_estimate": self._rule_based_profit_text(price, lang),
            "competition_level": self._translate_competition(competition_key, lang),
            "competition_level_key": competition_key,
            "source_links": build_source_links(title or extracted.get("url") or ""),
            "core_keywords": [title] if title else [],
            "selling_points": [extracted.get("availability")] if extracted.get("availability") else [],
            "reason": reasons,
            "fallback_score": score,
            "ai_unavailable": True,
        }

    def _pick_rule_based_recommendation(self, price: str, review_count: str, lang: str) -> tuple[str, int, str, list[str]]:
        price_number = self._parse_number(price)
        review_number = int(self._parse_number(review_count))

        if review_number >= 500:
            return (
                "monitor",
                46,
                "high",
                [
                    "AI 暂不可用，先按公开规则给出保守建议" if lang == "zh" else "AI is unavailable, so a conservative rule-based suggestion is shown",
                    "页面已经成功采集到公开商品信息" if lang == "zh" else "The system extracted public product data successfully",
                    "评论量偏高，说明竞争可能较强" if lang == "zh" else "High review volume suggests stronger competition",
                ],
            )

        if price_number >= 20:
            return (
                "sell",
                72,
                "medium",
                [
                    "AI 暂不可用，当前结果来自规则模型" if lang == "zh" else "AI is unavailable, so this result comes from a rule model",
                    "页面已经成功采集到标题、价格等公开信息" if lang == "zh" else "The system extracted title, price, and other public fields successfully",
                    "售价不低，通常更容易留出利润空间" if lang == "zh" else "The public selling price leaves more room for margin",
                ],
            )

        return (
            "monitor",
            58,
            "medium",
            [
                "AI 暂不可用，当前结果来自规则模型" if lang == "zh" else "AI is unavailable, so this result comes from a rule model",
                "页面已经成功采集到公开商品信息" if lang == "zh" else "The system extracted public product data successfully",
                "建议先核算拿货成本和运费再决定" if lang == "zh" else "Check sourcing cost and shipping before making a decision",
            ],
        )

    def _rule_based_profit_text(self, price: str, lang: str) -> str:
        price_number = self._parse_number(price)
        if lang == "en":
            if price_number >= 20:
                return "AI is unavailable. Based on the public price, this product may still have workable margin room."
            return "AI is unavailable. Please compare public price, sourcing cost, and shipping before deciding."
        if price_number >= 20:
            return "AI 暂不可用。按公开售价看，这个商品仍可能留出一定利润空间。"
        return "AI 暂不可用。建议先对比公开售价、拿货成本和运费，再决定是否继续。"

    def _parse_number(self, value: str | None) -> float:
        import re

        text = str(value or "").replace(",", "")
        match = re.search(r"(\d+(?:\.\d+)?)", text)
        if not match:
            return 0.0
        return float(match.group(1))

    def _translate_competition(self, value: str, lang: str) -> str:
        if lang == "en":
            mapping = {
                "low": "Low competition",
                "medium": "Medium competition",
                "high": "High competition",
            }
        else:
            mapping = {
                "low": "低竞争",
                "medium": "中竞争",
                "high": "高竞争",
            }
        return mapping.get(value, value)

    def _translate_reason_list(self, items: list[str], lang: str) -> list[str]:
        if lang == "zh":
            return items
        translated: list[str] = []
        for item in items:
            translated.append(
                item.replace("利润潜力", "Profit potential")
                .replace("竞争强度", "Competition")
                .replace("评论量", "Review volume")
                .replace("适合", "Suitable")
            )
        return translated


product_service = ProductService()
