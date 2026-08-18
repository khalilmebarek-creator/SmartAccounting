# PROJECT_MAP.md — المنصة المحاسبية الذكية
> آخر تحديث: 2026-08-18 | الإصدار: v3.2.0

---

## SYSTEM_FLOW — رحلة المستخدم

```
1. شاشة الدخول → LoginView (تسجيل + دخول + استعادة كلمة المرور)
2. MainWindow (sidebar + stacked views + شريط حالة)
3. إدخال البيانات المالية → DataEntryView
4. حساب النسب → CalculationEngine → AppState
5. لوحة التحكم → DashboardView (4 رسوم بيانية)
6. تحليل DuPont + رأس المال العامل → AnalysisView
7. النسب المالية (20 نسبة + Z-Score) → RatiosView
8. التدقيق المالي → AuditView (7 فحوصات)
9. النظام الجبائي الجزائري → TaxView (3 تبويبات)
10. المعايير المرجعية (7 قطاعات) → BenchmarksView (معايير + منافسون + اتجاه)
11. التقويم الجبائي والتذكيرات → TaxCalendarView
12. التقارير → ReportsView (TXT/HTML/Excel/PDF)
13. المصادقة الثنائية + الأمان → SecurityView
14. إدارة المستخدمين (4 أدوار) → UserManagementView
15. الشات الذكي (AI Chat) → ChatView
16. تحليل السيناريوهات → ScenariosView
17. التنبؤات المالية → ForecastingView
18. تحليل التعادل → BreakevenView
19. استيراد/تصدير → ImportExportView
20. فحص التحديثات → UpdateChecker (GitHub Pages)
21. الإعدادات (لغة/ثيم/API) → SettingsView
22. الإشعارات → NotificationView
23. لوحة التحكم المتقدمة (6 KPI + رسوم + تنبيهات + تخصيص) → AdvancedDashboardView
24. تعدد العملات (عملات + أسعار صرف + محول + تقرير متعدد العملات) → CurrencyView
25. المزامنة السحابية والنسخ الاحتياطي (وجهات + نسخ تلقائي + استرجاع مشفّر + سجل) → CloudSyncView
26. الشركات التجريبية (تجارية/خدمات/إنتاج/استيراد-تصدير) + معاملات شهرية + تقارير مُعدّة + قوالب CSV → DemoDataView
27. دفتر الأستاذ العام (قيود يومية + دفتر أستاذ + ميزان مراجعة) → LedgerView
28. العملاء والموردون (شركاء + معاملات + أرصدة + تقادم الديون) → PartnersView
29. الفواتير (بيع/شراء + عناصر + TVA + حالات) → InvoicingView
30. المخزون (عناصر + حركات + أسهم + تنبيهات) → InventoryView
31. الرواتب الجزائرية (موظفون + CNAS/IRG + كشوفات) → PayrollView
32. الميزانية (بنود + مقارنة بالفعلي + انحراف) → BudgetingView
```

---

## MODULE MAP — حالة كل مكون

### ✅ CORE (100% — مكتمل)
| المكون | الملفات | الحالة |
|--------|---------|--------|
| config | config.py (v3.1.2) | ✅ |
| database | config.py (v3.1.2) | ✅ |
| database | db_connection.py, db_schema.py (15 tables), db_operations.py | ✅ |
| calculations | modules/calculations.py (20 ratios + Z-Score) | ✅ |
| analysis | modules/analysis.py (DuPont + Waterfall + Industry Compare + Recommendations, Trends, WC, CashFlow) | ✅ |
| audit | modules/audit.py (8 checks) | ✅ |
| tax_engine | modules/tax.py + tax_config.json + tax_config.json + tax_years.py + config_years/ + tax_reminders.py + tax_reports.py | ✅ |
| tax_reports | modules/tax_reports.py (قوالب الإقرارات G50/G57/DAS + تصدير PDF/Excel) | ✅ |
| benchmarks | modules/benchmarks.py (7 قطاعات × 10 نسب + أفضل الممارسات + دولي + منافسون + اتجاه) | ✅ |
| advanced_dashboard | modules/advanced_dashboard.py (6 KPI + 4 رسوم + تنبيهات/إجراءات + تخطيطات مخصصة + تصدير) | ✅ |
| update_checker | modules/update_checker.py (GitHub Pages) | ✅ |
| scenarios | modules/scenarios.py (3 سيناريوهات + حساسية + Tornado + JSON) | ✅ |
| ai_insights | modules/ai_insights.py (تنبؤ 3-6 أشهر + فترات ثقة + كشف شذوذ + أنماط + توصيات + تنبيهات) | ✅ |
| cost_center_profitability | modules/cost_center_profitability.py (مراكز + توزيع مباشر/غير مباشر + ربحية + مقارنات + اتجاه + تقارير) | ✅ |
| currency | modules/currency.py (7 عملات افتراضية + أسعار صرف + تحويل + تقرير متعدد العملات) | ✅ |
| cloud_sync | modules/cloud_sync.py (وجهات مزامنة + snapshot مع checksum + تشفير بكلمة مرور + نسخ احتياطي مع تدوير + سجل DB) | ✅ |
| demo_data | modules/demo_data.py + demo_templates.py (4 شركات تجريبية + معاملات شهرية 12 شهراً + تقارير مُعدّة + قوالب CSV) | ✅ |
| reporting | modules/reporting.py (PDF عربي + Excel + HTML + DuPont Report + Scenario Report) | ✅ |
| data_import | modules/data_import.py (Excel/CSV) | ✅ |
| user_manager | modules/user_manager.py (4 أدوار، 16 صلاحية، 2FA) | ✅ |
| ledger | modules/ledger.py (قيود + دفتر أستاذ + ميزان مراجعة + CSV + DB) | ✅ |
| partners | modules/partners.py (عملاء/موردون + معاملات + أرصدة + تقادم + DB) | ✅ |
| invoicing | modules/invoicing.py (فواتير بيع/شراء + عناصر + TVA + حالات + CSV + DB) | ✅ |
| inventory | modules/inventory.py (عناصر + حركات + متوسط تكلفة + تنبيهات + DB) | ✅ |
| payroll | modules/payroll.py (موظفون + CNAS/IRG + كشوفات + CSV + DB) | ✅ |
| budgeting | modules/budgeting.py (بنود + مقارنة بالفعلي + انحراف + CSV + DB) | ✅ |

### ✅ UI (100% — مكتمل)
| المكون | الملفات | الحالة |
|--------|---------|--------|
| MainWindow | ui/main_window.py (28 view بالـ pyqtSignal للتحديثات + تحميل كسول) | ✅ |
| AppState | ui/app_state.py (fiscal_year, ratios, companies, settings) | ✅ |
| BaseView | ui/views/_base.py (header + stat cards + tab order) | ✅ |
| LoginView | ui/views/login_view.py (3-step forgot password + 👁 toggle) | ✅ |
| DataEntryView | ui/views/data_entry.py (22 field, showEvent + tab order) | ✅ |
| DashboardView | ui/views/dashboard.py (4 charts + export) | ✅ |
| AdvancedDashboardView | ui/views/advanced_dashboard_view.py (6 KPI + 4 رسوم + تنبيهات + تخصيص + تخطيطات + PDF/Excel) | ✅ |
| CostCenterProfitabilityView | ui/views/cost_center_profitability_view.py (مراكز + توزيع + تحليل + مقارنات + اتجاه + تقارير + توصيات + PDF/Excel) | ✅ |
| CurrencyView | ui/views/currency_view.py (إعدادات العملات + أسعار الصرف + محول + تقرير متعدد العملات + تصدير CSV) | ✅ |
| CloudSyncView | ui/views/cloud_sync_view.py (وجهات + نسخ احتياطي/استرجاع + سحب + إعدادات تلقائية + كلمة مرور + سجل + CSV) | ✅ |
| DemoDataView | ui/views/demo_data_view.py (اختيار شركة تجريبية + مؤشرات + جدول معاملات شهرية + تقرير مُعد + تصدير CSV + قوالب) | ✅ |
| LedgerView | ui/views/ledger_view.py (قيود + تصفية + ميزان مراجعة + CSV + DB) | ✅ |
| PartnersView | ui/views/partners_view.py (شركاء + معاملات + تقادم + CSV + DB) | ✅ |
| InvoicingView | ui/views/invoicing_view.py (إنشاء فاتورة + عناصر + حالات + CSV + DB) | ✅ |
| InventoryView | ui/views/inventory_view.py (عناصر + حركات + تنبيهات + CSV + DB) | ✅ |
| PayrollView | ui/views/payroll_view.py (موظفون + تشغيل رواتب + كشوفات + CSV + DB) | ✅ |
| BudgetingView | ui/views/budgeting_view.py (بنود + مقارنة بالفعلي + CSV + DB) | ✅ |
| RatiosView | ui/views/ratios_view.py (20 cards + Z-Score) | ✅ |
| BenchmarksView | ui/views/benchmarks_view.py (radar/bar charts, قوة/ضعف + اتجاه + ترتيب منافسين + auto-update) | ✅ |
| TaxCalendarView | ui/views/tax_calendar_view.py (year selector + monthly overview) | ✅ |
| AnalysisView | ui/views/analysis_view.py (DuPont: شلال/خط/مؤشر + مقارنة قطاع + توصيات + PDF) | ✅ |
| AuditView | ui/views/audit_view.py (7 checks) | ✅ |
| TaxView | ui/views/tax_view.py (4 tabs: simulation + calculators + obligations + declarations) | ✅ |
| ReportsView | ui/views/reports_view.py (TXT/HTML/PDF/Excel) | ✅ |
| ExportView | ui/views/export_view.py | ✅ |
| ScenariosView | ui/views/scenarios_view.py (3 سيناريوهات + خط/شريط/مساحة + حساسية Tornado + PDF + حفظ JSON/DB) | ✅ |
| ForecastingView | ui/views/forecasting_view.py | ✅ |
| BreakevenView | ui/views/breakeven_view.py | ✅ |
| SecurityView | ui/views/security_view.py (2FA) | ✅ |
| UserManagementView | ui/views/user_management_view.py (4 roles, 16 permissions) | ✅ |
| ChatView | ui/views/chat_view.py (AI Chat) | ✅ |
| SettingsView | ui/views/settings_view.py (lang + theme + API + fiscal year) | ✅ |
| Style Light | ui/resources/style.qss | ✅ |
| Style Dark | ui/resources/style_dark.qss | ✅ |
| Style Modern | ui/resources/style_modern.qss | ✅ |
| Messages | ui/widgets/messages.py (رسائل خطأ/تحذير موحّدة + إجراء مقترح مترجم) | ✅ |
| i18n | ui/resources/i18n.py (AR + EN + FR, 1986 keys) | ✅ |

### ✅ UTILS (100% — مكتمل)
| المكوّن | الملفات | الحالة |
|---------|---------|--------|
| formatters | utils/formatters.py | ✅ |
| validators | utils/validators.py | ✅ |
| app_logger | utils/app_logger.py | ✅ |
| security | utils/security.py (تشفير، 2FA، JWT) | ✅ |

---

## FILE STRUCTURE (v3.1.2)

