# اختبارات محرك العملاء والموردين (AR/AP)
# =========================================

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.partners import (
    PartnerManager, PartnerError, partner_manager, PARTNER_TYPES, TX_TYPES)


class TestPartnerManagement(unittest.TestCase):

    def setUp(self):
        self.mgr = PartnerManager()
        self.cust_id = self.mgr.add_partner("customer", "شركة الأمل",
                                            phone="0550", email="a@b.c")
        self.supp_id = self.mgr.add_partner("supplier", "مورد الجزائر")

    def test_add_customer(self):
        partner = self.mgr.get_partner(self.cust_id)
        self.assertEqual(partner["type"], "customer")
        self.assertEqual(partner["name"], "شركة الأمل")
        self.assertEqual(partner["phone"], "0550")

    def test_add_partner_rejects_bad_type(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_partner("vendor", "X")

    def test_add_partner_requires_name(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_partner("customer", "  ")

    def test_update_partner(self):
        self.assertTrue(self.mgr.update_partner(self.cust_id, phone="0551"))
        self.assertEqual(self.mgr.get_partner(self.cust_id)["phone"], "0551")

    def test_update_partner_missing(self):
        self.assertFalse(self.mgr.update_partner(999, phone="x"))

    def test_update_partner_invalid_type(self):
        with self.assertRaises(PartnerError):
            self.mgr.update_partner(self.cust_id, type="other")

    def test_update_partner_type(self):
        self.assertTrue(self.mgr.update_partner(self.cust_id, type="supplier"))
        self.assertEqual(self.mgr.get_partner(self.cust_id)["type"], "supplier")

    def test_update_partner_empty_name_raises(self):
        with self.assertRaises(PartnerError):
            self.mgr.update_partner(self.cust_id, name="  ")

    def test_delete_partner(self):
        self.assertTrue(self.mgr.delete_partner(self.cust_id))
        self.assertIsNone(self.mgr.get_partner(self.cust_id))

    def test_delete_partner_missing(self):
        self.assertFalse(self.mgr.delete_partner(999))

    def test_list_partners_sorted(self):
        names = [p["name"] for p in self.mgr.list_partners()]
        self.assertEqual(names, sorted(names))

    def test_list_partners_filtered(self):
        result = self.mgr.list_partners(partner_type="supplier")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], self.supp_id)

    def test_search_partners(self):
        result = self.mgr.search_partners("الأمل")
        self.assertEqual(len(result), 1)
        result = self.mgr.search_partners("0550")
        self.assertEqual(len(result), 1)
        result = self.mgr.search_partners("zzz")
        self.assertEqual(result, [])

    def test_search_partners_filtered_by_type(self):
        result = self.mgr.search_partners("", partner_type="supplier")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], self.supp_id)
        result = self.mgr.search_partners("", partner_type="customer")
        self.assertEqual(len(result), 1)

    def test_get_partner_missing(self):
        self.assertIsNone(self.mgr.get_partner(999))


