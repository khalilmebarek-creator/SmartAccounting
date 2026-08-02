# اختبارات الشركات التجريبية المتعددة (تجارية/خدمات/إنتاج/استيراد-تصدير)
# ========================================================================

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.demo_data import DemoData, DEMO_COMPANIES, _MONTHLY_WEIGHTS
from modules.demo_templates import (
    write_templates,
    export_company_csv,
    generate_demo_reports,
    FINANCIAL_COLUMNS,
    TRANSACTION_COLUMNS,
)
from modules.data_import import DataImporter


class FakeState:
    """بديل مبسّط لحالة التطبيق (ui.app_state.AppState)."""

    def __init__(self):
        self.company_name = ""
        self.company_name_fr = ""
        self.fiscal_year = 2024
        self.financial_data = {}
        self.tax_summary = None
        self.ratios = {}
        self.dupont = {}
        self.working_capital = {}
        self.saved = False

    def save_data(self):
        self.saved = True


class TestDemoCompanies(unittest.TestCase):
    """اختبارات الشركات التجريبية المتعددة"""

    EXPECTED_IDS = ["retail", "services", "manufacturing", "import_export"]

    def test_list_companies_returns_four(self):
        companies = DemoData.list_companies()
        self.assertEqual(len(companies), 4)
        self.assertEqual([c["id"] for c in companies], self.EXPECTED_IDS)

    def test_list_companies_fields(self):
        for c in DemoData.list_companies():
            self.assertIn("company_name", c)
            self.assertIn("industry", c)
            self.assertIn("fiscal_year", c)
            self.assertTrue(c["company_name"])
            self.assertTrue(c["industry"])
            self.assertEqual(c["fiscal_year"], 2024)

    def test_all_industries_have_weights(self):
        for cid in self.EXPECTED_IDS:
            self.assertIn(cid, _MONTHLY_WEIGHTS)
            self.assertEqual(len(_MONTHLY_WEIGHTS[cid]), 12)
            self.assertAlmostEqual(sum(_MONTHLY_WEIGHTS[cid]), 1.0, places=6)

    def test_get_company_returns_copy(self):
        c1 = DemoData.get_company("retail")
        c2 = DemoData.get_company("retail")
        self.assertEqual(c1, c2)
        c1["financial_data"]["revenue"] = 999
        self.assertNotEqual(c1["financial_data"]["revenue"],
                            c2["financial_data"]["revenue"])

    def test_get_company_missing_returns_none(self):
        self.assertIsNone(DemoData.get_company("does_not_exist"))

    def test_balance_sheet_equation(self):
        for cid in self.EXPECTED_IDS:
            fd = DemoData.get_company(cid)["financial_data"]
            self.assertEqual(
                fd["total_assets"],
                fd["current_assets"] + fd["non_current_assets"],
                msg=cid,
            )
            self.assertAlmostEqual(
                fd["total_assets"],
                fd["total_liabilities"] + fd["equity"],
                places=0,
                msg=cid,
            )

    def test_income_statement_consistency(self):
        for cid in self.EXPECTED_IDS:
            fd = DemoData.get_company(cid)["financial_data"]
            self.assertEqual(fd["gross_profit"],
                             fd["revenue"] - fd["cost_of_goods_sold"],
                             msg=cid)
            self.assertGreater(fd["revenue"], 0, msg=cid)
            self.assertGreater(fd["equity"], 0, msg=cid)

    def test_tax_summary_structure(self):
        for cid in self.EXPECTED_IDS:
            ts = DemoData.get_company(cid)["tax_summary"]
            self.assertIn("total_taxes", ts)
            self.assertIn("ibs", ts)
            self.assertIn("tax_burden_pct", ts)
            self.assertGreater(ts["total_taxes"], 0, msg=cid)

    def test_monthly_transactions_length(self):
        for cid in self.EXPECTED_IDS:
            rows = DemoData.get_monthly_transactions(cid)
            self.assertEqual(len(rows), 12, msg=cid)
            self.assertEqual([r["month"] for r in rows], list(range(1, 13)), msg=cid)

    def test_monthly_values_non_negative(self):
        for cid in self.EXPECTED_IDS:
            for r in DemoData.get_monthly_transactions(cid):
                for key in ("revenue", "cost_of_goods_sold", "operating_expenses",
                            "net_income", "cash", "accounts_receivable",
                            "inventory", "accounts_payable"):
                    self.assertGreaterEqual(r[key], 0, msg=f"{cid}:{r['month']}:{key}")

    def test_monthly_sums_match_annual(self):
        for cid in self.EXPECTED_IDS:
            fd = DemoData.get_company(cid)["financial_data"]
            rows = DemoData.get_monthly_transactions(cid)
            self.assertAlmostEqual(
                sum(r["revenue"] for r in rows), fd["revenue"], places=0, msg=cid)
            self.assertAlmostEqual(
                sum(r["cost_of_goods_sold"] for r in rows),
                fd["cost_of_goods_sold"], places=0, msg=cid)
            self.assertAlmostEqual(
                sum(r["operating_expenses"] for r in rows),
                fd["operating_expenses"], places=0, msg=cid)

    def test_monthly_missing_company(self):
        self.assertEqual(DemoData.get_monthly_transactions("nope"), [])

    def test_load_company_fills_state(self):
        state = FakeState()
        ok = DemoData.load_company(state, "manufacturing")
        self.assertTrue(ok)
        self.assertTrue(state.saved)
        self.assertEqual(state.company_name,
                         DEMO_COMPANIES["manufacturing"]["company_name"])
        self.assertGreater(state.financial_data["revenue"], 0)
        self.assertIn("roe", state.ratios)
        self.assertIn("current_ratio", state.ratios)
        self.assertTrue(state.tax_summary)

    def test_load_company_missing_returns_false(self):
        state = FakeState()
        self.assertFalse(DemoData.load_company(state, "missing"))
        self.assertFalse(state.saved)

    def test_generate_demo_reports(self):
        reports = generate_demo_reports("retail")
        self.assertEqual(sorted(reports.keys()),
                         ["balance_sheet", "income_statement", "ratios"])
        company = DEMO_COMPANIES["retail"]["company_name"]
        self.assertIn(company, reports["balance_sheet"])
        self.assertTrue(reports["income_statement"].strip())
        self.assertTrue(reports["ratios"].strip())

    def test_generate_demo_reports_missing(self):
        self.assertEqual(generate_demo_reports("nope"), {})

    def test_templates_and_export_csv_importable(self):
        with tempfile.TemporaryDirectory() as d:
            paths = write_templates(d)
            self.assertEqual(len(paths), 2)

            exporter = DataImporter()
            self.assertTrue(exporter.import_from_csv(paths[0]))
            self.assertTrue(exporter.validate_data())
            self.assertEqual(exporter.get_row_count(), 0)

            # استيراد القالب الثاني (المعاملات الشهرية)
            exporter2 = DataImporter()
            self.assertTrue(exporter2.import_from_csv(paths[1]))

    def test_export_company_csv(self):
        with tempfile.TemporaryDirectory() as d:
            paths = export_company_csv(d, "services")
            self.assertEqual(len(paths), 2)
            self.assertTrue(all(os.path.exists(p) for p in paths))

            importer = DataImporter()
            self.assertTrue(importer.import_from_csv(paths[0]))
            self.assertTrue(importer.validate_data())
            self.assertEqual(importer.get_row_count(), 1)

            importer2 = DataImporter()
            self.assertTrue(importer2.import_from_csv(paths[1]))
            self.assertEqual(importer2.get_row_count(), 12)

    def test_export_company_csv_missing(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(export_company_csv(d, "nope"), [])

    def test_columns_compatible_with_validator(self):
        for col in ("total_assets", "total_liabilities", "equity",
                    "revenue", "net_income"):
            self.assertIn(col, FINANCIAL_COLUMNS)


if __name__ == "__main__":
    unittest.main()
