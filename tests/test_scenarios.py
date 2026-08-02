# اختبارات تحليل السيناريوهات المالية
# =====================================

import unittest
import sys
import os
import sqlite3
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.scenarios import ScenarioAnalyzer
from database.db_operations import (
    save_analysis, save_scenario_results, get_scenario_results
)
from database.db_schema import create_tables
from database.db_connection import DatabaseConnection


DATA = {
    'revenue': 100000,
    'cost_of_goods_sold': 60000,
    'gross_profit': 40000,
    'operating_expenses': 20000,
    'operating_income': 20000,
    'net_income': 20000,
    'total_assets': 200000,
    'equity': 80000,
}


class TestScenarioAnalyzer(unittest.TestCase):
    """اختبارات محرك السيناريوهات"""

    def setUp(self):
        self.analyzer = ScenarioAnalyzer(DATA, {})

    def test_build_scenarios_returns_all_three(self):
        """اختبار إرجاع السيناريوهات الثلاثة"""
        scenarios = self.analyzer.build_scenarios()
        self.assertIn('best', scenarios)
        self.assertIn('base', scenarios)
        self.assertIn('worst', scenarios)

    def test_base_case_matches_current_data(self):
        """اختبار أن الحالة الطبيعية تعكس البيانات الحالية"""
        scenarios = self.analyzer.build_scenarios()
        base = scenarios['base']
        self.assertEqual(base['revenue'], 100000)
        self.assertEqual(base['net_income'], 20000)
        self.assertEqual(base['net_profit_margin'], 20.0)
        self.assertEqual(base['roe'], 25.0)
        self.assertEqual(base['outcome'], 'base')

    def test_best_case_increases_profit(self):
        """اختبار الحالة المثالية — أرباح أعلى"""
        scenarios = self.analyzer.build_scenarios()
        best = scenarios['best']
        # revenue +20% = 120000، تكاليف -10%، كفاءة +15%
        self.assertEqual(best['revenue'], 120000)
        self.assertEqual(best['cogs'], 55080)
        self.assertEqual(best['net_income'], 46560)
        self.assertGreater(best['net_income'], scenarios['base']['net_income'])
        self.assertEqual(best['outcome'], 'profit')
        # الكفاءة تخفض الأصول: 200000 × 0.85 = 170000
        self.assertEqual(best['total_assets'], 170000)
        self.assertEqual(best['roe'], 58.2)

    def test_worst_case_results_in_loss(self):
        """اختبار أسوأ حالة — خسائر محتملة"""
        scenarios = self.analyzer.build_scenarios()
        worst = scenarios['worst']
        # revenue -20% = 80000، تكاليف +15%، مشاكل +10%
        self.assertEqual(worst['revenue'], 80000)
        self.assertEqual(worst['cogs'], 60720)
        self.assertLess(worst['net_income'], 0)
        self.assertEqual(worst['outcome'], 'loss')
        self.assertEqual(worst['total_assets'], 220000)
        self.assertEqual(worst['roe'], -1.2)

    def test_custom_best_rates(self):
        """اختبار تغيير معدلات الحالة المثالية يدوياً"""
        scenarios = self.analyzer.build_scenarios(
            best={'revenue_change_pct': 0.10}
        )
        best = scenarios['best']
        # r=0.10 فقط، باقي الافتراضات: c=-0.10, e=0.15
        self.assertEqual(best['revenue'], 110000)
        self.assertEqual(best['cogs'], 50490)
        self.assertEqual(best['net_income'], 42680)

    def test_custom_worst_rates(self):
        """اختبار تغيير معدلات أسوأ حالة يدوياً"""
        scenarios = self.analyzer.build_scenarios(
            worst={'cost_change_pct': 0.30}
        )
        worst = scenarios['worst']
        # c=0.30 فقط، باقي الافتراضات: r=-0.20, e=-0.10
        # cogs = 60000×0.8×1.1×1.3 = 68640
        self.assertEqual(worst['cogs'], 68640)

    def test_sensitivity_analysis_structure(self):
        """اختبار بنية تحليل الحساسية"""
        results = self.analyzer.sensitivity_analysis('revenue')
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 5)
        for row in results:
            self.assertIn('pct_change', row)
            self.assertIn('net_income', row)
            self.assertIn('net_profit_margin', row)
            self.assertIn('roe', row)

    def test_sensitivity_revenue_linear(self):
        """اختبار حساسية الإيرادات — صافي الربح يتغير خطياً"""
        results = self.analyzer.sensitivity_analysis('revenue')
        by_pct = {r['pct_change']: r for r in results}
        # net = 20000 × (1 + s)
        self.assertEqual(by_pct[0.20]['net_income'], 24000)
        self.assertEqual(by_pct[-0.20]['net_income'], 16000)
        self.assertEqual(by_pct[0.0]['net_income'], 20000)

    def test_sensitivity_custom_steps(self):
        """اختبار خطوات مخصصة لحساسية الإيرادات"""
        results = self.analyzer.sensitivity_analysis('revenue', steps=[-0.5, 0, 0.5])
        pcts = [r['pct_change'] for r in results]
        self.assertEqual(pcts, [-0.5, 0, 0.5])
        self.assertEqual(results[2]['net_income'], 30000)

    def test_tornado_analysis_sorted_by_impact(self):
        """اختبار رسم الإعصار — مرتب تنازلياً حسب الأثر"""
        tornado = self.analyzer.tornado_analysis(range_pct=0.2)
        variables = [t['variable'] for t in tornado]
        self.assertEqual(variables, ['cost', 'efficiency', 'revenue'])
        impacts = [t['impact'] for t in tornado]
        self.assertEqual(impacts, sorted(impacts, reverse=True))

    def test_tornado_analysis_impact_values(self):
        """اختبار قيم الأثر في رسم الإعصار"""
        tornado = self.analyzer.tornado_analysis(range_pct=0.2)
        by_var = {t['variable']: t for t in tornado}
        # revenue: 20000×(1±0.2) → impact 8000
        self.assertEqual(by_var['revenue']['impact'], 8000)
        # cost / efficiency: ±0.2 → net بين 4000 و 36000 → impact 32000
        self.assertEqual(by_var['cost']['impact'], 32000)
        self.assertEqual(by_var['efficiency']['impact'], 32000)
        # cost -20% → تكاليف أقل → ربح أعلى (36000)؛ cost +20% → ربح أقل (4000)
        self.assertEqual(by_var['cost']['low_net'], 36000)
        self.assertEqual(by_var['cost']['high_net'], 4000)

    def test_compare_scenarios_structure(self):
        """اختبار بنية جدول المقارنة"""
        scenarios = self.analyzer.build_scenarios()
        comparison = self.analyzer.compare_scenarios(scenarios)
        self.assertIn('revenue', comparison)
        self.assertIn('net_income', comparison)
        self.assertIn('roe', comparison)
        row = comparison['revenue']
        self.assertEqual(row['best'], 120000)
        self.assertEqual(row['base'], 100000)
        self.assertEqual(row['worst'], 80000)

    def test_compare_scenarios_deltas(self):
        """اختبار فروق الحالة المثالية/الأسوأ عن الطبيعية"""
        scenarios = self.analyzer.build_scenarios()
        comparison = self.analyzer.compare_scenarios(scenarios)
        net = comparison['net_income']
        self.assertEqual(net['best_delta'], 26560)
        self.assertEqual(net['worst_delta'], -20960)

    def test_save_load_scenarios_roundtrip(self):
        """اختبار حفظ وتحميل السيناريوهات (JSON)"""
        scenarios = self.analyzer.build_scenarios()
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        try:
            self.assertTrue(ScenarioAnalyzer.save_scenarios(scenarios, path))
            loaded = ScenarioAnalyzer.load_scenarios(path)
            self.assertIn('best', loaded)
            self.assertIn('worst', loaded)
            self.assertEqual(loaded['best']['net_income'], 46560)
            self.assertEqual(loaded['base']['net_income'], 20000)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_load_scenarios_invalid(self):
        """اختبار تحميل ملف غير موجود"""
        loaded = ScenarioAnalyzer.load_scenarios("missing_file.json")
        self.assertEqual(loaded, {})

    def test_zero_revenue_does_not_crash(self):
        """اختبار عدم الانهيار مع إيرادات صفرية"""
        analyzer = ScenarioAnalyzer({'revenue': 0, 'total_assets': 0, 'equity': 0}, {})
        scenarios = analyzer.build_scenarios()
        self.assertEqual(scenarios['base']['net_income'], 0)
        self.assertEqual(scenarios['base']['net_profit_margin'], 0)
        self.assertEqual(analyzer.sensitivity_analysis('revenue'), [])

    def test_base_without_reported_net_income(self):
        """اختبار حساب صافي الربح عند غيابه من البيانات"""
        data = {
            'revenue': 100000,
            'cost_of_goods_sold': 60000,
            'operating_expenses': 20000,
            'total_assets': 200000,
            'equity': 80000,
        }
        analyzer = ScenarioAnalyzer(data, {})
        base = analyzer.build_scenarios()['base']
        # net = 100000 - 60000 - 20000 = 20000
        self.assertEqual(base['net_income'], 20000)


