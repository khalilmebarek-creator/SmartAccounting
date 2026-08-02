# Unit tests for modules/bank_sync.py (BankSyncManager) and
# modules/print_manager.py (PrintManager).

import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modules.bank_sync as bank_sync
import modules.print_manager as print_manager
from modules.bank_sync import BankSyncManager
from modules.print_manager import PrintManager


def _write(path, content, encoding="utf-8"):
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(content)


class FakeWebEngine(object):
    """Context manager that provides a fake QtWebEngine module in sys.modules."""

    def __init__(self, page_class=None):
        self.page_class = page_class if page_class is not None else mock.MagicMock()
        self._module = types.ModuleType("PyQt5.QtWebEngineWidgets")
        self._module.QWebEnginePage = self.page_class
        self._patch = mock.patch.dict(
            sys.modules, {"PyQt5.QtWebEngineWidgets": self._module}
        )

    def __enter__(self):
        self._patch.start()
        return self.page_class

    def __exit__(self, *exc):
        self._patch.stop()
        return False


# ==================== bank_sync.py ====================

class TestBankSyncDetection(unittest.TestCase):

    def setUp(self):
        self.manager = BankSyncManager()

    def test_detect_bank_returns_all_supported_banks(self):
        self.assertEqual(len(self.manager.get_bank_list()), 6)
        codes = {b["code"] for b in self.manager.get_bank_list()}
        self.assertTrue({"BNA", "CPA", "BADR", "BEA", "BDL", "CCP"} <= codes)

    def test_detect_bank_missing_file_returns_none(self):
        self.assertIsNone(self.manager.detect_bank("Z:/no/such/bank.csv"))

    def test_detect_bank_read_error_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bank.csv")
            _write(path, "BNA")
            with mock.patch("builtins.open", side_effect=OSError("boom")):
                self.assertIsNone(self.manager.detect_bank(path))

    def test_detect_bank_by_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bank.csv")
            _write(path, "Relevé BNA - Compte courant")
            self.assertEqual(self.manager.detect_bank(path), "BNA")

    def test_detect_bank_by_name_en(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bank.csv")
            _write(path, "Banque Nationale d'Algerie statement")
            self.assertEqual(self.manager.detect_bank(path), "BNA")

    def test_detect_bank_nationale_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bank.csv")
            _write(path, "NATIONALE")
            self.assertEqual(self.manager.detect_bank(path), "BNA")

    def test_detect_bank_populaire_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bank.csv")
            _write(path, "POPULAIRE")
            self.assertEqual(self.manager.detect_bank(path), "CPA")

    def test_detect_bank_unknown_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bank.csv")
            _write(path, "just some random text")
            self.assertIsNone(self.manager.detect_bank(path))


class TestBankSyncImport(unittest.TestCase):

    def setUp(self):
        self.manager = BankSyncManager()

    def _bna_file(self):
        tmp = tempfile.TemporaryDirectory()
        path = os.path.join(tmp.name, "bna.csv")
        _write(path, (
            "libelle;N;Date;Debit;Credit;Solde\n"
            "01/01/2026;1;First row is consumed as header;1000;0;50000\n"
            "02/01/2026;2;Paiement fournisseur;1000,50;0;50000,00\n"
            "03/01/2026;3;Vente client;0;2500,00;52500,00\n"
            "\n"
            "04/01/2026;4;;100;0;52600\n"
            "05/01/2026;5;Interet bancaire;0;100;52700\n"
        ), encoding="latin-1")
        return tmp, path

    def test_import_with_bank_format_success(self):
        tmp, path = self._bna_file()
        try:
            result = self.manager.import_bank_statement(path, "BNA", account_id="ACC1")
            self.assertEqual(result["bank"], "BNA")
            self.assertEqual(
                result["bank_name"], bank_sync.ALGERIAN_BANKS["BNA"]["name_en"]
            )
            self.assertEqual(result["account_id"], "ACC1")
            self.assertEqual(result["count"], 4)
            self.assertEqual(result["total_debit"], 2000.5)
            self.assertEqual(result["total_credit"], 2600.0)
            self.assertEqual(result["errors"], [])
            first = result["transactions"][0]
            self.assertEqual(first["date"], "2026-01-01")
            self.assertEqual(first["description"], "First row is consumed as header")
            self.assertEqual(first["debit"], 1000.0)
            self.assertEqual(first["balance"], 50000.0)
            self.assertEqual(first["amount"], -1000.0)
            self.assertEqual(first["bank"], "BNA")
            self.assertEqual(first["account_id"], "ACC1")
            self.assertEqual(result["transactions"][1]["amount"], -1000.5)
            self.assertEqual(result["transactions"][2]["amount"], 2500.0)
            self.assertEqual(result["transactions"][3]["amount"], 100.0)
            self.assertIsNotNone(self.manager.last_import)
        finally:
            tmp.cleanup()

    def test_import_with_bank_code_uses_detection_when_missing(self):
        tmp, path = self._bna_file()
        try:
            with mock.patch.object(self.manager, "detect_bank", return_value="BNA") as db:
                result = self.manager.import_bank_statement(path, account_id="A")
            db.assert_called_once_with(path)
            self.assertEqual(result["bank"], "BNA")
        finally:
            tmp.cleanup()

    def test_import_unknown_bank_falls_back_generic(self):
        tmp, path = self._bna_file()
        try:
            result = self.manager.import_bank_statement(path, "XYZ")
            self.assertEqual(result["bank"], "Generic")
            self.assertEqual(result["count"], 0)
        finally:
            tmp.cleanup()

    def test_import_detect_none_falls_back_generic(self):
        tmp, path = self._bna_file()
        try:
            with mock.patch.object(self.manager, "detect_bank", return_value=None):
                result = self.manager.import_bank_statement(path)
            self.assertEqual(result["bank"], "Generic")
        finally:
            tmp.cleanup()

    def test_import_with_bank_format_no_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "empty.csv")
            _write(path, "Date;Description\n")
            result = self.manager.import_bank_statement(path, "BNA")
            self.assertEqual(result["transactions"], [])
            self.assertEqual(result["errors"], ["No data found"])

    def test_import_with_bank_format_leading_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bna.csv")
            _write(path, (
                "\n"
                "libelle;N;Date;Debit;Credit;Solde\n"
                "01/01/2026;1;Paiement fournisseur;100;0;5000\n"
            ), encoding="latin-1")
            result = self.manager.import_bank_statement(path, "BNA")
            self.assertEqual(result["count"], 1)
            self.assertEqual(
                result["transactions"][0]["description"], "Paiement fournisseur"
            )

    def test_import_with_bank_format_missing_file(self):
        result = self.manager.import_bank_statement("Z:/no/such/bna.csv", "BNA")
        self.assertEqual(result["transactions"], [])
        self.assertTrue(result["errors"])

    def test_import_with_bank_format_row_parsing_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bna.csv")
            _write(path, (
                "libelle;N;Date;Debit;Credit;Solde\n"
                "01/01/2026;1;H1;100;0;5000\n"
                "02/01/2026;2;H2;0;200;5200\n"
            ), encoding="latin-1")
            with mock.patch.object(
                self.manager, "_parse_transaction", side_effect=ValueError("bad row")
            ):
                result = self.manager.import_bank_statement(path, "BNA")
            self.assertEqual(result["count"], 0)
            self.assertEqual(len(result["errors"]), 2)
            self.assertIn("Row parsing error", result["errors"][0])

    def test_parse_transaction_success_with_alternate_date(self):
        col_map = {"date": 0, "description": 1, "debit": 2, "credit": 3, "balance": 4}
        tx = self.manager._parse_transaction(
            ["01/02/2026", "Paiement", "10", "20", "30"], col_map, "%Y-%m-%d"
        )
        self.assertEqual(tx["date"], "2026-02-01")
        self.assertEqual(tx["debit"], 10)
        self.assertEqual(tx["credit"], 20)
        self.assertEqual(tx["balance"], 30)
        self.assertEqual(tx["amount"], 10)

    def test_parse_transaction_empty_description_returns_none(self):
        col_map = {"date": 0, "description": 1, "debit": 2, "credit": 3, "balance": 4}
        tx = self.manager._parse_transaction(["01/02/2026", "", "10"], col_map, "%d/%m/%Y")
        self.assertIsNone(tx)

    def test_parse_transaction_short_row(self):
        col_map = {"date": 0, "description": 1, "debit": 2, "credit": 3, "balance": 4}
        tx = self.manager._parse_transaction(["01/02/2026", "desc"], col_map, "%d/%m/%Y")
        self.assertEqual(tx["debit"], 0)
        self.assertEqual(tx["credit"], 0)
        self.assertEqual(tx["balance"], 0)
        self.assertEqual(tx["amount"], 0)


