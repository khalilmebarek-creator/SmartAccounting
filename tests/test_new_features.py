# اختبارات الميزات الجديدة
# ========================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestForecasting(unittest.TestCase):
    """اختبارات التنبؤ المالي"""

    def test_project_revenue(self):
        from modules.forecasting import FinancialForecaster
        data = {"revenue": 100000}
        f = FinancialForecaster(data, {})
        result = f.project_revenue([0.1, 0.1, 0.1])
        self.assertEqual(len(result["projections"]), 3)
        self.assertAlmostEqual(result["projections"][0]["projected_revenue"], 110000)
        self.assertAlmostEqual(result["projections"][2]["projected_revenue"], 133100)

    def test_project_revenue_zero(self):
        from modules.forecasting import FinancialForecaster
        f = FinancialForecaster({"revenue": 0}, {})
        result = f.project_revenue([0.1])
        self.assertIn("error", result)

    def test_scenario_analysis(self):
        from modules.forecasting import FinancialForecaster
        data = {"revenue": 100000, "net_income": 10000}
        f = FinancialForecaster(data, {})
        result = f.scenario_analysis({"optimistic": 0.2, "base": 0.1, "pessimistic": 0.05})
        self.assertIn("optimistic", result)
        self.assertIn("base", result)

    def test_cagr(self):
        from modules.forecasting import FinancialForecaster
        f = FinancialForecaster({}, {})
        cagr = f.cagr(100000, 150000, 3)
        self.assertGreater(cagr, 14)
        self.assertLess(cagr, 15)


class TestBudget(unittest.TestCase):
    """اختبارات الموازنة"""

    def test_create_budget(self):
        from modules.budget import BudgetPlanner
        data = {"revenue": 500000, "cost_of_goods_sold": 300000}
        bp = BudgetPlanner(data)
        items = bp.create_annual_budget({
            "revenue": {"budgeted": 500000},
            "cost_of_goods_sold": {"budgeted": 280000},
        })
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["budgeted"], 500000)
        self.assertEqual(items[0]["actual"], 500000)
        self.assertEqual(items[0]["variance"], 0)

    def test_budget_summary(self):
        from modules.budget import BudgetPlanner
        data = {"revenue": 500000}
        bp = BudgetPlanner(data)
        bp.create_annual_budget({"revenue": {"budgeted": 500000}})
        summary = bp.get_summary()
        self.assertEqual(summary["total_budgeted"], 500000)
        self.assertEqual(summary["utilization_pct"], 100)

    def test_budget_alerts(self):
        from modules.budget import BudgetPlanner
        data = {"cost_of_goods_sold": 300000}
        bp = BudgetPlanner(data)
        bp.create_annual_budget({"cost_of_goods_sold": {"budgeted": 200000}})
        alerts = bp.get_alerts(threshold_pct=10)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], "high")


class TestCostCenter(unittest.TestCase):
    """اختبارات مراكز التكلفة"""

    def test_define_centers(self):
        from modules.cost_center import CostCenterAnalyzer
        cc = CostCenterAnalyzer()
        centers = cc.define_centers([
            {"name": "Production", "costs": 120000, "revenue": 200000, "headcount": 15},
            {"name": "Sales", "costs": 30000, "revenue": 80000, "headcount": 5},
        ])
        self.assertEqual(len(centers), 2)
        self.assertGreater(centers[0]["profit"], 0)

    def test_summary(self):
        from modules.cost_center import CostCenterAnalyzer
        cc = CostCenterAnalyzer()
        cc.define_centers([
            {"name": "A", "costs": 100000, "revenue": 150000, "headcount": 10},
        ])
        summary = cc.get_summary()
        self.assertEqual(summary["total_costs"], 100000)
        self.assertEqual(summary["total_profit"], 50000)


class TestBreakEven(unittest.TestCase):
    """اختبارات تحليل التعادل"""

    def test_calculate(self):
        from modules.breakeven import BreakEvenAnalyzer
        data = {"revenue": 500000, "cost_of_goods_sold": 300000, "gross_profit": 200000, "net_income": 50000}
        be = BreakEvenAnalyzer(data)
        result = be.calculate(fixed_costs=100000, variable_cost_ratio=0.6)
        self.assertFalse("error" in result)
        self.assertEqual(result["breakeven_revenue"], 250000)
        self.assertTrue(result["is_profitable"])

    def test_not_profitable(self):
        from modules.breakeven import BreakEvenAnalyzer
        data = {"revenue": 200000, "cost_of_goods_sold": 180000, "gross_profit": 20000, "net_income": 5000}
        be = BreakEvenAnalyzer(data)
        result = be.calculate(fixed_costs=100000, variable_cost_ratio=0.6)
        self.assertFalse(result["is_profitable"])

    def test_sensitivity(self):
        from modules.breakeven import BreakEvenAnalyzer
        be = BreakEvenAnalyzer({"revenue": 500000})
        results = be.sensitivity_analysis(100000, [0.4, 0.5, 0.6, 0.7], 500000)
        self.assertEqual(len(results), 4)


if __name__ == "__main__":
    unittest.main()
