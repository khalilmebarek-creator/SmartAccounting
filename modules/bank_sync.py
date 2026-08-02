# تكامل البنوك - استيراد كشف الحساب البنكي
# ============================================

import csv
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from utils.app_logger import get_logger

logger = get_logger("bank_sync")

ALGERIAN_BANKS = {
    "BNA": {
        "name_ar": "البنك الوطني الجزائري",
        "name_en": "Banque Nationale d'Algérie",
        "csv_delimiter": ";",
        "date_format": "%d/%m/%Y",
        "encoding": "latin-1",
        "columns": {"date": 0, "description": 2, "debit": 3, "credit": 4, "balance": 5},
    },
    "CPA": {
        "name_ar": "البنك الخارجي الجزائري",
        "name_en": "Crédit Populaire d'Algérie",
        "csv_delimiter": ";",
        "date_format": "%d/%m/%Y",
        "encoding": "utf-8",
        "columns": {"date": 0, "description": 1, "debit": 2, "credit": 3, "balance": 4},
    },
    "BADR": {
        "name_ar": "البنك الجزائري للتنمية الريفية",
        "name_en": "Banque Algérienne de Développement Rural",
        "csv_delimiter": ",",
        "date_format": "%d/%m/%Y",
        "encoding": "utf-8",
        "columns": {"date": 0, "description": 1, "debit": 2, "credit": 3, "balance": 4},
    },
    "BEA": {
        "name_ar": "البنك嶦عالي",
        "name_en": "Banque Externe d'Algérie",
        "csv_delimiter": ";",
        "date_format": "%d-%m-%Y",
        "encoding": "latin-1",
        "columns": {"date": 0, "description": 1, "debit": 2, "credit": 3, "balance": 4},
    },
    "BDL": {
        "name_ar": "بنك الجزائر",
        "name_en": "Banque d'Algérie",
        "csv_delimiter": ",",
        "date_format": "%Y-%m-%d",
        "encoding": "utf-8",
        "columns": {"date": 0, "description": 1, "debit": 2, "credit": 3, "balance": 4},
    },
    "CCP": {
        "name_ar": "الصندوق الوطني للبريد",
        "name_en": "Algérie Poste - CCP",
        "csv_delimiter": ";",
        "date_format": "%d/%m/%Y",
        "encoding": "latin-1",
        "columns": {"date": 0, "description": 2, "debit": 3, "credit": 4, "balance": 5},
    },
}


