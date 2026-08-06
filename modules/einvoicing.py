# محرك الفواتير الإلكترونية
# ==========================
# توقيع رقمي + رمز QR + تحقق سلامة + تصدير XML/JSON + تتبع دورة الحياة

import hashlib
import json
from datetime import date, datetime
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("einvoicing")

EINVOICE_TABLE = "einvoices"
EINVOICE_ITEM_TABLE = "einvoice_items"

EINVOICE_STATUSES = ("draft", "generated", "verified", "sent", "paid", "cancelled")


class EInvoiceError(Exception):
    pass


class EInvoiceManager:

    def __init__(self):
        self._invoices = {}
        self._items = {}
        self._next_id = 1
        self._next_item_id = 1

    def create(self, customer, customer_tax_id="", invoice_date=None,
               due_date=None, notes="", reference=""):
        customer = (customer or "").strip()
        if not customer:
            raise EInvoiceError("customer is required")
        invoice_date = self._parse_date(invoice_date or date.today()).isoformat()
        due_date = self._parse_date(due_date).isoformat() if due_date else None
        invoice = {
            "id": self._next_id,
            "number": self._next_number(),
            "customer": customer,
            "customer_tax_id": customer_tax_id or "",
            "date": invoice_date,
            "due_date": due_date,
            "reference": reference or "",
            "notes": notes or "",
            "status": "draft",
            "subtotal": 0.0,
            "tva_total": 0.0,
            "grand_total": 0.0,
            "hash": "",
            "qr_data": "",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self._next_id += 1
        self._invoices[invoice["id"]] = invoice
        self._items[invoice["id"]] = []
        log.debug("Created e-invoice %s: %s", invoice["number"], customer)
        return invoice["id"]

    def add_item(self, invoice_id, description, quantity=1.0,
                 unit_price=0.0, tva_rate=0.19):
        if invoice_id not in self._invoices:
            raise EInvoiceError("invoice not found")
        description = (description or "").strip()
        if not description:
            raise EInvoiceError("item description is required")
        quantity = self._parse_amount(quantity, "quantity")
        unit_price = self._parse_amount(unit_price, "unit_price")
        tva_rate = self._parse_amount(tva_rate, "tva_rate")
        if quantity <= 0:
            raise EInvoiceError("quantity must be positive")
        if unit_price < 0:
            raise EInvoiceError("unit_price must be non-negative")
        if tva_rate < 0 or tva_rate > 1:
            raise EInvoiceError("tva_rate must be between 0 and 1")
        line_total = round(quantity * unit_price, 2)
        tva = round(line_total * tva_rate, 2)
        item = {
            "id": self._next_item_id,
            "invoice_id": invoice_id,
            "description": description,
            "quantity": quantity,
            "unit_price": unit_price,
            "tva_rate": tva_rate,
            "line_total": line_total,
            "tva": tva,
            "total": round(line_total + tva, 2),
        }
        self._next_item_id += 1
        self._items[invoice_id].append(item)
        self._recalc(invoice_id)
        return item["id"]

    def remove_item(self, invoice_id, item_id):
        if invoice_id not in self._invoices:
            return False
        before = len(self._items[invoice_id])
        self._items[invoice_id] = [
            it for it in self._items[invoice_id] if it["id"] != item_id
        ]
        if len(self._items[invoice_id]) == before:
            return False
        self._recalc(invoice_id)
        return True

    def _recalc(self, invoice_id):
        inv = self._invoices[invoice_id]
        items = self._items.get(invoice_id, [])
        inv["subtotal"] = round(sum(it["line_total"] for it in items), 2)
        inv["tva_total"] = round(sum(it["tva"] for it in items), 2)
        inv["grand_total"] = round(inv["subtotal"] + inv["tva_total"], 2)

    def _canonical_data(self, invoice_id):
        """البيانات القانونية للتوقيع (بدون الحقول الديناميكية: hash, qr_data, status, created_at)."""
        inv = self._invoices[invoice_id]
        return {
            "number": inv["number"],
            "customer": inv["customer"],
            "customer_tax_id": inv["customer_tax_id"],
            "date": inv["date"],
            "due_date": inv.get("due_date"),
            "reference": inv["reference"],
            "notes": inv["notes"],
            "subtotal": inv["subtotal"],
            "tva_total": inv["tva_total"],
            "grand_total": inv["grand_total"],
            "items": [{
                "description": it["description"],
                "quantity": it["quantity"],
                "unit_price": it["unit_price"],
                "tva_rate": it["tva_rate"],
                "line_total": it["line_total"],
                "tva": it["tva"],
                "total": it["total"],
            } for it in self._items.get(invoice_id, [])],
        }

    def generate(self, invoice_id):
        """توليد الفاتورة الإلكترونية: التوقيع الرقمي + رمز QR. Returns: dict."""
        inv = self._invoices.get(invoice_id)
        if not inv:
            raise EInvoiceError("invoice not found")
        if not self._items.get(invoice_id):
            raise EInvoiceError("invoice has no items")
        data = self._canonical_data(invoice_id)
        inv["hash"] = hashlib.sha256(
            json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
            .encode("utf-8")).hexdigest()
        qr_payload = json.dumps({
            "number": inv["number"],
            "date": inv["date"],
            "customer": inv["customer"],
            "tax_id": inv["customer_tax_id"],
            "total": inv["grand_total"],
            "tva": inv["tva_total"],
            "hash": inv["hash"][:16],
        }, ensure_ascii=False, separators=(",", ":"))
        inv["qr_data"] = qr_payload
        inv["status"] = "generated"
        log.info("Generated e-invoice %s (hash=%s...)", inv["number"], inv["hash"][:16])
        return self.get_invoice(invoice_id)

    def verify(self, invoice_id):
        """التحقق من سلامة الفاتورة الإلكترونية. Returns: (bool, message)."""
        inv = self._invoices.get(invoice_id)
        if not inv:
            return False, "invoice not found"
        if not inv["hash"]:
            return False, "invoice not generated yet"
        data = self._canonical_data(invoice_id)
        current_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
            .encode("utf-8")).hexdigest()
        if current_hash != inv["hash"]:
            return False, "data tampered"
        return True, "verified"

    def get_invoice(self, invoice_id):
        inv = self._invoices.get(invoice_id)
        if not inv:
            return None
        result = dict(inv)
        result["items"] = [dict(it) for it in self._items.get(invoice_id, [])]
        return result

    def list_invoices(self, status=None, customer=None):
        result = []
        for inv in self._invoices.values():
            if status and inv["status"] != status:
                continue
            if customer and customer.lower() not in inv["customer"].lower():
                continue
            row = dict(inv)
            row["item_count"] = len(self._items.get(inv["id"], []))
            result.append(row)
        result.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
        return result

    def update_status(self, invoice_id, status):
        inv = self._invoices.get(invoice_id)
        if not inv:
            return False
        status = (status or "").strip().lower()
        if status not in EINVOICE_STATUSES:
            raise EInvoiceError(f"status must be one of {EINVOICE_STATUSES}")
        inv["status"] = status
        return True

    def delete(self, invoice_id):
        if invoice_id not in self._invoices:
            return False
        del self._invoices[invoice_id]
        self._items.pop(invoice_id, None)
        return True

    def export_json(self, invoice_id):
        """تصدير فاتورة واحدة إلى JSON الكتروني كامل."""
        inv = self.get_invoice(invoice_id)
        if not inv:
            return None
        return json.dumps(inv, ensure_ascii=False, indent=2, default=str)

    def _next_number(self):
        year = str(date.today().year)
        nums = []
        for inv in self._invoices.values():
            if inv["number"].startswith(f"EINV-{year}-"):
                try:
                    nums.append(int(inv["number"].split("-")[-1]))
                except ValueError:
                    pass
        seq = max(nums + [0]) + 1
        return f"EINV-{year}-{seq:06d}"

    def totals(self):
        invoices = list(self._invoices.values())
        return {
            "count": len(invoices),
            "subtotal": round(sum(i["subtotal"] for i in invoices), 2),
            "tva_total": round(sum(i["tva_total"] for i in invoices), 2),
            "grand_total": round(sum(i["grand_total"] for i in invoices), 2),
        }

    def clear(self):
        self._invoices = {}
        self._items = {}
        self._next_id = 1
        self._next_item_id = 1

    def _ensure_tables(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {EINVOICE_TABLE} (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number VARCHAR(50) NOT NULL UNIQUE,
                customer VARCHAR(255) NOT NULL,
                customer_tax_id VARCHAR(50),
                invoice_date DATE NOT NULL,
                due_date DATE,
                reference VARCHAR(100),
                notes TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                subtotal DECIMAL(15,2) DEFAULT 0,
                tva_total DECIMAL(15,2) DEFAULT 0,
                grand_total DECIMAL(15,2) DEFAULT 0,
                hash VARCHAR(64),
                qr_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {EINVOICE_ITEM_TABLE} (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                description VARCHAR(255) NOT NULL,
                quantity DECIMAL(15,3) DEFAULT 1,
                unit_price DECIMAL(15,2) DEFAULT 0,
                tva_rate DECIMAL(5,4) DEFAULT 0.19,
                line_total DECIMAL(15,2) DEFAULT 0,
                tva DECIMAL(15,2) DEFAULT 0,
                total DECIMAL(15,2) DEFAULT 0,
                FOREIGN KEY (invoice_id) REFERENCES {EINVOICE_TABLE}(invoice_id)
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_tables(conn)
                conn.execute(f"DELETE FROM {EINVOICE_ITEM_TABLE}")
                conn.execute(f"DELETE FROM {EINVOICE_TABLE}")
                conn.execute(
                    "DELETE FROM sqlite_sequence WHERE name IN (?, ?)",
                    (EINVOICE_ITEM_TABLE, EINVOICE_TABLE),
                )
                for inv in self._invoices.values():
                    conn.execute(
                        f"INSERT INTO {EINVOICE_TABLE} (invoice_number, "
                        f"customer, customer_tax_id, invoice_date, due_date, "
                        f"reference, notes, status, subtotal, tva_total, "
                        f"grand_total, hash, qr_data) VALUES "
                        f"(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (inv["number"], inv["customer"],
                         inv["customer_tax_id"] or None,
                         inv["date"], inv.get("due_date"),
                         inv["reference"] or None, inv["notes"] or None,
                         inv["status"], inv["subtotal"], inv["tva_total"],
                         inv["grand_total"], inv["hash"] or None,
                         inv["qr_data"] or None),
                    )
                for inv_id, items in self._items.items():
                    for it in items:
                        conn.execute(
                            f"INSERT INTO {EINVOICE_ITEM_TABLE} (invoice_id, "
                            f"description, quantity, unit_price, tva_rate, "
                            f"line_total, tva, total) VALUES "
                            f"(?, ?, ?, ?, ?, ?, ?, ?)",
                            (inv_id, it["description"], it["quantity"],
                             it["unit_price"], it["tva_rate"],
                             it["line_total"], it["tva"], it["total"]),
                        )
            log.info("Saved %d e-invoices to database", len(self._invoices))
            return True
        except Exception as exc:
            log.error("einvoicing save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(EINVOICE_TABLE):
                    return False
                inv_rows = conn.fetch_all(
                    f"SELECT invoice_id, invoice_number, customer, "
                    f"customer_tax_id, invoice_date, due_date, reference, "
                    f"notes, status, subtotal, tva_total, grand_total, "
                    f"hash, qr_data, created_at FROM {EINVOICE_TABLE} "
                    f"ORDER BY invoice_id"
                )
                item_rows = conn.fetch_all(
                    f"SELECT item_id, invoice_id, description, quantity, "
                    f"unit_price, tva_rate, line_total, tva, total "
                    f"FROM {EINVOICE_ITEM_TABLE} ORDER BY item_id"
                )
        except Exception as exc:
            log.error("einvoicing load_db error: %s", exc)
            return False
        self._invoices = {}
        self._items = {}
        for r in inv_rows:
            inv = self._row_to_invoice(r)
            self._invoices[inv["id"]] = inv
            self._items[inv["id"]] = []
        for r in item_rows:
            item = self._row_to_item(r)
            oid = item["invoice_id"]
            if oid in self._items:
                self._items[oid].append(item)
        self._next_id = max(self._invoices.keys() or [0]) + 1
        self._next_item_id = max(
            [it["id"] for its in self._items.values() for it in its] + [0]
        ) + 1
        return bool(self._invoices)

    def clear_db(self):
        try:
            with get_connection() as conn:
                for tbl in (EINVOICE_ITEM_TABLE, EINVOICE_TABLE):
                    if conn.table_exists(tbl):
                        conn.execute(f"DELETE FROM {tbl}")
            return True
        except Exception as exc:
            log.error("einvoicing clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_invoice(r):
        return {
            "id": r[0], "number": r[1], "customer": r[2],
            "customer_tax_id": r[3] or "",
            "date": r[4], "due_date": r[5] if r[5] else None,
            "reference": r[6] or "", "notes": r[7] or "",
            "status": r[8], "subtotal": round(float(r[9] or 0), 2),
            "tva_total": round(float(r[10] or 0), 2),
            "grand_total": round(float(r[11] or 0), 2),
            "hash": r[12] or "", "qr_data": r[13] or "",
            "created_at": r[14] or "",
        }

    @staticmethod
    def _row_to_item(r):
        return {
            "id": r[0], "invoice_id": r[1], "description": r[2],
            "quantity": float(r[3] or 1),
            "unit_price": round(float(r[4] or 0), 2),
            "tva_rate": float(r[5] or 0.19),
            "line_total": round(float(r[6] or 0), 2),
            "tva": round(float(r[7] or 0), 2),
            "total": round(float(r[8] or 0), 2),
        }

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise EInvoiceError(f"Invalid date: {value!r}")
        raise EInvoiceError(f"Invalid date: {value!r}")

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise EInvoiceError(f"Invalid {field}: {value!r}")


einvoice_manager = EInvoiceManager()
