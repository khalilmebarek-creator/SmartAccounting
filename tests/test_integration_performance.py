# اختبارات الأداء تحت الحمل (Performance Under Load)
# ====================================================
#   - 1000+ معاملة إدراج وقراءة في قاعدة البيانات
#   - عدة مستخدمين متزامنين
#   - مجموعات بيانات كبيرة عبر محركات الحساب/المقارنة/الرؤى
#   - إجهاد الذاكرة (Memory Stress) عبر tracemalloc
# تُستخدم حدود زمنية متسامحة عمداً (لتفادي اختبارات متقلبة في بيئات مختلفة).

import unittest
import sys
import os
import gc
import time
import sqlite3
import tempfile
import tracemalloc
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import DatabaseConnection
from database.db_schema import create_tables
from modules.calculations import CalculationEngine
from modules.demo_data import DEMO_COMPANIES
from modules.comparative import ComparativeAnalyzer
from modules.ai_insights import AIInsightsEngine
from modules.reporting import ReportGenerator


def _mk_financial(i):
    """توليد بيانات مالية متنوعة للشركة رقم i"""
    revenue = 100000 + i * 137
    net_income = 5000 + (i % 7) * 2500
    total_assets = 300000 + i * 211
    total_liabilities = 120000 + (i % 3) * 40000
    equity = total_assets - total_liabilities
    return {
        "current_assets": 120000 + i * 13,
        "inventory": 30000 + (i % 5) * 2000,
        "current_liabilities": 80000 + (i % 4) * 5000,
        "revenue": revenue,
        "net_income": net_income,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "equity": equity,
        "cost_of_goods_sold": revenue * 0.6,
        "gross_profit": revenue * 0.4,
        "average_receivables": 60000,
        "average_inventory": 32000,
    }


class _PerfDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp_db.close()
        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name
        from database import db_connection as db_conn_module
        from database import db_operations
        from database import db_schema
        new_db = DatabaseConnection()
        db_conn_module.db = new_db
        db_operations.db = new_db
        db_schema.db = new_db

    @classmethod
    def tearDownClass(cls):
        import config
        config.DATABASE_PATH = cls.original_path
        from database import db_connection as db_conn_module
        db_conn_module.close_pool()
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)

    def setUp(self):
        if os.path.exists(self.tmp_db.name):
            conn = sqlite3.connect(self.tmp_db.name)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                for name in [r[0] for r in cursor.fetchall()]:
                    cursor.execute(f"DROP TABLE IF EXISTS [{name}]")
                conn.commit()
            finally:
                conn.close()
        self.assertTrue(create_tables())

    def _raw_conn(self, timeout=60):
        conn = sqlite3.connect(self.tmp_db.name, timeout=timeout)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


