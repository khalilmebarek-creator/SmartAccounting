# محرك الفواتير
# =============
# فواتير بيع/شراء مرقّمة تلقائياً + TVA + عناصر + حالات + تصدير PDF/CSV

from datetime import date
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("invoicing")

INVOICE_TABLE = "invoices"
INVOICE_ITEM_TABLE = "invoice_items"

INVOICE_TYPES = ("sale", "purchase")
INVOICE_STATUSES = ("draft", "confirmed", "paid", "cancelled")
DEFAULT_TVA_RATE = 0.19


class InvoiceError(Exception):
    """خطأ في بيانات الفاتورة"""
    pass


class InvoiceManager:
    """إدارة الفواتير: ترقيم تلقائي + بنود + TVA + حالات + حفظ DB."""

    def __init__(self):
        self._invoices = {}
        self._items = {}
        self._next_invoice_id = 1
        self._next_item_id = 1
        self._sequences = {}

    # ===== الإنشاء =====

    def create_invoice(self, invoice_type, partner_id, invoice_date,
                       items, tva_rate=DEFAULT_TVA_RATE, due_date=None,
                       notes=""):
        """إنشاء فاتورة مع بنودها. Returns: dict (invoice with items).

        items: قائمة {description, quantity, unit_price}.
        """
        invoice_type = (invoice_type or "").strip().lower()
        if invoice_type not in INVOICE_TYPES:
            raise InvoiceError("invoice_type must be 'sale' or 'purchase'")
        invoice_date = self._parse_date(invoice_date).isoformat()
        due_date = self._parse_date(due_date).isoformat() if due_date else None
        tva_rate = self._parse_amount(tva_rate, "tva_rate")
        if tva_rate < 0 or tva_rate > 1:
            raise InvoiceError("tva_rate must be between 0 and 1")
        if not items:
            raise InvoiceError("invoice must have at least one item")
        invoice_id = self._next_invoice_id
        self._next_invoice_id += 1
        number = self.next_invoice_number(invoice_type, int(invoice_date[:4]))
        invoice = {
            "id": invoice_id,
            "number": number,
            "type": invoice_type,
            "partner_id": partner_id,
            "date": invoice_date,
            "due_date": due_date,
            "tva_rate": tva_rate,
            "status": "draft",
            "notes": notes or "",
        }
        self._invoices[invoice_id] = invoice
        self._items[invoice_id] = []
        for item in items:
            self.add_item(invoice_id, item.get("description"),
                          item.get("quantity", 1), item.get("unit_price", 0))
        self._recompute(invoice_id)
        log.info("Created %s invoice %s (id=%s)", invoice_type, number, invoice_id)
        return self.get_invoice(invoice_id)

    def add_item(self, invoice_id, description, quantity=1.0, unit_price=0.0):
        """إضافة بند لفاتورة وإعادة حساب الإجماليات. Returns: item_id."""
        if invoice_id not in self._invoices:
            raise InvoiceError("invoice not found")
        description = (description or "").strip()
        if not description:
            raise InvoiceError("item description is required")
        quantity = self._parse_amount(quantity, "quantity")
        unit_price = self._parse_amount(unit_price, "unit_price")
        if quantity < 0 or unit_price < 0:
            raise InvoiceError("quantity and unit_price must be non-negative")
        item = {
            "id": self._next_item_id,
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
            "amount": round(quantity * unit_price, 2),
        }
        self._next_item_id += 1
        self._items[invoice_id].append(item)
        self._recompute(invoice_id)
        return item["id"]

    def remove_item(self, invoice_id, item_id):
        """حذف بند. Returns: bool."""
        if invoice_id not in self._invoices:
            return False
        before = len(self._items[invoice_id])
        self._items[invoice_id] = [
            it for it in self._items[invoice_id] if it["id"] != item_id
        ]
        if len(self._items[invoice_id]) == before:
            return False
        self._recompute(invoice_id)
        return True

    def _recompute(self, invoice_id):
        invoice = self._invoices[invoice_id]
        subtotal = round(sum(it["amount"] for it in self._items[invoice_id]), 2)
        tva_amount = round(subtotal * invoice["tva_rate"], 2)
        invoice["subtotal"] = subtotal
        invoice["tva_amount"] = tva_amount
        invoice["total"] = round(subtotal + tva_amount, 2)

    # ===== الحالات والاستعلام =====

    def update_status(self, invoice_id, status):
        """تحديث حالة الفاتورة. Returns: bool."""
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return False
        status = (status or "").strip().lower()
        if status not in INVOICE_STATUSES:
            raise InvoiceError(f"status must be one of {INVOICE_STATUSES}")
        invoice["status"] = status
        return True

    def get_invoice(self, invoice_id):
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return None
        result = dict(invoice)
        result["items"] = [dict(it) for it in self._items.get(invoice_id, [])]
        return result

    def list_invoices(self, invoice_type=None, status=None):
        """قائمة الفواتير مع مرشحات. مرتبة تنازلياً بالتاريخ."""
        result = []
        for invoice in self._invoices.values():
            if invoice_type and invoice["type"] != invoice_type:
                continue
            if status and invoice["status"] != status:
                continue
            result.append(self.get_invoice(invoice["id"]))
        result.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
        return result

    def delete_invoice(self, invoice_id):
        if invoice_id not in self._invoices:
            return False
        del self._invoices[invoice_id]
        self._items.pop(invoice_id, None)
        return True

    def find_invoice(self, number=None, invoice_id=None):
        """بحث بالرقم أو المعرّف. Returns: invoice dict أو None."""
        if invoice_id is not None:
            return self.get_invoice(invoice_id)
        if number:
            for inv in self._invoices.values():
                if inv["number"].lower() == str(number).strip().lower():
                    return self.get_invoice(inv["id"])
        return None

    # ===== الترقيم =====

    def next_invoice_number(self, invoice_type, year=None):
        """توليد الرقم التالي: SA-{year}-0001 (بيع) / BT-{year}-0001 (شراء)."""
        invoice_type = (invoice_type or "").strip().lower()
        if invoice_type not in INVOICE_TYPES:
            raise InvoiceError("invoice_type must be 'sale' or 'purchase'")
        year = year or date.today().year
        prefix = "SA" if invoice_type == "sale" else "BT"
        key = (prefix, str(year))
        used = [int(n.split("-")[-1]) for n in
                (i["number"] for i in self._invoices.values())
                if n.startswith(f"{prefix}-{year}-")]
        seq = max(used + [0]) + 1
        return f"{prefix}-{year}-{seq:04d}"

    # ===== التقارير =====

    def totals(self, invoice_type=None, status=None):
        """إحصاءات: عدد الفواتير + مجموع TVA + مجموع الصافي."""
        invoices = self.list_invoices(invoice_type, status)
        return {
            "count": len(invoices),
            "subtotal": round(sum(i["subtotal"] for i in invoices), 2),
            "tva_amount": round(sum(i["tva_amount"] for i in invoices), 2),
            "total": round(sum(i["total"] for i in invoices), 2),
        }

    def by_partner(self, partner_id):
        """فواتير طرف محدد + الإجمالي."""
        rows = [i for i in self.list_invoices() if i["partner_id"] == partner_id]
        return {
            "invoices": rows,
            "total": round(sum(i["total"] for i in rows), 2),
        }

    def export_csv(self, filepath, invoice_type=None):
        """تصدير الفواتير إلى CSV. Returns: bool."""
        import csv
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["number", "type", "partner_id", "date",
                                 "due_date", "subtotal", "tva_rate",
                                 "tva_amount", "total", "status"])
                for inv in self.list_invoices(invoice_type):
                    writer.writerow([
                        inv["number"], inv["type"], inv["partner_id"],
                        inv["date"], inv["due_date"] or "",
                        inv["subtotal"], inv["tva_rate"],
                        inv["tva_amount"], inv["total"], inv["status"],
                    ])
            return True
        except OSError as exc:
            log.error("invoices export_csv error: %s", exc)
            return False

    def clear(self):
        self._invoices = {}
        self._items = {}
        self._next_invoice_id = 1
        self._next_item_id = 1
        self._sequences = {}

    # ===== قاعدة البيانات =====

    def _ensure_tables(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {INVOICE_TABLE} (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number VARCHAR(50) NOT NULL,
                invoice_type VARCHAR(20) NOT NULL,
                partner_id INTEGER NOT NULL,
                invoice_date DATE NOT NULL,
                due_date DATE,
                subtotal DECIMAL(15,2) DEFAULT 0,
                tva_rate DECIMAL(5,4) DEFAULT 0,
                tva_amount DECIMAL(15,2) DEFAULT 0,
                total DECIMAL(15,2) DEFAULT 0,
                status VARCHAR(20) DEFAULT 'draft',
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(invoice_number)
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {INVOICE_ITEM_TABLE} (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                description VARCHAR(255) NOT NULL,
                quantity DECIMAL(15,2) DEFAULT 1,
                unit_price DECIMAL(15,2) DEFAULT 0,
                amount DECIMAL(15,2) DEFAULT 0,
                FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_tables(conn)
                conn.execute(f"DELETE FROM {INVOICE_ITEM_TABLE}")
                conn.execute(f"DELETE FROM {INVOICE_TABLE}")
                conn.execute(
                    "DELETE FROM sqlite_sequence WHERE name IN (?, ?)",
                    (INVOICE_ITEM_TABLE, INVOICE_TABLE),
                )
                for inv in self._invoices.values():
                    conn.execute(
                        f"INSERT INTO {INVOICE_TABLE} (invoice_number, "
                        f"invoice_type, partner_id, invoice_date, due_date, "
                        f"subtotal, tva_rate, tva_amount, total, status, notes) "
                        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (inv["number"], inv["type"], inv["partner_id"],
                         inv["date"], inv.get("due_date"),
                         inv.get("subtotal", 0), inv["tva_rate"],
                         inv.get("tva_amount", 0), inv.get("total", 0),
                         inv["status"], inv.get("notes", "")),
                    )
                for inv_id, items in self._items.items():
                    for it in items:
                        conn.execute(
                            f"INSERT INTO {INVOICE_ITEM_TABLE} (invoice_id, "
                            f"description, quantity, unit_price, amount) "
                            f"VALUES (?, ?, ?, ?, ?)",
                            (inv_id, it["description"], it["quantity"],
                             it["unit_price"], it["amount"]),
                        )
            log.info("Saved %d invoices to database", len(self._invoices))
            return True
        except Exception as exc:
            log.error("invoices save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(INVOICE_TABLE):
                    return False
                inv_rows = conn.fetch_all(
                    f"SELECT invoice_id, invoice_number, invoice_type, "
                    f"partner_id, invoice_date, due_date, subtotal, tva_rate, "
                    f"tva_amount, total, status, notes "
                    f"FROM {INVOICE_TABLE} ORDER BY invoice_id"
                )
                item_rows = conn.fetch_all(
                    f"SELECT item_id, invoice_id, description, quantity, "
                    f"unit_price, amount FROM {INVOICE_ITEM_TABLE} "
                    f"ORDER BY item_id"
                )
        except Exception as exc:
            log.error("invoices load_db error: %s", exc)
            return False
        self._invoices = {}
        self._items = {}
        for r in inv_rows:
            self._invoices[r[0]] = self._row_to_invoice(r)
            self._items[r[0]] = []
        for r in item_rows:
            self._items[r[1]].append(self._row_to_item(r))
        self._next_invoice_id = max(self._invoices.keys() or [0]) + 1
        self._next_item_id = max([it["id"] for items in self._items.values()
                                  for it in items] + [0]) + 1
        return bool(self._invoices)

    def clear_db(self):
        try:
            with get_connection() as conn:
                for tbl in (INVOICE_ITEM_TABLE, INVOICE_TABLE):
                    if conn.table_exists(tbl):
                        conn.execute(f"DELETE FROM {tbl}")
            return True
        except Exception as exc:
            log.error("invoices clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_invoice(r):
        return {
            "id": r[0], "number": r[1], "type": r[2], "partner_id": r[3],
            "date": r[4], "due_date": r[5],
            "subtotal": round(float(r[6] or 0), 2),
            "tva_rate": float(r[7] or 0),
            "tva_amount": round(float(r[8] or 0), 2),
            "total": round(float(r[9] or 0), 2),
            "status": r[10], "notes": r[11] or "",
        }

    @staticmethod
    def _row_to_item(r):
        return {
            "id": r[0], "description": r[2],
            "quantity": float(r[3] or 0), "unit_price": float(r[4] or 0),
            "amount": round(float(r[5] or 0), 2),
        }

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise InvoiceError(f"Invalid date: {value!r}")
        raise InvoiceError(f"Invalid date: {value!r}")

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise InvoiceError(f"Invalid {field}: {value!r}")


invoice_manager = InvoiceManager()
