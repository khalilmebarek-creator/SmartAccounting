# مرجع الواجهات البرمجية — المنصة المحاسبية الذكية

> **الإصدار**: v3.1.8 (آخر جلسة ميزات) — **المرجع يتطابق مع `modules/` الحالي (37 وحدة، 325 عملية)**.
> **الترميز**: UTF-8. **اللغة**: Python 3.13+.
> **الاستضافة**: انظر `docs/api/openapi.yaml` + `docs/api/index.html` (Swagger UI) لمعاينة تفاعلية.

---

## 1. نظرة عامة

المنصة تطبيق سطح مكتب (PyQt5) تتكون من 37 وحدة خدمات (`modules/*.py`). كل وحدة تُعرّف **محرّكاً** (class) أو دوال مساعدة، ويُستدعى عبر مثيل مباشر من طبقة الواجهة أو سكربتات الأتمتة/الاختبار. لا توجد شبكة HTTP داخلية — لذلك تحاكي مواصفات OpenAPI المرفقة كل دالة كعملية `POST /api/{module}/{method}` لأغراض التوثيق والمعاينة.

> **ملاحظة استيراد**: الحزمة `modules` تستخدم تحميلاً كسولاً (PEP 562) وتُعرّض قائمة ثابتة عبر `from modules import ...` (مثل `CalculationEngine`, `TaxEngine`). للمحرّكات الأحدث استورد مباشرة من ملفها: `from modules.user_testing import UserTestingEngine`، `from modules.ai_insights import AIInsightsEngine` … إلخ.

### اصطلاحات عامة
- **الأرقام المالية**: تُمرَّر وتُعاد كـ `float` (حسب الوحدة، بعضها يُقرّب لـ 2 منازل).
- **المعدلات**: كسر عشري (مثال: هامش الربح `0.25` = 25%)، والنسب التي تُعرض كنسبة مئوية يُحوّلها المحرّك.
- **التسمية**: `snake_case` للدوال، `CamelCase` للفئات، الثوابت `UPPER_SNAKE`.
- **الاستثناءات**: تُرفع `ValueError` عند معامل غير صالح، و`KeyError` عند كيان مفقود، وتُسجَّل الأخطاء عبر `modules/__init__.py:get_logger(...)`.

### تنسيق الاستجابة
كل عملية ترجع قيمة مباشرة (list/dict/float/str). عند الفشل داخل بعض المحرّكات (التصدير/DB) تُرجع `False` أو `[]` بدلاً من الرفع، حسب تصميم الوحدة — وضّحنا ذلك لكل عملية.

---

## 2. فهرس الوحدات

| الوحدة | الفئة/الدوال | الوصف |
|--------|--------------|-------|
| `calculations.py` | `CalculationEngine` | 21 نسبة مالية + Z-Score |
| `analysis.py` | `FinancialAnalyzer` | الاتجاهات، DuPont، رأس المال العامل، التدفقات |
| `audit.py` | `AuditEngine` | تدقيق القوائم المالية |
| `validation.py` | `DataValidator` | التحقق من صحة البيانات المالية |
| `activity_log.py` | `ActivityLog` | سجل الأنشطة والتغييرات |
| `fraud_detection.py` | `FraudDetector` | كشف التلاعب والتنبيهات |
| `reporting.py` | `ReportGenerator` | توليد/تصدير التقارير |
| `report_templates.py` | `ReportTemplates` | قوالب التقارير المخصصة |
| `print_manager.py` | `PrintManager` | الطباعة HTML |
| `excel_export.py` | `ExcelExporter` | تصدير Excel شامل |
| `forecasting.py` | `FinancialForecaster` | التنبؤ المالي |
| `budget.py` | `BudgetPlanner` | الموازنة والانحرافات |
| `cost_center.py` | `CostCenterAnalyzer` | تحليل مراكز التكلفة |
| `cost_center_profitability.py` | `CostCenterProfitabilityEngine` | ربحية المراكز |
| `breakeven.py` | `BreakEvenAnalyzer` | نقطة التعادل |
| `cashflow.py` | `CashFlowStatement` | التدفقات النقدية |
| `comparative.py` | `ComparativeAnalyzer` | المقارنة عبر السنوات |
| `benchmarks.py` | `BenchmarkAnalyzer` | المعايير والمقارنات القطاعية |
| `scenarios.py` | `ScenarioAnalyzer` | سيناريوهات + حساسية |
| `advanced_dashboard.py` | `AdvancedDashboardEngine` | لوحة تحكم متقدمة |
| `ai_insights.py` | `AIInsightsEngine` | الرؤى الذكية |
| `tax.py` | `TaxEngine` | النظام الجبائي الجزائري |
| `tax_reminders.py` | `TaxReminderManager` | التذكيرات الجبائية |
| `tax_reports.py` | `TaxDeclarationGenerator` | إقرارات G50/G57/DAS |
| `bank_sync.py` | `BankSyncManager` | كشوف البنوك والمطابقة |
| `data_import.py` | `DataImporter` | استيراد Excel/CSV |
| `csv_import.py` | `CSVImporter` | كشف الصيغ والترميز |
| `currency.py` | `CurrencyEngine` | العملات وأسعار الصرف |
| `cloud_sync.py` | `CloudSyncEngine` + `encrypt_payload/decrypt_payload` | المزامنة والنسخ المشفّر |
| `demo_data.py` | `DemoData` | الشركات التجريبية |
| `demo_templates.py` | 5 دوال | قوالب CSV تجريبية |
| `user_manager.py` | `UserManager` + 3 دوال | المستخدمون والأدوار و2FA |
| `user_testing.py` | `UserTestingEngine` + `satisfaction_level` | اختبار المستخدمين |
| `update_checker.py` | `UpdateChecker` + 5 دوال | التحديثات والاسترجاع |
| `scheduled_backup.py` | `ScheduledBackup` | النسخ المجدول |
| `backup.py` | `BackupManager` | النسخ الاحتياطي |
| `email_notifier.py` | `EmailNotifier` | التنبيهات البريدية |

