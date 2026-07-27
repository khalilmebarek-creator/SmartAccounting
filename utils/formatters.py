# دوال التنسيق
# ============

from datetime import datetime


class NumberFormatter:
    """تنسيق الأرقام المالية"""

    @staticmethod
    def format_currency(value, currency="ر.س", decimals=2):
        """تنسيق رقم كعملة"""
        if value is None:
            return "--"
        try:
            formatted = f"{value:,.{decimals}f}"
            return f"{formatted} {currency}"
        except (ValueError, TypeError):
            return "--"

    @staticmethod
    def format_percentage(value, decimals=2):
        """تنسيق رقم كنسبة مئوية"""
        if value is None:
            return "--"
        try:
            return f"{value:.{decimals}f}%"
        except (ValueError, TypeError):
            return "--"

    @staticmethod
    def format_ratio(value, decimals=4):
        """تنسيق رقم كنسبة (بدون علامة %)"""
        if value is None:
            return "--"
        try:
            return f"{value:.{decimals}f}"
        except (ValueError, TypeError):
            return "--"

    @staticmethod
    def format_large_number(value, decimals=1):
        """تنسيق الأرقام الكبيرة (K, M, B)"""
        if value is None:
            return "--"
        try:
            abs_val = abs(value)
            sign = "-" if value < 0 else ""
            if abs_val >= 1_000_000_000:
                return f"{sign}{abs_val / 1_000_000_000:.{decimals}f}B"
            elif abs_val >= 1_000_000:
                return f"{sign}{abs_val / 1_000_000:.{decimals}f}M"
            elif abs_val >= 1_000:
                return f"{sign}{abs_val / 1_000:.{decimals}f}K"
            else:
                return f"{sign}{abs_val:.{decimals}f}"
        except (ValueError, TypeError):
            return "--"

    @staticmethod
    def format_days(value):
        """تنسيق رقم كعدد أيام"""
        if value is None:
            return "--"
        try:
            return f"{int(value)} يوم"
        except (ValueError, TypeError):
            return "--"


class DateFormatter:
    """تنسيق التواريخ"""

    @staticmethod
    def format_datetime(dt=None, fmt="%Y-%m-%d %H:%M"):
        """تنسيق تاريخ ووقت"""
        if dt is None:
            dt = datetime.now()
        if isinstance(dt, str):
            return dt
        try:
            return dt.strftime(fmt)
        except (ValueError, AttributeError):
            return "--"

    @staticmethod
    def format_date(dt=None, fmt="%Y-%m-%d"):
        """تنسيق تاريخ فقط"""
        if dt is None:
            dt = datetime.now()
        if isinstance(dt, str):
            return dt
        try:
            return dt.strftime(fmt)
        except (ValueError, AttributeError):
            return "--"

    @staticmethod
    def get_fiscal_year_label(year):
        """تنسيقتسمية السنة المالية"""
        return f"FY {year}/{year + 1}"
