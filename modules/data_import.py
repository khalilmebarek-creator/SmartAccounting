# استيراد البيانات من Excel
# ==========================

import pandas as pd
from .validation import DataValidator

# كلمات محجوزة في SQLite لا تُستخدم كأسماء جداول
_SQLITE_RESERVED = {
    "abort", "action", "add", "after", "all", "alter", "analyze", "and",
    "as", "asc", "attach", "autoincrement", "before", "begin", "between",
    "by", "cascade", "case", "cast", "check", "collate", "column", "commit",
    "conflict", "constraint", "create", "cross", "current_date", "current_time",
    "current_timestamp", "database", "default", "deferrable", "deferred",
    "delete", "desc", "detach", "distinct", "drop", "each", "else", "end",
    "escape", "except", "exclusive", "exists", "explain", "fail", "for",
    "foreign", "from", "full", "glob", "group", "having", "if", "ignore",
    "immediate", "in", "index", "indexed", "initially", "inner", "insert",
    "instead", "intersect", "into", "is", "isnull", "join", "key", "left",
    "like", "limit", "match", "natural", "no", "not", "notnull", "null",
    "of", "offset", "on", "or", "order", "outer", "plan", "pragma", "primary",
    "query", "raise", "recursive", "references", "regexp", "reindex", "release",
    "rename", "replace", "restrict", "right", "rollback", "row", "savepoint",
    "select", "set", "table", "temp", "temporary", "then", "to", "transaction",
    "trigger", "union", "unique", "update", "using", "vacuum", "values",
    "view", "virtual", "when", "where", "with", "without",
}

