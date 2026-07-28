# PROJECT_MAP.md — المنصة المحاسبية الذكية
> آخر تحديث: 2026-07-28 | الإصدار: v3.1.2

---

## SYSTEM_FLOW — رحلة المستخدم

```
1. شاشة الدخول → LoginView (تسجيل + دخول + استعادة كلمة المرور)
2. MainWindow (sidebar + stacked views + شريط حالة)
3. إدخال البيانات المالية → DataEntryView
4. حساب النسب → CalculationEngine → AppState
5. لوحة التحكم → DashboardView (4 رسوم بيانية)
6. تحليل DuPont + رأس المال العامل → AnalysisView
7. النسب المالية (28 نسبة) → RatiosView
8. التدقيق المالي → AuditView (7 فحوصات)
9. النظام الجبائي الجزائري → TaxView (3 تبويبات)
10. المعايير المرجعية (7 قطاعات) → BenchmarksView
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
```

---

## MODULE MAP — حالة كل مكون

### ✅ CORE (100% — مكتمل)
| المكون | الملفات | الحالة |
|--------|---------|--------|
| config | config.py (v3.1.2) | ✅ |
| database | db_connection.py, db_schema.py (11 tables), db_operations.py | ✅ |
| calculations | modules/calculations.py (28 ratios + تحليل) | ✅ |
| analysis | modules/analysis.py (DuPont, Trends, WC, CashFlow, Benchmarks) | ✅ |
| audit | modules/audit.py (8 checks) | ✅ |
| tax_engine | modules/tax.py + tax_config.json + tax_reminders.py | ✅ |
| benchmarks | modules/benchmarks.py (7 قطاعات × 10 نسب) | ✅ |
| update_checker | modules/update_checker.py (GitHub Pages) | ✅ |
| reporting | modules/reporting.py (PDF عربي + Excel + HTML) | ✅ |
| data_import | modules/data_import.py (Excel/CSV) | ✅ |
| user_manager | modules/user_manager.py (4 أدوار، 16 صلاحية، 2FA) | ✅ |
| demo_data | modules/demo_data.py | ✅ |

### ✅ UI (100% — مكتمل)
| المكون | الملفات | الحالة |
|--------|---------|--------|
| MainWindow | ui/main_window.py (22 view بالـ pyqtSignal للتحديثات) | ✅ |
| AppState | ui/app_state.py (fiscal_year, ratios, companies, settings) | ✅ |
| BaseView | ui/views/_base.py (header + stat cards + tab order) | ✅ |
| LoginView | ui/views/login_view.py (3-step forgot password + 👁 toggle) | ✅ |
| DataEntryView | ui/views/data_entry.py (22 field, showEvent + tab order) | ✅ |
| DashboardView | ui/views/dashboard.py (4 charts + export) | ✅ |
| RatiosView | ui/views/ratios_view.py (28 cards) | ✅ |
| BenchmarksView | ui/views/benchmarks_view.py (radar/bar charts, auto-update on sector change) | ✅ |
| TaxCalendarView | ui/views/tax_calendar_view.py (year selector + monthly overview) | ✅ |
| AnalysisView | ui/views/analysis_view.py (DuPont + WC + CashFlow + Trends) | ✅ |
| AuditView | ui/views/audit_view.py (7 checks) | ✅ |
| TaxView | ui/views/tax_view.py (3 tabs: simulation + calculators + obligations) | ✅ |
| ReportsView | ui/views/reports_view.py (TXT/HTML/PDF/Excel) | ✅ |
| ExportView | ui/views/export_view.py | ✅ |
| ScenariosView | ui/views/scenarios_view.py | ✅ |
| ForecastingView | ui/views/forecasting_view.py | ✅ |
| BreakevenView | ui/views/breakeven_view.py | ✅ |
| SecurityView | ui/views/security_view.py (2FA) | ✅ |
| UserManagementView | ui/views/user_management_view.py (4 roles, 16 permissions) | ✅ |
| ChatView | ui/views/chat_view.py (AI Chat) | ✅ |
| SettingsView | ui/views/settings_view.py (lang + theme + API + fiscal year) | ✅ |
| Style Light | ui/resources/style.qss | ✅ |
| Style Dark | ui/resources/style_dark.qss | ✅ |
| Style Modern | ui/resources/style_modern.qss | ✅ |
| i18n | ui/resources/i18n.py (AR + EN + FR, 300+ keys) | ✅ |

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
│   ├── db_schema.py                 # 11 tables
│   └── db_operations.py
│
├── modules/
│   ├── calculations.py              # 28 financial ratios
│   ├── analysis.py                  # DuPont, Trends, WC, CashFlow
│   ├── audit.py                     # Financial audit checks
│   ├── benchmarks.py                # 7 sectors × 10 ratios
│   ├── tax.py                       # TaxEngine (IBS/TVA/IRG/CNAS/CNAC/VF)
│   ├── tax_reminders.py             # Reminder system + calendar
│   ├── tax_config.json              # Algerian tax rates
│   ├── reporting.py                 # TXT/HTML/PDF/Excel
│   ├── data_import.py               # Excel/CSV import
│   ├── update_checker.py            # GitHub Pages update check
│   ├── validation.py
│   ├── demo_data.py
│   ├── user_manager.py              # Auth + roles + 2FA + reset
│   ├── excel_export.py
│   └── print_manager.py
│
├── ui/
│   ├── main_window.py               # 22 views + pyqtSignal update
│   ├── app_state.py                 # State + settings
│   ├── run_ui.py                    # GUI entry
│   ├── resources/
│   │   ├── i18n.py                  # 300+ keys (AR/EN/FR)
│   │   ├── style.qss / style_dark.qss / style_modern.qss
│   │   └── fonts/ (Amiri 6 variants)
│   ├── widgets/
│   └── views/
│       ├── _base.py / _path.py
│       ├── login_view.py            # 3-step forgot + 👁 toggle + auto-fill
│       ├── data_entry.py            # showEvent + tab order
│       ├── dashboard.py
│       ├── ratios_view.py           # 28 cards
│       ├── analysis_view.py
│       ├── audit_view.py
│       ├── tax_view.py
│       ├── benchmarks_view.py       # auto-update on sector change
│       ├── tax_calendar_view.py     # year selector
│       ├── reports_view.py
│       ├── security_view.py / user_management_view.py
│       ├── chat_view.py
│       ├── settings_view.py
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
│   ├── version.json                 # v3.1.2 update check
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
    ├── test_app_state.py
    ├── test_formatters.py
    ├── test_validators.py
    ├── test_edge_cases.py
    ├── test_tax.py
    ├── test_ui.py                    # UI tests
    ├── test_security.py
    ├── test_demo_data.py
    ├── test_new_modules.py
    └── test_new_features.py