---

## 3. الوحدات الأساسية (Core Services)

### 3.1 `modules/calculations.py` — النسب المالية

**الفئة**: `CalculationEngine` — طرقها كلها `@staticmethod` عملياً (تُستدعى على المثيل).

| الدالة | المعاملات | الإرجاع | الوصف |
|--------|-----------|---------|-------|
| `current_ratio` | current_assets, current_liabilities | float | نسبة التداول |
| `quick_ratio` | current_assets, inventory, current_liabilities | float | النسبة السريعة |
| `cash_ratio` | cash, current_liabilities | float | نسبة النقدية |
| `gross_profit_margin` | gross_profit, revenue | float (0-1) | هامش الربح الإجمالي |
| `operating_profit_margin` | operating_income, revenue | float (0-1) | هامش الربح التشغيلي |
| `net_profit_margin` | net_income, revenue | float (0-1) | هامش الربح الصافي |
| `roa` | net_income, total_assets | float | العائد على الأصول |
| `roe` | net_income, equity | float | العائد على حقوق الملكية |
| `asset_turnover` | revenue, total_assets | float | معدل دوران الأصول |
| `receivables_turnover` | revenue, average_receivables | float | دوران الذمم المدينة |
| `days_sales_outstanding` | receivables_turnover | float | أيام تحصيل الذمم |
| `inventory_turnover` | cost_of_goods_sold, average_inventory | float | دوران المخزون |
| `days_inventory_outstanding` | inventory_turnover | float | أيام بقاء المخزون |
| `payables_turnover` | cost_of_goods_sold, average_payables | float | دوران الذمم الدائنة |
| `days_payable_outstanding` | payables_turnover | float | أيام سداد الذمم |
| `operating_cycle` | days_inventory_outstanding, days_sales_outstanding | float | دورة التشغيل |
| `cash_conversion_cycle` | dio, dso, dpo | float | دورة التحويل النقدي |
| `debt_to_equity` | total_liabilities, equity | float | الديون إلى الملكية |
| `debt_ratio` | total_liabilities, total_assets | float | نسبة الدين |
| `equity_ratio` | equity, total_assets | float | نسبة الملكية |
| `calculate_all_ratios` | financial_data (dict) | dict | يحسب كل النسب من قواميس الأصول/الخصوم/الإيرادات |
| `z_score` | working_capital, retained_earnings, ebit, market_value_equity, book_value_debt, sales, total_assets | float | درجة Altman Z-Score |
| `print_ratios` | ratios (dict) | None | طباعة النسب للطرفية |

**الأخطاء**: القسمة على صفر تُعيد `0.0` وتُسجَّل تحذيراً. القيم السالبة مسموحة (تُحتسب) لكن `validation.py` ينبّه.

