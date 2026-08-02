# Edge-case and error-handling tests for the six target feature modules.
# Focus: zero/negative/large values, missing/invalid data, bad paths,
# corrupted files, and non-numeric inputs.

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.analysis import FinancialAnalyzer
from modules.scenarios import ScenarioAnalyzer
from modules.benchmarks import BenchmarkAnalyzer, ALGERIAN_SECTORS
from modules.ai_insights import AIInsightsEngine
from modules.tax import TaxEngine
from modules.demo_data import _generate_monthly_transactions
import modules.ai_insights as ai_insights
import modules.fraud_detection as fraud_detection


# ==================== analysis.py ====================

class TestAnalysisEdgeCases(unittest.TestCase):

    def test_comparative_lower_is_better_better_value(self):
        analyzer = FinancialAnalyzer({})
        result = analyzer.comparative_analysis(
            {"debt_to_equity": 0.5}, {"debt_to_equity": 1.0}
        )
        better = result["debt_to_equity"]
        self.assertEqual(better["difference"], -0.5)
        self.assertEqual(better["percentage_difference"], -50.0)

    def test_comparative_lower_is_better_worse_value(self):
        analyzer = FinancialAnalyzer({})
        result = analyzer.comparative_analysis(
            {"debt_to_equity": 2.0}, {"debt_to_equity": 1.0}
        )
        worse = result["debt_to_equity"]
        self.assertEqual(worse["difference"], 1.0)
        # A value above the industry average must not be flagged as better
        # than a value below it for a lower-is-better ratio.
        better = analyzer.comparative_analysis(
            {"debt_to_equity": 0.5}, {"debt_to_equity": 1.0}
        )["debt_to_equity"]
        self.assertNotEqual(worse["status"], better["status"])

    def test_interpret_dupont_mid_branches(self):
        analyzer = FinancialAnalyzer({})
        interpretation = analyzer._interpret_dupont(7, 1.2, 2.5)
        self.assertEqual(len(interpretation), 3)

    def test_interpret_dupont_high_leverage(self):
        analyzer = FinancialAnalyzer({})
        interpretation = analyzer._interpret_dupont(7, 1.2, 4)
        self.assertEqual(len(interpretation), 3)

    def test_dupont_industry_comparison_aligned(self):
        analyzer = FinancialAnalyzer({})
        bm = ALGERIAN_SECTORS["commercial"]["benchmarks"]
        dupont = {
            "net_profit_margin": bm["net_profit_margin"]["avg"],
            "asset_turnover": bm["asset_turnover"]["avg"],
            "equity_multiplier": round(1 + bm["debt_to_equity"]["avg"], 4),
            "roe": bm["roe"]["avg"],
        }
        result = analyzer.dupont_industry_comparison(dupont, "commercial")
        self.assertEqual(result["roe"]["status"], "aligned")
        self.assertEqual(result["net_profit_margin"]["status"], "aligned")

    def test_dupont_recommendations_ok_range(self):
        analyzer = FinancialAnalyzer({})
        dupont = {
            "net_profit_margin": 7,
            "asset_turnover": 1.0,
            "equity_multiplier": 2.5,
            "roe": 15,
        }
        recs = analyzer.dupont_recommendations(dupont)
        codes = {r["code"] for r in recs}
        self.assertIn("rec_npm_ok", codes)
        self.assertIn("rec_at_ok", codes)
        self.assertIn("rec_em_ok", codes)
        self.assertIn("rec_roe_ok", codes)

    def test_cash_flow_analysis_negative_operating(self):
        analyzer = FinancialAnalyzer({})
        result = analyzer.cash_flow_analysis(-10, 5, 5)
        self.assertEqual(result["total_cash_flow"], 0)
        self.assertEqual(len(result["analysis"]), 2)

    def test_generate_report_with_working_capital(self):
        analyzer = FinancialAnalyzer({})
        analyzer.analysis_results["working_capital"] = {
            "working_capital": 500, "operating_cycle": 300,
        }
        report = analyzer.generate_report()
        self.assertIn("500", report)
        self.assertIn("300", report)

    def test_dupont_analysis_zero_equity(self):
        analyzer = FinancialAnalyzer({})
        result = analyzer.dupont_analysis(1000, 10000, 5000, 0)
        self.assertEqual(result["equity_multiplier"], 0)
        self.assertEqual(result["roe"], 0)


