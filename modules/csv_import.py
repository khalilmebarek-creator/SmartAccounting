# استيراد البيانات من CSV/Excel - استيراد مجمّع مع تعيين الأعمدة
# ==============================================================

import os
import csv
from typing import Dict, List, Optional, Tuple, Callable
from utils.app_logger import get_logger

logger = get_logger("csv_import")

ACCOUNTING_COLUMN_MAP = {
    "ar": {
        "date": ["التاريخ", "تاريخ", "datum"],
        "description": ["الوصف", "وصف", " البيان", "details", "description"],
        "debit": ["مدين", "مدين/عليه", "debit"],
        "credit": ["دائن", "دائن/لصالحه", "credit"],
        "amount": ["المبلغ", "مبلغ", "amount", "montant"],
        "account": ["الحساب", "رقم الحساب", "account", "compte"],
        "balance": ["الرصيد", "balance", "solde"],
        "category": ["الفئة", "نوع", "category", "type"],
        "revenue": ["الإيرادات", "إيرادات", "revenue", "chiffre_affaires"],
        "cogs": ["تكلفة المبيعات", "cost_of_goods_sold", "charges"],
        "expenses": ["المصاريف", "المصروفات", "expenses", "depenses"],
        "tax": ["الضريبة", "الضرائب", "tax", "impot"],
    },
    "en": {
        "date": ["date", "datum"],
        "description": ["description", "details", "memo", "narrative"],
        "debit": ["debit", "dr"],
        "credit": ["credit", "cr"],
        "amount": ["amount", "montant", "value"],
        "account": ["account", "account_number", "compte"],
        "balance": ["balance", "solde"],
        "category": ["category", "type"],
        "revenue": ["revenue", "income", "sales", "chiffre_affaires"],
        "cogs": ["cost_of_goods_sold", "cogs", "cost", "charges"],
        "expenses": ["expenses", "operating_expenses", "depenses"],
        "tax": ["tax", "taxes", "impot"],
    },
    "fr": {
        "date": ["date", "datum"],
        "description": ["description", "détails", "libellé", "intitulé"],
        "debit": ["débit", "debit"],
        "credit": ["crédit", "credit"],
        "amount": ["montant", "amount", "valeur"],
        "account": ["compte", "numéro_compte", "account"],
        "balance": ["solde", "balance"],
        "category": ["catégorie", "type"],
        "revenue": ["chiffre_affaires", "revenus", "recettes"],
        "cogs": ["charges", "coût_des_ventes"],
        "expenses": ["dépenses", "frais"],
        "tax": ["impôt", "taxes"],
    }
}


