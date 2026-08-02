# اختبارات محرك الرواتب الجزائرية
# ================================

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.payroll import (
    PayrollEngine, PayrollError, payroll_engine,
    compute_irg, compute_salary,
    CNAS_EMPLOYEE_RATE, UNEMPLOYMENT_RATE, CNAS_EMPLOYER_RATE, IRG_BRACKETS)


class TestComputeIRG(unittest.TestCase):

    def test_zero_and_negative(self):
        self.assertEqual(compute_irg(0), 0.0)
        self.assertEqual(compute_irg(-100), 0.0)
        self.assertEqual(compute_irg(None), 0.0)

    def test_below_first_bracket(self):
        self.assertEqual(compute_irg(14000.0), 0.0)

    def test_first_bracket(self):
        self.assertEqual(compute_irg(20000.0), 1000.0)

    def test_second_bracket(self):
        self.assertEqual(compute_irg(50000.0), 9000.0)

    def test_third_bracket(self):
        self.assertEqual(compute_irg(200000.0), 58000.0)

    def test_fourth_bracket(self):
        self.assertEqual(compute_irg(500000.0), 168750.0)

    def test_boundary_floor(self):
        self.assertEqual(compute_irg(15000.0), 0.0)


class TestComputeSalary(unittest.TestCase):

    def test_net_salary_components(self):
        details = compute_salary(100000.0)
        self.assertEqual(details["base_salary"], 100000.0)
        self.assertEqual(details["cnas_employee"], 9000.0)
        self.assertEqual(details["unemployment_insurance"], 1500.0)
        self.assertEqual(details["taxable_salary"], 89500.0)
        self.assertGreater(details["irg"], 0.0)
        self.assertEqual(details["employer_cnas"], 26000.0)

    def test_zero_base(self):
        details = compute_salary(0.0)
        self.assertEqual(details["net_salary"], 0.0)
        self.assertEqual(details["irg"], 0.0)

    def test_rejects_negative_base(self):
        with self.assertRaises(PayrollError):
            compute_salary(-1)


class TestEmployees(unittest.TestCase):

    def setUp(self):
        self.engine = PayrollEngine()
        self.emp_id = self.engine.add_employee(
            "محمد", position="محاسب", department="المالية",
            base_salary=80000.0, hire_date="2024-01-01")

    def test_add_employee(self):
        emp = self.engine.get_employee(self.emp_id)
        self.assertEqual(emp["name"], "محمد")
        self.assertEqual(emp["base_salary"], 80000.0)
        self.assertEqual(emp["status"], "active")

    def test_add_employee_requires_name(self):
        with self.assertRaises(PayrollError):
            self.engine.add_employee("  ")

    def test_add_employee_rejects_negative_salary(self):
        with self.assertRaises(PayrollError):
            self.engine.add_employee("x", base_salary=-1)

    def test_add_employee_rejects_bad_status(self):
        with self.assertRaises(PayrollError):
            self.engine.add_employee("x", status="banned")

    def test_add_employee_defaults(self):
        emp_id = self.engine.add_employee("بدون تفاصيل")
        emp = self.engine.get_employee(emp_id)
        self.assertEqual(emp["base_salary"], 0.0)
        self.assertEqual(emp["status"], "active")

    def test_update_employee(self):
        self.assertTrue(self.engine.update_employee(self.emp_id, position="مدير"))
        self.assertEqual(self.engine.get_employee(self.emp_id)["position"], "مدير")

    def test_update_employee_missing(self):
        self.assertFalse(self.engine.update_employee(999, name="x"))

    def test_update_employee_unknown_field_ignored(self):
        self.assertTrue(self.engine.update_employee(self.emp_id, bogus=1))
        self.assertEqual(self.engine.get_employee(self.emp_id)["base_salary"],
                         80000.0)

    def test_update_employee_empty_name_raises(self):
        with self.assertRaises(PayrollError):
            self.engine.update_employee(self.emp_id, name="  ")

    def test_update_employee_negative_salary_raises(self):
        with self.assertRaises(PayrollError):
            self.engine.update_employee(self.emp_id, base_salary=-1)

    def test_update_employee_invalid_salary_type(self):
        with self.assertRaises(PayrollError):
            self.engine.update_employee(self.emp_id, base_salary="abc")

    def test_update_employee_hire_date(self):
        self.assertTrue(self.engine.update_employee(self.emp_id,
                                                    hire_date="2025-03-01"))
        self.assertEqual(self.engine.get_employee(self.emp_id)["hire_date"],
                         "2025-03-01")

    def test_update_employee_invalid_hire_date(self):
        with self.assertRaises(PayrollError):
            self.engine.update_employee(self.emp_id, hire_date="bad-date")

    def test_add_employee_invalid_salary_type(self):
        with self.assertRaises(PayrollError):
            self.engine.add_employee("x", base_salary="abc")

    def test_add_employee_invalid_hire_date(self):
        with self.assertRaises(PayrollError):
            self.engine.add_employee("x", hire_date="bad-date")

    def test_add_employee_invalid_hire_date_type(self):
        with self.assertRaises(PayrollError):
            self.engine.add_employee("x", hire_date=12345)

    def test_update_employee_invalid_status(self):
        with self.assertRaises(PayrollError):
            self.engine.update_employee(self.emp_id, status="ghost")

    def test_delete_employee(self):
        self.assertTrue(self.engine.delete_employee(self.emp_id))
        self.assertIsNone(self.engine.get_employee(self.emp_id))
        self.assertFalse(self.engine.delete_employee(999))

    def test_get_employee_missing(self):
        self.assertIsNone(self.engine.get_employee(999))

    def test_list_employees_sorted(self):
        self.engine.add_employee("أحمد", base_salary=50000.0)
        self.engine.update_employee(self.emp_id, status="inactive")
        names = [e["name"] for e in self.engine.list_employees()]
        self.assertEqual(names, ["أحمد", "محمد"])
        active = self.engine.list_employees(status="active")
        self.assertEqual(len(active), 1)


