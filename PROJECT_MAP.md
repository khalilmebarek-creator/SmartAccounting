# PROJECT_MAP.md — المنصة المحاسبية الذكية
> آخر تحديث: 2026-07-13 | الإصدار: 2.1.0

---

## SYSTEM_FLOW — رحلة المستخدم

```
1. المستخدم يفتح التطبيق → MainWindow (sidebar + stacked views)
2. يُدخل البيانات المالية → DataEntryView
3. يضغط "احسب النسب" → CalculationEngine → AppState
4. ينتقل تلقائياً → DashboardView (charts) / RatiosView (cards) / AnalysisView (DuPont)
5. يشغّل التدقيق → AuditView → AuditEngine
6. يحفظ في DB → db_operations.save_analysis()
7. يستعرض التقارير → ReportsView → DB queries
8. يُصدّر التقارير → TXT / HTML / PDF export (عربي بالكامل)
9. يتصدير Dashboard كـ PDF → حفظ الرسوم البيانية
10. يستخدم الشات → AI Chat مع المساعد المالي الذكي
11. يحسب الضرائب → TaxView → محرك النظام الجبائي الجزائري
12. يغيّر الإعدادات → اللغة (AR/EN) + الثيم (فاتح/داكن) + API Key
```

---

## MODULE MAP — حالة كل مكون

### ✅ CORE (100% — مكتمل)
| المكون | الملفات | الحالة |
|--------|---------|--------|
| config | config.py | ✅ v2.1.0 |
| database | db_connection.py, db_schema.py (11 tables), db_operations.py | ✅ |
| calculations | modules/calculations.py (14 ratios) | ✅ |
| validation | modules/validation.py | ✅ |
| analysis | modules/analysis.py (DuPont, Trends, WC, CashFlow) | ✅ |
| audit | modules/audit.py (7 checks) | ✅ |
| reporting | modules/reporting.py (5 report types + PDF عربي) | ✅ |
| data_import | modules/data_import.py (Excel/CSV) | ✅ |
| tax_engine | modules/tax.py + tax_config.json (IBS/TVA/IRG/CNAS/CNAC/VF) | ✅ NEW |

### ✅ UI (100% — مكتمل)
| المكون | الملفات | الحالة |
|--------|---------|--------|
| MainWindow | ui/main_window.py (9 views + shortcuts) | ✅ |
| AppState | ui/app_state.py (settings persistence + tax state) | ✅ |
| Style Light | ui/resources/style.qss | ✅ |
| Style Dark | ui/resources/style_dark.qss | ✅ |
| i18n | ui/resources/i18n.py (AR + EN, 170+ keys) | ✅ |
| DataEntryView | ui/views/data_entry.py | ✅ |
| DashboardView | ui/views/dashboard.py (4 charts + export btn) | ✅ |
| RatiosView | ui/views/ratios_view.py (12 cards) | ✅ |
| AnalysisView | ui/views/analysis_view.py (DuPont + WC) | ✅ |
| AuditView | ui/views/audit_view.py (6 checks) | ✅ |
| ReportsView | ui/views/reports_view.py (TXT/HTML/PDF) | ✅ |
| SettingsView | ui/views/settings_view.py (lang + theme + API) | ✅ |
| ChatView | ui/views/chat_view.py (AI chat) | ✅ |
| TaxView | ui/views/tax_view.py (3 tabs: simulation + calculators + obligations) | ✅ NEW |

### ✅ UTILS (100% — مكتمل)
| المكون | الملفات | الحالة |
|--------|---------|--------|
| formatters | utils/formatters.py | ✅ (مُختبَر: 16 اختبار) |
| validators | utils/validators.py | ✅ (مُختبَر: 24 اختبار) |

