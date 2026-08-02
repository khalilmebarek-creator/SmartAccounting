# Unit tests for modules/breakeven.py, modules/cost_center.py and
# modules/forecasting.py. Focus: uncovered branches (default-value
# fallbacks, error paths, unit breakeven, ranking and recommendations).

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.breakeven import BreakEvenAnalyzer
from modules.cost_center import CostCenterAnalyzer
from modules.forecasting import FinancialForecaster


# ==================== breakeven.py ====================

class TestBreakEvenAnalyzer(unittest.TestCase):
    """Tests for BreakEvenAnalyzer default values, error paths and units."""

    def test_calculate_default_fixed_costs_from_gross_profit(self):
        be = BreakEvenAnalyzer({"revenue": 500000, "gross_profit": 200000, "net_income": 50000})
        result = be.calculate(variable_cost_ratio=0.6)
        self.assertEqual(result["fixed_costs"], 150000.0)

    def test_calculate_default_fixed_costs_percent_of_revenue(self):
        be = BreakEvenAnalyzer({"revenue": 500000, "gross_profit": 0})
        result = be.calculate(variable_cost_ratio=0.6)
        self.assertEqual(result["fixed_costs"], 150000.0)

    def test_calculate_default_vcr_from_cogs(self):
        be = BreakEvenAnalyzer({"revenue": 500000, "cost_of_goods_sold": 300000})
        result = be.calculate(fixed_costs=100000)
        self.assertEqual(result["variable_cost_ratio"], 60.0)
        self.assertEqual(result["contribution_margin_ratio"], 40.0)

    def test_calculate_default_vcr_fallback_without_revenue(self):
        be = BreakEvenAnalyzer({"revenue": 0})
        result = be.calculate(fixed_costs=100000)
        self.assertEqual(result["variable_cost_ratio"], 60.0)

    def test_calculate_negative_contribution_margin(self):
        be = BreakEvenAnalyzer({"revenue": 100000})
        result = be.calculate(fixed_costs=100000, variable_cost_ratio=1.0)
        self.assertEqual(result, {"error": "negative_contribution_margin"})
        result = be.calculate(fixed_costs=100000, variable_cost_ratio=1.5)
        self.assertEqual(result["error"], "negative_contribution_margin")

    def test_calculate_unit_breakeven(self):
        be = BreakEvenAnalyzer({"revenue": 100000})
        result = be.calculate(fixed_costs=100000, variable_cost_ratio=0.5,
                              unit_price=100, unit_variable_cost=40)
        self.assertEqual(result["unit_price"], 100)
        self.assertEqual(result["unit_variable_cost"], 40)
        self.assertEqual(result["unit_contribution"], 60.0)
        self.assertEqual(result["breakeven_units"], 1667)

    def test_calculate_unit_breakeven_non_positive_contribution(self):
        be = BreakEvenAnalyzer({"revenue": 100000})
        result = be.calculate(fixed_costs=100000, variable_cost_ratio=0.5,
                              unit_price=100, unit_variable_cost=150)
        self.assertNotIn("breakeven_units", result)
        self.assertNotIn("unit_contribution", result)

    def test_calculate_unit_breakeven_exact(self):
        be = BreakEvenAnalyzer({"revenue": 100000})
        result = be.calculate(fixed_costs=100000, variable_cost_ratio=0.5,
                              unit_price=50, unit_variable_cost=50)
        self.assertNotIn("breakeven_units", result)

    def test_sensitivity_infinite_breakeven(self):
        be = BreakEvenAnalyzer({"revenue": 100000})
        results = be.sensitivity_analysis(100000, [0.5, 1.0, 1.2], 500000)
        self.assertEqual(len(results), 3)
        self.assertIn("variable_cost_pct", results[0])
        self.assertEqual(results[1]["breakeven"], float("inf"))
        self.assertEqual(results[2]["breakeven"], float("inf"))


# ==================== cost_center.py ====================