class TestBulkTransactions(_PerfDB):
    """1000+ معاملة: إدراج جماعي وقراءة"""

    def test_insert_1200_tax_obligations(self):
        conn = self._raw_conn()
        try:
            conn.execute("INSERT INTO companies (company_name) VALUES ('حملة كبيرة')")
            conn.execute(
                "INSERT INTO fiscal_years (company_id, year, start_date, end_date) VALUES (?, ?, ?, ?)",
                (1, 2024, "2024-01-01", "2024-12-31"))
            fid = conn.execute("SELECT fiscal_year_id FROM fiscal_years WHERE company_id=1").fetchone()[0]
            rows = [
                (fid, "TVA" if i % 2 == 0 else "IBS", (i % 12) + 1, 20, 1000 + i, "pending")
                for i in range(1200)
            ]
            start = time.perf_counter()
            conn.executemany(
                "INSERT INTO tax_obligations "
                "(fiscal_year_id, tax_type, due_month, due_day, amount, status) "
                "VALUES (?, ?, ?, ?, ?, ?)", rows)
            conn.commit()
            elapsed = time.perf_counter() - start
            n = conn.execute("SELECT COUNT(*) FROM tax_obligations").fetchone()[0]
            self.assertEqual(n, 1200)

            start2 = time.perf_counter()
            fetched = conn.execute(
                "SELECT COUNT(*) FROM tax_obligations WHERE amount > 1000").fetchone()[0]
            read_time = time.perf_counter() - start2
            self.assertEqual(fetched, 1199)
        finally:
            conn.close()

        # الحدود الزمنية المتسامحة: الإدراج الجماعي أقل من 10 ثوانٍ
        self.assertLess(elapsed, 10.0, f"bulk insert too slow: {elapsed:.2f}s")
        self.assertLess(read_time, 5.0, f"read too slow: {read_time:.2f}s")

    def test_save_and_retrieve_1500_analyses(self):
        from database.db_operations import save_analysis, get_company_analyses
        start = time.perf_counter()
        for i in range(1500):
            fin = _mk_financial(i)
            save_analysis(f"شركة حملة {i}", 2024, fin, {
                "current_ratio": 1.5, "roe": 8.0, "net_profit_margin": 10.0,
            })
        elapsed = time.perf_counter() - start
        results = get_company_analyses("شركة حملة 1499")
        self.assertEqual(len(results), 1)
        self.assertLess(elapsed, 60.0, f"1500 saves too slow: {elapsed:.2f}s")

    def test_read_performance_with_index(self):
        conn = self._raw_conn()
        try:
            conn.execute("INSERT INTO companies (company_name) VALUES ('مؤشر')")
            conn.execute(
                "INSERT INTO fiscal_years (company_id, year, start_date, end_date) VALUES (1, 2024, '2024-01-01', '2024-12-31')")
            fid = conn.execute("SELECT fiscal_year_id FROM fiscal_years WHERE company_id=1").fetchone()[0]
            conn.executemany(
                "INSERT INTO tax_obligations (fiscal_year_id, tax_type, due_month, due_day, amount, status) "
                "VALUES (?, 'TVA', ?, 20, ?, 'pending')",
                [(fid, (i % 12) + 1, 100 + i) for i in range(1500)])
            conn.commit()
            start = time.perf_counter()
            for _ in range(200):
                conn.execute(
                    "SELECT COUNT(*) FROM tax_obligations WHERE fiscal_year_id=? AND due_month=3", (fid,)
                ).fetchone()
            elapsed = time.perf_counter() - start
            self.assertLess(elapsed, 5.0, f"indexed reads too slow: {elapsed:.2f}s")
        finally:
            conn.close()


class TestConcurrentUsers(_PerfDB):
    """عدة مستخدمين متزامنين"""

    def test_eight_users_twenty_saves_each(self):
        n_users, saves_each = 8, 20
        errors = []
        barrier = threading.Barrier(n_users)

        def worker(uid):
            try:
                barrier.wait(timeout=30)
                conn = sqlite3.connect(self.tmp_db.name, timeout=60)
                try:
                    conn.execute("PRAGMA journal_mode=WAL")
                    for i in range(saves_each):
                        conn.execute(
                            "INSERT INTO companies (company_name, industry) VALUES (?, ?)",
                            (f"مستخدم {uid} - {i}", "perf"))
                        conn.commit()
                finally:
                    conn.close()
            except Exception as e:  # pragma: no cover
                errors.append(e)

        start = time.perf_counter()
        threads = [threading.Thread(target=worker, args=(u,)) for u in range(n_users)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=180)
        elapsed = time.perf_counter() - start

        self.assertEqual(errors, [])
        conn = self._raw_conn()
        try:
            n = conn.execute("SELECT COUNT(*) FROM companies WHERE industry='perf'").fetchone()[0]
            self.assertEqual(n, n_users * saves_each)
        finally:
            conn.close()
        self.assertLess(elapsed, 90.0, f"concurrent writes too slow: {elapsed:.2f}s")


