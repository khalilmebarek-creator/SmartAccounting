# محرك الرواتب الجزائرية
# =======================
# أجر الموظفين وفق القانون الجزائري:
#   CNAS الموظف 9% + التأمين على البطالة 1.5% + IRG التصاعدي الشهري + CNAS رب العمل 26%

from datetime import date
from database.db_connection import get_connection
from utils.app_logger import get_logger

log = get_logger("payroll")

EMPLOYEE_TABLE = "employees"
PAYROLL_TABLE = "payroll_runs"

CNAS_EMPLOYEE_RATE = 0.09
UNEMPLOYMENT_RATE = 0.015
CNAS_EMPLOYER_RATE = 0.26

# شرائح IRG الشهرية (نسبة، خصم) — وفق الجدول التصاعدي الجزائري
IRG_BRACKETS = [
    (15000.0, 0.00, 0.0),
    (30000.0, 0.20, 3000.0),
    (120000.0, 0.30, 6000.0),
    (270000.0, 0.35, 12000.0),
    (float("inf"), 0.375, 18750.0),
]


class PayrollError(Exception):
    """خطأ في بيانات الرواتب"""
    pass


def compute_irg(taxable_salary):
    """حساب IRG التصاعدي الشهري على الراتب الخاضع. Returns: float."""
    taxable_salary = float(taxable_salary or 0)
    if taxable_salary <= 0:
        return 0.0
    for limit, rate, deduction in IRG_BRACKETS:
        if taxable_salary <= limit:
            return round(max(taxable_salary * rate - deduction, 0.0), 2)


def compute_salary(base_salary):
    """احتساب تفاصيل الراتب: خصومات CNAS/بطالة + IRG + صافي. Returns: dict."""
    base_salary = float(base_salary or 0)
    if base_salary < 0:
        raise PayrollError("base_salary must be non-negative")
    cnas_employee = round(base_salary * CNAS_EMPLOYEE_RATE, 2)
    unemployment_insurance = round(base_salary * UNEMPLOYMENT_RATE, 2)
    taxable_salary = round(base_salary - cnas_employee - unemployment_insurance, 2)
    irg = compute_irg(taxable_salary)
    net_salary = round(taxable_salary - irg, 2)
    employer_cnas = round(base_salary * CNAS_EMPLOYER_RATE, 2)
    return {
        "base_salary": base_salary,
        "cnas_employee": cnas_employee,
        "unemployment_insurance": unemployment_insurance,
        "taxable_salary": taxable_salary,
        "irg": irg,
        "net_salary": net_salary,
        "employer_cnas": employer_cnas,
    }