class TestCostCenterAnalyzer(unittest.TestCase):
    """Tests for CostCenterAnalyzer ranking and recommendations."""

    CENTERS = [
        {"name": "Production", "costs": 10000, "revenue": 20000, "headcount": 10},
        {"name": "R&D", "costs": 60000, "revenue": 5000, "headcount": 5},
        {"name": "Support", "costs": 0, "revenue": 0, "headcount": 3},
    ]

    def setUp(self):
        self.cc = CostCenterAnalyzer()
        self.cc.define_centers(self.CENTERS)

    def test_rank_by_efficiency(self):
        ranked = self.cc.rank_by_efficiency()
        self.assertEqual(ranked[0]["name"], "Support")
        self.assertEqual(ranked[1]["name"], "Production")
        self.assertEqual(ranked[2]["name"], "R&D")

    def test_rank_by_profitability(self):
        ranked = self.cc.rank_by_profitability()
        self.assertEqual(ranked[0]["name"], "Production")
        self.assertEqual(ranked[1]["name"], "Support")
        self.assertEqual(ranked[-1]["name"], "R&D")

    def test_get_recommendations(self):
        recs = self.cc.get_recommendations()
        types = [r["type"] for r in recs]
        self.assertIn("loss_warning", types)
        self.assertIn("high_cost", types)
        loss = next(r for r in recs if r["type"] == "loss_warning")
        self.assertEqual(loss["center"], "R&D")
        high = next(r for r in recs if r["type"] == "high_cost")
        self.assertEqual(high["center"], "R&D")
        self.assertIn("30%+", high["message"])

    def test_get_recommendations_empty(self):
        cc = CostCenterAnalyzer()
        self.assertEqual(cc.get_recommendations(), [])

    def test_get_summary(self):
        cc = CostCenterAnalyzer()
        cc.define_centers([
            {"name": "A", "costs": 10000, "revenue": 20000, "headcount": 10},
            {"name": "B", "costs": 5000, "revenue": 8000, "headcount": 5},
        ])
        summary = cc.get_summary()
        self.assertEqual(summary["total_costs"], 15000.0)
        self.assertEqual(summary["total_revenue"], 28000.0)
        self.assertEqual(summary["total_profit"], 13000.0)
        self.assertEqual(summary["total_headcount"], 15)
        self.assertEqual(summary["center_count"], 2)
        self.assertAlmostEqual(summary["overall_margin_pct"], 46.43, places=2)

    def test_get_summary_empty(self):
        cc = CostCenterAnalyzer()
        summary = cc.get_summary()
        self.assertEqual(summary["total_costs"], 0.0)
        self.assertEqual(summary["overall_margin_pct"], 0)
        self.assertEqual(summary["center_count"], 0)


# ==================== forecasting.py ====================

class TestFinancialForecaster(unittest.TestCase):
    """Tests for FinancialForecaster income statement projection and cagr."""

    def test_project_income_statement_default_ratios(self):
        data = {"revenue": 100000, "cost_of_goods_sold": 60000,
                "gross_profit": 40000, "net_income": 10000}
        f = FinancialForecaster(data, {})
        proj = f.project_income_statement([0.1])
        self.assertEqual(len(proj), 1)
        p = proj[0]
        self.assertEqual(p["year_offset"], 1)
        self.assertEqual(p["revenue"], 110000.0)
        self.assertEqual(p["cogs"], 66000.0)
        self.assertEqual(p["gross_profit"], 44000.0)
        self.assertEqual(p["opex"], 33000.0)
        self.assertEqual(p["net_income"], 11000.0)
        self.assertEqual(p["npm"], 10.0)

    def test_project_income_statement_explicit_ratios(self):
        f = FinancialForecaster({"revenue": 100000}, {})
        proj = f.project_income_statement([0.1], cogs_pct=0.5, opex_pct=0.2)
        p = proj[0]
        self.assertEqual(p["cogs"], 55000.0)
        self.assertEqual(p["opex"], 22000.0)
        self.assertEqual(p["net_income"], 33000.0)

    def test_project_income_statement_zero_revenue(self):
        f = FinancialForecaster({"revenue": 0}, {})
        result = f.project_income_statement([0.1])
        self.assertEqual(result, {"error": "revenue_zero"})

    def test_project_income_statement_zero_growth_and_loss(self):
        data = {"revenue": 100000, "gross_profit": 1000, "net_income": 5000}
        f = FinancialForecaster(data, {})
        proj = f.project_income_statement([-1.0])
        p = proj[0]
        self.assertEqual(p["revenue"], 0.0)
        self.assertEqual(p["npm"], 0)

    def test_project_income_statement_multiple_years(self):
        data = {"revenue": 100000, "cost_of_goods_sold": 50000,
                "gross_profit": 50000, "net_income": 20000}
        f = FinancialForecaster(data, {})
        proj = f.project_income_statement([0.1, 0.05])
        self.assertEqual(len(proj), 2)
        self.assertEqual(proj[1]["year_offset"], 2)
        self.assertAlmostEqual(proj[1]["revenue"], 115500.0)

    def test_scenario_analysis_error_on_zero_revenue(self):
        f = FinancialForecaster({"revenue": 0}, {})
        results = f.scenario_analysis({"pessimistic": -0.2, "base": 0.1})
        self.assertEqual(results["pessimistic"]["error"], "revenue_zero")
        self.assertEqual(results["base"]["error"], "revenue_zero")

    def test_scenario_analysis_success(self):
        data = {"revenue": 100000, "net_income": 10000}
        f = FinancialForecaster(data, {})
        results = f.scenario_analysis({"optimistic": 0.2})
        r = results["optimistic"]
        self.assertEqual(r["growth_rate"], 0.2)
        self.assertEqual(r["projected_revenue"], 120000.0)
        self.assertEqual(r["projected_net_income"], 12000.0)
        self.assertEqual(r["revenue_change"], 20000.0)

    def test_cagr_invalid_inputs_return_zero(self):
        f = FinancialForecaster({}, {})
        self.assertEqual(f.cagr(0, 100, 2), 0)
        self.assertEqual(f.cagr(100, 0, 2), 0)
        self.assertEqual(f.cagr(100, 200, 0), 0)
        self.assertEqual(f.cagr(100, 200, -1), 0)
        self.assertEqual(f.cagr(-50, 200, 2), 0)

    def test_cagr_valid_input(self):
        f = FinancialForecaster({}, {})
        self.assertEqual(f.cagr(100000, 133100, 3), 10.0)


if __name__ == "__main__":
    unittest.main()