**مثال**:
```python
from modules import CalculationEngine
eng = CalculationEngine()
ratios = eng.calculate_all_ratios({
    "current_assets": 500000, "inventory": 200000, "current_liabilities": 250000,
    "cash": 80000, "gross_profit": 800000, "operating_expenses": 400000,
    "operating_income": 400000, "net_income": 300000, "revenue": 2000000,
    "total_assets": 1500000, "equity": 700000, "cost_of_goods_sold": 1200000,
    "average_receivables": 250000, "average_inventory": 180000,
    "average_payables": 150000, "total_liabilities": 800000,
})
print(ratios["current_ratio"])      # 2.0
print(eng.z_score(300000, 120000, 250000, 900000, 800000, 2000000, 1500000))
```

---

### 3.2 `modules/analysis.py` — المحلل المالي

**الفئة**: `FinancialAnalyzer`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `trend_analysis` | data_series (list[dict]) | dict: نسبة النمو، الانحراف، أفضل/أسوأ فترة |
| `comparative_analysis` | company_ratios, industry_average | dict: الفجوات بالنسبة المئوية |
| `dupont_analysis` | net_income, revenue, total_assets, equity | dict: ROE = (هامش×دوران×مضاعف) |
| `dupont_waterfall` | net_profit_margin, asset_turnover, equity_multiplier | list: بيانات شلال DuPont |
| `dupont_industry_comparison` | dupont (dict), sector_code | dict مقارنة ROE مع القطاع |
| `dupont_recommendations` | dupont, sector_code | list[str] توصيات |
| `working_capital_analysis` | current_assets, current_liabilities, inventory | dict: رأس المال العامل والاحتياجات |
| `cash_flow_analysis` | operating_cf, investing_cf, financing_cf | dict: صافي التدفق والتحليل |
| `generate_report` | — | str نص تقرير شامل |
| `get_summary` | — | dict ملخص |

**مثال**:
```python
from modules import FinancialAnalyzer
fa = FinancialAnalyzer(data)          # data: dict مسطّح من حقول القوائم المالية
dup = fa.dupont_analysis(300000, 2000000, 1500000, 700000)
# dup["roe"] = 42.86 (نسبة مئوية)  →  300000/2000000 × 2000000/1500000 × 1500000/700000 × 100
```

---

### 3.3 `modules/audit.py` — التدقيق

**الفئة**: `AuditEngine`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `check_balance_sheet` | assets, liabilities, equity | dict تقرير توازن `A = L + E` |
| `check_income_statement` | revenue, cogs, operating_expenses, net_income | dict مطابقة صافي الدخل |
| `check_negative_values` | financial_data (dict) | dict قيم سالبة مشبوهة |
| `check_ratios_reasonableness` | ratios (dict) | dict نسب خارج الحدود الطبيعية |
| `check_cash_flow_consistency` | operating_cf, net_income | dict تناسق التدفق التشغيلي |
| `check_inventory_sanity` | inventory, cogs | dict فحص منطقية المخزون |
| `generate_audit_report` | — | str تقرير التدقيق |
| `get_audit_summary` | — | dict ملخص |
| `clear_audit` | — | None مسح النتائج |

---

### 3.4 `modules/validation.py` — التحقق

**الفئة**: `DataValidator`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `validate_non_negative_number` | value, field_name | bool (False مع رفع/تسجيل خطأ) |
| `validate_financial_statement` | data (dict) | dict بعلامات صح/خطأ لكل قسم |
| `get_errors` | — | list[str] |
| `get_warnings` | — | list[str] |
| `print_report` | — | None طباعة الملخص |

---

### 3.5 `modules/reporting.py` — التقارير

**الفئة**: `ReportGenerator`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `generate_balance_sheet_report` | assets, liabilities, equity | str (نص منسق) |
| `generate_income_statement_report` | revenue, cogs, expenses, net_income | str |
| `generate_financial_ratios_report` | ratios (dict) | str |
| `generate_comprehensive_report` | balance_sheet, income_statement, ratios, analysis | str تقرير شامل |
| `generate_dupont_report` | dupont, waterfall, industry, recommendations | str |
| `generate_scenario_report` | scenarios, comparison, sensitivity | str |
| `export_report_to_file` | report_content, filename | bool |
| `export_to_pdf` | report_content, filename | bool (يستخدم fpdf/weasyprint حسب التوفّر) |
| `export_to_excel` | filename, financial_data, ratios, tax_data | bool |

---

### 3.6 `modules/tax.py` — النظام الجبائي الجزائري

