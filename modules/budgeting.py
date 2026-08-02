# محرك الميزانية والتخطيط
# ========================
# خطط سنوية لكل بند + مقارنة فعلي/مخطط + انحرافات ونسب تنفيذ

from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("budgeting")

BUDGET_TABLE = "budget_items"

BUDGET_CATEGORIES = ("revenue", "expense", "investment")


class BudgetError(Exception):
    """خطأ في بيانات الميزانية"""
    pass


class BudgetManager:
    """إدارة الميزانية: بنود سنوية + مقارنة مع الفعلي + تقارير الانحراف."""

    def __init__(self):
        self._items = []
        self._next_id = 1

    # ===== البنود =====

    def set_budget_item(self, year, item_name, amount, category="expense"):
        """تعيين/تحديث بند ميزانية لسنة (باسم فريد). Returns: budget_id."""
        year = self._parse_year(year)
        item_name = (item_name or "").strip()
        if not item_name:
            raise BudgetError("item name is required")
        amount = self._parse_amount(amount, "amount")
        if amount < 0:
            raise BudgetError("amount must be non-negative")
        category = (category or "").strip().lower()
        if category not in BUDGET_CATEGORIES:
            raise BudgetError(f"category must be one of {BUDGET_CATEGORIES}")
        existing = self._find(year, item_name)
        if existing:
            existing["amount"] = amount
            existing["category"] = category
            return existing["id"]
        item = {
            "id": self._next_id,
            "year": year,
            "item_name": item_name,
            "amount": amount,
            "category": category,
        }
        self._next_id += 1
        self._items.append(item)
        log.debug("Set budget %s for %d: %s", item_name, year, amount)
        return item["id"]

    def update_budget_item(self, budget_id, **fields):
        """تحديث بند. Returns: bool."""
        item = next((i for i in self._items if i["id"] == budget_id), None)
        if not item:
            return False
        for key, value in fields.items():
            if key not in ("year", "item_name", "amount", "category"):
                continue
            if key == "year":
                value = self._parse_year(value)
            elif key == "item_name":
                value = (value or "").strip()
                if not value:
                    raise BudgetError("item name is required")
            elif key == "amount":
                value = self._parse_amount(value, key)
                if value < 0:
                    raise BudgetError("amount must be non-negative")
            elif key == "category":
                value = (value or "").strip().lower()
                if value not in BUDGET_CATEGORIES:
                    raise BudgetError(
                        f"category must be one of {BUDGET_CATEGORIES}")
            item[key] = value
        return True

    def delete_budget_item(self, budget_id):
        """حذف بند. Returns: bool."""
        for i, item in enumerate(self._items):
            if item["id"] == budget_id:
                del self._items[i]
                return True
        return False

    def get_budget_item(self, budget_id):
        for item in self._items:
            if item["id"] == budget_id:
                return dict(item)
        return None

    def get_budget(self, year):
        """بنود سنة محددة مرتبة حسب الفئة ثم الاسم."""
        items = [dict(i) for i in self._items if i["year"] == year]
        items.sort(key=lambda x: (x["category"], x["item_name"].lower()))
        return items

    def _find(self, year, item_name):
        for item in self._items:
            if item["year"] == year and \
                    item["item_name"].lower() == item_name.lower():
                return item
        return None

    # ===== التقارير =====

    def totals(self, year, category=None):
        """إجمالي المخطط لسنة (اختيارياً حسب الفئة)."""
        total = 0.0
        count = 0
        for item in self._items:
            if item["year"] != year:
                continue
            if category and item["category"] != category:
                continue
            total += item["amount"]
            count += 1
        return {"count": count, "total": round(total, 2)}

    def compare_to_actuals(self, year, actuals):
        """مقارنة المخطط بالفعلي.

        actuals: dict {item_name: قيمة فعلية}. المفاتيح تطابق أسماء البنود.

        Returns: قائمة {item_name, category, planned, actual, variance,
                        variance_pct, execution_pct}
        """
        result = []
        items = {i["item_name"]: i for i in self.get_budget(year)}
        names = set(items.keys()) | set((actuals or {}).keys())
        for name in sorted(names):
            item = items.get(name)
            planned = item["amount"] if item else 0.0
            actual = float((actuals or {}).get(name, 0) or 0)
            variance = round(actual - planned, 2)
            variance_pct = round(
                (variance / planned * 100), 2) if planned else 0.0
            execution_pct = round(
                (actual / planned * 100), 2) if planned else 0.0
            result.append({
                "item_name": name,
                "category": item["category"] if item else "expense",
                "planned": planned,
                "actual": actual,
                "variance": variance,
                "variance_pct": variance_pct,
                "execution_pct": execution_pct,
            })
        return result

    def variance_summary(self, year, actuals):
        """ملخص الانحراف: عدد البنود، التباين الكلي، نسبة التنفيذ."""
        rows = self.compare_to_actuals(year, actuals)
        planned = round(sum(r["planned"] for r in rows), 2)
        actual = round(sum(r["actual"] for r in rows), 2)
        return {
            "item_count": len(rows),
            "planned_total": planned,
            "actual_total": actual,
            "variance_total": round(actual - planned, 2),
            "execution_pct": round((actual / planned * 100), 2) if planned else 0.0,
        }

    def over_budget_items(self, year, actuals):
        """البنود التي تجاوزت المخطط (الإنفاق > المخطط)."""
        result = []
        for row in self.compare_to_actuals(year, actuals):
            if row["planned"] > 0 and row["variance"] > 0:
                result.append(row)
        result.sort(key=lambda x: x["variance"], reverse=True)
        return result

    def export_csv(self, filepath, year):
        """تصدير بنود سنة إلى CSV. Returns: bool."""
        import csv
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["year", "category", "item_name", "amount"])
                for item in self.get_budget(year):
                    writer.writerow([item["year"], item["category"],
                                     item["item_name"], item["amount"]])
            return True
        except OSError as exc:
            log.error("budget export_csv error: %s", exc)
            return False

    def clear(self):
        self._items = []
        self._next_id = 1

    # ===== قاعدة البيانات =====

    def _ensure_table(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {BUDGET_TABLE} (
                budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_year INTEGER NOT NULL,
                category VARCHAR(50) DEFAULT 'expense',
                item_name VARCHAR(255) NOT NULL,
                planned_amount DECIMAL(15,2) DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(budget_year, item_name)
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_table(conn)
                conn.execute(f"DELETE FROM {BUDGET_TABLE}")
                conn.execute(
                    "DELETE FROM sqlite_sequence WHERE name = ?",
                    (BUDGET_TABLE,),
                )
                for item in self._items:
                    conn.execute(
                        f"INSERT INTO {BUDGET_TABLE} (budget_year, category, "
                        f"item_name, planned_amount) VALUES (?, ?, ?, ?)",
                        (item["year"], item["category"], item["item_name"],
                         item["amount"]),
                    )
            log.info("Saved %d budget items to database", len(self._items))
            return True
        except Exception as exc:
            log.error("budget save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(BUDGET_TABLE):
                    return False
                rows = conn.fetch_all(
                    f"SELECT budget_id, budget_year, category, item_name, "
                    f"planned_amount FROM {BUDGET_TABLE} ORDER BY budget_id"
                )
        except Exception as exc:
            log.error("budget load_db error: %s", exc)
            return False
        self._items = [self._row_to_item(r) for r in rows]
        self._next_id = max([i["id"] for i in self._items] + [0]) + 1
        return bool(self._items)

    def clear_db(self):
        try:
            with get_connection() as conn:
                if conn.table_exists(BUDGET_TABLE):
                    conn.execute(f"DELETE FROM {BUDGET_TABLE}")
            return True
        except Exception as exc:
            log.error("budget clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_item(r):
        return {
            "id": r[0], "year": r[1], "category": r[2] or "expense",
            "item_name": r[3], "amount": round(float(r[4] or 0), 2),
        }

    @staticmethod
    def _parse_year(value):
        try:
            year = int(value)
        except (TypeError, ValueError):
            raise BudgetError(f"Invalid year: {value!r}")
        if year < 1900 or year > 2200:
            raise BudgetError("invalid year")
        return year

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise BudgetError(f"Invalid {field}: {value!r}")


budget_manager = BudgetManager()
