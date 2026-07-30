# اختبارات محرك الحسابات المالية
# ================================

import unittest
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.calculations import CalculationEngine


class TestCalculationEngine(unittest.TestCase):
    """اختبارات شاملة لمحرك الحسابات"""
    
    def setUp(self):
        """إعداد البيانات التجريبية قبل كل اختبار"""
        self.engine = CalculationEngine()
        # البيانات المرجعية للتحقق من الحسابات
        self.test_data = {
            'current_assets': 100000,
            'inventory': 20000,
            'current_liabilities': 50000,
            'cash': 8000,
            'gross_profit': 30000,
            'operating_expenses': 15000,
            'net_income': 15000,
            'revenue': 200000,
            'total_assets': 500000,
            'equity': 300000,
            'cost_of_goods_sold': 120000,
            'average_receivables': 40000,
            'average_inventory': 25000,
            'average_payables': 18000,
            'total_liabilities': 200000
        }
    
    # ===== اختبارات نسب السيولة =====
    
    def test_current_ratio_normal(self):
        """اختبار نسبة السيولة الحالية - حالة طبيعية"""
        result = self.engine.current_ratio(100000, 50000)
        self.assertEqual(result, 2.0)
    
    def test_current_ratio_zero_liabilities(self):
        """اختبار نسبة السيولة - التزامات صفر (تجنب القسمة على صفر)"""
        result = self.engine.current_ratio(100000, 0)
        self.assertEqual(result, 0)
    
    def test_quick_ratio_normal(self):
        """اختبار النسبة السريعة"""
        result = self.engine.quick_ratio(100000, 20000, 50000)
        self.assertEqual(result, 1.6)
    
    def test_quick_ratio_zero_liabilities(self):
        """اختبار النسبة السريعة - التزامات صفر"""
        result = self.engine.quick_ratio(100000, 20000, 0)
        self.assertEqual(result, 0)
    
    def test_cash_ratio_normal(self):
        """اختبار نسبة السيولة النقدية"""
        result = self.engine.cash_ratio(8000, 50000)
        self.assertAlmostEqual(result, 0.16)
    
    def test_cash_ratio_zero_liabilities(self):
        """اختبار نسبة السيولة النقدية - التزامات صفر"""
        result = self.engine.cash_ratio(8000, 0)
        self.assertEqual(result, 0)
    
    # ===== اختبارات نسب الربحية =====
    
    def test_gross_profit_margin(self):
        """اختبار هامش الربح الإجمالي"""
        result = self.engine.gross_profit_margin(30000, 200000)
        # 30000 / 200000 * 100 = 15.0%
        self.assertEqual(result, 15.0)
    
    def test_gross_profit_margin_zero_revenue(self):
        """اختبار هامش الربح - إيرادات صفر"""
        result = self.engine.gross_profit_margin(30000, 0)
        self.assertEqual(result, 0)
    
    def test_operating_profit_margin(self):
        """اختبار هامش الربح التشغيلي"""
        result = self.engine.operating_profit_margin(15000, 200000)
        self.assertEqual(result, 7.5)
    
    def test_operating_profit_margin_zero_revenue(self):
        result = self.engine.operating_profit_margin(15000, 0)
        self.assertEqual(result, 0)
    
    def test_net_profit_margin(self):
        """اختبار هامش صافي الربح"""
        result = self.engine.net_profit_margin(15000, 200000)
        # 15000 / 200000 * 100 = 7.5%
        self.assertEqual(result, 7.5)
    
    def test_roa(self):
        """اختبار العائد على الأصول"""
        result = self.engine.roa(15000, 500000)
        # 15000 / 500000 * 100 = 3.0%
        self.assertEqual(result, 3.0)
    
    def test_roa_zero_assets(self):
        """اختبار ROA - أصول صفر"""
        result = self.engine.roa(15000, 0)
        self.assertEqual(result, 0)
    
    def test_roe(self):
        """اختبار العائد على حقوق المالكين"""
        result = self.engine.roe(15000, 300000)
        # 15000 / 300000 * 100 = 5.0%
        self.assertEqual(result, 5.0)
    
    def test_roe_zero_equity(self):
        """اختبار ROE - حقوق ملكية صفر"""
        result = self.engine.roe(15000, 0)
        self.assertEqual(result, 0)
    
    # ===== اختبارات نسب الكفاءة =====
    
    def test_asset_turnover(self):
        """اختبار معدل دوران الأصول"""
        result = self.engine.asset_turnover(200000, 500000)
        # 200000 / 500000 = 0.4
        self.assertEqual(result, 0.4)
    
    def test_receivables_turnover(self):
        """اختبار معدل دوران الذمم المدينة"""
        result = self.engine.receivables_turnover(200000, 40000)
        # 200000 / 40000 = 5.0
        self.assertEqual(result, 5.0)
    
    def test_days_sales_outstanding(self):
        """اختبار عدد أيام البيع المعلقة"""
        result = self.engine.days_sales_outstanding(5.0)
        # 365 / 5 = 73
        self.assertEqual(result, 73)
    
    def test_inventory_turnover(self):
        """اختبار معدل دوران المخزون"""
        result = self.engine.inventory_turnover(120000, 25000)
        # 120000 / 25000 = 4.8
        self.assertEqual(result, 4.8)
    
    def test_days_inventory_outstanding(self):
        """اختبار فترة الاحتفاظ بالمخزون"""
        result = self.engine.days_inventory_outstanding(4.8)
        self.assertEqual(result, 76)
    
    def test_payables_turnover(self):
        """اختبار دوران الموردين"""
        result = self.engine.payables_turnover(120000, 18000)
        self.assertAlmostEqual(result, 6.6667, places=4)
    
    def test_days_payable_outstanding(self):
        """اختبار فترة سداد الموردين"""
        result = self.engine.days_payable_outstanding(6.6667)
        self.assertEqual(result, 55)
    
    def test_operating_cycle(self):
        """اختبار الدورة التشغيلية"""
        result = self.engine.operating_cycle(76, 73)
        self.assertEqual(result, 149)
    
    def test_cash_conversion_cycle(self):
        """اختبار دورة التحويل النقدي"""
        result = self.engine.cash_conversion_cycle(76, 73, 55)
        self.assertEqual(result, 94)
    
    # ===== اختبارات نسب الاستدانة =====
    
    def test_debt_to_equity(self):
        """اختبار نسبة الدين إلى حقوق المالكين"""
        result = self.engine.debt_to_equity(200000, 300000)
        # 200000 / 300000 = 0.6667
        self.assertAlmostEqual(result, 0.6667, places=4)
    
    def test_debt_ratio(self):
        """اختبار نسبة الدين"""
        result = self.engine.debt_ratio(200000, 500000)
        # 200000 / 500000 = 0.4
        self.assertEqual(result, 0.4)
    
    def test_equity_ratio(self):
        """اختبار نسبة حقوق الملكية"""
        result = self.engine.equity_ratio(300000, 500000)
        self.assertEqual(result, 0.6)
    
    # ===== اختبار الدالة الشاملة =====
    
    def test_calculate_all_ratios_success(self):
        """اختبار حساب كل النسب دفعة واحدة"""
        ratios = self.engine.calculate_all_ratios(self.test_data)
        
        # التحقق من وجود كل النسب
        expected_keys = [
            'current_ratio', 'quick_ratio', 'cash_ratio',
            'gross_profit_margin', 'operating_profit_margin', 'net_profit_margin',
            'roa', 'roe',
            'asset_turnover', 'receivables_turnover',
            'days_sales_outstanding', 'inventory_turnover',
            'days_inventory_outstanding', 'payables_turnover',
            'days_payable_outstanding', 'operating_cycle',
            'cash_conversion_cycle',
            'debt_to_equity', 'debt_ratio', 'equity_ratio'
        ]
        for key in expected_keys:
            self.assertIn(key, ratios)
        
        # التحقق من قيم محددة
        self.assertEqual(ratios['current_ratio'], 2.0)
        self.assertEqual(ratios['quick_ratio'], 1.6)
        self.assertEqual(ratios['net_profit_margin'], 7.5)
        self.assertEqual(ratios['roe'], 5.0)
        self.assertEqual(ratios['roa'], 3.0)
    
    def test_calculate_all_ratios_with_missing_data(self):
        """اختبار حساب النسب مع بيانات ناقصة - لازم يفشل بأمان"""
        bad_data = {'revenue': 100}  # بيانات ناقصة
        ratios = self.engine.calculate_all_ratios(bad_data)
        # إما يرجع None أو يرجع dict بنسب ناقصة - لا يفجّر البرنامج
        # السلوك الحالي: يرجع dict لكن بدون كل المفاتيح
        # الفحص المهم: ما يفجّر KeyError
        if ratios is not None:
            self.assertIsInstance(ratios, dict)
    
    def test_engine_with_initial_data(self):
        """اختبار تمرير البيانات في الـ constructor"""
        engine = CalculationEngine(self.test_data)
        self.assertEqual(engine.data, self.test_data)


