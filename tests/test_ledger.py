# Ø§Ø®ØªØ¨Ø§Ø±Ø§Øª Ø¯ÙØªØ± Ø§Ù„Ø£Ø³ØªØ§Ø° Ø§Ù„Ø¹Ø§Ù…
# ===========================

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.ledger import LedgerBook, LedgerError, ledger_book


class TestLedgerEntries(unittest.TestCase):

    def setUp(self):
        self.book = LedgerBook()

    def test_add_debit_entry(self):
        entry_id = self.book.add_entry("2026-08-01", "5300", debit=1000.0,
                                       description="Ù†Ù‚Ø¯ÙŠØ©", reference="RV-1")
        self.assertEqual(entry_id, 1)
        entry = self.book.get_entry(1)
        self.assertEqual(entry["account_code"], "5300")
        self.assertEqual(entry["debit"], 1000.0)
        self.assertEqual(entry["credit"], 0.0)

    def test_add_credit_entry(self):
        entry_id = self.book.add_entry("2026-08-01", "4010", credit=500.0)
        self.assertEqual(self.book.get_entry(entry_id)["credit"], 500.0)

    def test_account_name_defaults_to_code(self):
        eid = self.book.add_entry("2026-08-01", "6000", debit=10.0)
        self.assertEqual(self.book.get_entry(eid)["account_name"], "6000")

    def test_accepts_date_object(self):
        from datetime import date
        eid = self.book.add_entry(date(2026, 8, 1), "5300", debit=1.0)
        self.assertEqual(self.book.get_entry(eid)["date"], "2026-08-01")

    def test_rejects_invalid_date(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry("2026-13-45", "5300", debit=1.0)

    def test_rejects_invalid_date_type(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry(12345, "5300", debit=1.0)

    def test_requires_account_code(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry("2026-08-01", "  ", debit=1.0)

    def test_requires_account_code_none(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry("2026-08-01", None, debit=1.0)

    def test_rejects_negative_amounts(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry("2026-08-01", "5300", debit=-5.0)

    def test_rejects_both_debit_and_credit(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry("2026-08-01", "5300", debit=5.0, credit=5.0)

    def test_rejects_zero_zero(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry("2026-08-01", "5300")

    def test_rejects_non_numeric_amount(self):
        with self.assertRaises(LedgerError):
            self.book.add_entry("2026-08-01", "5300", debit="abc")

    def test_delete_entry(self):
        eid = self.book.add_entry("2026-08-01", "5300", debit=1.0)
        self.assertTrue(self.book.delete_entry(eid))
        self.assertIsNone(self.book.get_entry(eid))

    def test_delete_missing_entry(self):
        self.assertFalse(self.book.delete_entry(999))

    def test_get_entry_missing(self):
        self.assertIsNone(self.book.get_entry(999))

    def test_rounds_amounts(self):
        eid = self.book.add_entry("2026-08-01", "5300", debit=1.006)
        self.assertEqual(self.book.get_entry(eid)["debit"], 1.01)


class TestLedgerQueries(unittest.TestCase):

    def setUp(self):
        self.book = LedgerBook()
        self.book.add_entry("2026-08-01", "5300", debit=1000.0, reference="1")
        self.book.add_entry("2026-08-02", "4010", credit=500.0, reference="2")
        self.book.add_entry("2026-08-03", "5300", debit=250.0, reference="3")

    def test_get_entries_all_sorted(self):
        entries = self.book.get_entries()
        self.assertEqual(len(entries), 3)
        self.assertEqual([e["date"] for e in entries],
                         ["2026-08-01", "2026-08-02", "2026-08-03"])

    def test_get_entries_by_account(self):
        entries = self.book.get_entries(account_code="5300")
        self.assertEqual(len(entries), 2)

    def test_get_entries_date_range(self):
        entries = self.book.get_entries(date_from="2026-08-02")
        self.assertEqual(len(entries), 2)
        entries = self.book.get_entries(date_to="2026-08-02")
        self.assertEqual(len(entries), 2)

    def test_get_entries_returns_copies(self):
        entries = self.book.get_entries()
        entries[0]["debit"] = 999.0
        self.assertEqual(self.book.get_entry(1)["debit"], 1000.0)

    def test_account_balance(self):
        self.assertEqual(self.book.account_balance("5300"), 1250.0)
        self.assertEqual(self.book.account_balance("4010"), -500.0)
        self.assertEqual(self.book.account_balance("9999"), 0.0)

    def test_account_ledger_running_balance(self):
        rows = self.book.account_ledger("5300")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["running_balance"], 1000.0)
        self.assertEqual(rows[1]["running_balance"], 1250.0)

    def test_trial_balance(self):
        tb = self.book.trial_balance()
        self.assertEqual(tb["total_debit"], 1250.0)
        self.assertEqual(tb["total_credit"], 500.0)
        self.assertFalse(tb["balanced"])
        self.assertEqual(tb["entry_count"], 3)

    def test_trial_balance_balanced(self):
        self.book.add_entry("2026-08-04", "5120", credit=750.0)
        tb = self.book.trial_balance()
        self.assertTrue(tb["balanced"])

    def test_accounts_summary(self):
        summary = self.book.accounts_summary()
        self.assertEqual(len(summary), 2)
        acc = next(a for a in summary if a["account_code"] == "5300")
        self.assertEqual(acc["balance"], 1250.0)
        acc = next(a for a in summary if a["account_code"] == "4010")
        self.assertEqual(acc["balance"], -500.0)

    def test_clear(self):
        self.book.clear()
        self.assertEqual(self.book.get_entries(), [])
        self.assertEqual(self.book.trial_balance()["entry_count"], 0)

    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ledger.csv")
            self.assertTrue(self.book.export_csv(path))
            with open(path, encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("5300", content)
            self.assertIn("date", content)

    def test_export_csv_os_error(self):
        with mock.patch("builtins.open", side_effect=OSError("boom")):
            self.assertFalse(self.book.export_csv("x.csv"))


class TestLedgerDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp.close()
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp.name
        from database.db_connection import close_pool
        close_pool()

    @classmethod
    def tearDownClass(cls):
        config.DATABASE_PATH = cls.original_path
        from database.db_connection import close_pool
        close_pool()
        os.unlink(cls.tmp.name)

    def setUp(self):
        self.book = LedgerBook()

    def test_save_and_load_db(self):
        self.book.add_entry("2026-08-01", "5300", debit=1000.0,
                            description="Ù†Ù‚Ø¯ÙŠØ©", reference="R1")
        self.book.add_entry("2026-08-02", "4010", credit=1000.0)
        self.assertTrue(self.book.save_db())
        other = LedgerBook()
        self.assertTrue(other.load_db())
        self.assertEqual(len(other.get_entries()), 2)
        self.assertEqual(other.account_balance("5300"), 1000.0)
        self.assertEqual(other.get_entry(1)["description"], "Ù†Ù‚Ø¯ÙŠØ©")
        # Ø§Ù„Ù…Ø¹Ø±Ù‘ÙØ§Øª ØªØªØ§Ø¨Ø¹ Ø¨Ø¹Ø¯ Ø§Ù„ØªØ­Ù…ÙŠÙ„
        eid = other.add_entry("2026-08-03", "5120", credit=100.0)
        self.assertEqual(eid, 3)

    def test_load_db_empty_table_returns_false(self):
        self.book.save_db()
        other = LedgerBook()
        self.assertFalse(other.load_db())

    def test_clear_db(self):
        self.book.add_entry("2026-08-01", "5300", debit=1.0)
        self.book.save_db()
        self.assertTrue(self.book.clear_db())
        other = LedgerBook()
        self.assertFalse(other.load_db())

    def test_save_db_raises_error(self):
        with mock.patch("modules.ledger.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.book.save_db())

    def test_load_db_raises_error(self):
        with mock.patch("modules.ledger.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.book.load_db())

    def test_load_db_missing_table(self):
        conn = mock.MagicMock()
        conn.table_exists.return_value = False
        with mock.patch("modules.ledger.get_connection") as get_conn:
            get_conn.return_value.__enter__.return_value = conn
            self.assertFalse(self.book.load_db())

    def test_clear_db_raises_error(self):
        with mock.patch("modules.ledger.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.book.clear_db())


class TestLedgerSingleton(unittest.TestCase):

    def test_singleton_exists(self):
        self.assertIsInstance(ledger_book, LedgerBook)


if __name__ == "__main__":
    unittest.main()

