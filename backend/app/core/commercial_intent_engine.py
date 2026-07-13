from __future__ import annotations

from statistics import mean


class CommercialIntentEngine:
    BUY_TERMS = {
        "buy",
        "best",
        "price",
        "deal",
        "for sale",
        "supplier",
        "wholesale",
        "review",
        "vs",
    }

    LOW_INTENT_TERMS = {
        "news",
        "movie",
        "lyrics",
        "meaning",
        "meme",
        "entertainment",
    }

    def score(
        self,
        *,
        keyword: str,
        keyword_intent_score: float,
        commerce_signal: float,
        search_signal: float,
        discussion_signal: float,
        content_signal: float,
        reality_sources: list[dict] | None = None,
    ) -> float:
        lowered = str(keyword or "").strip().lower()
        score = float(keyword_intent_score or 45)

        if any(term in lowered for term in self.BUY_TERMS):
            score += 12
        if any(term in lowered for term in self.LOW_INTENT_TERMS):
            score -= 20

        if float(commerce_signal or 0) >= 70:
            score += 18
        elif float(commerce_signal or 0) >= 50:
            score += 10

        if float(search_signal or 0) >= 70:
            score += 8
        if float(discussion_signal or 0) >= 55:
            score += 6
        if float(content_signal or 0) >= 55:
            score += 4

        if reality_sources:
            commerce_reliability = [
                float(item.get("reliability") or 0)
                for item in reality_sources
                if str(item.get("source") or "") in {"amazon", "walmart", "ebay", "shopify"}
                and str(item.get("status") or "") in {"real", "limited"}
            ]
            if commerce_reliability:
                score += mean(commerce_reliability) * 12

        return round(max(0.0, min(100.0, score)), 2)


commercial_intent_engine = CommercialIntentEngine()
