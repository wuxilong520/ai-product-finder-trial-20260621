from __future__ import annotations


class ConsumerInterestEngine:
    def score(
        self,
        *,
        search_signal: float,
        content_signal: float,
        discussion_signal: float,
        commerce_signal: float,
    ) -> float:
        return round(
            max(
                0.0,
                min(
                    100.0,
                    float(search_signal or 0) * 0.35
                    + float(content_signal or 0) * 0.25
                    + float(discussion_signal or 0) * 0.2
                    + float(commerce_signal or 0) * 0.2,
                ),
            ),
            2,
        )


consumer_interest_engine = ConsumerInterestEngine()