class TestLargeDatasets(unittest.TestCase):
    """مجموعات بيانات كبيرة عبر محركات الحساب"""

    def test_ratio_engine_on_2000_datasets(self):
        engine = CalculationEngine()
        start = time.perf_counter()
        count = 0
        for i in range(2000):
            ratios = engine.calculate_all_ratios(_mk_financial(i))
            if ratios is not None and len(ratios) == 20:
                count += 1
        elapsed = time.perf_counter() - start
        self.assertEqual(count, 2000)
        self.assertLess(elapsed, 30.0, f"2000 ratio calcs too slow: {elapsed:.2f}s")

    def test_comparative_on_eight_years(self):
        by_year = {2024 - i: _mk_financial(i * 31) for i in range(8)}
        start = time.perf_counter()
        comp = ComparativeAnalyzer(by_year).get_comparison()
        elapsed = time.perf_counter() - start
        self.assertEqual(comp["years"], sorted(by_year))
        self.assertEqual(len(comp["ratios_by_year"]), 8)
        self.assertLess(elapsed, 10.0, f"8-year comparative too slow: {elapsed:.2f}s")

    def test_ai_forecast_on_long_series(self):
        engine = AIInsightsEngine()
        series = [1000 + (i % 12) * 50 + i * 3 for i in range(120)]
        start = time.perf_counter()
        forecast = engine.forecast(series, months=6, method="linear")
        patterns = engine.patterns(series, periods_per_year=12)
        elapsed = time.perf_counter() - start
        self.assertIn("forecast", forecast)
        self.assertEqual(len(forecast["forecast"]), 6)
        self.assertIn("seasonality", patterns)
        self.assertIn("trend", patterns)
        self.assertLess(elapsed, 10.0, f"AI on 120 points too slow: {elapsed:.2f}s")

    def test_report_generation_on_large_ratios(self):
        ratios = {k: (i % 500) / 10 for i, k in enumerate([
            "current_ratio", "quick_ratio", "gross_profit_margin", "net_profit_margin",
            "roa", "roe", "asset_turnover", "receivables_turnover", "inventory_turnover",
            "debt_to_equity", "debt_ratio"])}
        reporter = ReportGenerator("شركة تقارير", 2024)
        start = time.perf_counter()
        for _ in range(300):
            reporter.generate_financial_ratios_report(ratios)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 10.0, f"300 report generations too slow: {elapsed:.2f}s")


class TestMemoryStress(unittest.TestCase):
    """إجهاد الذاكرة: لا نمو غير منضبط أثناء العمليات المتكررة"""

    def test_ratio_loop_memory_bounded(self):
        engine = CalculationEngine()
        gc.collect()
        tracemalloc.start()
        start = tracemalloc.get_traced_memory()
        try:
            for i in range(1500):
                engine.calculate_all_ratios(_mk_financial(i))
            current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(current, start[0] + 5 * 1024 * 1024,
                        f"leak suspect: current={current - start[0]:,} bytes")
        self.assertLess(peak, 60 * 1024 * 1024,
                        f"peak too high: {peak / 1024 / 1024:.1f} MB")

    def test_repeated_state_churn_stable(self):
        # محاكاة جلسات متكررة (تحميل شركة + حساب + مسح) — الذاكرة يجب أن تستقر
        from modules.demo_data import DemoData
        from ui.app_state import AppState
        import ui.app_state as app_state_module

        with tempfile.TemporaryDirectory() as tmp:
            app_state_module.SETTINGS_FILE = os.path.join(tmp, "s.json")
            app_state_module.DATA_FILE = os.path.join(tmp, "d.json")
            app_state_module.CHAT_FILE = os.path.join(tmp, "c.json")
            gc.collect()
            tracemalloc.start()
            snap1 = None
            snap2 = None
            try:
                for i in range(15):
                    state = AppState()
                    DemoData.load_company(state, list(DEMO_COMPANIES.keys())[i % 4])
                    state.clear()
                    del state
                    gc.collect()
                    if i == 7:
                        snap1 = tracemalloc.take_snapshot()
                gc.collect()
                snap2 = tracemalloc.take_snapshot()
                stats1 = sum(s.size_diff for s in snap1.compare_to(snap1, "filename")) if snap1 else 0
                stats2 = sum(s.size_diff for s in snap2.compare_to(snap1, "filename")) if snap1 else 0
            finally:
                tracemalloc.stop()
            self.assertLess(stats2, 3 * 1024 * 1024,
                            f"memory grew across sessions: {stats2:,} bytes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
