# محرك العملاء والموردين (AR/AP)
# ===============================
# إدارة الأطراف (عملاء/موردون) + معاملاتهم + الأرصدة + آجال الاستحقاق

from datetime import date
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("partners")

PARTNER_TABLE = "partners"
PARTNER_TX_TABLE = "partner_transactions"

PARTNER_TYPES = ("customer", "supplier")
TX_TYPES = ("invoice", "payment", "credit_note", "debit_note")


class PartnerError(Exception):
    """خطأ في بيانات العملاء/الموردين"""
    pass


class PartnerManager:
    """إدارة العملاء والموردين ورصد أرصدة الذمم المدينة/الدائنة.

    قاعدة الرصيد:
      - عميل (customer): فاتورة تُزيد الذمم (+)، سداد تُنقص (−).
      - مورد (supplier): فاتورة تُزيد الذمم (+)، سداد تُنقص (−).
    """

    def __init__(self):
        self._partners = []
        self._transactions = []
        self._next_partner_id = 1
        self._next_tx_id = 1

    # ===== الأطراف =====

    def add_partner(self, partner_type, name, phone="", email="", address="",
                    tax_id="", notes=""):
        """إضافة عميل/مورد. Returns: partner_id."""
        partner_type = (partner_type or "").strip().lower()
        if partner_type not in PARTNER_TYPES:
            raise PartnerError("partner_type must be 'customer' or 'supplier'")
        name = (name or "").strip()
        if not name:
            raise PartnerError("partner name is required")
        partner = {
            "id": self._next_partner_id,
            "type": partner_type,
            "name": name,
            "phone": phone or "",
            "email": email or "",
            "address": address or "",
            "tax_id": tax_id or "",
            "notes": notes or "",
        }
        self._partners.append(partner)
        self._next_partner_id += 1
        log.debug("Added partner %s: %s", partner["id"], name)
        return partner["id"]

    def update_partner(self, partner_id, **fields):
        """تحديث حقول طرف. Returns: bool."""
        stored = next((p for p in self._partners if p["id"] == partner_id), None)
        if not stored:
            return False
        for key, value in fields.items():
            if key in stored and key != "id" and value is not None:
                stored[key] = value
        if "name" in fields and not (fields.get("name") or "").strip():
            raise PartnerError("partner name is required")
        if "type" in fields:
            ftype = (fields["type"] or "").strip().lower()
            if ftype not in PARTNER_TYPES:
                raise PartnerError("partner_type must be 'customer' or 'supplier'")
            stored["type"] = ftype
        return True

    def delete_partner(self, partner_id):
        """حذف طرف ومعاملاته. Returns: bool."""
        if not self.get_partner(partner_id):
            return False
        self._partners = [p for p in self._partners if p["id"] != partner_id]
        self._transactions = [t for t in self._transactions
                              if t["partner_id"] != partner_id]
        return True

    def get_partner(self, partner_id):
        for p in self._partners:
            if p["id"] == partner_id:
                return dict(p)
        return None

    def list_partners(self, partner_type=None):
        """قائمة الأطراف (اختيارياً حسب النوع) مع الرصيد الحالي."""
        result = []
        for p in self._partners:
            if partner_type and p["type"] != partner_type:
                continue
            row = dict(p)
            row["balance"] = self.get_balance(p["id"])
            result.append(row)
        result.sort(key=lambda x: x["name"].lower())
        return result

    def search_partners(self, term, partner_type=None):
        """بحث نصي في الاسم/الهاتف/البريد. Returns: قائمة."""
        term = (term or "").strip().lower()
        result = []
        for p in self._partners:
            if partner_type and p["type"] != partner_type:
                continue
            haystack = " ".join([p["name"], p["phone"], p["email"],
                                 p["tax_id"]]).lower()
            if not term or term in haystack:
                result.append(dict(p))
        return result

    # ===== المعاملات =====

    def add_transaction(self, partner_id, tx_date, tx_type, amount,
                        reference="", notes=""):
        """إضافة معاملة على حساب طرف. Returns: transaction_id.

        transaction_type: invoice / payment / credit_note / debit_note.
        """
        if not self.get_partner(partner_id):
            raise PartnerError("partner not found")
        tx_type = (tx_type or "").strip().lower()
        if tx_type not in TX_TYPES:
            raise PartnerError(f"transaction_type must be one of {TX_TYPES}")
        amount = self._parse_amount(amount, "amount")
        if amount <= 0:
            raise PartnerError("amount must be positive")
        tx_date = self._parse_date(tx_date).isoformat()
        tx = {
            "id": self._next_tx_id,
            "partner_id": partner_id,
            "date": tx_date,
            "type": tx_type,
            "amount": round(amount, 2),
            "reference": reference or "",
            "notes": notes or "",
        }
        self._transactions.append(tx)
        self._next_tx_id += 1
        log.debug("Added %s transaction %s for partner %s",
                  tx_type, tx["id"], partner_id)
        return tx["id"]

    def get_transaction(self, tx_id):
        for t in self._transactions:
            if t["id"] == tx_id:
                return dict(t)
        return None

    def list_transactions(self, partner_id=None, tx_type=None):
        """معاملات طرف (أو كلها) مرتبة تاريخياً."""
        result = []
        for t in self._transactions:
            if partner_id and t["partner_id"] != partner_id:
                continue
            if tx_type and t["type"] != tx_type:
                continue
            result.append(dict(t))
        result.sort(key=lambda x: (x["date"], x["id"]))
        return result

    # ===== الأرصدة =====

    def get_balance(self, partner_id):
        """رصيد الذمم لطرف.

        موجب = مستحق للطرف أو علينا حسب نوعه:
          customer: موجبة = مستحق من العميل (AR)، سالبة = رصيد دائن.
          supplier: موجبة = مستحق للمورد (AP)، سالبة = رصيد مدين.
        """
        partner = self.get_partner(partner_id)
        if not partner:
            return 0.0
        balance = 0.0
        for t in self._transactions:
            if t["partner_id"] != partner_id:
                continue
            if t["type"] in ("invoice", "debit_note"):
                balance += t["amount"]
            elif t["type"] in ("payment", "credit_note"):
                balance -= t["amount"]
        return round(balance, 2)

    def get_balance_details(self, partner_id):
        """تفصيل الرصيد: إجمالي الفواتير، المدفوعات، الصافي."""
        total_invoiced = 0.0
        total_paid = 0.0
        for t in self._transactions:
            if t["partner_id"] != partner_id:
                continue
            if t["type"] in ("invoice", "debit_note"):
                total_invoiced += t["amount"]
            elif t["type"] in ("payment", "credit_note"):
                total_paid += t["amount"]
        return {
            "invoiced": round(total_invoiced, 2),
            "paid": round(total_paid, 2),
            "net": round(total_invoiced - total_paid, 2),
        }

    def aging(self, partner_id=None, as_of=None):
        """آجال الاستحقاق: الفواتير غير المسددة مجمّعة حسب العمر (أيام).

        Returns: قائمة {partner_id, partner_name, partner_type,
                 current, days_1_30, days_31_60, days_61_90, days_90_plus, total}
        """
        as_of = self._parse_date(as_of or date.today())
        partner_ids = [partner_id] if partner_id else \
            [p["id"] for p in self._partners]
        buckets = []
        for pid in partner_ids:
            partner = self.get_partner(pid)
            if not partner:
                continue
            invoiced = {}
            paid = 0.0
            for t in self._transactions:
                if t["partner_id"] != pid:
                    continue
                if t["type"] in ("invoice", "debit_note"):
                    invoiced[t["id"]] = t
                elif t["type"] in ("payment", "credit_note"):
                    paid += t["amount"]
            outstanding = []
            for t in invoiced.values():
                remaining = t["amount"]
                if paid > 0:
                    take = min(remaining, paid)
                    remaining -= take
                    paid -= take
                if remaining > 0:
                    age = max((as_of - self._parse_date(t["date"])).days, 0)
                    outstanding.append((age, remaining))
            row = {
                "partner_id": pid,
                "partner_name": partner["name"],
                "partner_type": partner["type"],
                "current": 0.0, "days_1_30": 0.0, "days_31_60": 0.0,
                "days_61_90": 0.0, "days_90_plus": 0.0, "total": 0.0,
            }
            for age, amount in outstanding:
                amount = round(amount, 2)
                if age == 0:
                    row["current"] = round(row["current"] + amount, 2)
                elif age <= 30:
                    row["days_1_30"] = round(row["days_1_30"] + amount, 2)
                elif age <= 60:
                    row["days_31_60"] = round(row["days_31_60"] + amount, 2)
                elif age <= 90:
                    row["days_61_90"] = round(row["days_61_90"] + amount, 2)
                else:
                    row["days_90_plus"] = round(row["days_90_plus"] + amount, 2)
            row["total"] = round(sum([row[k] for k in
                ("current", "days_1_30", "days_31_60", "days_61_90",
                 "days_90_plus")]), 2)
            buckets.append(row)
        buckets.sort(key=lambda x: x["partner_name"].lower())
        return buckets

    def clear(self):
        self._partners = []
        self._transactions = []
        self._next_partner_id = 1
        self._next_tx_id = 1

    # ===== قاعدة البيانات =====

    def _ensure_tables(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {PARTNER_TABLE} (
                partner_id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_type VARCHAR(20) NOT NULL,
                partner_name VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                email VARCHAR(255),
                address TEXT,
                tax_id VARCHAR(100),
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {PARTNER_TX_TABLE} (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER NOT NULL,
                transaction_date DATE NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                amount DECIMAL(15,2) DEFAULT 0,
                reference VARCHAR(100),
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (partner_id) REFERENCES partners(partner_id)
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_tables(conn)
                conn.execute(f"DELETE FROM {PARTNER_TABLE}")
                conn.execute(f"DELETE FROM {PARTNER_TX_TABLE}")
                conn.execute("DELETE FROM sqlite_sequence WHERE name IN (?, ?)",
                             (PARTNER_TABLE, PARTNER_TX_TABLE))
                for p in self._partners:
                    conn.execute(
                        f"INSERT INTO {PARTNER_TABLE} "
                        f"(partner_type, partner_name, phone, email, address, "
                        f"tax_id, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (p["type"], p["name"], p["phone"], p["email"],
                         p["address"], p["tax_id"], p["notes"]),
                    )
                for t in self._transactions:
                    conn.execute(
                        f"INSERT INTO {PARTNER_TX_TABLE} "
                        f"(partner_id, transaction_date, transaction_type, "
                        f"amount, reference, notes) VALUES (?, ?, ?, ?, ?, ?)",
                        (t["partner_id"], t["date"], t["type"], t["amount"],
                         t["reference"], t["notes"]),
                    )
            log.info("Saved %d partners to database", len(self._partners))
            return True
        except Exception as exc:
            log.error("partners save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(PARTNER_TABLE):
                    return False
                p_rows = conn.fetch_all(
                    f"SELECT partner_id, partner_type, partner_name, phone, "
                    f"email, address, tax_id, notes FROM {PARTNER_TABLE} "
                    f"ORDER BY partner_id"
                )
                t_rows = conn.fetch_all(
                    f"SELECT transaction_id, partner_id, transaction_date, "
                    f"transaction_type, amount, reference, notes "
                    f"FROM {PARTNER_TX_TABLE} ORDER BY transaction_id"
                )
        except Exception as exc:
            log.error("partners load_db error: %s", exc)
            return False
        self._partners = [self._row_to_partner(r) for r in p_rows]
        self._transactions = [self._row_to_tx(r) for r in t_rows]
        self._next_partner_id = max([p["id"] for p in self._partners] + [0]) + 1
        self._next_tx_id = max([t["id"] for t in self._transactions] + [0]) + 1
        return bool(self._partners)

    def clear_db(self):
        try:
            with get_connection() as conn:
                for tbl in (PARTNER_TABLE, PARTNER_TX_TABLE):
                    if conn.table_exists(tbl):
                        conn.execute(f"DELETE FROM {tbl}")
            return True
        except Exception as exc:
            log.error("partners clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_partner(row):
        return {
            "id": row[0], "type": row[1], "name": row[2], "phone": row[3] or "",
            "email": row[4] or "", "address": row[5] or "",
            "tax_id": row[6] or "", "notes": row[7] or "",
        }

    @staticmethod
    def _row_to_tx(row):
        return {
            "id": row[0], "partner_id": row[1], "date": row[2],
            "type": row[3], "amount": round(float(row[4] or 0), 2),
            "reference": row[5] or "", "notes": row[6] or "",
        }

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise PartnerError(f"Invalid date: {value!r}")
        raise PartnerError(f"Invalid date: {value!r}")

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise PartnerError(f"Invalid {field}: {value!r}")


partner_manager = PartnerManager()