class TestBankSyncParsers(unittest.TestCase):

    def setUp(self):
        self.manager = BankSyncManager()

    def test_parse_date_primary_format(self):
        self.assertEqual(self.manager._parse_date("05/03/2026", "%d/%m/%Y"), "2026-03-05")

    def test_parse_date_dash_format(self):
        self.assertEqual(self.manager._parse_date("05-03-2026", "%d/%m/%Y"), "2026-03-05")

    def test_parse_date_iso_format(self):
        self.assertEqual(self.manager._parse_date("2026-03-05", "%d/%m/%Y"), "2026-03-05")

    def test_parse_date_month_name_format(self):
        self.assertEqual(self.manager._parse_date("05 Mar 2026", "%d/%m/%Y"), "2026-03-05")

    def test_parse_date_invalid_returns_raw(self):
        self.assertEqual(self.manager._parse_date("not-a-date", "%d/%m/%Y"), "not-a-date")

    def test_parse_amount_empty(self):
        self.assertEqual(self.manager._parse_amount(""), 0.0)

    def test_parse_amount_plain(self):
        self.assertEqual(self.manager._parse_amount("1234.56"), 1234.56)

    def test_parse_amount_comma_decimal(self):
        self.assertEqual(self.manager._parse_amount("1000,50"), 1000.5)

    def test_parse_amount_comma_thousands(self):
        self.assertEqual(self.manager._parse_amount("1,000,000"), 1000000.0)

    def test_parse_amount_both_comma_then_dot(self):
        self.assertEqual(self.manager._parse_amount("1,234.56"), 1234.56)

    def test_parse_amount_both_dot_then_comma(self):
        self.assertEqual(self.manager._parse_amount("1.234,56"), 1234.56)

    def test_parse_amount_negative_absolute(self):
        self.assertEqual(self.manager._parse_amount("-500"), 500.0)

    def test_parse_amount_invalid_returns_zero(self):
        self.assertEqual(self.manager._parse_amount("abc"), 0.0)

    def test_parse_amount_with_spaces(self):
        self.assertEqual(self.manager._parse_amount("1 000,50"), 1000.5)