class BankSyncManager:
    """مدير تكامل البنوك واستيراد كشف الحساب"""

    def __init__(self):
        self.supported_banks = ALGERIAN_BANKS
        self.last_import = None

    def get_bank_list(self) -> List[Dict]:
        """قائمة البنوك المدعومة"""
        result = []
        for code, info in self.supported_banks.items():
            result.append({
                "code": code,
                "name_ar": info["name_ar"],
                "name_en": info["name_en"],
            })
        return result

    def detect_bank(self, filepath: str) -> Optional[str]:
        """اكتشاف البنك من محتوى الملف"""
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(2048).upper()
        except Exception:
            return None

        for code, info in self.supported_banks.items():
            if code.upper() in content or info["name_en"].upper() in content:
                return code

        if "BNA" in content or "NATIONALE" in content:
            return "BNA"
        if "CPA" in content or "POPULAIRE" in content:
            return "CPA"

        return None

    def import_bank_statement(self, filepath: str, bank_code: str = None,
                               account_id: str = "") -> Dict:
        """استيراد كشف حساب بنكي"""
        if bank_code is None:
            bank_code = self.detect_bank(filepath)

        if bank_code and bank_code in self.supported_banks:
            return self._import_with_bank_format(filepath, bank_code, account_id)

        return self._import_generic(filepath, account_id)

    def _import_with_bank_format(self, filepath: str, bank_code: str,
                                  account_id: str) -> Dict:
        """استيراد بتنسيق بنك محدد"""
        bank = self.supported_banks[bank_code]
        delimiter = bank.get("csv_delimiter", ",")
        encoding = bank.get("encoding", "utf-8")
        date_format = bank.get("date_format", "%d/%m/%Y")
        col_map = bank.get("columns", {})

        transactions = []
        errors = []

        try:
            with open(filepath, "r", encoding=encoding, errors="replace") as f:
                rows = list(csv.reader(f, delimiter=delimiter))

                start = 0
                for i, row in enumerate(rows):
                    if not row or not any(cell.strip() for cell in row):
                        continue
                    if not any(c.isdigit() for c in "".join(row)):
                        start = i + 1
                    break

                if start >= len(rows):
                    return {"transactions": [], "errors": ["No data found"]}

                for row in rows[start:]:
                    if not row or not any(cell.strip() for cell in row):
                        continue

                    try:
                        tx = self._parse_transaction(row, col_map, date_format)
                        if tx:
                            tx["bank"] = bank_code
                            tx["account_id"] = account_id
                            transactions.append(tx)
                    except Exception as e:
                        errors.append(f"Row parsing error: {e}")

            self.last_import = datetime.now().isoformat()
            logger.info(f"Imported {len(transactions)} transactions from {bank_code}")

            return {
                "bank": bank_code,
                "bank_name": bank["name_en"],
                "account_id": account_id,
                "transactions": transactions,
                "total_debit": sum(t.get("debit", 0) for t in transactions),
                "total_credit": sum(t.get("credit", 0) for t in transactions),
                "count": len(transactions),
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Bank import error: {e}")
            return {"transactions": [], "errors": [str(e)]}

    def _parse_transaction(self, row: List, col_map: Dict, date_format: str) -> Optional[Dict]:
        """تحليل صف معاملة"""
        date_idx = col_map.get("date", 0)
        desc_idx = col_map.get("description", 1)
        debit_idx = col_map.get("debit", 2)
        credit_idx = col_map.get("credit", 3)
        balance_idx = col_map.get("balance", 4)

        date_str = row[date_idx].strip() if date_idx < len(row) else ""
        description = row[desc_idx].strip() if desc_idx < len(row) else ""

        if not description:
            return None

        parsed_date = self._parse_date(date_str, date_format)

        debit = self._parse_amount(row[debit_idx] if debit_idx < len(row) else "0")
        credit = self._parse_amount(row[credit_idx] if credit_idx < len(row) else "0")
        balance = self._parse_amount(row[balance_idx] if balance_idx < len(row) else "0")

        return {
            "date": parsed_date,
            "date_raw": date_str,
            "description": description,
            "debit": debit,
            "credit": credit,
            "balance": balance,
            "amount": credit - debit if credit > 0 else -debit,
        }

    def _parse_date(self, date_str: str, date_format: str) -> str:
        """تحليل التاريخ"""
        date_str = date_str.strip()
        formats = [date_format, "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y",
                   "%m/%d/%Y", "%d %b %Y", "%d %B %Y"]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str

    def _parse_amount(self, value: str) -> float:
        """تحليل المبلغ"""
        if not value:
            return 0.0
        cleaned = value.strip().replace(" ", "")
        dot_pos = cleaned.find(".")
        comma_pos = cleaned.find(",")
        if dot_pos >= 0 and comma_pos >= 0:
            if comma_pos < dot_pos:
                cleaned = cleaned.replace(",", "")
            else:
                cleaned = cleaned.replace(".", "").replace(",", ".")
        elif comma_pos >= 0:
            after_comma = cleaned[comma_pos + 1:]
            if len(after_comma) <= 2:
                cleaned = cleaned.replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        cleaned = re.sub(r"[^\d.\-]", "", cleaned)
        try:
            return abs(float(cleaned))
        except (ValueError, TypeError):
            return 0.0

    def _import_generic(self, filepath: str, account_id: str) -> Dict:
        """استيراد عام لأي CSV"""
        transactions = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                headers = next(reader, [])

                date_col = self._find_column(headers, ["date", "التاريخ", "datum", "_date"])
                desc_col = self._find_column(headers, ["description", "الوصف", "details", "memo", "libellé"])
                debit_col = self._find_column(headers, ["debit", "مدين", "débit"])
                credit_col = self._find_column(headers, ["credit", "دائن", "crédit"])
                amount_col = self._find_column(headers, ["amount", "المبلغ", "montant", "balance"])

                for row in reader:
                    if not row:
                        continue
                    try:
                        desc = row[desc_col].strip() if desc_col is not None and desc_col < len(row) else ""
                        if not desc:
                            continue

                        tx = {
                            "date": self._parse_date(row[date_col] if date_col is not None and date_col < len(row) else "", "%d/%m/%Y"),
                            "description": desc,
                            "debit": self._parse_amount(row[debit_col] if debit_col is not None and debit_col < len(row) else "0"),
                            "credit": self._parse_amount(row[credit_col] if credit_col is not None and credit_col < len(row) else "0"),
                            "balance": self._parse_amount(row[amount_col] if amount_col is not None and amount_col < len(row) else "0"),
                            "bank": "Unknown",
                            "account_id": account_id,
                        }
                        tx["amount"] = tx["credit"] - tx["debit"] if tx["credit"] > 0 else -tx["debit"]
                        transactions.append(tx)
                    except Exception:
                        pass

            return {
                "bank": "Generic",
                "account_id": account_id,
                "transactions": transactions,
                "total_debit": sum(t["debit"] for t in transactions),
                "total_credit": sum(t["credit"] for t in transactions),
                "count": len(transactions),
                "errors": [],
            }
        except Exception as e:
            return {"transactions": [], "errors": [str(e)]}

    def _find_column(self, headers: List[str], candidates: List[str]) -> Optional[int]:
        """إيجاد عمود من القائمة"""
        for candidate in candidates:
            for i, h in enumerate(headers):
                if h.strip().lower() == candidate.lower():
                    return i
        return None

    def reconcile(self, bank_transactions: List[Dict],
                  book_transactions: List[Dict],
                  tolerance: float = 0.01) -> Dict:
        """المطابقة بين الحسابات البنكية والسجلات"""
        matched = []
        unmatched_bank = list(bank_transactions)
        unmatched_book = list(book_transactions)

        for bt in bank_transactions[:]:
            for bk in book_transactions[:]:
                date_match = bt.get("date") == bk.get("date")
                amount_match = abs(bt.get("amount", 0) - bk.get("amount", 0)) <= tolerance

                if date_match and amount_match:
                    matched.append({"bank": bt, "book": bk})
                    if bt in unmatched_bank:
                        unmatched_bank.remove(bt)
                    if bk in unmatched_book:
                        unmatched_book.remove(bk)
                    break

        return {
            "matched_count": len(matched),
            "unmatched_bank_count": len(unmatched_bank),
            "unmatched_book_count": len(unmatched_book),
            "matched": matched,
            "unmatched_bank": unmatched_bank,
            "unmatched_book": unmatched_book,
            "match_rate": len(matched) / max(len(bank_transactions), 1) * 100,
        }


bank_sync = BankSyncManager()
