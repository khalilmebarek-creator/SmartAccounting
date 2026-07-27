# اختبارات Edge Cases الإضافية
# =============================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.calculations import CalculationEngine
from modules.analysis import FinancialAnalyzer
from modules.audit import AuditEngine
from modules.reporting import ReportGenerator


class TestCalculationEdgeCases(unittest.TestCase):
    """حالات حدية إضافية لمحرك الحسابات"""

    def test_net_profit_margin_zero_revenue(self):
        """هامش صافي الربح مع إيرادات صفر"""
        calc = CalculationEngine()
        result = calc.net_profit_margin(15000, 0)
        self.assertEqual(result, 0)

    def test_debt_to_equity_zero_equity(self):
        """نسبة الدين مع حقوق ملكية صفر"""
        calc = CalculationEngine()
        result = calc.debt_to_equity(200000, 0)
        self.assertEqual(result, 0)

    def test_debt_ratio_zero_assets(self):
        """نسبة الدين مع أصول صفر"""
        calc = CalculationEngine()
        result = calc.debt_ratio(100000, 0)
        self.assertEqual(result, 0)

    def test_asset_turnover_zero_assets(self):
        """معدل دوران الأصول مع أصول صفر"""
        calc = CalculationEngine()
        result = calc.asset_turnover(200000, 0)
        self.assertEqual(result, 0)

    def test_inventory_turnover_zero_inventory(self):
        """معدل دوران المخزون مع مخزون صفر"""
        calc = CalculationEngine()
        result = calc.inventory_turnover(120000, 0)
        self.assertEqual(result, 0)

    def test_receivables_turnover_zero_receivables(self):
        """معدل دوران الذمم مع ذمم صفر"""
        calc = CalculationEngine()
        result = calc.receivables_turnover(200000, 0)
        self.assertEqual(result, 0)

    def test_quick_ratio_zero_inventory(self):
        """النسبة السريعة مع مخزون صفر"""
        calc = CalculationEngine()
        result = calc.quick_ratio(100000, 0, 50000)
        self.assertEqual(result, 2.0)


class TestAnalysisEdgeCases(unittest.TestCase):
    """حالات حدية إضافية للتحليل المالي"""

    def test_dupont_all_zero(self):
        """DuPont مع كل القيم صفر"""
        analyzer = FinancialAnalyzer({})
        result = analyzer.dupont_analysis(0, 0, 0, 0)
        self.assertEqual(result['net_profit_margin'], 0)
        self.assertEqual(result['asset_turnover'], 0)
        self.assertEqual(result['equity_multiplier'], 0)
        self.assertEqual(result['roe'], 0)

    def test_working_capital_equal(self):
        """رأس المال العامل مع تساوي الأصول والالتزامات"""
        analyzer = FinancialAnalyzer({})
        result = analyzer.working_capital_analysis(100000, 100000, 20000)
        self.assertEqual(result['working_capital'], 0)
        self.assertIn("صفر", result['status'])

    def test_trend_analysis_two_items(self):
        """تحليل الاتجاه مع عنصرين فقط"""
        analyzer = FinancialAnalyzer({})
        result = analyzer.trend_analysis([100, 150])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['percentage_change'], 50.0)

    def test_interpret_dupont_low_values(self):
        """تفسير DuPont مع قيم منخفضة"""
        analyzer = FinancialAnalyzer({})
        interp = analyzer._interpret_dupont(2, 0.5, 1.5)
        self.assertEqual(len(interp), 3)
        self.assertTrue(any("منخفض" in i for i in interp))


class TestAuditEdgeCases(unittest.TestCase):
    """حالات حدية إضافية للتدقيق"""

    def test_audit_clean_data(self):
        """تدقيق بيانات نظيفة بالكامل"""
        auditor = AuditEngine()
        auditor.check_balance_sheet(500000, 200000, 300000)
        auditor.check_negative_values({
            'revenue': 200000, 'total_assets': 500000, 'equity': 300000
        })
        auditor.check_ratios_reasonableness({
            'current_ratio': 2.0, 'debt_to_equity': 0.67,
            'net_profit_margin': 7.5
        })
        auditor.check_inventory_sanity(20000, 120000)

        summary = auditor.get_audit_summary()
        self.assertEqual(summary['total_issues'], 0)
        self.assertEqual(summary['total_warnings'], 0)

    def test_audit_multiple_warnings(self):
        """تدقيق ينتج تحذيرات متعددة"""
        auditor = AuditEngine()
        auditor.check_balance_sheet(500000, 200000, 300000)
        auditor.check_ratios_reasonableness({
            'current_ratio': 0.3, 'debt_to_equity': 3.0,
            'net_profit_margin': -5.0
        })
        summary = auditor.get_audit_summary()
        self.assertGreater(summary['total_warnings'], 0)

    def test_audit_report_length(self):
        """تقرير التدقيق يجب أن يكون نص طويل"""
        auditor = AuditEngine()
        auditor.check_balance_sheet(500000, 200000, 300000)
        report = auditor.generate_audit_report()
        self.assertGreater(len(report), 50)