class TestBankSyncGeneric(unittest.TestCase):

    def setUp(self):
        self.manager = BankSyncManager()

    def test_import_generic_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "generic.csv")
            _write(path, (
                "date,description,debit,credit,balance\n"
                "05/01/2026,Paiement fournisseur,500,0,1000\n"
                "06/01/2026,Vente,0,300,1300\n"
            ))
            result = self.manager._import_generic(path, "A1")
            self.assertEqual(result["bank"], "Generic")
            self.assertEqual(result["account_id"], "A1")
            self.assertEqual(result["count"], 2)
            self.assertEqual(result["total_debit"], 500)
            self.assertEqual(result["total_credit"], 300)
            self.assertEqual(result["errors"], [])
            self.assertEqual(result["transactions"][0]["amount"], -500)
            self.assertEqual(result["transactions"][1]["amount"], 300)
            self.assertEqual(result["transactions"][0]["date"], "2026-01-05")

    def test_import_generic_partial_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "generic.csv")
            _write(path, "date,description\n01/01/2026,Only desc\n")
            result = self.manager._import_generic(path, "")
            self.assertEqual(result["count"], 1)
            self.assertEqual(result["transactions"][0]["debit"], 0)
            self.assertEqual(result["transactions"][0]["credit"], 0)

    def test_import_generic_unmatched_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "generic.csv")
            _write(path, "a,b\n1,2\n")
            result = self.manager._import_generic(path, "")
            self.assertEqual(result["count"], 0)

    def test_import_generic_missing_file(self):
        result = self.manager._import_generic("Z:/no/such/generic.csv", "")
        self.assertEqual(result["transactions"], [])
        self.assertTrue(result["errors"])

    def test_import_generic_row_exception_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "generic.csv")
            _write(path, "date,description\n01/01/2026,desc\n")
            with mock.patch.object(
                self.manager, "_parse_date", side_effect=ValueError("bad date")
            ):
                result = self.manager._import_generic(path, "")
            self.assertEqual(result["count"], 0)

    def test_find_column_found(self):
        self.assertEqual(
            self.manager._find_column(["date", "description"], ["description"]), 1
        )

    def test_find_column_case_insensitive(self):
        self.assertEqual(
            self.manager._find_column(["DATE", "DESCRIPTION"], ["date"]), 0
        )

    def test_find_column_not_found(self):
        self.assertIsNone(self.manager._find_column(["a", "b"], ["date"]))


