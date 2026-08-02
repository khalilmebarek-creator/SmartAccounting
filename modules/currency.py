# محرك تعدد العملات
# ====================
# إدارة العملات + أسعار الصرف + التحويل + تقارير متعددة العملات

from utils.app_logger import get_logger

log = get_logger("currency")

# العملات الافتراضية: الكود → (الاسم بالعربية، الاسم بالإنجليزية، الرمز)
DEFAULT_CURRENCIES = {
    "DZD": {"name_ar": "دينار جزائري", "name_en": "Algerian Dinar", "symbol": "دج"},
    "USD": {"name_ar": "دولار أمريكي", "name_en": "US Dollar", "symbol": "$"},
    "EUR": {"name_ar": "يورو", "name_en": "Euro", "symbol": "€"},
    "TND": {"name_ar": "دينار تونسي", "name_en": "Tunisian Dinar", "symbol": "د.ت"},
    "MAD": {"name_ar": "درهم مغربي", "name_en": "Moroccan Dirham", "symbol": "م.د"},
    "SAR": {"name_ar": "ريال سعودي", "name_en": "Saudi Riyal", "symbol": "ر.س"},
    "EGP": {"name_ar": "جنيه مصري", "name_en": "Egyptian Pound", "symbol": "ج.م"},
}

# قائمة بنود القوائم المالية المدعومة في التقرير متعدد العملات
REPORT_ITEMS = [
    "revenue", "cost_of_goods_sold", "gross_profit",
    "operating_expenses", "operating_income", "interest_expense",
    "tax_expense", "net_income",
    "current_assets", "non_current_assets", "total_assets",
    "current_liabilities", "non_current_liabilities", "total_liabilities",
    "share_capital", "retained_earnings", "total_equity",
    "cash", "inventory", "average_receivables", "average_payables",
]


class CurrencyEngine:
    """محرك تعدد العملات: تحويل + أسعار صرف + تنسيق متعدد العملات.

    معنى سعر الصرف: سعر وحدة واحدة من العملة الأجنبية بالعملة الأساسية.
    مثال: أساس DZD وسعر USD = 134 → 1 دولار = 134 دينار.
    """

    def __init__(self, base_currency="DZD", rates=None, currencies=None):
        self.base_currency = base_currency
        self.currencies = dict(currencies) if currencies else dict(DEFAULT_CURRENCIES)
        self.rates = dict(rates) if rates else {}
        self.rates.setdefault(self.base_currency, 1.0)

    # ===== الإدارة =====

    def set_base_currency(self, code):
        """تعيين العملة الأساسية وإعادة تطبيع أسعار الصرف."""
        code = (code or "").upper().strip()
        if code not in self.currencies:
            return False
        if code == self.base_currency:
            return True
        factor = self.get_rate(code)
        if factor <= 0:
            return False
        for c in list(self.rates):
            self.rates[c] = self.rates[c] / factor
        self.base_currency = code
        self.rates[code] = 1.0
        return True

    def add_currency(self, code, name_ar=None, symbol=None, rate=None):
        """إضافة عملة جديدة (اختيارياً مع سعر صرف أولي)."""
        code = (code or "").upper().strip()
        if not code:
            return False
        meta = self.currencies.get(code, {})
        self.currencies[code] = {
            "name_ar": name_ar or meta.get("name_ar", code),
            "name_en": meta.get("name_en", code),
            "symbol": symbol or meta.get("symbol", code),
        }
        if rate is not None:
            self.set_rate(code, rate)
        else:
            self.rates.setdefault(code, 1.0)
        return True

    def remove_currency(self, code):
        """حذف عملة (لا يمكن حذف الأساسية)."""
        code = (code or "").upper().strip()
        if code == self.base_currency or code not in self.currencies:
            return False
        del self.currencies[code]
        self.rates.pop(code, None)
        return True

    def set_rate(self, code, rate):
        """تعيين سعر الصرف (يجب أن يكون > 0)."""
        code = (code or "").upper().strip()
        if code not in self.currencies:
            return False
        try:
            rate = float(rate)
        except (TypeError, ValueError):
            return False
        if rate <= 0:
            return False
        self.rates[code] = rate
        return True

    def get_rate(self, code):
        """سعر الصرف للعملة مقابل الأساس."""
        code = (code or "").upper().strip()
        if code in self.rates:
            return self.rates[code]
        return 1.0 if code == self.base_currency else 0.0

    # ===== التحويل =====

    def convert_to_base(self, amount, code):
        """تحويل مبلغ من عملة إلى العملة الأساسية."""
        rate = self.get_rate(code)
        if rate <= 0:
            return 0.0
        try:
            return float(amount) * rate
        except (TypeError, ValueError):
            return 0.0

    def convert_from_base(self, amount, code):
        """تحويل مبلغ من العملة الأساسية إلى عملة أخرى."""
        rate = self.get_rate(code)
        if rate <= 0:
            return 0.0
        try:
            return float(amount) / rate
        except (TypeError, ValueError):
            return 0.0

    def convert(self, amount, from_code, to_code):
        """تحويل مبلغ من عملة إلى أخرى عبر الأساس."""
        if from_code == to_code:
            return float(amount) if amount is not None else 0.0
        base = self.convert_to_base(amount, from_code)
        return self.convert_from_base(base, to_code)

    # ===== التنسيق =====

    def symbol(self, code=None):
        code = (code or self.base_currency).upper().strip()
        return self.currencies.get(code, {}).get("symbol", code)

    def name(self, code=None, lang="ar"):
        code = (code or self.base_currency).upper().strip()
        meta = self.currencies.get(code, {})
        return meta.get("name_" + ("ar" if lang == "ar" else "en"), code)

    def format(self, amount, code=None, decimals=2):
        """تنسيق مبلغ مع رمز العملة."""
        code = (code or self.base_currency).upper().strip()
        try:
            value = float(amount) if amount is not None else 0.0
            return f"{value:,.{decimals}f} {self.symbol(code)}"
        except (TypeError, ValueError):
            return f"0.00 {self.symbol(code)}"

    # ===== الحفظ والاسترجاع =====

    def to_dict(self):
        return {
            "base_currency": self.base_currency,
            "currencies": self.currencies,
            "rates": self.rates,
        }

    def load_from_dict(self, data):
        """تحميل حالة المحرك من dict (من الإعدادات المحفوظة)."""
        data = data or {}
        base = data.get("base_currency")
        if base in (data.get("currencies") or {}):
            self.base_currency = base
        if data.get("currencies"):
            self.currencies = dict(data["currencies"])
        if data.get("rates"):
            self.rates = dict(data["rates"])
        self.rates.setdefault(self.base_currency, 1.0)
        return True

    def supported_currencies(self):
        return list(self.currencies.keys())

    # ===== التقارير =====

    def report(self, financial_data, target_currency=None):
        """قائمة دخل وميزانية بسيطة محوّلة إلى عملة محددة.

        Returns: قائمة بنود {item, label_key, amount, converted}
        """
        target = (target_currency or self.base_currency).upper().strip()
        rows = []
        for item in REPORT_ITEMS:
            if item in financial_data:
                amount = financial_data.get(item, 0) or 0
                converted = self.convert(amount, self.base_currency, target)
                rows.append({
                    "item": item,
                    "amount": float(amount),
                    "converted": converted,
                    "currency": target,
                })
        return rows


currency_engine = CurrencyEngine()
