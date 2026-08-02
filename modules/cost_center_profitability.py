# تحليل ربحية مراكز التكلفة — محرك متقدم
# =========================================
# تعريف مراكز التكلفة (أقسام/مشاريع/فروع/خطوط إنتاج) + توزيع التكاليف
# المباشرة وغير المباشرة بطرق تخصيص متعددة + تحليل الربحية + المقارنات
# (بين المراكز / الفترات السابقة / الميزانية / المعايير) + التقارير
# (الأداء / الترتيب / الاتجاه / التباين) + التوصيات.

from utils.app_logger import get_logger

log = get_logger("cost_center_profitability")

_ALLOCATION_METHODS = ("revenue", "headcount", "area", "equal")

_VALID_TYPES = ("department", "project", "branch", "production_line")


def _round2(value):
    return round(float(value or 0), 2)


class CostCenterProfitabilityEngine:
    """محرك تحليل ربحية مراكز التكلفة"""

    def __init__(self, financial_data=None):
        self.data = financial_data or {}
        self.centers = []
        self.target_margin_pct = 0.0
        self.last_method = "revenue"
        self.last_indirect_total = 0.0

    # ---------- التعريف ----------

    def define_centers(self, centers):
        """تخزين المراكز الخام. القائمة الداخلية تُبنى عند التخصيص."""
        self.centers = []
        self._raw_centers = list(centers) if centers else []
        return self._raw_centers

    def set_standards(self, target_margin_pct):
        """تعيين هامش الربح المعياري للمقارنة مع المعايير."""
        if target_margin_pct is not None and target_margin_pct >= 0:
            self.target_margin_pct = float(target_margin_pct)
        return self.target_margin_pct

    # ---------- التوزيع (Allocation) ----------

    def _weight(self, center, method):
        if method == "headcount":
            return max(float(center.get("headcount") or 0), 0.0)
        if method == "area":
            return max(float(center.get("area") or 0), 0.0)
        if method == "equal":
            return 1.0
        return max(float(center.get("revenue") or 0), 0.0)

    def allocate(self, indirect_total, method="revenue"):
        """
        توزيع التكاليف غير المباشرة على المراكز.
        الطرق: revenue / headcount / area / equal — غير المعروفة ترجع إلى revenue.
        """
        method = method if method in _ALLOCATION_METHODS else "revenue"
        indirect_total = float(indirect_total or 0)
        self.last_method = method
        self.last_indirect_total = indirect_total

        raw = list(getattr(self, "_raw_centers", []) or [])
        weights = [self._weight(c, method) for c in raw]
        total_weight = sum(weights)

        # إن كانت جميع الأوزان صفراً نوزّع بالتساوي لتجنب القسمة على صفر
        if total_weight <= 0 and raw:
            weights = [1.0] * len(raw)
            total_weight = float(len(raw))

        # المرحلة 1: التوزيع والحسابات الأساسية
        enriched = []
        for center, weight in zip(raw, weights):
            revenue = _round2(center.get("revenue", 0))
            direct = _round2(center.get("direct_costs", center.get("costs", 0)))
            headcount = _round2(center.get("headcount", 0))
            area = _round2(center.get("area", 0))
            ctype = center.get("type", "department")
            if ctype not in _VALID_TYPES:
                ctype = "department"

            if total_weight > 0 and indirect_total > 0:
                indirect = _round2(indirect_total * weight / total_weight)
            else:
                indirect = 0.0

            total_costs = _round2(direct + indirect)
            profit = _round2(revenue - total_costs)
            margin = _round2(profit / revenue * 100) if revenue else 0.0
            alloc_base_pct = _round2(weight / total_weight * 100) if total_weight > 0 else 0.0

            enriched.append({
                "name": center.get("name", ""),
                "type": ctype,
                "revenue": revenue,
                "direct_costs": direct,
                "indirect_costs": indirect,
                "total_costs": total_costs,
                "profit": profit,
                "margin_pct": margin,
                "headcount": headcount,
                "area": area,
                "revenue_share_pct": 0.0,
                "cost_share_pct": 0.0,
                "profit_share_pct": 0.0,
                "alloc_base_pct": alloc_base_pct,
            })

        # المرحلة 2: الحصص النسبية
        total_revenue = sum(c["revenue"] for c in enriched) or 0.0
        total_costs_all = sum(c["total_costs"] for c in enriched) or 0.0
        total_profit = sum(c["profit"] for c in enriched) or 0.0
        for c in enriched:
            c["revenue_share_pct"] = _round2(c["revenue"] / total_revenue * 100) if total_revenue else 0.0
            c["cost_share_pct"] = _round2(c["total_costs"] / total_costs_all * 100) if total_costs_all else 0.0
            c["profit_share_pct"] = _round2(c["profit"] / total_profit * 100) if total_profit else 0.0

        self.centers = enriched
        return self.centers

    # ---------- تحليل الربحية ----------

    def get_summary(self):
        centers = self.centers
        total_revenue = sum(c["revenue"] for c in centers)
        total_direct = sum(c["direct_costs"] for c in centers)
        total_indirect = sum(c["indirect_costs"] for c in centers)
        total_costs = total_direct + total_indirect
        total_profit = total_revenue - total_costs
        overall_margin = _round2(total_profit / total_revenue * 100) if total_revenue else 0.0

        best = None
        worst = None
        if centers:
            def _key(c):
                return (c["margin_pct"], c["profit"], c["revenue"])
            best = max(centers, key=_key)["name"]
            worst = min(centers, key=_key)["name"]

        return {
            "total_revenue": _round2(total_revenue),
            "total_direct_costs": _round2(total_direct),
            "total_indirect_costs": _round2(total_indirect),
            "total_costs": _round2(total_costs),
            "total_profit": _round2(total_profit),
            "overall_margin_pct": overall_margin,
            "center_count": len(centers),
            "best_center": best,
            "worst_center": worst,
        }

    def rank_by_profitability(self):
        """ترتيب حسب هامش الربح ثم الربح ثم الإيرادات."""
        return sorted(
            self.centers,
            key=lambda c: (c["margin_pct"], c["profit"], c["revenue"]),
            reverse=True,
        )

    def rank_by_profit(self):
        """ترتيب حسب صافي الربح."""
        return sorted(self.centers, key=lambda c: c["profit"], reverse=True)

    # ---------- المقارنات ----------

    def _match_actual(self, name):
        for c in self.centers:
            if c["name"] == name:
                return c
        return None

    def compare_previous(self, previous_data):
        """
        مقارنة المراكز الحالية مع الفترة السابقة.
        previous_data: قائمة {name, revenue, costs}
        """
        rows = []
        for prev in previous_data or []:
            name = prev.get("name", "")
            actual = self._match_actual(name)
            if actual is None:
                continue
            prev_rev = _round2(prev.get("revenue", 0))
            prev_costs = _round2(prev.get("costs", 0))
            prev_profit = _round2(prev_rev - prev_costs)
            rev_delta = _round2(actual["revenue"] - prev_rev)
            profit_delta = _round2(actual["profit"] - prev_profit)
            rev_delta_pct = _round2(rev_delta / prev_rev * 100) if prev_rev else 0.0
            profit_delta_pct = _round2(profit_delta / prev_profit * 100) if prev_profit else 0.0
            change = "stable"
            if profit_delta > 0 and profit_delta_pct >= 1:
                change = "improved"
            elif profit_delta < 0 and profit_delta_pct <= -1:
                change = "declined"
            rows.append({
                "name": name,
                "revenue": actual["revenue"],
                "prev_revenue": prev_rev,
                "revenue_delta": rev_delta,
                "revenue_delta_pct": rev_delta_pct,
                "profit": actual["profit"],
                "prev_profit": prev_profit,
                "profit_delta": profit_delta,
                "profit_delta_pct": profit_delta_pct,
                "change": change,
            })
        return rows

    def compare_budget(self, budget_data):
        """
        مقارنة المراكز الحالية مع الميزانية (تحليل التباين).
        budget_data: قائمة {name, revenue, costs}
        """
        rows = []
        for budget in budget_data or []:
            name = budget.get("name", "")
            actual = self._match_actual(name)
            if actual is None:
                continue
            budget_rev = _round2(budget.get("revenue", 0))
            budget_costs = _round2(budget.get("costs", 0))
            budget_profit = _round2(budget_rev - budget_costs)
            rev_var = _round2(actual["revenue"] - budget_rev)
            profit_var = _round2(actual["profit"] - budget_profit)
            rev_var_pct = _round2(rev_var / budget_rev * 100) if budget_rev else 0.0
            profit_var_pct = _round2(profit_var / budget_profit * 100) if budget_profit else 0.0
            rows.append({
                "name": name,
                "revenue": actual["revenue"],
                "budget_revenue": budget_rev,
                "revenue_variance": rev_var,
                "revenue_var_pct": rev_var_pct,
                "profit": actual["profit"],
                "budget_profit": budget_profit,
                "profit_variance": profit_var,
                "profit_var_pct": profit_var_pct,
                "variance_type": "favorable" if profit_var >= 0 else "unfavorable",
            })
        return rows

    def compare_standards(self):
        """مقارنة هوامش المراكز مع الهامش المعياري المحدد."""
        target = float(self.target_margin_pct or 0)
        rows = []
        for c in self.centers:
            margin = c["margin_pct"]
            gap = _round2(margin - target)
            if c["revenue"] == 0:
                status = "below" if target > 0 else "meets"
            elif margin >= target:
                status = "meets" if _round2(margin - target) == 0 else "above"
            else:
                status = "below"
            rows.append({
                "name": c["name"],
                "margin_pct": margin,
                "target_margin_pct": target,
                "gap_pct": gap,
                "status": status,
            })
        return rows

    # ---------- الاتجاه والتباين ----------

    def trend_analysis(self, periods):
        """
        تحليل الاتجاه عبر فترات زمنية.
        periods: قائمة من الفترات، كل فترة قائمة مراكز {name, revenue, costs}.
        """
        result_periods = []
        for idx, period in enumerate(periods or [], start=1):
            revenue = sum(_round2(c.get("revenue", 0)) for c in period or [])
            costs = sum(_round2(c.get("costs", c.get("direct_costs", 0))) for c in period or [])
            profit = _round2(revenue - costs)
            margin = _round2(profit / revenue * 100) if revenue else 0.0
            result_periods.append({
                "period": idx,
                "revenue": _round2(revenue),
                "costs": _round2(costs),
                "profit": profit,
                "margin_pct": margin,
            })

        direction = "flat"
        growth_rate_pct = 0.0
        if len(result_periods) >= 2:
            first_profit = result_periods[0]["profit"]
            last_profit = result_periods[-1]["profit"]
            if last_profit > first_profit:
                direction = "up"
            elif last_profit < first_profit:
                direction = "down"
            growth_rate_pct = _round2(
                (last_profit - first_profit) / first_profit * 100
            ) if first_profit else 0.0

        return {
            "periods": result_periods,
            "direction": direction,
            "growth_rate_pct": growth_rate_pct,
        }

    def variance_analysis(self, budget_data):
        """تقرير التباين الإجمالي مقابل الميزانية."""
        rows = self.compare_budget(budget_data)
        total_actual_rev = sum(r["revenue"] for r in rows)
        total_budget_rev = sum(r["budget_revenue"] for r in rows)
        total_actual_profit = sum(r["profit"] for r in rows)
        total_budget_profit = sum(r["budget_profit"] for r in rows)
        return {
            "total_actual_revenue": _round2(total_actual_rev),
            "total_budget_revenue": _round2(total_budget_rev),
            "total_revenue_variance": _round2(total_actual_rev - total_budget_rev),
            "total_actual_profit": _round2(total_actual_profit),
            "total_budget_profit": _round2(total_budget_profit),
            "total_profit_variance": _round2(total_actual_profit - total_budget_profit),
            "items": rows,
        }

    # ---------- التقارير والتوصيات ----------

    def get_reports(self):
        """تقرير متكامل: الأداء + الترتيب + التوصيات."""
        return {
            "performance": self.centers,
            "ranking": self.rank_by_profitability(),
            "recommendations": self.get_recommendations(),
        }

    def get_recommendations(self):
        """توصيات ذكية لتحسين ربحية المراكز."""
        recs = []
        centers = self.centers
        if not centers:
            return recs

        by_margin = sorted(
            centers, key=lambda c: (c["margin_pct"], c["profit"]), reverse=True
        )

        for c in centers:
            if c["revenue"] > 0 and c["profit"] < 0:
                recs.append({
                    "center": c["name"],
                    "type": "loss_warning",
                    "message": f"loss:{c['margin_pct']:.1f}",
                })

        for c in centers:
            if c["total_costs"] > 0:
                indirect_share = c["indirect_costs"] / c["total_costs"] * 100
                if indirect_share > 40:
                    recs.append({
                        "center": c["name"],
                        "type": "high_indirect",
                        "message": f"indirect_share:{indirect_share:.1f}",
                    })

        target = float(self.target_margin_pct or 0)
        if target > 0:
            for c in centers:
                if c["revenue"] > 0 and 0 <= c["margin_pct"] < target:
                    recs.append({
                        "center": c["name"],
                        "type": "low_margin",
                        "message": f"margin:{c['margin_pct']:.1f}",
                    })

        top = by_margin[0]
        if top["revenue"] > 0 and top["margin_pct"] > 0:
            recs.append({
                "center": top["name"],
                "type": "top_performer",
                "message": f"margin:{top['margin_pct']:.1f}",
            })

        avg_cost_per_head = sum(
            c["direct_costs"] / c["headcount"] for c in centers if c["headcount"] > 0
        ) / sum(1 for c in centers if c["headcount"] > 0) if any(
            c["headcount"] > 0 for c in centers
        ) else 0.0
        if avg_cost_per_head > 0:
            for c in centers:
                if c["headcount"] > 0:
                    cph = c["direct_costs"] / c["headcount"]
                    if cph > avg_cost_per_head * 1.3:
                        recs.append({
                            "center": c["name"],
                            "type": "high_cost_per_head",
                            "message": f"cost_per_head:{cph:,.0f}",
                        })
        return recs

    # ---------- دفعة واحدة ----------

    def analyze(self, centers, indirect_total=0, method="revenue",
                target_margin_pct=None):
        """تحليل كامل دفعة واحدة."""
        self.define_centers(centers)
        if target_margin_pct is not None:
            self.set_standards(target_margin_pct)
        self.allocate(indirect_total, method=method)
        return {
            "centers": self.centers,
            "summary": self.get_summary(),
        }


cost_center_profitability_engine = CostCenterProfitabilityEngine()
