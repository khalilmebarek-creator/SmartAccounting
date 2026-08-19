# اختبارات عمليات قاعدة البيانات
# =================================

import unittest
import sys
import os
import sqlite3
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import DatabaseConnection
from database.db_schema import create_tables
from database.db_operations import save_analysis, get_company_analyses, get_company_dupont_history


class TestDatabaseOperations(unittest.TestCase):
    """اختبارات شاملة لعمليات قاعدة البيانات"""
    
    @classmethod
    def setUpClass(cls):
        """إعداد قاعدة بيانات مؤقتة للاختبار"""
        # إنشاء ملف DB مؤقت لكل instance من الـ class
        cls.tmp_db = tempfile.NamedTemporaryFile(
            suffix='.db', delete=False
        )
        cls.tmp_db.close()
        
        # استبدال مسار الـ DB بالمسار المؤقت
        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name
        
        # ✅ إعادة تهيئة كل الـ references للـ db
        from database import db_connection as db_conn_module
        from database import db_operations
        from database import db_schema
        new_db = DatabaseConnection()
        db_conn_module.db = new_db
        db_operations.db = new_db
        db_schema.db = new_db
    
    @classmethod
    def tearDownClass(cls):
        """تنظيف بعد كل الاختبارات"""
        # استرجاع المسار الأصلي
        import config
        config.DATABASE_PATH = cls.original_path

        # إغلاق الاتصالات المُجمّعة قبل حذف الملف المؤقت
        from database import db_connection as db_conn_module
        db_conn_module.close_pool()

        # حذف الملف المؤقت
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)
    
    def setUp(self):
        """قبل كل اختبار - إنشاء الجداول + تنظيف"""
        # ✅ مسح كل البيانات القديمة من الـ DB المؤقت
        import sqlite3
        if os.path.exists(self.tmp_db.name):
            conn = sqlite3.connect(self.tmp_db.name)
            try:
                cursor = conn.cursor()
                # احصل على كل الجداول (تجاهل الجداول الداخلية زي sqlite_sequence)
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = [row[0] for row in cursor.fetchall()]
                # امسحها
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                conn.commit()
            finally:
                conn.close()
        
        result = create_tables()
        self.assertTrue(result)
    
    # ===== اختبارات الاتصال =====
    
    def test_create_tables(self):
        """اختبار إنشاء كل الجداول"""
        # التحقق من وجود الجداول
        db = DatabaseConnection()
        self.assertTrue(db.connect())
        try:
            db.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in db.cursor.fetchall()]
            expected_tables = [
                'companies', 'fiscal_years', 'assets', 'liabilities',
                'equity', 'income_statement', 'financial_ratios',
                'audit_log', 'notes'
            ]
            for table in expected_tables:
                self.assertIn(table, tables)
        finally:
            db.disconnect()
    
    # ===== اختبارات save_analysis =====
    
    def test_save_analysis_creates_company(self):
        """اختبار حفظ تحليل ينشئ شركة جديدة"""
        test_data = {
            'current_assets': 100000,
            'inventory': 20000,
            'current_liabilities': 50000,
            'gross_profit': 30000,
            'net_income': 15000,
            'revenue': 200000,
            'total_assets': 500000,
            'equity': 300000,
            'cost_of_goods_sold': 120000,
            'average_receivables': 40000,
            'average_inventory': 25000,
            'total_liabilities': 200000
        }
        ratios = {
            'current_ratio': 2.0,
            'quick_ratio': 1.6,
            'gross_profit_margin': 15.0,
            'net_profit_margin': 7.5,
            'roa': 3.0,
            'roe': 5.0,
            'asset_turnover': 0.4,
            'receivables_turnover': 5.0,
            'days_sales_outstanding': 73,
            'inventory_turnover': 4.8,
            'debt_to_equity': 0.6667,
            'debt_ratio': 0.4
        }
        
        fiscal_year_id = save_analysis(
            company_name="شركة اختبار",
            fiscal_year=2024,
            financial_data=test_data,
            ratios=ratios
        )
        
        self.assertIsNotNone(fiscal_year_id)
        self.assertIsInstance(fiscal_year_id, int)
    
    def test_save_analysis_reuses_existing_company(self):
        """اختبار حفظ تحليل لشركة موجودة - يستخدم نفس الـ company_id"""
        test_data = {'revenue': 100, 'net_income': 10, 'total_assets': 1000,
                    'total_liabilities': 500, 'equity': 500}
        ratios = {'current_ratio': 1.0}
        
        # حفظ مرتين لنفس الشركة
        id1 = save_analysis("شركة مكررة", 2023, test_data, ratios)
        id2 = save_analysis("شركة مكررة", 2024, test_data, ratios)
        
        self.assertIsNotNone(id1)
        self.assertIsNotNone(id2)
        # لازم يكون fiscal_year_ids مختلفة
        self.assertNotEqual(id1, id2)
    
    def test_save_analysis_with_missing_fields(self):
        """اختبار حفظ تحليل مع حقول ناقصة"""
        incomplete_data = {'revenue': 100}
        ratios = {'current_ratio': 1.0}
        
        # لازم ينجح (مع قيم افتراضية صفر)
        fiscal_year_id = save_analysis(
            "شركة ناقصة", 2024, incomplete_data, ratios
        )
        self.assertIsNotNone(fiscal_year_id)
    
    # ===== اختبارات get_company_analyses =====
    
    def test_get_company_analyses_empty(self):
        """اختبار جلب التحليلات لشركة غير موجودة"""
        results = get_company_analyses("شركة غير موجودة")
        self.assertEqual(len(results), 0)
    
    def test_get_company_analyses_after_save(self):
        """اختبار جلب التحليلات بعد الحفظ"""
        test_data = {
            'revenue': 200000, 'net_income': 15000, 'total_assets': 500000,
            'total_liabilities': 200000, 'equity': 300000
        }
        ratios = {
            'current_ratio': 2.0, 'net_profit_margin': 7.5, 'roe': 5.0,
            'debt_to_equity': 0.6667
        }
        
        save_analysis("شركة الاستعلام", 2024, test_data, ratios)
        results = get_company_analyses("شركة الاستعلام")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['year'], 2024)
        self.assertEqual(results[0]['company_name'], "شركة الاستعلام")
        self.assertEqual(results[0]['current_ratio'], 2.0)
    
    def test_get_company_analyses_multiple_years(self):
        """اختبار جلب تحليلات لعدة سنوات"""
        test_data = {'revenue': 100, 'net_income': 10}
        ratios = {'current_ratio': 1.5}
        
        save_analysis("شركة متعددة", 2022, test_data, ratios)
        save_analysis("شركة متعددة", 2023, test_data, ratios)
        save_analysis("شركة متعددة", 2024, test_data, ratios)
        
        results = get_company_analyses("شركة متعددة")
        self.assertEqual(len(results), 3)
        # لازم تكون مرتبة من الأحدث للأقدم
        self.assertEqual(results[0]['year'], 2024)

    # ===== اختبارات get_company_dupont_history - تاريخ DuPont =====

    def test_get_company_dupont_history_after_save(self):
        """اختبار جلب تاريخ DuPont بعد حفظ عدة سنوات"""
        test_data = {
            'revenue': 200000, 'net_income': 15000, 'total_assets': 500000,
            'total_liabilities': 200000, 'equity': 300000
        }
        ratios = {'net_profit_margin': 7.5, 'asset_turnover': 0.4, 'roe': 5.0}
        
        save_analysis("شركة التاريخ", 2023, test_data, ratios)
        save_analysis("شركة التاريخ", 2024, test_data, ratios)
        
        history = get_company_dupont_history("شركة التاريخ")
        self.assertEqual(len(history), 2)
        # مرتبة تصاعدياً حسب السنة
        self.assertEqual(history[0]['year'], 2023)
        self.assertEqual(history[1]['year'], 2024)
        # التحقق من المكونات
        self.assertEqual(history[0]['net_profit_margin'], 7.5)
        self.assertEqual(history[0]['asset_turnover'], 0.4)
        self.assertEqual(history[0]['roe'], 5.0)
        # EM مشتق: EM = ROE / (NPM × AT) = 5.0 / (7.5 × 0.4) = 1.6667
        self.assertAlmostEqual(history[0]['equity_multiplier'], 1.6667, places=3)

    def test_get_company_dupont_history_empty(self):
        """اختبار جلب تاريخ DuPont لشركة غير موجودة"""
        history = get_company_dupont_history("شركة بلا تاريخ")
        self.assertEqual(history, [])