class TestBankSyncReconcile(unittest.TestCase):

    def setUp(self):
        self.manager = BankSyncManager()

    def test_reconcile_full_match(self):
        bank = [{"date": "2026-01-01", "amount": 100.0}]
        book = [{"date": "2026-01-01", "amount": 100.01}]
        result = self.manager.reconcile(bank, book, tolerance=0.02)
        self.assertEqual(result["matched_count"], 1)
        self.assertEqual(result["unmatched_bank_count"], 0)
        self.assertEqual(result["unmatched_book_count"], 0)
        self.assertEqual(result["match_rate"], 100.0)

    def test_reconcile_no_match(self):
        bank = [{"date": "2026-01-01", "amount": 100.0}]
        book = [{"date": "2026-01-02", "amount": 200.0}]
        result = self.manager.reconcile(bank, book)
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["unmatched_bank_count"], 1)
        self.assertEqual(result["unmatched_book_count"], 1)
        self.assertEqual(result["match_rate"], 0.0)

    def test_reconcile_empty_inputs(self):
        result = self.manager.reconcile([], [])
        self.assertEqual(result["matched_count"], 0)
        self.assertEqual(result["match_rate"], 0.0)


# ==================== print_manager.py ====================

class TestPrintHtml(unittest.TestCase):

    def setUp(self):
        self.manager = PrintManager()

    def tearDown(self):
        self.manager.cleanup()

    def test_print_html_no_application_returns_false(self):
        with FakeWebEngine(), mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=None
        ):
            self.assertFalse(self.manager.print_html("<p>hi</p>"))

    def test_print_html_dialog_cancelled_returns_false(self):
        with FakeWebEngine(), mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=object()
        ), mock.patch("PyQt5.QtPrintSupport.QPrinter"), mock.patch(
            "PyQt5.QtPrintSupport.QPrintDialog"
        ) as dlg, mock.patch("PyQt5.QtCore.QEventLoop"):
            dlg.return_value.exec_.return_value = 0
            self.assertFalse(self.manager.print_html("<p>hi</p>"))

    def test_print_html_success(self):
        page_class = mock.MagicMock()
        with FakeWebEngine(page_class), mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=object()
        ), mock.patch("PyQt5.QtPrintSupport.QPrinter"), mock.patch(
            "PyQt5.QtPrintSupport.QPrintDialog"
        ) as dlg, mock.patch("PyQt5.QtCore.QEventLoop") as loop_cls:
            dlg.return_value.exec_.return_value = dlg.Accepted
            result = self.manager.print_html("<p>hello</p>", landscape=False)
            self.assertTrue(result)
            page = page_class.return_value
            page.print.assert_called_once()
            callback = page.print.call_args[0][1]
            callback(True)
            callback(False)
            loop_cls.return_value.exec_.assert_called_once()

    def test_print_html_landscape_sets_orientation(self):
        with FakeWebEngine(), mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=object()
        ), mock.patch("PyQt5.QtPrintSupport.QPrinter") as printer_cls, mock.patch(
            "PyQt5.QtPrintSupport.QPrintDialog"
        ) as dlg, mock.patch("PyQt5.QtCore.QEventLoop"):
            dlg.return_value.exec_.return_value = dlg.Accepted
            result = self.manager.print_html("<p>hi</p>", landscape=True)
            self.assertTrue(result)
            printer_cls.return_value.setPageOrientation.assert_called_once()

    def test_print_html_falls_back_to_temp_file_on_import_error(self):
        with mock.patch.object(
            PrintManager, "_print_via_temp_file", return_value=True
        ) as fb, mock.patch.dict(
            sys.modules, {"PyQt5.QtWebEngineWidgets": None}
        ):
            result = self.manager.print_html("<p>hi</p>")
            self.assertTrue(result)
            fb.assert_called_once_with("<p>hi</p>", "Smart Accounting Platform")

    def test_print_html_generic_exception_returns_false(self):
        with FakeWebEngine(), mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=object()
        ), mock.patch(
            "PyQt5.QtPrintSupport.QPrinter",
            side_effect=RuntimeError("printer boom"),
        ):
            result = self.manager.print_html("<p>hi</p>")
            self.assertFalse(result)


