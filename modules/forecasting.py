# التنبؤ المالي
# =============

from utils.app_logger import get_logger

log = get_logger("forecasting")


class FinancialForecaster:
    """محرك التنبؤ المالي — نمذجة النمو وتوقع الأرباح"""

    def __init__(self, financial_data, ratios):
        self.data = financial_data
        self.ratios = ratios

    def project_revenue(self, growth_rates):
        """
        توقع الإيرادات لسنوات قادمة
        growth_rates: قائمة نسب النمو لكل سنة (مثلاً [0.1, 0.08, 0.05])
        """
        base_revenue = self.data.get("revenue", 0)
        if base_revenue <= 0:
            return {"error": "revenue_zero"}
        
        projections = []
        current = base_revenue
        for i, rate in enumerate(growth_rates):
            current = current * (1 + rate)
            projections.append({
                "year_offset": i + 1,
                "growth_rate": rate,
                "projected_revenue": round(current, 2)
            })
        return {
            "base_revenue": base_revenue,
            "projections": projections
        }

    def project_income_statement(self, growth_rates, cogs_pct=None, opex_pct=None):
        """توقع قائمة الدخل لسنوات قادمة"""
        rev_result = self.project_revenue(growth_rates)
        if "error" in rev_result:
            return rev_result
        
        if cogs_pct is None:
            rev = self.data.get("revenue", 1) or 1
            cogs_pct = self.data.get("cost_of_goods_sold", 0) / rev
        if opex_pct is None:
            rev = self.data.get("revenue", 1) or 1
            gross = self.data.get("gross_profit", 0)
            net = self.data.get("net_income", 0)
            opex_pct = max(gross - net, 0) / rev

        projections = []
        for p in rev_result["projections"]:
            proj_rev = p["projected_revenue"]
            proj_cogs = proj_rev * cogs_pct
            proj_gross = proj_rev - proj_cogs
            proj_opex = proj_rev * opex_pct
            proj_net = proj_gross - proj_opex
            projections.append({
                "year_offset": p["year_offset"],
                "revenue": round(proj_rev, 2),
                "cogs": round(proj_cogs, 2),
                "gross_profit": round(proj_gross, 2),
                "opex": round(proj_opex, 2),
                "net_income": round(proj_net, 2),
                "npm": round(proj_net / proj_rev * 100, 2) if proj_rev else 0
            })
        return projections

    def scenario_analysis(self, scenarios):
        """تحليل سيناريوهات (متفائل / معتدل / متشائم)"""
        results = {}
        for name, rate in scenarios.items():
            rev_result = self.project_revenue([rate])
            if "error" in rev_result:
                results[name] = {"error": "revenue_zero"}
                continue
            proj = rev_result["projections"][0]
            base_rev = self.data.get("revenue", 0)
            base_net = self.data.get("net_income", 0)
            npm = (base_net / base_rev * 100) if base_rev else 0
            proj_net = proj["projected_revenue"] * npm / 100
            results[name] = {
                "growth_rate": rate,
                "projected_revenue": proj["projected_revenue"],
                "projected_net_income": round(proj_net, 2),
                "revenue_change": round(proj["projected_revenue"] - base_rev, 2)
            }
        return results

    def cagr(self, beginning_value, ending_value, years):
        """حساب معدل النمو السنوي المركب"""
        if beginning_value <= 0 or ending_value <= 0 or years <= 0:
            return 0
        return round(((ending_value / beginning_value) ** (1 / years) - 1) * 100, 2)
