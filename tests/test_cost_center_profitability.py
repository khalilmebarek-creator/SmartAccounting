# اختبارات تحليل ربحية مراكز التكلفة
# =====================================
# TDD: المحرك + محرك التخصيص + المقارنات + التقارير

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from modules.cost_center_profitability import CostCenterProfitabilityEngine


# ============ التخصيص (Allocation) ============

def _centers():
    return [
        {"name": "الإنتاج", "type": "department", "revenue": 200000, "direct_costs": 80000, "headcount": 15, "area": 500},
        {"name": "التسويق", "type": "department", "revenue": 80000, "direct_costs": 30000, "headcount": 5, "area": 200},
        {"name": "المبيعات", "type": "branch", "revenue": 120000, "direct_costs": 50000, "headcount": 10, "area": 300},
    ]


def test_allocate_revenue_method():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(50000, method="revenue")
    revs = [c["revenue"] for c in result]
    total = sum(revs)
    for c in result:
        expected = round(50000 * c["revenue"] / total, 2)
        assert c["indirect_costs"] == pytest.approx(expected, abs=0.05)


def test_allocate_headcount_method():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(50000, method="headcount")
    hcs = [c["headcount"] for c in result]
    total = sum(hcs)
    for c in result:
        expected = round(50000 * c["headcount"] / total, 2)
        assert c["indirect_costs"] == pytest.approx(expected, abs=0.05)


def test_allocate_area_method():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(50000, method="area")
    areas = [c["area"] for c in result]
    total = sum(areas)
    for c in result:
        expected = round(50000 * c["area"] / total, 2)
        assert c["indirect_costs"] == pytest.approx(expected, abs=0.05)


def test_allocate_equal_method():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(60000, method="equal")
    for c in result:
        assert c["indirect_costs"] == pytest.approx(20000, abs=0.01)


def test_allocate_zero_indirect():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(0, method="revenue")
    for c in result:
        assert c["indirect_costs"] == 0


def test_total_allocated_equals_pool():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(33333.33, method="revenue")
    total = sum(c["indirect_costs"] for c in result)
    assert total == pytest.approx(33333.33, abs=0.05)


def test_allocate_zero_revenue_falls_back_equal():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "A", "revenue": 0, "direct_costs": 10},
        {"name": "B", "revenue": 0, "direct_costs": 10},
    ])
    result = engine.allocate(100, method="revenue")
    for c in result:
        assert c["indirect_costs"] == pytest.approx(50, abs=0.01)


def test_allocate_area_missing_falls_back_equal():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "A", "revenue": 100, "area": 0},
        {"name": "B", "revenue": 100, "area": 0},
    ])
    result = engine.allocate(100, method="area")
    for c in result:
        assert c["indirect_costs"] == pytest.approx(50, abs=0.01)


def test_unknown_method_falls_back_revenue():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(50000, method="unknown")
    revs = [c["revenue"] for c in result]
    total = sum(revs)
    for c in result:
        expected = round(50000 * c["revenue"] / total, 2)
        assert c["indirect_costs"] == pytest.approx(expected, abs=0.05)


def test_total_costs_equals_direct_plus_indirect():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(50000, method="revenue")
    for c in result:
        assert c["total_costs"] == pytest.approx(c["direct_costs"] + c["indirect_costs"], abs=0.01)


def test_alloc_base_pct_sums_100():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(50000, method="revenue")
    total = sum(c["alloc_base_pct"] for c in result)
    assert total == pytest.approx(100, abs=0.1)


def test_legacy_costs_field_accepted():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "A", "revenue": 100, "costs": 30},
    ])
    result = engine.allocate(0, method="revenue")
    assert result[0]["direct_costs"] == 30
    assert result[0]["total_costs"] == 30


# ============ الربحية ============

def test_profit_margin_positive():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(0, method="revenue")
    production = next(c for c in result if c["name"] == "الإنتاج")
    assert production["profit"] == pytest.approx(120000, abs=0.01)
    assert production["margin_pct"] == pytest.approx(60, abs=0.1)


def test_loss_center_negative_margin():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "خاسر", "revenue": 50000, "direct_costs": 90000},
    ])
    result = engine.allocate(0, method="revenue")
    assert result[0]["profit"] < 0
    assert result[0]["margin_pct"] < 0


