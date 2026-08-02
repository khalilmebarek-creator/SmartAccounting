# Unit tests for modules/calculations.py, modules/report_templates.py and
# modules/activity_log.py. Focus: error-handling branches, file I/O failure
# paths, and report/audit helpers.

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.calculations import CalculationEngine
from modules.report_templates import ReportTemplates
import modules.report_templates as report_templates_module
import modules.activity_log as activity_log_module
from modules.activity_log import ActivityLog


# ==================== calculations.py ====================

class TestCalculationEngineErrorPaths(unittest.TestCase):
    """Tests for CalculationEngine exception branches and print_ratios."""

    def setUp(self):
        self.engine = CalculationEngine()
        self.valid_data = {
            "current_assets": 100000,
            "inventory": 20000,
            "current_liabilities": 50000,
            "cash": 8000,
            "gross_profit": 30000,
            "operating_expenses": 15000,
            "net_income": 15000,
            "revenue": 200000,
            "total_assets": 500000,
            "equity": 300000,
            "cost_of_goods_sold": 120000,
            "average_receivables": 40000,
            "average_inventory": 25000,
            "average_payables": 18000,
            "total_liabilities": 200000,
        }

    def test_calculate_all_ratios_none_input_caught(self):
        data = dict(self.valid_data)
        data["current_assets"] = None
        ratios = self.engine.calculate_all_ratios(data)
        self.assertIsNotNone(ratios)
        self.assertEqual(ratios["current_ratio"], 0)
        self.assertEqual(ratios["quick_ratio"], 0)
        self.assertEqual(ratios["net_profit_margin"], 7.5)

    def test_calculate_all_ratios_missing_optional_fields(self):
        data = dict(self.valid_data)
        data.pop("cash", None)
        data.pop("average_payables", None)
        data.pop("operating_expenses", None)
        data.pop("operating_income", None)
        ratios = self.engine.calculate_all_ratios(data)
        self.assertIsNotNone(ratios)
        self.assertEqual(ratios["cash_ratio"], 0)
        self.assertEqual(ratios["payables_turnover"], 0)

    def test_calculate_all_ratios_missing_key_returns_none(self):
        data = dict(self.valid_data)
        del data["equity"]
        self.assertIsNone(self.engine.calculate_all_ratios(data))

    def test_days_sales_outstanding_failure_sets_zero(self):
        with mock.patch.object(self.engine, "days_sales_outstanding",
                               side_effect=ValueError("boom")):
            ratios = self.engine.calculate_all_ratios(self.valid_data)
        self.assertEqual(ratios["days_sales_outstanding"], 0)

    def test_days_inventory_outstanding_failure_sets_zero(self):
        with mock.patch.object(self.engine, "days_inventory_outstanding",
                               side_effect=ValueError("boom")):
            ratios = self.engine.calculate_all_ratios(self.valid_data)
        self.assertEqual(ratios["days_inventory_outstanding"], 0)

    def test_days_payable_outstanding_failure_sets_zero(self):
        with mock.patch.object(self.engine, "days_payable_outstanding",
                               side_effect=ValueError("boom")):
            ratios = self.engine.calculate_all_ratios(self.valid_data)
        self.assertEqual(ratios["days_payable_outstanding"], 0)

    def test_operating_cycle_failure_sets_zero(self):
        with mock.patch.object(self.engine, "operating_cycle",
                               side_effect=ValueError("boom")):
            ratios = self.engine.calculate_all_ratios(self.valid_data)
        self.assertEqual(ratios["operating_cycle"], 0)

    def test_cash_conversion_cycle_failure_sets_zero(self):
        with mock.patch.object(self.engine, "cash_conversion_cycle",
                               side_effect=ValueError("boom")):
            ratios = self.engine.calculate_all_ratios(self.valid_data)
        self.assertEqual(ratios["cash_conversion_cycle"], 0)

    def test_print_ratios_empty_inputs(self):
        self.engine.print_ratios(None)
        self.engine.print_ratios({})

    def test_print_ratios_full_output(self):
        ratios = {
            "current_ratio": 2.0, "quick_ratio": 1.6, "cash_ratio": 0.16,
            "gross_profit_margin": 15.0, "operating_profit_margin": 7.5,
            "net_profit_margin": 7.5, "roa": 3.0, "roe": 5.0,
            "asset_turnover": 0.4, "receivables_turnover": 5.0,
            "days_sales_outstanding": 73, "inventory_turnover": 4.8,
            "days_inventory_outstanding": 76, "payables_turnover": 6.67,
            "days_payable_outstanding": 55, "operating_cycle": 149,
            "cash_conversion_cycle": 94, "debt_to_equity": 0.67,
            "debt_ratio": 0.4, "equity_ratio": 0.6,
        }
        self.engine.print_ratios(ratios)


