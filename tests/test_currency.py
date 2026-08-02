# اختبارات محرك تعدد العملات
# =============================

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCurrencyEngine(unittest.TestCase):
    """اختبارات أساسية لمحرك العملات"""

    def setUp(self):
        from modules.currency import CurrencyEngine
        self.engine = CurrencyEngine(base_currency="DZD")
        self.engine.set_rate("USD", 134.0)
        self.engine.set_rate("EUR", 156.0)

    def test_default_currencies_present(self):
        self.assertIn("DZD", self.engine.supported_currencies())
        self.assertIn("USD", self.engine.supported_currencies())

    def test_base_rate_is_one(self):
        self.assertEqual(self.engine.get_rate("DZD"), 1.0)

    def test_convert_simple(self):
        self.assertAlmostEqual(self.engine.convert(100, "USD", "DZD"), 13400.0)
        self.assertAlmostEqual(self.engine.convert(13400, "DZD", "USD"), 100.0)

    def test_convert_cross_currency(self):
        self.assertAlmostEqual(
            self.engine.convert(100, "USD", "EUR"), 100 * 134.0 / 156.0
        )

    def test_convert_same_currency(self):
        self.assertEqual(self.engine.convert(50, "USD", "USD"), 50.0)

    def test_convert_unknown_rate_zero(self):
        self.assertEqual(self.engine.convert(100, "XYZ", "DZD"), 0.0)

    def test_set_rate_invalid(self):
        self.assertFalse(self.engine.set_rate("USD", 0))
        self.assertFalse(self.engine.set_rate("USD", -5))
        self.assertFalse(self.engine.set_rate("USD", "abc"))

    def test_add_currency(self):
        self.assertTrue(self.engine.add_currency("GBP", "جنيه إسترليني", "£", 180.0))
        self.assertEqual(self.engine.get_rate("GBP"), 180.0)

    def test_remove_currency(self):
        self.assertTrue(self.engine.remove_currency("USD"))
        self.assertNotIn("USD", self.engine.supported_currencies())

    def test_cannot_remove_base(self):
        self.assertFalse(self.engine.remove_currency("DZD"))

    def test_set_base_currency(self):
        self.assertTrue(self.engine.set_base_currency("USD"))
        self.assertEqual(self.engine.base_currency, "USD")
        self.assertEqual(self.engine.get_rate("USD"), 1.0)

    def test_format(self):
        self.assertIn("دج", self.engine.format(1000, "DZD"))
        self.assertIn("$", self.engine.format(1000, "USD"))

    def test_to_dict_roundtrip(self):
        data = self.engine.to_dict()
        from modules.currency import CurrencyEngine
        eng2 = CurrencyEngine()
        eng2.load_from_dict(data)
        self.assertEqual(eng2.base_currency, "DZD")
        self.assertAlmostEqual(eng2.get_rate("USD"), 134.0)
        self.assertAlmostEqual(eng2.convert(10, "USD", "DZD"), 1340.0)


class TestCurrencyReport(unittest.TestCase):
    """اختبارات التقرير متعدد العملات"""

    def setUp(self):
        from modules.currency import CurrencyEngine
        self.engine = CurrencyEngine(base_currency="DZD")
        self.engine.set_rate("USD", 134.0)
        self.financial = {
            "revenue": 5000000, "cost_of_goods_sold": 3200000,
            "gross_profit": 1800000, "net_income": 650000,
            "total_assets": 8000000, "total_liabilities": 3200000,
            "total_equity": 4800000, "cash": 300000,
        }

    def test_report_includes_financial_items(self):
        rows = self.engine.report(self.financial)
        items = [r["item"] for r in rows]
        self.assertIn("revenue", items)
        self.assertIn("net_income", items)

    def test_report_converts_to_target(self):
        rows = self.engine.report(self.financial, "USD")
        revenue_row = next(r for r in rows if r["item"] == "revenue")
        self.assertAlmostEqual(revenue_row["converted"], 5000000 / 134.0)

    def test_report_skips_missing_items(self):
        rows = self.engine.report({})
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
