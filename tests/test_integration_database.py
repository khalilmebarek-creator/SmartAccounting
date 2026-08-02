# اختبارات تكامل قاعدة البيانات
# ==============================
#   - سلامة البيانات (Data Integrity): مفتاح خارجي، تفرد، ترابط بين الجداول
#   - المعاملات (Transactions): تراجع آمن عند الخطأ
#   - الوصول المتزامن (Concurrent Access): كتابة/قراءة من عدة مستخدمين
#   - النسخ الاحتياطي والاسترجاع (Backup/Restore): رحلة دائرية

import unittest
import sys
import os
import sqlite3
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import DatabaseConnection
from database.db_schema import create_tables
from database.db_operations import (
    save_analysis, get_company_analyses, get_company_dupont_history,
    get_company_ratio_history, delete_analysis, save_tax_obligation,
    get_tax_obligations, update_obligation_status, save_scenario_results,
    save_tax_data, get_tax_data,
)


class _BaseIntegrationDB(unittest.TestCase):
    """قاعدة مشتركة: قاعدة بيانات مؤقتة معزولة لكل فئة"""

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
        import sqlite3 as _sq
        if os.path.exists(self.tmp_db.name):
            conn = _sq.connect(self.tmp_db.name)
            try:
                conn.execute("PRAGMA foreign_keys = OFF")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = [row[0] for row in cursor.fetchall()]
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS [{table}]")
                conn.commit()
            finally:
                conn.close()
        self.assertTrue(create_tables())

    # ----- أدوات مساعدة -----
    def _save_demo(self, company, year, revenue=500000, net_income=60000,
                   total_assets=1200000, total_liabilities=500000, equity=700000):
        financial = {
            "current_assets": 400000, "inventory": 90000,
            "current_liabilities": 200000, "revenue": revenue,
            "net_income": net_income, "total_assets": total_assets,
            "total_liabilities": total_liabilities, "equity": equity,
            "cost_of_goods_sold": revenue * 0.6,
            "average_receivables": 80000, "average_inventory": 95000,
        }
        ratios = {
            "current_ratio": 2.0, "net_profit_margin": 12.0, "roe": 8.57,
            "debt_to_equity": 0.714, "asset_turnover": 0.42,
            "quick_ratio": 1.55, "gross_profit_margin": 40.0,
            "roa": 5.0, "receivables_turnover": 6.25,
            "days_sales_outstanding": 58, "inventory_turnover": 3.2,
            "debt_ratio": 0.42,
        }
        return save_analysis(company, year, financial, ratios)

    def _raw_conn(self):
        conn = sqlite3.connect(self.tmp_db.name, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


class TestDataIntegrity(_BaseIntegrationDB):
    """سلامة البيانات: قيود، تفرد، ترابط"""

    def test_foreign_key_enforced(self):
        conn = self._raw_conn()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO income_statement (fiscal_year_id, revenue) VALUES (9999, 100)"
                )
        finally:
            conn.close()

    def test_unique_fiscal_year_per_asset_row(self):
        fid = self._save_demo("الشركة الحصرية", 2024)
        self.assertIsNotNone(fid)
        conn = self._raw_conn()
        try:
            # save_analysis أنشأ صف أصول واحداً للسنة المالية
            n = conn.execute(
                "SELECT COUNT(*) FROM assets WHERE fiscal_year_id=?", (fid,)).fetchone()[0]
            self.assertEqual(n, 1)
            # صف ثانٍ لنفس السنة → مرفوض بتفرد
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO assets (fiscal_year_id, total_assets) VALUES (?, 200)",
                    (fid,))
        finally:
            conn.close()

    def test_unique_company_year_combination(self):
        fid1 = self._save_demo("الشركة الموحدة", 2024)
        fid2 = self._save_demo("الشركة الموحدة", 2024)  # نفس الشركة والسنة → يعيد نفس السنة
        self.assertEqual(fid1, fid2)

    def test_retrieve_pipeline_matches_saved(self):
        fid = self._save_demo("شركة الاسترجاع", 2024, revenue=600000, net_income=72000)
        self.assertIsNotNone(fid)
        analyses = get_company_analyses("شركة الاسترجاع")
        self.assertEqual(len(analyses), 1)
        self.assertEqual(analyses[0]["fiscal_year_id"], fid)
        self.assertEqual(analyses[0]["current_ratio"], 2.0)
        self.assertEqual(analyses[0]["roe"], 8.57)

    def test_dupont_history_derives_equity_multiplier(self):
        self._save_demo("شركة التاريخ", 2023, net_income=50000)
        self._save_demo("شركة التاريخ", 2024, net_income=60000)
        history = get_company_dupont_history("شركة التاريخ")
        self.assertEqual(len(history), 2)
        self.assertEqual([h["year"] for h in history], [2023, 2024])
        self.assertGreater(history[0]["equity_multiplier"], 0)

    def test_ratio_history_ordered_ascending(self):
        self._save_demo("شركة الاتجاه", 2022)
        self._save_demo("شركة الاتجاه", 2023)
        self._save_demo("شركة الاتجاه", 2024)
        hist = get_company_ratio_history("شركة الاتجاه")
        self.assertEqual([h["year"] for h in hist], [2022, 2023, 2024])

    def test_delete_analysis_cascades_children(self):
        fid = self._save_demo("شركة الحذف", 2024)
        save_tax_obligation(fid, {"tax_type": "TVA", "month": 1, "amount": 1000, "status": "pending"})
        self.assertEqual(len(get_tax_obligations(fid)), 1)
        self.assertTrue(delete_analysis("شركة الحذف", 2024))
        self.assertEqual(len(get_company_analyses("شركة الحذف")), 0)
        # الالتزام الجبائي حُذف أيضاً بفعل الحذف الترابطي
        conn = self._raw_conn()
        try:
            n = conn.execute("SELECT COUNT(*) FROM tax_obligations WHERE fiscal_year_id=?", (fid,)).fetchone()[0]
            self.assertEqual(n, 0)
        finally:
            conn.close()

    def test_tax_data_roundtrip(self):
        fid = self._save_demo("شركة الجباية", 2024)
        payload = {
            "activity_type": "commercial", "number_of_employees": 12,
            "avg_salary": 40000, "ibs_amount": 260000, "ibs_rate": 0.26,
            "tva_collected": 190000, "tva_paid": 120000, "tva_net": 70000,
            "total_taxes": 330000, "tax_burden_pct": 0.25,
            "simulation": {"note": "استحقاق سنوي"},
        }
        self.assertTrue(save_tax_data(fid, payload))
        loaded = get_tax_data(fid)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["ibs_amount"], 260000)
        self.assertEqual(loaded["simulation"]["note"], "استحقاق سنوي")


