# تحليل مراكز التكلفة
# ======================

from utils.app_logger import get_logger

log = get_logger("cost_center")


class CostCenterAnalyzer:
    """تحليل مراكز التكلفة — تقسيم التكاليف وتحليل ربحية الأقسام"""

    def __init__(self, financial_data=None):
        self.data = financial_data or {}
        self.centers = []

    def define_centers(self, centers):
        """
        تعريف مراكز التكلفة
        centers: قائمة dicts مثال:
        [
            {"name": "الإنتاج", "costs": 120000, "revenue": 200000, "headcount": 15},
            {"name": "التسويق", "costs": 30000, "revenue": 80000, "headcount": 5},
            {"name": "الإدارة", "costs": 50000, "revenue": 0, "headcount": 8},
        ]
        """
        self.centers = []
        total_costs = sum(c.get("costs", 0) for c in centers)
        for c in centers:
            costs = c.get("costs", 0)
            revenue = c.get("revenue", 0)
            headcount = c.get("headcount", 1)
            profit = revenue - costs
            margin = (profit / revenue * 100) if revenue else 0
            cost_share = (costs / total_costs * 100) if total_costs else 0
            cost_per_head = costs / headcount if headcount else 0
            revenue_per_head = revenue / headcount if headcount else 0
            self.centers.append({
                "name": c["name"],
                "costs": costs,
                "revenue": revenue,
                "profit": round(profit, 2),
                "margin_pct": round(margin, 2),
                "cost_share_pct": round(cost_share, 2),
                "headcount": headcount,
                "cost_per_head": round(cost_per_head, 2),
                "revenue_per_head": round(revenue_per_head, 2),
                "efficiency": round(revenue / costs, 2) if costs > 0 else float('inf'),
            })
        return self.centers

    def get_summary(self):
        """ملخص مراكز التكلفة"""
        total_costs = sum(c["costs"] for c in self.centers)
        total_revenue = sum(c["revenue"] for c in self.centers)
        total_profit = total_revenue - total_costs
        total_headcount = sum(c["headcount"] for c in self.centers)
        return {
            "total_costs": round(total_costs, 2),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "overall_margin_pct": round(total_profit / total_revenue * 100, 2) if total_revenue else 0,
            "total_headcount": total_headcount,
            "center_count": len(self.centers)
        }

    def rank_by_efficiency(self):
        """ترتيب المراكز حسب الكفاءة"""
        return sorted(self.centers, key=lambda c: c.get("efficiency", 0), reverse=True)

    def rank_by_profitability(self):
        """ترتيب المراكز حسب الربحية"""
        return sorted(self.centers, key=lambda c: c.get("margin_pct", 0), reverse=True)

    def get_recommendations(self):
        """توصيات لتحسين الكفاءة"""
        recs = []
        for c in self.centers:
            if c["revenue"] > 0 and c["margin_pct"] < 0:
                recs.append({
                    "center": c["name"],
                    "type": "loss_warning",
                    "message": f"Center '{c['name']}' is running at a loss ({c['margin_pct']:.1f}%)"
                })
            if c["cost_per_head"] > 0:
                avg_cost_per_head = sum(cc["cost_per_head"] for cc in self.centers) / len(self.centers) if self.centers else 0
                if c["cost_per_head"] > avg_cost_per_head * 1.3:
                    recs.append({
                        "center": c["name"],
                        "type": "high_cost",
                        "message": f"Center '{c['name']}' cost/employee ({c['cost_per_head']:,.0f}) is 30%+ above average ({avg_cost_per_head:,.0f})"
                    })
        return recs