class TestScenarioDatabase(unittest.TestCase):
    """اختبارات حفظ/استرجاع السيناريوهات في قاعدة البيانات"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        cls.tmp_db.close()

        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name

        from database import db_connection as db_conn_module
        from database import db_operations
        from database import db_schema
        new_db = DatabaseConnection()
        db_conn_module.db = new_db
        db_operations.db = new_db
        db_schema.db = new_db

    @classmethod
    def tearDownClass(cls):
        import config
        config.DATABASE_PATH = cls.original_path
        from database import db_connection as db_conn_module
        db_conn_module.close_pool()
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)

    def setUp(self):
        if os.path.exists(self.tmp_db.name):
            conn = sqlite3.connect(self.tmp_db.name)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = [row[0] for row in cursor.fetchall()]
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                conn.commit()
            finally:
                conn.close()
        self.assertTrue(create_tables())

    def test_save_and_get_scenario_results(self):
        """اختبار حفظ واسترجاع نتائج السيناريوهات"""
        fy_id = save_analysis("شركة سيناريو", 2024, DATA, {})
        self.assertIsNotNone(fy_id)

        scenarios = ScenarioAnalyzer(DATA, {}).build_scenarios()
        self.assertTrue(save_scenario_results(fy_id, scenarios))

        results = get_scenario_results(fy_id)
        self.assertIn('best', results)
        self.assertIn('base', results)
        self.assertIn('worst', results)
        self.assertEqual(results['best']['net_income'], 46560)
        self.assertEqual(results['base']['net_income'], 20000)
        self.assertLess(results['worst']['net_income'], 0)

    def test_save_scenario_results_overwrites(self):
        """اختبار أن الحفظ الجديد يستبدل القديم"""
        fy_id = save_analysis("شركة سيناريو", 2024, DATA, {})
        analyzer = ScenarioAnalyzer(DATA, {})
        save_scenario_results(fy_id, analyzer.build_scenarios())

        modified = analyzer.build_scenarios(
            best={'revenue_change_pct': 0.50}
        )
        save_scenario_results(fy_id, modified)

        results = get_scenario_results(fy_id)
        self.assertEqual(len(results), 3)
        self.assertEqual(results['best']['revenue'], 150000)

    def test_get_scenario_results_empty(self):
        """اختبار الاسترجاع لسنة مالية بلا نتائج"""
        self.assertEqual(get_scenario_results(99999), {})


class TestScenarioReporting(unittest.TestCase):
    """اختبارات تقرير السيناريوهات"""

    def setUp(self):
        from modules.reporting import ReportGenerator
        self.reporter = ReportGenerator("شركة الاختبار", 2024)
        self.analyzer = ScenarioAnalyzer(DATA, {})

    def test_generate_scenario_report_sections(self):
        """اختبار أقسام تقرير السيناريوهات"""
        scenarios = self.analyzer.build_scenarios()
        report = self.reporter.generate_scenario_report(scenarios)
        self.assertIn('السيناريوهات', report)
        self.assertIn('شركة الاختبار', report)
        self.assertIn('الحالة المثالية', report)
        self.assertIn('أسوأ حالة', report)
        self.assertIn('الحالة الطبيعية', report)
        self.assertIn('20,000', report)

    def test_generate_scenario_report_with_comparison(self):
        """اختبار التقرير مع جدول المقارنة"""
        scenarios = self.analyzer.build_scenarios()
        comparison = self.analyzer.compare_scenarios(scenarios)
        report = self.reporter.generate_scenario_report(scenarios, comparison=comparison)
        self.assertIn('المقارنة', report)
        self.assertIn('الإيرادات', report)

    def test_generate_scenario_report_with_sensitivity(self):
        """اختبار التقرير مع تحليل الحساسية"""
        scenarios = self.analyzer.build_scenarios()
        sensitivity = self.analyzer.sensitivity_analysis('revenue')
        report = self.reporter.generate_scenario_report(scenarios, sensitivity=sensitivity)
        self.assertIn('الحساسية', report)
        self.assertIn('20.00%', report)


if __name__ == '__main__':
    unittest.main(verbosity=2)
