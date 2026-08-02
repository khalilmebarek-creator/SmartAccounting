# Supplemental unit tests filling the remaining coverage gaps in:
#   modules/budget.py, modules/validation.py,
#   modules/advanced_dashboard.py, modules/cost_center_profitability.py
# Style matches tests/test_cashflow.py / tests/test_edge_errors.py.

import contextlib
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.budget import BudgetPlanner
from modules.validation import DataValidator
from modules.advanced_dashboard import AdvancedDashboardEngine
from modules.cost_center_profitability import CostCenterProfitabilityEngine


# ==================== budget.py ====================

class TestBudgetPlannerGaps(unittest.TestCase):

    def test_variance_analysis_categories(self):
        planner = BudgetPlanner({
            "revenue": 500000,
            "cogs": 200000,
            "marketing": 100000,
        })
        planner.create_annual_budget({
            "revenue": {"budgeted": 400000},
            "cogs": {"budgeted": 300000},
            "marketing": {"budgeted": 100000},
        })
        result = planner.variance_analysis()
        self.assertEqual(
            [i["category"] for i in result["favorable"]], ["cogs"]
        )
        self.assertEqual(
            [i["category"] for i in result["unfavorable"]], ["revenue"]
        )
        self.assertEqual(
            [i["category"] for i in result["on_track"]], ["marketing"]
        )
        self.assertEqual(result["favorable_count"], 1)
        self.assertEqual(result["unfavorable_count"], 1)

    def test_variance_analysis_empty(self):
        planner = BudgetPlanner()
        result = planner.variance_analysis()
        self.assertEqual(result["favorable"], [])
        self.assertEqual(result["unfavorable"], [])
        self.assertEqual(result["on_track"], [])
        self.assertEqual(result["favorable_count"], 0)

    def test_get_alerts_medium_severity_and_zero_budget_skip(self):
        planner = BudgetPlanner({"a": 115, "b": 0, "c": 0})
        planner.create_annual_budget({
            "a": {"budgeted": 100},
            "b": {"budgeted": 0},
            "c": {"budgeted": 100},
        })
        alerts = planner.get_alerts(threshold_pct=10)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["category"], "a")
        self.assertEqual(alerts[0]["severity"], "medium")
        self.assertEqual(alerts[0]["pct_over"], 15)

    def test_get_alerts_high_severity(self):
        planner = BudgetPlanner({"x": 130})
        planner.create_annual_budget({"x": {"budgeted": 100}})
        alerts = planner.get_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "high")

    def test_get_summary_empty_planner(self):
        planner = BudgetPlanner()
        summary = planner.get_summary()
        self.assertEqual(summary["total_budgeted"], 0)
        self.assertEqual(summary["total_actual"], 0)
        self.assertEqual(summary["utilization_pct"], 0)
        self.assertEqual(summary["item_count"], 0)

    def test_export_json(self):
        planner = BudgetPlanner({"revenue": 500000})
        planner.create_annual_budget({"revenue": {"budgeted": 400000}})
        text = planner.export_json()
        data = json.loads(text)
        self.assertEqual(len(data["items"]), 1)
        self.assertIn("summary", data)
        self.assertIn("alerts", data)
        self.assertEqual(data["summary"]["total_budgeted"], 400000)


# ==================== validation.py ====================

class TestDataValidatorGaps(unittest.TestCase):

    def test_financial_statement_negative_liabilities(self):
        validator = DataValidator()
        result = validator.validate_financial_statement({
            "total_assets": 100,
            "total_liabilities": -5,
            "equity": 105,
            "revenue": 10,
        })
        self.assertFalse(result)
        self.assertTrue(any("الالتزامات" in e for e in validator.errors))

    def test_financial_statement_negative_equity(self):
        validator = DataValidator()
        result = validator.validate_financial_statement({
            "total_assets": 100,
            "total_liabilities": 110,
            "equity": -10,
            "revenue": 10,
        })
        self.assertFalse(result)
        self.assertTrue(any("حقوق المالكين" in e for e in validator.errors))

    def test_financial_statement_invalid_net_income(self):
        validator = DataValidator()
        result = validator.validate_financial_statement({
            "total_assets": 100,
            "total_liabilities": 40,
            "equity": 60,
            "revenue": 50,
            "net_income": "abc",
        })
        self.assertFalse(result)
        self.assertTrue(any("صافي الربح" in e for e in validator.errors))

    def test_print_report_with_errors(self):
        validator = DataValidator()
        validator.validate_financial_statement({
            "total_assets": 100,
            "total_liabilities": 40,
            "equity": 50,
            "revenue": 10,
        })
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            validator.print_report()
        self.assertIn("الأخطاء", buffer.getvalue())

    def test_print_report_with_warnings(self):
        validator = DataValidator()
        validator.validate_financial_statement({
            "total_assets": 100,
            "total_liabilities": 40,
            "equity": 60,
            "revenue": 50,
            "net_income": -5,
        })
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            validator.print_report()
        self.assertIn("التحذيرات", buffer.getvalue())


# ==================== advanced_dashboard.py ====================

