# اختبارات محرك الميزانية والتخطيط
# ================================

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.budgeting import (
    BudgetManager, BudgetError, budget_manager, BUDGET_CATEGORIES)


class TestBudgetItems(unittest.TestCase):

    def setUp(self):
        self.mgr = BudgetManager()
        self.r_id = self.mgr.set_budget_item(2026, "إيرادات المبيعات", 100000.0,
                                             category="revenue")
        self.e_id = self.mgr.set_budget_item(2026, "رواتب", 40000.0,
                                             category="expense")
        self.mgr.set_budget_item(2026, "معدات", 20000.0, category="investment")

    def test_set_item(self):
        item = self.mgr.get_budget_item(self.r_id)
        self.assertEqual(item["year"], 2026)
        self.assertEqual(item["category"], "revenue")
        self.assertEqual(item["amount"], 100000.0)

    def test_set_item_requires_name(self):
        with self.assertRaises(BudgetError):
            self.mgr.set_budget_item(2026, "  ", 1.0)

    def test_set_item_rejects_negative(self):
        with self.assertRaises(BudgetError):
            self.mgr.set_budget_item(2026, "x", -1.0)

    def test_set_item_rejects_bad_category(self):
        with self.assertRaises(BudgetError):
            self.mgr.set_budget_item(2026, "x", 1.0, category="other")

    def test_set_item_rejects_bad_year(self):
        with self.assertRaises(BudgetError):
            self.mgr.set_budget_item(1800, "x", 1.0)
        with self.assertRaises(BudgetError):
            self.mgr.set_budget_item(2300, "x", 1.0)
        with self.assertRaises(BudgetError):
            self.mgr.set_budget_item("bad", "x", 1.0)

    def test_set_item_rejects_invalid_amount_type(self):
        with self.assertRaises(BudgetError):
            self.mgr.set_budget_item(2026, "x", "abc")

    def test_set_item_updates_existing(self):
        same_id = self.mgr.set_budget_item(2026, "رواتب", 45000.0,
                                           category="expense")
        self.assertEqual(same_id, self.e_id)
        self.assertEqual(self.mgr.get_budget_item(self.e_id)["amount"], 45000.0)

    def test_update_budget_item(self):
        self.assertTrue(self.mgr.update_budget_item(self.e_id, amount=50000.0))
        self.assertEqual(self.mgr.get_budget_item(self.e_id)["amount"], 50000.0)

    def test_update_budget_item_missing(self):
        self.assertFalse(self.mgr.update_budget_item(999, amount=1.0))

    def test_update_budget_item_validation(self):
        with self.assertRaises(BudgetError):
            self.mgr.update_budget_item(self.e_id, amount=-1)
        with self.assertRaises(BudgetError):
            self.mgr.update_budget_item(self.e_id, item_name="  ")
        with self.assertRaises(BudgetError):
            self.mgr.update_budget_item(self.e_id, category="nope")
        with self.assertRaises(BudgetError):
            self.mgr.update_budget_item(self.e_id, year=1800)

    def test_update_budget_item_unknown_field_ignored(self):
        self.assertTrue(self.mgr.update_budget_item(self.e_id, bogus=1))
        self.assertEqual(self.mgr.get_budget_item(self.e_id)["amount"], 40000.0)

    def test_delete_budget_item(self):
        self.assertTrue(self.mgr.delete_budget_item(self.e_id))
        self.assertIsNone(self.mgr.get_budget_item(self.e_id))
        self.assertFalse(self.mgr.delete_budget_item(999))

    def test_get_budget_sorted(self):
        items = self.mgr.get_budget(2026)
        self.assertEqual(len(items), 3)
        cats = [i["category"] for i in items]
        self.assertEqual(cats, sorted(cats))

    def test_get_budget_other_year(self):
        self.assertEqual(self.mgr.get_budget(2027), [])

    def test_totals(self):
        totals = self.mgr.totals(2026)
        self.assertEqual(totals["count"], 3)
        self.assertEqual(totals["total"], 160000.0)

    def test_totals_by_category(self):
        totals = self.mgr.totals(2026, category="expense")
        self.assertEqual(totals["count"], 1)
        self.assertEqual(totals["total"], 40000.0)

    def test_totals_other_year(self):
        self.assertEqual(self.mgr.totals(2027)["count"], 0)


