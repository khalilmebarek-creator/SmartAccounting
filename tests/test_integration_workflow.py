# اختبارات تكامل سير العمل (Workflow Testing)
# ===========================================
# يجمع هذا الملف سيناريوهات مستخدم كاملة (User Journeys) تربط بين عدة وحدات:
#   demo_data → calculations → analysis → audit → tax → reporting → تصدير
#   comparative → benchmarks → ai_insights
#   AppState (إدارة الحالة) → save/load/clear
#   تدفق البيانات (Data Flow) والاتساق بين المخرجات

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.calculations import CalculationEngine
from modules.analysis import FinancialAnalyzer
from modules.audit import AuditEngine
from modules.tax import TaxEngine
from modules.reporting import ReportGenerator
from modules.demo_data import DemoData, DEMO_COMPANIES
from modules.comparative import ComparativeAnalyzer
from modules.benchmarks import BenchmarkAnalyzer
from modules.ai_insights import AIInsightsEngine


def _demo_financial(company_id="retail"):
    return dict(DEMO_COMPANIES[company_id]["financial_data"])


class TestFullUserJourney(unittest.TestCase):
    """رحلة مستخدم كاملة: إدخال بيانات → نسب → تحليل → تدقيق → جباية → تقرير → تصدير"""

    def test_journey_demo_data_to_exported_report(self):
        # 1) بيانات مالية جاهزة (إدخال بيانات)
        fin = _demo_financial("retail")
        self.assertTrue(fin["revenue"] > 0)

        # 2) حساب 20 نسبة مالية
        engine = CalculationEngine()
        ratios = engine.calculate_all_ratios(fin)
        self.assertIsNotNone(ratios)
        self.assertEqual(len(ratios), 20)
        self.assertIn("current_ratio", ratios)
        self.assertIn("roe", ratios)

        # 3) تحليل DuPont + رأس المال العامل (يُخزن في analysis_results)
        analyzer = FinancialAnalyzer(fin)
        dupont = analyzer.dupont_analysis(
            fin["net_income"], fin["revenue"], fin["total_assets"], fin["equity"]
        )
        self.assertAlmostEqual(dupont["roe"], ratios["roe"], delta=0.5)
        wc = analyzer.working_capital_analysis(
            fin["current_assets"], fin["current_liabilities"], fin["inventory"]
        )
        self.assertIn("status", wc)
        self.assertIn("dupont", analyzer.analysis_results)

        # 4) تدقيق مالي — البيانات التجريبية يجب ألا تنتج مشاكل جوهرية
        auditor = AuditEngine()
        self.assertTrue(auditor.check_balance_sheet(
            fin["total_assets"], fin["total_liabilities"], fin["equity"]))
        self.assertTrue(auditor.check_negative_values(fin))
        auditor.check_ratios_reasonableness(ratios)
        summary = auditor.get_audit_summary()
        self.assertIn("total_issues", summary)

        # 5) محاكاة جبائية كاملة
        tax = TaxEngine()
        sim = tax.simulate(
            revenue=fin["revenue"],
            cogs=fin["cost_of_goods_sold"],
            operating_expenses=fin.get("operating_expenses", 0),
            total_assets=fin["total_assets"],
            total_liabilities=fin["total_liabilities"],
            equity=fin["equity"],
            number_of_employees=10,
            avg_salary=35000,
            activity_type="commercial",
        )
        self.assertGreater(sim["total_taxes"], 0)
        self.assertIn("ibs", sim)
        self.assertIn("tax_burden_pct", sim)
        self.assertGreater(sim["net_income_after_taxes"], 0)

        # 6) توليد تقرير شامل وتصديره
        reporter = ReportGenerator("شركة الأمل للتجارة العامة", 2024)
        report = reporter.generate_comprehensive_report(
            balance_sheet=fin, income_statement=fin, ratios=ratios, analysis=analyzer.generate_report()
        )
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 100)

        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "report.txt")
            ok = reporter.export_report_to_file(report, out)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(out))
            with open(out, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertGreater(len(content), 100)

    def test_journey_multi_year_comparative_benchmarks_ai(self):
        # 1) مقارنة متعددة السنوات بين شركتين
        comp = ComparativeAnalyzer({
            2023: _demo_financial("retail"),
            2024: _demo_financial("services"),
        })
        comparison = comp.get_comparison()
        self.assertEqual(comparison["years"], [2023, 2024])
        self.assertIn("ratios_by_year", comparison)
        self.assertIn("item_changes", comparison)

        # 2) المعايير المرجعية للقطاع
        ratios24 = comparison["ratios_by_year"][2024]
        bench = BenchmarkAnalyzer()
        sector = bench.compare_with_sector(ratios24, "services")
        self.assertNotIn("error", sector)
        self.assertIn("overall_score", sector)
        self.assertIn("strengths", sector)
        self.assertIn("weaknesses", sector)

        # 3) الرؤى الذكية من سلسلة شهرية
        monthly = DemoData.get_monthly_transactions("retail")
        revenue_series = [m["revenue"] for m in monthly]
        expense_series = [m["operating_expenses"] for m in monthly]
        profit_series = [m["net_income"] for m in monthly]
        ai = AIInsightsEngine()
        insights = ai.generate_insights(
            revenue_history=revenue_series,
            expense_history=expense_series,
            profit_history=profit_series,
            transactions=monthly,
            ratios=ratios24,
        )
        self.assertIn("forecasts", insights)
        self.assertIn("anomalies", insights)
        self.assertIn("recommendations", insights)
        self.assertIn("alerts", insights)


class TestStateManagementJourney(unittest.TestCase):
    """رحلة إدارة الحالة: تحميل شركة → حساب → حفظ → إعادة تحميل → مسح"""

    def setUp(self):
        import ui.app_state as app_state_module
        self._app_state_module = app_state_module
        self._tmpdir = tempfile.TemporaryDirectory()
        # توجيه ملفات الحالة إلى مجلد مؤقت (حماية الملفات الحقيقية)
        app_state_module.SETTINGS_FILE = os.path.join(self._tmpdir.name, "settings.json")
        app_state_module.DATA_FILE = os.path.join(self._tmpdir.name, "accounting_data.json")
        app_state_module.CHAT_FILE = os.path.join(self._tmpdir.name, "chat_history.json")

    def tearDown(self):
        self._tmpdir.cleanup()

    def _new_state(self):
        return self._app_state_module.AppState()

    def test_load_company_populates_all_state(self):
        state = self._new_state()
        ok = DemoData.load_company(state, "retail")
        self.assertTrue(ok)
        self.assertEqual(state.company_name, DEMO_COMPANIES["retail"]["company_name"])
        self.assertEqual(state.fiscal_year, DEMO_COMPANIES["retail"]["fiscal_year"])
        self.assertTrue(state.has_data())
        self.assertTrue(state.ratios)          # 20 نسبة محسوبة
        self.assertIn("roe", state.ratios)
        self.assertTrue(state.dupont)          # تحليل DuPont
        self.assertTrue(state.working_capital)  # رأس المال العامل

    def test_save_then_reload_roundtrip(self):
        state = self._new_state()
        DemoData.load_company(state, "services")
        ratios_before = dict(state.ratios)
        state.save_data()

        # حالة جديدة تقرأ من نفس الملف
        state2 = self._new_state()
        self.assertEqual(state2.company_name, state.company_name)
        self.assertEqual(state2.fiscal_year, state.fiscal_year)
        self.assertEqual(state2.ratios, ratios_before)
        self.assertEqual(state2.financial_data["revenue"], state.financial_data["revenue"])

    def test_clear_resets_state_and_disk(self):
        state = self._new_state()
        DemoData.load_company(state, "manufacturing")
        self.assertTrue(state.has_data())
        state.clear()
        self.assertFalse(state.has_data())
        self.assertEqual(state.company_name, "")
        self.assertEqual(state.ratios, {})

    def test_state_drives_ratios_and_report(self):
        state = self._new_state()
        DemoData.load_company(state, "import_export")
        self.assertEqual(len(state.ratios), 20)
        summary = state.summary()
        self.assertIsInstance(summary, str)
        self.assertIn(DEMO_COMPANIES["import_export"]["company_name"], summary)


class TestDataFlowConsistency(unittest.TestCase):
    """التأكد من اتساق البيانات عبر سلسلة الوحدات (Data Flow)"""

    def test_ratios_consistent_with_analysis_and_audit(self):
        for cid in ("retail", "services", "manufacturing", "import_export"):
            fin = _demo_financial(cid)
            ratios = CalculationEngine().calculate_all_ratios(fin)

            # ROE عبر المحرك = ROE عبر DuPont (مع فارق التقريب)
            dupont = FinancialAnalyzer(fin).dupont_analysis(
                fin["net_income"], fin["revenue"], fin["total_assets"], fin["equity"])
            self.assertAlmostEqual(dupont["roe"], ratios["roe"], delta=0.6, msg=cid)

            # زاوية التدقيق — الميزانية والإشارات الصحيحة
            auditor = AuditEngine()
            self.assertTrue(auditor.check_balance_sheet(
                fin["total_assets"], fin["total_liabilities"], fin["equity"]), msg=cid)
            self.assertTrue(auditor.check_negative_values(fin), msg=cid)

            # اتساق قائمة الدخل الكاملة (الديمو يتضمن بنود أخرى):
            # operating_income + other_income - other_expenses = net_income
            operating = fin.get("operating_income",
                                fin["revenue"] - fin["cost_of_goods_sold"]
                                - fin.get("operating_expenses", 0))
            self.assertAlmostEqual(
                operating + fin.get("other_income", 0) - fin.get("other_expenses", 0),
                fin["net_income"], delta=1.0, msg=cid)

        # التدقيق الصارم يجب أن يكتشف عدم تطابق في بيانات غير متسقة
        auditor = AuditEngine()
        self.assertFalse(auditor.check_income_statement(100, 40, 30, 50))

    def test_comparative_ratio_matches_single_year_engine(self):
        fin = _demo_financial("retail")
        ratios = CalculationEngine().calculate_all_ratios(fin)
        comp = ComparativeAnalyzer({2024: fin}).get_comparison()
        for key in ("current_ratio", "roe", "net_profit_margin"):
            self.assertAlmostEqual(
                comp["ratios_by_year"][2024][key], ratios[key], delta=0.01, msg=key)

    def test_cashflow_bridges_financial_data_and_reporting(self):
        from modules.cashflow import CashFlowStatement
        fin = _demo_financial("retail")
        cashflow = CashFlowStatement().calculate(fin)
        self.assertIn("operating", cashflow)
        self.assertIn("net_change", cashflow)
        self.assertIn("ending_cash", cashflow)
        # القائمة النصية قابلة للتصدير لاحقاً
        report = CashFlowStatement().generate_report(cashflow)
        self.assertGreater(len(report), 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