# ==================== scenarios.py ====================

class TestScenariosEdgeCases(unittest.TestCase):

    def test_outcome_base_type(self):
        self.assertEqual(ScenarioAnalyzer._outcome(100, 50, "base"), "base")

    def test_sensitivity_invalid_variable_raises(self):
        analyzer = ScenarioAnalyzer({"revenue": 1000}, {})
        with self.assertRaises(ValueError):
            analyzer.sensitivity_analysis(variable="invalid_var")

    def test_save_scenarios_bad_path_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_path = os.path.join(tmp, "missing_dir", "x.json")
            ok = ScenarioAnalyzer.save_scenarios(
                {"best": {}, "base": {}, "worst": {}}, bad_path
            )
            self.assertFalse(ok)

    def test_load_scenarios_wrong_structure_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sc.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"foo": 1}, f)
            result = ScenarioAnalyzer.load_scenarios(path)
            self.assertEqual(result, {})


# ==================== benchmarks.py ====================

class TestBenchmarksEdgeCases(unittest.TestCase):

    def setUp(self):
        self.analyzer = BenchmarkAnalyzer()

    def test_compare_with_sector_skips_unknown_ratio(self):
        result = self.analyzer.compare_with_sector(
            {"net_profit_margin": 5, "unknown_ratio": 99}, "commercial"
        )
        self.assertNotIn("unknown_ratio", result["ratios"])
        self.assertIn("net_profit_margin", result["ratios"])

    def test_compare_with_sector_skips_none_value(self):
        result = self.analyzer.compare_with_sector(
            {"net_profit_margin": None, "current_ratio": 2.0}, "commercial"
        )
        self.assertNotIn("net_profit_margin", result["ratios"])
        self.assertIn("current_ratio", result["ratios"])

    def test_score_ratio_lower_is_better(self):
        bm = {"min": 0.2, "avg": 1.0, "max": 3.0,
              "ideal": (0.5, 1.5), "best_practice": 0.52, "international": 0.17}
        self.assertEqual(BenchmarkAnalyzer._score_ratio(0.4, bm, True), ("best", 100))
        self.assertEqual(BenchmarkAnalyzer._score_ratio(2.0, bm, True), ("above", 60))
        self.assertEqual(BenchmarkAnalyzer._score_ratio(5.0, bm, True), ("critical", 20))

    def test_score_ratio_higher_is_better(self):
        bm = {"min": 1, "avg": 5, "max": 15,
              "ideal": (3, 10), "best_practice": 11, "international": 18}
        self.assertEqual(BenchmarkAnalyzer._score_ratio(0.5, bm, False), ("critical", 0))
        self.assertEqual(BenchmarkAnalyzer._score_ratio(2.0, bm, False), ("below", 50))
        self.assertEqual(BenchmarkAnalyzer._score_ratio(5.0, bm, False), ("good", 90))
        self.assertEqual(BenchmarkAnalyzer._score_ratio(10.5, bm, False), ("above", 70))
        self.assertEqual(BenchmarkAnalyzer._score_ratio(13.0, bm, False), ("excellent", 85))
        self.assertEqual(BenchmarkAnalyzer._score_ratio(16.0, bm, False), ("best", 100))

    def test_get_rating_good_band(self):
        rating = self.analyzer._get_rating(60)
        self.assertEqual(rating["en"], "Good")

    def test_get_radar_data_invalid_sector(self):
        result = self.analyzer.get_radar_data({}, "nope")
        self.assertEqual(result["labels"], [])

    def test_suggest_improvements_invalid_sector(self):
        result = self.analyzer.suggest_improvements({}, "nope")
        self.assertEqual(result, [])

    def test_get_strengths_weaknesses_invalid_sector(self):
        result = self.analyzer.get_strengths_weaknesses({}, "nope")
        self.assertIn("error", result)
        self.assertEqual(result["strengths"], [])

    def test_compare_with_competitors_invalid_sector(self):
        result = self.analyzer.compare_with_competitors({}, "nope")
        self.assertIn("error", result)

    def test_get_international_standards_invalid_sector(self):
        self.assertEqual(self.analyzer.get_international_standards("nope"), {})