class PayrollEngine:
    """إدارة الموظفين وتشغيل كشوف الرواتب الشهرية."""

    def __init__(self):
        self._employees = {}
        self._runs = {}
        self._next_employee_id = 1

    # ===== الموظفون =====

    def add_employee(self, name, position="", department="", base_salary=0.0,
                     hire_date=None, status="active", notes=""):
        """إضافة موظف. Returns: employee_id."""
        name = (name or "").strip()
        if not name:
            raise PayrollError("employee name is required")
        base_salary = self._parse_amount(base_salary, "base_salary")
        if base_salary < 0:
            raise PayrollError("base_salary must be non-negative")
        status = (status or "").strip().lower() or "active"
        if status not in ("active", "inactive"):
            raise PayrollError("status must be 'active' or 'inactive'")
        employee = {
            "id": self._next_employee_id,
            "name": name,
            "position": position or "",
            "department": department or "",
            "base_salary": base_salary,
            "hire_date": self._parse_date(hire_date).isoformat() if hire_date else None,
            "status": status,
            "notes": notes or "",
        }
        self._next_employee_id += 1
        self._employees[employee["id"]] = employee
        self._runs[employee["id"]] = {}
        log.debug("Added employee %s: %s", employee["id"], name)
        return employee["id"]

    def update_employee(self, employee_id, **fields):
        """تحديث بيانات موظف. Returns: bool."""
        emp = self._employees.get(employee_id)
        if not emp:
            return False
        allowed = ("name", "position", "department", "base_salary",
                   "hire_date", "status", "notes")
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "name":
                value = (value or "").strip()
                if not value:
                    raise PayrollError("employee name is required")
            elif key == "base_salary":
                value = self._parse_amount(value, key)
                if value < 0:
                    raise PayrollError("base_salary must be non-negative")
            elif key == "status":
                value = (value or "").strip().lower()
                if value not in ("active", "inactive"):
                    raise PayrollError("status must be 'active' or 'inactive'")
            elif key == "hire_date":
                value = self._parse_date(value).isoformat() if value else None
            emp[key] = value
        return True

    def delete_employee(self, employee_id):
        """حذف موظف وكشوفه. Returns: bool."""
        if employee_id not in self._employees:
            return False
        del self._employees[employee_id]
        self._runs.pop(employee_id, None)
        return True

    def get_employee(self, employee_id):
        emp = self._employees.get(employee_id)
        return dict(emp) if emp else None

    def list_employees(self, status=None):
        result = []
        for emp in self._employees.values():
            if status and emp["status"] != status:
                continue
            result.append(dict(emp))
        result.sort(key=lambda x: x["name"].lower())
        return result

    # ===== كشف الراتب =====

    def run_payroll(self, month, year):
        """تشغيل كشف رواتب لشهر/سنة لكل الموظفين النشطين.
        Returns: قائمة كشوف {employee_id, ..., net_salary}."""
        month, year = self._validate_period(month, year)
        results = []
        for emp in self.list_employees(status="active"):
            run = self.compute_payslip(emp["id"], month, year)
            self._runs[emp["id"]][(month, year)] = run
            results.append(run)
        log.info("Payroll run for %d/%d: %d employees",
                 month, year, len(results))
        return results

    def compute_payslip(self, employee_id, month, year):
        """حساب كشف أجر موظف (دون تخزين). Returns: dict."""
        emp = self._employees.get(employee_id)
        if not emp:
            raise PayrollError("employee not found")
        month, year = self._validate_period(month, year)
        details = compute_salary(emp["base_salary"])
        return {
            "employee_id": employee_id,
            "employee_name": emp["name"],
            "position": emp["position"],
            "department": emp["department"],
            "month": month,
            "year": year,
            "status": emp["status"],
            **details,
        }

    def get_payroll(self, month, year):
        """كشوف شهر محدد. Returns: قائمة (من الذاكرة أو تُحسب)."""
        month, year = self._validate_period(month, year)
        runs = []
        for emp in self._employees.values():
            run = self._runs.get(emp["id"], {}).get((month, year))
            if run is None:
                run = self.compute_payslip(emp["id"], month, year)
            runs.append(dict(run))
        runs.sort(key=lambda x: x["employee_name"].lower())
        return runs

    def get_employee_run(self, employee_id, month, year):
        """كشف موظف محدد (ذو تخزين أو يحسب). Returns: dict أو None."""
        if employee_id not in self._employees:
            return None
        month, year = self._validate_period(month, year)
        run = self._runs.get(employee_id, {}).get((month, year))
        if run is None:
            try:
                run = self.compute_payslip(employee_id, month, year)
            except PayrollError:
                return None
        return dict(run)

    def monthly_totals(self, month, year):
        """إجماليات الشهر: الرواتب الأساسية، الخصومات، الصافي (للنشطين فقط)."""
        month, year = self._validate_period(month, year)
        runs = [self.compute_payslip(e["id"], month, year)
                for e in self.list_employees(status="active")]
        total = {}
        for key in ("base_salary", "cnas_employee", "unemployment_insurance",
                    "taxable_salary", "irg", "net_salary"):
            total[key] = round(sum(r[key] for r in runs), 2)
        total["employee_count"] = len(runs)
        return total

    def employee_history(self, employee_id):
        """تاريخ كشوف موظف (شهور محسوبة عند الطلب)."""
        if employee_id not in self._employees:
            return []
        runs = [dict(r) for r in self._runs.get(employee_id, {}).values()]
        runs.sort(key=lambda x: (x["year"], x["month"]))
        return runs

    def export_payslips_csv(self, filepath, month, year):
        """تصدير كشوف الشهر إلى CSV. Returns: bool."""
        import csv
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["employee_id", "employee_name", "position",
                                 "base_salary", "cnas_employee",
                                 "unemployment_insurance", "taxable_salary",
                                 "irg", "net_salary"])
                for run in self.get_payroll(month, year):
                    writer.writerow([
                        run["employee_id"], run["employee_name"],
                        run["position"], run["base_salary"],
                        run["cnas_employee"], run["unemployment_insurance"],
                        run["taxable_salary"], run["irg"], run["net_salary"],
                    ])
            return True
        except OSError as exc:
            log.error("payroll export_csv error: %s", exc)
            return False

    def clear(self):
        self._employees = {}
        self._runs = {}
        self._next_employee_id = 1

    # ===== قاعدة البيانات =====

    def _ensure_tables(self, conn):
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {EMPLOYEE_TABLE} (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name VARCHAR(255) NOT NULL,
                position VARCHAR(255),
                department VARCHAR(100),
                base_salary DECIMAL(15,2) DEFAULT 0,
                hire_date DATE,
                status VARCHAR(20) DEFAULT 'active',
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {PAYROLL_TABLE} (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                pay_month INTEGER NOT NULL,
                pay_year INTEGER NOT NULL,
                base_salary DECIMAL(15,2) DEFAULT 0,
                cnas_employee DECIMAL(15,2) DEFAULT 0,
                unemployment_insurance DECIMAL(15,2) DEFAULT 0,
                taxable_salary DECIMAL(15,2) DEFAULT 0,
                irg DECIMAL(15,2) DEFAULT 0,
                net_salary DECIMAL(15,2) DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id, pay_month, pay_year),
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)

    def save_db(self):
        try:
            with get_connection() as conn:
                self._ensure_tables(conn)
                conn.execute(f"DELETE FROM {PAYROLL_TABLE}")
                conn.execute(f"DELETE FROM {EMPLOYEE_TABLE}")
                conn.execute("DELETE FROM sqlite_sequence WHERE name IN (?, ?)",
                             (PAYROLL_TABLE, EMPLOYEE_TABLE))
                for emp in self._employees.values():
                    conn.execute(
                        f"INSERT INTO {EMPLOYEE_TABLE} (employee_name, "
                        f"position, department, base_salary, hire_date, "
                        f"status, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (emp["name"], emp["position"], emp["department"],
                         emp["base_salary"], emp["hire_date"], emp["status"],
                         emp["notes"]),
                    )
                for emp_id, runs in self._runs.items():
                    for (month, year), run in runs.items():
                        conn.execute(
                            f"INSERT INTO {PAYROLL_TABLE} (employee_id, "
                            f"pay_month, pay_year, base_salary, cnas_employee, "
                            f"unemployment_insurance, taxable_salary, irg, "
                            f"net_salary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (emp_id, month, year, run["base_salary"],
                             run["cnas_employee"], run["unemployment_insurance"],
                             run["taxable_salary"], run["irg"],
                             run["net_salary"]),
                        )
            log.info("Saved %d employees to database", len(self._employees))
            return True
        except Exception as exc:
            log.error("payroll save_db error: %s", exc)
            return False

    def load_db(self):
        try:
            with get_connection() as conn:
                if not conn.table_exists(EMPLOYEE_TABLE):
                    return False
                emp_rows = conn.fetch_all(
                    f"SELECT employee_id, employee_name, position, department, "
                    f"base_salary, hire_date, status, notes "
                    f"FROM {EMPLOYEE_TABLE} ORDER BY employee_id"
                )
                run_rows = conn.fetch_all(
                    f"SELECT employee_id, pay_month, pay_year, base_salary, "
                    f"cnas_employee, unemployment_insurance, taxable_salary, "
                    f"irg, net_salary FROM {PAYROLL_TABLE}"
                )
        except Exception as exc:
            log.error("payroll load_db error: %s", exc)
            return False
        self._employees = {}
        self._runs = {}
        for r in emp_rows:
            emp = self._row_to_employee(r)
            self._employees[emp["id"]] = emp
            self._runs[emp["id"]] = {}
        for r in run_rows:
            month, year = r[1], r[2]
            self._runs[r[0]][(month, year)] = {
                "employee_id": r[0], "month": month, "year": year,
                "base_salary": round(float(r[3] or 0), 2),
                "cnas_employee": round(float(r[4] or 0), 2),
                "unemployment_insurance": round(float(r[5] or 0), 2),
                "taxable_salary": round(float(r[6] or 0), 2),
                "irg": round(float(r[7] or 0), 2),
                "net_salary": round(float(r[8] or 0), 2),
            }
        self._next_employee_id = max(self._employees.keys() or [0]) + 1
        return bool(self._employees)

    def clear_db(self):
        try:
            with get_connection() as conn:
                for tbl in (PAYROLL_TABLE, EMPLOYEE_TABLE):
                    if conn.table_exists(tbl):
                        conn.execute(f"DELETE FROM {tbl}")
            return True
        except Exception as exc:
            log.error("payroll clear_db error: %s", exc)
            return False

    @staticmethod
    def _row_to_employee(r):
        return {
            "id": r[0], "name": r[1], "position": r[2] or "",
            "department": r[3] or "", "base_salary": round(float(r[4] or 0), 2),
            "hire_date": r[5], "status": r[6] or "active", "notes": r[7] or "",
        }

    @staticmethod
    def _validate_period(month, year):
        try:
            month = int(month)
            year = int(year)
        except (TypeError, ValueError):
            raise PayrollError("month and year must be integers")
        if month < 1 or month > 12:
            raise PayrollError("month must be between 1 and 12")
        if year < 1900:
            raise PayrollError("invalid year")
        return month, year

    @staticmethod
    def _parse_amount(value, field):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise PayrollError(f"Invalid {field}: {value!r}")

    @staticmethod
    def _parse_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise PayrollError(f"Invalid date: {value!r}")
        raise PayrollError(f"Invalid date: {value!r}")


payroll_engine = PayrollEngine()
