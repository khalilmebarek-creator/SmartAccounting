# محرك تحليل السيناريوهات المالية
# =================================

import json
from utils.app_logger import get_logger

log = get_logger("scenarios")


class ScenarioAnalyzer:
    """محرك المحاكاة المالية — سيناريوهات مثالي/طبيعي/أسوأ حالة + حساسية"""

    DEFAULT_BEST = {
        "revenue_change_pct": 0.20,
        "cost_change_pct": -0.10,
        "efficiency_change_pct": 0.15,
    }
    DEFAULT_WORST = {
        "revenue_change_pct": -0.20,
        "cost_change_pct": 0.15,
        "efficiency_change_pct": -0.10,
    }
    SCENARIO_TYPES = ("best", "base", "worst")
    COMPARISON_METRICS = (
        "revenue", "cogs", "operating_expenses", "gross_profit",
        "net_income", "net_profit_margin", "asset_turnover", "roa", "roe",
    )
    SENSITIVITY_STEPS = (-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20)
    SENSITIVITY_VARIABLES = ("revenue", "cost", "efficiency")

    def __init__(self, financial_data, ratios):
        self.data = financial_data or {}
        self.ratios = ratios or {}

    # ===== أساسيات البيانات =====

    def _base_values(self):
        """استخراج القيم الأساسية من البيانات المالية"""
        rev = self.data.get("revenue", 0) or 0
        cogs = self.data.get("cost_of_goods_sold", 0) or 0
        opex = self.data.get("operating_expenses", 0) or 0
        gross = self.data.get("gross_profit", None)
        if gross is None:
            gross = rev - cogs
        operating = self.data.get("operating_income", None)
        if operating is None:
            operating = gross - opex
        other_income = self.data.get("other_income", 0) or 0
        other_expenses = self.data.get("other_expenses", 0) or 0
        net = self.data.get("net_income", None)
        if net is None:
            net = operating + other_income - other_expenses
        return {
            "revenue": rev, "cogs": cogs, "opex": opex, "gross": gross,
            "operating": operating, "other_income": other_income,
            "other_expenses": other_expenses, "net": net,
            "total_assets": self.data.get("total_assets", 0) or 0,
            "equity": self.data.get("equity", 0) or 0,
        }

    @staticmethod
    def _round2(value):
        return round(value, 2)

    @staticmethod
    def _round4(value):
        return round(value, 4)

    # ===== الإسقاط (projection) =====

    def _project(self, revenue_change_pct, cost_change_pct, efficiency_change_pct):
        """حساب السيناريو وفق معدلات التغيير المحددة"""
        base = self._base_values()
        r = revenue_change_pct
        c = cost_change_pct
        e = efficiency_change_pct

        revenue = base["revenue"] * (1 + r)
        cogs = base["cogs"] * (1 + r) * (1 - e) * (1 + c)
        opex = base["opex"] * (1 + r) * (1 - e) * (1 + c)
        other_income = base["other_income"] * (1 + r)
        other_expenses = base["other_expenses"] * (1 + r) * (1 + c)
        gross = revenue - cogs
        operating = gross - opex
        net = operating + other_income - other_expenses
        total_assets = base["total_assets"] * (1 - e)

        net_profit_margin = (net / revenue * 100) if revenue else 0
        asset_turnover = (revenue / total_assets) if total_assets else 0
        roa = (net / total_assets * 100) if total_assets else 0
        roe = (net / base["equity"] * 100) if base["equity"] else 0

        return {
            "assumptions": {
                "revenue_change_pct": round(r, 4),
                "cost_change_pct": round(c, 4),
                "efficiency_change_pct": round(e, 4),
            },
            "revenue": self._round2(revenue),
            "cogs": self._round2(cogs),
            "operating_expenses": self._round2(opex),
            "gross_profit": self._round2(gross),
            "operating_income": self._round2(operating),
            "other_income": self._round2(other_income),
            "other_expenses": self._round2(other_expenses),
            "net_income": self._round2(net),
            "total_assets": self._round2(total_assets),
            "equity": self._round2(base["equity"]),
            "net_profit_margin": round(net_profit_margin, 2),
            "asset_turnover": self._round4(asset_turnover),
            "roa": round(roa, 2),
            "roe": round(roe, 2),
        }

    def _base_snapshot(self):
        """الحالة الطبيعية — نسخة مطابقة من البيانات الحالية"""
        base = self._base_values()
        net_profit_margin = (base["net"] / base["revenue"] * 100) if base["revenue"] else 0
        asset_turnover = (base["revenue"] / base["total_assets"]) if base["total_assets"] else 0
        roa = (base["net"] / base["total_assets"] * 100) if base["total_assets"] else 0
        roe = (base["net"] / base["equity"] * 100) if base["equity"] else 0

        return {
            "assumptions": {
                "revenue_change_pct": 0.0,
                "cost_change_pct": 0.0,
                "efficiency_change_pct": 0.0,
            },
            "revenue": self._round2(base["revenue"]),
            "cogs": self._round2(base["cogs"]),
            "operating_expenses": self._round2(base["opex"]),
            "gross_profit": self._round2(base["gross"]),
            "operating_income": self._round2(base["operating"]),
            "other_income": self._round2(base["other_income"]),
            "other_expenses": self._round2(base["other_expenses"]),
            "net_income": self._round2(base["net"]),
            "total_assets": self._round2(base["total_assets"]),
            "equity": self._round2(base["equity"]),
            "net_profit_margin": round(net_profit_margin, 2),
            "asset_turnover": self._round4(asset_turnover),
            "roa": round(roa, 2),
            "roe": round(roe, 2),
            "outcome": "base",
        }

    @staticmethod
    def _outcome(net_income, base_net_income, scenario_type):
        if scenario_type == "base":
            return "base"
        if net_income > base_net_income:
            return "profit"
        if net_income < 0:
            return "loss"
        return "decline"

    # ===== السيناريوهات الثلاثة =====

    def build_scenarios(self, best=None, worst=None):
        """بناء السيناريوهات الثلاثة (مثالي / طبيعي / أسوأ حالة)

        best/worst: قواميس اختيارية لتعديل معدلات التغيير (نسب عشرية).
        """
        best_rates = dict(self.DEFAULT_BEST)
        best_rates.update(best or {})
        worst_rates = dict(self.DEFAULT_WORST)
        worst_rates.update(worst or {})

        base = self._base_snapshot()
        best_proj = self._project(**best_rates)
        worst_proj = self._project(**worst_rates)

        best_proj["outcome"] = self._outcome(best_proj["net_income"], base["net_income"], "best")
        worst_proj["outcome"] = self._outcome(worst_proj["net_income"], base["net_income"], "worst")

        return {
            "best": best_proj,
            "base": base,
            "worst": worst_proj,
        }

    # ===== تحليل الحساسية =====

    def sensitivity_analysis(self, variable="revenue", steps=None):
        """تأثير تغيير متغير واحد على صافي الربح بخطوات محددة

        variable: revenue | cost | efficiency
        steps: قائمة نسب (عشرية) — الافتراضي ±20/10/5%
        """
        if variable not in self.SENSITIVITY_VARIABLES:
            raise ValueError(f"variable must be one of {self.SENSITIVITY_VARIABLES}")

        base = self._base_snapshot()
        if base["revenue"] <= 0:
            return []
        steps = list(steps) if steps is not None else list(self.SENSITIVITY_STEPS)

        results = []
        for s in steps:
            adjustments = {"revenue_change_pct": 0.0, "cost_change_pct": 0.0, "efficiency_change_pct": 0.0}
            adjustments[f"{variable}_change_pct"] = s
            proj = self._project(**adjustments)
            results.append({
                "pct_change": round(s, 4),
                "revenue": proj["revenue"],
                "net_income": proj["net_income"],
                "net_profit_margin": proj["net_profit_margin"],
                "roe": proj["roe"],
            })

        return results

    def tornado_analysis(self, range_pct=0.20):
        """رسم الإعصار — أثر كل متغير عند حديه الأدنى والأعلى"""
        tornado = []
        for variable in self.SENSITIVITY_VARIABLES:
            adjustments = {"revenue_change_pct": 0.0, "cost_change_pct": 0.0, "efficiency_change_pct": 0.0}
            adjustments[f"{variable}_change_pct"] = range_pct
            high = self._project(**adjustments)["net_income"]
            adjustments[f"{variable}_change_pct"] = -range_pct
            low = self._project(**adjustments)["net_income"]
            tornado.append({
                "variable": variable,
                "low_pct": -range_pct,
                "high_pct": range_pct,
                "low_net": self._round2(low),
                "high_net": self._round2(high),
                "impact": self._round2(abs(high - low)),
            })
        tornado.sort(key=lambda t: (-t["impact"], t["variable"]))
        return tornado

    # ===== جدول المقارنة =====

    def compare_scenarios(self, scenarios):
        """جدول مقارنة المؤشرات بين السيناريوهات الثلاثة"""
        comparison = {}
        for metric in self.COMPARISON_METRICS:
            best = scenarios["best"].get(metric, 0)
            base = scenarios["base"].get(metric, 0)
            worst = scenarios["worst"].get(metric, 0)
            comparison[metric] = {
                "best": self._round2(best),
                "base": self._round2(base),
                "worst": self._round2(worst),
                "best_delta": self._round2(best - base),
                "worst_delta": self._round2(worst - base),
            }
        return comparison

    # ===== حفظ/تحميل =====

    @staticmethod
    def save_scenarios(scenarios, filepath):
        """حفظ السيناريوهات إلى ملف JSON"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(scenarios, f, ensure_ascii=False, indent=2)
            log.info("Scenarios saved to: %s", filepath)
            return True
        except Exception as e:
            log.error("Failed to save scenarios: %s", e)
            return False

    @staticmethod
    def load_scenarios(filepath):
        """تحميل السيناريوهات من ملف JSON"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and all(k in data for k in ("best", "base", "worst")):
                return data
            return {}
        except Exception as e:
            log.error("Failed to load scenarios: %s", e)
            return {}
