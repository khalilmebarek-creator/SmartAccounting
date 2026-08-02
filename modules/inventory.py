# محرك إدارة المخزون
# ===================
# أصناف + حركات (دخول/خروج/تسوية) + تكلفة متوسط متحرك + نقاط إعادة الطلب

from datetime import date
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("inventory")

ITEM_TABLE = "inventory_items"
MOVEMENT_TABLE = "inventory_movements"

MOVEMENT_TYPES = ("in", "out", "adjustment")


class InventoryError(Exception):
    """خطأ في بيانات المخزون"""
    pass


class InventoryManager:
    """إدارة المخزون: الأصناف والحركات وتقييم التكلفة (متوسط متحرك)."""

    def __init__(self):
        self._items = {}
        self._movements = {}
        self._next_item_id = 1
        self._next_movement_id = 1

    # ===== الأصناف =====

    def add_item(self, name, sku="", category="", unit="", quantity=0.0,
                 cost_price=0.0, sale_price=0.0, min_quantity=0.0):
        """إضافة صنف. Returns: item_id."""
        name = (name or "").strip()
        if not name:
            raise InventoryError("item name is required")
        quantity = self._parse_amount(quantity, "quantity")
        cost_price = self._parse_amount(cost_price, "cost_price")
        sale_price = self._parse_amount(sale_price, "sale_price")
        min_quantity = self._parse_amount(min_quantity, "min_quantity")
        for field, value in (("cost_price", cost_price),
                             ("sale_price", sale_price)):
            if value < 0:
                raise InventoryError(f"{field} must be non-negative")
        sku = (sku or "").strip()
        if sku and self.find_by_sku(sku):
            raise InventoryError(f"SKU already exists: {sku}")
        item = {
            "id": self._next_item_id,
            "sku": sku,
            "name": name,
            "category": category or "",
            "unit": unit or "",
            "quantity": quantity,
            "avg_cost": cost_price,
            "sale_price": sale_price,
            "min_quantity": min_quantity,
        }
        self._next_item_id += 1
        self._items[item["id"]] = item
        self._movements[item["id"]] = []
        log.debug("Added inventory item %s: %s", item["id"], name)
        return item["id"]

    def update_item(self, item_id, **fields):
        """تحديث حقول صنف. Returns: bool."""
        item = self._items.get(item_id)
        if not item:
            return False
        allowed = ("sku", "name", "category", "unit", "sale_price",
                   "min_quantity", "quantity")
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "name":
                value = (value or "").strip()
                if not value:
                    raise InventoryError("item name is required")
            elif key == "sku":
                value = (value or "").strip()
                if value and self.find_by_sku(value) is not None and \
                        self.find_by_sku(value)["id"] != item_id:
                    raise InventoryError(f"SKU already exists: {value}")
            elif key in ("sale_price", "min_quantity", "quantity"):
                value = self._parse_amount(value, key)
                if key == "sale_price" and value < 0:
                    raise InventoryError("sale_price must be non-negative")
            item[key] = value
        return True

    def delete_item(self, item_id):
        """حذف صنف مع حركاته. Returns: bool."""
        if item_id not in self._items:
            return False
        del self._items[item_id]
        self._movements.pop(item_id, None)
        return True

    def get_item(self, item_id):
        item = self._items.get(item_id)
        return dict(item) if item else None

    def list_items(self, category=None, low_stock_only=False):
        """قائمة الأصناف (اختيارياً حسب الفئة/نقص المخزون)."""
        result = []
        for item in self._items.values():
            if category and item["category"] != category:
                continue
            if low_stock_only and not self.is_low_stock(item["id"]):
                continue
            row = dict(item)
            row["stock_value"] = self.item_value(item["id"])
            row["low_stock"] = self.is_low_stock(item["id"])
            result.append(row)
        result.sort(key=lambda x: x["name"].lower())
        return result

    def find_by_sku(self, sku):
        sku = (sku or "").strip()
        for item in self._items.values():
            if item["sku"] and item["sku"].lower() == sku.lower():
                return dict(item)
        return None

    def categories(self):
        """قائمة الفئات الفريدة."""
        cats = sorted({i["category"] for i in self._items.values() if i["category"]})
        return cats

    # ===== الحركات =====

    def add_movement(self, item_id, movement_date, movement_type, quantity,
                     unit_cost=None, reference="", notes="", allow_negative=False):
        """تسجيل حركة مخزون. Returns: movement_id.

        - in: إضافة كمية + تحديث متوسط التكلفة إن وُجدت كلفة.
        - out: إنقاص كمية (يرفض النقصان تحت الصفر ما لم allow_negative).
        - adjustment: ضبط الكمية مباشرة على القيمة المعطاة.
        """
        if item_id not in self._items:
            raise InventoryError("item not found")
        movement_type = (movement_type or "").strip().lower()
        if movement_type not in MOVEMENT_TYPES:
            raise InventoryError("movement_type must be one of in/out/adjustment")
        quantity = self._parse_amount(quantity, "quantity")
        if quantity < 0:
            raise InventoryError("quantity must be non-negative")
        movement_date = self._parse_date(movement_date).isoformat()
        item = self._items[item_id]
        unit_cost = self._parse_amount(unit_cost, "unit_cost") \
            if unit_cost is not None else None
        if unit_cost is not None and unit_cost < 0:
            raise InventoryError("unit_cost must be non-negative")

        if movement_type == "in":
            new_qty = item["quantity"] + quantity
            if quantity > 0 and unit_cost is not None:
                item["avg_cost"] = round(
                    (item["quantity"] * item["avg_cost"] + quantity * unit_cost)
                    / new_qty, 2) if new_qty else 0.0
            item["quantity"] = new_qty
        elif movement_type == "out":
            if quantity > item["quantity"] and not allow_negative:
                raise InventoryError("insufficient stock")
            item["quantity"] = item["quantity"] - quantity
        else:  # adjustment
            item["quantity"] = quantity
            if unit_cost is not None:
                item["avg_cost"] = unit_cost

        movement = {
            "id": self._next_movement_id,
            "item_id": item_id,
            "date": movement_date,
            "type": movement_type,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "reference": reference or "",
            "notes": notes or "",
        }
        self._next_movement_id += 1
        self._movements[item_id].append(movement)
        log.debug("Movement %s (%s) for item %s", movement["id"],
                  movement_type, item_id)
        return movement["id"]

    def movement_history(self, item_id):
        """سجل حركات صنف مرتباً تاريخياً."""
        movements = self._movements.get(item_id, [])
        result = [dict(m) for m in movements]
        result.sort(key=lambda x: (x["date"], x["id"]))
        return result

    # ===== القيم والنقص =====

    def current_stock(self, item_id):
        item = self._items.get(item_id)
        return item["quantity"] if item else 0.0

    def item_value(self, item_id):
        """قيمة المخزون لصنف = كمية × متوسط التكلفة."""
        item = self._items.get(item_id)
        if not item:
            return 0.0
        return round(item["quantity"] * item["avg_cost"], 2)

    def stock_value(self, category=None):
        """إجمالي قيمة المخزون (اختيارياً لفئة)."""
        total = 0.0
        for item in self._items.values():
            if category and item["category"] != category:
                continue
            total += self.item_value(item["id"])
        return round(total, 2)

    def is_low_stock(self, item_id):
        item = self._items.get(item_id)
        if not item:
            return False
        return item["quantity"] <= item["min_quantity"]

    def low_stock_items(self):
        """الأصناف عند أو تحت حد إعادة الطلب."""
        return self.list_items(low_stock_only=True)

    def clear(self):
        self._items = {}
        self._movements = {}
        self._next_item_id = 1
        self._next_movement_id = 1

    # ===== قاعدة البيانات =====

    def _ensure_tables(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {ITEM_TABLE} (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku VARCHAR(100) UNIQUE,
                item_name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                unit VARCHAR(50),
                quantity DECIMAL(15,3) DEFAULT 0,
                avg_cost DECIMAL(15,2) DEFAULT 0,
                sale_price DECIMAL(15,2) DEFAULT 0,
                min_quantity DECIMAL(15,3) DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {MOVEMENT_TABLE} (
                movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                movement_date DATE NOT NULL,
                movement_type VARCHAR(20) NOT NULL,
                quantity DECIMAL(15,3) DEFAULT 0,
                unit_cost DECIMAL(15,2) DEFAULT 0,
                reference VARCHAR(100),
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES inventory_items(item_id)
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_tables(conn)
                conn.execute(f"DELETE FROM {MOVEMENT_TABLE}")
                conn.execute(f"DELETE FROM {ITEM_TABLE}")
                conn.execute("DELETE FROM sqlite_sequence WHERE name IN (?, ?)",
                             (MOVEMENT_TABLE, ITEM_TABLE))
                for item in self._items.values():
                    conn.execute(
                        f"INSERT INTO {ITEM_TABLE} (sku, item_name, category, "
                        f"unit, quantity, avg_cost, sale_price, min_quantity) "
                        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (item["sku"] or None, item["name"], item["category"],
                         item["unit"], item["quantity"], item["avg_cost"],
                         item["sale_price"], item["min_quantity"]),
                    )
                for item_id, movements in self._movements.items():
                    for m in movements:
                        conn.execute(
                            f"INSERT INTO {MOVEMENT_TABLE} (item_id, "
                            f"movement_date, movement_type, quantity, "
                            f"unit_cost, reference, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (item_id, m["date"], m["type"], m["quantity"],
                             m.get("unit_cost") or 0, m["reference"], m["notes"]),
                        )
            log.info("Saved %d inventory items to database", len(self._items))
            return True
        except Exception as exc:
            log.error("inventory save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(ITEM_TABLE):
                    return False
                item_rows = conn.fetch_all(
                    f"SELECT item_id, sku, item_name, category, unit, quantity, "
                    f"avg_cost, sale_price, min_quantity "
                    f"FROM {ITEM_TABLE} ORDER BY item_id"
                )
                mov_rows = conn.fetch_all(
                    f"SELECT movement_id, item_id, movement_date, movement_type, "
                    f"quantity, unit_cost, reference, notes "
                    f"FROM {MOVEMENT_TABLE} ORDER BY movement_id"
                )
        except Exception as exc:
            log.error("inventory load_db error: %s", exc)
            return False
        self._items = {}
        self._movements = {}
        for r in item_rows:
            item = self._row_to_item(r)
            self._items[item["id"]] = item
            self._movements[item["id"]] = []
        for r in mov_rows:
            self._movements[r[1]].append(self._row_to_movement(r))
        self._next_item_id = max(self._items.keys() or [0]) + 1
        self._next_movement_id = max(
            [m["id"] for moves in self._movements.values() for m in moves] + [0]) + 1
        return bool(self._items)

    def clear_db(self):
        try:
            with get_connection() as conn:
                for tbl in (MOVEMENT_TABLE, ITEM_TABLE):
                    if conn.table_exists(tbl):
                        conn.execute(f"DELETE FROM {tbl}")
            return True
        except Exception as exc:
            log.error("inventory clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_item(r):
        return {
            "id": r[0], "sku": r[1] or "", "name": r[2], "category": r[3] or "",
            "unit": r[4] or "", "quantity": float(r[5] or 0),
            "avg_cost": round(float(r[6] or 0), 2),
            "sale_price": round(float(r[7] or 0), 2),
            "min_quantity": float(r[8] or 0),
        }

    @staticmethod
    def _row_to_movement(r):
        return {
            "id": r[0], "item_id": r[1], "date": r[2], "type": r[3],
            "quantity": float(r[4] or 0),
            "unit_cost": round(float(r[5] or 0), 2) if r[5] is not None else None,
            "reference": r[6] or "", "notes": r[7] or "",
        }

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise InventoryError(f"Invalid date: {value!r}")
        raise InventoryError(f"Invalid date: {value!r}")

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise InventoryError(f"Invalid {field}: {value!r}")


inventory_manager = InventoryManager()