```

---

## TEST SUMMARY (v3.1.2)

| الملف | العدد | الحالة |
|-------|-------|--------|
| test_calculations.py | ✅ | 27 |
| test_audit.py | ✅ | 19 |
| test_analysis.py | ✅ | 14 |
| test_validation.py | ✅ | 13 |
| test_data_import.py | ✅ | 13 |
| test_database.py | ✅ | 7 |
| test_reporting.py | ✅ | 11 |
| test_app_state.py | ✅ | 7 |
| test_formatters.py | ✅ | 16 |
| test_validators.py | ✅ | 24 |
| test_edge_cases.py | ✅ | 31 |
| test_tax.py | ✅ | 19 |
| test_ui.py | ✅ | 42 |
| test_security.py | ✅ | 40 |
| test_demo_data.py | ✅ | 10 |
| test_new_modules.py | ✅ | 24 |
| test_new_features.py | ✅ | 11 |
| **المجموع** | **✅ 351** | |

---

## KEYBOARD SHORTCUTS

| الاختصار | الوظيفة |
|----------|---------|
| Ctrl+Q | خروج |
| Ctrl+R | حساب النسب |
| Ctrl+S | حفظ في DB |
| Ctrl+P | طباعة |
| Ctrl+E | تصدير |
| Ctrl+, | الإعدادات |
| Ctrl+1-9 | التنقل بين الواجهات |

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

| # | التاريخ | الإجراء | النتيجة |
|---|---------|---------|---------|
| 1-31 | 2026-07-13 | v2.0.0 → v2.1.0 (الإصدار الأولي) | ✅ 184 اختبار |
| 32 | 2026-07-27 | v3.0.0 إعادة هيكلة كاملة + 22 شاشة | ✅ |
| 33 | 2026-07-28 | v3.1.0 إصلاح البيانات المالية | ✅ |
| 34 | 2026-07-28 | v3.1.1 UI/UX fixes (5 مشاكل) + تحديث checker | ✅ 322 اختبار |
| 35 | 2026-07-28 | v3.1.2 إصلاح التنقل: سنة التقويم + تحديث المعايير + اختبارات UI | ✅ 322 اختبار |
| 36 | 2026-07-28 | v3.1.2 تحسين التحديث التلقائي: batch script + إعادة تشغيل + إصدار | ✅ 351 اختبار |