class TestPayrollRuns(unittest.TestCase):

    def setUp(self):
        self.engine = PayrollEngine()
        self.e1 = self.engine.add_employee("موظف أ", base_salary=60000.0)
        self.e2 = self.engine.add_employee("موظف ب", base_salary=45000.0)
        self.e3 = self.engine.add_employee("متقاعد", base_salary=30000.0,
                                           status="inactive")

    def test_compute_payslip(self):
        slip = self.engine.compute_payslip(self.e1, 8, 2026)
        self.assertEqual(slip["month"], 8)
        self.assertEqual(slip["year"], 2026)
        self.assertEqual(slip["base_salary"], 60000.0)
        self.assertEqual(slip["net_salary"],
                         slip["taxable_salary"] - slip["irg"])

    def test_compute_payslip_unknown_employee(self):
        with self.assertRaises(PayrollError):
            self.engine.compute_payslip(999, 8, 2026)

    def test_run_payroll_only_active(self):
        results = self.engine.run_payroll(8, 2026)
        self.assertEqual(len(results), 2)

    def test_get_payroll_sorted(self):
        self.engine.run_payroll(8, 2026)
        names = [r["employee_name"] for r in self.engine.get_payroll(8, 2026)]
        self.assertEqual(len(names), 3)
        self.assertEqual(names, sorted(names))

    def test_get_payroll_computes_when_absent(self):
        runs = self.engine.get_payroll(1, 2026)
        self.assertEqual(len(runs), 3)

    def test_get_employee_run(self):
        run = self.engine.get_employee_run(self.e1, 8, 2026)
        self.assertEqual(run["employee_id"], self.e1)

    def test_get_employee_run_unknown(self):
        self.assertIsNone(self.engine.get_employee_run(999, 8, 2026))

    def test_get_employee_run_compute_failure_returns_none(self):
        with mock.patch("modules.payroll.PayrollEngine.compute_payslip",
                        side_effect=PayrollError("boom")):
            self.assertIsNone(self.engine.get_employee_run(self.e1, 8, 2026))

    def test_employee_accepts_date_object(self):
        from datetime import date
        eid = self.engine.add_employee("بالتاريخ", hire_date=date(2024, 1, 1))
        self.assertEqual(self.engine.get_employee(eid)["hire_date"],
                         "2024-01-01")

    def test_monthly_totals(self):
        self.engine.run_payroll(8, 2026)
        totals = self.engine.monthly_totals(8, 2026)
        self.assertEqual(totals["employee_count"], 2)
        self.assertEqual(totals["base_salary"], 105000.0)
        expected_net = round(sum(
            compute_salary(emp["base_salary"])["net_salary"]
            for emp in self.engine.list_employees(status="active")), 2)
        self.assertEqual(totals["net_salary"], expected_net)

    def test_employee_history_sorted(self):
        self.engine.run_payroll(7, 2026)
        self.engine.run_payroll(8, 2026)
        history = self.engine.employee_history(self.e1)
        self.assertEqual(len(history), 2)
        self.assertEqual([(h["year"], h["month"]) for h in history],
                         [(2026, 7), (2026, 8)])

    def test_employee_history_unknown(self):
        self.assertEqual(self.engine.employee_history(999), [])

    def test_validate_period(self):
        with self.assertRaises(PayrollError):
            self.engine.compute_payslip(self.e1, 13, 2026)
        with self.assertRaises(PayrollError):
            self.engine.compute_payslip(self.e1, "x", 2026)
        with self.assertRaises(PayrollError):
            self.engine.compute_payslip(self.e1, 8, 1899)

    def test_export_payslips_csv(self):
        self.engine.run_payroll(8, 2026)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "payslips.csv")
            self.assertTrue(self.engine.export_payslips_csv(path, 8, 2026))
            with open(path, encoding="utf-8-sig") as f:
                content = f.read()
            self.assertIn("base_salary", content)

    def test_export_csv_os_error(self):
        with mock.patch("builtins.open", side_effect=OSError("boom")):
            self.assertFalse(self.engine.export_payslips_csv("x.csv", 8, 2026))

    def test_clear(self):
        self.engine.clear()
        self.assertEqual(self.engine.list_employees(), [])
        self.assertEqual(self.engine.monthly_totals(8, 2026)["employee_count"], 0)


class TestPayrollDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp.close()
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp.name
        from database.db_connection import close_pool
        close_pool()

    @classmethod
    def tearDownClass(cls):
        config.DATABASE_PATH = cls.original_path
        from database.db_connection import close_pool
        close_pool()
        os.unlink(cls.tmp.name)

    def setUp(self):
        self.engine = PayrollEngine()

    def test_save_and_load_db(self):
        e1 = self.engine.add_employee("سارة", base_salary=70000.0)
        self.engine.run_payroll(8, 2026)
        self.assertTrue(self.engine.save_db())
        other = PayrollEngine()
        self.assertTrue(other.load_db())
        self.assertEqual(len(other.list_employees()), 1)
        self.assertEqual(other.get_employee(e1)["base_salary"], 70000.0)
        run = other.get_employee_run(e1, 8, 2026)
        self.assertIsNotNone(run)
        new_id = other.add_employee("ياسين", base_salary=40000.0)
        self.assertEqual(new_id, 2)

    def test_load_db_empty_table_returns_false(self):
        self.engine.save_db()
        other = PayrollEngine()
        self.assertFalse(other.load_db())

    def test_clear_db(self):
        self.engine.add_employee("مغادر")
        self.engine.save_db()
        self.assertTrue(self.engine.clear_db())
        other = PayrollEngine()
        self.assertFalse(other.load_db())

    def test_save_db_raises_error(self):
        with mock.patch("modules.payroll.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.engine.save_db())

    def test_load_db_raises_error(self):
        with mock.patch("modules.payroll.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.engine.load_db())

    def test_load_db_missing_table(self):
        conn = mock.MagicMock()
        conn.table_exists.return_value = False
        with mock.patch("modules.payroll.get_connection") as get_conn:
            get_conn.return_value.__enter__.return_value = conn
            self.assertFalse(self.engine.load_db())

    def test_clear_db_raises_error(self):
        with mock.patch("modules.payroll.get_connection",
                        side_effect=Exception("boom")):
            self.assertFalse(self.engine.clear_db())


class TestPayrollSingleton(unittest.TestCase):

    def test_singleton_exists(self):
        self.assertIsInstance(payroll_engine, PayrollEngine)

    def test_constants(self):
        self.assertEqual(CNAS_EMPLOYEE_RATE, 0.09)
        self.assertEqual(CNAS_EMPLOYER_RATE, 0.26)
        self.assertEqual(UNEMPLOYMENT_RATE, 0.015)
        self.assertEqual(len(IRG_BRACKETS), 5)


if __name__ == "__main__":
    unittest.main()
