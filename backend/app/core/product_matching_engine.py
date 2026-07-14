from __future__ import annotations

import re
from difflib import SequenceMatcher


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", " ", str(value or "").lower())).strip()


def _tokenize(value: str) -> set[str]:
    text = _normalize_text(value)
    return {token for token in text.split(" ") if token}


class ProductMatchingEngine:
    def match(
        self,
        *,
        title_a: str,
        title_b: str,
        keyword_a: str | None = None,
        keyword_b: str | None = None,
        image_a: str | None = None,
        image_b: str | None = None,
        specs_a: list[str] | None = None,
        specs_b: list[str] | None = None,
    ) -> dict:
        norm_a = _normalize_text(title_a)
        norm_b = _normalize_text(title_b)
        title_score = SequenceMatcher(None, norm_a, norm_b).ratio() * 100

        tokens_a = _tokenize(title_a) | _tokenize(keyword_a or "")
        tokens_b = _tokenize(title_b) | _tokenize(keyword_b or "")
        token_overlap = len(tokens_a & tokens_b) / max(1, len(tokens_a | tokens_b))
        token_score = token_overlap * 100

        spec_tokens_a = set()
        spec_tokens_b = set()
        for item in specs_a or []:
            spec_tokens_a |= _tokenize(item)
        for item in specs_b or []:
            spec_tokens_b |= _tokenize(item)
        spec_score = (len(spec_tokens_a & spec_tokens_b) / max(1, len(spec_tokens_a | spec_tokens_b))) * 100 if (spec_tokens_a or spec_tokens_b) else 0

        image_score = 0.0
        if image_a and image_b:
            if image_a == image_b:
                image_score = 100.0
            elif image_a.split("?")[0].split("/")[-1] == image_b.split("?")[0].split("/")[-1]:
                image_score = 80.0

        similarity_score = round(
            min(
                100.0,
                title_score * 0.45 + token_score * 0.35 + spec_score * 0.1 + image_score * 0.1,
            ),
            2,
        )
        same_product_group = similarity_score >= 78
        return {
            "similarity_score": similarity_score,
            "same_product_group": same_product_group,
            "title_score": round(title_score, 2),
            "token_score": round(token_score, 2),
            "spec_score": round(spec_score, 2),
            "image_score": round(image_score, 2),
        }


product_matching_engine = ProductMatchingEngine()
