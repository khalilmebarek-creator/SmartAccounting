# تحليل التعادل
# ===============

from utils.app_logger import get_logger

log = get_logger("breakeven")


class BreakEvenAnalyzer:
    """تحليل نقطة التعادل — هامش المساهمة وحد الأمان"""

    def __init__(self, financial_data=None):
        self.data = financial_data or {}

    def calculate(self, fixed_costs=None, variable_cost_ratio=None, unit_price=None, unit_variable_cost=None):
        """
        حساب نقطة التعادل
        يمكن الإدخال بشكل مختصر (fixed_costs + variable_cost_ratio + revenue)
        أو بشكل تفصيلي (unit_price + unit_variable_cost + fixed_costs)
        """
        revenue = self.data.get("revenue", 0)
        cogs = self.data.get("cost_of_goods_sold", 0)
        net_income = self.data.get("net_income", 0)
        gross_profit = self.data.get("gross_profit", 0)

        if fixed_costs is None:
            fixed_costs = max(gross_profit - net_income, 0) if gross_profit else revenue * 0.3
        
        if variable_cost_ratio is None:
            variable_cost_ratio = cogs / revenue if revenue else 0.6

        contribution_margin_ratio = 1 - variable_cost_ratio

        if contribution_margin_ratio <= 0:
            return {"error": "negative_contribution_margin"}

        breakeven_revenue = fixed_costs / contribution_margin_ratio
        margin_of_safety = revenue - breakeven_revenue
        margin_of_safety_pct = (margin_of_safety / revenue * 100) if revenue else 0
        operating_leverage = (revenue - cogs) / net_income if net_income else 0

        result = {
            "fixed_costs": round(fixed_costs, 2),
            "variable_cost_ratio": round(variable_cost_ratio * 100, 2),
            "contribution_margin_ratio": round(contribution_margin_ratio * 100, 2),
            "breakeven_revenue": round(breakeven_revenue, 2),
            "current_revenue": round(revenue, 2),
            "margin_of_safety": round(margin_of_safety, 2),
            "margin_of_safety_pct": round(margin_of_safety_pct, 2),
            "operating_leverage": round(operating_leverage, 2),
            "is_profitable": revenue > breakeven_revenue,
        }

        if unit_price and unit_variable_cost:
            unit_contribution = unit_price - unit_variable_cost
            if unit_contribution > 0:
                breakeven_units = fixed_costs / unit_contribution
                result["unit_price"] = unit_price
                result["unit_variable_cost"] = unit_variable_cost
                result["unit_contribution"] = round(unit_contribution, 2)
                result["breakeven_units"] = round(breakeven_units, 0)

        return result

    def sensitivity_analysis(self, fixed_costs, variable_cost_ratio_range, base_revenue):
        """تحليل الحساسية — تأثير تغير النسبة المتغيرة على نقطة التعادل"""
        results = []
        for vc_ratio in variable_cost_ratio_range:
            cm_ratio = 1 - vc_ratio
            if cm_ratio <= 0:
                results.append({"vc_ratio": vc_ratio, "breakeven": float('inf')})
                continue
            be = fixed_costs / cm_ratio
            margin = base_revenue - be
            results.append({
                "variable_cost_pct": round(vc_ratio * 100, 2),
                "contribution_margin_pct": round(cm_ratio * 100, 2),
                "breakeven_revenue": round(be, 2),
                "margin_of_safety": round(margin, 2),
                "margin_of_safety_pct": round(margin / base_revenue * 100, 2) if base_revenue else 0,
            })
        return results