```
Accounting_Platform/
├── config.py                        # v3.1.2
├── installer.iss                    # Inno Setup (v3.1.2)
├── build_nuitka.bat                 # Nuitka build script
├── PROJECT_MAP.md                   # هذا الملف
├── AGENTS.md                        # Surgical Editing Protocol
├── users.json                       # Users + reset_tokens
│
├── database/
│   ├── db_connection.py
│   ├── db_schema.py                 # 15 tables
│   └── db_operations.py
│
├── modules/
│   ├── calculations.py              # 20 financial ratios + Z-Score
│   ├── analysis.py                  # DuPont, Trends, WC, CashFlow
│   ├── scenarios.py                 # 3 scenarios + sensitivity + tornado
│   ├── audit.py                     # Financial audit checks
│   ├── benchmarks.py                # 7 sectors × 10 ratios + standards + competitors
│   ├── advanced_dashboard.py        # 6 KPI + charts + alerts + layouts
│   ├── ai_insights.py               # ML insights: forecast + anomalies + patterns + recs + alerts
│   ├── cost_center_profitability.py # cost centers + allocation + profitability + comparisons
│   ├── currency.py                  # multi-currency engine + exchange rates + report
│   ├── cloud_sync.py                # cloud sync destinations + snapshots + backup + history
│   ├── demo_templates.py            # CSV templates + export company data + pre-made reports
│   ├── tax.py                       # TaxEngine (IBS/TVA/IRG/CNAS/CNAC/VF + IFU + formation + rental)
│   ├── tax_years.py                 # Year configs manager (config_years/*.json + .active_year)
│   ├── tax_reminders.py             # Reminder system + calendar
│   ├── tax_config.json              # Algerian tax rates (legacy, year 2025)
│   ├── config_years/                # Year-based tax configs (2025/2026…) + .active_year pointer
│   ├── tax_reports.py               # G50/G57/DAS declaration templates + PDF/Excel
│   ├── reporting.py                 # TXT/HTML/PDF/Excel
│   ├── data_import.py               # Excel/CSV import
│   ├── update_checker.py            # GitHub Pages update check
│   ├── validation.py
│   ├── demo_data.py                # legacy demo + 4 demo companies + monthly transactions
│   ├── user_manager.py              # Auth + roles + 2FA + reset
│   ├── excel_export.py
│   ├── print_manager.py
│   ├── ledger.py                  # دفتر الأستاذ: قيود + دفتر + ميزان مراجعة + CSV + DB
│   ├── partners.py                # عملاء/موردون + معاملات + أرصدة + تقادم + DB
│   ├── invoicing.py               # فواتير بيع/شراء + عناصر + TVA + حالات + CSV + DB
│   ├── inventory.py               # عناصر + حركات + متوسط تكلفة + تنبيهات + DB
│   ├── payroll.py                 # موظفون + CNAS/IRG + كشوفات + CSV + DB
│   └── budgeting.py               # بنود + مقارنة بالفعلي + انحراف + CSV + DB
│
├── ui/
│   ├── main_window.py               # 35 views + قوائم/اختصارات/انتقالات/ثيم
│   ├── app_state.py                 # State + settings
│   ├── run_ui.py                    # GUI entry
│   ├── resources/
│   │   ├── i18n.py                  # 300+ keys (AR/EN/FR)
│   │   ├── style.qss / style_dark.qss / style_modern.qss
│   │   └── fonts/ (Amiri 6 variants)
│   ├── widgets/
│   │   ├── messages.py               # unified error/warning helpers + suggested action
│   │   ├── toast.py                  # toast notifications with fade animations
│   │   ├── loading_overlay.py        # LoadingOverlay + SpinnerWidget
│   │   ├── alert_banner.py
│   │   └── table_filter.py / undo_redo.py
│   └── views/
│       ├── _base.py / _path.py
│       ├── login_view.py            # 3-step forgot + 👁 toggle + auto-fill
│       ├── data_entry.py            # showEvent + tab order
│       ├── dashboard.py
│       ├── advanced_dashboard_view.py  # KPI cards + charts + alerts + customize
│       ├── ai_insights_view.py         # forecasting + anomalies + patterns + recs + alerts
│       ├── cost_center_profitability_view.py  # centers + allocation + analysis + comparison + trend
│       ├── currency_view.py            # multi-currency settings + converter + report + CSV
│       ├── cloud_sync_view.py          # destinations + backup/restore + passphrase + history
│       ├── demo_data_view.py           # demo companies + monthly transactions + reports + templates
│       ├── ratios_view.py           # 20 cards + Z-Score
│       ├── analysis_view.py
│       ├── scenarios_view.py         # 3 scenarios + charts + tornado + PDF
│       ├── audit_view.py
│       ├── tax_view.py
│       ├── benchmarks_view.py       # standards + strengths + trend + competitors
│       ├── tax_calendar_view.py     # year selector
│       ├── reports_view.py
│       ├── security_view.py / user_management_view.py
│       ├── chat_view.py
│       ├── settings_view.py
│       ├── ledger_view.py             # دفتر الأستاذ: قيود + تصفية + ميزان مراجعة + CSV
│       ├── partners_view.py           # عملاء/موردون + معاملات + تقادم + CSV
│       ├── invoicing_view.py          # فواتير بيع/شراء + عناصر + حالات + CSV
│       ├── inventory_view.py          # عناصر + حركات + تنبيهات + CSV
│       ├── payroll_view.py            # موظفون + تشغيل رواتب + كشوفات + CSV
│       ├── budgeting_view.py          # بنود + مقارنة بالفعلي + CSV
│       └── (scenarios, forecasting, breakeven, export)
│
├── utils/
│   ├── formatters.py
│   ├── validators.py
│   ├── app_logger.py
│   └── security.py
│
├── docs/
│   ├── index.html                   # Website (AR/EN/FR)
│   ├── script.js                    # i18n translations
│   ├── style.css
│   ├── version.json                 # v3.1.4 update check
│   └── *_chart.png
│
└── tests/
    ├── test_calculations.py
    ├── test_audit.py
    ├── test_analysis.py
    ├── test_validation.py
    ├── test_data_import.py
    ├── test_database.py
    ├── test_reporting.py
    ├── test_scenarios.py
    ├── test_app_state.py
    ├── test_formatters.py
    ├── test_validators.py
    ├── test_edge_cases.py
    ├── test_messages.py              # unified error-message helpers
    ├── test_tax.py
    ├── test_tax_reports.py
    ├── test_tax_years.py               # year-based tax configs + IFU/formation/rental
    ├── test_ui.py                    # UI tests
    ├── test_security.py
    ├── test_demo_data.py
    ├── test_new_modules.py
    ├── test_new_features.py
    └── test_reference_standards.py
    └── test_advanced_dashboard.py
    └── test_ai_insights.py
    └── test_cost_center_profitability.py
    └── test_currency.py
    └── test_cloud_sync.py
    └── test_demo_companies.py
    └── test_cashflow.py               # CashFlowStatement (جلسة التغطية الشاملة)
    └── test_comparative.py            # ComparativeAnalyzer
    └── test_edge_errors.py            # edge/error paths للميزات الست المستهدفة
    └── test_backup.py                 # backup + scheduled_backup
    └── test_bank_print.py             # bank_sync + print_manager
    └── test_breakeven_costcenter.py   # breakeven + cost_center + forecasting
    └── test_reporting_modules.py      # calculations + report_templates + activity_log
    └── test_email_currency.py         # email_notifier + currency
    └── test_importers.py              # data_import + csv_import
    └── test_excel_export.py           # excel_export
    └── test_reporting_extra.py        # reporting export_to_pdf/excel
    └── test_user_manager.py           # user_manager (auth/roles/2FA/lockout)
    └── test_update_checker_extra.py   # update_checker (شبكة mock)
    └── test_cloud_sync_extra.py       # cloud_sync (HTTP/تشفير/snapshot)
    └── test_tax_reminders_extra.py    # tax_reminders (تواريخ/تقويم)
    └── test_tax_reports_extra.py      # tax_reports G50/G57/DAS PDF
    └── test_small_gaps.py             # budget + validation + advanced_dashboard + cost_center_profitability
    └── test_user_testing.py           # user_testing (جلسات/ملاحظات/رضا/تقارير/تصدير/DB) — جلسة v3.1.6
    ├── test_ledger.py                 # ledger (قيود/دفتر/ميزان مراجعة/DB) — جلسة المرحلة الثانية
    ├── test_partners.py               # partners (شركاء/معاملات/تقادم/DB)
    ├── test_invoicing.py              # invoicing (فواتير/عناصر/TVA/حالات/DB)
    ├── test_inventory.py              # inventory (عناصر/حركات/تقييم/DB)
    ├── test_payroll.py                # payroll (موظفون/IRG/كشوفات/DB)
    └── test_budgeting.py              # budgeting (بنود/مقارنة/انحراف/DB)
```
```
    ├── test_integration_workflow.py   # سير العمل: رحلات مستخدم كاملة + حالة + تدفق بيانات
    ├── test_integration_database.py   # سلامة/معاملات/تزامن/نسخ-استرجاع
    └── test_integration_performance.py# أداء تحت الحمل + إجهاد ذاكرة (جلسة التكامل)
```
```
    └── test_uat.py                    # UAT كمستخدم حقيقي: تسجيل دخول + تجول 35 شاشة + لغة + حفظ (جلسة v3.1.6)
```

---

## TEST SUMMARY (v3.1.8)

| الملف | العدد | الحالة |
|-------|-------|--------|
| test_advanced_dashboard.py | ✅ | 30 |
| test_ai_insights.py | ✅ | 33 |
| test_analysis.py | ✅ | 22 |
| test_app_state.py | ✅ | 7 |
| test_audit.py | ✅ | 19 |
| test_backup.py | ✅ | 54 |
| test_bank_print.py | ✅ | 66 |
| test_breakeven_costcenter.py | ✅ | 24 |
| test_calculations.py | ✅ | 37 |
| test_cashflow.py | ✅ | 8 |
| test_cloud_sync.py | ✅ | 16 |
| test_cloud_sync_extra.py | ✅ | 33 |
| test_comparative.py | ✅ | 10 |
| test_cost_center_profitability.py | ✅ | 40 |
| test_currency.py | ✅ | 16 |
| test_database.py | ✅ | 11 |
| test_data_import.py | ✅ | 16 |
| test_demo_companies.py | ✅ | 20 |
| test_demo_data.py | ✅ | 10 |
| test_edge_cases.py | ✅ | 31 |
| test_edge_errors.py | ✅ | 63 |
| test_email_currency.py | ✅ | 44 |
| test_excel_export.py | ✅ | 9 |
| test_formatters.py | ✅ | 22 |
| test_importers.py | ✅ | 50 |
| test_messages.py | ✅ | 8 |
| test_new_features.py | ✅ | 12 |
| test_new_modules.py | ✅ | 24 |
| test_reference_standards.py | ✅ | 25 |
| test_reporting.py | ✅ | 14 |
| test_reporting_extra.py | ✅ | 15 |
| test_reporting_modules.py | ✅ | 52 |
| test_scenarios.py | ✅ | 23 |
| test_security.py | ✅ | 36 |
| test_small_gaps.py | ✅ | 34 |
| test_tax.py | ✅ | 20 |
| test_tax_reminders_extra.py | ✅ | 32 |
| test_tax_reports.py | ✅ | 22 |
| test_tax_reports_extra.py | ✅ | 14 |
| test_tax_years.py | ✅ | 62 |
| test_ui.py | ✅ | 116 |
| test_update_checker.py | ✅ | 15 |
| test_update_checker_extra.py | ✅ | 28 |
| test_user_manager.py | ✅ | 73 |
| test_user_testing.py | ✅ | 66 |
| test_validation.py | ✅ | 13 |
| test_validators.py | ✅ | 23 |
| test_ledger.py | ✅ | 36 |
| test_partners.py | ✅ | 50 |
| test_invoicing.py | ✅ | 46 |
| test_inventory.py | ✅ | 47 |
| test_payroll.py | ✅ | 55 |
| test_budgeting.py | ✅ | 35 |
| test_integration_workflow.py | ✅ | 9 |
| test_integration_database.py | ✅ | 18 |
| test_integration_performance.py | ✅ | 10 |
| test_ui_views.py | ✅ | 114 |
| test_uat.py | ✅ | 9 |
| test_startup_perf.py | ✅ | 4 |
| test_exporters.py | ✅ | 9 |
| **المجموع** | **✅ 1800** | |

> التوزيع: 1547 اختباراً غير واجهة + 116 في test_ui.py + 114 في test_ui_views.py + 9 في test_uat.py + 4 في test_startup_perf.py + 9 في test_exporters.py (test_bank_print ضمن المجموعة غير الواجهة) — المرجع الرسمي: `python -m pytest tests -q`

---

## KEYBOARD SHORTCUTS

| الاختصار | الوظيفة |
|----------|---------|
| Ctrl+Q | خروج |
| Ctrl+L | تسجيل خروج |
| Ctrl+R | حساب النسب |
| Ctrl+S | حفظ في DB |
| Ctrl+P | طباعة |
| Ctrl+E | تصدير |
| Ctrl+, | الإعدادات |
| Ctrl+T | تبديل الثيم (فاتح/داكن) |
| F1 | نافذة الاختصارات |
| Ctrl+1..9, Ctrl+0 | الشاشات 1-10 |
| Ctrl+Shift+1..9, Ctrl+Shift+0 | الشاشات 11-20 |
| Ctrl+Shift+A | شاشة 21 (مزامنة البنك) |
| F2..F8 | الشاشات 22-28 |
| F9 | شاشة 29 (اختبار المستخدمين) |
| F10, F11, F12 | الشاشات 30-32 (دفتر الأستاذ / العملاء والموردون / الفواتير) |
| Ctrl+Shift+B, Ctrl+Shift+C, Ctrl+Shift+D | الشاشات 33-35 (المخزون / الرواتب / الميزانية) |
| قائمة "عرض" | تنقّل بالماوس بين كل الشاشات 35 + الثيم |

---

## DEPLOYMENT

- **Nuitka 4.1.3**: Python → C → native exe
- **Inno Setup 6**: Installer ~61 MB
- **Portable ZIP**: ~62 MB (WinRAR)
- **GitHub Releases**: v3.0.0 → v3.1.0 → v3.1.1 → v3.1.2
- **GitHub Pages**: https://khalilmebarek-creator.github.io/SmartAccounting/
- **Update Checker**: يفحص `docs/version.json` على GitHub Pages

---

## EXECUTION LOG

> **آخر حالة (2026-08-17):** v3.2.0 — **2075 اختباراً** (سطح المكتب) + **56 اختباراً Flutter** (mobile/) + **تطبيق جوال Android** (arm64 18.2MB) + تغطية وحدات 100% + 2105 مفتاح i18n × 3 + **شريط Ribbon 7 تبويبات** + **إصلاح انهيار matplotlib** + **ML مفعّل كاملاً** + **تقارير IAS/IFRS** + **منصة ذكاء اصطناعي متكاملة** + **توحيد تصميم الشاشات المحاسبية الأربع (34-37)** + **تمرير عمودي QScrollArea لكل الشاشات** (BaseView + wrap_in_scroll لـ QWidget).

