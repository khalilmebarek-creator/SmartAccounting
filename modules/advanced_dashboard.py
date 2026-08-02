# لوحة التحكم المتقدمة
# =========================

import logging
import math

from modules.benchmarks import ALGERIAN_SECTORS, benchmark_analyzer

logger = logging.getLogger(__name__)

DEFAULT_KPIS = [
    "revenue", "net_profit", "roe", "roa", "liquidity", "debt_ratio",
]

ALL_WIDGETS = [
    "kpi_cards", "revenue_trend", "expense_breakdown", "profitability_trend",
    "ratios_radar", "alerts",
]

_HIGHER_BETTER_THRESHOLDS = {
    "current_ratio": (2.0, 1.0),
    "roe": (15.0, 8.0),
    "roa": (8.0, 3.0),
}

_LOWER_BETTER_THRESHOLDS = {
    "debt_ratio": (0.5, 0.7),
}

_MONTHS_AR = [
    "جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان",
    "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]

_MONTHLY_WEIGHTS = [0.07, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.11, 0.09, 0.08, 0.07, 0.06]
_QUARTERLY_WEIGHTS = [0.20, 0.27, 0.32, 0.21]


class AdvancedDashboardEngine:
    """محرك لوحة التحكم المتقدمة التفاعلية"""

    @staticmethod
    def _safe_div(a, b):
        if b is None or b == 0:
            return 0
        try:
            return a / b
        except (TypeError, ValueError):
            return 0

    # ===== مؤشرات الأداء الرئيسية =====

    def status_for_value(self, key: str, value: float) -> str:
        """تحديد حالة اللون (أخضر/أصفر/أحمر) لقيمة معيار"""
        if key in _LOWER_BETTER_THRESHOLDS:
            green, yellow = _LOWER_BETTER_THRESHOLDS[key]
            if value <= green:
                return "green"
            if value <= yellow:
                return "yellow"
            return "red"
        if key in _HIGHER_BETTER_THRESHOLDS:
            green, yellow = _HIGHER_BETTER_THRESHOLDS[key]
            if value >= green:
                return "green"
            if value >= yellow:
                return "yellow"
            return "red"
        return "green"

    def _kpi_status(self, key: str, value: float) -> str:
        if key == "liquidity":
            return self.status_for_value("current_ratio", value)
        if key == "debt_ratio":
            return self.status_for_value("debt_ratio", value / 100.0)
        if key in ("revenue", "net_profit"):
            if value > 0:
                return "green"
            if value < 0:
                return "red"
            return "yellow"
        return self.status_for_value(key, value)

    def compute_kpis(self, financial_data: dict, ratios: dict) -> list:
        """حساب بطاقات مؤشرات الأداء الرئيسية الستة مع حالة صحتها"""
        ratios = ratios or {}
        revenue = financial_data.get("revenue", 0) or 0
        net_income = financial_data.get("net_income", 0) or 0
        current_assets = financial_data.get("current_assets", 0) or 0
        current_liabilities = financial_data.get("current_liabilities", 0) or 0

        values = {
            "revenue": revenue,
            "net_profit": net_income,
            "roe": ratios.get("roe", 0) or 0,
            "roa": ratios.get("roa", 0) or 0,
            "liquidity": self._safe_div(current_assets, current_liabilities),
            "debt_ratio": (ratios.get("debt_ratio", 0) or 0) * 100,
        }
        units = {
            "revenue": "DZD",
            "net_profit": "DZD",
            "roe": "%",
            "roa": "%",
            "liquidity": "x",
            "debt_ratio": "%",
        }

        kpis = []
        for key in DEFAULT_KPIS:
            value = values.get(key, 0)
            kpis.append({
                "key": key,
                "value": round(value, 2),
                "unit": units.get(key, ""),
                "status": self._kpi_status(key, value),
            })
        logger.info(f"Dashboard KPIs computed: ROE={values['roe']}%, CR={values['liquidity']}")
        return kpis

    # ===== بيانات الرسوم البيانية =====

    def revenue_trend(self, financial_data: dict, period: str = "monthly") -> dict:
        """سلسلة الإيرادات الشهرية أو الربعية (توزيع تناسبي للإيرادات السنوية)"""
        revenue = financial_data.get("revenue", 0) or 0
        if period == "quarterly":
            weights, labels = _QUARTERLY_WEIGHTS, ["Q1", "Q2", "Q3", "Q4"]
        else:
            weights, labels = _MONTHLY_WEIGHTS, list(_MONTHS_AR)
        values = [round(revenue * w) for w in weights]
        diff = round(revenue) - sum(values)
        values[-1] += diff
        return {"labels": labels, "values": values}

    def expense_breakdown(self, financial_data: dict) -> dict:
        """توزيع الإيرادات بين تكلفة البضاعة والمصاريف وصافي الربح"""
        revenue = financial_data.get("revenue", 0) or 0
        cogs = financial_data.get("cost_of_goods_sold", 0) or 0
        gross = financial_data.get("gross_profit", 0) or 0
        opex = financial_data.get("operating_expenses", 0) or 0
        net = financial_data.get("net_income", 0) or 0

        if not cogs and gross:
            cogs = max(0, revenue - gross)
        if not opex and gross:
            opex = max(0, gross - net)
        return {
            "labels": ["cogs", "opex", "net_profit"],
            "values": [round(cogs, 2), round(opex, 2), round(net, 2)],
        }

    def profitability_trend(self, history: list) -> dict:
        """اتجاه الربحية عبر السنوات (ROE وهامش صافي الربح)"""
        years = []
        series = {"roe": [], "net_profit_margin": []}
        if not history:
            return {"years": years, "series": series}
        ordered = sorted(history, key=lambda h: h.get("year", 0) or 0)
        for h in ordered:
            ratios = h.get("ratios") or {}
            years.append(h.get("year", 0))
            series["roe"].append(ratios.get("roe", 0) or 0)
            series["net_profit_margin"].append(ratios.get("net_profit_margin", 0) or 0)
        return {"years": years, "series": series}

    def ratios_radar(self, ratios: dict, sector_code: str) -> dict:
        """بيانات الرادار: مقارنة نسب الشركة مع متوسط القطاع"""
        return benchmark_analyzer.get_radar_data(ratios or {}, sector_code)

    # ===== نظام التنبيهات =====

    def _anomaly_alerts(self, financial_data: dict) -> list:
        alerts = []
        total_assets = financial_data.get("total_assets", 0) or 0
        total_liabilities = financial_data.get("total_liabilities", 0) or 0
        equity = financial_data.get("equity", 0) or 0
        if abs(total_assets - (total_liabilities + equity)) > 1:
            alerts.append({
                "category": "anomaly",
                "severity": "critical",
                "key": "balance_sheet",
                "message_ar": "عدم تطابق في معادلة الميزانية: الأصول ≠ الخصوم + حقوق الملكية",
                "message_en": "Balance sheet mismatch: Assets ≠ Liabilities + Equity",
            })

        gross = financial_data.get("gross_profit", 0) or 0
        opex = financial_data.get("operating_expenses", 0) or 0
        net = financial_data.get("net_income", 0) or 0
        if net and opex:
            expected_net = gross - opex
            if abs(net - expected_net) > max(1, abs(net) * 0.05):
                alerts.append({
                    "category": "anomaly",
                    "severity": "warning",
                    "key": "income_statement",
                    "message_ar": "عدم تطابق في قائمة الدخل: صافي الربح لا يطابق (مجمل الربح - المصاريف التشغيلية)",
                    "message_en": "Income statement mismatch: net income does not match (gross profit - operating expenses)",
                })

        for field, label_ar, label_en in (
            ("equity", "حقوق الملكية", "Equity"),
            ("current_assets", "الأصول المتداولة", "Current Assets"),
            ("current_liabilities", "الخصوم المتداولة", "Current Liabilities"),
            ("revenue", "الإيرادات", "Revenue"),
            ("net_income", "صافي الربح", "Net Income"),
        ):
            if (financial_data.get(field, 0) or 0) < 0:
                alerts.append({
                    "category": "anomaly",
                    "severity": "warning",
                    "key": f"{field}_negative",
                    "message_ar": f"قيمة سالبة غير منطقية في {label_ar}",
                    "message_en": f"Unreasonable negative value in {label_en}",
                })
        return alerts

    def _performance_alerts(self, financial_data: dict, ratios: dict) -> list:
        alerts = []
        ratios = ratios or {}
        if (financial_data.get("net_income", 0) or 0) < 0:
            alerts.append({
                "category": "performance",
                "severity": "critical",
                "key": "net_income",
                "message_ar": "الشركة تسجل خسارة صافية - تحذير أداء",
                "message_en": "Company is recording a net loss - performance warning",
            })

        current_ratio = ratios.get("current_ratio", 0) or 0
        if current_ratio < 0.5:
            alerts.append({
                "category": "performance",
                "severity": "critical",
                "key": "current_ratio",
                "message_ar": "السيولة منخفضة جداً: صعوبات محتملة في الوفاء بالالتزامات قصيرة الأجل",
                "message_en": "Critically low liquidity: potential difficulty meeting short-term obligations",
            })
        elif current_ratio < 1.0:
            alerts.append({
                "category": "performance",
                "severity": "warning",
                "key": "current_ratio",
                "message_ar": "السيولة أقل من المستوى الآمن (نسبة التداول أقل من 1)",
                "message_en": "Liquidity below safe level (current ratio below 1)",
            })

        if (ratios.get("debt_to_equity", 0) or 0) > 2:
            alerts.append({
                "category": "performance",
                "severity": "warning",
                "key": "debt_to_equity",
                "message_ar": "نسبة الدين إلى حقوق الملكية مرتفعة (أعلى من 2)",
                "message_en": "High debt to equity ratio (above 2)",
            })
        return alerts

    def _ratio_alerts(self, ratios: dict, sector_code: str) -> list:
        if not sector_code or sector_code not in ALGERIAN_SECTORS:
            return []
        alerts = []
        for s in benchmark_analyzer.suggest_improvements(ratios or {}, sector_code):
            alerts.append({
                "category": "ratio",
                "severity": s.get("severity", "warning"),
                "key": s.get("ratio", ""),
                "message_ar": s.get("message_ar", ""),
                "message_en": s.get("message_en", ""),
            })
        return alerts

    def _action_items(self, financial_data: dict, ratios: dict, sector_code: str) -> list:
        if not sector_code or sector_code not in ALGERIAN_SECTORS:
            return []
        actions = []
        for s in benchmark_analyzer.suggest_improvements(ratios or {}, sector_code):
            if s.get("severity") in ("critical", "warning"):
                actions.append({
                    "category": "action",
                    "severity": s.get("severity", "warning"),
                    "key": s.get("ratio", ""),
                    "message_ar": "إجراء مقترح: " + s.get("message_ar", ""),
                    "message_en": "Suggested action: " + s.get("message_en", ""),
                })
        return actions

    def alerts(self, financial_data: dict, ratios: dict,
               sector_code: str = None) -> list:
        """تجميع جميع التنبيهات (شذوذ/أداء/معايير/إجراءات)"""
        items = []
        items.extend(self._anomaly_alerts(financial_data))
        items.extend(self._performance_alerts(financial_data, ratios))
        items.extend(self._ratio_alerts(ratios, sector_code))
        items.extend(self._action_items(financial_data, ratios, sector_code))
        return items

    # ===== التخصيص والتخطيط =====

    def default_layout(self) -> dict:
        return {
            "name": "default",
            "widgets": list(ALL_WIDGETS),
            "kpis": list(DEFAULT_KPIS),
            "color": "#2196F3",
        }

    def build_layout(self, widgets: list, kpis: list,
                     color: str = "#2196F3", name: str = "custom") -> dict:
        return {
            "name": name,
            "widgets": list(widgets),
            "kpis": list(kpis),
            "color": color,
        }

    def health_score(self, kpis: list) -> dict:
        """درجة الصحة العامة للشركة من حالة مؤشرات الأداء"""
        score_map = {"green": 100, "yellow": 60, "red": 20}
        if not kpis:
            return {"score": 0, "color": "#E74C3C", "rating_ar": "غير متوفر", "rating_en": "N/A"}
        total = sum(score_map.get(k.get("status"), 60) for k in kpis)
        score = total / len(kpis)
        if score >= 85:
            return {"score": round(score, 1), "color": "#27AE60", "rating_ar": "ممتاز", "rating_en": "Excellent"}
        if score >= 60:
            return {"score": round(score, 1), "color": "#F39C12", "rating_ar": "جيد", "rating_en": "Good"}
        return {"score": round(score, 1), "color": "#E74C3C", "rating_ar": "ضعيف", "rating_en": "Poor"}

    # ===== التصدير =====

    def export_data(self, financial_data: dict, ratios: dict,
                    sector_code: str = None) -> dict:
        """تجميع كل بيانات اللوحة لتصديرها إلى PDF/Excel"""
        return {
            "kpis": self.compute_kpis(financial_data, ratios),
            "expenses": self.expense_breakdown(financial_data),
            "revenue_trend": self.revenue_trend(financial_data, period="monthly"),
            "alerts": self.alerts(financial_data, ratios, sector_code),
            "ratios": ratios or {},
        }


advanced_dashboard_engine = AdvancedDashboardEngine()
