# اختبارات AppState
# =================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.app_state import AppState


class TestAppState(unittest.TestCase):
    """اختبارات إدارة الحالة المشتركة"""

    def setUp(self):
        self.state = AppState()

    def test_initial_state_empty(self):
        """الحالة الافتراضية فارغة"""
        self.assertEqual(self.state.company_name, "")
        self.assertEqual(self.state.financial_data, {})
        self.assertEqual(self.state.ratios, {})
        self.assertEqual(self.state.dupont, {})
        self.assertEqual(self.state.working_capital, {})
        self.assertIsNone(self.state.audit_result)

    def test_has_data_empty(self):
        """has_data يرجع False لو لا توجد نسب"""
        self.assertFalse(self.state.has_data())

    def test_has_data_with_ratios(self):
        """has_data يرجع True لو في نسب"""
        self.state.ratios = {'roe': 5.0}
        self.assertTrue(self.state.has_data())

    def test_clear(self):
        """clear يمسح كل البيانات"""
        self.state.company_name = "test"
        self.state.financial_data = {'revenue': 100}
        self.state.ratios = {'roe': 5.0}
        self.state.dupont = {'net_profit_margin': 7.5}
        self.state.working_capital = {'working_capital': 50000}
        self.state.audit_result = "some result"

        self.state.clear()

        self.assertEqual(self.state.company_name, "")
        self.assertEqual(self.state.financial_data, {})
        self.assertEqual(self.state.ratios, {})
        self.assertEqual(self.state.dupont, {})
        self.assertEqual(self.state.working_capital, {})
        self.assertIsNone(self.state.audit_result)

    def test_summary_empty(self):
        """summary يرجع رسالة لو لا توجد بيانات"""
        result = self.state.summary()
        self.assertIn("لا توجد", result)

    def test_summary_with_data(self):
        """summary يرجع معلومات صحيحة"""
        self.state.company_name = "شركة اختبار"
        self.state.fiscal_year = 2024
        self.state.ratios = {'roe': 12.5, 'current_ratio': 2.0}
        result = self.state.summary()
        self.assertIn("شركة اختبار", result)
        self.assertIn("2024", result)
        self.assertIn("12.50", result)
        self.assertIn("2.00", result)

    def test_fiscal_year_default(self):
        """السنة المالية الافتراضية 2024"""
        self.assertEqual(self.state.fiscal_year, 2024)


if __name__ == '__main__':
    unittest.main()
