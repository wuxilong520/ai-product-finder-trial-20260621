from __future__ import annotations


class DataTrustEngine:
    SCORE_MAP = {
        'real': 1.0,
        'partial': 0.5,
        'mock': 0.0,
        'inconsistent': -1.0,
    }

    def score(self, *, data_source_type: str, inconsistent: bool = False) -> float:
        if inconsistent:
            return -1.0
        return float(self.SCORE_MAP.get(str(data_source_type), 0.0))


data_trust_engine = DataTrustEngine()
