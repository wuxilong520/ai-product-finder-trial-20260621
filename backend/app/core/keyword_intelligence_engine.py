from __future__ import annotations


class KeywordIntelligenceEngine:
    def analyze(
        self,
        *,
        keyword: str,
        related_keywords: list[str] | None = None,
        rising_keywords: list[str] | None = None,
    ) -> dict:
        normalized_keyword = str(keyword or "").strip()
        related = [str(item).strip() for item in (related_keywords or []) if str(item).strip()]
        rising = [str(item).strip() for item in (rising_keywords or []) if str(item).strip()]
        long_tail = self._build_long_tail(normalized_keyword, related, rising)
        buyer_intent = self._buyer_intent(normalized_keyword)
        commercial_intent = self._commercial_intent_score(normalized_keyword, long_tail)
        return {
            "main_keyword": normalized_keyword,
            "related_keywords": related[:10],
            "long_tail_keywords": long_tail[:10],
            "buyer_intent": buyer_intent,
            "commercial_intent": commercial_intent,
        }

    def _build_long_tail(self, keyword: str, related: list[str], rising: list[str]) -> list[str]:
        long_tail = []
        seeds = [
            f"best {keyword}",
            f"{keyword} for shopify",
            f"{keyword} wholesale supplier",
            f"buy {keyword} online",
            f"low competition {keyword}",
        ]
        for item in [*related, *rising, *seeds]:
            normalized = str(item).strip()
            if normalized and normalized not in long_tail:
                long_tail.append(normalized)
        return long_tail

    def _buyer_intent(self, keyword: str) -> str:
        lowered = keyword.lower()
        transactional_terms = ["buy", "wholesale", "supplier", "price", "shop", "for sale"]
        informational_terms = ["what", "how", "review", "vs", "guide", "meaning"]
        if any(term in lowered for term in transactional_terms):
            return "transactional"
        if any(term in lowered for term in informational_terms):
            return "informational"
        return "commercial"

    def _commercial_intent_score(self, keyword: str, long_tail: list[str]) -> float:
        lowered = keyword.lower()
        score = 45.0
        if any(term in lowered for term in ["buy", "wholesale", "supplier", "price"]):
            score += 25
        if any("best" in item.lower() or "for " in item.lower() for item in long_tail):
            score += 15
        if any(term in lowered for term in ["review", "guide", "what", "how"]):
            score -= 15
        return round(max(0.0, min(100.0, score)), 2)


keyword_intelligence_engine = KeywordIntelligenceEngine()