class TestTransactions(_BaseIntegrationDB):
    """المعاملات: التراجع يحافظ على سلامة قاعدة البيانات"""

    def test_validation_error_rolls_back_cleanly(self):
        before = len(get_company_analyses("شركة فاسدة"))
        bad_data = {"revenue": -500, "net_income": 10}
        result = save_analysis("شركة فاسدة", 2024, bad_data, {"roe": 1.0})
        self.assertIsNone(result)
        after = len(get_company_analyses("شركة فاسدة"))
        self.assertEqual(before, after)
        # لا يجب أن تُنشأ الشركة أصلاً
        conn = self._raw_conn()
        try:
            n = conn.execute("SELECT COUNT(*) FROM companies WHERE company_name='شركة فاسدة'").fetchone()[0]
            self.assertEqual(n, 0)
        finally:
            conn.close()

    def test_scenario_save_with_bad_fy_fails_without_partial_rows(self):
        # سنة مالية غير موجودة → مفتاح خارجي يفشل والتراجع يمنع أي صف جزئي
        self.assertFalse(save_scenario_results(99999, {
            "best": {"assumptions": {}, "revenue": 1, "net_income": 1},
        }))
        conn = self._raw_conn()
        try:
            n = conn.execute("SELECT COUNT(*) FROM scenario_results WHERE fiscal_year_id=99999").fetchone()[0]
            self.assertEqual(n, 0)
        finally:
            conn.close()

    def test_invalid_status_rejected_without_change(self):
        fid = self._save_demo("شركة الالتزام", 2024)
        save_tax_obligation(fid, {"tax_type": "IBS", "month": 3, "amount": 5000, "status": "pending"})
        obs = get_tax_obligations(fid)
        self.assertEqual(len(obs), 1)
        self.assertFalse(update_obligation_status(obs[0]["obligation_id"], "bogus_status"))
        # لا تغيير
        obs2 = get_tax_obligations(fid)
        self.assertEqual(obs2[0]["status"], "pending")

    def test_tax_data_negative_rejected(self):
        fid = self._save_demo("شركة السالب", 2024)
        self.assertFalse(save_tax_data(fid, {"ibs_amount": -10, "tva_collected": 0, "total_taxes": 0}))
        self.assertIsNone(get_tax_data(fid))


