# اختبارات توليد التقارير
# =========================

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.reporting import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    """اختبارات شاملة لمولد التقارير"""
    
    def setUp(self):
        """إعداد مولد التقارير"""
        self.reporter = ReportGenerator("شركة الاختبار", 2024)
    
    def test_init(self):
        """اختبار التهيئة"""
        self.assertEqual(self.reporter.company_name, "شركة الاختبار")
        self.assertEqual(self.reporter.fiscal_year, 2024)
        self.assertIsNotNone(self.reporter.generated_date)
    
    def test_generate_balance_sheet_report_simple(self):
        """اختبار توليد تقرير ميزانية بسيط"""
        report = self.reporter.generate_balance_sheet_report(
            assets=500000,
            liabilities=200000,
            equity=300000
        )
        self.assertIsInstance(report, str)
        self.assertIn('الميزانية', report)
        self.assertIn('شركة الاختبار', report)
        self.assertIn('500,000', report)
    
    def test_generate_balance_sheet_report_detailed(self):
        """اختبار تقرير ميزانية مفصّل"""
        assets = {
            'أصول متداولة': 300000,
            'أصول ثابتة': 200000
        }
        liabilities = {
            'التزامات متداولة': 100000,
            'التزامات طويلة الأجل': 100000
        }
        equity = {
            'رأس المال': 200000,
            'أرباح محتجزة': 100000
        }
        report = self.reporter.generate_balance_sheet_report(assets, liabilities, equity)
        self.assertIn('أصول متداولة', report)
        self.assertIn('التزامات متداولة', report)
    
    def test_generate_income_statement_report(self):
        """اختبار توليد تقرير الدخل"""
        report = self.reporter.generate_income_statement_report(
            revenue=200000,
            cogs=120000,
            expenses=65000,
            net_income=15000
        )
        self.assertIsInstance(report, str)
        self.assertIn('قائمة الدخل', report)
        # ربح إجمالي = 200000 - 120000 = 80000
        self.assertIn('80,000', report)
    
    def test_generate_financial_ratios_report(self):
        """اختبار توليد تقرير النسب"""
        ratios = {
            'current_ratio': 2.0,
            'quick_ratio': 1.6,
            'gross_profit_margin': 15.0,
            'net_profit_margin': 7.5,
            'roa': 3.0,
            'roe': 5.0,
            'asset_turnover': 0.4,
            'receivables_turnover': 5.0,
            'inventory_turnover': 4.8,
            'debt_to_equity': 0.6667,
            'debt_ratio': 0.4
        }
        report = self.reporter.generate_financial_ratios_report(ratios)
        self.assertIsInstance(report, str)
        self.assertIn('النسب المالية', report)
        self.assertIn('2.0', report)
        self.assertIn('7.5', report)
    
    def test_generate_financial_ratios_report_partial(self):
        """اختبار تقرير بنسب جزئية"""
        ratios = {'current_ratio': 2.0}
        report = self.reporter.generate_financial_ratios_report(ratios)
        self.assertIn('2.0', report)
        # لازم ما يفجّرش لو النسب ناقصة
    
    def test_generate_comprehensive_report(self):
        """اختبار التقرير الشامل"""
        report = self.reporter.generate_comprehensive_report(
            balance_sheet={'total_assets': 500000},
            income_statement={'revenue': 200000, 'net_income': 15000},
            ratios={'roe': 5.0, 'current_ratio': 2.0},
            analysis="تحليل شامل"
        )
        self.assertIsInstance(report, str)
        self.assertIn('الشامل', report)
    
    def test_export_report_to_file(self):
        """اختبار تصدير التقرير لملف"""
        report_content = "تقرير اختباري\n"
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.txt', 
            delete=False, 
            encoding='utf-8'
        ) as f:
            tmp_path = f.name
        
        try:
            result = self.reporter.export_report_to_file(report_content, tmp_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(tmp_path))
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn('تقرير اختباري', content)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_export_report_invalid_path(self):
        """اختبار تصدير بمكان غير صحيح"""
        result = self.reporter.export_report_to_file("test", "/invalid/path/file.txt")
        # لازم يرجع False
        self.assertFalse(result)
    
    def test_export_to_pdf_success(self):
        """اختبار تصدير التقرير إلى PDF"""
        report_content = "تقرير اختباري\nالبيانات المالية\n"
        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.pdf',
            delete=False
        ) as f:
            tmp_path = f.name
        
        try:
            result = self.reporter.export_to_pdf(report_content, tmp_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_export_to_pdf_invalid_path(self):
        """اختبار تصدير PDF بمكان غير صحيح"""
        result = self.reporter.export_to_pdf("test", "/invalid/path/report.pdf")
        self.assertFalse(result)

    # ===== اختبارات generate_dupont_report =====

    def test_generate_dupont_report(self):
        """اختبار توليد تقرير DuPont"""
        dupont = {'net_profit_margin': 7.5, 'asset_turnover': 0.4,
                  'equity_multiplier': 1.6667, 'roe': 5.0}
        waterfall = {'base': 7.5, 'turnover_effect': -4.5,
                     'leverage_effect': 2.0, 'total': 5.0}
        report = self.reporter.generate_dupont_report(dupont, waterfall)
        self.assertIsInstance(report, str)
        self.assertIn('DuPont', report)
        self.assertIn('ROE', report)
        self.assertIn('7.5', report)
        self.assertIn('5.0', report)

    def test_generate_dupont_report_with_industry(self):
        """اختبار تقرير DuPont مع مقارنة القطاع"""
        dupont = {'net_profit_margin': 3, 'asset_turnover': 0.4,
                  'equity_multiplier': 1.8, 'roe': 2.16}
        industry = {
            'roe': {'company_value': 2.16, 'sector_average': 12,
                    'status': 'below', 'deviation': -9.84},
            'net_profit_margin': {'company_value': 3, 'sector_average': 5,
                                  'status': 'below', 'deviation': -2},
            'asset_turnover': {'company_value': 0.4, 'sector_average': 1.2,
                               'status': 'below', 'deviation': -0.8},
            'equity_multiplier': {'company_value': 1.8, 'sector_average': 2.0,
                                  'status': 'below', 'deviation': -0.2},
        }
        report = self.reporter.generate_dupont_report(dupont, None, industry)
        self.assertIn('القطاع', report)
        self.assertIn('12', report)

    def test_generate_dupont_report_with_recommendations(self):
        """اختبار تقرير DuPont مع التوصيات"""
        dupont = {'net_profit_margin': 3, 'asset_turnover': 0.4,
                  'equity_multiplier': 1.8, 'roe': 2.16}
        recommendations = [
            {'component': 'roe', 'level': 'critical', 'code': 'rec_roe_low',
             'company_value': 2.16, 'target': 10}
        ]
        report = self.reporter.generate_dupont_report(dupont, None, None, recommendations)
        self.assertIn('التوصيات', report)
        self.assertIn('العائد على حقوق الملكية', report)


if __name__ == '__main__':
    unittest.main(verbosity=2)