# ==================== ai_insights.py ====================

class TestAIInsightsEdgeCases(unittest.TestCase):

    def setUp(self):
        self.engine = AIInsightsEngine()

    def test_wrap_negative_last_with_positive_mean(self):
        result = self.engine.forecast([10, 20, -5], months=3)
        self.assertNotIn("error", result)
        self.assertEqual(result["last_value"], -5)

    def test_linear_forecast_flat_series_r2_none(self):
        result = self.engine.forecast([5, 5, 5, 5], months=2)
        self.assertIsNone(result["r2"])
        self.assertEqual(len(result["forecast"]), 2)

    def test_transaction_anomalies_empty(self):
        self.assertEqual(self.engine.detect_transaction_anomalies([]), [])

    def test_transaction_anomalies_too_few(self):
        self.assertEqual(self.engine.detect_transaction_anomalies([1, 2, 3]), [])

    def test_transaction_anomalies_iqr_zero(self):
        self.assertEqual(
            self.engine.detect_transaction_anomalies([100, 100, 100, 100]), []
        )

    def test_transaction_anomalies_scalar_items(self):
        anomalies = self.engine.detect_transaction_anomalies([100, 200, 300, 500, 2000])
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["amount"], 2000)

    def test_ratio_anomalies_skips_bad_values(self):
        current = {"roe": 15, "bad": "abc", "debt": 5, "npm": 3, "profit": 50}
        previous = {"roe": 10, "bad": "xyz", "debt": 0, "npm": None, "profit": 10}
        anomalies = self.engine.detect_ratio_anomalies(current, previous)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["ratio"], "profit")

    def test_severity_high(self):
        self.assertEqual(self.engine._severity(3.2), "high")

    def test_seasonality_all_zeros(self):
        result = self.engine._seasonality([0] * 24, 12)
        self.assertEqual(result["indexes"], [0.0] * 12)
        self.assertEqual(result["peak_month"], 1)
        self.assertEqual(result["complete_cycles"], 2)

    def test_cyclical_constant_series(self):
        # Perfectly flat detrended series => std == 0 => fallback cycle_length 1
        with mock.patch.object(
            ai_insights.np, "polyfit", return_value=(0.0, 5.0)
        ):
            result = self.engine._cyclical([5] * 10)
            self.assertEqual(result["cycle_length"], 1)
            self.assertEqual(result["stability"], 0.0)

    def test_cyclical_polyfit_exception_fallback(self):
        with mock.patch.object(
            ai_insights.np, "polyfit", side_effect=ValueError("bad")
        ):
            result = self.engine._cyclical([1, 3, 2, 5, 4, 6])
            self.assertIn("cycle_length", result)

    def test_recommendations_cash_mid_range(self):
        recs = self.engine.recommendations(ratios={}, cash=400, monthly_expenses=100)
        cash_recs = [r for r in recs if r["category"] == "cash"]
        self.assertEqual(len(cash_recs), 1)
        self.assertEqual(cash_recs[0]["priority"], "low")

    def test_alerts_medium_anomalies(self):
        alerts = self.engine.alerts(anomalies=[{"severity": "medium"}])
        messages = [a["message"] for a in alerts]
        self.assertIn("anomalies_medium", messages)

    def test_alerts_profit_slowdown(self):
        alerts = self.engine.alerts(forecasts={"profit": {"growth_rate_pct": -5}})
        messages = [a["message"] for a in alerts]
        self.assertIn("profit_slowdown", messages)

    def test_alerts_profit_declining(self):
        alerts = self.engine.alerts(forecasts={"profit": {"growth_rate_pct": -15}})
        messages = [a["message"] for a in alerts]
        self.assertIn("profit_declining", messages)

    def test_alerts_revenue_steady(self):
        alerts = self.engine.alerts(forecasts={"revenue": {"growth_rate_pct": 10}})
        messages = [a["message"] for a in alerts]
        self.assertIn("revenue_steady", messages)

    def test_alerts_revenue_high_growth(self):
        alerts = self.engine.alerts(forecasts={"revenue": {"growth_rate_pct": 18}})
        messages = [a["message"] for a in alerts]
        self.assertIn("revenue_growth", messages)