class TestReportingEdgeCases(unittest.TestCase):
    """حالات حدية إضافية للتقارير"""

    def test_report_empty_ratios(self):
        """تقرير نسب فارغ"""
        reporter = ReportGenerator("شركة اختبار", 2024)
        report = reporter.generate_financial_ratios_report({})
        self.assertIn("2024", report)

    def test_report_comprehensive(self):
        """تقرير شامل مع بيانات كاملة"""
        reporter = ReportGenerator("شركة اختبار", 2024)
        report = reporter.generate_comprehensive_report(
            balance_sheet={'total_assets': 500000},
            income_statement={'revenue': 200000},
            ratios={'roe': 5.0},
            analysis="تحليل جيد"
        )
        self.assertIn("500,000", report)
        self.assertIn("200,000", report)
        self.assertIn("تحليل جيد", report)


class TestVault(unittest.TestCase):
    """ اختبارات وحدة vault للتشفير """

    def test_encrypt_decrypt_roundtrip(self):
        from utils.vault import encrypt, decrypt
        original = "MySecretPassword123!"
        encrypted = encrypt(original)
        self.assertNotEqual(encrypted, original)
        self.assertTrue(encrypted.startswith("ENC:"))
        decrypted = decrypt(encrypted)
        self.assertEqual(decrypted, original)

    def test_decrypt_non_encrypted_passthrough(self):
        from utils.vault import decrypt
        self.assertEqual(decrypt("plain text"), "plain text")

    def test_decrypt_empty_string(self):
        from utils.vault import decrypt
        self.assertEqual(decrypt(""), "")

    def test_encrypt_empty_string(self):
        from utils.vault import encrypt
        self.assertEqual(encrypt(""), "")

    def test_is_encrypted(self):
        from utils.vault import is_encrypted
        self.assertTrue(is_encrypted("ENC:dGVzdA=="))
        self.assertFalse(is_encrypted("plain"))
        self.assertFalse(is_encrypted(""))


class TestInputSanitization(unittest.TestCase):
    """ اختبارات تنظيف المدخلات """

    def test_sanitize_removes_html_chars(self):
        from ui.views.data_entry import _sanitize_text
        result = _sanitize_text('Hello <script>alert("xss")</script>')
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)

    def test_sanitize_trims_length(self):
        from ui.views.data_entry import _sanitize_text
        long_text = "A" * 300
        result = _sanitize_text(long_text)
        self.assertLessEqual(len(result), 200)

    def test_sanitize_removes_quotes(self):
        from ui.views.data_entry import _sanitize_text
        result = _sanitize_text('Company "Name"')
        self.assertNotIn('"', result)


class TestDBHelpers(unittest.TestCase):
    """ اختبارات مساعدات قاعدة البيانات """

    def test_safe_div_normal(self):
        from modules.calculations import CalculationEngine
        calc = CalculationEngine()
        self.assertEqual(calc._safe_div(10, 2), 5.0)

    def test_safe_div_zero(self):
        from modules.calculations import CalculationEngine
        calc = CalculationEngine()
        self.assertEqual(calc._safe_div(10, 0), 0)

    def test_safe_div_custom_default(self):
        from modules.calculations import CalculationEngine
        calc = CalculationEngine()
        self.assertEqual(calc._safe_div(10, 0, -1), -1)


class TestBackupRotation(unittest.TestCase):
    """ اختبارات دوران النسخ الاحتياطية """

    def test_rotate_keeps_max_backups(self):
        from modules.backup import BackupManager, MAX_BACKUPS
        self.assertEqual(MAX_BACKUPS, 10)

    def test_sanitize_name_basic(self):
        from modules.backup import _sanitize_name
        self.assertEqual(_sanitize_name("test_db"), "test_db")

    def test_sanitize_name_special_chars(self):
        from modules.backup import _sanitize_name
        result = _sanitize_name("my db!@#")
        self.assertNotIn("!", result)
        self.assertNotIn("@", result)

    def test_sanitize_name_digit_start(self):
        from modules.backup import _sanitize_name
        result = _sanitize_name("123test")
        self.assertTrue(result.startswith("t_"))


if __name__ == '__main__':
    unittest.main()