def test_zero_revenue_center_margin_zero():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "إدارة", "revenue": 0, "direct_costs": 40000},
    ])
    result = engine.allocate(0, method="revenue")
    assert result[0]["margin_pct"] == 0
    assert result[0]["profit"] == -40000


def test_summary_totals():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(50000, method="revenue")
    summary = engine.get_summary()
    assert summary["total_revenue"] == 400000
    assert summary["total_direct_costs"] == 160000
    assert summary["total_indirect_costs"] == 50000
    assert summary["total_costs"] == 210000
    assert summary["total_profit"] == pytest.approx(190000, abs=0.1)
    assert summary["overall_margin_pct"] == pytest.approx(47.5, abs=0.1)
    assert summary["center_count"] == 3


def test_summary_best_worst_center():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    summary = engine.get_summary()
    assert summary["best_center"] == "التسويق"
    assert summary["worst_center"] == "المبيعات"


def test_rank_by_profitability_sorted():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    ranked = engine.rank_by_profitability()
    margins = [c["margin_pct"] for c in ranked]
    assert margins == sorted(margins, reverse=True)
    assert ranked[0]["name"] == "التسويق"


def test_rank_by_profit_sorted():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    ranked = engine.rank_by_profit()
    profits = [c["profit"] for c in ranked]
    assert profits == sorted(profits, reverse=True)


def test_revenue_share_pct_sums_100():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    result = engine.allocate(0, method="revenue")
    total = sum(c["revenue_share_pct"] for c in result)
    assert total == pytest.approx(100, abs=0.1)


# ============ المقارنات ============

def test_compare_previous_delta():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    previous = [
        {"name": "الإنتاج", "revenue": 150000, "costs": 100000},
        {"name": "التسويق", "revenue": 90000, "costs": 30000},
    ]
    rows = engine.compare_previous(previous)
    production = next(r for r in rows if r["name"] == "الإنتاج")
    assert production["revenue_delta"] == 50000
    assert production["prev_profit"] == 50000
    assert production["change"] == "improved"


def test_compare_previous_decline():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    previous = [{"name": "التسويق", "revenue": 90000, "costs": 30000}]
    rows = engine.compare_previous(previous)
    marketing = next(r for r in rows if r["name"] == "التسويق")
    assert marketing["change"] == "declined"


def test_compare_previous_only_common_centers():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    rows = engine.compare_previous([{"name": "الإنتاج", "revenue": 100, "costs": 100}])
    assert len(rows) == 1
    assert rows[0]["name"] == "الإنتاج"


def test_compare_budget_variance():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    budget = [
        {"name": "الإنتاج", "revenue": 180000, "costs": 90000},
        {"name": "التسويق", "revenue": 90000, "costs": 25000},
        {"name": "المبيعات", "revenue": 120000, "costs": 50000},
    ]
    rows = engine.compare_budget(budget)
    production = next(r for r in rows if r["name"] == "الإنتاج")
    assert production["revenue_variance"] == 20000
    assert production["profit_variance"] == pytest.approx(30000, abs=0.1)
    assert production["variance_type"] == "favorable"


def test_compare_budget_unfavorable():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    budget = [{"name": "التسويق", "revenue": 90000, "costs": 30000}]
    rows = engine.compare_budget(budget)
    marketing = next(r for r in rows if r["name"] == "التسويق")
    assert marketing["profit_variance"] == pytest.approx(-10000, abs=0.1)
    assert marketing["variance_type"] == "unfavorable"


def test_compare_standards_status():
    engine = CostCenterProfitabilityEngine()
    engine.set_standards(30)
    engine.define_centers([
        {"name": "قوي", "revenue": 100, "direct_costs": 40},
        {"name": "ضعيف", "revenue": 100, "direct_costs": 80},
    ])
    engine.allocate(0, method="revenue")
    rows = engine.compare_standards()
    strong = next(r for r in rows if r["name"] == "قوي")
    assert strong["status"] == "above"
    weak = next(r for r in rows if r["name"] == "ضعيف")
    assert weak["status"] == "below"
    assert weak["gap_pct"] == pytest.approx(-10, abs=0.1)


def test_compare_standards_meets():
    engine = CostCenterProfitabilityEngine()
    engine.set_standards(62.5)
    engine.define_centers([{"name": "A", "revenue": 100, "direct_costs": 37.5}])
    engine.allocate(0, method="revenue")
    row = engine.compare_standards()[0]
    assert row["status"] == "meets"


# ============ الاتجاه والتباين ============