# ==================== tax.py ====================

class TestTaxEdgeCases(unittest.TestCase):

    def test_invalid_config_falls_back_to_default(self):
        engine = TaxEngine(config_path="Z:/nonexistent/tax_config.json")
        self.assertEqual(engine.config["country"], "Algeria")

    def test_reload_config_default_path(self):
        engine = TaxEngine()
        engine.reload_config()
        self.assertEqual(engine.get_config_year(), engine.config.get("year", 2025))

    def test_get_activity_types(self):
        engine = TaxEngine()
        self.assertEqual(len(engine.get_activity_types()), 8)

    def test_tva_collection_credit(self):
        engine = TaxEngine()
        result = engine.calculate_tva_collection(100, 200)
        self.assertEqual(result["status"], "to_receive")
        self.assertEqual(result["amount"], 100)

    def test_irg_zero_salary(self):
        engine = TaxEngine()
        result = engine.calculate_irg(0)
        self.assertEqual(result["irg_amount"], 0)
        self.assertEqual(result["monthly_irg"], 0)

    def test_build_das_data_all_zero(self):
        engine = TaxEngine()
        result = engine.build_das_data(0, 0, 0)
        self.assertEqual(result["cnas_employee_annual"], 0)
        self.assertEqual(result["irg_withheld_annual"], 0)
        self.assertEqual(result["net_payroll_annual"], 0)

    def test_get_obligations_default_month(self):
        engine = TaxEngine()
        obligations = engine.get_obligations(
            month=None, activity_type="other", monthly_payroll=0, annual_turnover=0
        )
        for ob in obligations:
            self.assertEqual(ob["month"], datetime.now().month)

    def test_ibs_rate_label_unknown(self):
        engine = TaxEngine()
        self.assertEqual(engine.get_ibs_rate_label("unknown_type"), "unknown_type")

    def test_ibs_rate_label_known(self):
        engine = TaxEngine()
        label = engine.get_ibs_rate_label("production")
        self.assertIsInstance(label, str)
        self.assertNotEqual(label, "production")

    def test_tva_items_and_exemptions(self):
        engine = TaxEngine()
        self.assertIsInstance(engine.get_tva_items(), list)
        self.assertIsInstance(engine.get_tva_exemptions(), list)

    def test_format_currency(self):
        engine = TaxEngine()
        self.assertEqual(engine.format_currency(1234.5), "1,234.50 DZD")


# ==================== fraud_detection.py ====================

