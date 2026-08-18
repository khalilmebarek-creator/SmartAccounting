# إطار المزامنة البنكية
# ======================
# محاكي بنكي + استيراد كشوفات + تسوية + دعم صيغ متعددة

import json
import csv
import hashlib
from datetime import date, datetime, timedelta
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("bank_api")

TRANSACTIONS_TABLE = "bank_transactions"


class BankAPIError(Exception):
    pass


class BankSimulator:
    """محاكي بنكي: يولد كشوفات افتراضية للاختبار دون اتصال حقيقي."""

    _templates = {
        "BNA": {"name": "البنك الوطني الجزائري", "prefix": "BNA"},
        "BEA": {"name": "بنك الجزائر الخارجي", "prefix": "BEA"},
        "CPA": {"name": "القرض الشعبي الجزائري", "prefix": "CPA"},
        "BDL": {"name": "بنك التنمية المحلية", "prefix": "BDL"},
        "BADR": {"name": "بنك الفلاحة والتنمية الريفية", "prefix": "BADR"},
        "ABC": {"name": "البنك العربي الجزائري", "prefix": "ABC"},
    }

    def __init__(self, bank_code="BNA", account_number=None):
        if bank_code not in self._templates:
            raise BankAPIError(f"unknown bank: {bank_code}")
        self.bank_code = bank_code
        self.bank_info = self._templates[bank_code]
        self.account = account_number or f"DZ{hashlib.sha256(str(date.today()).encode()).hexdigest()[:14].upper()}"

    def fetch_transactions(self, from_date=None, to_date=None, count=20):
        """محاكاة جلب كشف حساب. Returns: list of transaction dicts."""
        from_date = self._parse_date(from_date) or date.today() - timedelta(days=30)
        to_date = self._parse_date(to_date) or date.today()
        transactions = []
        base_ref = int(datetime.now().timestamp()) % 100000
        for i in range(count):
            day_offset = (i * 37 + 13) % (to_date - from_date).days
            t_date = from_date + timedelta(days=max(day_offset, 0))
            amount = round((-50000 + (i * 7300 + i * i * 47) % 120000) / 100, 2)
            t_type = "credit" if amount > 0 else "debit"
            desc_words = ["PAIEMENT", "VIREMENT", "CHEQUE", "PRELEVEMENT",
                          "CARTE", "ESPECES", "EFFET", "COMMISSION"]
            t = {
                "id": f"{self.bank_info['prefix']}-{base_ref+i:06d}",
                "date": t_date.isoformat(),
                "type": t_type,
                "amount": abs(amount),
                "description": f"{desc_words[i % len(desc_words)]} #{base_ref+i}",
                "reference": f"REF{base_ref+i:08d}",
                "balance": round(1000000 + sum(
                    t2["amount"] if t2["type"] == "credit" else -t2["amount"]
                    for t2 in transactions
                ) + (amount if t_type == "credit" else -amount), 2),
            }
            transactions.append(t)
        transactions.sort(key=lambda x: x["date"])
        return transactions

    def export_json(self, filepath, transactions=None):
        if transactions is None:
            transactions = self.fetch_transactions()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "bank": self.bank_info["name"],
                "code": self.bank_code,
                "account": self.account,
                "fetched": datetime.now().isoformat(),
                "transactions": transactions,
            }, f, ensure_ascii=False, indent=2)
        return True

    def export_csv(self, filepath, transactions=None):
        if transactions is None:
            transactions = self.fetch_transactions()
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["id", "date", "type", "amount", "description",
                         "reference", "balance"])
            for t in transactions:
                w.writerow([t["id"], t["date"], t["type"], t["amount"],
                            t["description"], t["reference"], t["balance"]])
        return True

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
        return None


class BankReconciler:
    """تسوية الكشوفات البنكية مع سجلات التطبيق."""

    def __init__(self):
        self._transactions = []
        self._matched = set()

    def load_bank_statement(self, transactions):
        """تحميل كشف بنكي (قائمة معاملات)."""
        self._transactions = transactions
        return len(transactions)

    def reconcile(self, book_entries, tolerance=0.01, days_tolerance=3):
        """مقارنة المعاملات البنكية مع السجلات المحاسبية.
        
        Returns: dict {matched, unmatched_bank, unmatched_book, discrepancies}
        """
        matched = []
        unmatched_bank = list(range(len(self._transactions)))
        unmatched_book = []
        discrepancies = []
        book_used = set()

        for bi, bt in enumerate(self._transactions):
            bt_date = bt.get("date", "")
            bt_amount = abs(float(bt.get("amount", 0)))
            for bj, be in enumerate(book_entries):
                if bj in book_used:
                    continue
                be_amount = abs(float(be.get("amount", 0)))
                be_date = be.get("date", "")
                if abs(bt_amount - be_amount) <= tolerance:
                    try:
                        btd = date.fromisoformat(bt_date)
                        bed = date.fromisoformat(be_date)
                        if abs((btd - bed).days) <= days_tolerance:
                            matched.append({"bank": bt, "book": be})
                            book_used.add(bj)
                            if bi in unmatched_bank:
                                unmatched_bank.remove(bi)
                            break
                    except (ValueError, TypeError):
                        pass
            else:
                if bi not in [m["bank"] for m in matched if m["bank"] == bt]:
                    pass

        for bj, be in enumerate(book_entries):
            if bj not in book_used:
                unmatched_book.append(be)

        unmatched_bank_tx = [self._transactions[i] for i in unmatched_bank]
        if unmatched_bank_tx or unmatched_book:
            discrepancies.append({
                "unmatched_bank": len(unmatched_bank_tx),
                "unmatched_book": len(unmatched_book),
            })

        return {
            "matched": len(matched),
            "total_bank": len(self._transactions),
            "total_book": len(book_entries),
            "matched_pairs": matched,
            "unmatched_bank": unmatched_bank_tx,
            "unmatched_book": unmatched_book,
            "discrepancies": discrepancies,
        }

    def _ensure_tables(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TRANSACTIONS_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_ref VARCHAR(100),
                tx_date DATE NOT NULL,
                tx_type VARCHAR(20),
                amount DECIMAL(15,2),
                description TEXT,
                reference VARCHAR(100),
                balance DECIMAL(15,2),
                matched BOOLEAN DEFAULT 0,
                book_ref VARCHAR(100),
                imported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_tables(conn)
                conn.execute(f"DELETE FROM {TRANSACTIONS_TABLE}")
                for t in self._transactions:
                    conn.execute(
                        f"INSERT INTO {TRANSACTIONS_TABLE} (bank_ref, tx_date, "
                        f"tx_type, amount, description, reference, balance, "
                        f"matched) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (t["id"], t["date"], t["type"], t["amount"],
                         t["description"], t["reference"], t["balance"], 0),
                    )
            return True
        except Exception as exc:
            log.error("bank_reconciler save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(TRANSACTIONS_TABLE):
                    return False
                rows = conn.fetch_all(
                    f"SELECT bank_ref, tx_date, tx_type, amount, description, "
                    f"reference, balance FROM {TRANSACTIONS_TABLE}"
                )
                self._transactions = [
                    {"id": r[0], "date": r[1], "type": r[2],
                     "amount": float(r[3] or 0), "description": r[4] or "",
                     "reference": r[5] or "", "balance": float(r[6] or 0)}
                    for r in rows
                ]
            return bool(self._transactions)
        except Exception as exc:
            log.error("bank_reconciler load_db error: %s", exc)
            return False


bank_simulator = BankSimulator()
bank_reconciler = BankReconciler()
