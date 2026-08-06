# محرك المشتريات
# ===============
# طلبات شراء + موردين + بنود + تاريخ الحالة + تكامل المخزون

from datetime import date
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("procurement")

ORDERS_TABLE = "procurement_orders"
ITEMS_TABLE = "procurement_order_items"

ORDER_STATUSES = ("draft", "pending", "approved", "received", "cancelled")


class ProcurementError(Exception):
    pass


class ProcurementManager:

    def __init__(self):
        self._orders = {}
        self._items = {}
        self._next_order_id = 1
        self._next_item_id = 1

    def add_order(self, supplier, order_date, reference="", notes="",
                  status="pending"):
        supplier = (supplier or "").strip()
        if not supplier:
            raise ProcurementError("supplier is required")
        order_date = self._parse_date(order_date).isoformat()
        status = (status or "").strip().lower()
        if status not in ORDER_STATUSES:
            raise ProcurementError(f"status must be one of {ORDER_STATUSES}")
        order = {
            "id": self._next_order_id,
            "supplier": supplier,
            "date": order_date,
            "reference": reference or "",
            "notes": notes or "",
            "status": status,
            "total": 0.0,
            "tax": 0.0,
            "grand_total": 0.0,
        }
        self._next_order_id += 1
        self._orders[order["id"]] = order
        self._items[order["id"]] = []
        log.debug("Added procurement order %s: %s", order["id"], supplier)
        return order["id"]

    def update_order(self, order_id, **fields):
        order = self._orders.get(order_id)
        if not order:
            return False
        allowed = ("supplier", "date", "reference", "notes", "status")
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "supplier":
                value = (value or "").strip()
                if not value:
                    raise ProcurementError("supplier is required")
            elif key == "date":
                value = self._parse_date(value).isoformat()
            elif key == "status":
                value = (value or "").strip().lower()
                if value not in ORDER_STATUSES:
                    raise ProcurementError(
                        f"status must be one of {ORDER_STATUSES}")
            order[key] = value
        return True

    def delete_order(self, order_id):
        if order_id not in self._orders:
            return False
        del self._orders[order_id]
        self._items.pop(order_id, None)
        return True

    def get_order(self, order_id):
        order = self._orders.get(order_id)
        if not order:
            return None
        result = dict(order)
        result["items"] = [dict(i) for i in self._items.get(order_id, [])]
        return result

    def list_orders(self, status=None, supplier=None):
        result = []
        for order in self._orders.values():
            if status and order["status"] != status:
                continue
            if supplier and supplier.lower() not in order["supplier"].lower():
                continue
            row = dict(order)
            row["item_count"] = len(self._items.get(order["id"], []))
            result.append(row)
        result.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
        return result

    def add_item(self, order_id, name, quantity=1.0, unit_price=0.0,
                 unit="", tax_rate=0.0):
        if order_id not in self._orders:
            raise ProcurementError("order not found")
        name = (name or "").strip()
        if not name:
            raise ProcurementError("item name is required")
        quantity = self._parse_amount(quantity, "quantity")
        unit_price = self._parse_amount(unit_price, "unit_price")
        tax_rate = self._parse_amount(tax_rate, "tax_rate")
        if quantity <= 0:
            raise ProcurementError("quantity must be positive")
        if unit_price < 0:
            raise ProcurementError("unit_price must be non-negative")
        if tax_rate < 0:
            raise ProcurementError("tax_rate must be non-negative")
        line_total = round(quantity * unit_price, 2)
        tax = round(line_total * tax_rate / 100, 2)
        item = {
            "id": self._next_item_id,
            "order_id": order_id,
            "name": name,
            "quantity": quantity,
            "unit_price": unit_price,
            "unit": unit or "",
            "tax_rate": tax_rate,
            "line_total": line_total,
            "tax": tax,
            "grand_total": round(line_total + tax, 2),
        }
        self._next_item_id += 1
        self._items[order_id].append(item)
        self._recalc_order(order_id)
        log.debug("Added item %s to order %s", item["id"], order_id)
        return item["id"]

    def update_item(self, item_id, **fields):
        for order_id, items in self._items.items():
            for item in items:
                if item["id"] == item_id:
                    for key, value in fields.items():
                        if key not in ("name", "quantity", "unit_price",
                                       "unit", "tax_rate"):
                            continue
                        if key == "name":
                            value = (value or "").strip()
                            if not value:
                                raise ProcurementError(
                                    "item name is required")
                        elif key in ("quantity", "unit_price", "tax_rate"):
                            value = self._parse_amount(value, key)
                        item[key] = value
                    item["line_total"] = round(
                        item["quantity"] * item["unit_price"], 2)
                    item["tax"] = round(
                        item["line_total"] * item["tax_rate"] / 100, 2)
                    item["grand_total"] = round(
                        item["line_total"] + item["tax"], 2)
                    self._recalc_order(order_id)
                    return True
        return False

    def delete_item(self, item_id):
        for order_id, items in self._items.items():
            for item in items:
                if item["id"] == item_id:
                    items.remove(item)
                    self._recalc_order(order_id)
                    return True
        return False

    def order_items(self, order_id):
        return [dict(i) for i in self._items.get(order_id, [])]

    def _recalc_order(self, order_id):
        order = self._orders.get(order_id)
        if not order:
            return
        items = self._items.get(order_id, [])
        order["total"] = round(sum(i["line_total"] for i in items), 2)
        order["tax"] = round(sum(i["tax"] for i in items), 2)
        order["grand_total"] = round(order["total"] + order["tax"], 2)

    def set_status(self, order_id, status):
        order = self._orders.get(order_id)
        if not order:
            return False
        status = (status or "").strip().lower()
        if status not in ORDER_STATUSES:
            raise ProcurementError(f"status must be one of {ORDER_STATUSES}")
        order["status"] = status
        return True

    def clear(self):
        self._orders = {}
        self._items = {}
        self._next_order_id = 1
        self._next_item_id = 1

    def _ensure_tables(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {ORDERS_TABLE} (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier VARCHAR(255) NOT NULL,
                order_date DATE NOT NULL,
                reference VARCHAR(100),
                notes TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                total DECIMAL(15,2) DEFAULT 0,
                tax DECIMAL(15,2) DEFAULT 0,
                grand_total DECIMAL(15,2) DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {ITEMS_TABLE} (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                item_name VARCHAR(255) NOT NULL,
                quantity DECIMAL(15,3) DEFAULT 1,
                unit_price DECIMAL(15,2) DEFAULT 0,
                unit VARCHAR(50),
                tax_rate DECIMAL(5,2) DEFAULT 0,
                line_total DECIMAL(15,2) DEFAULT 0,
                tax DECIMAL(15,2) DEFAULT 0,
                grand_total DECIMAL(15,2) DEFAULT 0,
                FOREIGN KEY (order_id) REFERENCES {ORDERS_TABLE}(order_id)
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_tables(conn)
                conn.execute(f"DELETE FROM {ITEMS_TABLE}")
                conn.execute(f"DELETE FROM {ORDERS_TABLE}")
                conn.execute("DELETE FROM sqlite_sequence WHERE name IN (?, ?)",
                             (ITEMS_TABLE, ORDERS_TABLE))
                for order in self._orders.values():
                    conn.execute(
                        f"INSERT INTO {ORDERS_TABLE} (supplier, order_date, "
                        f"reference, notes, status, total, tax, grand_total) "
                        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (order["supplier"], order["date"],
                         order["reference"] or None, order["notes"] or None,
                         order["status"], order["total"], order["tax"],
                         order["grand_total"]),
                    )
                for order_id, items in self._items.items():
                    for item in items:
                        conn.execute(
                            f"INSERT INTO {ITEMS_TABLE} (order_id, item_name, "
                            f"quantity, unit_price, unit, tax_rate, "
                            f"line_total, tax, grand_total) "
                            f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (order_id, item["name"], item["quantity"],
                             item["unit_price"], item["unit"] or None,
                             item["tax_rate"], item["line_total"],
                             item["tax"], item["grand_total"]),
                        )
            log.info("Saved %d procurement orders to database",
                     len(self._orders))
            return True
        except Exception as exc:
            log.error("procurement save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(ORDERS_TABLE):
                    return False
                order_rows = conn.fetch_all(
                    f"SELECT order_id, supplier, order_date, reference, "
                    f"notes, status, total, tax, grand_total "
                    f"FROM {ORDERS_TABLE} ORDER BY order_id"
                )
                item_rows = conn.fetch_all(
                    f"SELECT item_id, order_id, item_name, quantity, "
                    f"unit_price, unit, tax_rate, line_total, tax, "
                    f"grand_total FROM {ITEMS_TABLE} ORDER BY item_id"
                )
        except Exception as exc:
            log.error("procurement load_db error: %s", exc)
            return False
        self._orders = {}
        self._items = {}
        for r in order_rows:
            order = self._row_to_order(r)
            self._orders[order["id"]] = order
            self._items[order["id"]] = []
        for r in item_rows:
            item = self._row_to_item(r)
            oid = item["order_id"]
            if oid in self._items:
                self._items[oid].append(item)
        self._next_order_id = max(self._orders.keys() or [0]) + 1
        self._next_item_id = max(
            [it["id"] for its in self._items.values() for it in its] + [0]) + 1
        return bool(self._orders)

    def clear_db(self):
        try:
            with get_connection() as conn:
                for tbl in (ITEMS_TABLE, ORDERS_TABLE):
                    if conn.table_exists(tbl):
                        conn.execute(f"DELETE FROM {tbl}")
            return True
        except Exception as exc:
            log.error("procurement clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_order(r):
        return {
            "id": r[0], "supplier": r[1], "date": r[2],
            "reference": r[3] or "", "notes": r[4] or "",
            "status": r[5] or "pending",
            "total": round(float(r[6] or 0), 2),
            "tax": round(float(r[7] or 0), 2),
            "grand_total": round(float(r[8] or 0), 2),
        }

    @staticmethod
    def _row_to_item(r):
        return {
            "id": r[0], "order_id": r[1], "name": r[2],
            "quantity": float(r[3] or 1),
            "unit_price": round(float(r[4] or 0), 2),
            "unit": r[5] or "",
            "tax_rate": round(float(r[6] or 0), 2),
            "line_total": round(float(r[7] or 0), 2),
            "tax": round(float(r[8] or 0), 2),
            "grand_total": round(float(r[9] or 0), 2),
        }

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ProcurementError(f"Invalid date: {value!r}")
        raise ProcurementError(f"Invalid date: {value!r}")

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ProcurementError(f"Invalid {field}: {value!r}")


procurement_manager = ProcurementManager()