class TestPrintViaTempFile(unittest.TestCase):

    def setUp(self):
        self.manager = PrintManager()

    def tearDown(self):
        self.manager.cleanup()

    def test_print_via_temp_file_no_application_returns_false(self):
        with mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=None
        ):
            self.assertFalse(self.manager._print_via_temp_file("<p>hi</p>", "T"))

    def test_print_via_temp_file_dialog_cancelled_returns_false(self):
        with mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=object()
        ), mock.patch("PyQt5.QtPrintSupport.QPrinter"), mock.patch(
            "PyQt5.QtPrintSupport.QPrintDialog"
        ) as dlg:
            dlg.return_value.exec_.return_value = 0
            self.assertFalse(self.manager._print_via_temp_file("<p>hi</p>", "T"))

    def test_print_via_temp_file_success(self):
        with mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=object()
        ), mock.patch("PyQt5.QtPrintSupport.QPrinter"), mock.patch(
            "PyQt5.QtPrintSupport.QPrintDialog"
        ) as dlg, mock.patch("PyQt5.QtGui.QTextDocument") as doc_cls:
            dlg.return_value.exec_.return_value = dlg.Accepted
            result = self.manager._print_via_temp_file("<p>hi</p>", "T")
            self.assertTrue(result)
            doc_cls.return_value.print_.assert_called_once()

    def test_print_via_temp_file_exception_returns_false(self):
        with mock.patch(
            "PyQt5.QtWidgets.QApplication.instance", return_value=object()
        ), mock.patch("PyQt5.QtPrintSupport.QPrinter"), mock.patch(
            "PyQt5.QtPrintSupport.QPrintDialog"
        ) as dlg, mock.patch(
            "PyQt5.QtGui.QTextDocument", side_effect=RuntimeError("boom")
        ):
            dlg.return_value.exec_.return_value = dlg.Accepted
            self.assertFalse(self.manager._print_via_temp_file("<p>hi</p>", "T"))


class TestGenerateReportHtml(unittest.TestCase):

    def setUp(self):
        self.manager = PrintManager()

    def tearDown(self):
        self.manager.cleanup()

    def test_generate_report_html_with_sections(self):
        sections = [
            {
                "title": "Income",
                "headers": ["Item", "Amount"],
                "rows": [
                    ("Revenue", 1000),
                    ("Cost", -250.5),
                    ("Note", "plain text"),
                ],
                "content": "some paragraph",
            },
        ]
        html = self.manager.generate_report_html(
            "Monthly", sections, company_name="ACME", fiscal_year="2026"
        )
        self.assertIn("Monthly", html)
        self.assertIn("ACME", html)
        self.assertIn("2026", html)
        self.assertIn('class="positive"', html)
        self.assertIn('class="negative"', html)
        self.assertIn("1,000.00", html)
        self.assertIn("-250.50", html)
        self.assertIn("some paragraph", html)

    def test_generate_report_html_rows_without_headers(self):
        sections = [{"title": "OnlyRows", "rows": [("A", 1), ("B", 2)]}]
        html = self.manager.generate_report_html("R", sections)
        self.assertIn("OnlyRows", html)
        self.assertIn("1.00", html)

    def test_generate_report_html_empty_rows_section(self):
        sections = [{"title": "EmptySection"}]
        html = self.manager.generate_report_html("R", sections)
        self.assertIn("EmptySection", html)

    def test_generate_report_html_no_sections(self):
        html = self.manager.generate_report_html("R", [])
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Smart Accounting Platform", html)


