# اختبارات التحليل المالي
# =========================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.analysis import FinancialAnalyzer


class TestFinancialAnalyzer(unittest.TestCase):
    """اختبارات شاملة للمحلل المالي"""
    
    def setUp(self):
        """إعداد البيانات قبل كل اختبار"""
        self.data = {
            'current_assets': 100000,
            'inventory': 20000,
            'current_liabilities': 50000,
            'net_income': 15000,
            'revenue': 200000,
            'total_assets': 500000,
            'equity': 300000
        }
        self.analyzer = FinancialAnalyzer(self.data)
    
    # ===== اختبارات trend_analysis =====
    
    def test_trend_analysis_sufficient_data(self):
        """اختبار تحليل الاتجاه مع بيانات كافية"""
        data_series = [100, 120, 150, 180]
        trends = self.analyzer.trend_analysis(data_series)
        self.assertIsNotNone(trends)
        self.assertEqual(len(trends), 3)  # 3 اتجاهات (بين 4 نقاط)
        # التحقق من الاتجاه الأول
        self.assertEqual(trends[0]['value'], 120)
        self.assertEqual(trends[0]['percentage_change'], 20.0)
    
    def test_trend_analysis_insufficient_data(self):
        """اختبار مع بيانات غير كافية"""
        trends = self.analyzer.trend_analysis([100])
        self.assertIsNone(trends)
    
    def test_trend_analysis_with_zero_previous(self):
        """اختبار مع قيمة سابقة صفر"""
        data_series = [0, 100, 200]
        trends = self.analyzer.trend_analysis(data_series)
        self.assertIsNotNone(trends)
        # التحقق من التعامل مع القسمة على صفر
        self.assertEqual(trends[0]['percentage_change'], 0)
    
    # ===== اختبارات comparative_analysis =====
    
    def test_comparative_analysis(self):
        """اختبار التحليل المقارن"""
        company_ratios = {'roe': 10, 'current_ratio': 2.0}
        industry = {'roe': 8, 'current_ratio': 1.5}
        comparison = self.analyzer.comparative_analysis(company_ratios, industry)
        self.assertIn('roe', comparison)
        self.assertIn('current_ratio', comparison)
        self.assertEqual(comparison['roe']['company_value'], 10)
        self.assertEqual(comparison['roe']['difference'], 2)
    
    def test_comparative_analysis_with_missing_industry(self):
        """اختبار مع غياب بعض نسب الصناعة"""
        company_ratios = {'roe': 10}
        industry = {}
        comparison = self.analyzer.comparative_analysis(company_ratios, industry)
        self.assertEqual(comparison['roe']['difference'], 0)
    
    # ===== اختبارات dupont_analysis - الأهم =====
    
    def test_dupont_analysis_normal(self):
        """اختبار تحليل DuPont مع بيانات طبيعية"""
        dupont = self.analyzer.dupont_analysis(
            net_income=15000,
            revenue=200000,
            total_assets=500000,
            equity=300000
        )
        # net_profit_margin = 15000/200000*100 = 7.5
        # asset_turnover = 200000/500000 = 0.4
        # equity_multiplier = 500000/300000 = 1.6667
        # ROE = 7.5% * 0.4 * 1.6667 = 5.0
        self.assertEqual(dupont['net_profit_margin'], 7.5)
        self.assertEqual(dupont['asset_turnover'], 0.4)
        self.assertAlmostEqual(dupont['equity_multiplier'], 1.6667, places=4)
        self.assertEqual(dupont['roe'], 5.0)
        # التحقق من وجود analysis
        self.assertIn('analysis', dupont)
    
    def test_dupont_analysis_stores_in_results(self):
        """اختبار إن DuPont يتسجل في self.analysis_results - Bug #3"""
        # قبل الاستدعاء، analysis_results فاضي
        self.assertNotIn('dupont', self.analyzer.analysis_results)
        
        # استدعاء dupont_analysis
        self.analyzer.dupont_analysis(15000, 200000, 500000, 300000)
        
        # بعد الاستدعاء، لازم يكون اتسجل
        self.assertIn('dupont', self.analyzer.analysis_results)
        self.assertEqual(
            self.analyzer.analysis_results['dupont']['roe'], 
            5.0
        )
    
    def test_dupont_analysis_with_zero_values(self):
        """اختبار DuPont مع قيم صفر"""
        dupont = self.analyzer.dupont_analysis(0, 0, 100, 100)
        self.assertEqual(dupont['net_profit_margin'], 0)
        self.assertEqual(dupont['roe'], 0)
    
    # ===== اختبارات working_capital_analysis =====
    
    def test_working_capital_analysis_positive(self):
        """اختبار رأس المال العامل الموجب"""
        result = self.analyzer.working_capital_analysis(
            current_assets=100000,
            current_liabilities=50000,
            inventory=20000
        )
        self.assertEqual(result['working_capital'], 50000)
        self.assertIn('موجب', result['status'])
    
    def test_working_capital_analysis_negative(self):
        """اختبار رأس المال العامل السالب"""
        result = self.analyzer.working_capital_analysis(
            current_assets=30000,
            current_liabilities=50000,
            inventory=10000
        )
        self.assertEqual(result['working_capital'], -20000)
        self.assertIn('سالب', result['status'])
    
    # ===== اختبارات cash_flow_analysis =====
    
    def test_cash_flow_analysis_positive(self):
        """اختبار تحليل التدفقات النقدية"""
        result = self.analyzer.cash_flow_analysis(
            operating_cash_flow=10000,
            investing_cash_flow=-5000,
            financing_cash_flow=-2000
        )
        self.assertEqual(result['total_cash_flow'], 3000)
        self.assertIn('analysis', result)
    
    # ===== اختبارات generate_report =====
    
    def test_generate_report_contains_dupont(self):
        """اختبار إن التقرير يحتوي على DuPont بعد التحليل"""
        self.analyzer.dupont_analysis(15000, 200000, 500000, 300000)
        report = self.analyzer.generate_report()
        self.assertIn('DuPont', report)
        self.assertIn('ROE', report)
    
    def test_generate_report_with_trends(self):
        """اختبار التقرير مع اتجاهات"""
        self.analyzer.analysis_results['trends'] = [
            {'period': 1, 'value': 100, 'percentage_change': 10.5}
        ]
        report = self.analyzer.generate_report()
        self.assertIn('الاتجاهات', report)
    
    def test_get_summary(self):
        """اختبار ملخص التحليل"""
        summary = self.analyzer.get_summary()
        self.assertIn('analysis_results', summary)
        self.assertIn('report', summary)


if __name__ == '__main__':
    unittest.main(verbosity=2)
