# خطة النظام الجبائي الجزائري — Tax Module Plan

## الهدف
إضافة نظام جبائي شامل للمنصة المحاسبية يدعم النظام الجزائري مع إمكانية التحديث السنوي.

## التعديلات المطلوبة

### 1. إصلاح الأزرار البيضاء (style.qss)
**المشكلة:** `QPushButton` الأساسي بدون لون خلفية
**الحل:** إضافة `background-color` و `color` لـ QPushButton الأساسي

### 2. ملف الإعدادات الجبائية (JSON قابل للتحديث)
**الملف:** `modules/tax_config.json`
**الهدف:** تحديث النسب بدون تغيير الكود
**المحتوى:** IBS, TVA, IRG, CNAS, CNAC rates + barèmes

### 3. محرك الضرائب (modules/tax.py)
**الفئة:** `TaxEngine`
**الوظائف:**
- `calculate_ibs(taxable_income, activity_type)` → IBS
- `calculate_tva(taxable_amount, rate_type)` → TVA
- `calculate_irg(annual_salary)` → IRG
- `calculate_cnas(gross_salary)` → CNAS employer + employee
- `calculate_cnac(gross_salary)` → CNAC
- `get_tax_obligations(company_type, month)` → قائمة الالتزامات
- `simulate_all(data)` → ملخص شامل
- `update_config(new_rates)` → تحديث النسب

### 4. قاعدة البيانات (db_schema.py + db_operations.py)
**جداول جديدة:**
- `tax_data` (tax_id, fiscal_year_id, ibs_amount, tva_amount, irg_amount, cnas_amount, cnac_amount, total_taxes, calculated_date)
- `tax_obligations` (obligation_id, company_id, tax_type, due_date, amount, status, paid_date)

### 5. واجهة المستخدم (ui/views/tax_view.py)
**المكونات:**
- حاسبة الضرائب (输入 + حساب)
- عرض النتائج (جدول + بطاقات)
- تقويم الالتزامات (قائمة المواعيد)
- محاكاة ضريبية (what-if analysis)
- زر تحديث النسب (من ملف JSON)

### 6. تحديثات MainWindow
- إضافة sidebar item: "💰 النظام الجبائي"
- إضافة view في QStackedWidget (index 8)
- إضافة shortcut: Ctrl+T
- إضافة للـ retranslate loop

### 7. تحديث i18n.py
- إضافة 50+ مفتاح ترجمة للنظام الجبائي

### 8. تحديث AppState
- إضافة `self.tax_data = {}`
- إضافة `self.tax_summary = {}`
- تحديث `clear()`

### 9. اختبارات (tests/test_tax.py)
- اختبار IBS بأنواع النشاط
- اختبار TVA
- اختبار IRG
- اختبار CNAS
- اختبار تحديث النسب

## الملفات المتأثرة

| الملف | التعديل |
|-------|---------|
| `ui/resources/style.qss` | إصلاح QPushButton الأساسي |
| `modules/tax_config.json` | **جديد** — نسب الضرائب |
| `modules/tax.py` | **جديد** — محرك الضرائب |
| `modules/__init__.py` | إضافة TaxEngine |
| `database/db_schema.py` | إضافة جدول tax_data |
| `database/db_operations.py` | إضافة save/load taxes |
| `database/__init__.py` | إضافة الدوال الجديدة |
| `ui/views/tax_view.py` | **جديد** — واجهة النظام الجبائي |
| `ui/main_window.py` | إضافة TaxView |
| `ui/app_state.py` | إضافة tax fields |
| `ui/resources/i18n.py` | إضافة ترجمات |
| `tests/test_tax.py` | **جديد** — اختبارات |
| `PROJECT_MAP.md` | تحديث |

## الترتيب
1. إصلاح الأزرار (style.qss)
2. tax_config.json
3. modules/tax.py
4. database updates
5. app_state.py
6. i18n.py
7. tax_view.py
8. main_window.py
9. tests
10. PROJECT_MAP.md