**الفئة**: `TaxEngine` — يُقرأ من `modules/tax_config.json`.

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `reload_config` | config_path | bool |
| `get_config_year` | — | int |
| `get_activity_types` | — | list[str] (تجاري/خدمات/مستقل/صناعي...) |
| `calculate_ibs` | taxable_income, activity_type | float ضريبة الأرباح |
| `calculate_ibs_acomptes` | taxable_income, activity_type | dict أقساط 3/6/11 |
| `calculate_ibs_balance` | taxable_income, activity_type, acomptes_paid | float الباقي |
| `get_tva_rates` | — | dict (19% عام / 9% مخفّض / 0% معفى) |
| `calculate_tva` | amount_excl_tax, rate_type | dict TVA + الإجمالي شامل |
| `calculate_tva_collection` | tva_collected, tva_paid | float مستحق |
| `calculate_tva_refund` | tva_collected, tva_paid, previous_credit | float رصيد/استرداد |
| `calculate_irg` | annual_taxable_salary | float جدول IRG المقطوع |
| `calculate_cnas` | gross_salary | dict حصة الموظف (9%) والشريك (26%) |
| `calculate_cnac` | gross_salary | dict حصص التأمين |
| `calculate_versement_forfaitaire` | monthly_payroll, is_construction | float |
| `calculate_payroll` | gross_salary, is_construction | dict التفصيل الكامل |
| `build_das_data` | monthly_payroll, number_of_employees, avg_salary | dict |
| `get_obligations` | month, activity_type, monthly_payroll, annual_turnover | list التزامات الشهر |
| `simulate` | revenue, cogs, operating_expenses, total_assets, total_liabilities, equity, number_of_employees, avg_salary, activity_type, is_construction | dict محاكاة ضريبية كاملة |
| `get_ibs_rate_label` | activity_type | str |
| `get_tva_items` | — | list عناصر TVA |
| `get_tva_exemptions` | — | list الإعفاءات |
| `format_currency` | amount | str بتنسيق دج |

**مثال**:
```python
from modules import TaxEngine
tax = TaxEngine()
ibs = tax.calculate_ibs(2_000_000, "تجاري")          # IBS 19%
tva = tax.calculate_tva(1_000_000, "standard")       # 19% → 190,000
pay = tax.calculate_payroll(120_000, False)          # تفصيل CNAS/CNAC/IRG
print(ibs, tva["tva_amount"], pay["net_salary"])
```

---

### 3.7 `modules/scenarios.py` — السيناريوهات

**الفئة**: `ScenarioAnalyzer`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `build_scenarios` | best (dict), worst (dict) | dict: مثالي/طبيعي/أسوأ |
| `sensitivity_analysis` | variable (str), steps (int) | list نقاط الحساسية |
| `tornado_analysis` | range_pct (float) | dict بيانات Tornado |
| `compare_scenarios` | scenarios (dict) | dict مقارنة |
| `save_scenarios` *(static)* | scenarios, filepath | bool JSON |
| `load_scenarios` *(static)* | filepath | dict |

---

### 3.8 `modules/ai_insights.py` — الرؤى الذكية (pandas/numpy فقط)

**الفئة**: `AIInsightsEngine`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `forecast` | series (list), months (int), method ("linear"/"moving_average"/"exponential") | dict قيم + فترات ثقة 95% |
| `forecast_all` | revenue, expenses, profit, months, method | dict تنبؤ للمقاييس الثلاثة |
| `detect_anomalies` | series, threshold | list مؤشرات الشذوذ (z-score) |
| `detect_transaction_anomalies` | transactions, threshold | list شذوذ IQR |
| `detect_ratio_anomalies` | current, previous, threshold | list |
| `unexpected_profit_loss` | profit_series | list انعكاسات غير متوقعة |
| `patterns` | series, periods_per_year | dict اتجاه/موسمية/دورات/مخاطر |
| `recommendations` | ratios, cash, monthly_expenses, revenue_growth | list[str] توصيات |
| `alerts` | forecasts, anomalies, patterns, ratios, recommendations | list تنبيهات (خطر/تحذير/فرصة/إجراء) |
| `generate_insights` | revenue_history, expense_history, profit_history, transactions, ratios, months, method | dict التقرير الكامل |

---

### 3.9 `modules/benchmarks.py` — المعايير المرجعية

**الفئة**: `BenchmarkAnalyzer`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `get_sectors_list` | — | list القطاعات |
| `compare_with_sector` | company_ratios, sector_code | dict مقارنة |
| `get_radar_data` | company_ratios, sector_code | dict رادار |
| `suggest_improvements` | company_ratios, sector_code | list[str] |
| `get_strengths_weaknesses` | company_ratios, sector_code | dict نقاط قوة/ضعف |
| `compare_with_competitors` | company_ratios, sector_code, competitors | dict (من جدول `competitor_data`) |
| `get_trend_data` | history, sector_code | dict اتجاه عبر السنوات |
| `get_international_standards` | sector_code | dict المعايير الدولية |