class TestFraudDetectionErrorPaths(unittest.TestCase):

    def setUp(self):
        self._orig_log_file = fraud_detection.LOG_FILE
        self._tmp = tempfile.TemporaryDirectory()
        fraud_detection.LOG_FILE = os.path.join(self._tmp.name, "fraud_log.json")

    def tearDown(self):
        fraud_detection.LOG_FILE = self._orig_log_file
        self._tmp.cleanup()

    def test_load_corrupted_log_no_crash(self):
        with open(fraud_detection.LOG_FILE, "w", encoding="utf-8") as f:
            f.write("this is {not valid json")
        detector = fraud_detection.FraudDetector()
        self.assertEqual(detector.get_alert_count()["total"], 0)

    def test_load_generic_error_no_crash(self):
        with open(fraud_detection.LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        with mock.patch.object(fraud_detection.json, "load",
                               side_effect=RuntimeError("boom")):
            detector = fraud_detection.FraudDetector()
            self.assertEqual(detector.get_alert_count()["total"], 0)

    def test_save_error_bad_path_no_crash(self):
        fraud_detection.LOG_FILE = os.path.join(
            self._tmp.name, "no_such_dir", "fraud_log.json"
        )
        detector = fraud_detection.FraudDetector()
        detector._alerts.append({"x": 1})
        detector._dirty = True
        detector._save()
        self.assertFalse(os.path.exists(fraud_detection.LOG_FILE))

    def test_flush_saves_when_dirty(self):
        detector = fraud_detection.FraudDetector()
        detector.check_data_change("revenue", 100, 150, user="tester")
        self.assertTrue(detector._dirty)
        detector.flush()
        self.assertTrue(os.path.exists(fraud_detection.LOG_FILE))
        self.assertFalse(detector._dirty)

    def test_check_data_change_non_numeric_old_value(self):
        detector = fraud_detection.FraudDetector()
        alerts = detector.check_data_change("revenue", "abc", 100, user="tester")
        self.assertEqual(alerts, [])

    def test_check_data_change_non_numeric_new_value(self):
        detector = fraud_detection.FraudDetector()
        alerts = detector.check_data_change("revenue", 100, "not-a-number", user="tester")
        self.assertEqual(alerts, [])


# ==================== final 99% line closers ====================

class TestFinalLineClosers(unittest.TestCase):

    def test_dupont_industry_comparison_na_when_avg_zero(self):
        from modules.benchmarks import ALGERIAN_SECTORS as sectors
        analyzer = FinancialAnalyzer({})
        orig = sectors["commercial"]["benchmarks"]["roe"]["avg"]
        try:
            sectors["commercial"]["benchmarks"]["roe"]["avg"] = 0
            result = analyzer.dupont_industry_comparison(
                {"net_profit_margin": 5, "asset_turnover": 1,
                 "equity_multiplier": 2, "roe": 12}, "commercial"
            )
            self.assertEqual(result["roe"]["status"], "n/a")
        finally:
            sectors["commercial"]["benchmarks"]["roe"]["avg"] = orig

    def test_radar_max_zero_falls_back_to_one(self):
        from modules.benchmarks import ALGERIAN_SECTORS as sectors
        analyzer = BenchmarkAnalyzer()
        orig = sectors["commercial"]["benchmarks"]["roe"]["max"]
        try:
            sectors["commercial"]["benchmarks"]["roe"]["max"] = 0
            result = analyzer.get_radar_data({"roe": 10}, "commercial")
            self.assertEqual(result["company"][0], 100.0)
        finally:
            sectors["commercial"]["benchmarks"]["roe"]["max"] = orig

    def test_compare_with_competitors_skips_error_entry(self):
        analyzer = BenchmarkAnalyzer()
        with mock.patch.object(
            analyzer, "compare_with_sector", return_value={"error": "boom"}
        ):
            result = analyzer.compare_with_competitors(
                {"roe": 10}, "commercial",
                competitors=[{"name": "c", "ratios": {}}],
            )
        self.assertEqual(result["ranking"], [])
        self.assertEqual(result["count"], 0)

    def test_get_international_standards_valid_sector(self):
        analyzer = BenchmarkAnalyzer()
        result = analyzer.get_international_standards("commercial")
        self.assertIn("net_profit_margin", result)
        self.assertIsInstance(result["net_profit_margin"], (int, float))

    def test_generate_monthly_transactions_unknown_company(self):
        self.assertEqual(_generate_monthly_transactions("unknown_company"), [])

    def test_r2_exception_returns_none(self):
        engine = AIInsightsEngine()
        with mock.patch.object(ai_insights.np, "mean", side_effect=RuntimeError("x")):
            self.assertIsNone(engine._r2([1, 2, 3], [1, 2, 3]))


if __name__ == "__main__":
    unittest.main()
