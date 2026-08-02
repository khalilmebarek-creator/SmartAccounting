# Unit tests for modules/comparative.py (ComparativeAnalyzer).

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.comparative import ComparativeAnalyzer


def sample_data():
    return {
        2023: {
            "revenue": 200000, "gross_profit": 80000, "net_income": 20000,
            "total_assets": 500000, "total_liabilities": 200000, "equity": 300000,
            "current_assets": 100000, "current_liabilities": 50000,
            "inventory": 20000, "cost_of_goods_sold": 120000,
            "operating_expenses": 50000,
        },
        2024: {
            "revenue": 240000, "gross_profit": 96000, "net_income": 26000,
            "total_assets": 550000, "total_liabilities": 220000, "equity": 330000,
            "current_assets": 120000, "current_liabilities": 60000,
            "inventory": 25000, "cost_of_goods_sold": 144000,
            "operating_expenses": 60000,
        },
    }


class TestComparativeAnalyzer(unittest.TestCase):

    def test_init_sorts_years(self):
        data = sample_data()
        data = {2024: data[2024], 2023: data[2023]}
        analyzer = ComparativeAnalyzer(data)
        self.assertEqual(list(analyzer.financial_data_by_year.keys()), [2023, 2024])

    def test_yoy_change_normal(self):
        analyzer = ComparativeAnalyzer(sample_data())
        change = analyzer._yoy_change(240000, 200000)
        self.assertEqual(change["absolute"], 40000)
        self.assertEqual(change["percentage"], 20.0)

    def test_yoy_change_zero_previous(self):
        analyzer = ComparativeAnalyzer(sample_data())
        change = analyzer._yoy_change(100, 0)
        self.assertEqual(change, {"absolute": 0, "percentage": 0})

    def test_yoy_change_negative_previous(self):
        analyzer = ComparativeAnalyzer(sample_data())
        change = analyzer._yoy_change(50, -50)
        self.assertEqual(change["absolute"], 100)
        self.assertEqual(change["percentage"], 200.0)

    def test_get_comparison_structure(self):
        analyzer = ComparativeAnalyzer(sample_data())
        result = analyzer.get_comparison()
        self.assertEqual(result["years"], [2023, 2024])
        self.assertIn("ratios_by_year", result)
        self.assertIn("item_changes", result)
        self.assertIn("ratio_changes", result)
        self.assertIn("revenue", result["item_changes"])
        self.assertIn("2023-2024", result["item_changes"]["revenue"])

    def test_get_comparison_missing_item_values(self):
        data = {
            2023: {"revenue": 1000, "net_income": 100},
            2024: {"revenue": 2000, "net_income": 200},
        }
        analyzer = ComparativeAnalyzer(data)
        result = analyzer.get_comparison()
        # Missing equity/total_assets default to 0 instead of crashing.
        self.assertIn("equity", result["item_changes"])
        self.assertEqual(result["item_changes"]["equity"]["2023-2024"]["previous"], 0)

    def test_get_comparison_none_item_values(self):
        data = {
            2023: {"revenue": 1000, "net_income": 100, "equity": None},
            2024: {"revenue": 2000, "net_income": 200, "equity": 300},
        }
        analyzer = ComparativeAnalyzer(data)
        result = analyzer.get_comparison()
        self.assertEqual(result["item_changes"]["equity"]["2023-2024"]["previous"], 0)

    def test_single_year_returns_empty_changes(self):
        data = {2023: sample_data()[2023]}
        analyzer = ComparativeAnalyzer(data)
        result = analyzer.get_comparison()
        self.assertEqual(result["years"], [2023])
        self.assertEqual(result["item_changes"]["revenue"], {})
        self.assertEqual(result["ratio_changes"]["roe"], {})

    def test_generate_report_sections(self):
        analyzer = ComparativeAnalyzer(sample_data())
        report = analyzer.generate_report()
        self.assertIn("COMPARATIVE FINANCIAL ANALYSIS REPORT", report)
        self.assertIn("SECTION 1", report)
        self.assertIn("SECTION 2", report)
        self.assertIn("SECTION 3", report)
        self.assertIn("SECTION 4", report)
        self.assertIn("END OF REPORT", report)

    def test_generate_report_single_year(self):
        data = {2023: sample_data()[2023]}
        analyzer = ComparativeAnalyzer(data)
        report = analyzer.generate_report()
        self.assertIn("Years: 2023", report)


if __name__ == "__main__":
    unittest.main()
