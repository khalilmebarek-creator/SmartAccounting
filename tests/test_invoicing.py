# اختبارات محرك الفواتير
# =======================

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.invoicing import (
    InvoiceManager, InvoiceError, invoice_manager,
    INVOICE_TYPES, INVOICE_STATUSES, DEFAULT_TVA_RATE)


class TestInvoiceCreation(unittest.TestCase):

    def setUp(self):
        self.mgr = InvoiceManager()

    def _sale(self, **kw):
        items = kw.pop("items", [{"description": "خدمة", "quantity": 1,
                                  "unit_price": 1000.0}])
        return self.mgr.create_invoice("sale", 1, "2026-08-01", items, **kw)

    def test_create_sale_invoice(self):
        inv = self._sale()
        self.assertEqual(inv["type"], "sale")
        self.assertEqual(inv["status"], "draft")
        self.assertEqual(inv["number"], "SA-2026-0001")
        self.assertEqual(len(inv["items"]), 1)

    def test_create_purchase_invoice_number(self):
        inv = self.mgr.create_invoice(
            "purchase", 2, "2026-08-01",
            [{"description": "بضاعة", "quantity": 5, "unit_price": 200.0}])
        self.assertEqual(inv["number"], "BT-2026-0001")

    def test_totals_with_tva(self):
        inv = self._sale(items=[{"description": "سلعة", "quantity": 2,
                                 "unit_price": 100.0}])
        self.assertEqual(inv["subtotal"], 200.0)
        self.assertEqual(inv["tva_amount"], 38.0)
        self.assertEqual(inv["total"], 238.0)

    def test_custom_tva_rate(self):
        inv = self._sale(tva_rate=0.09)
        self.assertEqual(inv["tva_amount"], 90.0)

    def test_due_date(self):
        inv = self._sale(due_date="2026-09-01")
        self.assertEqual(inv["due_date"], "2026-09-01")

    def test_rejects_bad_type(self):
        with self.assertRaises(InvoiceError):
            self.mgr.create_invoice("other", 1, "2026-08-01",
                                    [{"description": "x", "unit_price": 1}])

    def test_rejects_no_items(self):
        with self.assertRaises(InvoiceError):
            self.mgr.create_invoice("sale", 1, "2026-08-01", [])

    def test_rejects_bad_tva(self):
        with self.assertRaises(InvoiceError):
            self._sale(tva_rate=1.5)
        with self.assertRaises(InvoiceError):
            self._sale(tva_rate=-0.1)

    def test_rejects_invalid_date(self):
        with self.assertRaises(InvoiceError):
            self.mgr.create_invoice("sale", 1, "bad-date",
                                    [{"description": "x", "unit_price": 1}])

    def test_rejects_invalid_date_type(self):
        with self.assertRaises(InvoiceError):
            self.mgr.create_invoice("sale", 1, 12345,
                                    [{"description": "x", "unit_price": 1}])

    def test_accepts_date_object(self):
        from datetime import date
        inv = self.mgr.create_invoice(
            "sale", 1, date(2026, 8, 1),
            [{"description": "x", "unit_price": 1}])
        self.assertEqual(inv["date"], "2026-08-01")

    def test_rejects_invalid_quantity_type(self):
        with self.assertRaises(InvoiceError):
            self.mgr.create_invoice(
                "sale", 1, "2026-08-01",
                [{"description": "x", "quantity": "abc", "unit_price": 1}])

    def test_add_item(self):
        inv = self._sale()
        item_id = self.mgr.add_item(inv["id"], "خدمة إضافية", 3, 50.0)
        inv = self.mgr.get_invoice(inv["id"])
        self.assertEqual(len(inv["items"]), 2)
        self.assertGreater(item_id, 0)

    def test_add_item_missing_invoice(self):
        with self.assertRaises(InvoiceError):
            self.mgr.add_item(999, "x", 1, 1.0)

    def test_add_item_requires_description(self):
        inv = self._sale()
        with self.assertRaises(InvoiceError):
            self.mgr.add_item(inv["id"], "  ", 1, 1.0)

    def test_add_item_rejects_negative(self):
        inv = self._sale()
        with self.assertRaises(InvoiceError):
            self.mgr.add_item(inv["id"], "x", -1, 1.0)

    def test_remove_item(self):
        inv = self._sale()
        item_id = inv["items"][0]["id"]
        self.assertTrue(self.mgr.remove_item(inv["id"], item_id))
        self.assertEqual(len(self.mgr.get_invoice(inv["id"])["items"]), 0)

    def test_remove_item_missing(self):
        inv = self._sale()
        self.assertFalse(self.mgr.remove_item(inv["id"], 999))
        self.assertFalse(self.mgr.remove_item(999, 1))