class TestPartnerTransactions(unittest.TestCase):

    def setUp(self):
        self.mgr = PartnerManager()
        self.cust_id = self.mgr.add_partner("customer", "عميل واحد")
        self.supp_id = self.mgr.add_partner("supplier", "مورد واحد")

    def test_add_invoice_increases_customer_balance(self):
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 1000.0)
        self.assertEqual(self.mgr.get_balance(self.cust_id), 1000.0)

    def test_payment_decreases_balance(self):
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 1000.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-02", "payment", 300.0)
        self.assertEqual(self.mgr.get_balance(self.cust_id), 700.0)

    def test_supplier_balance_sign_flip(self):
        self.mgr.add_transaction(self.supp_id, "2026-08-01", "invoice", 500.0)
        self.assertEqual(self.mgr.get_balance(self.supp_id), 500.0)
        self.mgr.add_transaction(self.supp_id, "2026-08-02", "payment", 200.0)
        self.assertEqual(self.mgr.get_balance(self.supp_id), 300.0)

    def test_credit_and_debit_notes(self):
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-02", "credit_note", 40.0)
        self.assertEqual(self.mgr.get_balance(self.cust_id), 60.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-03", "debit_note", 10.0)
        self.assertEqual(self.mgr.get_balance(self.cust_id), 70.0)

    def test_balance_details(self):
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 1000.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-02", "payment", 400.0)
        details = self.mgr.get_balance_details(self.cust_id)
        self.assertEqual(details["invoiced"], 1000.0)
        self.assertEqual(details["paid"], 400.0)
        self.assertEqual(details["net"], 600.0)

    def test_add_transaction_unknown_partner(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_transaction(999, "2026-08-01", "invoice", 10.0)

    def test_add_transaction_rejects_bad_type(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_transaction(self.cust_id, "2026-08-01", "transfer", 10.0)

    def test_add_transaction_rejects_nonpositive(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 0.0)
        with self.assertRaises(PartnerError):
            self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", -5.0)

    def test_add_transaction_rejects_invalid_date(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_transaction(self.cust_id, "bad-date", "invoice", 10.0)

    def test_add_transaction_rejects_invalid_date_type(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_transaction(self.cust_id, 12345, "invoice", 10.0)

    def test_add_transaction_rejects_invalid_amount_type(self):
        with self.assertRaises(PartnerError):
            self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", "abc")

    def test_list_transactions_sorted(self):
        t1 = self.mgr.add_transaction(self.cust_id, "2026-08-02", "payment", 10.0)
        t2 = self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        rows = self.mgr.list_transactions(partner_id=self.cust_id)
        self.assertEqual([r["id"] for r in rows], [t2, t1])

    def test_list_transactions_filtered_by_type(self):
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-02", "payment", 10.0)
        rows = self.mgr.list_transactions(tx_type="payment")
        self.assertEqual(len(rows), 1)

    def test_get_transaction(self):
        tx_id = self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        self.assertEqual(self.mgr.get_transaction(tx_id)["amount"], 100.0)
        self.assertIsNone(self.mgr.get_transaction(999))

    def test_list_transactions_partner_filter_skips_others(self):
        other = self.mgr.add_partner("customer", "عميل آخر")
        self.mgr.add_transaction(other, "2026-08-01", "invoice", 999.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        rows = self.mgr.list_transactions(partner_id=self.cust_id)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], 100.0)

    def test_get_balance_ignores_other_partner(self):
        other = self.mgr.add_partner("customer", "عميل آخر")
        self.mgr.add_transaction(other, "2026-08-01", "invoice", 999.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        self.assertEqual(self.mgr.get_balance(self.cust_id), 100.0)

    def test_balance_details_ignores_other_partner(self):
        other = self.mgr.add_partner("customer", "عميل آخر")
        self.mgr.add_transaction(other, "2026-08-01", "invoice", 999.0)
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        details = self.mgr.get_balance_details(self.cust_id)
        self.assertEqual(details["invoiced"], 100.0)

    def test_get_balance_unknown_partner(self):
        self.assertEqual(self.mgr.get_balance(999), 0.0)

    def test_rounds_amount(self):
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 10.005)
        self.assertEqual(self.mgr.get_balance(self.cust_id), 10.01)


class TestAging(unittest.TestCase):

    def setUp(self):
        self.mgr = PartnerManager()
        self.cust_id = self.mgr.add_partner("customer", "العميل الأول")

    def test_aging_buckets(self):
        self.mgr.add_transaction(self.cust_id, "2026-07-01", "invoice", 100.0)
        self.mgr.add_transaction(self.cust_id, "2026-07-15", "invoice", 200.0)
        self.mgr.add_transaction(self.cust_id, "2026-07-25", "invoice", 300.0)
        rows = self.mgr.aging(partner_id=self.cust_id, as_of="2026-08-01")
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["days_1_30"], 500.0)
        self.assertEqual(row["days_31_60"], 100.0)
        self.assertEqual(row["total"], 600.0)

    def test_aging_partially_paid(self):
        self.mgr.add_transaction(self.cust_id, "2026-07-01", "invoice", 100.0)
        self.mgr.add_transaction(self.cust_id, "2026-07-02", "payment", 40.0)
        rows = self.mgr.aging(partner_id=self.cust_id, as_of="2026-08-01")
        self.assertEqual(rows[0]["days_31_60"], 60.0)
        self.assertEqual(rows[0]["total"], 60.0)

    def test_aging_all_partners(self):
        other = self.mgr.add_partner("supplier", "مورد اثنان")
        self.mgr.add_transaction(self.cust_id, "2026-07-01", "invoice", 100.0)
        self.mgr.add_transaction(other, "2026-07-01", "invoice", 50.0)
        self.assertEqual(len(self.mgr.aging(as_of="2026-08-01")), 2)

    def test_aging_current_bucket(self):
        self.mgr.add_transaction(self.cust_id, "2026-08-01", "invoice", 100.0)
        rows = self.mgr.aging(partner_id=self.cust_id, as_of="2026-08-01")
        self.assertEqual(rows[0]["current"], 100.0)

    def test_aging_old_buckets(self):
        self.mgr.add_transaction(self.cust_id, "2026-05-20", "invoice", 100.0)
        self.mgr.add_transaction(self.cust_id, "2026-04-01", "invoice", 200.0)
        rows = self.mgr.aging(partner_id=self.cust_id, as_of="2026-08-01")
        self.assertEqual(rows[0]["days_61_90"], 100.0)
        self.assertEqual(rows[0]["days_90_plus"], 200.0)

    def test_aging_unknown_partner(self):
        self.assertEqual(self.mgr.aging(partner_id=999), [])

    def test_clear(self):
        self.mgr.add_transaction(self.cust_id, "2026-07-01", "invoice", 100.0)
        self.mgr.clear()
        self.assertEqual(self.mgr.list_partners(), [])
        self.assertEqual(self.mgr.get_balance(self.cust_id), 0.0)


class TestPartnersDB(unittest.TestCase):

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
        self.mgr = PartnerManager()

    def test_save_and_load_db(self):
        cust = self.mgr.add_partner("customer", "الشركة الخضراء", phone="0100")
        self.mgr.add_transaction(cust, "2026-08-01", "invoice", 1500.0)
        self.mgr.add_transaction(cust, "2026-08-02", "payment", 500.0)
        self.assertTrue(self.mgr.save_db())
        other = PartnerManager()
        self.assertTrue(other.load_db())
        self.assertEqual(len(other.list_partners()), 1)
        self.assertEqual(other.get_balance(cust), 1000.0)
        new_id = other.add_partner("supplier", "مورد جديد")
        self.assertEqual(new_id, 2)

    def test_load_db_empty_table_returns_false(self):
        self.mgr.save_db()
        other = PartnerManager()
        self.assertFalse(other.load_db())

    def test_clear_db(self):
        self.mgr.add_partner("customer", "شركة زوال")
        self.mgr.save_db()
        self.assertTrue(self.mgr.clear_db())
        other = PartnerManager()
        self.assertFalse(other.load_db())

    def test_save_db_raises_error(self):
        with mock.patch("modules.partners.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.save_db())

    def test_load_db_raises_error(self):
        with mock.patch("modules.partners.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.load_db())

    def test_load_db_missing_table(self):
        conn = mock.MagicMock()
        conn.table_exists.return_value = False
        with mock.patch("modules.partners.get_connection") as get_conn:
            get_conn.return_value.__enter__.return_value = conn
            self.assertFalse(self.mgr.load_db())

    def test_clear_db_raises_error(self):
        with mock.patch("modules.partners.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.clear_db())


class TestPartnersSingleton(unittest.TestCase):

    def test_singleton_exists(self):
        self.assertIsInstance(partner_manager, PartnerManager)

    def test_constants(self):
        self.assertEqual(PARTNER_TYPES, ("customer", "supplier"))
        self.assertIn("credit_note", TX_TYPES)


if __name__ == "__main__":
    unittest.main()