| # | التاريخ | الإجراء | النتيجة |
|---|---------|---------|---------|
| 1-31 | 2026-07-13 | v2.0.0 → v2.1.0 (الإصدار الأولي) | ✅ 184 اختبار |
| 32 | 2026-07-27 | v3.0.0 إعادة هيكلة كاملة + 22 شاشة | ✅ |
| 33 | 2026-07-28 | v3.1.0 إصلاح البيانات المالية | ✅ |
| 34 | 2026-07-28 | v3.1.1 UI/UX fixes (5 مشاكل) + تحديث checker | ✅ 322 اختبار |
| 35 | 2026-07-28 | v3.1.2 إصلاح التنقل: سنة التقويم + تحديث المعايير + اختبارات UI | ✅ 322 اختبار |
| 36 | 2026-07-28 | v3.1.2 تحسين التحديث التلقائي: batch script + إعادة تشغيل + إصدار | ✅ 351 اختبار |
| 37 | 2026-07-30 | v3.1.3 إصلاح مشكلة الشرطة السفلية + إصدار | ✅ 319 اختبار |
| 38 | 2026-07-31 | v3.1.4 إصلاح عدم فتح التطبيق بعد التحديث (matplotlib مفقود) + تحديث مخفي wscript/VBS + مثبّت محسّن | ✅ 318 اختبار |
| 39 | 2026-07-31 | إصلاح خطأ محاكاة الضرائب: CNAS/CNAC لا تتضاعف مع عدد الموظفين (tax.py) + إصلاح ترميز اختبارات Windows cp1252 (conftest.py) + تحديث أرقام الموقع (20 نسبة + Z-Score / 362 اختبار) | ✅ 362 اختبار |
| 40 | 2026-07-31 | شاشة تحليل DuPont المتقدمة: شلال/خط/مؤشر ROE + مقارنة قطاعية + توصيات + تصدير PDF (analysis.py, db_operations.py, reporting.py, analysis_view.py, i18n) | ✅ 375 اختبار |
| 41 | 2026-07-31 | شاشة تحليل السيناريوهات: مثالي/طبيعي/أسوأ + حساسية Tornado + خط/شريط/مساحة + PDF + حفظ JSON/DB (scenarios.py, db_schema.py, reporting.py, scenarios_view.py, i18n, app_state) | ✅ 398 اختبار |
| 42 | 2026-07-31 | ميزة المعايير المرجعية المتقدمة: أفضل الممارسات + معيار دولي + نقاط قوة/ضعف + تحليل اتجاه + مقارنة منافسين (benchmarks.py, db_schema.py +14 جدول, db_operations.py, benchmarks_view.py, i18n, test_reference_standards.py) | ✅ 423 اختبار |
| 43 | 2026-07-31 | شاشة لوحة التحكم المتقدمة: 6 بطاقات KPI بحالة لونية + 4 رسوم (إيرادات شهرية/ربعية + مصروفات + ربحية + رادار) + تنبيهات (شذوذ/أداء/معايير/إجراءات) + تخصيص كامل + حفظ تخطيطات DB + تصدير PDF/Excel (advanced_dashboard.py, db_schema.py +15 جدول, db_operations.py, advanced_dashboard_view.py, main_window.py, i18n, test_advanced_dashboard.py) | ✅ 453 اختبار |
| 44 | 2026-07-31 | ميزة الامتثال الضريبي الجزائري: نسبة TVA 6% جديدة + ترحيل رصيد TVA + دفعات IBS المقدمة (3,6,11) + تصفية IBS + بيانات DAS + قوالب الإقرارات G50/G57/DAS مع تصدير PDF/Excel + تبويب إقرارات في TaxView (tax.py, tax_config.json, tax_reports.py, tax_view.py, i18n, test_tax_reports.py) | ✅ 475 اختبار |
| 45 | 2026-07-31 | محرك الرؤى الذكية AI: تنبؤ 3-6 أشهر (خطي/متوسط/أسي + فترات ثقة 95%) + كشف شذوذ (z-score + IQR للمعاملات) + أنماط (اتجاه/موسمية/دورات/مخاطر) + توصيات ذكية + تنبيهات + شاشة جديدة + تصدير PDF/Excel (ai_insights.py, ai_insights_view.py, main_window.py + شاشة 24, i18n 1275, test_ai_insights.py) | ✅ 508 اختبار |
| 46 | 2026-08-01 | تحليل ربحية مراكز التكلفة: تعريف مراكز (قسم/مشروع/فرع/خط إنتاج) + توزيع مباشر/غير مباشر (إيرادات/عدد موظفين/مساحة/متساوٍ) + ربحية + مقارنات (سابقة/ميزانية/معايير) + اتجاه متعدد الفترات + تقارير/توصيات + شاشة جديدة + تصدير PDF/Excel (cost_center_profitability.py, cost_center_profitability_view.py, main_window.py + شاشة 25, i18n 1373, test_cost_center_profitability.py) | ✅ 558 اختبار |
| 47 | 2026-08-01 | تحسين أداء شامل: تحميل كسول للمشاهد (main_window.py) + تحميل كسول للوحدات (modules/__init__.py + PEP 562) + تجمّع اتصالات DB (db_connection.py + close_pool) + دفعات executemany (db_operations.py) + لوحة تحكم بلا إعادة رسم زائدة (dashboard.py) + اختبارات TestConnectionPool (إقلاع 778→49ms، RSS 128→45MB، حفظ DB 4.6×، قراءة 17×، لوحة 340→0ms) + تقرير docs/PERFORMANCE_REPORT.md | ✅ 560 اختبار |
| 48 | 2026-08-01 | تعدد العملات + المزامنة السحابية: محرك عملات (7 عملات + أسعار + تحويل + تقرير متعدد العملات) + شاشة تعدد العملات (currency_view.py) + محرك مزامنة سحابية (وجهات + snapshot مع checksum + تشفير بكلمة مرور + نسخ احتياطي مع تدوير + استرجاع + سجل DB) + شاشة المزامنة (cloud_sync_view.py) + ربط شاشتي 26/27 في main_window + إصلاح وصول شاشة 25 (sidebar) + i18n 1483 (currency.py, cloud_sync.py, test_currency.py 16, test_cloud_sync.py 16, app_state.py) | ✅ 606 اختبار |
| 49 | 2026-08-01 | الشركات التجريبية: 4 شركات (تجارية/خدمات/إنتاج/استيراد-تصدير) ببيانات مالية وضريبية متسقة + مولّد معاملات شهرية (12 شهراً بأوزان موسمية) + تحميل شركة إلى التطبيق + تقارير مُعدّة مسبقاً (ميزانية/دخل/نسب) + تصدير بيانات CSV + قوالب استيراد CSV متوافقة مع DataImporter + شاشة جديدة (demo_data_view.py) + ربط شاشة 28 في main_window + i18n 1519 (demo_data.py, demo_templates.py, test_demo_companies.py 20) | ✅ 626 اختبار |
| 50 | 2026-08-01 | تحسينات UI/UX: اختصارات كاملة لكل الشاشات 28 (F2..F8 للشاشات 22-28 + Ctrl+T للثيم) + قائمة "عرض" ديناميكية بكل الشاشات + نافذة اختصارات كاملة + انتقالات تلاشي عند تغيير الشاشة + مؤشر تحميل في شريط الحالة + رسائل خطأ موحّدة مع إجراء مقترح مترجم (messages.py + إعادة ربط أخطاء الطباعة/التصدير/الاختبارات) + تحسينات إتاحة/تباين في الثيمات الثلاثة (focus/disabled/ComboBox/ToolTip + تباين نص داكن #888888→#9A9A9A) + i18n 1530 (main_window.py, messages.py, style*.qss, test_messages.py 8) | ✅ 634 اختبار |
| 51 | 2026-08-01 | التغطية الشاملة للوحدات (Goal: >90%): اختبار كل module بمنفردة مع edge/error cases (صفر/سالب/دقة عشرية/بيانات مفقودة/مدخلات غير صالحة/أخطاء DB وشبكة) — غطّت الميزات الست (DuPont/Scenarios/Benchmarks/AI/Tax/Anomaly) + cashflow + comparative (كانا 0%) + كل الطبقات المتوسطة/الضعيفة عبر 20 ملف اختبار جديد + إصلاح خلل واحد: generate_report في comparative.py كان يرمي KeyError مع بيانات ناقصة (استُخدم .get(item/ratio, 0)) | ✅ 1229 اختبار + تغطية وحدات **99%** (كانت 73%) |
| 52 | 2026-08-01 | اختبار التكامل والأداء والاستقرار (Goal: ربط الميزات): 3 ملفات جديدة — workflow (9: رحلات مستخدم كاملة demo→ratios→analysis→audit→tax→report→export + multi-year comparative/benchmarks/AI + AppState save/load/clear + اتساق ROE/تدفق بيانات) + database (18: سلامة FK/تفرد/ترابط + معاملات بتراجع كامل + تزامن 8 كتّاب + نسخ/استرجاع/JSON) + performance (10: 1200 إدراج مجمّع/1500 save/8 مستخدمين/2000 حساب/إجهاد ذاكرة) + إصلاح 3 أخطاء منتج (رأس المال العامل لا يُخزَّن، حذف notes الترابطي معطوب، نسخ احتياطي يفقد بيانات WAL) + تقرير docs/INTEGRATION_REPORT.md | ✅ **1266** اختبار (1127 عبر unittest) + تغطية **99%** (كل modules 100% ما عدا tax_reminders 98% فرع ميت) |
| 53 | 2026-08-01 | شاشة اختبار المستخدمين (29) — Goal: اختبار المستخدمين الحقيقيين: محرك user_testing.py (4 مجموعات مستخدمين × 5 سيناريوهات + ملاحظات/مقترحات/أعطال بتصنيفات/أولويات/حالات + درجة رضا بقيود وتحليل مفصّل + تقارير تعقيبات/أعطال/تحسينات/ملخص + بيانات تجريبية + تصدير/استيراد JSON + CSV/Excel/PDF + حفظ/تحميل DB عبر get_connection) + شاشة user_testing_view.py + ربط شاشة 29 في main_window (سايدبار + F9 + view_keys) + i18n 1626 (user_testing.py, user_testing_view.py, main_window.py) + إعادة هيكلة satisfaction_level بلا فرع ميت + إصلاح تصدير PDF عند غياب خط عربي (cp1252 fallback) | ✅ **1332** اختبار + تغطية وحدات **99%** (user_testing.py 100%) |
| 54 | 2026-08-01 | التوثيق الشامل (Goal: API + User + Video + Knowledge base): إعادة توليد docs/API_REFERENCE.md بصيغة UTF-8 صحيحة (37 وحدة/325 عملية + معاملات + أخطاء + أمثلة مُتحقق منها) + docs/api/openapi.yaml (OpenAPI 3.0 لـ Swagger UI — 325 عملية) + docs/api/index.html (عارض Swagger عبر موقع docs/) + docs/USER_GUIDE.md (29 شاشة + ميزات جديدة + أفضل ممارسات + Troubleshooting + FAQ) + docs/tutorials/ (4 سكربتات فيديو جاهزة لأدوات AI: جولة الميزات/سير عمل التحليل/توليد التقارير/نصائح وخدع) + docs/KNOWLEDGE_BASE.md (فهرس موحّد + FAQ) + روابط جديدة في footer الموقع | ✅ مستندات (لا اختبارات جديدة) |
| 55 | 2026-08-01 | **التصحيحات النهائية + مراجعة الأمان (Goal: صفر أخطاء حرجة + جاهزية للعرض)**: إصلاح 13 خللاً موثّقاً سابقاً — print_manager (استيراد QPageLayout لفرع Landscape) + bank_sync (رأس الملف: كشف بلا أرقام بدل ابتلاع أول صف بيانات) + report_templates (deepcopy لـ DEFAULT_TEMPLATES عند التحميل) + reporting (رسالة واضحة عند غياب Amiri وتصدير عربي) + update_checker (try/finally + تنظيف الملف الجزئي + تصفير last_error بعد نجاح fallback) + user_manager (token=None → err_reset_invalid_token) + scheduled_backup (استعادة vault.enc + meta.json ضمن files) + backup (SQL بالاسم الحقيقي للتصدير + تحقق `_is_valid_sqlite` قبل الاستعادة) + data_import (disconnect عند فشل connect + رفض الكلمات المحجوزة SQLite) + currency (حذف سطر no-op) + tax_reminders (إزالة فرع except ميت) + i18n (window_title v2.5.0 → v3.1.6 ×3 لغات) + مراجعة أمان (PBKDF2 100k + salt لكل مستخدم + تخزين مشفّر SMTP/API + روابط HTTPS فقط — كلها سليمة) + **تغطية وحدات 100%** (إغلاق آخر الفجوات الدفاعية) | ✅ **1350** اختبار + تغطية وحدات **100%** |
| 56 | 2026-08-02 | **المرحلة الثانية — 6 شاشات محاسبية جديدة (Goal: واجهات للميزات المحاسبية الخمسة)**: محرك ledger.py (قيود يومية + دفتر أستاذ + ميزان مراجعة + CSV + DB) + partners.py (عملاء/موردون + معاملات + أرصدة + تقادم الديون + DB) + invoicing.py (فواتير بيع/شراء + عناصر + TVA + حالات + CSV + DB) + inventory.py (عناصر + حركات + متوسط تكلفة + تنبيهات + DB) + payroll.py (موظفون + CNAS/IRG/حساسية + كشوفات + CSV + DB) + budgeting.py (بنود + مقارنة بالفعلي + انحراف + CSV + DB) + شاشات ledger_view/partners_view/invoicing_view/inventory_view/payroll_view/budgeting_view (شاشات 30-35) + ربط في main_window (factories 30-35 + sidebar_items 35 + اختصارات F10/F11/F12 + Ctrl+Shift+B/C/D) + إصلاح apply_language (sidebar_user_testing المفقودة كانت تحذف شاشة 29 عند تغيير اللغة) + i18n 1874 (ledger_/partners_/invoicing_/inventory_/payroll_/budgeting_* + sidebar) + 37 اختبار واجهة جديد في test_ui.py (110) + 269 اختبار محركات (test_ledger 36 + test_partners 50 + test_invoicing 46 + test_inventory 47 + test_payroll 55 + test_budgeting 35) + تعارض QMessageBox في الاختبارات حُلّ عبر unittest.mock (0xC0000005) | ✅ **1656** اختبار + تغطية وحدات **100%** |
| 57 | 2026-08-02 | **إصلاح الشاشة السوداء عند التنقل (Goal: لا تبقى أي شاشة عالقة عند شفافية صفر)**: الخلل — `_fade_in_view` في main_window.py يخزّن الأنيميشن في `self._view_anim` (مرجع واحد) فيُتلفف الأنيميشن السابق أثناء طيرانه فيبقى QGraphicsOpacityEffect عند شفافية ~0 مع عدم إطلاق `finished` → الشاشة سوداء دائمة على الأجهزة البطيئة؛ الإصلاح — حاوية `self._view_anims` (بمفتاح id(widget)) توقف/تحذف الأنيميشن السابق قبل بدء جديد + `QTimer.singleShot(300)` كضمانة تُزيل التأثير حتى لو لم يُبعث `finished` + دالة `_remove` تتحقق أن التأثير/المرجع ما زال لنفس الأنيميشن (حماية من finished متأخر يزيل تأثير الشاشة الجديدة) + 5 اختبارات واجهة جديدة في test_ui.py (115) (TestFadeInSafety: تبديل سريع/لا أنيميشنات متبقية/تنقل واحد/None/فشل setOpacity) | ✅ **1661** اختبار + تغطية وحدات **100%** |
| 58 | 2026-08-02 | **تغطية الواجهات + إصلاحات i18n (Goal: كل الشاشات الـ35 مختبرة + صفر مفاتيح ترجمة ناقصة)**: `tests/test_ui_views.py` الجديد (111 اختباراً، 25 فئة) يغطي الشاشات الـ24 غير المغطاة سابقاً (dashboard/ratios/audit/reports/settings/chat/tax/comparative/cashflow/security/zscore/forecasting/budget/cost_center/breakeven/data_import/bank_sync/scenarios/advanced_dashboard/ai_insights/currency/cloud_sync/demo_data/user_testing/analysis) + **إصلاح بغّ حقيقي** `bank_sync_view.py:229,231` (استدعاء `ThemeColors.get()` بوسيطين — الدالة تقبل وسيطاً واحداً → TypeError عند رسم جدول المعاملات؛ أصبح بوسيط واحد) + **إصلاح تسرّب حالة** في test_ui_views.py (`test_calculate_cash_flow` + `test_add_year_requires_data` كانا يعدّلان `state.financial_data` دون استعادة → كسر `test_financial_spins_start_zero` في test_ui.py عند التشغيل المتسلسل — أصبحا try/finally) + **إضافة 44 مفتاح i18n مفقوداً** (chat_offline_* للمساعد المحلي: advice tips/labels/benchmark/dupont/receivables… + breakeven_chart_title + cloud_action/destination/status + cost_profit_prev_profit + login_reg_display) عبر اللغات الثلاث — كان المساعد المحلي بالعربية يعرض أسماء مفاتيح خام | ✅ **1772** اختبار + تغطية وحدات **100%** |
| 59 | 2026-08-02 | **تحسينات UI حسب ملاحظات المستخدم (Goal: مقروئية وسهولة استخدام الشاشات المبلّغ عنها)**: 5 شاشات — لوحة التحكم المتقدمة (`advanced_dashboard_view.py`: اللون المميز في `color_combo` يُعرض باسمه المُترجم عبر مفاتيح `color_*` الجديدة بدل رمز `#2196F3` — mapping `_THEME_COLOR_KEYS`) + ربحية المراكز (`cost_center_profitability_view.py`: صفوف جدول مراكز التكلفة `verticalHeader().setDefaultSectionSize(46)` + `setMinimumHeight`) + المزامنة السحابية (`cloud_sync_view.py`: سجل العمليات صفوف 44px + حد أدنى) + الشركات التجريبية (`demo_data_view.py`: جدول المعاملات الشهرية صفوف 42px + حد أدنى) + اختبار المستخدمين (`user_testing_view.py`: حقول الجلسة/الملاحظة 36px + خانة التعليق `setMinimumHeight(110)` بدل `setMaximumHeight(70)` + جدول الملاحظات صفوف 48px مع `setWordWrap(True)` + حد أدنى) + **إصلاح عزل اختبارات** في test_ui.py (`TestDataEntryView.setUp` يستدعي `state.clear()` — كان تشغيل التطبيق وحفظ بيانات إلى accounting_data.json يكسر اختبارات «يبدأ فارغاً»: test_company_name_starts_empty + test_save_button_starts_disabled) + i18n 1924 (+6 مفاتيح color_* ×3 لغات) | ✅ **1772** اختبار + تغطية وحدات **100%** |
| 60 | 2026-08-02 | **معالجة Smart App Control (Goal: حل حجب الـ exe غير الموقّع على Windows 11)**: سكربت `tools/allow_smart_app_control.ps1` جديد — يفحص حالة SAC من السجل (`HKLM:\...\CI\Policy\VerifiedAndReputablePolicyState` → Off/Enforcement/Warning) + يعرض تعليمات الإيقاف بالعربية + يضيف استثناءات Defender للمثبّت (`installer_output\*.exe`) وبنية Nuitka (`dist_nuitka`) مع فحص صلاحيات Administrator + يفحص حالة توقيع الـ exe (`Get-AuthenticodeSignature` → NotSigned) — التحقق على جهاز التطوير: SAC مفعّل **Enforcement** + exe **NotSigned** (تأكيد السبب الجذري)؛ **إصلاح ترميز**: السكربت يحتاج UTF-8 **BOM** لأن PowerShell 5.1 يقرأ cp1252 فيفشل ParserError مع العربية (نُفّذ `Set-Content -Encoding UTF8`) + تحديث التوثيق لإرشاد المستخدمين للسكربت أو إيقاف SAC: USER_GUIDE.md (جدول السطر 1 + سطر الملاحظة بدل «لم يُحل بعد»)، docs/index.html `dl_note_sac`، docs/script.js بالثلاث لغات | ✅ **1772** اختبار + تغطية وحدات **100%** |
| 61 | 2026-08-02 | **UAT شامل كمستخدمين (Goal: تجربة التطبيق من وجهة المستخدم النهائي قبل الرفع)**: `tests/test_uat.py` الجديد (9 اختبارات) — رحلة مستخدم حقيقية عبر `MainWindow`: تسجيل الدخول (تعبئة login_email/login_password + mock لـ needs_password_change عبر PasswordChangeDialog) + تجوّل الشاشات الـ35 عبر `change_view` (factories 1-35 + sidebar) + إدخال بيانات تجريبية وحساب النسب + تبديل اللغات الثلاث + `save_to_db` + تسجيل الخروج + بدء التطبيق عند شاشة الدخول؛ **كشف وإصلاح بغّ حقيقي**: `bank_sync_view.py:238` و`data_import_view.py:260` يستدعيان `self._clear_layout()` في `retranslate` دون وجود الأسلوب → AttributeError عند تبديل اللغة بينما المشهد محمّل (سقوط التطبيق) — أُضيف `_clear_layout()` + `_clear_nested()` (تفرّغ layout بعمق مع deleteLater) إلى `ui/views/_base.py` (BaseView) + 5 اختبارات انحدار في test_ui_views.py (114: إعادة بناء DataImportView/BankSyncView بعد retranslate + تجريد layouts متداخلة + فراغ + إعادة بناء BaseView) → `_base.py` عند **100%** | ✅ **1786** اختبار + تغطية وحدات **100%** |
| 62 | 2026-08-03 | **رفع الإصدار إلى v3.1.7 (Goal: نشر نسخة جديدة تعتمد نتائج UAT)**: رفع `config.py` APP_VERSION + `i18n.py` window_title ×3 لغات + `installer.iss` + `build_nuitka.py` (product/file version) إلى 3.1.7 + تحديث docs/version.json (changelog جديد + download/installer URLs v3.1.7) + docs/index.html (badge + softwareVersion + روابط التحميل + سجل v3.1.7 مع upd_date8/upd_new31) + docs/script.js (hero_badge ×3 لغات + upd_date8/upd_new31 بالثلاث) + KNOWLEDGE_BASE.md + USER_GUIDE.md + openapi.yaml + AGENTS.md + إعادة بناء Nuitka (82MB) + Inno Setup (51.6MB) + ZIP المحمول (83MB) كـ v3.1.7 + إنشاء GitHub release v3.1.7 برفع assets | ✅ **1786** اختبار + تغطية وحدات **100%** |
| 63 | 2026-08-03 | **مراجعة مواد الدفاع إلى v3.1.7 (Goal: تقرير الدفاع يعكس الحالة النهائية)**: تحديث `docs/generate_report.py` — الإصدار v3.1.6→v3.1.7 (غلاف + الملخص + الجلسات v3.1.3→v3.1.7) + 1350→**1786** اختبار (6 مواضع) + قسم جديد **13.12 UAT الشامل (v3.1.7)** (رحلة مستخدم عبر 35 شاشة + إصلاح بغّ تبديل اللغة `_clear_layout`) + تحديث أحجام المثبّتات (Setup 51.6MB / ZIP 82.9MB) + إعادة توليد التقرير: DOCX عبر generate_report.py (52832 بايت) + PDF عبر docx2pdf/Word COM 16.0 (257204 بايت) — التحقق: v3.1.7 ×4 + 1786 ×6 في DOCX | ✅ **1786** اختبار + تغطية وحدات **100%** |
| 64 | 2026-08-03 | **إصلاح «الشاشات الفارغة» في المثبّتات (Goal: exe v3.1.7 المبني يعرض المشاهد)**: مستخدم أبلغ أن الشاشات فارغة في النسخة المثبّتة (بينما المصدر يعمل) — **التشخيص**: التحميل الكسول يستورد المشاهد ديناميكياً (`_lazy_view_factory` في main_window.py:29 عبر `importlib.import_module("ui.views.data_entry")` + `modules/__init__.py:69` PEP 562 `__getattr__`) وNuitka لا يتبّع الاستيرادات الديناميكية بالسلاسل → **لا تُضمَّن وحدات المشاهد الـ35 ولا محرّكات modules** في الـ exe (تحقق: `dist_nuitka/run_ui.dist/ui/` فيه `resources` فقط ولا `views`) → عند الدخول يصل `_get_or_create_view(1)` فيفشل استيراد `ui.views.data_entry` فيبقى الـ placeholder الفارغ (سجل المثبّت: `User logged in` من user_manager فقط بلا أي سطر main_window)؛ **الإصلاح**: إضافة `--include-package=ui.views` + `--include-package=ui.resources` + `--include-package=modules` إلى build_nuitka.py + إصلاح build_nuitka.bat ليستدعي build_nuitka.py (كان يحتوي أمراً قديماً مكرراً بدون الإصلاح) + إعادة بناء Nuitka (exe **143MB** بدل 82MB) + Inno Setup (**66.9MB**) + ZIP محمول (**109MB**)؛ **التحقق**: دخول فعلي عبر UI Automation على الـ exe المحدّث نجح — `User logged in: admin` → `Lazy-loaded view: data_entry (index=1)` → `User logged in: admin (admin)` بلا أخطاء + تحميل dashboard/tax/audit/reports/chat/cost_center/budgeting/ledger/partners/invoicing/payroll/user_testing/cloud_sync/demo_data/ai_insights في الـ ZIP + كل مصانع المشاهد الـ35 `_get_or_create_view` تنجح من المصدر | ✅ **1786** اختبار + تغطية وحدات **100%** |
| 65 | 2026-08-03 | **إصلاح مشاكل الـ v3.1.7 الخمس المتبقية (Goal: حسم كل بلاغات المستخدم على النسخة المثبّتة)**: (1) **الشاشات الفارغة في التثبيت الفعلي** — الجذر الحقيقي: التثبيت الحالي وصل ناقصاً ملفات حرجة من الترقية (Setup-v3.1.6 = 319 ملفاً: لا sqlite3.dll/_sqlite3.pyd ولا pandas/_libs ولا pytz/zoneinfo) بينما Setup-v3.1.7 كامل (985 ملفاً) — نُسخت الملفات المفقودة من dist إلى التثبيت + تحقق UI Automation أن dupont/benchmarks/advanced_dashboard/cloud_sync/user_testing/ledger/inventory/payroll/budgeting تُحمَّل كلها بلا exceptions.log؛ (2) **DuPont (4) يتجمّد عند العودة** — سببه ملفات numpy/matplotlib الناقصة في التثبيت (analysis_view.py يستوردها في الأعلى) — بعد النسخ تحقّق آلي بدورة عودة مزدوجة (dashboard→dupont→dashboard→dupont→dashboard): كل نقر ~0.6s بلا تجمّد ولا استثناءات؛ (3) **أرقام تظهر قبل الإدخال** — `data_entry.py::_make_spin()` كان يعرض `0.00` في كل الحقول المالية قبل الإدخال — أصبح `setSpecialValueText(t("de_enter_amount"))` (مفتاح i18n جديد `de_enter_amount` ×3 لغات = 1925 مفتاحاً) تُعرض تسمية «أدخل المبلغ» بدل 0.00 + اختبار انحدار `test_financial_spins_show_empty_before_input`؛ (4) **التحديث يطلب سرّية جديدة** — الجذر: `installer.iss` كان ينسخ `dist_nuitka\run_ui.dist\*` بـ `ignoreversion` فيضمّن users.json (بـ must_change_password الافتراضي) + settings.json + accounting_data.json + DB — عند الترقية تُستبدل بيانات المستخدم → يُطلب تغيير السرّية؛ **الإصلاح**: `Excludes` في [Files] تستثني users.json/settings.json/accounting_data.json/chat_history.json/login_session.json/activity_log.json/accounting_platform.db/templates\custom_templates.json + مجلدات logs/data/backups (التطبيق يتحمّل غيابها ويُنشئها: `_safe_read` يرجع الافتراضي + `create_tables()` تنشئ DB) — **التحقق الحقيقي**: تثبيت صامت نظيف = 975 ملفاً بلا أي ملف حالة + تشغيل أُنشئ users.json/accounting_data.json ودخول admin نجح + تثبيت ترقية فوق تثبيت سابق حافظ على users.json الحقيقي حرفياً (قبل/بعد متطابقان)؛ إعادة بناء Nuitka (exe **143MB**) + Inno Setup (**66.9MB**) + ZIP محمول (**109.4MB**، 973 ملفاً بلا ملفات حالة) | ✅ **1787** اختبار + تغطية وحدات **100%** |
| 66 | 2026-08-04 | **معالجة ملاحظات تحليل المشروع السبع (Goal: رفع جودة البنية + تحقق قابل للقياس)**: (1) **تلوّث git** - git rm --cached لـ .vault_salt + accounting_data.json.bak + activity_log.json + nuitka-crash-report.xml (-32,652 سطراً) + توسيع .gitignore (chat_history.json/login_session.json/*.db-shm/*.db-wal/artifacts/)؛ (2) **مخلفات الجذر** - سجلات Nuitka والاختبارات نُقلت إلى artifacts/ وحُذفت tmp*/file.txt/tunnel_*؛ (3) **ترويسة PROJECT_MAP** - قسم «آخر حالة» + EXECUTION LOG برموز ✅/🔶/⛔؛ (4) **اختبارات أداء** test_startup_perf.py (4: إقلاع ≤3s فعلي 44ms + مشاهد ≤1.5s فعلي 95-402ms + ذاكرة ≤700MB فعلي 45MB - حدود متسامحة)؛ (5) **CI** .github/workflows/ci.yml (ubuntu-latest + Python 3.11 + libegl1/libgl1/libxkbcommon0/libdbus-1-3/xvfb + xvfb-run pytest tests -q + تغطية معلوماتية فقط دون --fail-under=100)؛ (6) **تفكيك setup_ui الست العملاقة** إلى دوال _build_* (data_entry 350->27/settings 261->15/scenarios 224->28/analysis 217->31/benchmarks 212->24/user_testing 192->9 - إعادة ترتيب صرفة + تحقق 245 passed لكل ملف)؛ (7) **طبقة التصدير الموحدة** ui/exporters.py (new_workbook/add_excel_sheet/ask_save_path/style_header_row/write_charts_pdf - تجميع تكرار 24x getSaveFileName/6x PdfPages/6x PatternFill) + ترحيل 3 شاشات (advanced_dashboard/ai_insights/cost_center_profitability -180 سطر boilerplate بمخرجات مطابقة) + 9 اختبارات test_exporters.py | ✅ **1800** اختبار + تغطية وحدات **100%** |
| 67 | 2026-08-04 | **حزمة مذكرة الماستر (thesis/) (Goal: تجهيز مواد الدفاع الأكاديمية)**: إنشاء `thesis/` بوثائق مذكرة شاملة وفق الميكانيزم الوطني (القرار الوزاري 1275 لـ 27/09/2022 «شهادة ↔ مؤسسة ناشئة/براءة اختراع» + قرار 29/12/2014 لاجتماعات المذكرة) — OUTLINE.md (I-X بأهداف/أشكال/جداول/تسجيل أرقام + 1800 اختبار/35 شاشة/37 وحدة) + INTRO_DRAFT.md (مقدمة ~3 صفحات بحقائق موثّقة: 1.36 مليون PME نهاية 2022/95% من المنشآت/>70% اليد العاملة/أربع 28 لكل 1000 + معدلات فعلية من modules/tax_config.json: IBS 19/23/26%، TVA 19/9/6/0%، IRG 0-35%، CNAS 33.5%، CNAC 2%، VF 2% + ورقة تحقق) + LITERATURE_REVIEW_FRAMEWORK.md (استراتيجية بحث مصفوفات 2.1-2.5 + فجوات G1-G5) + STYLE_GUIDE.md + REFERENCES_TEMPLATE.md (APA 7th + نصوص تنظيمية) + generate_template.py مولّد DOCX وفق المواصفات (A4/هوامش ربط 3سم/TNR 12/سطر 1.5/ترقيم روماني-عربي/حقل TOC/غلاف/ملخصات 3 لغات/8 فصول/ببليوغرافيا/ملاحق) → thesis_template.docx (40,934B، تحقّق: 8 فصول + مقطعين + Word COM يفتحه) | ✅ tools وثائق المقالات (لا اختبارات — توثيق فحسب) |
| 68 | 2026-08-04 | **سكربت فيديو تعليمي + عروض مرئية (Goal: محتوى تسويقي + تعليمي للمستخدمين)**: `docs/VIDEO_TUTORIAL.md` (سكربت كامل 12-15 دقيقة / 9 فصول / VO + overlays + shot list) + `docs/VIDEO_STORYBOARD.md` (shot list تفصيلي 11 مشهداً / overlay style guide / موسيقى مقترحة) + `thesis/generate_slides.py` مولّد 11 شريحة PNG 1920×1080 (Pillow + Amiri Arabic) → `thesis/video_slides/slide_*.png` — يغطي كل الشاشات الـ35 + اختصارات Ctrl+1-0/F2-F12 + النظام الجبائي الكامل (IBS/TVA/IRG/CNAS/CNAC/VF + التقويم + الإقرارات) + الرؤى الذكية (3 طرق تنبؤ + كشف شذوذ + توصيات) + المزامنة السحابية + التصدير (PDF/Excel) — نصوص VO بالإنجليزية + إشارات اختصارات عربية/إنجليزية + إرشادات إنتاج (OBS/Camtasia/DaVinci) | ✅ tools وثائق التسويق |
| 69 | 2026-08-04 | **تحسين الفيديو حسب ملاحظات المستخدم (Goal: جودة العرض)**: إصلاح اتجاه النص في الشرائح — إضافة `arabic_reshaper` + `python-bidi` (نص عربي مشكّل متصل RTL + إنجليزي LTR عبر غلاف `_SmartDraw` يعيد تشكيل أي نص عربي تلقائياً) + إعادة توليد 11 شريحة + إضافة موسيقى خلفية مولّدة برمجياً (أكورد Cmaj7 + ألحان هادئة + fade in/out) عبر `AudioArrayClip` → `SmartAccounting_Tutorial.mp4` (76 ثانية / 1080p / 24fps / صوت AAC) — تحقق المستخدم: «محتوى عجبني» | ✅ تعديل عرض (لا اختبارات جديدة) |
| 70 | 2026-08-04 | **مراجعة شاملة للجاهزية + إصلاحات ISO 9001 (Goal: شهادة ISO)**: مراجعة شاملة (مشروع/فيديو/توثيق) كشفت: (1) اختبار واحد فاشل — `pypdf` ناقص في requirements-dev.txt → أُضيف `pypdf>=4.0,<6.0` و1800/1800 ناجح؛ (2) CI كان يثبّت `requirements.txt` فقط فـpypdf مفقود في GitHub Actions → `pip install -r requirements-dev.txt`؛ (3) pyproject.toml كان 2.1.0 → 3.1.7 + README badge 1.0.0 → 3.1.7 + محتوى README محدّث (35 شاشة/20 نسبة/بنية حالية)؛ (4) USER_GUIDE + KNOWLEDGE_BASE 29 → 35 شاشة (أضيفت شاشات 30-35 باختصاراتها F10/F11/F12/Ctrl+Shift+B/C/D) + index.html meta 27 → 35؛ (5) وثائق ISO جديدة — `docs/QUALITY_POLICY.md` (بيان + 9 أهداف قابلة للقياس + مخاطر + سجلات ISO 9001) + `CHANGELOG.md` (v3.0.0 → v3.1.7 كامل)؛ (6) تنظيف 274MB مخلفات (zips v3.1.1/3.1.2 + cloudflared.exe + Setup-v3.0.0.exe من docs/)؛ (7) جلب الوسوم البعيدة v3.0.0/v3.1.3/3.1.4/3.1.6/3.1.7 — v3.1.5 لم يكن له commit مستقل (دُمج في a2e6cd2) → توثيق traceability note في CHANGELOG | ✅ 1800/1800 + توثيق |
| 71 | 2026-08-04 | **استكمال ملف الجودة ISO بند 8.1 (Goal: اكتمال شروط الشهادة)**: `docs/DEVELOPMENT_METHODOLOGY.md` — منهجية تطوير موثقة تعكس الممارسات الفعلية (نموذج تكراري موجّه بالأهداف) — دورة حياة الميزة (تحليل تأثير ← تصميم DRY ← تعديل جراحي ← TDD ← مجموعة كاملة ← توثيق ← مزامنة الحالة ← Conventional Commit) + الأدوار + معايير القبول (Definition of Done) + إجراءات عدم المطابقة (RCA + اختبار انحدار + تسجيل) + إدارة التكوين والإصدارات + تتبع الإصدارات — رُبطت في KNOWLEDGE_BASE.md (قسم ISO) + QUALITY_POLICY.md (إدارة السجلات) — **نتيجة CI التحقق: GitHub Actions أخضر (1800 passed, 27.8s)** | ✅ توثيق (لا اختبارات جديدة) |
| 72 | 2026-08-04 | **طلب براءة اختراع INAPI (Goal: حماية قانونية للابتكار)**: `thesis/PATENT_APPLICATION.md` — ملف براءة اختراع كامل بالفرنسية (لغة INAPI المعيارية) — العنوان: Système et procédé automatisé d'analyse financière conforme à la fiscalité algérienne intégrant IA pour PME — 10 قسم (domaine technique / état de l'art G1-G5 / exposé inventif / description détaillée 5 figures / 10 revendications indépendantes+-dependantes / résumé / dessins / données prototype / novéauté / appel de protection) — الملفات المحمية: TaxEngine (IBS/TVA/IRG/CNAS/CNAC/VF + calendar + pénalités) + CalculationEngine (20 ratios + Z-Score) + AIInsightsEngine (forecasting 3 méthodes + anomalies z-score/IQR + alertes) + FinancialAnalyzer (DuPont decomposition) + BenchmarkEngine (7 sectors × 10 ratios) + ScenarioAnalyzer (3 scenarios + Tornado) + Security (PBKDF2/AES-256/2FA/4 roles) + CloudSync (AES-GCM + SHA-256 checksum) + i18n (1925 keys × 3 + RTL) + lazy loading (44ms) + SQLite WAL | ✅ وثائق (لا اختبارات) |
| 73 | 2026-08-04 | **إصدارات النظام الجبائي السنوية (Goal: مواكبة نشرة DGI 2026)**: تحليل نشرة DGI الرسمية `Downloads/النظام-الجبائي-الجزائري-2026.pdf` (43 صفحة) → تصحيح شرائح IRG 2026 (0/23/27/30/33/35% بحدود 240k/480k/960k/1920k/3840k بدل القديم الخاطئ 0/20/30/35% بحدود 120k/360k/1440k) + إضافة النظم المفقودة: **IFU** (ضريبة جزافية وحيدة — 0.5% مقاول ذاتي/5% إنتاج/12% أخرى، حد أدنى 30,000 دج) + **رسم التكوين المهني والتمهين** (1% × 2 من كتلة الأجور قابلة للخصم بالميزانية المنفقة) + **الاقتطاع من المصدر على الإيجارات** (7% سكني/15% تجاري مهني + اقتطاع مؤقت 7% فوق 1.8M) + `modules/tax_years.py` (إدارة السنوات: list/load/save/copy/delete/validate/import-export JSON، مجلد `modules/config_years/`، مؤشر `.active_year`) + ملفّا `tax_config_2025.json` و`tax_config_2026.json` وفق النشرة + تبويب «سنوات النظام» في TaxView (مبدّل سنوات + محرر JSON مع تحقق/استيراد/تصدير + حاسبات IFU/تكوين/إيجار) + **دمج عميق** مع الافتراضية كي تعمل الملفات القديمة (تنسيق 2025 المنسوخ من القالب القديم بلا أقسام جديدة) + i18n 1986 (+61 ×3) (tax_years.py, tax.py, tax_view.py) | ✅ **1862** اختبار (62 في test_tax_years.py) |
| 74 | 2026-08-04 | **رفع الإصدار إلى v3.1.8 (Goal: نشر ميزة النشريات الجبائية السنوية)**: رفع `config.py` APP_VERSION + `i18n.py` window_title ×3 لغات + `installer.iss` + `build_nuitka.py` (product/file version) + `pyproject.toml` إلى 3.1.8 + تحديث docs/version.json (changelog v3.1.8 + download/installer URLs v3.1.8) + docs/index.html (badge + softwareVersion + روابط التحميل + سجل v3.1.8 مع upd_date9/upd_new34/upd_new35 + 1862 اختبار) + docs/script.js (hero_badge ×3 لغات + upd_date9/upd_new34/upd_new35 بالثلاث) + README badges (version/tests) + KNOWLEDGE_BASE.md + USER_GUIDE.md + API_REFERENCE.md + openapi.yaml + QUALITY_POLICY/DEVELOPMENT_METHODOLOGY (1800→1862) + CHANGELOG (v3.1.8 أعلى السجل — نُقلت إضافة النشرة الجبائية من ضمن v3.1.7 إلى v3.1.8) + AGENTS.md + إعادة بناء Nuitka + Inno Setup + ZIP المحمول كـ v3.1.8 + إنشاء GitHub release v3.1.8 برفع assets | ✅ **1862** اختبار + تغطية وحدات **100%** |
| 75 | 2026-08-05 | **التحسينات الأساسية بعد موافقة صاحب المشروع (Goal: نظافة كود + مثبّتات مطابقة + ترقية آمنة + توثيق حي)**: (1) **تنظيف الاستيرادات غير المستخدمة** — أداة `clean_imports2.py` (AST) أزالت **105 استيرادات** غير مستخدمة عبر 40 ملفاً (modules + ui) + `shutil` الزائد من tax_years.py (commit adaddfb) — بقيت استيرادات `_ # noqa: F401` المقصودة في ui/views/_path.py + 115 ملاحظة old غير مستوردة لم تُلمس (التعديل الجراحي) → **1862 اختبار ناجح + تغطية modules 100% (7233 سطراً، 0 مفقود)** بعد التنظيف إعادة بنية Nuitka (exe يعمل 137MB)؛ (2) **إعادة بناء المثبّتات لتطابق الريبو**: Nuitka → Inno Setup (ISCC — SmartAccounting-Setup-v3.1.8.exe **63.8MB**) + ZIP محمول (SmartAccounting-v3.1.8-win64.zip **104.3MB**)؛ (3) **اختبار مسار الترقية v3.1.7→v3.1.8 الفعلي** (upgrade_test.py + /DIR= بلا مسؤول): تثبيت نظيف v3.1.7 → بذر users.json/settings.json/accounting_data.json بمستخدم حقيقي → تثبيت v3.1.8 فوقه → **ملفات الحالة متطابقة بايت-بايت (SHA-256 قبل/بعد) + تسجيل دخول المستخدم على v3.1.8 نجح** (`User logged in: admin` + `Lazy-loaded view: data_entry`) — تأكيد أن Excludes في installer.iss تحفظ بيانات المستخدم فعلاً (ملاحظة: SAC مفعّل Enforcement على جهاز التطوير يحجب المثبّت غير الموقّع عند التثبيت في Program Files — الحل: /DIR= مكتب مستخدم أو سكربت allow_smart_app_control.ps1)؛ (4) **مزامنة أرقام الوثائق الحية**: script.js hero_badge EN/FR v3.1.7→v3.1.8 (كانت العربية 3.1.8 فقط) + QUALITY_POLICY.md + DEVELOPMENT_METHODOLOGY.md (v3.0.0→v3.1.7 أصبحت →v3.1.8) — وثائق thesis/ والفيديو بقيت v3.1.7/1800 عمداً (snapshots الدفاع / مواد الفيديو المولّدة) | ✅ **1862** اختبار + تغطية وحدات **100%** |
| 76 | 2026-08-05 | **التوحيد الشامل لتباعد الواجهات (Goal: UI احترافي متناسق عبر الشاشات الـ35 والثيمات الثلاثة)**: (1) **Audit AST** لكل استدعاءات setSpacing/setContentsMargins في ui/views/*.py (39 ملفاً) + تصنيف الاستثناءات المقصودة (أغلفة QScrollArea بـ (0,0,0,0)+spacing 0 في analysis/scenarios/data_entry + صف كلمة المرور spacing 5 في login — لم تُلمس)؛ (2) **`ui/constants.py` جديد** — المصدر الموحد: SPACING_TIGHT=5/NORMAL=8/MEDIUM=10/LARGE=15/XLARGE=20 + MARGIN_SMALL=5/NORMAL=10/LARGE=15/XLARGE=20 + MIN_HEIGHT_FIELD/BUTTON=40 + PAGE_MARGINS=(20,20,20,20)+PAGE_SPACING=15 + CARD_MARGINS=(16,12,16,12)+CARD_SPACING=10 + STAT_MARGINS=(16,12,16,12)+STAT_SPACING=8 + FORM_MARGINS=(15,10,15,10)+FORM_SPACING=8 + **`apply_standard_layout(layout, level)`** (page/card/stat/form)؛ (3) **`ui/views/_base.py`** على المعايير (17 شاشة ترث BaseView تلقائياً) + توحيد التباعد الضيق 3-5→8 في 9 شاشات (audit ×2/advanced_dashboard/dashboard/analysis/scenarios/tax_calendar/tax ×3 نماذج/chat)؛ (4) **الثيمات الثلاثة** (style/dark/modern.qss): اكتشاف نموذج صندوق Qt (min-height يُضاف فوق padding الرأسي — كانت 38+11px = زر 62px) → padding رأسي 0 + min-height 40 → **حقوق مقاسة 42-44px/أزرار 42px موحّدة عبر الثيمات**؛ (5) **QA**: `tests/test_ui_constants.py` (15: ثوابت/مستويات/BaseView/منع spacing<5 خارج أغلفة التمرير عبر AST — فشل أولاً على analysis/scenarios ثم أُصلح) + **Geometry QA** للشاشات الـ35 (كل حقل ظاهر ≥40px وزر ≥38px — استثناء صحيح: الحقول الداخلية لـ QDateEdit/QDoubleSpinBox 18px) + لقطات BEFORE/AFTER (35+35 offscreen 1280×740) بمقارنة pixel-diff (12 شاشة تغيّرت 1-14.5%) + **1877 اختبار + تغطية 100%**؛ (6) **توثيق**: docs/UI_STYLE_GUIDE.md (المرجع الإلزامي) + docs/UI_SPACING_AUDIT_REPORT.md + تحديث «آخر حالة» | ✅ **1877** اختبار + تغطية وحدات **100%** |
| 77 | 2026-08-05 | **المرحلة 1 من التنظيم الشامل للواجهة (Goal: نافذة متكيفة + شريط حالة + جداول/تبويبات موحّدة — بدون المساس ببنية التنقل)**: بعد موافقة صاحب المشروع على النطاق «المرحلة 1 الآمنة أولاً» من Prompt «Complete Application UI/UX Organization & Design» (المراحل 2-3/بنية Header+Sidebar مجمّع مؤجلة): (1) **حجم النافذة متكيف**: `setGeometry(100,100,1440,880)`+`setMinimumSize(1100,650)` أصبحا `QApplication.primaryScreen().availableGeometry()` + حد أدنى متكيف `min(1200, العرض)×min(800, الارتفاع)` — يفتح بحجم شاشة المستخدم (1920×1080 أو حسب دقته) ولا يتجاوز الشاشات الأصغر؛ (2) **شريط الحالة 40px** في الثيمات الثلاثة (`min-height:40px` + `QStatusBar::item{border:none}` + `QStatusBar QLabel{color}` حسب الثيم) + **ملصق إصدار دائم** `QLabel#versionLabel = v{APP_VERSION}` عبر addPermanentWidget (نقل استيراد APP_VERSION إلى أعلى main_window.py)؛ (3) **صفوف الجداول 44px برمجياً**: تحقق فعلي أن `min-height` في QSS لا يعمل على `QTableWidget::item` (بقيت 31px) → `MainWindow._normalize_table_rows()` تستدعي `verticalHeader().setDefaultSectionSize(44)` لكل جدول عند إنشاء المشهد كسولاً (بلا لمّس أي من الشاشات الـ35)؛ (4) **التبويبات**: الفاتح لم يكن يملك قسم QTabWidget/QTabBar (كان افتراضياً) → أُضيف (pane بإطار #E8ECF1 + tab بـ#ECF0F1 + المحدد أبيض بحد سفلي أزرق #3498DB)؛ (5) **شريط التمرير الأفقي** أُضيف للفاتح (كان عمودياً فقط) بنفس نمط العمودي؛ (6) **QA**: 260 واجهة (test_ui/test_ui_views/test_uat/test_ui_constants/test_startup_perf) ناجحة أولاً بعد إصلاح استيراد QApplication (كان داخل دالة) → **1877 اختبار + تغطية 100%** + تحقق برمجي (نافذة 800×600 أوفسكرين متكيفة، شريط 41px، versionLabel v3.1.8، صفوف tax 44×2) + لقطة | ✅ **1877** اختبار + تغطية وحدات **100%** |
| 78 | 2026-08-05 | **Module 1 تجاري: الترخيص والتفعيل (Goal: أساس الاشتراكات الآمن — بدون قفل أي ميزة بعد)**: بعد موافقة صاحب المشروع على Prompt v4.0 Commercial Build (Module 1 الآن + **PyInstaller** بدل Nuitka — هجرة أداة البناء جلسة مستقلة لاحقاً + تأجيل النشر الرقمي لعدم وجود حسابات رسمية) — **commercial/licensing/**: `license.py` (RSA-2048 PKCS1v15 SHA-256، توقيع حمولة JSON canonical (tier/licensee/expiry/hwid/issued/uid)، تنسيق المفتاح `base64(payload)---base64(signature)` مجمّعاً بخانات 5 أحرف — الصيغة البشرية XXXX-XXXX-XXXX-XXXX-XXXX في الـ prompt لا تحمل توقيعاً 256 بايت (موثّق) + تحمّل whitespace في اللصق + `=` padding) + `hardware_id.py` (SHA-256 من MAC+CPU+serial مع fallbacks دفاعية + lru_cache لأن قرص WMI يضيف ~0.5-1s) + `expiry.py` (مهلة **14 يوماً** ثم **read-only**) + `tier.py` (FREE/PRO/ENTERPRISE + `feature_enabled()` — بوابات جاهزة بلا قفل فعلي: cloud_sync/multi_device=PRO، ai_unlimited/api_access/audit_trail=ENTERPRISE، المجهول مفتوح افتراضياً) + `activation.py` (LicenseStore: challenge/حفظ ذرّي license.dat/is_read_only) + `keygen.py` CLI للبائع فقط (`--new-keypair/--sample/--hwid/--tier/--days/--licensee`) — المفتاح الخاص في `commercial/keys/` (gitignored) والمفتاح العام مضمّن `pub_key.pem` (متعقّب) + 5 مفاتيح تجريبية مقابل `SAMPLE_HARDWARE_ID="0"*64` في sample_keys.txt (كلها تتحقق بالمفتاح المضمّن) + `license_dialog.py` (حوار لصق مفتاح ← تفعيل ← إعادة تشغيل — المنطق في دوال نقية `describe_license/try_activate` لأن **QDialog لا يُبنى تحت pytest على هذا الجهاز** (تحقق بمسبار minimal: QWidget يعمل، QDialog يتجمّد حتى مع QApplication(sys.argv))؛ الفئة `# pragma: no cover` موثّقة) + ربط في main_window (Help ← menu_license ← show_license_dialog) + `run_ui.py::_nudge_license_check` يعرض الحوار عند الإقلاع **فقط** عندما is_read_only() (بعد المهلة) وبحماية try/except كاملة؛ i18n **2007** (+21 ×3)؛ استبدال اختبارات الحوار الـ5 بدوال نقية → **67 اختباراً + تغطية 99%** على الحزمة (2 سطر فقط غير مغطى: passthrough _group + سطر print) + **1944 اختباراً كاملاً** + docs/COMMERCIAL_MODULE1_SUMMARY.md + commercial/licensing/README.md + CHANGELOG.md؛ تحقق من افتراضات الـ prompt: api_key فارغ أصلاً (لا Module 5 تنظيف الآن)، cloud_sync محلي سليم، لا LICENSE في الجذر، users.json schema مختلف (admin@accounting.local) | ✅ **1944** اختبار + تغطية وحدات **100%** |
| 79 | 2026-08-05 | **Module 2 + 3 تجاريان: التشفير والبوابات (Goal: تشفير التخزين + تفعيل الطبقات فعلياً)**: بعد موافقة صاحب المشروع على النطاق «Module 2 + 3» (النشر الرقمي ما زال مؤجلاً لحين الحسابات الرسمية) — **Module 2** `commercial/encryption/`: `kdf.py` (**Argon2id** من `cryptography` المدمج — صفر تبعيات جديدة؛ افتراضيات OWASP 64MiB/3/1) + `filecrypt.py` (تنسيق ذاتي الوصف `SACF1|kdf_id|mc|tc|par|salt_len|nonce_len|salt|nonce|ct||tag` — **الـ tag يصادق على الرأس كاملاً (AAD)** فأي تلاعب بأي بايت (حتى معاملات KDF) يفشل، والرسالة نفسها لكلمة مرور خاطئة/تلاعب بلا oracle + كتابة ذرّية للملفات) + **دمج في cloud_sync**: `encrypt_payload` أصبح Argon2id بملح عشوائي لكل ملف و`decrypt_payload` يكشف التنسيق ويرجع تلقائياً لمسار PBKDF2 القديم — **سنابات قديمة تبقى تعمل** (تحقق بسناب قديم مصنوع يدوياً)؛ تأجيل مقصود موثّق: تشفير accounting_data.json يكسر التصدير/النسخ/المزامنة (التبني مع الوحدة المالكة)، license.dat يبقى نصياً (ذاتي التحقق)؛ **Module 3** `commercial/entitlement.py`: `current_tier()` (ملف الترخيص → الطبقة، FREE عند الغياب/التلف) + `required_tier()` + `feature_allowed()` + `set_store()/reset()` للاختبارات والربط — **البوابات مفعّلة فعلياً**: `cloud_sync` (**PRO**) على push/pull في CloudSyncView (النسخ الاحتياطي المحلي/الوجهات/السجل/كلمة المرور تبقى FREE — أمان محلي ≠ سحابة) + `ai_unlimited` (**ENTERPRISE**) يُزيل التنبؤ 6 أشهر ويمنع تصدير PDF/Excel في AIInsightsView (FREE تحتفظ بتحليل 3 أشهر) + رسالة مرفوضة مترجمة باسم الميزة والطبقة + تلميح «مساعدة ← الترخيص» عبر `show_feature_denied` في ui/widgets/messages.py؛ لا أسطح بعد (موثّق): multi_device/api_access/audit_trail؛ i18n **2011** (+4 ×3)؛ دروس مسجلة: بناء QWidget بدون `QApplication(sys.argv)` يهشم pytest (درس Module 1 يتكرر) + `QMessageBox.warning` غير المعمّى يحجب 116s في offscreen؛ **47 اختباراً جديداً** (30 تشفير + 17 بوابات بترخيص PRO/ENTERPRISE حقيقي) → **1991 اختباراً كاملاً + تغطية modules 100% + commercial 99%** + docs/COMMERCIAL_MODULE2_3_SUMMARY.md + commercial/encryption/README.md + CHANGELOG.md | ✅ **1991** اختبار + تغطية وحدات **100%** |

| 80 | 2026-08-05 | **ميزة «تذكرني» (حفظ الحساب وكلمة السر، Goal: إلغاء طلب الدخول كل إقلاع)**: بعد ملاحظة المستخدم أن التطبيق يطلب الدخول كل مرة — خانة اختيارية login_remember_me في شاشتي الدخول والتسجيل (تنقل حالتها من التسجيل إلى الدخول عند العودة) — عند تفعيلها تُحفظ الجلسة في ui/login_session.py **مشفّرة AES-256-GCM (commercial/encryption) بمفتاح SHA-256 لبصمة العتاد** (hardware_id.fingerprint): كلمة السر **لا تُكتب نصاً أبداً** (اختبار فحص ثنائي للملف)، والجلسة تعمل على جهاز التخزين فقط — جهاز آخر/ملف منقول → يُبقى البريد فقط ويفشل الدخول التلقائي بأمان؛ login_session.json القديم (بريد فقط) يبقى مدعوماً + تحقق سريع بـ fingerprint_hash قبل الـ Argon2id + KDF أخف للجلسة (16MiB/1) لسرعة الإقلاع؛ **auto-login في MainWindow** عند الإقلاع (QTimer.singleShot) مع حراسة: لا دخول تلقائي عند must_change_password (يُسجَّل الخروج) ولا عند 2FA/كلمة خاطئة/فشل فك التشفير (يبقى على شاشة الدخول) + _do_logout يستدعي clear_saved_password() (يمسح كلمة السر ويبقي البريد)؛ i18n **2012** (+1 ×3)؛ **29 اختباراً جديداً** (`tests/test_login_remember.py`: تخزين/فك/جهاز آخر/ملف تالف/حالة الخانة/auto-login/لوغاوت — درس: insertWidget يزيح فهرس QStackedWidget فالمساواة مع مسار الدخول اليدوي لا رقم ثابت + mock على ui.views.login_view.save_login_session لأن الاستيراد مباشر) → **2020 اختباراً كاملاً + تغطية modules 100% + login_session 100%** + PROJECT_MAP (جلسة 80) |

| 81 | 2026-08-05 | **توحيد ارتفاعات العناصر عبر الشاشات (Goal: معالجة ملاحظة المستخدم «خانات الشاشات غير متناسقة»)**: بعد عرض المستخدم صوراً لعدة شاشات أظهرت تبايناً في ارتفاعات الحقول/الأزرار والهوامش — **Audit AST شامل** عبر 35 شاشة كشف: 51% (18 شاشة) لا تستخدم BaseView + 32 موضعاً بـ 36px بدل MIN_HEIGHT_FIELD=40 + أزرار بـ 38/42/45/48/50px + هامشان رئيسيان منحرفان — **الإصلاحات**: توحيد جميع الحقول والأزرار إلى 40px في 12 شاشة (settings 11 حقل+6 أزرار/advanced_dashboard 3/ai_insights/benchmarks/tax_calendar year+ack/user_testing 10/cost_center_profitability 3/zscore/chat 2/cashflow 2/tax construction+simulate/breakeven/budget/cost_center/dashboard/forecasting/scenarios) + **إصلاح هامشين**: zscore (25,25,25,25)→PAGE_MARGINS (20,20,20,20) وsettings (40,30,40,30)→(20,20,20,20) + spacing 30→15 + **إصلاح تعارض صفوف الجداول الثلاثة**: cost_center_profitability 46→44 / demo_data 42→44 (و setMinimumHeight 42*13→44*13) / user_testing 48→44 (و 48*6→44*6) لتطابق _normalize_table_rows (44px) — لا تغيير لـ login_view (شاشة مستقلة بتصميمها المقصود) ولا لمُلصقات النتائج (zscore result_label=50 عرض مقصود)؛ **QA**: Geometry check برمجي لكل الـ35 شاشة (0 حقول < 38px + كل الشاشات تُحمَّل) + **2020 اختباراً كاملاً** (لم يُكسر أي اختبار) |
| 82 | 2026-08-05 | **المرحلة 2 من توحيد التباعد (Goal: إكمال بقية شاشات التباين)**: بعد طلب المستخدم «كمل باقي شاشات» — فحصا `setContentsMargins` و`setSpacing` لكل الشاشات (باستثناء login_view المقصود) — **التوحيدات**: بطاقات objectName="card" → CARD_MARGINS (16,12,16,12) في 10 شاشات (dashboard ChartWidget+SummaryCard/ratios/analysis 2/advanced_dashboard 4: health+revenue+alerts+custom/scenarios 3/benchmarks score_layout/ai_insights growth_box/cost_center_profitability stat_card/audit stat_card) + مجموعات QGroupBox الصريحة → (15,20,15,15) (settings 7 مجموعات + zscore fields_layout) + إزالة آخر setSpacing(18) (settings ai/email→15) + **حقول الإقرارات الضريبية الستة** في tax_view (decl_* بلا ارتفاع صريح → 40px) + زرّا Undo/Redo في data_entry (36→40) + أداة TableFilterWidget المشتركة (search_input 32→40 — أثرت على tax_view والجهات المستخدمة)؛ **QA**: Geometry check (0 حقول <38px — بعد قياس minimumHeight لا sizeHint الافتراضي 25px) + **2020 اختباراً كاملاً** — **درس**: استبدال جماعي بـ PowerShell كسر أسماء متغيرات layouts (استُعيد الملف من git وأُعيد التعديل لكل موضع عبر أسماء المتغيرات الصحيحة) + Set-Content -Encoding UTF8 يضيف BOM يكسر ast.parse في الاختبارات (أُزيل BOM بالبايتات) |
| 83 | 2026-08-05 | **إصلاحات UI حسب صور المستخدم (Goal: معالجة الشاشات المتداخلة/الضيّقة)**: بعد عرض المستخدم صوراً لخمس شاشات واشتكاء «الخانات صغيرة ومتداخلة ومش باينة» — (1) **اختبار المستخدمين**: بطاقتا الجلسات والملاحظات كانتا QGridLayout بأربعة/ستة أعمدة بلا معاملات تمدد → ضيق وتداخل في RTL → `setColumnStretch(1/3/5, 3)` لأعمدة الحقول + `name_edit` ناقص setMinimumHeight(40) — النتيجة: حقول الجلسات 497px والملاحظات 320px بارتفاع 40px موحّد؛ (2) **التقويم الجبائي**: جدول upcoming_table كان QHeaderView.Stretch بالتساوي على 7 أعمدة فتُضغط أعمدة النص والتأكيد → Interactive + عمود الاسم Stretch + عروض ثابتة (90/110/80/100/130/120)؛ (3) **التخطيط والمتابعة (budget_view)**: فراغ كبير في النصف — الجدولان input_table (6 صفوف) وresults_table بلا minimumHeight فيتمددان بلا حدود عمودياً → `verticalHeader 44` + `minimumHeight(44*6+30)` + results_table `QSizePolicy.Preferred`؛ (4) **المزامنة السحابية**: فراغ هائل في الأسفل — dest_table/backup_table بلا ارتفاع + `_main_layout.addStretch()` في النهاية → minimumHeight (44*3+30) لكل جدول + إزالة addStretch — **QA**: الشاشات الأربع تُبنى وتُعرض بحجم 1280×800 + حقول 40px بعرض كافٍ + **2020 اختباراً كاملاً** |
| 84 | 2026-08-05 | **مراجعة واستبدال عمل MiniMax على التقويم + إصلاح الإقرارات (Goal: اعتماد نهج مطوّر محترف)**: المستخدم غير مقتنع بعمل MiniMax («دور مطور صحح الخلل واختر الأنسب») — **مشاكل MiniMax المكتشفة**: (1) `card.setStyleSheet("QFrame#card { border-left: ... }")` — anti-pattern يتجاوز QSS الثيم كاملاً للبطاقة (الـ widget-level stylesheet يستبدل قواعد التطبيق لهذا الـ widget)؛ (2) ألوان `#hex` صلبة غير متجاوبة مع Light/Dark؛ (3) تعقيد زائد (border-width ديناميكي/ألوان border غير دلالية). **الإصلاح — استبدال كامل**: (أ) إزالة `_OBLIGATION_COLORS` (hex) واستبدالها بـ `_TAX_TYPE_COLORS` مفاتيح ThemeColors (TVA→info, IBS→error, IRG→warning, CNAS→success, CNAC→info, Accounting→text_secondary, Audit→error)؛ (ب) إزالة `card.setStyleSheet()` تماماً — البطاقات تبقى بثيمها الخالص من QSS؛ (ج) شريط علوي رفيع 3px للأشهر المهمة (IBS/Audit/Accounting) عبر QWidget عادي (لا objectName = لا تعارض مع QSS)؛ (د) تنقيح الكود (إزالة تعليقات MiniMax، تبسيط while loop، حذف border_color/border_width المتغيرين)؛ **إصلاح خامس**: شاشة الإقرارات — نموذج `company_form` QFormLayout كان يفيض بالتسميات العربية الطويلة → `setRowWrapPolicy(WrapLongRows)` + `setFieldGrowthPolicy(AllNonFixedFieldsGrow)` — التسميات تلف بدل التداخل. **QA**: 2020 اختباراً أخضر + 4 شاشات تُبنى + بطاقات 12 متساوية 251px + QSS الداكن/الفاتح محفوظ. **درس**: `setStyleSheet` على widget بـ objectName موجود في QSS التطبيق = خطر تدمير الثيم؛ الأفضل دائماً تجنبها لصالح عناصر عادية (QWidget/QLabel بلا objectName) أو استخدام ThemeColors الدلالية. |
| 95 | 2026-08-16 | **دليل تفاعلي + توزيع الشاشات للفريق (Goal: Help غني بلا كود + إدارة شاشات لكل عضو)**: (1) **دليل الاستخدام التفاعلي** — `ui/views/guide_view.py` (نافذة QWidget بـ 7 تبويبات QTextBrowser + أزرار تنقل سابق/تالي + إغلاق) ومحتوى مستخدم-نهائي كامل (نظرة عامة/بدء سريع/جولة الشاشات/الجباية/AI/الأمان/أسئلة شائعة) — **بدون أي ذكر للكود أو بنية المشروع** (اختبار TDD يرفض `.py`/`def `/`class `/`modules/` في المحتوى) + تسجيل في Help ← menu_guide + i18n +57 ×3 → **6 اختبارات**؛ (2) **توزيع الشاشات لكل عضو** — `user_manager.get_allowed_screens/set_allowed_screens/list_users` (المدير None=كل الشاشات؛ الشاشتان 1و2 إلزاميتان دائماً؛ الحفظ في users.json) + **سجل مركزي** `ui/views/view_registry.py` (المصدر الوحيد لـ39 شاشة — MainWindow يبني المصانع منه + الحوار يستخدمه) + `screens_assignment_view.py` (39 checkbox مع تعطيل 1و2) + مجموعة «المستخدمون والشاشات» في settings (تظهر للمدير فقط + حوار تحذير عند عدم اختيار عضو) + ترشيح `_build_ribbon` + حراسة `_go_to_view` (رفض + log) + إعادة البناء عند الدخول وتصفير عند الخروج + i18n +8 ×3 → **12 اختباراً** (8 وحدة + 4 تكامل MainWindow: عضو مقيّد يرى [1,2,3,9] فقط، الاختصار لا يفتح الممنوع، المدير يرى الكل) → **2061 اختباراً أخضر** — **درس pytest**: إنشاء QApplication داخل setUp حذف كائنات C++ (wrapped deleted) — يُنشأ على مستوى الوحدة كبقية ملفات الواجهة |
| 96 | 2026-08-16 | **توحيد تصميم الشاشات المحاسبية الأربع (Goal: إصلاح تداخل الحقول والجداول في الشاشات 34-37)**: بعد تأكيد المستخدم أن الصور من شاشات الرواتب/الميزانية/المشتريات/الفواتير الإلكترونية — تطبيق نمط الجلسة 85 (عناوين فوق الحقول + صفوف مقسمة + زر محاذاة أسفل): (1) **payroll_view.py** — نموذج إضافة موظف 5 عناصر في صف واحد بلا عناوين → صفّان بعنوانين (اسم+منصب، قسم+راتب) + زر `Qt.AlignBottom` + نموذج تشغيل الرواتب (QLabel inline) → حقلين مسمّيين (شهر+سنة) + صف أزرار منفصل + إضافة `from PyQt5.QtCore import Qt`؛ (2) **budgeting_view.py** — نموذج إضافة بند 5 عناصر في صف واحد → صفّان (سنة+اسم، تصنيف+مبلغ) + زر أسفل + إضافة Qt import؛ (3) **procurement_view.py** — نموذج 3 حقول + زر → صفّان (مورّد+تاريخ، مرجع+زر) + إزالة `stats.addStretch()` (إحصائيات عرض كامل) + إضافة `Qt` لل imports؛ (4) **einvoicing_view.py** — نموذج 3 حقول + زر → صفّان (عميل+رقم ضريبي، تاريخ+زر) + إزالة `stats.addStretch()` + إضافة `Qt` لل imports؛ **TDD**: اختبار `test_form_fields_have_labels` لكل شاشة (يتحقق من ظهور عناوين الحقول فوقها) + فئتين جديدتين TestProcurementView + TestEInvoicingView (4 اختبارات بنية + اختبارات وظيفية) → **6 اختبارات جديدة (4 فاشلة أولاً ثم ناجحة)** → **2071 اختباراً أخضر + صفر تراجعات** |
| 97 | 2026-08-17 | **تمرير عمودي QScrollArea لكل الشاشات (Goal: شاشات قابلة للتمرير لمنع تداخل المحتوى)**: طلب المستخدم — تحليل التأثير: 22 شاشة BaseView + 22 شاشة QWidget مستقلة + لا self.layout() في أي شاشة → تعديل ملف واحد _base.py؛ **التنفيذ الجراحي**: لفّ _main_layout داخل QScrollArea في BaseView.__init__() (outer QVBoxLayout(self) + scroll QScrollArea NoFrame widgetResizable + container QWidget + _main_layout على container) — DRY تعديل واحد يغطي 22 شاشة؛ **TDD**: TestBaseViewScrollArea (4 اختبارات: exists/resizable/no_frame/layout_inside_scroll) — فشلت 4 أولاً ثم نجحت؛ **إصلاح اختبار انحدار**: test_main_layout_uses_page_standard كان يتحقق من view.layout() (outer spacing=0) → أصبح view._main_layout (spacing=15)؛ **2075 اختباراً أخضر + صفر تراجعات** |
| 97b | 2026-08-17 | **تمرير عمودي لـ QWidget + إعادة تشكيل 5 شاشات (Goal: شاشات قابلة للتمرير + حقول غير متداخلة)**: **المكونان**: (1) `wrap_in_scroll()` في `_base.py` — يلف أي view في QScrollArea + `view._wrapped_view` للوصول للمحتوى؛ MainWindow `_get_or_create_view` يستدعيها لكل lazy view + `_go_to_view` يمرّر getattr `_wrapped_view` للrefresh والطباعة؛ (2) **إعادة تشكيل 5 شاشات**: partners_view — نموذج إضافة شريك (5 عناصر صف واحد → صفّان type+name+phone / email+tax_id+btn) + نموذج معاملة (4 عناصر → صفّان date+type / amount+ref+btn) + minHeight للجداول الثلاثة (partners/tx/aging)؛ cost_center_view — results_table minHeight(44*6+30)؛ cost_center_profitability_view — allocate_group (6 عناصر صف واحد → صفّان indirect+method+target / run_btn مع vlayout+stretch) + 6 جداول بـ minHeight؛ tax_view — `_money_input()` helper بـ `setMinimumHeight(40)` + results_table minHeight(44*8+30) + oblig_table minHeight(44*6+30) — **لا اختبارات جديدة مطلوبة (TDD غير وارد — تعديلات UI سطحية)** → **2075 اختباراً أخضر** |

---

## ERRORS FOUND — جلسة اختبار التكامل (2026-08-01)

### مُصلَح
| الملف | السطر | الخلل | الإصلاح |
|-------|-------|-------|---------|
| modules/analysis.py | 338-351 | `working_capital_analysis` يعيد القاموس دون تخزينه في `analysis_results` (بخلاف `dupont_analysis`) → `state.working_capital = {}` دائماً بعد `load_company` + قسم رأس المال العامل في التقرير لا يُملأ أبداً | تخزين النتيجة في `self.analysis_results['working_capital']` |
| database/db_operations.py | 567 | `delete_analysis` يحذف من جدول `notes` عبر `WHERE fiscal_year_id = ?` والجدول لا يحوي العمود (مفتاحه `audit_log_id`) → `no such column` → الحذف يفشل عند وجود سجل notes | حذف notes أولاً عبر `audit_log_id IN (SELECT log_id FROM audit_log WHERE fiscal_year_id = ?)` |
| modules/backup.py | 27-38 | `backup()` ينسخ ملف `.db` فقط بـ `shutil.copy2` في وضع WAL → آخر الكتابات في `-wal` لا تدخل النسخة → **فقدان بيانات صامت** عند الاستعادة | SQLite Online Backup API (`source.backup(target)`) + `close_pool()` قبل استبدال الملف في `restore()` |

### اختبارات صُحّحت (ليست أخطاء منتج)
| الملف | الملاحظة |
|-------|----------|
| tests/test_integration_workflow.py | `check_income_statement` الصارم يفشل مع بيانات الديمو (تتضمن other_income/other_expenses) — اتساقها الحقيقي `operating_income + other_income - other_expenses = net_income`؛ والتحقق من `state.summary()` كان يتوقع مفتاح "summary" |
| tests/test_integration_database.py | إيقاف FK أثناء إسقاط الجداول في setUp؛ كتابة التزامن باتصالات خام لكل خيط (التجمّع مصمَّم لخيط واحد)؛ `test_pool_reuse` أُعيدت كإعادة استخدام تسلسلي |
| tests/test_integration_performance.py | مولّد البيانات لم يتضمن `gross_profit` (مطلوب للمحرك)؛ حساب عدّاد القراءة 1200-1001=199 خاطئ (الصحيح 1199) |
| tests/test_backup.py | اختبارا النسخ البايتي الحرفي حُدّثا للتحقق من صحة SQLite للنسخة (التطابق البايتي كان سلوك الخطأ نفسه في WAL) |

---

## ERRORS FOUND — جلسة التغطية الشاملة (2026-08-01)

### مُصلَح
| الملف | السطر | الخلل | الإصلاح |
|-------|-------|-------|---------|
| modules/comparative.py | 101, 130 | `generate_report()` يرمي `KeyError` إذا غابت نسبة/بند من `ratios_by_year`/`financial_data` (بيانات ناقصة مثل غياب `average_receivables`) | `.get(item, 0)` / `.get(ratio, 0)` |

### موثّق (لم يُلمس — كود قائم يعمل أو يتطلب قراراً)
| الملف | السطر | الملاحظة |
|-------|-------|----------|
| modules/ai_insights.py | — | لا مشاكل؛ 2 سطر فقط من 321 غير مغطّاة سابقاً أُغلقت كلها |
| tests/test_validation.py | 92-100 | اختبار موجود بلا أي `assert` (توثيق فقط — لم يُعدَّل) |

---

## ERRORS FOUND — جلسة التصحيحات النهائية (2026-08-01)

### مُصلَح
| الملف | السطر | الخلل | الإصلاح |
|-------|-------|-------|---------|
| modules/print_manager.py | 33 | `QPageLayout.Landscape` يُستدعى دون استيراد `QPageLayout` → `print_html(landscape=True)` يرمي `NameError` يُبتلع ويعيد `False` (فرع Landscape معطّل) | استيراد `QPageLayout` من `PyQt5.QtGui` داخل block الاستيراد + اختبار `test_print_html_landscape_sets_orientation` |
| modules/bank_sync.py | 130-133 | كشف رأس الملف كان يلتقط أول صف يحتوي أرقاماً كرأس ويُسقط أول معاملة في كل كشف | الكشف الآن: أول صف بلا أرقام = رأس (الصفوف الفارغة تُتخطّى) — لا يُبتلع أي صف بيانات + تحديث `test_import_with_bank_format_success` (count 4) + `test_import_with_bank_format_leading_blank_lines` |
| modules/report_templates.py | 132 | `update_template` على قالب افتراضي يلوّث `DEFAULT_TEMPLATES` العمومي (مرجع مشترك) | `copy.deepcopy` عند دمج الافتراضية في `_load()` + اختبار `test_update_default_template_does_not_corrupt_defaults` |
| modules/reporting.py | 418, 455, 463-472 | عند غياب خط Amiri وتصدير نص عربي: فشل غامض عبر `FPDFException` | فحص صريح قبل التصدير: نص عربي + غياب الخط → `False` مع رسالة واضحة في log + اختبار `test_export_to_pdf_arabic_without_font_fails_clearly` |
| modules/update_checker.py | 187-207 | `download_installer` يفتح الملف دون `try/finally` → عند فشل القراءة يبقى الملف مقفولاً/جزئياً على القرص | `try/finally` يُغلق الملف دائماً ويحذف الملف الجزئي عند الفشل + اختبارا `closes_and_removes_partial`/`removes_temp_partial`/`cleanup_*_error_swallowed` |
| modules/update_checker.py | 46-99 | `last_error` لا يُصفَّر بعد نجاح الـfallback → حالة مضللة | تصفير `last_error` قبل `return` الناجح + اختبار `test_success_after_fallback_resets_last_error` (وعدّل `fallback_url_used_after_primary_failure`) |
| modules/user_manager.py | 359 | `token.strip()` في `confirm_password_reset` يرمي `AttributeError` إذا كان `token=None` | `token is None` → `err_reset_invalid_token` + اختبار `test_confirm_password_reset_none_token_returns_invalid` |
| modules/scheduled_backup.py | 179-193 | `restore_backup` لا يستعيد `vault.enc` رغم تضمينه عند الإنشاء | استعادة `vault.enc` + اختبار `test_restore_backup_restores_vault` |
| modules/scheduled_backup.py | 130-133 | `meta["files"]` تُحسب قبل كتابة `meta.json` → القائمة لا تتضمن الملف نفسه | كتابة `meta.json` أولاً ثم إعادة كتابته بفاتح `files` شامل + اختبار `test_create_backup_meta_includes_itself` |
| modules/backup.py | 114-115, 141-150 | `export_all_to_json` كان يبني SQL على الاسم المُبسَّط (`_sanitize_name`) فتفشل الجداول بأسماء خاصة | SQL بالاسم الحقيقي للجدول + التبسيط لاسم الملف فقط + اختبار `test_export_all_to_json_special_table_name` |
| modules/backup.py | 76-83 | `restore()` بلا تحقق من صحة الأرشيف → بايتات فاسدة تُستعاد "بنجاح" | `_is_valid_sqlite()` (رأس 16 بايت + قراءة sqlite_master) قبل أي استبدال + اختبارا `restore_corrupt_backup_returns_false`/`is_valid_sqlite_read_error_returns_false` (وحُدّث `restore_success`/`restore_exception` بأرشيف SQLite سليم) |
| modules/data_import.py | 149-151 | عند فشل `connect()` يُرجَع مبكراً داخل `try` دون `disconnect()` | استدعاء `disconnect()` (محمي) قبل الإرجاع + اختبارا `connect_failure_disconnects`/`connect_failure_disconnect_raises` |
| modules/data_import.py | 129 | تنظيف اسم الجدول لا يرفض الكلمات المحجوزة في SQLite | `_SQLITE_RESERVED` تُرفض قبل التصدير + اختبار `test_export_to_database_rejects_reserved_table_name` |
| modules/currency.py | 59 | `set_base_currency` سطر no-op (يقرأ ويكتب نفس المفتاح قبل تغيير القاعدة) | حذف السطر (السطر 61 يضبط القاعدة الجديدة فعلياً) |
| modules/tax_reminders.py | 290-291 | فرع `except ValueError` ميت (لا يُبنى `datetime` داخل `try` في الحالة السنوية) | استبداله بحارس `if m in monthly` — فرع ميت أُزيل وتغطية الوحدة صارت 100% |
| ui/resources/i18n.py | 7, 1691, 3375 | `window_title` قديم v2.5.0 في اللغات الثلاث | تحديث إلى v3.1.6 (مطابق لـ config.APP_VERSION) |

### مراجعة الأمان (2026-08-01)
| البند | الحالة |
|-------|--------|
| كلمات مرور المستخدمين (users.json) | ✅ PBKDF2-HMAC-SHA256 100k تكرار + salt عشوائي 16 بايت لكل مستخدم + مقارنة ثابتة الزمن `hmac.compare_digest` + هجرة تلقائية من SHA256 القديم |
| كلمة مرور SMTP (email_notifier) | ✅ تُخزَّن مشفّرة عبر `utils.vault` (Fernet/AES-GCM) بمفتاح مشتق من الجهاز + salt ملف |
| مفتاح OpenAI API (app_state) | ✅ مشفّر عند الحفظ/فكّ عند القراءة + إخفاء في حقل الإدخال (QLineEdit.Password مع مفتاح إظهار) |
| كلمة مرور المسؤول الافتراضية (config) | ✅ قابلة للتجاوز عبر متغير البيئة `SAP_ADMIN_PASSWORD` + إجبار تغييرها عند أول دخول (`must_change_password`) |
| روابط التحديثات (update_checker) | ✅ HTTPS فقط (GitHub Pages) |
| حقن SQL | ✅ استعلامات مُعاملات + أسماء جداول مُنقّاة/مرفوضة المحجوزة |

---

## SESSION LOG

| الجلسة | التاريخ | الإصدار | الملفات | المحتوى |
|--------|---------|---------|---------|---------|
| 97c | 2026-08-18 | v3.2.0 | config.py, modules/bank_api.py, modules/backup.py, modules/bank_sync.py, modules/cloud_sync.py, modules/excel_export.py, modules/print_manager.py, modules/tax_reminders.py, modules/update_checker.py, modules/user_testing.py, modules/data_import.py, ui/app_state.py, ui/login_session.py, .bandit, .github/workflows/codeql.yml | **تخفيف أثر Bandit + CodeQL**: إصلاح MD5→SHA-256 في bank_api.py + إزالة كلمة المرور الافتراضية في config.py + إضافة logging لـ 14 try/except pass + ملف .bandit لـ false positives + CodeQL workflow مجاني على GitHub → **0 HIGH** (كان 1) + **183 إجمالي** (117 LOW مقبول + 66 MEDIUM B608 SQL مُعاملات/جداول ثابتة false positive) — **2075 اختباراً أخضر** + push `e806f75` |
