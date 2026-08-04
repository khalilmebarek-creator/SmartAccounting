# المنصة المحاسبية الذكية
# The Smart Accounting Platform

![Version](https://img.shields.io/badge/version-3.1.8-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Tests](https://img.shields.io/badge/tests-1862-green)
![Coverage](https://img.shields.io/badge/coverage-100%25-orange)

منصة محاسبية متكاملة للمؤسسات الصغيرة والمتوسطة في الجزائر — 35 شاشة تفاعلية، امتثال ضريبي جزائري كامل (IBS/TVA/IRG/CNAS/CNAC/VF)، تحليل مالي متقدم (20 نسبة + DuPont + Z-Score)، ورؤى ذكية قائمة على الذكاء الاصطناعي.

---

## ✨ المميزات

- 🖥️ **35 شاشة تفاعلية** — إدخال بيانات، لوحات تحكم، تحليلات، تقارير
- 📊 **20 نسبة مالية + DuPont + Z-Score** — تحليل معمّق للعائد والأداء
- 🧾 **امتثال ضريبي جزائري 100%** — IBS/TVA/IRG/CNAS/CNAC/VF + تقويم + إقرارات (G50/G57/DAS)
- 🤖 **رؤى ذكية (AI)** — تنبؤ 3-6 أشهر + كشف شذوذ + توصيات
- 💾 **حفظ محلي آمن** — SQLite مع تشفير كلمات المرور (PBKDF2) وخزنة AES-256-GCM
- ☁️ **مزامنة سحابية** — Dropbox/OneDrive/Google Drive + نسخ احتياطي تلقائي
- 🌐 **3 لغات** — العربية (RTL) / English / Français
- 📄 **تصدير موحّد** — PDF / Excel / CSV عبر طبقة موحّدة (ui/exporters.py)

---

## 📁 بنية المشروع

```
Accounting_Platform/
├── main.py                          # نقطة الدخول CLI
├── config.py                        # الإصدار والإعدادات (v3.1.8)
├── requirements.txt                 # المكتبات المطلوبة (إنتاج)
├── requirements-dev.txt             # مكتبات التطوير/الاختبار
├── ui/
│   ├── run_ui.py                    # نقطة دخول الواجهة (PyQt5)
│   ├── main_window.py               # النافذة الرئيسية + التحميل الكسول
│   ├── exporters.py                 # طبقة التصدير الموحدة
│   ├── views/                       # 35 شاشة (views)
│   └── resources/fonts/             # الخطوط (Amiri) والأيقونات
├── modules/                         # 44 وحدة (محركات الأعمال + الضرائب)
├── database/                        # SQLite + WAL + تجمّع اتصالات
├── tests/                           # 62 ملفًا / 1800 اختبار
├── docs/                            # التوثيق + الموقع (GitHub Pages)
├── thesis/                          # حزمة مذكرة الماستر + الفيديو التعليمي
├── .github/workflows/ci.yml         # CI (اختبارات + تغطية)
└── installer.iss                    # برنامج التثبيت (Inno Setup)
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

التطبيق فيه واجهة رسومية كاملة بـ **35 شاشة**، منظمة في مجموعات:

| المجموعة | الشاشات (أمثلة) |
|---|---|
| **📋 إدخال البيانات** | إدخال البيانات، لوحة التحكم، النسب المالية، DuPont |
| **📈 التحليل المتقدم** | Z-Score، السيناريوهات، نقطة التعادل، الميزانية، التنبؤ |
| **🧾 النظام الجبائي** | IBS/TVA/IRG/CNAS/CNAC/VF + التقويم الجبائي + الإقرارات |
| **🤖 الذكاء الاصطناعي** | الرؤى الذكية، كشف الشذوذ، التوصيات |
| **🏢 المحاسبة المتقدمة** | دفتر الأستاذ، الفواتير، المخزون، الرواتب، الميزانية |
| **🔧 الإنتاجية** | المزامنة السحابية، الشركات التجريبية، اختبار المستخدمين |

**الميزات:**
- ✅ دعم كامل للغة العربية (RTL) + English + Français
- ✅ اختصارات لوحة مفاتيح كاملة (Ctrl+1..0، F2..F12، Ctrl+T للثيم)
- ✅ حساب فوري للنسب (44ms إقلاع، <100ms تحميل مشهد)
- ✅ حفظ مباشر في SQLite مع تشفير
- ✅ تصدير PDF/Excel عبر طبقة موحّدة

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
pip install -r requirements-dev.txt
python -m pytest tests -q
```

- ✅ **1800 اختباراً** — كلها ناجحة (62 ملفًا)
- ✅ **تغطية الوحدات 100%** (`modules/` — 37 محركًا)
- ✅ **اختبارات أداء** — إقلاع/تحميل/ذاكرة بحدود متسامحة
- ✅ **CI عبر GitHub Actions** — على كل push إلى main

---

## 📝 الترخيص
MIT License — استخدمه براحتك.

---

## 🤝 المساهمة

مرحب بأي تحسين! افتح Issue أو PR.

---

**تم بناء المنصة بـ ❤️ باستخدام Python و VS Code**