class TestBudgetComparison(unittest.TestCase):

    def setUp(self):
        self.mgr = BudgetManager()
        self.mgr.set_budget_item(2026, "رواتب", 40000.0, category="expense")
        self.mgr.set_budget_item(2026, "مبيعات", 100000.0, category="revenue")

    def test_compare_to_actuals(self):
        rows = self.mgr.compare_to_actuals(2026, {"رواتب": 45000.0})
        by_name = {r["item_name"]: r for r in rows}
        self.assertEqual(len(rows), 2)
        self.assertEqual(by_name["رواتب"]["variance"], 5000.0)
        self.assertEqual(by_name["رواتب"]["variance_pct"], 12.5)
        self.assertEqual(by_name["رواتب"]["execution_pct"], 112.5)
        self.assertEqual(by_name["مبيعات"]["variance"], -100000.0)

    def test_compare_with_extra_actual(self):
        rows = self.mgr.compare_to_actuals(2026, {"غير مخطط له": 100.0})
        extra = next(r for r in rows if r["item_name"] == "غير مخطط له")
        self.assertEqual(extra["planned"], 0.0)
        self.assertEqual(extra["variance_pct"], 0.0)

    def test_compare_planned_zero(self):
        self.mgr.set_budget_item(2026, "بدون خطة", 0.0)
        rows = self.mgr.compare_to_actuals(2026, {"بدون خطة": 10.0})
        row = next(r for r in rows if r["item_name"] == "بدون خطة")
        self.assertEqual(row["variance_pct"], 0.0)
        self.assertEqual(row["execution_pct"], 0.0)

    def test_variance_summary(self):
        summary = self.mgr.variance_summary(2026, {"رواتب": 44000.0,
                                                   "مبيعات": 110000.0})
        self.assertEqual(summary["item_count"], 2)
        self.assertEqual(summary["planned_total"], 140000.0)
        self.assertEqual(summary["actual_total"], 154000.0)
        self.assertEqual(summary["variance_total"], 14000.0)

    def test_variance_summary_zero_planned(self):
        summary = self.mgr.variance_summary(2026, {})
        self.assertEqual(summary["execution_pct"], 0.0)

    def test_over_budget_items(self):
        rows = self.mgr.over_budget_items(2026, {"رواتب": 50000.0,
                                                 "مبيعات": 50000.0})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["item_name"], "رواتب")

    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "budget.csv")
            self.assertTrue(self.mgr.export_csv(path, 2026))
            with open(path, encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("رواتب", content)
            self.assertIn("year", content)

    def test_export_csv_os_error(self):
        with mock.patch("builtins.open", side_effect=OSError("boom")):
            self.assertFalse(self.mgr.export_csv("x.csv", 2026))

    def test_clear(self):
        self.mgr.clear()
        self.assertEqual(self.mgr.get_budget(2026), [])
        self.assertEqual(self.mgr.totals(2026)["count"], 0)


class TestBudgetDB(unittest.TestCase):

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
        self.mgr = BudgetManager()

    def test_save_and_load_db(self):
        self.mgr.set_budget_item(2026, "مبيعات", 100000.0, category="revenue")
        self.mgr.set_budget_item(2026, "رواتب", 40000.0, category="expense")
        self.assertTrue(self.mgr.save_db())
        other = BudgetManager()
        self.assertTrue(other.load_db())
        self.assertEqual(len(other.get_budget(2026)), 2)
        self.assertEqual(other.totals(2026)["total"], 140000.0)
        new_id = other.set_budget_item(2026, "معدات", 5000.0)
        self.assertEqual(new_id, 3)

    def test_load_db_empty_table_returns_false(self):
        self.mgr.save_db()
        other = BudgetManager()
        self.assertFalse(other.load_db())

    def test_clear_db(self):
        self.mgr.set_budget_item(2026, "مؤقت", 1.0)
        self.mgr.save_db()
        self.assertTrue(self.mgr.clear_db())
        other = BudgetManager()
        self.assertFalse(other.load_db())

    def test_save_db_raises_error(self):
        with mock.patch("modules.budgeting.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.save_db())

    def test_load_db_raises_error(self):
        with mock.patch("modules.budgeting.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.load_db())

    def test_load_db_missing_table(self):
        conn = mock.MagicMock()
        conn.table_exists.return_value = False
        with mock.patch("modules.budgeting.get_connection") as get_conn:
            get_conn.return_value.__enter__.return_value = conn
            self.assertFalse(self.mgr.load_db())

    def test_clear_db_raises_error(self):
        with mock.patch("modules.budgeting.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.clear_db())


class TestBudgetSingleton(unittest.TestCase):

    def test_singleton_exists(self):
        self.assertIsInstance(budget_manager, BudgetManager)

    def test_constants(self):
        self.assertEqual(BUDGET_CATEGORIES, ("revenue", "expense", "investment"))


if __name__ == "__main__":
    unittest.main()
