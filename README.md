# المنصة المحاسبية الذكية
# The Smart Accounting Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

منصة محاسبية متكاملة لتحليل البيانات المالية، حساب النسب، تحليل DuPont، التدقيق، وتوليد التقارير.

---

## ✨ المميزات

- 🧮 **محرك حسابات مالية** — نسب السيولة، الربحية، الكفاءة، الاستدانة
- 🔄 **تحليل DuPont** — تحليل معمّق للعائد على حقوق المالكين
- 🔍 **التحقق من البيانات** — ضمان صحة المدخلات قبل المعالجة
- 🔍 **التدقيق والمراجعة** — كشف الأخطاء والتناقضات في البيانات المالية
- 📊 **توليد التقارير** — تقارير مفصّلة بالعربية
- 💾 **قاعدة بيانات SQLite** — حفظ كل التحليلات بشكل منظم
- 📥 **استيراد Excel/CSV** — قراءة البيانات من ملفات خارجية

---

## 📁 بنية المشروع

```
Accounting_Platform/
├── main.py                          # نقطة الدخول الرئيسية
├── config.py                        # الإعدادات
├── requirements.txt                 # المكتبات المطلوبة
├── README.md                        # هذا الملف
├── accounting_platform.db           # قاعدة البيانات SQLite
│
├── database/
│   ├── __init__.py                  # Exports
│   ├── db_connection.py             # إدارة الاتصال بالـ DB
│   ├── db_schema.py                 # إنشاء الجداول
│   └── db_operations.py             # عمليات الحفظ والاسترجاع
│
└── modules/
    ├── __init__.py                  # Exports
    ├── calculations.py              # النسب المالية
    ├── validation.py                # التحقق من البيانات
    ├── analysis.py                  # التحليل المالي (DuPont, ...)
    ├── audit.py                     # التدقيق والمراجعة
    ├── reporting.py                 # توليد التقارير
    └── data_import.py               # استيراد Excel/CSV
```

---

## 🚀 التثبيت والتشغيل

### 1️⃣ المتطلبات
- Python 3.11 أو أحدث
- pip

### 2️⃣ تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 3️⃣ تشغيل البرنامج
**وضع CLI (سطر الأوامر):**
```bash
python main.py
```

**وضع الواجهة الرسومية (PyQt5):**
```bash
python ui/run_ui.py
```

---

## 🖥️ واجهة PyQt5 الرسومية

التطبيق فيه واجهة رسومية كاملة بـ 4 شاشات:

| الشاشة | الوظيفة |
|---|---|
| **📋 إدخال البيانات** | نموذج لإدخال كل البيانات المالية مع أزرار (احسب، حفظ، مسح، استيراد Excel) |
| **📊 النسب المالية** | 12 نسبة موزّعة على كروت ملوّنة (أخضر/أصفر/أحمر) حسب القيمة |
| **📈 تحليل DuPont** | المعادلة + 4 مكونات + تفسير + رأس المال العامل |
| **💾 التحليلات المحفوظة** | استعلام من قاعدة البيانات + تصدير TXT/HTML |

**الميزات:**
- ✅ دعم كامل للغة العربية (RTL)
- ✅ ستايل حديث بألوان احترافية
- ✅ حساب فوري للنسب
- ✅ حفظ مباشر في قاعدة البيانات
- ✅ استيراد من Excel/CSV
- ✅ تصدير تقارير بصيغ متعددة

---

## 📊 أمثلة على الاستخدام

### حساب النسب المالية
```python
from modules import CalculationEngine

financial_data = {
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

calculator = CalculationEngine(financial_data)
ratios = calculator.calculate_all_ratios(financial_data)
calculator.print_ratios(ratios)
```

### تحليل DuPont
```python
from modules import FinancialAnalyzer

analyzer = FinancialAnalyzer(financial_data)
dupont = analyzer.dupont_analysis(
    net_income=15000,
    revenue=200000,
    total_assets=500000,
    equity=300000
)
print(dupont)
```

### حفظ تحليل في قاعدة البيانات
```python
from database import save_analysis

fiscal_year_id = save_analysis(
    company_name="شركة المثال",
    fiscal_year=2024,
    financial_data=financial_data,
    ratios=ratios
)
```

### استيراد من Excel
```python
from modules import DataImporter

importer = DataImporter()
importer.import_from_excel("data.xlsx")
print(importer.get_summary())
```

---

## 🗄️ بنية قاعدة البيانات

| الجدول | الوصف |
|---|---|
| `companies` | بيانات الشركات |
| `fiscal_years` | السنوات المالية |
| `assets` | الأصول (متداولة وغير متداولة) |
| `liabilities` | الالتزامات |
| `equity` | حقوق المالكين |
| `income_statement` | قائمة الدخل |
| `financial_ratios` | النسب المالية المحسوبة |
| `audit_log` | سجل التدقيق |
| `notes` | ملاحظات المدققين |

---

## 🧪 الاختبار

```bash
python main.py
```

المخرجات تتضمن:
- ✅ إنشاء قاعدة البيانات
- ✅ حساب كل النسب المالية
- ✅ التحقق من توازن الميزانية
- ✅ تحليل DuPont
- ✅ تقرير التدقيق
- ✅ توليد التقارير
- ✅ حفظ التحليل في الـ DB

---

## 📝 الترخيص

MIT License — استخدمه براحتك.

---

## 🤝 المساهمة

مرحب بأي تحسين! افتح Issue أو PR.

---

**تم بناء المنصة بـ ❤️ باستخدام Python و VS Code**