class TestZScoreAdditional(unittest.TestCase):
    """Tests for the Altman Z-Score zone classification."""

    def setUp(self):
        self.engine = CalculationEngine()

    def test_safe_zone(self):
        result = self.engine.z_score(
            working_capital=800000, retained_earnings=600000, ebit=400000,
            market_value_equity=3000000, book_value_debt=800000,
            sales=2400000, total_assets=2000000)
        self.assertEqual(result["status"], "safe")
        self.assertGreater(result["z_score"], 2.99)

    def test_grey_zone(self):
        result = self.engine.z_score(
            working_capital=500000, retained_earnings=250000, ebit=150000,
            market_value_equity=1200000, book_value_debt=900000,
            sales=1500000, total_assets=2000000)
        self.assertEqual(result["status"], "grey")

    def test_danger_zone(self):
        result = self.engine.z_score(
            working_capital=50000, retained_earnings=30000, ebit=20000,
            market_value_equity=150000, book_value_debt=1000000,
            sales=100000, total_assets=500000)
        self.assertEqual(result["status"], "danger")

    def test_zero_total_assets(self):
        result = self.engine.z_score(0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(result["z_score"], 0)
        self.assertEqual(result["status"], "danger")
        self.assertEqual(result["components"], {})

    def test_zero_book_value_debt(self):
        result = self.engine.z_score(
            working_capital=500000, retained_earnings=300000, ebit=200000,
            market_value_equity=1500000, book_value_debt=0,
            sales=1200000, total_assets=2000000)
        self.assertEqual(result["components"]["x4"], 0)


# ==================== report_templates.py ====================

class TestReportTemplates(unittest.TestCase):
    """Tests for ReportTemplates CRUD, load/save failure paths and HTML."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._patcher = mock.patch("modules.report_templates.TEMPLATES_DIR", self._tmp.name)
        self._patcher.start()
        self.addCleanup(self._patcher.stop)
        self.addCleanup(self._tmp.cleanup)
        self.rt = ReportTemplates()

    def test_load_corrupted_custom_templates(self):
        with open(os.path.join(self._tmp.name, "custom_templates.json"), "w", encoding="utf-8") as f:
            f.write("{not valid json")
        rt = ReportTemplates()
        self.assertIn("financial_summary", rt.get_all_templates())

    def test_load_generic_error_falls_back_to_defaults(self):
        with open(os.path.join(self._tmp.name, "custom_templates.json"), "w", encoding="utf-8") as f:
            json.dump({"custom": {}}, f)
        with mock.patch.object(report_templates_module.json, "load",
                               side_effect=RuntimeError("boom")):
            rt = ReportTemplates()
        self.assertIn("financial_summary", rt.get_all_templates())

    def test_save_failure_is_caught(self):
        with mock.patch.object(report_templates_module.json, "dump",
                               side_effect=OSError("disk full")):
            ok = self.rt.create_template("custom_x", {"name": "X", "sections": []})
        self.assertTrue(ok)

    def test_create_default_template_id_returns_false(self):
        self.assertFalse(self.rt.create_template("financial_summary", {"name": "X"}))

    def test_create_custom_template_persists(self):
        ok = self.rt.create_template("my_template", {"name": "Mine", "sections": ["summary"]})
        self.assertTrue(ok)
        self.assertEqual(self.rt.get_template("my_template")["name"], "Mine")

    def test_update_template_existing(self):
        ok = self.rt.update_template("financial_summary", {"format": "excel"})
        self.assertTrue(ok)
        self.assertEqual(self.rt.get_template("financial_summary")["format"], "excel")

    def test_update_template_missing_returns_false(self):
        self.assertFalse(self.rt.update_template("no_such_template", {"x": 1}))

    def test_update_default_template_does_not_corrupt_defaults(self):
        original = report_templates_module.DEFAULT_TEMPLATES["financial_summary"]["format"]
        self.rt.update_template("financial_summary", {"format": "excel"})
        self.assertEqual(
            report_templates_module.DEFAULT_TEMPLATES["financial_summary"]["format"],
            original,
        )
        self.assertEqual(self.rt.get_template("financial_summary")["format"], "excel")

    def test_delete_default_template_returns_false(self):
        self.assertFalse(self.rt.delete_template("financial_summary"))

    def test_delete_missing_template_returns_false(self):
        self.assertFalse(self.rt.delete_template("never_created"))

    def test_delete_custom_template(self):
        self.rt.create_template("to_delete", {"name": "X"})
        self.assertTrue(self.rt.delete_template("to_delete"))
        self.assertIsNone(self.rt.get_template("to_delete"))

    def test_get_sections_known_template(self):
        self.assertEqual(self.rt.get_sections_for_template("financial_summary"),
                         ["balance_sheet", "income_statement", "ratios", "charts"])

    def test_get_sections_unknown_template(self):
        self.assertEqual(self.rt.get_sections_for_template("nope"), [])

    def test_generate_report_header_known(self):
        header = self.rt.generate_report_header("financial_summary", "ACME SARL")
        self.assertIn("التقرير المالي الشامل", header)
        self.assertIn("ACME SARL", header)
        self.assertIn("<!DOCTYPE html>", header)
        self.assertIn("</div>", header)

    def test_generate_report_header_unknown_uses_default_title(self):
        header = self.rt.generate_report_header("unknown_id")
        self.assertIn("تقرير", header)

    def test_generate_report_footer(self):
        footer = self.rt.generate_report_footer()
        self.assertIn("Smart Accounting Platform", footer)
        self.assertIn("Generated:", footer)
        self.assertIn("</html>", footer)


# ==================== activity_log.py ====================

class TestActivityLog(unittest.TestCase):
    """Tests for ActivityLog load/save failures, log variants and summary."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_log_file = activity_log_module.LOG_FILE
        self._orig_audit_dir = activity_log_module.AUDIT_DIR
        activity_log_module.LOG_FILE = os.path.join(self._tmp.name, "activity_log.json")
        activity_log_module.AUDIT_DIR = os.path.join(self._tmp.name, "audit_trails")
        self.log = activity_log_module.ActivityLog()

    def tearDown(self):
        activity_log_module.LOG_FILE = self._orig_log_file
        activity_log_module.AUDIT_DIR = self._orig_audit_dir
        self._tmp.cleanup()

    def test_load_corrupted_log(self):
        with open(activity_log_module.LOG_FILE, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        log = activity_log_module.ActivityLog()
        self.assertEqual(len(log.get_entries()), 0)

    def test_load_generic_error_no_crash(self):
        with open(activity_log_module.LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        with mock.patch.object(activity_log_module.json, "load",
                               side_effect=RuntimeError("boom")):
            log = activity_log_module.ActivityLog()
        self.assertEqual(len(log.get_entries()), 0)

    def test_save_failure_is_caught(self):
        with mock.patch.object(activity_log_module.json, "dump",
                               side_effect=OSError("disk full")):
            self.log.log("test_action")
            self.log.flush()
        self.assertTrue(self.log._dirty)
        self.assertEqual(len(self.log.get_entries()), 1)

    def test_set_current_user(self):
        self.log.set_current_user("alice")
        self.assertEqual(self.log._current_user, "alice")

    def test_set_current_user_empty_falls_back(self):
        self.log.set_current_user("")
        self.assertEqual(self.log._current_user, "system")
        self.log.set_current_user(None)
        self.assertEqual(self.log._current_user, "system")

    def test_flush_saves_when_dirty(self):
        self.log.log("test_action")
        self.assertTrue(self.log._dirty)
        self.log.flush()
        self.assertFalse(self.log._dirty)
        self.assertTrue(os.path.exists(activity_log_module.LOG_FILE))

    def test_flush_skips_when_clean(self):
        with mock.patch.object(self.log, "_save") as mock_save:
            self.log.flush()
        mock_save.assert_not_called()

    def test_log_stores_old_and_new_values(self):
        entry_id = self.log.log("edit", old_value=5, new_value=10)
        entry = self.log.get_entries()[0]
        self.assertEqual(entry["id"], entry_id)
        self.assertEqual(entry["old_value"], "5")
        self.assertEqual(entry["new_value"], "10")

    def test_log_change(self):
        entry_id = self.log.log_change("invoice", "INV-001", "amount", 100, 150)
        entry = self.log.get_entries()[0]
        self.assertEqual(entry["id"], entry_id)
        self.assertEqual(entry["action"], "edit_invoice")
        self.assertIn("INV-001", entry["details"])
        self.assertEqual(entry["old_value"], "100")
        self.assertEqual(entry["new_value"], "150")

    def test_log_auth_success(self):
        self.log.log_auth("login", "alice", True)
        entry = self.log.get_entries()[0]
        self.assertEqual(entry["action"], "auth_login_success")
        self.assertEqual(entry["category"], "auth")
        self.assertEqual(entry["user"], "alice")
        self.assertIn("SUCCESS", entry["details"])

    def test_log_auth_failed(self):
        self.log.log_auth("login", "alice", False)
        entry = self.log.get_entries()[0]
        self.assertEqual(entry["action"], "auth_login_failed")
        self.assertIn("FAILED", entry["details"])

    def test_log_export(self):
        self.log.log_export("pdf", "report.pdf", user="bob")
        entry = self.log.get_entries()[0]
        self.assertEqual(entry["action"], "export")
        self.assertEqual(entry["category"], "report")
        self.assertEqual(entry["user"], "bob")
        self.assertIn("report.pdf", entry["details"])

    def test_log_backup(self):
        self.log.log_backup("create", "backup_2026.zip")
        entry = self.log.get_entries()[0]
        self.assertEqual(entry["action"], "backup_create")
        self.assertEqual(entry["category"], "backup")
        self.assertIn("backup_2026.zip", entry["details"])

    def test_get_entries_filters(self):
        self.log.log("open", category="data", user="u1")
        self.log.log("print", category="report", user="u2")
        self.log.log("save", category="data", user="u2")
        self.assertEqual(len(self.log.get_entries(category="data")), 2)
        self.assertEqual(len(self.log.get_entries(category="report")), 1)
        self.assertEqual(len(self.log.get_entries(category="nope")), 0)
        self.assertEqual(len(self.log.get_entries(user="u2")), 2)
        self.assertEqual(len(self.log.get_entries(user="nobody")), 0)
        self.assertEqual(len(self.log.get_entries(action="save")), 1)
        self.assertEqual(len(self.log.get_entries(action="nonexistent")), 0)

    def test_get_entries_limit(self):
        for i in range(5):
            self.log.log(f"action_{i}")
        entries = self.log.get_entries(limit=2)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[-1]["action"], "action_4")

    def test_get_summary(self):
        self.log.log("a1", category="data", user="u1")
        self.log.log("a2", category="report", user="u2")
        self.log.log("a3", category="data", user="u1")
        summary = self.log.get_summary()
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["by_category"], {"data": 2, "report": 1})
        self.assertEqual(summary["by_user"], {"u1": 2, "u2": 1})
        self.assertEqual(len(summary["recent_actions"]), 3)
        self.assertEqual(summary["recent_actions"][0]["action"], "a1")

    def test_get_summary_empty(self):
        summary = self.log.get_summary()
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["by_category"], {})
        self.assertEqual(summary["by_user"], {})
        self.assertEqual(summary["recent_actions"], [])

    def test_export_audit_trail_default_filename(self):
        self.log.log("export_me")
        path = self.log.export_audit_trail()
        self.assertTrue(path.startswith(activity_log_module.AUDIT_DIR))
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)

    def test_export_audit_trail_custom_filename(self):
        self.log.log("export_me")
        path = self.log.export_audit_trail("my_trail.json")
        self.assertEqual(path, os.path.join(activity_log_module.AUDIT_DIR, "my_trail.json"))
        self.assertTrue(os.path.exists(path))

    def test_maybe_flush_saves_at_threshold(self):
        for i in range(10):
            self.log.log(f"action_{i}")
        self.assertFalse(self.log._dirty)
        self.assertTrue(os.path.exists(activity_log_module.LOG_FILE))

    def test_clear_empties_and_saves(self):
        self.log.log("before_clear")
        self.log.clear()
        self.assertEqual(len(self.log.get_entries()), 0)
        self.assertFalse(self.log._dirty)
        self.assertTrue(os.path.exists(activity_log_module.LOG_FILE))


if __name__ == "__main__":
    unittest.main()
