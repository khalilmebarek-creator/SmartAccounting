# اختبارات استيراد البيانات
# ===========================

import unittest
import sys
import os
import pandas as pd
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_import import DataImporter


class TestDataImporter(unittest.TestCase):
    """اختبارات شاملة لمستورد البيانات"""
    
    def setUp(self):
        """إعداد المستورد"""
        self.importer = DataImporter()
    
    def tearDown(self):
        """تنظيف الملفات المؤقتة"""
        # أي ملفات مؤقتة يتم حذفها هنا
        pass
    
    # ===== اختبارات استيراد CSV =====
    
    def test_import_from_csv_valid(self):
        """اختبار استيراد CSV صحيح"""
        # إنشاء ملف CSV مؤقت
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False, encoding='utf-8'
        ) as f:
            f.write("name,revenue,net_income\n")
            f.write("شركة أ,100000,10000\n")
            f.write("شركة ب,200000,20000\n")
            tmp_path = f.name
        
        try:
            result = self.importer.import_from_csv(tmp_path)
            self.assertTrue(result)
            data = self.importer.get_data()
            self.assertIsNotNone(data)
            self.assertEqual(len(data), 2)
        finally:
            os.unlink(tmp_path)
    
    def test_import_from_csv_nonexistent(self):
        """اختبار استيراد ملف غير موجود"""
        result = self.importer.import_from_csv("/nonexistent/file.csv")
        self.assertFalse(result)
    
    # ===== اختبارات get_data و get_columns =====
    
    def test_get_data_no_data(self):
        """اختبار جلب البيانات قبل الاستيراد"""
        data = self.importer.get_data()
        self.assertIsNone(data)
    
    def test_get_columns_no_data(self):
        """اختبار جلب الأعمدة قبل الاستيراد"""
        columns = self.importer.get_columns()
        self.assertIsNone(columns)
    
    def test_get_row_count_zero(self):
        """اختبار عدد الصفوف قبل الاستيراد"""
        count = self.importer.get_row_count()
        self.assertEqual(count, 0)
    
    # ===== اختبارات filter_data و sort_data =====
    
    def test_filter_data(self):
        """اختبار تصفية البيانات"""
        # إعداد بيانات يدوياً
        self.importer.data = pd.DataFrame({
            'company': ['A', 'B', 'A'],
            'revenue': [100, 200, 300]
        })
        
        filtered = self.importer.filter_data('company', 'A')
        self.assertIsNotNone(filtered)
        self.assertEqual(len(filtered), 2)
    
    def test_filter_data_no_data(self):
        """اختبار تصفية بدون بيانات"""
        result = self.importer.filter_data('col', 'val')
        self.assertIsNone(result)
    
    def test_sort_data(self):
        """اختبار ترتيب البيانات"""
        self.importer.data = pd.DataFrame({
            'value': [30, 10, 20]
        })
        
        sorted_data = self.importer.sort_data('value', ascending=True)
        self.assertIsNotNone(sorted_data)
        self.assertEqual(sorted_data.iloc[0]['value'], 10)
    
    # ===== اختبارات validate_data =====
    
    def test_validate_data_no_data(self):
        """اختبار التحقق بدون بيانات"""
        result = self.importer.validate_data()
        self.assertFalse(result)
    
    def test_validate_data_valid_financial(self):
        """اختبار التحقق من بيانات مالية صحيحة"""
        self.importer.data = pd.DataFrame([{
            'total_assets': 500000,
            'total_liabilities': 200000,
            'equity': 300000,
            'revenue': 200000,
            'net_income': 15000
        }])
        
        result = self.importer.validate_data()
        self.assertTrue(result)
    
    def test_validate_data_unbalanced(self):
        """اختبار التحقق من بيانات غير متوازنة"""
        self.importer.data = pd.DataFrame([{
            'total_assets': 600000,  # غير متوازن
            'total_liabilities': 200000,
            'equity': 300000,
            'revenue': 200000,
            'net_income': 15000
        }])
        
        result = self.importer.validate_data()
        self.assertFalse(result)
    
    # ===== اختبارات export_to_database - Bug #5 =====
    
    def test_export_to_database_no_data(self):
        """اختبار التصدير بدون بيانات"""
        result = self.importer.export_to_database(None, "test_table")
        self.assertFalse(result)
    
    def test_export_to_database_with_data(self):
        """اختبار التصدير ببيانات صحيحة"""
        from database.db_connection import DatabaseConnection
        import tempfile as tmp
        
        # إعداد البيانات
        self.importer.data = pd.DataFrame([{
            'log_id': 1, 'fiscal_year_id': 1, 'issue_type': 'test',
            'issue_description': 'test desc', 'severity': 'low', 'status': 'open'
        }])
        
        # استخدام DB مؤقت منعاً للتضارب
        tmp_db_file = tmp.NamedTemporaryFile(suffix='.db', delete=False)
        tmp_db_file.close()
        
        # إنشاء اتصال بجدول مؤقت
        db = DatabaseConnection()
        # ✅ نخلي الـ DB يستخدم الملف المؤقت
        original_path = None
        try:
            import config
            original_path = config.DATABASE_PATH
            config.DATABASE_PATH = tmp_db_file.name
            db.connect()
            # إنشاء جدول اختبار
            db.cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    log_id INTEGER, fiscal_year_id INTEGER,
                    issue_type TEXT, issue_description TEXT,
                    severity TEXT, status TEXT
                )
            """)
            db.connection.commit()
            db.disconnect()
            
            # تصدير
            db.connect()  # نعيد الاتصال عشان نستخدم الملف المؤقت
            result = self.importer.export_to_database(db, "test_table")
            self.assertTrue(result)
            db.disconnect()
            
            # التحقق من البيانات
            db.connect()
            db.cursor.execute("SELECT COUNT(*) FROM test_table")
            count = db.cursor.fetchone()[0]
            db.disconnect()
            self.assertEqual(count, 1)
        finally:
            # استرجاع المسار الأصلي
            if original_path:
                config.DATABASE_PATH = original_path
            # حذف الملف المؤقت (مع تجاهل permission errors على Windows)
            if os.path.exists(tmp_db_file.name):
                try:
                    os.unlink(tmp_db_file.name)
                except (PermissionError, OSError):
                    pass  # Windows قد يحتفظ بالملف مؤقتاً


if __name__ == '__main__':
    unittest.main(verbosity=2)
