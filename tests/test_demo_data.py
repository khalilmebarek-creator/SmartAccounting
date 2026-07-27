# اختبارات البيانات التجريبية
# ==============================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.demo_data import DemoData, DEMO_DATA
from modules.calculations import CalculationEngine


class TestDemoData(unittest.TestCase):
    """اختبارات البيانات التجريبية"""

    def test_get_data_returns_dict(self):
        data = DemoData.get_data()
        self.assertIsInstance(data, dict)

    def test_get_data_has_required_keys(self):
        data = DemoData.get_data()
        for key in ["company_name", "fiscal_year", "financial_data", "tax_summary"]:
            self.assertIn(key, data)

    def test_get_financial_data(self):
        fd = DemoData.get_financial_data()
        self.assertIsInstance(fd, dict)
        self.assertIn("revenue", fd)
        self.assertIn("total_assets", fd)

    def test_get_company_name(self):
        name = DemoData.get_company_name()
        self.assertIsInstance(name, str)
        self.assertTrue(len(name) > 0)

    def test_financial_data_consistency(self):
        fd = DemoData.get_financial_data()
        self.assertGreater(fd["revenue"], 0)
        self.assertGreater(fd["total_assets"], 0)
        self.assertGreater(fd["equity"], 0)
        self.assertEqual(fd["total_assets"], fd["current_assets"] + fd["non_current_assets"])

    def test_balance_sheet_equation(self):
        fd = DemoData.get_financial_data()
        self.assertAlmostEqual(
            fd["total_assets"],
            fd["total_liabilities"] + fd["equity"],
            places=0
        )

    def test_gross_profit_consistency(self):
        fd = DemoData.get_financial_data()
        expected_gp = fd["revenue"] - fd["cost_of_goods_sold"]
        self.assertEqual(fd["gross_profit"], expected_gp)

    def test_calculation_engine_with_demo_data(self):
        fd = DemoData.get_financial_data()
        engine = CalculationEngine(fd)
        ratios = engine.calculate_all_ratios(fd)
        self.assertIsNotNone(ratios)
        self.assertIn("current_ratio", ratios)
        self.assertIn("roe", ratios)

    def test_tax_summary_structure(self):
        ts = DEMO_DATA["tax_summary"]
        self.assertIn("total_taxes", ts)
        self.assertIn("ibs", ts)
        self.assertIn("tax_burden_pct", ts)
        self.assertGreater(ts["total_taxes"], 0)

    def test_get_data_returns_copy(self):
        data1 = DemoData.get_data()
        data2 = DemoData.get_data()
        self.assertEqual(data1, data2)
        data1["company_name"] = "MODIFIED"
        self.assertNotEqual(data1["company_name"], data2["company_name"])


if __name__ == "__main__":
    unittest.main()
