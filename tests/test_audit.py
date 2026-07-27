# اختبارات التدقيق والمراجعة
# =============================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.audit import AuditEngine


class TestAuditEngine(unittest.TestCase):
    """اختبارات شاملة لمحرك التدقيق"""
    
    def setUp(self):
        """إعداد المدقق قبل كل اختبار"""
        self.auditor = AuditEngine()
    
    # ===== اختبارات check_balance_sheet =====
    
    def test_check_balance_sheet_balanced(self):
        """اختبار ميزانية متوازنة"""
        result = self.auditor.check_balance_sheet(500000, 200000, 300000)
        self.assertTrue(result)
        self.assertEqual(len(self.auditor.issues), 0)
        self.assertGreater(len(self.auditor.notes), 0)
    
    def test_check_balance_sheet_unbalanced(self):
        """اختبار ميزانية غير متوازنة"""
        result = self.auditor.check_balance_sheet(600000, 200000, 300000)
        self.assertFalse(result)
        self.assertGreater(len(self.auditor.issues), 0)
        self.assertEqual(self.auditor.issues[0]['severity'], 'حرج')
    
    # ===== اختبارات check_income_statement =====
    
    def test_check_income_statement_valid(self):
        """اختبار قائمة دخل صحيحة"""
        # revenue - cogs - expenses = net_income
        # 200000 - 120000 - 65000 = 15000
        result = self.auditor.check_income_statement(200000, 120000, 65000, 15000)
        self.assertTrue(result)
    
    def test_check_income_statement_invalid(self):
        """اختبار قائمة دخل غير صحيحة"""
        result = self.auditor.check_income_statement(200000, 120000, 65000, 20000)
        self.assertFalse(result)
        self.assertGreater(len(self.auditor.issues), 0)
    
    # ===== اختبارات check_negative_values =====
    
    def test_check_negative_values_clean(self):
        """اختبار بيانات بدون قيم سالبة"""
        data = {'revenue': 100000, 'total_assets': 500000, 'equity': 300000}
        result = self.auditor.check_negative_values(data)
        self.assertTrue(result)
    
    def test_check_negative_values_violation(self):
        """اختبار بيانات بقيم سالبة غير مسموحة"""
        data = {'revenue': -100, 'total_assets': 500000, 'equity': 300000}
        result = self.auditor.check_negative_values(data)
        self.assertFalse(result)
    
    # ===== اختبارات check_ratios_reasonableness - Bug #4 =====
    
    def test_ratios_reasonableness_normal(self):
        """اختبار نسب طبيعية"""
        ratios = {
            'current_ratio': 2.0,
            'debt_to_equity': 0.7,
            'net_profit_margin': 7.5
        }
        self.auditor.check_ratios_reasonableness(ratios)
        # النسب الطبيعية ما تنتج تحذيرات أو أخطاء
        self.assertEqual(len(self.auditor.warnings), 0)
        self.assertEqual(len(self.auditor.issues), 0)
    
    def test_ratios_reasonableness_low_current_ratio(self):
        """اختبار نسبة سيولة منخفضة جداً"""
        ratios = {'current_ratio': 0.3, 'net_profit_margin': 5}
        self.auditor.check_ratios_reasonableness(ratios)
        self.assertGreater(len(self.auditor.warnings), 0)
    
    def test_ratios_reasonableness_high_debt(self):
        """اختبار ديون عالية"""
        ratios = {'debt_to_equity': 3.0, 'net_profit_margin': 5}
        self.auditor.check_ratios_reasonableness(ratios)
        self.assertGreater(len(self.auditor.warnings), 0)
    
    def test_loss_creates_warning_not_issue(self):
        """اختبار إن الخسارة تحذير مش issue - Bug #4"""
        ratios = {'net_profit_margin': -5.0}
        self.auditor.check_ratios_reasonableness(ratios)
        # بعد إصلاح Bug #4: الخسارة لازم تكون warning مش issue
        self.assertEqual(len(self.auditor.issues), 0)
        self.assertGreater(len(self.auditor.warnings), 0)
        # التحقق من النص
        loss_warning = self.warnings_text() if hasattr(self, 'warnings_text') else None
        # التحقق من وجود تحذير خسارة
        has_loss_warning = any(
            'خسائر' in str(w.get('description', ''))
            for w in self.auditor.warnings
        )
        self.assertTrue(has_loss_warning, "لم يتم إنشاء تحذير خسارة")
    
    def test_ratios_reasonableness_high_current_ratio(self):
        """اختبار نسبة سيولة عالية جداً"""
        ratios = {'current_ratio': 6.0, 'net_profit_margin': 5}
        self.auditor.check_ratios_reasonableness(ratios)
        self.assertGreater(len(self.auditor.warnings), 0)
    
    # ===== اختبارات check_cash_flow_consistency =====
    
    def test_cash_flow_consistency_good(self):
        """اختبار اتساق جيد بين التدفق والربح"""
        # التدفق قريب من الربح
        self.auditor.check_cash_flow_consistency(10000, 12000)
        self.assertEqual(len(self.auditor.warnings), 0)
    
    def test_cash_flow_consistency_poor(self):
        """اختبار اتساق ضعيف"""
        # التدفق أقل بكثير من الربح
        self.auditor.check_cash_flow_consistency(2000, 10000)
        self.assertGreater(len(self.auditor.warnings), 0)
    
    # ===== اختبارات check_inventory_sanity =====
    
    def test_inventory_sanity_normal(self):
        """اختبار مخزون طبيعي"""
        result = self.auditor.check_inventory_sanity(inventory=1000, cogs=5000)
        self.assertTrue(result)
    
    def test_inventory_sanity_zero_with_cogs(self):
        """اختبار مخزون صفر مع تكلفة بضاعة"""
        result = self.auditor.check_inventory_sanity(inventory=0, cogs=5000)
        self.assertTrue(result)  # ما يفشلش، بس يضيف warning
        self.assertGreater(len(self.auditor.warnings), 0)
    
    # ===== اختبارات generate_audit_report =====
    
    def test_generate_audit_report_clean(self):
        """توليد تقرير لبيانات نظيفة"""
        self.auditor.check_balance_sheet(500000, 200000, 300000)
        report = self.auditor.generate_audit_report()
        self.assertIsInstance(report, str)
        self.assertIn('تقرير التدقيق', report)
        self.assertIn('نجح', report)
    
    def test_generate_audit_report_with_issues(self):
        """توليد تقرير مع وجود أخطاء"""
        self.auditor.check_balance_sheet(600000, 200000, 300000)
        report = self.auditor.generate_audit_report()
        self.assertIn('الأخطاء', report)
        self.assertIn('فشل', report)
    
    def test_get_audit_summary(self):
        """اختبار الحصول على ملخص التدقيق"""
        self.auditor.check_balance_sheet(500000, 200000, 300000)
        summary = self.auditor.get_audit_summary()
        self.assertIn('total_issues', summary)
        self.assertIn('total_warnings', summary)
        self.assertIn('report', summary)
    
    def test_clear_audit(self):
        """اختبار مسح نتائج التدقيق"""
        self.auditor.check_balance_sheet(600000, 200000, 300000)
        self.assertGreater(len(self.auditor.issues), 0)
        self.auditor.clear_audit()
        self.assertEqual(len(self.auditor.issues), 0)
        self.assertEqual(len(self.auditor.warnings), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