class TestInvoiceQueries(unittest.TestCase):

    def setUp(self):
        self.mgr = InvoiceManager()
        self.mgr.create_invoice("sale", 1, "2026-08-01",
                                [{"description": "أ", "unit_price": 100}])
        self.mgr.create_invoice("sale", 1, "2026-08-02",
                                [{"description": "ب", "unit_price": 200}])
        self.mgr.create_invoice("purchase", 2, "2026-08-03",
                                [{"description": "ج", "unit_price": 300}])

    def test_list_all(self):
        self.assertEqual(len(self.mgr.list_invoices()), 3)

    def test_list_filtered(self):
        self.assertEqual(len(self.mgr.list_invoices(invoice_type="sale")), 2)
        self.assertEqual(len(self.mgr.list_invoices(status="draft")), 3)

    def test_list_filtered_by_status_skips_others(self):
        self.mgr.update_status(1, "confirmed")
        rows = self.mgr.list_invoices(status="paid")
        self.assertEqual(rows, [])
        rows = self.mgr.list_invoices(status="confirmed")
        self.assertEqual(len(rows), 1)

    def test_sorted_desc_by_date(self):
        dates = [i["date"] for i in self.mgr.list_invoices()]
        self.assertEqual(dates, ["2026-08-03", "2026-08-02", "2026-08-01"])

    def test_update_status(self):
        inv = self.mgr.list_invoices()[0]
        self.assertTrue(self.mgr.update_status(inv["id"], "confirmed"))
        self.assertEqual(self.mgr.get_invoice(inv["id"])["status"], "confirmed")

    def test_update_status_missing(self):
        self.assertFalse(self.mgr.update_status(999, "paid"))

    def test_update_status_invalid(self):
        inv = self.mgr.list_invoices()[0]
        with self.assertRaises(InvoiceError):
            self.mgr.update_status(inv["id"], "shipped")

    def test_find_invoice_by_number(self):
        inv = self.mgr.find_invoice(number="SA-2026-0001")
        self.assertIsNotNone(inv)
        self.assertEqual(inv["number"], "SA-2026-0001")

    def test_find_invoice_by_id(self):
        inv = self.mgr.find_invoice(invoice_id=2)
        self.assertEqual(inv["id"], 2)

    def test_find_invoice_missing(self):
        self.assertIsNone(self.mgr.find_invoice(number="XX"))
        self.assertIsNone(self.mgr.get_invoice(999))

    def test_delete_invoice(self):
        self.assertTrue(self.mgr.delete_invoice(1))
        self.assertIsNone(self.mgr.get_invoice(1))
        self.assertFalse(self.mgr.delete_invoice(999))

    def test_totals(self):
        totals = self.mgr.totals()
        self.assertEqual(totals["count"], 3)
        self.assertEqual(totals["total"], round(600 * 1.19, 2))

    def test_totals_filtered(self):
        totals = self.mgr.totals(invoice_type="sale")
        self.assertEqual(totals["count"], 2)

    def test_by_partner(self):
        result = self.mgr.by_partner(1)
        self.assertEqual(len(result["invoices"]), 2)
        self.assertEqual(result["total"], round(300 * 1.19, 2))

    def test_next_invoice_number_respects_year(self):
        n = self.mgr.next_invoice_number("sale", 2025)
        self.assertEqual(n, "SA-2025-0001")
        self.mgr.create_invoice("sale", 1, "2025-06-01",
                                [{"description": "ق", "unit_price": 1}])
        n = self.mgr.next_invoice_number("sale", 2025)
        self.assertEqual(n, "SA-2025-0002")

    def test_next_invoice_number_bad_type(self):
        with self.assertRaises(InvoiceError):
            self.mgr.next_invoice_number("bad")

    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "inv.csv")
            self.assertTrue(self.mgr.export_csv(path))
            with open(path, encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("SA-2026-0001", content)

    def test_export_csv_os_error(self):
        with mock.patch("builtins.open", side_effect=OSError("boom")):
            self.assertFalse(self.mgr.export_csv("x.csv"))

    def test_clear(self):
        self.mgr.clear()
        self.assertEqual(self.mgr.list_invoices(), [])


class TestInvoicingDB(unittest.TestCase):

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
        self.mgr = InvoiceManager()

    def test_save_and_load_db(self):
        self.mgr.create_invoice(
            "sale", 1, "2026-08-01",
            [{"description": "خدمة", "quantity": 2, "unit_price": 100.0}])
        self.assertTrue(self.mgr.save_db())
        other = InvoiceManager()
        self.assertTrue(other.load_db())
        inv = other.list_invoices()[0]
        self.assertEqual(inv["number"], "SA-2026-0001")
        self.assertEqual(inv["subtotal"], 200.0)
        self.assertEqual(len(inv["items"]), 1)

    def test_load_db_empty_table_returns_false(self):
        self.mgr.save_db()
        other = InvoiceManager()
        self.assertFalse(other.load_db())

    def test_clear_db(self):
        self.mgr.create_invoice("sale", 1, "2026-08-01",
                                [{"description": "x", "unit_price": 1}])
        self.mgr.save_db()
        self.assertTrue(self.mgr.clear_db())
        other = InvoiceManager()
        self.assertFalse(other.load_db())

    def test_save_db_raises_error(self):
        with mock.patch("modules.invoicing.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.save_db())

    def test_load_db_raises_error(self):
        with mock.patch("modules.invoicing.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.load_db())

    def test_load_db_missing_table(self):
        conn = mock.MagicMock()
        conn.table_exists.return_value = False
        with mock.patch("modules.invoicing.get_connection") as get_conn:
            get_conn.return_value.__enter__.return_value = conn
            self.assertFalse(self.mgr.load_db())

    def test_clear_db_raises_error(self):
        with mock.patch("modules.invoicing.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.clear_db())


class TestInvoicingSingleton(unittest.TestCase):

    def test_singleton_exists(self):
        self.assertIsInstance(invoice_manager, InvoiceManager)

    def test_constants(self):
        self.assertEqual(INVOICE_TYPES, ("sale", "purchase"))
        self.assertIn("confirmed", INVOICE_STATUSES)
        self.assertEqual(DEFAULT_TVA_RATE, 0.19)


if __name__ == "__main__":
    unittest.main()
