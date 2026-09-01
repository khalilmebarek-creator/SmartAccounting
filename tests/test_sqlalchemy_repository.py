# اختبارات طبقة SQLAlchemy (models + engine + repository)
# =======================================================

import unittest
import sys
import os
import sqlite3
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import models
from database.engine import get_engine, dispose_engine
from database.repository import (
    create_tables, save_analysis, get_company_analyses, get_company_dupont_history,
    save_scenario_results, get_scenario_results, delete_analysis,
)


EXPECTED_TABLES = {
    "companies", "fiscal_years", "assets", "liabilities", "equity",
    "income_statement", "financial_ratios", "audit_log", "notes", "tax_data",
    "tax_obligations", "scenario_results", "reference_standards",
    "competitor_data", "dashboard_layouts", "ledger_entries", "partners",
    "partner_transactions", "invoices", "invoice_items", "inventory_items",
    "inventory_movements", "employees", "payroll_runs", "budget_items",
}


class BaseSQLATest(unittest.TestCase):
    """قاعدة مشتركة: DB مؤقت + engine مُعادة تهيئته"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp_db.close()
        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name
        dispose_engine()

    @classmethod
    def tearDownClass(cls):
        import config
        config.DATABASE_PATH = cls.original_path
        dispose_engine()
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)

    def setUp(self):
        create_tables()


class TestModelsMetadata(unittest.TestCase):
    """اختبارات تعريف جداول SQLAlchemy metadata"""

    def test_models_metadata_has_all_expected_tables(self):
        for name in EXPECTED_TABLES:
            self.assertIn(name, models.metadata.tables, f"{name} missing from metadata")

    def test_models_has_expected_table_count(self):
        self.assertEqual(len(models.metadata.tables), len(EXPECTED_TABLES))

    def test_create_all_idempotent(self):
        self.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_db.close()
        try:
            import config
            orig = config.DATABASE_PATH
            config.DATABASE_PATH = self.tmp_db.name
            dispose_engine()
            try:
                models.create_all()
                models.create_all()
                conn = sqlite3.connect(self.tmp_db.name)
                try:
                    tables = {
                        r[0] for r in conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                    }
                    self.assertTrue(EXPECTED_TABLES.issubset(tables))
                finally:
                    conn.close()
            finally:
                config.DATABASE_PATH = orig
                dispose_engine()
        finally:
            if os.path.exists(self.tmp_db.name):
                os.unlink(self.tmp_db.name)


class TestCreateTables(BaseSQLATest):
    """create_tables() الآن يستدعي models.create_all()"""

    def test_create_tables_creates_all_tables(self):
        conn = sqlite3.connect(self.tmp_db.name)
        try:
            tables = {
                r[0] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            self.assertTrue(EXPECTED_TABLES.issubset(tables))
        finally:
            conn.close()

    def test_create_tables_idempotent(self):
        create_tables()
        create_tables()
        conn = sqlite3.connect(self.tmp_db.name)
        try:
            tables = {
                r[0] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            self.assertTrue(EXPECTED_TABLES.issubset(tables))
        finally:
            conn.close()


class TestRepositoryCRUD(BaseSQLATest):
    """رحلة CRUD كاملة عبر repository.py (طبقة SQLAlchemy Core)"""

    def test_save_and_get_analysis(self):
        fy_id = save_analysis(
            "شركة اختبار",
            2026,
            {
                "revenue": 300000, "cogs": 120000, "operating_expenses": 50000,
                "cash": 20000, "receivables": 30000, "inventory": 40000,
                "total_assets": 200000, "total_liabilities": 80000,
                "shareholders_equity": 120000, "average_payables": 8000,
            },
            {"net_profit_margin": 0.433, "current_ratio": 1.125},
        )
        self.assertIsNotNone(fy_id)

        analyses = get_company_analyses("شركة اختبار")
        self.assertEqual(len(analyses), 1)
        self.assertEqual(analyses[0]["year"], 2026)

    def test_delete_analysis_removes_row(self):
        fy_id = save_analysis(
            "شركة الحذف",
            2026,
            {
                "revenue": 100000, "cogs": 40000, "operating_expenses": 10000,
                "cash": 5000, "receivables": 5000, "inventory": 10000,
                "total_assets": 50000, "total_liabilities": 20000,
                "shareholders_equity": 30000, "average_payables": 5000,
            },
            {"net_profit_margin": 0.5, "current_ratio": 1.0},
        )
        delete_analysis("شركة الحذف", 2026)
        self.assertEqual(get_company_analyses("شركة الحذف"), [])
        self.assertEqual(get_company_dupont_history("شركة الحذف"), [])

    def test_scenario_results_round_trip(self):
        fy_id = save_analysis(
            "شركة السيناريوهات",
            2026,
            {
                "revenue": 100000, "cogs": 40000, "operating_expenses": 10000,
                "cash": 5000, "receivables": 5000, "inventory": 10000,
                "total_assets": 50000, "total_liabilities": 20000,
                "shareholders_equity": 30000, "average_payables": 5000,
            },
            {"net_profit_margin": 0.5},
        )
        scenarios = {
            "best": {
                "assumptions": {"revenue_change_pct": 0.2},
                "revenue": 120000.0, "net_income": 46560.0,
                "net_profit_margin": 38.8, "roe": 58.2,
            },
            "base": {
                "assumptions": {"revenue_change_pct": 0.0},
                "revenue": 100000.0, "net_income": 38800.0,
                "net_profit_margin": 38.8, "roe": 48.5,
            },
        }
        save_scenario_results(fy_id, scenarios)
        results = get_scenario_results(fy_id)
        self.assertEqual(len(results), 2)
        self.assertIn("best", results)
        self.assertEqual(results["best"]["assumptions"]["revenue_change_pct"], 0.2)


class TestDisposeEngineIsolation(unittest.TestCase):
    """dispose_engine() يُجدد الاتصال عند تغيير مسار الـ DB"""

    def test_engine_switches_when_path_changes(self):
        tmp1 = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp1.close()
        tmp2 = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp2.close()

        import config
        orig = config.DATABASE_PATH

        try:
            config.DATABASE_PATH = tmp1.name
            dispose_engine()
            db1 = get_engine().url.database

            config.DATABASE_PATH = tmp2.name
            dispose_engine()
            db2 = get_engine().url.database

            self.assertEqual(db1, tmp1.name)
            self.assertEqual(db2, tmp2.name)
            self.assertNotEqual(db1, db2)
        finally:
            config.DATABASE_PATH = orig
            dispose_engine()
            for p in (tmp1.name, tmp2.name):
                if os.path.exists(p):
                    os.unlink(p)


if __name__ == "__main__":
    unittest.main()