class TestZScore(unittest.TestCase):
    """اختبارات Altman Z-Score"""

    def setUp(self):
        self.engine = CalculationEngine()

    def test_safe_zone(self):
        result = self.engine.z_score(
            working_capital=800000, retained_earnings=600000,
            ebit=400000, market_value_equity=3000000,
            book_value_debt=800000, sales=2400000, total_assets=2000000
        )
        self.assertEqual(result["status"], "safe")
        self.assertGreater(result["z_score"], 2.99)

    def test_grey_zone(self):
        result = self.engine.z_score(
            working_capital=500000, retained_earnings=250000,
            ebit=150000, market_value_equity=1200000,
            book_value_debt=900000, sales=1500000, total_assets=2000000
        )
        self.assertEqual(result["status"], "grey")
        self.assertGreater(result["z_score"], 1.81)
        self.assertLessEqual(result["z_score"], 2.99)

    def test_danger_zone(self):
        result = self.engine.z_score(
            working_capital=50000, retained_earnings=30000,
            ebit=20000, market_value_equity=150000,
            book_value_debt=1000000, sales=100000, total_assets=500000
        )
        self.assertEqual(result["status"], "danger")
        self.assertLess(result["z_score"], 1.81)

    def test_zero_total_assets(self):
        result = self.engine.z_score(
            working_capital=0, retained_earnings=0, ebit=0,
            market_value_equity=0, book_value_debt=0,
            sales=0, total_assets=0
        )
        self.assertEqual(result["z_score"], 0)
        self.assertEqual(result["status"], "danger")

    def test_components_keys(self):
        result = self.engine.z_score(
            working_capital=500000, retained_earnings=300000,
            ebit=200000, market_value_equity=1500000,
            book_value_debt=800000, sales=1200000, total_assets=2000000
        )
        for key in ["x1", "x2", "x3", "x4", "x5"]:
            self.assertIn(key, result["components"])

    def test_zero_debt(self):
        result = self.engine.z_score(
            working_capital=500000, retained_earnings=300000,
            ebit=200000, market_value_equity=1500000,
            book_value_debt=0, sales=1200000, total_assets=2000000
        )
        self.assertEqual(result["components"]["x4"], 0)

    def test_known_example(self):
        result = self.engine.z_score(
            working_capital=500000, retained_earnings=300000,
            ebit=200000, market_value_equity=1500000,
            book_value_debt=800000, sales=1200000, total_assets=2000000
        )
        x1 = 500000 / 2000000
        x2 = 300000 / 2000000
        x3 = 200000 / 2000000
        x4 = 1500000 / 800000
        x5 = 1200000 / 2000000
        expected = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5
        self.assertAlmostEqual(result["z_score"], round(expected, 3), places=2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
