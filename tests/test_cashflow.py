# Unit tests for modules/cashflow.py (CashFlowStatement).

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.cashflow import CashFlowStatement


class TestCashFlowStatement(unittest.TestCase):

    def setUp(self):
        self.statement = CashFlowStatement()

    def test_simplified_estimate_structure(self):
        data = {
            "net_income": 10000,
            "depreciation": 2000,
            "revenue": 200000,
            "total_assets": 500000,
            "total_liabilities": 200000,
            "equity": 300000,
        }
        result = self.statement.calculate(data)
        self.assertEqual(
            sorted(result.keys()),
            sorted(["operating", "investing", "financing", "net_change",
                    "beginning_cash", "ending_cash"]),
        )
        self.assertEqual(result["operating"], 12000)
        self.assertEqual(result["beginning_cash"], 10000)
        self.assertEqual(result["ending_cash"], result["beginning_cash"] + result["net_change"])

    def test_simplified_estimate_missing_keys_default_to_zero(self):
        result = self.statement.calculate({})
        self.assertEqual(result["operating"], 0)
        self.assertEqual(result["investing"], 0)
        self.assertEqual(result["net_change"], 0)

    def test_simplified_estimate_zero_values(self):
        data = {"net_income": 0, "depreciation": 0, "revenue": 0,
                "total_assets": 0, "total_liabilities": 0, "equity": 0}
        result = self.statement.calculate(data)
        self.assertEqual(result["net_change"], 0)
        self.assertEqual(result["ending_cash"], 0)

    def test_full_calculation_uses_previous_data(self):
        current = {
            "net_income": 15000,
            "depreciation": 3000,
            "current_assets": 120000,
            "current_liabilities": 60000,
            "inventory": 25000,
            "total_assets": 550000,
            "total_liabilities": 220000,
            "equity": 330000,
        }
        previous = {
            "net_income": 10000,
            "depreciation": 2000,
            "current_assets": 100000,
            "current_liabilities": 50000,
            "inventory": 20000,
            "total_assets": 500000,
            "total_liabilities": 200000,
            "equity": 300000,
        }
        result = self.statement.calculate(current, previous)
        # delta_ca = +20000, delta_cl = +10000, delta_inventory = +5000
        self.assertEqual(result["operating"], 15000 + 3000 - 20000 + 10000 - 5000)
        self.assertEqual(result["investing"], -(550000 - 500000))
        self.assertEqual(result["financing"], 20000 + 30000)
        self.assertEqual(result["net_change"],
                         result["operating"] + result["investing"] + result["financing"])
        self.assertEqual(result["beginning_cash"], 500000 * 0.05)
        self.assertEqual(result["ending_cash"], result["beginning_cash"] + result["net_change"])

    def test_full_calculation_missing_previous_keys(self):
        current = {"net_income": 1000, "depreciation": 100}
        previous = {}
        result = self.statement.calculate(current, previous)
        self.assertEqual(result["operating"], 1100)
        self.assertEqual(result["net_change"],
                         result["operating"] + result["investing"] + result["financing"])

    def test_generate_report_with_results(self):
        results = {"operating": 100, "investing": -50, "financing": 20,
                   "net_change": 70, "beginning_cash": 30, "ending_cash": 100}
        report = self.statement.generate_report(results)
        self.assertIn("STATEMENT OF CASH FLOWS", report)
        self.assertIn("100.00", report)

    def test_generate_report_without_data(self):
        report = self.statement.generate_report()
        self.assertIn("No cash flow data", report)

    def test_generate_report_reuses_last_results(self):
        results = {"operating": 1, "investing": 2, "financing": 3,
                   "net_change": 6, "beginning_cash": 4, "ending_cash": 10}
        self.statement.generate_report(results)
        report = self.statement.generate_report()
        self.assertIn("STATEMENT OF CASH FLOWS", report)


if __name__ == "__main__":
    unittest.main()
