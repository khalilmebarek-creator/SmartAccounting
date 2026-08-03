# PROJECT_MAP.md — المنصة المحاسبية الذكية
> آخر تحديث: 2026-08-03 | الإصدار: v3.1.7

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
| tax_engine | modules/tax.py + tax_config.json + tax_reminders.py + tax_reports.py | ✅ |
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
| i18n | ui/resources/i18n.py (AR + EN + FR, 1924 keys) | ✅ |

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
│   ├── tax.py                       # TaxEngine (IBS/TVA/IRG/CNAS/CNAC/VF)
│   ├── tax_reminders.py             # Reminder system + calendar
│   ├── tax_config.json              # Algerian tax rates
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

## TEST SUMMARY (v3.1.7)

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
| **المجموع** | **✅ 1787** | |

> التوزيع: 1547 اختباراً غير واجهة + 116 في test_ui.py + 114 في test_ui_views.py + 9 في test_uat.py (test_bank_print ضمن المجموعة غير الواجهة) — المرجع الرسمي: `python -m pytest tests -q`

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

> **آخر حالة (2026-08-03):** v3.1.7 — **1787 اختباراً** + تغطية وحدات 100% + 1925 مفتاح i18n × 3 لغات. الجدول أدناه سجل تاريخي؛ أرقام الجلسات القديمة تعكس حالتها وقتها.

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