class DataImporter:
    """فئة لاستيراد البيانات من ملفات Excel"""
    
    def __init__(self):
        """تهيئة المستورد"""
        self.data = None
        self.validator = DataValidator()
    
    def import_from_excel(self, file_path, sheet_name=0):
        """
        استيراد البيانات من ملف Excel
        
        المدخلات:
            file_path: مسار الملف
            sheet_name: اسم الورقة (أو الرقم)
        """
        try:
            print(f"🔄 جاري استيراد البيانات من: {file_path}")
            
            # قراءة الملف
            self.data = pd.read_excel(file_path, sheet_name=sheet_name)
            
            print(f"✅ تم استيراد {len(self.data)} صف من البيانات")
            return True
            
        except FileNotFoundError:
            print(f"❌ الملف غير موجود: {file_path}")
            return False
        except Exception as e:
            print(f"❌ خطأ في استيراد الملف: {e}")
            return False
    
    def import_from_csv(self, file_path):
        """
        استيراد البيانات من ملف CSV
        
        المدخلات:
            file_path: مسار الملف
        """
        try:
            print(f"🔄 جاري استيراد البيانات من: {file_path}")
            
            # قراءة الملف
            self.data = pd.read_csv(file_path)
            
            print(f"✅ تم استيراد {len(self.data)} صف من البيانات")
            return True
            
        except FileNotFoundError:
            print(f"❌ الملف غير موجود: {file_path}")
            return False
        except Exception as e:
            print(f"❌ خطأ في استيراد الملف: {e}")
            return False
    
    def get_data(self):
        """الحصول على البيانات المستوردة"""
        return self.data
    
    def get_columns(self):
        """الحصول على أسماء الأعمدة"""
        if self.data is not None:
            return self.data.columns.tolist()
        return None
    
    def get_row_count(self):
        """الحصول على عدد الصفوف"""
        if self.data is not None:
            return len(self.data)
        return 0
    
    def validate_data(self):
        """التحقق من صحة البيانات"""
        if self.data is None:
            print("❌ لا توجد بيانات للتحقق!")
            return False
        
        print("🔍 جاري التحقق من صحة البيانات...")
        
        # التحقق من كل صف
        for idx, row in self.data.iterrows():
            data_dict = row.to_dict()
            
            if not self.validator.validate_financial_statement(data_dict):
                print(f"❌ خطأ في الصف {idx + 1}:")
                self.validator.print_report()
                return False
        
        print("✅ جميع البيانات صحيحة!")
        return True
    
    def get_summary(self):
        """الحصول على ملخص البيانات"""
        if self.data is None:
            print("❌ لا توجد بيانات!")
            return None
        
        print("\n" + "="*50)
        print("📊 ملخص البيانات")
        print("="*50)
        print(f"\n📈 عدد الصفوف: {len(self.data)}")
        print(f"📊 عدد الأعمدة: {len(self.data.columns)}")
        print(f"\n🔍 الأعمدة:")
        for col in self.data.columns:
            print(f"  • {col}")
        print("\n" + "="*50)
        
        return self.data.describe()
    
    def export_to_database(self, db_connection, table_name):
        """
        تصدير البيانات إلى قاعدة البيانات
        
        المدخلات:
            db_connection: اتصال قاعدة البيانات (instance of DatabaseConnection)
            table_name: اسم الجدول
        """
        if self.data is None:
            print("❌ لا توجد بيانات للتصدير!")
            return False
        
        # تنظيف اسم الجدول لمنع SQL injection
        safe_name = ''.join(c for c in table_name if c.isalnum() or c == '_')
        if not safe_name or not safe_name[0].isalpha():
            print(f"❌ اسم الجدول غير صالح: {table_name}")
            return False

        if safe_name.lower() in _SQLITE_RESERVED:
            print(f"❌ اسم الجدول كلمة محجوزة في SQLite: {table_name}")
            return False
        
        try:
            print(f"🔄 جاري تصدير البيانات إلى جدول: {safe_name}")
            
            # تنظيف القيم NaN → None (عشان SQLite يفهمها)
            data_clean = self.data.where(pd.notnull(self.data), None)
            
            # بناء استعلام INSERT ديناميكي
            columns = ', '.join(data_clean.columns)
            placeholders = ', '.join(['?'] * len(data_clean.columns))
            insert_query = f"INSERT INTO {safe_name} ({columns}) VALUES ({placeholders})"
            
            # تحويل DataFrame إلى list of tuples
            rows = [tuple(row) for row in data_clean.values]
            
            # تنفيذ الإدراج في transaction واحدة (أسرع وأأمن)
            if not db_connection.connect():
                print("❌ فشل الاتصال بقاعدة البيانات")
                try:
                    db_connection.disconnect()
                except Exception:
                    pass  # noqa: B110 — best-effort disconnect in error path
                return False
            
            try:
                for row in rows:
                    db_connection.cursor.execute(insert_query, row)
                db_connection.connection.commit()
                print(f"✅ تم تصدير {len(rows)} صف إلى جدول {table_name}")
                return True
            except Exception as e:
                db_connection.connection.rollback()
                print(f"❌ خطأ في الإدراج، تم التراجع: {e}")
                return False
            finally:
                db_connection.disconnect()
            
        except Exception as e:
            print(f"❌ خطأ في التصدير: {e}")
            return False
    
    def filter_data(self, column, value):
        """
        تصفية البيانات
        
        المدخلات:
            column: اسم العمود
            value: القيمة المطلوبة
        """
        if self.data is None:
            print("❌ لا توجد بيانات!")
            return None
        
        try:
            filtered = self.data[self.data[column] == value]
            print(f"✅ تم تصفية {len(filtered)} صف")
            return filtered
        except Exception as e:
            print(f"❌ خطأ في التصفية: {e}")
            return None
    
    def sort_data(self, column, ascending=True):
        """
        ترتيب البيانات
        
        المدخلات:
            column: اسم العمود
            ascending: ترتيب تصاعدي (True) أو تنازلي (False)
        """
        if self.data is None:
            print("❌ لا توجد بيانات!")
            return None
        
        try:
            sorted_data = self.data.sort_values(by=column, ascending=ascending)
            print(f"✅ تم ترتيب البيانات حسب {column}")
            return sorted_data
        except Exception as e:
            print(f"❌ خطأ في الترتيب: {e}")
            return None
        