---

### 3.10 `modules/cost_center_profitability.py` — ربحية المراكز

**الفئة**: `CostCenterProfitabilityEngine`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `define_centers` | centers (list[dict]) | None |
| `set_standards` | target_margin_pct | None |
| `allocate` | indirect_total, method ("revenue"/"headcount"/"area"/"equal") | dict توزيع غير مباشر |
| `get_summary` | — | dict ملخص |
| `rank_by_profitability` | — | list ترتيب |
| `rank_by_profit` | — | list ترتيب ربح |
| `compare_previous` | previous_data | dict مقارنة سابقة |
| `compare_budget` | budget_data | dict مقابل الميزانية |
| `compare_standards` | — | dict مقابل المعيار |
| `trend_analysis` | periods (list) | dict اتجاه متعدد الفترات |
| `variance_analysis` | budget_data | dict انحرافات |
| `get_reports` | — | dict تقارير |
| `get_recommendations` | — | list[str] توصيات |
| `analyze` | centers, indirect_total, method, target_margin_pct | dict الكل دفعة واحدة |

---

### 3.11 `modules/advanced_dashboard.py` — لوحة التحكم المتقدمة

**الفئة**: `AdvancedDashboardEngine`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `status_for_value` | key, value | str حالة لونية (جيد/متوسط/حرج) |
| `compute_kpis` | financial_data, ratios | list بطاقات KPI |
| `revenue_trend` | financial_data, period ("monthly"/"quarterly") | dict |
| `expense_breakdown` | financial_data | dict |
| `profitability_trend` | history | dict |
| `ratios_radar` | ratios, sector_code | dict |
| `alerts` | financial_data, ratios, sector_code | list تنبيهات (شذوذ/أداء/معايير/إجراءات) |
| `default_layout` | — | dict تخطيط |
| `build_layout` | widgets, kpis, color, name | dict |
| `health_score` | kpis | float درجة صحية 0-100 |
| `export_data` | financial_data, ratios, sector_code | dict بيانات التصدير |

---

### 3.12 `modules/currency.py` — العملات

**الفئة**: `CurrencyEngine` — أساسية العملة الافتراضية DZD.

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `set_base_currency` | code | None |
| `add_currency` | code, name_ar, symbol, rate | bool |
| `remove_currency` | code | bool |
| `set_rate` | code, rate | bool |
| `get_rate` | code | float |
| `convert_to_base` | amount, code | float |
| `convert_from_base` | amount, code | float |
| `convert` | amount, from_code, to_code | float |
| `symbol` | code | str |
| `name` | code, lang | str |
| `format` | amount, code, decimals | str |
| `to_dict` / `load_from_dict` | — / data | dict / None |
| `supported_currencies` | — | list |
| `report` | financial_data, target_currency | dict تقرير متعدد العملات |

---

### 3.13 `modules/cloud_sync.py` — المزامنة والنسخ الاحتياطي

**دوال**: `encrypt_payload(payload, passphrase) → str`، `decrypt_payload(encoded, passphrase) → dict` (AES-GCM).

**الفئة**: `CloudSyncEngine`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `settings` / `set_setting` | — / key, value | dict / None |
| `get_passphrase` / `set_passphrase` | — / passphrase | str / None |
| `history` / `clear_history` | limit / — | list / None |
| `list_destinations` / `add_destination` / `remove_destination` / `set_destination_auto` | — / name, path, auto / dest_id / dest_id, auto | list / bool / bool / bool |
| `read_snapshot` | path, passphrase | dict |
| `list_snapshots` | directory | list |
| `push` | state, dest_id, passphrase | dict snapshot + checksum |
| `pull` | state, dest_id, snapshot_name, passphrase | dict |
| `backup_local` | state, passphrase | str مسار |
| `restore_backup` | state, snapshot_name, passphrase | bool |
| `restore_from_file` | state, path, passphrase | bool |
| `auto_backup_due` | — | bool |
| `run_auto_backup` | state | bool |
| `status` | — | dict الحالة |

---

### 3.14 `modules/user_testing.py` — اختبار المستخدمين

**دالة**: `satisfaction_level(score) → str` (poor/fair/good/excellent حسب `SATISFACTION_LEVELS`).

