# اختبار التقرير التنفيذي الشامل
# ================================
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.app_state import state


class TestExecutiveReportModule(unittest.TestCase):
    """محرك التقرير التنفيذي: تجميع سليم + مخرجات نص/HTML."""

    def setUp(self):
        state.clear()

    def tearDown(self):
        state.clear()

    def test_build_report_has_all_sections(self):
        import modules.executive_report as er
        report = er.build_report()
        for key in ("health_score", "executive_summary", "recommendations",
                    "key_ratios", "balance_sheet", "income_statement",
                    "cash_flow", "equity_statement", "tax_rows"):
            self.assertIn(key, report)

    def test_key_ratios_align_with_labels(self):
        import modules.executive_report as er
        ratio_keys = [k for k, _ in er.KEY_RATIOS]
        self.assertIn("current_ratio", ratio_keys)
        self.assertIn("z_score", ratio_keys)
        self.assertEqual(len(er.KEY_RATIOS), len(set(ratio_keys)),
                         "duplicate ratio keys in KEY_RATIOS")

    def test_render_html_contains_title(self):
        import modules.executive_report as er
        from ui.resources.i18n import t
        report = er.build_report()
        html = er.render_html(report)
        self.assertIn(t("er_title"), html)

    def test_render_text_is_nonempty(self):
        import modules.executive_report as er
        report = er.build_report()
        text = er.render_text(report)
        self.assertTrue(len(text) > 0)

    def test_tax_rows_empty_without_summary(self):
        import modules.executive_report as er
        report = er.build_report()
        self.assertEqual(report["tax_rows"], [])

    def test_tax_rows_populated_with_summary(self):
        import modules.executive_report as er
        state.tax_summary = {
            "ibs": {"tax_amount": 1000},
            "cnas_annual": 200,
            "cnac_annual": 50,
            "irg_annual": 300,
            "vf_annual": 100,
            "total_taxes": 1650,
            "tax_burden_pct": 8.25,
        }
        rows = er.build_report()["tax_rows"]
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0], ("er_tax_ibs", 1000.0))
        self.assertEqual(rows[5], ("er_tax_total", 1650.0))

    def test_full_report_renders_with_data(self):
        import modules.executive_report as er
        state.company_name = "شركة اختبار"
        state.financial_data = {
            "revenue": 200000, "cogs": 120000, "gross_profit": 80000,
            "operating_expenses": 40000, "net_income": 30000,
            "total_assets": 500000, "current_assets": 100000,
            "total_liabilities": 200000, "current_liabilities": 80000,
            "equity": 300000, "cash": 50000, "inventory": 20000,
            "avg_receivables": 40000, "avg_payables": 18000,
            "fiscal_year": 2026,
        }
        state.ratios = {
            "current_ratio": 1.25, "quick_ratio": 0.9, "gross_profit_margin": 40.0,
            "net_profit_margin": 15.0, "operating_margin": 20.0, "roe": 10.0,
            "return_on_assets": 6.0, "debt_to_equity": 2.5, "debt_ratio": 0.4,
            "interest_coverage": 5.0, "asset_turnover": 0.4,
            "inventory_turnover": 3.0, "receivables_turnover": 5.0, "z_score": 2.0,
        }
        state.tax_summary = {
            "ibs": {"tax_amount": 1000}, "cnas_annual": 200, "cnac_annual": 50,
            "irg_annual": 300, "vf_annual": 100, "total_taxes": 1650,
            "tax_burden_pct": 8.25,
        }
        report = er.build_report()
        text = er.render_text(report)
        html = er.render_html(report)
        self.assertIn("شركة اختبار", html)
        self.assertIn("1,650.00", text)
        self.assertIn("الملخص الجبائي", text)
        self.assertIn("التوصيات", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
