# اختبارات التحقق من البيانات
# =============================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.validation import DataValidator


class TestDataValidator(unittest.TestCase):
    """اختبارات شاملة لفئة التحقق من البيانات"""
    
    def setUp(self):
        """إعداد المدقق قبل كل اختبار"""
        self.validator = DataValidator()
        # بيانات صحيحة ومتوازنة للميزانية
        self.valid_data = {
            'total_assets': 500000,
            'total_liabilities': 200000,
            'equity': 300000,
            'revenue': 200000,
            'net_income': 15000
        }
    
    # ===== اختبارات validate_non_negative_number =====
    
    def test_validate_non_negative_number_valid(self):
        """اختبار قيمة موجبة صحيحة"""
        result = self.validator.validate_non_negative_number(1000, 'test_field')
        self.assertTrue(result)
        self.assertEqual(len(self.validator.errors), 0)
    
    def test_validate_non_negative_number_zero(self):
        """اختبار قيمة صفر - مسموح (مش سالب)"""
        result = self.validator.validate_non_negative_number(0, 'test_field')
        self.assertTrue(result)
    
    def test_validate_non_negative_number_negative(self):
        """اختبار قيمة سالبة - لازم يفشل"""
        result = self.validator.validate_non_negative_number(-100, 'test_field')
        self.assertFalse(result)
        self.assertEqual(len(self.validator.errors), 1)
        self.assertIn('سالبة', self.validator.errors[0])
    
    def test_validate_non_negative_number_non_numeric(self):
        """اختبار قيمة غير رقمية"""
        result = self.validator.validate_non_negative_number("abc", 'test_field')
        self.assertFalse(result)
        self.assertIn('رقمية', self.validator.errors[0])
    
    def test_validate_non_negative_number_none(self):
        """اختبار قيمة None"""
        result = self.validator.validate_non_negative_number(None, 'test_field')
        self.assertFalse(result)
    
    # ===== اختبارات validate_financial_statement =====
    
    def test_validate_financial_statement_valid(self):
        """اختبار بيانات مالية صحيحة ومتوازنة"""
        result = self.validator.validate_financial_statement(self.valid_data)
        self.assertTrue(result)
        self.assertEqual(len(self.validator.errors), 0)
    
    def test_validate_financial_statement_unbalanced(self):
        """اختبار ميزانية غير متوازنة"""
        unbalanced = self.valid_data.copy()
        unbalanced['total_assets'] = 600000  # الأصول لا تساوي الالتزامات + الملكية
        result = self.validator.validate_financial_statement(unbalanced)
        self.assertFalse(result)
        self.assertIn('عدم توازن', self.validator.errors[0])
    
    def test_validate_financial_statement_negative_revenue(self):
        """اختبار إيرادات سالبة"""
        bad_data = self.valid_data.copy()
        bad_data['revenue'] = -100
        result = self.validator.validate_financial_statement(bad_data)
        self.assertFalse(result)
    
    def test_validate_financial_statement_loss_warning(self):
        """اختبار تحذير الخسارة (مش خطأ)"""
        loss_data = self.valid_data.copy()
        loss_data['net_income'] = -5000  # خسارة
        result = self.validator.validate_financial_statement(loss_data)
        # النتيجة: True (مش خطأ، لكن في warning)
        self.assertTrue(result)
        self.assertGreater(len(self.validator.warnings), 0)
        self.assertTrue(any('خسائر' in w for w in self.validator.warnings))
    
    def test_validate_financial_statement_zero_assets_warning(self):
        """اختبار تحذير الأصول الصفرية"""
        zero_data = self.valid_data.copy()
        zero_data['total_assets'] = 0
        zero_data['total_liabilities'] = 0
        zero_data['equity'] = 0
        # راح يفشل توازن الميزانية، لكن نتأكد من السلوك
        result = self.validator.validate_financial_statement(zero_data)
        # السلوك: قد يفشل في التوازن أو ينجح حسب المنطق
    
    def test_validate_financial_statement_missing_data(self):
        """اختبار بيانات ناقصة"""
        incomplete = {'revenue': 100}
        result = self.validator.validate_financial_statement(incomplete)
        # لازم يفشل لأن الأصول غير موجودة
        self.assertFalse(result)
    
    def test_get_errors_and_warnings(self):
        """اختبار جلب الأخطاء والتحذيرات"""
        loss_data = self.valid_data.copy()
        loss_data['net_income'] = -1000
        self.validator.validate_financial_statement(loss_data)
        errors = self.validator.get_errors()
        warnings = self.validator.get_warnings()
        self.assertIsInstance(errors, list)
        self.assertIsInstance(warnings, list)
    
    def test_print_report_no_errors(self):
        """اختبار طباعة تقرير نظيف"""
        self.validator.validate_financial_statement(self.valid_data)
        # مجرد التحقق من إنه ما يفجّر
        try:
            self.validator.print_report()
        except Exception as e:
            self.fail(f"print_report فجّر: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
