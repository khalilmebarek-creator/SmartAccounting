# التحقق من صحة البيانات
# =====================

class DataValidator:
    """فئة للتحقق من صحة البيانات المحاسبية"""
    
    def __init__(self):
        """تهيئة المدقق"""
        self.errors = []
        self.warnings = []
    
    def validate_non_negative_number(self, value, field_name):
        """التحقق من أن القيمة غير سالبة"""
        try:
            num = float(value)
            if num < 0:
                self.errors.append(f"❌ {field_name} لا يمكن أن تكون قيمة سالبة: {value}")
                return False
            return True
        except (ValueError, TypeError):
            self.errors.append(f"❌ {field_name} يجب أن تكون قيمة رقمية: {value}")
            return False
    
    def validate_financial_statement(self, data):
        """التحقق من صحة البيانات المالية الكاملة"""
        self.errors = []
        self.warnings = []
        
        # التحقق من الأصول
        if not self.validate_non_negative_number(data.get('total_assets'), 'إجمالي الأصول'):
            return False
        
        # التحقق من الالتزامات
        if not self.validate_non_negative_number(data.get('total_liabilities'), 'إجمالي الالتزامات'):
            return False
        
        # التحقق من حقوق المالكين
        if not self.validate_non_negative_number(data.get('equity'), 'حقوق المالكين'):
            return False
        
        # التحقق من المعادلة الأساسية
        # الأصول = الالتزامات + حقوق المالكين
        total_assets = float(data.get('total_assets') or 0)
        total_liabilities = float(data.get('total_liabilities') or 0)
        equity = float(data.get('equity') or 0)
        
        if abs(total_assets - (total_liabilities + equity)) > 0.01:
            self.errors.append("❌ عدم توازن الميزانية: الأصول ≠ الالتزامات + حقوق المالكين")
            return False
        
        # التحقق من الإيرادات
        if not self.validate_non_negative_number(data.get('revenue'), 'الإيرادات'):
            return False
        
        # التحقق من صافي الربح
        net_income = data.get('net_income', 0)
        try:
            float(net_income)
        except (ValueError, TypeError):
            self.errors.append("❌ صافي الربح يجب أن تكون قيمة رقمية")
            return False
        
        # تحذيرات
        if float(net_income) < 0:
            self.warnings.append("⚠️ تحذير: الشركة تحقق خسائر")
        
        if float(total_assets) == 0:
            self.warnings.append("⚠️ تحذير: إجمالي الأصول = صفر")
        
        if float(equity) <= 0:
            self.warnings.append("⚠️ تحذير: حقوق المالكين سالبة أو صفرية")
        
        return len(self.errors) == 0
    
    def get_errors(self):
        """الحصول على قائمة الأخطاء"""
        return self.errors
    
    def get_warnings(self):
        """الحصول على قائمة التحذيرات"""
        return self.warnings
    
    def print_report(self):
        """طباعة تقرير التحقق"""
        if self.errors:
            print("\n❌ الأخطاء المكتشفة:")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print("\n⚠️ التحذيرات:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ البيانات صحيحة تماماً!")
            