class TestPrintFinancialReport(unittest.TestCase):

    def setUp(self):
        self.manager = PrintManager()

    def tearDown(self):
        self.manager.cleanup()

    def _full_data(self):
        return {
            "income": {
                "revenue": 1000, "cogs": 400, "gross_profit": 600,
                "operating_expenses": 200, "net_income": 400,
            },
            "balance": {
                "current_assets": 100, "fixed_assets": 200, "total_assets": 300,
                "current_liabilities": 50, "long_term_liabilities": 100,
                "equity": 150,
            },
            "ratios": {
                "current_ratio": 2.0, "quick_ratio": 1.5, "debt_to_equity": 0.66,
                "net_profit_margin": 40, "roa": 5, "roe": 8,
            },
        }

    def test_print_financial_report_full(self):
        with mock.patch.object(PrintManager, "print_html", return_value=True) as ph:
            result = self.manager.print_financial_report("ACME", "2026", self._full_data())
        self.assertTrue(result)
        html = ph.call_args[0][0]
        self.assertIn("قائمة الدخل", html)
        self.assertIn("الميزانية العمومية", html)
        self.assertIn("النسب المالية", html)
        self.assertIn("2.00", html)
        self.assertIn("Financial Report - ACME", ph.call_args[0][1])

    def test_print_financial_report_empty_data(self):
        with mock.patch.object(PrintManager, "print_html", return_value=True) as ph:
            result = self.manager.print_financial_report("ACME", "2026", {})
        self.assertTrue(result)
        self.assertIn("التقرير المالي", ph.call_args[0][0])

    def test_print_financial_report_partial_ratios(self):
        with mock.patch.object(PrintManager, "print_html", return_value=True) as ph:
            result = self.manager.print_financial_report(
                "ACME", "2026", {"ratios": {"current_ratio": 2.0}}
            )
        self.assertTrue(result)
        html = ph.call_args[0][0]
        self.assertIn("النسب المالية", html)
        self.assertNotIn("هامش صافي الربح", html)

    def test_print_financial_report_empty_ratios_no_section(self):
        with mock.patch.object(PrintManager, "print_html", return_value=True) as ph:
            result = self.manager.print_financial_report(
                "ACME", "2026", {"ratios": {}}
            )
        self.assertTrue(result)
        self.assertNotIn("النسب المالية", ph.call_args[0][0])


class TestSaveAndCleanup(unittest.TestCase):

    def setUp(self):
        self.manager = PrintManager()

    def tearDown(self):
        self.manager.cleanup()

    def test_save_and_print_html_success(self):
        path = self.manager.save_and_print_html("<html>hi</html>", "Test Report")
        self.assertTrue(path)
        self.assertTrue(os.path.exists(path))
        self.assertIn("Test_Report", path)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "<html>hi</html>")

    def test_save_and_print_html_exception_returns_none(self):
        with mock.patch("builtins.open", side_effect=OSError("boom")):
            path = self.manager.save_and_print_html("<html></html>", "x")
        self.assertIsNone(path)

    def test_cleanup_removes_temp_dir(self):
        path = self.manager.temp_dir
        self.assertTrue(os.path.isdir(path))
        self.manager.cleanup()
        self.assertFalse(os.path.exists(path))

    def test_cleanup_handles_rmtree_error(self):
        with mock.patch("shutil.rmtree", side_effect=OSError("boom")):
            self.manager.cleanup()
        self.assertTrue(os.path.isdir(self.manager.temp_dir))


if __name__ == "__main__":
    unittest.main()
