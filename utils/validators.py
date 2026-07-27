# دوال التحقق من صحة المدخلات
# ============================


class InputValidator:
    """التحقق من صحة مدخلات المستخدم"""

    @staticmethod
    def validate_number(value, min_val=None, max_val=None, field_name="القيمة"):
        """التحقق من صحة رقم"""
        try:
            num = float(value)
        except (ValueError, TypeError):
            return False, f"❌ {field_name}: يجب أن تكون قيمة رقمية"

        if min_val is not None and num < min_val:
            return False, f"❌ {field_name}: القيمة أقل من الحد الأدنى ({min_val})"

        if max_val is not None and num > max_val:
            return False, f"❌ {field_name}: القيمة تتجاوز الحد الأقصى ({max_val})"

        return True, ""

    @staticmethod
    def validate_non_negative(value, field_name="القيمة"):
        """التحقق من أن القيمة غير سالبة"""
        try:
            num = float(value)
            if num < 0:
                return False, f"❌ {field_name}: لا يمكن أن تكون قيمة سالبة"
            return True, ""
        except (ValueError, TypeError):
            return False, f"❌ {field_name}: يجب أن تكون قيمة رقمية"

    @staticmethod
    def validate_positive(value, field_name="القيمة"):
        """التحقق من أن القيمة موجبة (أكبر من صفر)"""
        try:
            num = float(value)
            if num <= 0:
                return False, f"❌ {field_name}: يجب أن تكون أكبر من صفر"
            return True, ""
        except (ValueError, TypeError):
            return False, f"❌ {field_name}: يجب أن تكون قيمة رقمية"

    @staticmethod
    def validate_text(value, min_length=1, max_length=200, field_name="النص"):
        """التحقق من صحة نص"""
        if not isinstance(value, str):
            return False, f"❌ {field_name}: يجب أن يكون نصاً"

        value = value.strip()
        if len(value) < min_length:
            return False, f"❌ {field_name}: نص قصير جداً (الحد الأدنى: {min_length})"

        if len(value) > max_length:
            return False, f"❌ {field_name}: نص طويل جداً (الحد الأقصى: {max_length})"

        return True, ""

    @staticmethod
    def validate_year(year, field_name="السنة"):
        """التحقق من صحة السنة المالية"""
        try:
            y = int(year)
            if y < 2000 or y > 2100:
                return False, f"❌ {field_name}: يجب أن تكون بين 2000 و 2100"
            return True, ""
        except (ValueError, TypeError):
            return False, f"❌ {field_name}: يجب أن تكون سنة صحيحة"

    @staticmethod
    def validate_balance_sheet(total_assets, total_liabilities, equity):
        """التحقق من توازن الميزانية العمومية"""
        try:
            assets = float(total_assets)
            liabilities = float(total_liabilities)
            eq = float(equity)

            diff = abs(assets - (liabilities + eq))
            if diff > 0.01:
                return False, (
                    f"❌ الميزانية غير متوازنة:\n"
                    f"   الأصول = {assets:,.2f}\n"
                    f"   الالتزامات + حقوق الملكية = {liabilities + eq:,.2f}\n"
                    f"   الفرق = {diff:,.2f}"
                )
            return True, ""
        except (ValueError, TypeError):
            return False, "❌ خطأ في قيم الميزانية"
