# Extra unit tests for modules/reporting.py (ReportGenerator).
# Covers the previously untested DuPont/scenario branches, the missing-font
# fallback paths in export_to_pdf and the export_to_excel method.

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl

from modules.reporting import ReportGenerator


class TestReportGeneratorExtra(unittest.TestCase):
    """Extra coverage for ReportGenerator edge branches."""

    def setUp(self):
        self.reporter = ReportGenerator("شركة الاختبار", 2024)
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _path(self, name):
        return os.path.join(self._tmp.name, name)

    # ===== generate_dupont_report =====

    def test_dupont_report_industry_gap_with_target(self):
        """Industry-gap recommendations append the sector average."""
        dupont = {"net_profit_margin": 3, "asset_turnover": 0.4,
                  "equity_multiplier": 1.8, "roe": 2.16}
        recommendations = [
            {"code": "rec_industry_gap", "company_value": 3.0, "target": 5.0},
        ]
        report = self.reporter.generate_dupont_report(
            dupont, None, None, recommendations
        )
        self.assertIn("(المتوسط: 5.0)", report)

    def test_dupont_report_recommendation_unknown_code(self):
        """Unknown recommendation codes fall back to the raw code."""
        dupont = {"net_profit_margin": 3, "asset_turnover": 0.4,
                  "equity_multiplier": 1.8, "roe": 2.16}
        report = self.reporter.generate_dupont_report(
            dupont, None, None, [{"code": "rec_custom"}]
        )
        self.assertIn("rec_custom", report)

    # ===== generate_scenario_report =====

    def test_scenario_report_skips_missing_scenarios(self):
        """Missing scenario entries are skipped without crashing."""
        scenarios = {
            "best": None,
            "base": {
                "assumptions": {"revenue_change_pct": 0.0,
                                "cost_change_pct": 0.0,
                                "efficiency_change_pct": 0.0},
                "revenue": 1000, "cogs": 600, "operating_expenses": 200,
                "net_income": 200, "net_profit_margin": 20.0,
                "asset_turnover": 1.2, "roa": 10.0, "roe": 15.0,
                "outcome": "base",
            },
            "worst": None,
        }
        report = self.reporter.generate_scenario_report(scenarios)
        self.assertIn("الحالة الطبيعية", report)

    def test_scenario_report_with_comparison_and_sensitivity(self):
        """Scenario report renders comparison and sensitivity tables."""
        scenarios = {
            "best": {"assumptions": {"revenue_change_pct": 0.2,
                                     "cost_change_pct": -0.1,
                                     "efficiency_change_pct": 0.1},
                     "revenue": 1200, "cogs": 500, "operating_expenses": 150,
                     "net_income": 300, "net_profit_margin": 25.0,
                     "asset_turnover": 1.5, "roa": 12.0, "roe": 18.0,
                     "outcome": "profit"},
            "base": {"assumptions": {"revenue_change_pct": 0.0,
                                     "cost_change_pct": 0.0,
                                     "efficiency_change_pct": 0.0},
                     "revenue": 1000, "cogs": 600, "operating_expenses": 200,
                     "net_income": 200, "net_profit_margin": 20.0,
                     "asset_turnover": 1.2, "roa": 10.0, "roe": 15.0,
                     "outcome": "base"},
            "worst": {"assumptions": {"revenue_change_pct": -0.2,
                                      "cost_change_pct": 0.1,
                                      "efficiency_change_pct": -0.1},
                      "revenue": 800, "cogs": 700, "operating_expenses": 250,
                      "net_income": -50, "net_profit_margin": -6.25,
                      "asset_turnover": 0.9, "roa": -2.0, "roe": -3.0,
                      "outcome": "loss"},
        }
        comparison = {
            "revenue": {"best": 1200, "base": 1000, "worst": 800},
            "net_income": {"best": 300, "base": 200, "worst": -50},
        }
        sensitivity = [
            {"pct_change": 0.10, "net_income": 220,
             "net_profit_margin": 22.0, "roe": 16.5},
            {"pct_change": -0.10, "net_income": 180,
             "net_profit_margin": 18.0, "roe": 13.5},
        ]
        report = self.reporter.generate_scenario_report(
            scenarios, comparison, sensitivity
        )
        self.assertIn("جدول المقارنة", report)
        self.assertIn("تحليل الحساسية", report)
        self.assertIn("الحالة المثالية", report)

    # ===== font-path helpers =====

    def test_arabic_font_paths_missing_return_none(self):
        """Font-path helpers return None when the fonts are absent."""
        with mock.patch("modules.reporting.os.path.exists", return_value=False):
            self.assertIsNone(self.reporter._get_arabic_font_path())
            self.assertIsNone(self.reporter._get_arabic_bold_font_path())

    def test_arabic_bold_font_path_found(self):
        """Bold font-path helper returns the path when the file exists."""
        path = self.reporter._get_arabic_bold_font_path()
        self.assertTrue(path is None or os.path.exists(path))

    # ===== export_to_pdf without Arabic font =====

    def test_export_to_pdf_without_arabic_font_success(self):
        """PDF export falls back to Helvetica when Amiri is unavailable."""
        ascii_reporter = ReportGenerator("Test Company", 2024)
        path = self._path("no_font.pdf")
        content = "\n=== REPORT ===\n---\nPlain ASCII line\nAnother line\n"
        with mock.patch.object(ReportGenerator, "_get_arabic_font_path",
                               return_value=None), \
             mock.patch.object(ReportGenerator, "_get_arabic_bold_font_path",
                               return_value=None):
            result = ascii_reporter.export_to_pdf(content, path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)

    def test_export_to_pdf_without_arabic_font_section_error(self):
        """Section glyphs unsupported by Helvetica make the export fail."""
        ascii_reporter = ReportGenerator("Test Company", 2024)
        path = self._path("no_font_section.pdf")
        content = "\u2550\u2550\u2550 TITLE \u2550\u2550\u2550\n---\n"
        with mock.patch.object(ReportGenerator, "_get_arabic_font_path",
                               return_value=None), \
             mock.patch.object(ReportGenerator, "_get_arabic_bold_font_path",
                               return_value=None):
            result = ascii_reporter.export_to_pdf(content, path)
        self.assertFalse(result)

    def test_export_to_pdf_arabic_without_font_fails_clearly(self):
        """Arabic content without Amiri fails with a clear error instead of a
        garbled PDF."""
        ascii_reporter = ReportGenerator("Test Company", 2024)
        path = self._path("arabic_no_font.pdf")
        content = "\nتقرير مالي باللغة العربية\n"
        with mock.patch.object(ReportGenerator, "_get_arabic_font_path",
                               return_value=None), \
             mock.patch.object(ReportGenerator, "_get_arabic_bold_font_path",
                               return_value=None), \
             self.assertLogs("reporting", level="ERROR") as cm:
            result = ascii_reporter.export_to_pdf(content, path)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(path))
        self.assertTrue(
            any("Amiri" in m and "Arabic" in m for m in cm.output),
            f"expected a clear Arabic-font error, got: {cm.output}",
        )

    def test_export_to_pdf_section_with_arabic_font(self):
        """Section glyphs render successfully when Amiri is available."""
        reporter = ReportGenerator("Company X", 2024)
        path = self._path("amiri_section.pdf")
        content = "\u2550\u2550\u2550 TITLE \u2550\u2550\u2550\n---\n"
        result = reporter.export_to_pdf(content, path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)

    # ===== export_to_excel =====

    def test_export_to_excel_full(self):
        """Export an Excel report with financial data and ratios."""
        financial_data = {
            "current_assets": 6000, "inventory": 3000, "total_assets": 11000,
            "current_liabilities": 3000, "total_liabilities": 5000,
            "equity": 6000, "revenue": 20000, "cost_of_goods_sold": 12000,
            "gross_profit": 8000, "net_income": 4000,
        }
        ratios = {"current_ratio": 2.0, "quick_ratio": 1.5,
                  "gross_profit_margin": 40.0, "net_profit_margin": 20.0,
                  "roa": 10.0, "roe": 15.0, "asset_turnover": 1.5,
                  "debt_to_equity": 0.5, "debt_ratio": 0.3}
        path = self._path("report.xlsx")
        result = self.reporter.export_to_excel(path, financial_data, ratios)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        wb = openpyxl.load_workbook(path)
        self.assertEqual(wb.sheetnames, ["Financial Report"])

    def test_export_to_excel_financial_only(self):
        """Export works when only financial data is provided."""
        path = self._path("fin_only.xlsx")
        result = self.reporter.export_to_excel(
            path, {"revenue": 100, "net_income": 10}
        )
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))

    def test_export_to_excel_ratios_only(self):
        """Export works when only ratios are provided."""
        path = self._path("ratios_only.xlsx")
        result = self.reporter.export_to_excel(path, None, {"roe": 12.0})
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))

    def test_export_to_excel_empty(self):
        """Export works with no financial data and no ratios."""
        path = self._path("empty.xlsx")
        result = self.reporter.export_to_excel(path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))

    def test_export_to_excel_save_error_returns_false(self):
        """A workbook save failure is reported as False."""
        path = self._path("fail.xlsx")
        with mock.patch.object(openpyxl.Workbook, "save",
                               side_effect=PermissionError("denied")):
            result = self.reporter.export_to_excel(path, {"revenue": 1})
        self.assertFalse(result)
        self.assertFalse(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
