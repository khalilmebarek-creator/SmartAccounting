# محرك دفتر الأستاذ العام
# ========================
# سجل القيود المحاسبية + ميزان المراجعة + أرصدة الحسابات + ترحيلات شهرية

from datetime import date
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("ledger")

LEDGER_TABLE = "ledger_entries"


class LedgerError(Exception):
    """خطأ محاسبي في دفتر الأستاذ"""
    pass


class LedgerBook:
    """دفتر الأستاذ العام: قيود يومية + ميزان مراجعة + أرصدة حسابات.

    كل قيد: حساب واحد بمدين (debit) أو دائن (credit) — لا يمكن أن يكون الاثنان
    معاً أكبر من صفر في نفس القيد (القيود المزدوجة تُسجَّل كقيدين مترابطين
    بنفس المرجع reference).
    """

    def __init__(self):
        self._entries = []
        self._next_id = 1

    # ===== القيود =====

    def add_entry(self, entry_date, account_code, debit=0.0, credit=0.0,
                  description="", account_name=None, reference=None):
        """إضافة قيد محاسبي. Returns: entry_id أو يرفع LedgerError."""
        entry_date = self._parse_date(entry_date)
        account_code = self._clean_required(account_code, "account_code")
        debit = self._parse_amount(debit, "debit")
        credit = self._parse_amount(credit, "credit")
        if debit < 0 or credit < 0:
            raise LedgerError("Debit and credit must be non-negative")
        if debit > 0 and credit > 0:
            raise LedgerError("An entry cannot have both debit and credit")
        if debit == 0 and credit == 0:
            raise LedgerError("An entry must have a debit or a credit")
        entry = {
            "id": self._next_id,
            "date": entry_date.isoformat(),
            "account_code": account_code,
            "account_name": account_name or account_code,
            "description": description or "",
            "debit": round(debit, 2),
            "credit": round(credit, 2),
            "reference": reference,
        }
        self._entries.append(entry)
        self._next_id += 1
        log.debug("Added ledger entry %s (%s: %s)", entry["id"],
                  account_code, entry["reference"])
        return entry["id"]

    def delete_entry(self, entry_id):
        """حذف قيد. Returns: bool."""
        for i, e in enumerate(self._entries):
            if e["id"] == entry_id:
                del self._entries[i]
                return True
        return False

    def get_entries(self, account_code=None, date_from=None, date_to=None):
        """استرجاع القيود مع مرشحات اختيارية (تُرجع نسخاً مرتبة بالتاريخ)."""
        result = []
        for e in self._entries:
            if account_code and e["account_code"] != account_code:
                continue
            if date_from and e["date"] < self._parse_date(date_from).isoformat():
                continue
            if date_to and e["date"] > self._parse_date(date_to).isoformat():
                continue
            result.append(dict(e))
        result.sort(key=lambda x: (x["date"], x["id"]))
        return result

    def get_entry(self, entry_id):
        for e in self._entries:
            if e["id"] == entry_id:
                return dict(e)
        return None

    # ===== الأرصدة =====

    def account_balance(self, account_code):
        """صافي رصيد حساب: مجموع المدين - مجموع الدائن."""
        debit = sum(e["debit"] for e in self._entries
                    if e["account_code"] == account_code)
        credit = sum(e["credit"] for e in self._entries
                     if e["account_code"] == account_code)
        return round(debit - credit, 2)

    def account_ledger(self, account_code):
        """حركة حساب مع رصيد جارٍ بعد كل قيد."""
        rows = self.get_entries(account_code=account_code)
        running = 0.0
        for row in rows:
            running += row["debit"] - row["credit"]
            row["running_balance"] = round(running, 2)
        return rows

    def trial_balance(self):
        """ميزان المراجعة: مجموع المدين، مجموع الدائن، وحالة التوازن."""
        total_debit = round(sum(e["debit"] for e in self._entries), 2)
        total_credit = round(sum(e["credit"] for e in self._entries), 2)
        return {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balanced": total_debit == total_credit,
            "entry_count": len(self._entries),
        }

    def accounts_summary(self):
        """ملخص لكل حساب: مدين، دائن، رصيد."""
        summary = {}
        for e in self._entries:
            acc = summary.setdefault(e["account_code"], {
                "account_code": e["account_code"],
                "account_name": e["account_name"],
                "debit": 0.0,
                "credit": 0.0,
            })
            acc["debit"] = round(acc["debit"] + e["debit"], 2)
            acc["credit"] = round(acc["credit"] + e["credit"], 2)
        for acc in summary.values():
            acc["balance"] = round(acc["debit"] - acc["credit"], 2)
        return list(summary.values())

    def clear(self):
        """مسح الدفتر بالكامل."""
        self._entries = []
        self._next_id = 1

    def export_csv(self, filepath):
        """تصدير كل القيود إلى CSV. Returns: bool."""
        import csv
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "account_code", "account_name",
                                 "description", "debit", "credit", "reference"])
                for e in self.get_entries():
                    writer.writerow([
                        e["date"], e["account_code"], e["account_name"],
                        e["description"], e["debit"], e["credit"],
                        e.get("reference") or "",
                    ])
            return True
        except OSError as exc:
            log.error("export_csv error: %s", exc)
            return False

    # ===== قاعدة البيانات =====

    def _ensure_table(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {LEDGER_TABLE} (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE NOT NULL,
                account_code VARCHAR(50) NOT NULL,
                account_name VARCHAR(255),
                description TEXT,
                debit DECIMAL(15,2) DEFAULT 0,
                credit DECIMAL(15,2) DEFAULT 0,
                reference VARCHAR(100),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def save_db(self):
        """حفظ كل القيود في قاعدة SQLite (إعادة كتابة كاملة)."""
        try:
            with get_connection() as conn:
                self._ensure_table(conn)
                conn.execute(f"DELETE FROM {LEDGER_TABLE}")
                conn.execute(
                    "DELETE FROM sqlite_sequence WHERE name = ?",
                    (LEDGER_TABLE,),
                )
                for e in self._entries:
                    conn.execute(
                        f"INSERT INTO {LEDGER_TABLE} "
                        f"(entry_date, account_code, account_name, description, "
                        f"debit, credit, reference) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (e["date"], e["account_code"], e["account_name"],
                         e["description"], e["debit"], e["credit"],
                         e.get("reference")),
                    )
            log.info("Saved %d ledger entries to database", len(self._entries))
            return True
        except Exception as exc:
            log.error("ledger save_db error: %s", exc)
            return False

    def load_db(self):
        """تحميل القيود من قاعدة SQLite إلى الذاكرة (يستبدل الحالة)."""
        try:
            with get_connection() as conn:
                if not conn.table_exists(LEDGER_TABLE):
                    return False
                rows = conn.fetch_all(
                    f"SELECT entry_id, entry_date, account_code, account_name, "
                    f"description, debit, credit, reference "
                    f"FROM {LEDGER_TABLE} ORDER BY entry_id"
                )
        except Exception as exc:
            log.error("ledger load_db error: %s", exc)
            return False
        self._entries = [self._row_to_entry(r) for r in rows]
        self._next_id = max([e["id"] for e in self._entries] + [0]) + 1
        return bool(self._entries)

    def clear_db(self):
        try:
            with get_connection() as conn:
                if conn.table_exists(LEDGER_TABLE):
                    conn.execute(f"DELETE FROM {LEDGER_TABLE}")
            return True
        except Exception as exc:
            log.error("ledger clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_entry(row):
        return {
            "id": row[0],
            "date": row[1],
            "account_code": row[2],
            "account_name": row[3] or row[2],
            "description": row[4] or "",
            "debit": round(float(row[5] or 0), 2),
            "credit": round(float(row[6] or 0), 2),
            "reference": row[7],
        }

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise LedgerError(f"Invalid date: {value!r}")
        raise LedgerError(f"Invalid date: {value!r}")

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise LedgerError(f"Invalid {field}: {value!r}")

    @staticmethod
    def _clean_required(value, field):
        value = (value or "").strip()
        if not value:
            raise LedgerError(f"{field} is required")
        return value


ledger_book = LedgerBook()
