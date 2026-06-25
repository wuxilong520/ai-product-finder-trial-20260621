from __future__ import annotations


class ProfitRealEngine:
    def calculate(self, *, selling_price: float, total_cost: float) -> dict:
        profit = round(selling_price - total_cost, 2)
        profit_margin = round((profit / selling_price) if selling_price > 0 else 0.0, 4)
        break_even_price = round(total_cost, 2)
        return {
            "profit": profit,
            "profit_margin": profit_margin,
            "break_even_price": break_even_price,
        }


profit_real_engine = ProfitRealEngine()