class TestConcurrentAccess(_BaseIntegrationDB):
    """الوصول المتزامن: عدة مستخدمين يكتبون ويقرؤون في آنٍ واحد"""

    def test_concurrent_writes_from_eight_threads(self):
        n_users = 8
        saves_each = 25
        errors = []
        barrier = threading.Barrier(n_users)

        def worker(uid):
            try:
                barrier.wait(timeout=30)
                conn = sqlite3.connect(self.tmp_db.name, timeout=30)
                try:
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("PRAGMA foreign_keys = ON")
                    for i in range(saves_each):
                        conn.execute(
                            "INSERT INTO companies (company_name) VALUES (?)",
                            (f"مستخدم {uid} - معاملة {i}",))
                        conn.commit()
                finally:
                    conn.close()
            except Exception as e:  # pragma: no cover - تسجيل فقط
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(u,)) for u in range(n_users)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=120)

        self.assertEqual(errors, [])
        conn = self._raw_conn()
        try:
            n = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            self.assertEqual(n, n_users * saves_each)
        finally:
            conn.close()

    def test_concurrent_mixed_read_write_keeps_integrity(self):
        n_users = 6
        errors = []
        barrier = threading.Barrier(n_users + 1)

        def writer(uid):
            try:
                barrier.wait(timeout=30)
                conn = sqlite3.connect(self.tmp_db.name, timeout=30)
                try:
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("PRAGMA foreign_keys = ON")
                    for i in range(15):
                        conn.execute(
                            "INSERT INTO companies (company_name) VALUES (?)",
                            (f"كاتب {uid} - {i}",))
                        conn.commit()
                finally:
                    conn.close()
            except Exception as e:  # pragma: no cover
                errors.append(e)

        def reader():
            try:
                barrier.wait(timeout=30)
                conn = sqlite3.connect(self.tmp_db.name, timeout=30)
                try:
                    conn.execute("PRAGMA journal_mode=WAL")
                    for _ in range(40):
                        conn.execute("SELECT COUNT(*) FROM companies").fetchone()
                finally:
                    conn.close()
            except Exception as e:  # pragma: no cover
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(u,)) for u in range(n_users)]
        threads.append(threading.Thread(target=reader))
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=120)

        self.assertEqual(errors, [])
        conn = self._raw_conn()
        try:
            n = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            self.assertEqual(n, n_users * 15)
            # كل كاتب كُتب بشكل كامل دون فقدان
            uniq = conn.execute("SELECT COUNT(DISTINCT company_name) FROM companies").fetchone()[0]
            self.assertEqual(uniq, n_users * 15)
        finally:
            conn.close()

    def test_pool_reuse_reuses_single_connection(self):
        # إعادة استخدام اتصال مُجمّع واحد عبر دورات متتالية دون تسريب
        from database.db_connection import _pool, close_pool
        close_pool()
        for _ in range(20):
            c = DatabaseConnection()
            self.assertTrue(c.connect())
            c.execute("INSERT INTO companies (company_name) VALUES (?)",
                      ("مجمع إعادة الاستخدام",))
            c.disconnect()
        self.assertEqual(len(_pool), 1)
        conn = self._raw_conn()
        try:
            n = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE company_name='مجمع إعادة الاستخدام'"
            ).fetchone()[0]
            self.assertEqual(n, 20)
        finally:
            conn.close()


class TestBackupRestore(_BaseIntegrationDB):
    """النسخ الاحتياطي والاسترجاع"""

    def test_backup_restore_roundtrip(self):
        from modules.backup import BackupManager
        self._save_demo("شركة النسخ", 2024, revenue=700000)
        self._save_demo("شركة النسخ", 2025, revenue=750000)

        mgr = BackupManager()
        with tempfile.TemporaryDirectory() as tmp:
            backup_path = os.path.join(tmp, "accounting.db")
            ok, _ = mgr.backup(backup_path)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(backup_path))

            # تدمير البيانات
            self.assertTrue(delete_analysis("شركة النسخ", 2024))
            self.assertTrue(delete_analysis("شركة النسخ", 2025))
            self.assertEqual(len(get_company_analyses("شركة النسخ")), 0)

            # الاسترجاع
            ok2, _ = mgr.restore(backup_path)
            self.assertTrue(ok2)
            analyses = get_company_analyses("شركة النسخ")
            self.assertEqual(len(analyses), 2)
            self.assertEqual(analyses[0]["year"], 2025)

    def test_auto_backup_lands_in_backups_dir(self):
        from modules.backup import BackupManager
        self._save_demo("شركة تلقائية", 2024)
        mgr = BackupManager()
        ok, path = mgr.auto_backup(label="test")
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(path))
        backups = mgr.list_backups(os.path.dirname(path))
        self.assertTrue(any(b["name"].endswith(os.path.basename(path)) for b in backups))

    def test_export_import_json_roundtrip(self):
        from modules.backup import BackupManager
        self._save_demo("شركة جسون", 2024, revenue=300000)
        mgr = BackupManager()
        with tempfile.TemporaryDirectory() as tmp:
            ok, count = mgr.export_all_to_json(tmp)
            self.assertTrue(ok)
            self.assertGreater(count, 0)
            exported = [f for f in os.listdir(tmp) if f.endswith(".json")]
            self.assertGreater(len(exported), 0)

            # مسح قاعدة البيانات ثم إعادة استيراد — رحلة دائرية حقيقية
            import sqlite3 as _sq
            conn = _sq.connect(self.tmp_db.name)
            try:
                conn.execute("PRAGMA foreign_keys = OFF")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                for table in [r[0] for r in cursor.fetchall()]:
                    cursor.execute(f"DROP TABLE IF EXISTS [{table}]")
                conn.commit()
            finally:
                conn.close()
            self.assertTrue(create_tables())

            ok2, _ = mgr.import_from_json(os.path.join(tmp, "companies.json"))
            self.assertTrue(ok2)
            conn = self._raw_conn()
            try:
                n = conn.execute(
                    "SELECT COUNT(*) FROM companies WHERE company_name='شركة جسون'"
                ).fetchone()[0]
                self.assertEqual(n, 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