class TestAdvancedDashboardGaps(unittest.TestCase):

    def setUp(self):
        self.engine = AdvancedDashboardEngine()

    def test_safe_div_zero_or_none(self):
        self.assertEqual(self.engine._safe_div(10, 0), 0)
        self.assertEqual(self.engine._safe_div(10, None), 0)

    def test_safe_div_type_error(self):
        self.assertEqual(self.engine._safe_div("x", 5), 0)
        self.assertEqual(self.engine._safe_div(10, "y"), 0)

    def test_kpi_status_zero(self):
        self.assertEqual(self.engine._kpi_status("revenue", 0), "yellow")
        self.assertEqual(self.engine._kpi_status("net_profit", 0), "yellow")

    def test_kpi_status_negative(self):
        self.assertEqual(self.engine._kpi_status("revenue", -1), "red")
        self.assertEqual(self.engine._kpi_status("net_profit", -5), "red")

    def test_kpi_status_positive(self):
        self.assertEqual(self.engine._kpi_status("revenue", 1), "green")
        self.assertEqual(self.engine._kpi_status("net_profit", 1), "green")

    def test_compute_kpis_zero_current_liabilities(self):
        kpis = self.engine.compute_kpis(
            {"current_assets": 100, "current_liabilities": 0}, {}
        )
        liquidity = next(k for k in kpis if k["key"] == "liquidity")
        self.assertEqual(liquidity["value"], 0)

    def test_expense_breakdown_derives_cogs_and_opex(self):
        result = self.engine.expense_breakdown(
            {"revenue": 100, "gross_profit": 40, "net_income": 10}
        )
        self.assertEqual(result["values"], [60.0, 30.0, 10.0])

    def test_performance_alerts_net_loss(self):
        alerts = self.engine._performance_alerts({"net_income": -5}, {})
        self.assertTrue(any(
            a["key"] == "net_income" and a["severity"] == "critical"
            for a in alerts
        ))

    def test_performance_alerts_high_debt_to_equity(self):
        alerts = self.engine._performance_alerts(
            {"net_income": 5}, {"debt_to_equity": 3.0}
        )
        self.assertTrue(any(a["key"] == "debt_to_equity" for a in alerts))

    def test_health_score_empty(self):
        result = self.engine.health_score([])
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["rating_en"], "N/A")

    def test_health_score_excellent(self):
        result = self.engine.health_score([{"status": "green"}] * 6)
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["rating_en"], "Excellent")

    def test_health_score_good(self):
        result = self.engine.health_score([{"status": "yellow"}])
        self.assertEqual(result["score"], 60.0)
        self.assertEqual(result["rating_en"], "Good")

    def test_health_score_poor(self):
        result = self.engine.health_score([{"status": "red"}])
        self.assertEqual(result["score"], 20.0)
        self.assertEqual(result["rating_en"], "Poor")

    def test_health_score_unknown_status(self):
        result = self.engine.health_score([{"status": "weird"}])
        self.assertEqual(result["score"], 60.0)
        self.assertEqual(result["rating_en"], "Good")


# ==================== cost_center_profitability.py ====================

class TestCostCenterProfitabilityGaps(unittest.TestCase):

    def test_allocate_invalid_type_defaults_department(self):
        engine = CostCenterProfitabilityEngine()
        engine.define_centers([
            {"name": "X", "type": "mystery", "revenue": 100, "direct_costs": 10}
        ])
        result = engine.allocate(0)
        self.assertEqual(result[0]["type"], "department")

    def test_compare_previous_unmatched_center_skipped(self):
        engine = CostCenterProfitabilityEngine()
        engine.define_centers([{"name": "A", "revenue": 100, "direct_costs": 40}])
        engine.allocate(0)
        rows = engine.compare_previous([{"name": "Z", "revenue": 50, "costs": 20}])
        self.assertEqual(rows, [])

    def test_compare_budget_unmatched_center_skipped(self):
        engine = CostCenterProfitabilityEngine()
        engine.define_centers([{"name": "A", "revenue": 100, "direct_costs": 40}])
        engine.allocate(0)
        rows = engine.compare_budget([{"name": "Z", "revenue": 50, "costs": 20}])
        self.assertEqual(rows, [])

    def test_compare_standards_zero_revenue_below(self):
        engine = CostCenterProfitabilityEngine()
        engine.set_standards(10)
        engine.define_centers([{"name": "Admin", "revenue": 0, "direct_costs": 100}])
        engine.allocate(0)
        rows = engine.compare_standards()
        self.assertEqual(rows[0]["status"], "below")

    def test_compare_standards_zero_revenue_meets(self):
        engine = CostCenterProfitabilityEngine()
        engine.set_standards(0)
        engine.define_centers([{"name": "Admin", "revenue": 0, "direct_costs": 100}])
        engine.allocate(0)
        rows = engine.compare_standards()
        self.assertEqual(rows[0]["status"], "meets")

    def test_get_recommendations_empty(self):
        engine = CostCenterProfitabilityEngine()
        self.assertEqual(engine.get_recommendations(), [])

    def test_recommendations_low_margin(self):
        engine = CostCenterProfitabilityEngine()
        engine.set_standards(50)
        engine.define_centers([{"name": "M", "revenue": 100, "direct_costs": 60}])
        engine.allocate(0)
        recs = engine.get_recommendations()
        self.assertTrue(any(r["type"] == "low_margin" for r in recs))

    def test_recommendations_high_cost_per_head(self):
        engine = CostCenterProfitabilityEngine()
        engine.define_centers([
            {"name": "A", "revenue": 100000, "direct_costs": 1000, "headcount": 10},
            {"name": "B", "revenue": 100000, "direct_costs": 5000, "headcount": 10},
        ])
        engine.allocate(0)
        recs = engine.get_recommendations()
        self.assertTrue(any(
            r["type"] == "high_cost_per_head" and r["center"] == "B"
            for r in recs
        ))

    def test_analyze_with_target_margin(self):
        engine = CostCenterProfitabilityEngine()
        result = engine.analyze(
            [{"name": "A", "revenue": 100, "direct_costs": 40}],
            target_margin_pct=30,
        )
        self.assertEqual(engine.target_margin_pct, 30)
        self.assertEqual(result["summary"]["center_count"], 1)
        self.assertEqual(result["summary"]["best_center"], "A")


if __name__ == "__main__":
    unittest.main()