class TestConnectionPool(unittest.TestCase):
    """اختبارات تجمّع اتصالات قاعدة البيانات"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        cls.tmp_db.close()
        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name

    @classmethod
    def tearDownClass(cls):
        import config
        config.DATABASE_PATH = cls.original_path
        from database import db_connection as db_conn_module
        db_conn_module.close_pool()
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)

    def test_connection_is_reused_across_operations(self):
        """يجب إعادة استخدام نفس الاتصال المُجمّع بين العمليات"""
        c1 = DatabaseConnection()
        c2 = DatabaseConnection()
        self.assertTrue(c1.connect())
        first = c1.connection
        c1.disconnect()
        self.assertTrue(c2.connect())
        self.assertIs(c2.connection, first, "يجب إعادة استخدام نفس الاتصال المُجمّع")
        c2.disconnect()

    def test_close_pool_closes_connections(self):
        """يجب إغلاق الاتصالات المُجمّعة عند close_pool ثم فتح اتصال جديد"""
        from database import db_connection as db_conn_module
        c = DatabaseConnection()
        self.assertTrue(c.connect())
        conn = c.connection
        c.disconnect()
        db_conn_module.close_pool()
        self.assertEqual(db_conn_module._pool, {}, "يجب إفراغ التجمّع بعد close_pool")
        try:
            conn.execute("SELECT 1")
            closed = False
        except Exception:
            closed = True
        self.assertTrue(closed, "يجب إغلاق الاتصال القديم بعد close_pool")
        self.assertTrue(c.connect())
        self.assertIsNot(c.connection, conn)
        c.disconnect()


if __name__ == '__main__':
    unittest.main(verbosity=2)