### ✅ BUGS — ALL FIXED
| ID | الوصف | الحالة |
|----|-------|--------|
| BUG-1 | DataImporter غير مُصدّر من modules/__init__.py | ✅ FIXED |
| BUG-2 | _get_status_text ي-crash لو good_threshold=None | ✅ FIXED |
| BUG-3 | BEGIN يدوي في SQLite يسبب nested transaction | ✅ FIXED |
| BUG-4 | AuditView لا يستدعي check_income_statement | ✅ FIXED |
| BUG-5 | self.refresh_callbacks = [] كود ميت | ✅ REMOVED |
| BUG-6 | print() في calculations.py production code | ✅ REMOVED |
| BUG-7 | PDF لا يدعم العربي (Helvetica) | ✅ FIXED — Amiri font |
| BUG-8 | QPrintDialog في错误的位置 | ✅ FIXED — PyQt5.QtPrintSupport |
| BUG-9 | QPushButton base styling (invisible buttons) | ✅ FIXED — style.qss |

---

## NEW FEATURES — v2.1.0 — النظام الجبائي الجزائري

### 🆕 1. محرك الضرائب (TaxEngine)
- حساب IBS (ضريبة أرباح الشركات): 19% إنتاجي، 23% بناء، 26% أخرى
- حساب TVA (ضريبة القيمة المضافة): 19% عادي، 9% مخفض، 0% معفي
- حساب IRG (ضريبة الدخل على الرواتب): تصاعدية 0/20/30/35%
- حساب CNAS (الصندوق الوطني للتأمينات): 24.5% صاحب عمل + 9% موظف
- حساب CNAC (تأمين البطالة): 1.5% صاحب عمل + 0.5% موظف
- الدفعات المقدمة (Versement Forfaitaire): 2% عادي، 1% بناء
- محاكاة شاملة لجميع الضرائب دفعة واحدة

### 🆕 2. ملف النسب الجبائية (tax_config.json)
- جميع النسب الجبائية الجزائرية قابلة للتعديل
- سهل التحديث السنوي عند تغيير النسب
- يتضمن التقويم الجبائي الشهري والربع سنوي والسنوي
- أنواع النشاط مع النسب المقابلة

### 🆕 3. واجهة النظام الجبائي (TaxView)
- تبويب 1: المحاكاة الشاملة (بيانات مالية → ملخص ضرائب كامل)
- تبويب 2: الآلات الحاسبة (IBS / TVA / IRG / CNAS / CNAC / رواتب)
- تبويب 3: الالتزامات الجبائية الشهرية

### 🆕 4. قاعدة البيانات — جداول جديدة
- جدول `tax_data`: حفظ نتائج المحاكاة الجبائية
- جدول `tax_obligations`: التزامات شهرية مع حالات الدفع

---

## KEYBOARD SHORTCUTS

| الاختصار | الوظيفة |
|----------|---------|
| Ctrl+Q | خروج |
| Ctrl+R | حساب النسب |
| Ctrl+S | حفظ في DB |
| Ctrl+P | طباعة |
| Ctrl+E | تصدير Dashboard PDF |
| Ctrl+, | الإعدادات |
| Ctrl+1-9 | التنقل بين الواجهات (9 = النظام الجبائي) |

---

## FILE STRUCTURE (v2.1.0)

```
Accounting_Platform/
├── main.py                          # CLI entry point
├── config.py                        # Settings (v2.1.0)
├── requirements.txt                 # Dependencies
├── settings.json                    # App settings (auto-generated)
├── PROJECT_MAP.md                   # ← هذا الملف
│
├── database/
│   ├── __init__.py
│   ├── db_connection.py
│   ├── db_schema.py                 # 11 tables (9 original + tax_data + tax_obligations)
│   └── db_operations.py             # + tax save/load/query functions
│
├── modules/
│   ├── __init__.py                  # + TaxEngine export
│   ├── calculations.py              # 14 ratios
│   ├── validation.py
│   ├── analysis.py                  # DuPont, Trends, WC, CashFlow
│   ├── audit.py                     # 7 checks
│   ├── reporting.py                 # Reports + PDF (Amiri font)
│   ├── data_import.py               # Excel/CSV
│   ├── tax.py                       # 🆕 TaxEngine (IBS/TVA/IRG/CNAS/CNAC/VF)
│   └── tax_config.json              # 🆕 Algerian tax rates (JSON, updateable)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # 9 views + shortcuts + theming
│   ├── app_state.py                 # State + settings + tax state
│   ├── run_ui.py                    # GUI entry (v2.1.0)
│   ├── resources/
│   │   ├── style.qss                # Light theme (button fix)
│   │   ├── style_dark.qss           # Dark theme
│   │   ├── i18n.py                  # AR + EN (170+ keys, tax translations)
│   │   └── fonts/
│   │       ├── Amiri-Regular.ttf    # Arabic font
│   │       ├── Amiri-Bold.ttf
│   │       └── Amiri-*.ttf
│   ├── widgets/
│   │   └── __init__.py
│   └── views/
│       ├── __init__.py
│       ├── data_entry.py
│       ├── dashboard.py             # 4 charts + export button
│       ├── ratios_view.py           # 12 cards
│       ├── analysis_view.py         # DuPont + WC
│       ├── audit_view.py            # 6 checks
│       ├── reports_view.py          # TXT/HTML/PDF
│       ├── settings_view.py         # Language + Theme + API
│       ├── chat_view.py             # AI Chat
│       └── tax_view.py              # 🆕 Tax System (3 tabs)
│
├── utils/
│   ├── __init__.py
│   ├── formatters.py
│   └── validators.py
│
└── tests/
    ├── run_all_tests.py
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
    └── test_tax.py                  # 🆕 19 tax tests
```