**الفئة**: `UserTestingEngine` — ثوابت `USER_GROUPS` (4)، `SCENARIOS` (5)، `FEEDBACK_CATEGORIES` (5)، `PRIORITIES` (4)، `STATUSES` (4).

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `create_session` | name, tester_name, user_group, scenario, environment, notes | dict الجلسة |
| `get_session` / `list_sessions` / `delete_session` | session_id / — / session_id | dict / list / bool |
| `add_feedback` | session_id, category, comment, rating, user_group, scenario, priority, title, status | dict |
| `update_feedback` | session_id, feedback_id + حقول اختيارية | dict (ValueError لتصنيف/مجموعة/سيناريو غير صالح) |
| `delete_feedback` | session_id, feedback_id | bool |
| `list_feedback` | session_id, category, user_group, status | list |
| `satisfaction_score` | session_id | dict: overall (round 2), count, level, by_category, by_user_group, by_scenario |
| `feedback_report` / `issue_list` / `enhancement_requests` / `summary_text` | session_id | dict / list / list / str |
| `export_json` / `import_json` | path / path | bool / int (عدد المستورد) |
| `to_dict` *(static)* | session | dict |
| `save_session_db` / `load_session_db` / `list_session_ids_db` / `delete_session_db` | session_id | bool / bool / list / bool — عبر `get_connection()` |
| `export_excel` / `export_csv` / `export_pdf` | path, session_id | bool |
| `build_demo_data` | — | int عدد الجلسات |

---

### 3.15 `modules/user_manager.py` — المستخدمون

**دوال**: `validate_password_strength(password) → dict`، `validate_email(email) → bool`، `generate_otp(length) → str`.

**الفئة**: `UserManager`

| الدالة | المعاملات | الإرجاع |
|--------|-----------|---------|
| `login` | email, password | bool |
| `verify_otp` | username, otp_code | bool |
| `generate_and_send_otp` | email | bool |
| `enable_two_factor` | username, enabled | bool |
| `logout` | — | None |
| `register` | email, password, display_name, role | bool |
| `change_password` | username, old_password, new_password | bool |
| `reset_password_by_email` | email, new_password | bool |
| `request_password_reset` | email | str token |
| `confirm_password_reset` | email, token, new_password | bool |
| `needs_password_change` | — | bool |
| `delete_user` | username | bool |
| `get_current_user` | — | dict |
| `is_admin` / `has_permission` | — / permission | bool |
| `get_role_permissions` | role | list |
| `is_logged_in` | — | bool |
| `get_all_users` | — | list |

---

### 3.16 `modules/demo_data.py` و `demo_templates.py` — الشركات التجريبية

**الفئة**: `DemoData` — ثوابت/قوائم: `list_companies()` (4 شركات: تجارية/خدمات/إنتاج/استيراد-تصدير)، `get_financial_data(company_id)`، `get_company_name(company_id)`، `get_data()`.

**دوال** `demo_templates.py`:
- `write_financial_template(path)` / `write_transactions_template(path)` — قوالب CSV فارغة متوافقة مع `DataImporter`.
- `write_templates(directory)` — يكتب القالبين.
- `export_company_csv(directory, company_id)` — بيانات الشركة CSV.
- `generate_demo_reports(company_id)` — تقارير مُعدّة (ميزانية/دخل/نسب).

---

## 4. الوحدات الداعمة (Support Services) — مرجع مختصر

### 4.1 `modules/activity_log.py` — `ActivityLog`
`set_current_user(username)` · `flush()` · `log(action, details, category, user, old_value, new_value, ip_address)` · `log_change(entity, entity_id, field, old_value, new_value, user)` · `log_auth(action, username, success, ip)` · `log_export(format_type, filename, user)` · `log_backup(action, filename)` · `get_entries(limit, category, user, action) → list` · `get_summary() → dict` · `export_audit_trail(filename) → bool` · `clear()`.

### 4.2 `modules/fraud_detection.py` — `FraudDetector`
`flush()` · `check_data_change(field, old_value, new_value, user)` · `check_balance_sheet(data, user)` · `check_rapid_edits(user)` · `check_after_audit(field, new_value, user)` · `mark_audit_approved()` / `mark_audit_reset()` · `check_tax_consistency(financial_data, tax_summary)` · `get_alerts(severity_filter, limit) → list` · `get_alert_count() → int` · `clear_alerts()`.

### 4.3 `modules/backup.py` — `BackupManager`
`backup(backup_path) → bool` · `auto_backup(label)` · `restore(backup_path) → bool` · `list_backups(directory) → list` · `export_all_to_json(directory) → str` · `import_from_json(json_file) → int`.

### 4.4 `modules/scheduled_backup.py` — `ScheduledBackup`
`start()` / `stop()` / `is_running()` · `manual_backup() → bool` · `get_backups() → list` · `restore_backup(backup_name) → bool` · `get_settings() → dict` / `update_settings(updates) → bool`.