class CSVImporter:
    """مستورد CSV/Excel متقدم مع تعيين تلقائي للأعمدة"""

    def __init__(self):
        self.detected_columns: Dict[str, int] = {}
        self.data_rows: List[Dict] = []
        self.errors: List[str] = []
        self.stats = {"total": 0, "imported": 0, "skipped": 0, "errors": 0}

    def detect_delimiter(self, filepath: str) -> str:
        """اكتشاف فاصل CSV تلقائياً"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                sample = f.read(4096)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            return dialect.delimiter
        except Exception:
            return ","

    def detect_file_type(self, filepath: str) -> str:
        """اكتشاف نوع الملف"""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".csv":
            return "csv"
        elif ext in (".xlsx", ".xls"):
            return "excel"
        elif ext == ".tsv":
            return "tsv"
        return "unknown"

    def auto_map_columns(self, headers: List[str], lang: str = "ar") -> Dict[str, int]:
        """تعيين تلقائي للأعمدة"""
        mapping = {}
        column_defs = ACCOUNTING_COLUMN_MAP.get(lang, ACCOUNTING_COLUMN_MAP["en"])

        for field_name, aliases in column_defs.items():
            for alias in aliases:
                for i, header in enumerate(headers):
                    h_lower = header.strip().lower()
                    a_lower = alias.strip().lower()
                    if h_lower == a_lower or a_lower in h_lower or h_lower in a_lower:
                        mapping[field_name] = i
                        break
                if field_name in mapping:
                    break

        self.detected_columns = mapping
        return mapping

    def read_csv(self, filepath: str, encoding: str = "utf-8",
                 delimiter: str = None, has_header: bool = True) -> Tuple[List[str], List[List]]:
        """قراءة ملف CSV"""
        if delimiter is None:
            delimiter = self.detect_delimiter(filepath)

        rows = []
        headers = []

        try:
            with open(filepath, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f, delimiter=delimiter)
                if has_header:
                    headers = next(reader, [])
                for row in reader:
                    if row and any(cell.strip() for cell in row):
                        rows.append(row)

            self.stats["total"] = len(rows)
            return headers, rows
        except UnicodeDecodeError:
            with open(filepath, "r", encoding="latin-1", newline="") as f:
                reader = csv.reader(f, delimiter=delimiter)
                if has_header:
                    headers = next(reader, [])
                for row in reader:
                    if row and any(cell.strip() for cell in row):
                        rows.append(row)
            self.stats["total"] = len(rows)
            return headers, rows
        except Exception as e:
            self.errors.append(f"Error reading CSV: {e}")
            return [], []

    def read_excel(self, filepath: str, sheet_name=0) -> Tuple[List[str], List[List]]:
        """قراءة ملف Excel"""
        try:
            import pandas as pd
            df = pd.read_excel(filepath, sheet_name=sheet_name, dtype=str)
            df = df.fillna("")
            headers = list(df.columns)
            rows = df.values.tolist()
            self.stats["total"] = len(rows)
            return headers, rows
        except ImportError:
            self.errors.append("pandas/openpyxl not installed")
            return [], []
        except Exception as e:
            self.errors.append(f"Error reading Excel: {e}")
            return [], []

    def import_data(self, filepath: str, lang: str = "ar",
                    encoding: str = "utf-8",
                    on_row: Callable = None) -> Dict:
        """استيراد بيانات من ملف"""
        self.data_rows = []
        self.errors = []
        self.stats = {"total": 0, "imported": 0, "skipped": 0, "errors": 0}

        file_type = self.detect_file_type(filepath)
        if file_type == "csv" or file_type == "tsv":
            headers, rows = self.read_csv(filepath, encoding=encoding)
        elif file_type == "excel":
            headers, rows = self.read_excel(filepath)
        else:
            self.errors.append(f"Unsupported file type: {file_type}")
            return self._build_result()

        if not headers or not rows:
            self.errors.append("No data found in file")
            return self._build_result()

        mapping = self.auto_map_columns(headers, lang)

        for i, row in enumerate(rows):
            try:
                record = {}
                for field_name, col_idx in mapping.items():
                    if col_idx < len(row):
                        value = row[col_idx].strip() if isinstance(row[col_idx], str) else row[col_idx]
                        if field_name in ("debit", "credit", "amount", "balance", "revenue", "cogs", "expenses", "tax"):
                            try:
                                value = float(str(value).replace(",", "").replace(" ", "")) if value else 0.0
                            except (ValueError, TypeError):
                                value = 0.0
                        record[field_name] = value

                if not record.get("description") and not record.get("amount"):
                    self.stats["skipped"] += 1
                    continue

                self.data_rows.append(record)
                self.stats["imported"] += 1

                if on_row:
                    on_row(i, record)

            except Exception as e:
                self.errors.append(f"Row {i+1}: {e}")
                self.stats["errors"] += 1

        logger.info(f"Import completed: {self.stats}")
        return self._build_result()

    def _build_result(self) -> Dict:
        return {
            "data": self.data_rows,
            "column_mapping": self.detected_columns,
            "stats": self.stats.copy(),
            "errors": self.errors.copy(),
        }

    def get_preview(self, rows: List[List], headers: List[str], max_rows: int = 5) -> List[Dict]:
        """معاينة أول صفوف"""
        preview = []
        for row in rows[:max_rows]:
            record = {}
            for i, h in enumerate(headers):
                if i < len(row):
                    record[h] = row[i]
            preview.append(record)
        return preview


csv_importer = CSVImporter()
