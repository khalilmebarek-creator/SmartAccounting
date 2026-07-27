# اختبارات Utils - Formatters
# ===========================

import unittest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.formatters import NumberFormatter, DateFormatter


class TestNumberFormatter(unittest.TestCase):
    """اختبارات تنسيق الأرقام"""

    def test_format_currency_normal(self):
        result = NumberFormatter.format_currency(1234567.89)
        self.assertIn("1,234,567.89", result)
        self.assertIn("ر.س", result)

    def test_format_currency_none(self):
        self.assertEqual(NumberFormatter.format_currency(None), "--")

    def test_format_currency_custom_currency(self):
        result = NumberFormatter.format_currency(100, currency="USD")
        self.assertIn("USD", result)

    def test_format_percentage_normal(self):
        result = NumberFormatter.format_percentage(15.5)
        self.assertEqual(result, "15.50%")

    def test_format_percentage_none(self):
        self.assertEqual(NumberFormatter.format_percentage(None), "--")

    def test_format_percentage_zero(self):
        result = NumberFormatter.format_percentage(0)
        self.assertEqual(result, "0.00%")

    def test_format_ratio_normal(self):
        result = NumberFormatter.format_ratio(1.2345)
        self.assertEqual(result, "1.2345")

    def test_format_ratio_none(self):
        self.assertEqual(NumberFormatter.format_ratio(None), "--")

    def test_format_large_number_billions(self):
        result = NumberFormatter.format_large_number(1_500_000_000)
        self.assertEqual(result, "1.5B")

    def test_format_large_number_millions(self):
        result = NumberFormatter.format_large_number(2_500_000)
        self.assertEqual(result, "2.5M")

    def test_format_large_number_thousands(self):
        result = NumberFormatter.format_large_number(75_000)
        self.assertEqual(result, "75.0K")

    def test_format_large_number_small(self):
        result = NumberFormatter.format_large_number(42)
        self.assertEqual(result, "42.0")

    def test_format_large_number_negative(self):
        result = NumberFormatter.format_large_number(-3_000_000)
        self.assertEqual(result, "-3.0M")

    def test_format_large_number_none(self):
        self.assertEqual(NumberFormatter.format_large_number(None), "--")

    def test_format_days(self):
        result = NumberFormatter.format_days(45)
        self.assertEqual(result, "45 يوم")

    def test_format_days_none(self):
        self.assertEqual(NumberFormatter.format_days(None), "--")


class TestDateFormatter(unittest.TestCase):
    """اختبارات تنسيق التواريخ"""

    def test_format_datetime_default(self):
        result = DateFormatter.format_datetime()
        self.assertIn("-", result)

    def test_format_datetime_specific(self):
        dt = datetime(2024, 6, 15, 10, 30)
        result = DateFormatter.format_datetime(dt, "%Y-%m-%d %H:%M")
        self.assertEqual(result, "2024-06-15 10:30")

    def test_format_datetime_string_passthrough(self):
        result = DateFormatter.format_datetime("2024-01-01")
        self.assertEqual(result, "2024-01-01")

    def test_format_date_default(self):
        result = DateFormatter.format_date()
        self.assertIn("-", result)

    def test_format_date_specific(self):
        dt = datetime(2024, 12, 25)
        result = DateFormatter.format_date(dt, "%Y/%m/%d")
        self.assertEqual(result, "2024/12/25")

    def test_get_fiscal_year_label(self):
        result = DateFormatter.get_fiscal_year_label(2024)
        self.assertEqual(result, "FY 2024/2025")


if __name__ == '__main__':
    unittest.main()