### 4.5 `modules/email_notifier.py` — `EmailNotifier`
`configure(smtp_server, smtp_port, sender_email, sender_password, manager_email)` · `is_configured() → bool` · `send_alert(alert) → bool` · `send_summary(alert_count, high_alerts) → bool`.

### 4.6 `modules/forecasting.py` — `FinancialForecaster`
`project_revenue(growth_rates) → list` · `project_income_statement(growth_rates, cogs_pct, opex_pct) → list` · `scenario_analysis(scenarios) → dict` · `cagr(beginning_value, ending_value, years) → float`.

### 4.7 `modules/budget.py` — `BudgetPlanner`
`create_annual_budget(categories) → bool` · `get_summary() → dict` · `get_alerts(threshold_pct) → list` · `variance_analysis() → dict` · `export_json() → str`.

### 4.8 `modules/cost_center.py` — `CostCenterAnalyzer`
`define_centers(centers)` · `get_summary() → dict` · `rank_by_efficiency() → list` · `rank_by_profitability() → list` · `get_recommendations() → list`.

### 4.9 `modules/breakeven.py` — `BreakEvenAnalyzer`
`calculate(fixed_costs, variable_cost_ratio, unit_price, unit_variable_cost) → dict` (نقطة التعادل بالوحدات/الدينار) · `sensitivity_analysis(fixed_costs, variable_cost_ratio_range, base_revenue) → dict`.

### 4.10 `modules/cashflow.py` — `CashFlowStatement`
`calculate(financial_data, prev_financial_data) → dict` (تشغيلي/استثماري/تمويلي) · `generate_report(results) → str`.

### 4.11 `modules/comparative.py` — `ComparativeAnalyzer`
`get_comparison() → dict` · `generate_report() → str` (يستخدم `.get(item, 0)` مع بيانات ناقصة — لا يرمي KeyError).

### 4.12 `modules/breakeven.py` … `modules/tax_reports.py` — انظر 4.13.

### 4.13 `modules/tax_reminders.py` — `TaxReminderManager`
`get_upcoming_reminders(days_ahead) → list` · `acknowledge_reminder(reminder_id) → bool` · `add_custom_reminder(name, due_date, description, tax_type) → dict` · `remove_custom_reminder(index) → bool` · `get_calendar_summary(year) → dict`.

### 4.14 `modules/tax_reports.py` — `TaxDeclarationGenerator`
`get_declaration_types() → list` (G50/G57/DAS) · `get_declaration_info(decl_type)` · `build_header(company_info, fiscal_year, period_label)` · `generate_g50(header, month, year, monthly_turnover, tva_collected, tva_deductible, previous_credit)` · `generate_g57(header, taxable_income, acomptes_paid, activity_type, reinvestment)` · `generate_das(header, monthly_payroll, number_of_employees, avg_salary)` · `generate(decl_type, data)` · `render_text(declaration)` · `export_pdf(declaration, filename) → bool` · `export_excel(declaration, filename) → bool`.

### 4.15 `modules/bank_sync.py` — `BankSyncManager`
`get_bank_list() → list` · `detect_bank(filepath) → str` · `import_bank_statement(filepath, bank_code, account_id) → dict` · `reconcile(bank_transactions, book_transactions, tolerance) → dict`.

### 4.16 `modules/data_import.py` — `DataImporter`
`import_from_excel(file_path, sheet_name) → bool` · `import_from_csv(file_path) → bool` · `get_data() → list` · `get_columns() → list` · `get_row_count() → int` · `validate_data() → dict` · `get_summary() → dict` · `export_to_database(db_connection, table_name) → bool` · `filter_data(column, value)` · `sort_data(column, ascending)`.

### 4.17 `modules/csv_import.py` — `CSVImporter`
`detect_delimiter(filepath) → str` · `detect_file_type(filepath) → str` · `auto_map_columns(headers, lang) → dict` · `read_csv(filepath, encoding, delimiter, has_header)` · `read_excel(filepath, sheet_name)` · `import_data(filepath, lang, encoding, on_row) → int` · `get_preview(rows, headers, max_rows)`.

### 4.18 `modules/report_templates.py` — `ReportTemplates`
`get_template(template_id)` · `get_all_templates() → list` · `create_template(template_id, template_data) → bool` · `update_template(template_id, updates) → bool` · `delete_template(template_id) → bool` · `get_sections_for_template(template_id)` · `generate_report_header(template_id, company_name)` · `generate_report_footer()`.