---

## TEST SUMMARY

| الملف | عدد الاختبارات | الحالة |
|-------|---------------|--------|
| test_calculations.py | 20 | ✅ |
| test_audit.py | 19 | ✅ |
| test_analysis.py | 14 | ✅ |
| test_validation.py | 13 | ✅ |
| test_data_import.py | 13 | ✅ |
| test_database.py | 7 | ✅ |
| test_reporting.py | 11 | ✅ |
| test_app_state.py | 7 | ✅ |
| test_formatters.py | 16 | ✅ |
| test_validators.py | 24 | ✅ |
| test_edge_cases.py | 21 | ✅ |
| test_tax.py | 19 | ✅ 🆕 |
| **المجموع** | **184** | **✅ 100%** |

---

## EXECUTION LOG

| # | التاريخ | الإجراء | النتيجة |
|---|---------|---------|---------|
| 1 | 2026-07-13 | إنشاء المشروع + database + modules | ✅ |
| 2 | 2026-07-13 | إنشاء UI views (6 واجهات) | ✅ |
| 3 | 2026-07-13 | إنشاء utils/ + dashboard + audit_view | ✅ |
| 4 | 2026-07-13 | Fix run_ui.py sys.path | ✅ |
| 5 | 2026-07-13 | Audit شامل — 9 bugs, 6 orphans | ✅ |
| 6-10 | 2026-07-13 | FIX BUG-1 إلى BUG-6 | ✅ |
| 11-13 | 2026-07-13 | Add tests + style improvements | ✅ 165 tests |
| 14-16 | 2026-07-13 | PDF export + reports_view | ✅ |
| 17 | 2026-07-13 | 🆕 PDF عربي (Amiri font) | ✅ |
| 18 | 2026-07-13 | 🆕 Dashboard PDF export | ✅ |
| 19 | 2026-07-13 | 🆕 Print support (Ctrl+P) | ✅ |
| 20 | 2026-07-13 | 🆕 Dark Mode (style_dark.qss) | ✅ |
| 21 | 2026-07-13 | 🆕 i18n system (AR/EN) | ✅ |
| 22 | 2026-07-13 | 🆕 AI Chat (OpenAI API) | ✅ |
| 23 | 2026-07-13 | 🆕 Settings view | ✅ |
| 24 | 2026-07-13 | 🆕 Keyboard shortcuts (1-8) | ✅ |
| 25 | 2026-07-13 | All 165 tests pass | ✅ |
| 26 | 2026-07-13 | 🆕 FIX QPushButton invisible buttons | ✅ |
| 27 | 2026-07-13 | 🆕 TaxEngine (IBS/TVA/IRG/CNAS/CNAC/VF) | ✅ |
| 28 | 2026-07-13 | 🆕 tax_config.json (updateable rates) | ✅ |
| 29 | 2026-07-13 | 🆕 Database: tax_data + tax_obligations | ✅ |
| 30 | 2026-07-13 | 🆕 TaxView UI (3 tabs) + i18n + shortcuts | ✅ |
| 31 | 2026-07-13 | 🆕 19 tax tests — ALL PASS | ✅ 184 tests total |