def test_trend_analysis_structure():
    engine = CostCenterProfitabilityEngine()
    periods = [
        [
            {"name": "A", "revenue": 100, "costs": 60},
            {"name": "B", "revenue": 100, "costs": 70},
        ],
        [
            {"name": "A", "revenue": 200, "costs": 80},
            {"name": "B", "revenue": 100, "costs": 70},
        ],
    ]
    result = engine.trend_analysis(periods)
    assert len(result["periods"]) == 2
    assert result["periods"][0]["profit"] == pytest.approx(70, abs=0.1)
    assert result["periods"][1]["profit"] == pytest.approx(150, abs=0.1)
    assert result["direction"] == "up"
    assert result["growth_rate_pct"] > 0


def test_trend_analysis_down():
    engine = CostCenterProfitabilityEngine()
    periods = [
        [{"name": "A", "revenue": 200, "costs": 80}],
        [{"name": "A", "revenue": 100, "costs": 80}],
    ]
    result = engine.trend_analysis(periods)
    assert result["direction"] == "down"


def test_variance_analysis_report():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    budget = [
        {"name": "الإنتاج", "revenue": 180000, "costs": 90000},
        {"name": "التسويق", "revenue": 90000, "costs": 30000},
        {"name": "المبيعات", "revenue": 120000, "costs": 50000},
    ]
    report = engine.variance_analysis(budget)
    assert report["total_actual_revenue"] == 400000
    assert report["total_budget_revenue"] == 390000
    assert report["total_revenue_variance"] == 10000
    assert report["total_profit_variance"] == pytest.approx(20000, abs=0.1)
    assert len(report["items"]) == 3


# ============ التقارير والتوصيات ============

def test_reports_returns_all_sections():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(30000, method="revenue")
    reports = engine.get_reports()
    assert "performance" in reports
    assert "ranking" in reports
    assert "recommendations" in reports
    assert len(reports["performance"]) == 3
    assert reports["ranking"][0]["name"] == "التسويق"


def test_recommendations_loss_warning():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "خاسر", "revenue": 50000, "direct_costs": 90000},
    ])
    engine.allocate(0, method="revenue")
    recs = engine.get_recommendations()
    assert any(r["type"] == "loss_warning" for r in recs)


def test_recommendations_high_indirect_share():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "A", "revenue": 100000, "direct_costs": 10000, "headcount": 10},
        {"name": "B", "revenue": 100000, "direct_costs": 10000, "headcount": 10},
    ])
    engine.allocate(90000, method="revenue")
    recs = engine.get_recommendations()
    assert any(r["type"] == "high_indirect" for r in recs)


def test_recommendations_top_performer():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers(_centers())
    engine.allocate(0, method="revenue")
    recs = engine.get_recommendations()
    assert any(r["type"] == "top_performer" for r in recs)


def test_recommendations_healthy_centers_minimal():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "A", "revenue": 100000, "direct_costs": 20000, "headcount": 10},
        {"name": "B", "revenue": 100000, "direct_costs": 20000, "headcount": 10},
    ])
    engine.allocate(20000, method="equal")
    recs = engine.get_recommendations()
    assert len(recs) <= 1


# ============ analyze دفعة واحدة + حشو ============

def test_analyze_one_shot():
    engine = CostCenterProfitabilityEngine()
    result = engine.analyze(_centers(), indirect_total=50000, method="revenue")
    assert "centers" in result
    assert "summary" in result
    assert len(result["centers"]) == 3
    assert result["summary"]["total_revenue"] == 400000
    assert result["centers"][0]["indirect_costs"] > 0


def test_analyze_empty_centers():
    engine = CostCenterProfitabilityEngine()
    result = engine.analyze([], indirect_total=50000, method="revenue")
    assert result["centers"] == []
    assert result["summary"]["center_count"] == 0


def test_analyze_none_centers():
    engine = CostCenterProfitabilityEngine()
    result = engine.analyze(None, indirect_total=50000, method="revenue")
    assert result["centers"] == []


def test_negative_revenue_handled():
    engine = CostCenterProfitabilityEngine()
    engine.define_centers([
        {"name": "A", "revenue": -5000, "direct_costs": 1000},
    ])
    result = engine.allocate(0, method="revenue")
    assert result[0]["profit"] == -6000


def test_set_standards_negative_ignored():
    engine = CostCenterProfitabilityEngine()
    engine.set_standards(-5)
    assert engine.target_margin_pct == 0