### 4.19 `modules/print_manager.py` — `PrintManager`
`print_html(html_content, title, landscape) → bool` · `generate_report_html(title, sections, company_name, fiscal_year) → str` · `print_financial_report(company_name, fiscal_year, data) → bool` · `save_and_print_html(html_content, title)` · `cleanup()`.

### 4.20 `modules/excel_export.py` — `ExcelExporter`
`export_full_report(filepath, data, company_name, fiscal_year, ratios, tax_data, budget_data, cashflow_data, cost_centers, comparative_data) → bool` · `export_comparison(data, filepath, title) → bool`.

### 4.21 `modules/update_checker.py` — `UpdateChecker` + دوال
`check_for_updates(timeout) → dict` · `is_rollout_eligible() → bool` · `get_update_info() → dict` — ودوال مساعدة: `check_updates_async(callback, timeout)`، `download_installer(installer_url, progress_callback, output_path, chunk_size)`، `backup_current_executable(exe_path)`، `has_rollback_backup(exe_path)`، `restore_previous_executable(exe_path)`، `cleanup_rollback(exe_path)`.

---

## 5. رموز الخطأ ومعالجتها

| الخطأ | متى يحدث | مثال المعالجة |
|-------|----------|---------------|
| `ValueError` | معامل خارج النطاق أو غير صالح (تصنيف/مجموعة/سيناريو/قيمة سلبية غير مسموحة) | قبضه وأظهر رسالة موحّدة عبر `ui/widgets/messages.py` |
| `KeyError` | جلسة/كيان/قسم مفقود (`get_session("999")`) | تحقق بـ`in` أو قبضه |
| `OSError` | ملف/مسار غير قابل للكتابة أثناء التصدير | تعيد معظم دوال التصدير `False` وتُسجّل |
| `RuntimeError` | انهيار قاعدة البيانات/الاتصال (`get_connection` يفشل) | تعيد دوال DB قيماً افتراضية (False/[]) |

> **قاعدة موحّدة**: دوال التصدير (`export_*`) وكل قنوات DB لا ترفع عادةً — تعيد `bool`/`list` وتُسجّل الخطأ عبر `get_logger(module).error(...)`.

---

## 6. أمثلة استخدام متكاملة

### 6.1 رحلة مالية كاملة (إدخال → نسب → تحليل → تقرير)
```python
from modules import (DataValidator, CalculationEngine, FinancialAnalyzer, AuditEngine, ReportGenerator)

data = {
    "current_assets": 500000, "inventory": 200000, "current_liabilities": 250000,
    "cash": 80000, "gross_profit": 800000, "operating_expenses": 400000,
    "operating_income": 400000, "net_income": 300000, "revenue": 2000000,
    "total_assets": 1500000, "equity": 700000, "cost_of_goods_sold": 1200000,
    "average_receivables": 250000, "average_inventory": 180000,
    "average_payables": 150000, "total_liabilities": 800000,
}
validator = DataValidator()
assert validator.validate_financial_statement(data)          # توازن A = L + E ✓

ratios = CalculationEngine().calculate_all_ratios(data)
analysis = FinancialAnalyzer(data).dupont_analysis(300000, 2000000, 1500000, 700000)
audit = AuditEngine().check_balance_sheet(1500000, 800000, 700000)   # متوازنة ✓

rg = ReportGenerator("شركة التجربة", "2026")
report = rg.generate_comprehensive_report(1500000, data, ratios, analysis)
rg.export_to_pdf(report, "report.pdf")
```

### 6.2 اختبار مستخدمين + تصدير
```python
from modules.user_testing import UserTestingEngine

ut = UserTestingEngine()
s = ut.create_session("اختبار", tester_name="سارة", user_group="manager", scenario="analysis")
ut.add_feedback(s["id"], "bugs", "تعذر تصدير PDF", rating=2, priority="high")
print(ut.satisfaction_score(s["id"])["overall"])   # 2.0
ut.export_json("sessions.json")
assert ut.import_json("sessions.json") > 0
```

### 6.3 محاكاة ضريبية
```python
from modules import TaxEngine
res = TaxEngine().simulate(
    revenue=8_000_000, cogs=5_000_000, operating_expenses=1_500_000,
    total_assets=12_000_000, total_liabilities=6_000_000, equity=6_000_000,
    number_of_employees=12, avg_salary=90_000, activity_type="تجاري", is_construction=False,
)
print(res["ibs"], res["tva"], res["cnas_total"])
```

---

*آخر تحديث: 2026-08-01 — جلسة التوثيق الشامل (v3.1.8).*
