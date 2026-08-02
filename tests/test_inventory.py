# اختبارات محرك إدارة المخزون
# ============================

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.inventory import (
    InventoryManager, InventoryError, inventory_manager, MOVEMENT_TYPES)


class TestInventoryItems(unittest.TestCase):

    def setUp(self):
        self.mgr = InventoryManager()
        self.item_id = self.mgr.add_item("قهوة", sku="SKU-1", category="مشروبات",
                                         quantity=10, cost_price=500.0,
                                         sale_price=800.0, min_quantity=3)

    def test_add_item(self):
        item = self.mgr.get_item(self.item_id)
        self.assertEqual(item["name"], "قهوة")
        self.assertEqual(item["sku"], "SKU-1")
        self.assertEqual(item["quantity"], 10.0)
        self.assertEqual(item["avg_cost"], 500.0)

    def test_add_item_requires_name(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_item("  ")

    def test_add_item_rejects_negative_prices(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_item("x", cost_price=-1)
        with self.assertRaises(InventoryError):
            self.mgr.add_item("x", sale_price=-1)

    def test_add_item_duplicate_sku(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_item("مكرر", sku="sku-1")

    def test_update_item(self):
        self.assertTrue(self.mgr.update_item(self.item_id, sale_price=900.0))
        self.assertEqual(self.mgr.get_item(self.item_id)["sale_price"], 900.0)

    def test_update_item_missing(self):
        self.assertFalse(self.mgr.update_item(999, name="x"))

    def test_update_item_requires_name(self):
        with self.assertRaises(InventoryError):
            self.mgr.update_item(self.item_id, name="  ")

    def test_update_item_rejects_negative_sale_price(self):
        with self.assertRaises(InventoryError):
            self.mgr.update_item(self.item_id, sale_price=-1)

    def test_update_item_duplicate_sku(self):
        other = self.mgr.add_item("آخر", sku="SKU-2")
        with self.assertRaises(InventoryError):
            self.mgr.update_item(other, sku="sku-1")

    def test_update_item_unknown_field_ignored(self):
        self.assertTrue(self.mgr.update_item(self.item_id, bogus=1))
        self.assertNotIn("bogus", self.mgr.get_item(self.item_id))

    def test_delete_item(self):
        self.assertTrue(self.mgr.delete_item(self.item_id))
        self.assertIsNone(self.mgr.get_item(self.item_id))
        self.assertFalse(self.mgr.delete_item(999))

    def test_get_item_missing(self):
        self.assertIsNone(self.mgr.get_item(999))

    def test_find_by_sku(self):
        self.assertEqual(self.mgr.find_by_sku("SKU-1")["id"], self.item_id)
        self.assertIsNone(self.mgr.find_by_sku("NOPE"))

    def test_list_items_sorted(self):
        self.mgr.add_item("تفاح", category="فواكه")
        names = [i["name"] for i in self.mgr.list_items()]
        self.assertEqual(names, sorted(names))

    def test_list_items_by_category(self):
        self.mgr.add_item("تفاح", category="فواكه")
        rows = self.mgr.list_items(category="مشروبات")
        self.assertEqual(len(rows), 1)

    def test_list_items_low_stock_filters(self):
        low = self.mgr.add_item("شاي", quantity=1, min_quantity=5)
        rows = self.mgr.list_items(low_stock_only=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], low)

    def test_categories(self):
        self.mgr.add_item("تفاح", category="فواكه")
        self.mgr.add_item("برتقال", category="فواكه")
        cats = self.mgr.categories()
        self.assertEqual(cats, ["فواكه", "مشروبات"])


class TestInventoryMovements(unittest.TestCase):

    def setUp(self):
        self.mgr = InventoryManager()
        self.item_id = self.mgr.add_item("سكر", quantity=0, cost_price=100.0,
                                         min_quantity=5)

    def test_stock_in_moves_average_cost(self):
        self.mgr.add_movement(self.item_id, "2026-08-01", "in", 10, unit_cost=100.0)
        self.mgr.add_movement(self.item_id, "2026-08-02", "in", 10, unit_cost=200.0)
        self.assertEqual(self.mgr.current_stock(self.item_id), 20.0)
        self.assertEqual(self.mgr.get_item(self.item_id)["avg_cost"], 150.0)

    def test_stock_out(self):
        self.mgr.add_movement(self.item_id, "2026-08-01", "in", 10)
        self.mgr.add_movement(self.item_id, "2026-08-02", "out", 4)
        self.assertEqual(self.mgr.current_stock(self.item_id), 6.0)

    def test_out_rejects_insufficient(self):
        self.mgr.add_movement(self.item_id, "2026-08-01", "in", 3)
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(self.item_id, "2026-08-02", "out", 5)

    def test_out_allow_negative(self):
        self.mgr.add_movement(self.item_id, "2026-08-01", "out", 5,
                              allow_negative=True)
        self.assertEqual(self.mgr.current_stock(self.item_id), -5.0)

    def test_adjustment_sets_quantity(self):
        self.mgr.add_movement(self.item_id, "2026-08-01", "in", 10)
        self.mgr.add_movement(self.item_id, "2026-08-02", "adjustment", 25,
                              unit_cost=90.0)
        self.assertEqual(self.mgr.current_stock(self.item_id), 25.0)
        self.assertEqual(self.mgr.get_item(self.item_id)["avg_cost"], 90.0)

    def test_unknown_item(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(999, "2026-08-01", "in", 1)

    def test_bad_movement_type(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(self.item_id, "2026-08-01", "transfer", 1)

    def test_rejects_negative_quantity(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(self.item_id, "2026-08-01", "in", -1)

    def test_rejects_invalid_date_type(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(self.item_id, 12345, "in", 1)

    def test_rejects_invalid_date_string(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(self.item_id, "bad-date", "in", 1)

    def test_rejects_invalid_quantity_type(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(self.item_id, "2026-08-01", "in", "abc")

    def test_rejects_negative_cost(self):
        with self.assertRaises(InventoryError):
            self.mgr.add_movement(self.item_id, "2026-08-01", "in", 1,
                                  unit_cost=-5)

    def test_movement_history_sorted(self):
        m1 = self.mgr.add_movement(self.item_id, "2026-08-02", "in", 1)
        m2 = self.mgr.add_movement(self.item_id, "2026-08-01", "in", 1)
        rows = self.mgr.movement_history(self.item_id)
        self.assertEqual([r["id"] for r in rows], [m2, m1])

    def test_movement_accepts_date_object(self):
        from datetime import date
        self.mgr.add_movement(self.item_id, date(2026, 8, 1), "in", 1)
        rows = self.mgr.movement_history(self.item_id)
        self.assertEqual(rows[0]["date"], "2026-08-01")

    def test_clear(self):
        self.mgr.add_movement(self.item_id, "2026-08-01", "in", 5)
        self.mgr.clear()
        self.assertEqual(self.mgr.list_items(), [])
        self.assertEqual(self.mgr.current_stock(self.item_id), 0.0)


class TestInventoryValuation(unittest.TestCase):

    def setUp(self):
        self.mgr = InventoryManager()
        self.item_id = self.mgr.add_item("زيت", category="أغذية", quantity=10,
                                         cost_price=300.0, min_quantity=4)

    def test_item_value(self):
        self.assertEqual(self.mgr.item_value(self.item_id), 3000.0)

    def test_item_value_unknown(self):
        self.assertEqual(self.mgr.item_value(999), 0.0)

    def test_stock_value(self):
        self.assertEqual(self.mgr.stock_value(), 3000.0)
        self.assertEqual(self.mgr.stock_value(category="أغذية"), 3000.0)
        self.assertEqual(self.mgr.stock_value(category="أخرى"), 0.0)

    def test_is_low_stock(self):
        self.assertFalse(self.mgr.is_low_stock(self.item_id))
        self.mgr.add_movement(self.item_id, "2026-08-01", "out", 7)
        self.assertTrue(self.mgr.is_low_stock(self.item_id))

    def test_is_low_stock_unknown(self):
        self.assertFalse(self.mgr.is_low_stock(999))

    def test_low_stock_items(self):
        self.mgr.add_movement(self.item_id, "2026-08-01", "out", 7)
        rows = self.mgr.low_stock_items()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["low_stock"])


class TestInventoryDB(unittest.TestCase):

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
        self.mgr = InventoryManager()

    def test_save_and_load_db(self):
        item_id = self.mgr.add_item("دقيق", sku="D1", quantity=20,
                                    cost_price=250.0, min_quantity=5)
        self.mgr.add_movement(item_id, "2026-08-01", "in", 10, unit_cost=300.0)
        self.assertTrue(self.mgr.save_db())
        other = InventoryManager()
        self.assertTrue(other.load_db())
        self.assertEqual(len(other.list_items()), 1)
        self.assertEqual(other.current_stock(item_id), 30.0)
        new_id = other.add_item("ملح", sku="S1")
        self.assertEqual(new_id, 2)

    def test_load_db_empty_table_returns_false(self):
        self.mgr.save_db()
        other = InventoryManager()
        self.assertFalse(other.load_db())

    def test_clear_db(self):
        self.mgr.add_item("مخزون مؤقت")
        self.mgr.save_db()
        self.assertTrue(self.mgr.clear_db())
        other = InventoryManager()
        self.assertFalse(other.load_db())

    def test_save_db_raises_error(self):
        with mock.patch("modules.inventory.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.save_db())

    def test_load_db_raises_error(self):
        with mock.patch("modules.inventory.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.load_db())

    def test_load_db_missing_table(self):
        conn = mock.MagicMock()
        conn.table_exists.return_value = False
        with mock.patch("modules.inventory.get_connection") as get_conn:
            get_conn.return_value.__enter__.return_value = conn
            self.assertFalse(self.mgr.load_db())

    def test_clear_db_raises_error(self):
        with mock.patch("modules.inventory.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.mgr.clear_db())


class TestInventorySingleton(unittest.TestCase):

    def test_singleton_exists(self):
        self.assertIsInstance(inventory_manager, InventoryManager)

    def test_constants(self):
        self.assertIn("adjustment", MOVEMENT_TYPES)


if __name__ == "__main__":
    unittest.main()
