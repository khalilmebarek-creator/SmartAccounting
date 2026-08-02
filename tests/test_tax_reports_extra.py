# Extra unit tests for modules/tax_reports.py (TaxDeclarationGenerator).
# Covers the untested branches: build_header, header period label, credit
# rendering for G50, refund rendering for G57, full DAS rendering, unknown
# declaration errors, and PDF/Excel export failure paths.

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.tax_reports import TaxDeclarationGenerator


def _company_info():
    return {
        "company_name": "شركة النور للتجارة",
        "nif": "099916000123456",
        "rc": "16/00-1234567B23",
        "ai": "16000991",
        "address": "الجزائر العاصمة",
        "dgi_center": "مديرية الضرائب — الجزائر",
    }


class TestDeclarationInfoAndHeader(unittest.TestCase):

    def setUp(self):
        self.gen = TaxDeclarationGenerator()

    def test_get_declaration_info_known(self):
        info = self.gen.get_declaration_info("g50")
        self.assertIn("name_en", info)
        self.assertIn("VAT", info["name_en"])

    def test_get_declaration_info_unknown_returns_empty(self):
        self.assertEqual(self.gen.get_declaration_info("xyz"), {})

    def test_build_header_fields(self):
        header = self.gen.build_header(_company_info(), 2025, "جانفي 2025")
        self.assertEqual(header["company_name"], "شركة النور للتجارة")
        self.assertEqual(header["nif"], "099916000123456")
        self.assertEqual(header["fiscal_year"], 2025)
        self.assertEqual(header["period"], "جانفي 2025")

    def test_build_header_empty_company(self):
        header = self.gen.build_header({}, 2026)
        self.assertEqual(header["company_name"], "")
        self.assertEqual(header["period"], "")


class TestRenderBranches(unittest.TestCase):

    def setUp(self):
        self.gen = TaxDeclarationGenerator()
        self.header = self.gen.build_header(_company_info(), 2025, "جانفي 2025")

    def test_render_g50_with_period_label(self):
        decl = self.gen.generate("g50", {
            "header": self.header,
            "month": 1,
            "year": 2025,
            "monthly_turnover": 1000000,
            "tva_collected": 190000,
            "tva_deductible": 100000,
        })
        text = self.gen.render_text(decl)
        self.assertIn("الفترة: جانفي 2025", text)
        self.assertIn("المبلغ الواجب دفعه", text)

    def test_render_g50_credit_branch(self):
        decl = self.gen.generate("g50", {
            "header": self.header,
            "month": 1,
            "year": 2025,
            "monthly_turnover": 1000000,
            "tva_collected": 100000,
            "tva_deductible": 190000,
            "previous_credit": 50000,
        })
        self.assertEqual(decl["net_tva"]["status"], "credit")
        text = self.gen.render_text(decl)
        self.assertIn("رصيد يُرحل/يُسترجع", text)
        self.assertIn("رصيد سابق: 50,000.00 DZD", text)

    def test_render_g57_refund_branch(self):
        decl = self.gen.generate("g57", {
            "header": self.header,
            "taxable_income": 10000000,
            "acomptes_paid": 2000000,
            "activity_type": "production",
        })
        self.assertGreater(decl["balance"]["refund_amount"], 0)
        text = self.gen.render_text(decl)
        self.assertIn("فائض يُسترجع", text)

    def test_render_das_full(self):
        decl = self.gen.generate("das", {
            "header": self.header,
            "monthly_payroll": 100000,
            "number_of_employees": 2,
            "avg_salary": 50000,
        })
        text = self.gen.render_text(decl)
        self.assertIn("عدد الموظفين: 2", text)
        self.assertIn("CNAS — حصة صاحب العمل", text)
        self.assertIn("IRG المقتطع من الأجور", text)
        self.assertIn("صافي الأجور المدفوعة", text)

    def test_render_text_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            self.gen.render_text({"type": "xyz", "header": {}})


class TestExportFailures(unittest.TestCase):

    def setUp(self):
        self.gen = TaxDeclarationGenerator()
        self.header = self.gen.build_header(_company_info(), 2025)
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_pdf_failure_returns_false(self):
        decl = self.gen.generate("g50", {
            "header": self.header,
            "month": 1,
            "year": 2025,
            "monthly_turnover": 1000,
            "tva_collected": 100,
            "tva_deductible": 100,
        })
        path = os.path.join(self.tmp.name, "g50.pdf")
        with mock.patch(
            "modules.reporting.ReportGenerator", side_effect=Exception("boom")
        ):
            result = self.gen.export_pdf(decl, path)
        self.assertFalse(result)

    def test_export_excel_failure_returns_false(self):
        decl = self.gen.generate("g50", {
            "header": self.header,
            "month": 1,
            "year": 2025,
            "monthly_turnover": 1000,
            "tva_collected": 100,
            "tva_deductible": 100,
        })
        path = os.path.join(self.tmp.name, "g50.xlsx")
        with mock.patch(
            "openpyxl.Workbook", side_effect=Exception("boom")
        ):
            result = self.gen.export_excel(decl, path)
        self.assertFalse(result)

    def test_export_excel_g50_credit_branch(self):
        decl = self.gen.generate("g50", {
            "header": self.header,
            "month": 1,
            "year": 2025,
            "monthly_turnover": 1000,
            "tva_collected": 100,
            "tva_deductible": 190,
        })
        self.assertEqual(decl["net_tva"]["status"], "credit")
        path = os.path.join(self.tmp.name, "g50_credit.xlsx")
        result = self.gen.export_excel(decl, path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))

    def test_export_excel_g57_branch_with_refund(self):
        decl = self.gen.generate("g57", {
            "header": self.header,
            "taxable_income": 10000000,
            "acomptes_paid": 2000000,
            "activity_type": "production",
        })
        path = os.path.join(self.tmp.name, "g57.xlsx")
        result = self.gen.export_excel(decl, path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))

    def test_export_excel_das_default_branch(self):
        decl = self.gen.generate("das", {
            "header": self.header,
            "monthly_payroll": 100000,
            "number_of_employees": 1,
        })
        path = os.path.join(self.tmp.name, "das.xlsx")
        result = self.gen.export_excel(decl, path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
