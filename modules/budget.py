# التخطيط والمتابعة المالية
# ===========================

import json
from utils.app_logger import get_logger

log = get_logger("budget")


class BudgetPlanner:
    """محرك موازنة التخطيط — إنشاء ومتابعة الموازنة"""

    def __init__(self, financial_data=None):
        self.data = financial_data or {}
        self.budget_items = []

    def create_annual_budget(self, categories):
        """
        إنشاء موازنة سنوية
        categories: dict مثال:
        {
            "revenue": {"budgeted": 500000},
            "cost_of_goods_sold": {"budgeted": 300000},
            "operating_expenses": {"budgeted": 100000},
            "salaries": {"budgeted": 80000},
            "marketing": {"budgeted": 20000},
        }
        """
        self.budget_items = []
        for cat, vals in categories.items():
            actual = self.data.get(cat, 0)
            budgeted = vals.get("budgeted", 0)
            variance = actual - budgeted
            variance_pct = (variance / budgeted * 100) if budgeted else 0
            self.budget_items.append({
                "category": cat,
                "budgeted": budgeted,
                "actual": actual,
                "variance": round(variance, 2),
                "variance_pct": round(variance_pct, 2),
                "status": "over" if variance > 0 else "under" if variance < 0 else "on_track"
            })
        return self.budget_items

    def get_summary(self):
        """ملخص الموازنة"""
        total_budgeted = sum(item["budgeted"] for item in self.budget_items)
        total_actual = sum(item["actual"] for item in self.budget_items)
        total_variance = total_actual - total_budgeted
        utilization = (total_actual / total_budgeted * 100) if total_budgeted else 0
        return {
            "total_budgeted": round(total_budgeted, 2),
            "total_actual": round(total_actual, 2),
            "total_variance": round(total_variance, 2),
            "utilization_pct": round(utilization, 2),
            "item_count": len(self.budget_items)
        }

    def get_alerts(self, threshold_pct=10):
        """تنبيهات تجاوز الموازنة"""
        alerts = []
        for item in self.budget_items:
            if item["budgeted"] > 0:
                pct_over = (item["actual"] / item["budgeted"]) * 100
                if pct_over > (100 + threshold_pct):
                    alerts.append({
                        "category": item["category"],
                        "budgeted": item["budgeted"],
                        "actual": item["actual"],
                        "pct_over": round(pct_over - 100, 2),
                        "severity": "high" if pct_over > 120 else "medium"
                    })
        return alerts

    def variance_analysis(self):
        """تحليل الانحرافات"""
        favorable = [i for i in self.budget_items if i["variance"] < 0]
        unfavorable = [i for i in self.budget_items if i["variance"] > 0]
        on_track = [i for i in self.budget_items if i["variance"] == 0]
        return {
            "favorable": favorable,
            "unfavorable": unfavorable,
            "on_track": on_track,
            "favorable_count": len(favorable),
            "unfavorable_count": len(unfavorable),
        }

    def export_json(self):
        """تصدير كـ JSON"""
        return json.dumps({
            "items": self.budget_items,
            "summary": self.get_summary(),
            "alerts": self.get_alerts()
        }, ensure_ascii=False, indent=2)
