# Surgical Editing Protocol (بروتوكول التعديل الجراحي)

## الدور والمهمة
Staff Software Engineer. التعديلات تكون جراحية دقيقة دون تخريب الميزات الأخرى.

## قواعد التعديل الجراحي
1. **المس فقط ما يجب لمسه**: لا تحسن تنسيق كود مجاور، لا تعد صياغة تعليقات قديمة، لا تقم بـ Refactoring لكود يعمل ما لم يُطلب.
2. **مطابقة الأسلوب**: التزم بأسلوب الكود الحالي تماماً حتى لو كان غير مثالي.
3. **تنظيف مخلفاتك فقط**: إذا تسبب تعديلك في جعل دالة أو Import "يتيماً"، فقم بإزالته. لا تلمس الأكواد الميتة القديمة.

## بروتوكول التحليل والتنفيذ
1. **تحليل التأثير (Impact Analysis)**: اقرأ PROJECT_MAP.md، حدد الملفات المتأثرة بدقة.
2. **السلامة المعمارية والتجريد**: التزم بـ DRY، استخدم طبقة Shared/Core، أضف Logging للتعديل الجديد.
3. **التحقق والنجاح (Goal-Driven)**: اكتب الاختبار، تأكد من فشله، ثم اجعله ينجح (TDD). تأكد من عدم كسر الاختبارات القديمة.
4. **مزامنة الحالة**: حدّث PROJECT_MAP.md فوراً. أي كود أصبح Deprecated يجب أن يُعالج أو يُسجل.

## قواعد الرفع
- بعد كل تعديل كود، تحديث الموقع (docs/) مطلوب
- بعد كل تعديل، تحديث PROJECT_MAP.md مطلوب
- الإصدار الحالي: v3.1.6

## الحالة الحالية (2026-08-02)
- **إصلاح الشاشة السوداء عند التنقل (جلسة v3.1.6):** `_fade_in_view` في main_window.py كان يخزّن الأنيميشن في مرجع واحد `self._view_anim` فيُتلفف الأنيميشن السابق أثناء طيرانه فيبقى QGraphicsOpacityEffect عند شفافية ~0 دون إطلاق `finished` → شاشة سوداء دائمة على الأجهزة البطيئة؛ الإصلاح — حاوية `self._view_anims` + إيقاف الأنيميشن السابق + `QTimer.singleShot(300)` كضمانة تُزيل التأثير دائماً + حماية من finished متأخر (5 اختبارات واجهة جديدة: TestFadeInSafety)
- **1661 اختباراً كلها ناجحة عبر `python -m pytest tests -q`** (269 محرك جديد: test_ledger 36 + test_partners 50 + test_invoicing 46 + test_inventory 47 + test_payroll 55 + test_budgeting 35 + 42 واجهة في test_ui.py = 115)
- تغطية الوحدات: **100%** عبر `python -m coverage run --source=modules --omit="modules/__init__.py" -m pytest tests -q`
- **المرحلة الثانية — 6 شاشات محاسبية جديدة (شاشات 30-35):** محركات ledger.py + partners.py + invoicing.py + inventory.py + payroll.py + budgeting.py (ميزان مراجعة/تقادم الديون/TVA/متوسط تكلفة/CNAS+IRG/مقارنة الميزانية) + واجهات ledger_view/partners_view/invoicing_view/inventory_view/payroll_view/budgeting_view + ربط في main_window (factories 30-35 + sidebar 35 + اختصارات F10/F11/F12 + Ctrl+Shift+B/C/D) + إصلاح apply_language (sidebar_user_testing المفقودة كانت تحذف شاشة 29 عند تغيير اللغة)
- التوثيق الشامل (جلسة v3.1.6): API_REFERENCE.md أعيدت بصيغة UTF-8 + docs/api/openapi.yaml (OpenAPI 3.0 — 325 عملية، تُعرض في docs/api/index.html) + USER_GUIDE.md (29 شاشة/ممارسات/FAQ) + tutorials/ (4 سكربتات فيديو AI) + KNOWLEDGE_BASE.md (فهرس)
- 20 نسبة مالية في RatiosView + z_score في منفصل
- 3 حقول إدخال جديدة: cash, operating_expenses, average_payables
- شاشة DuPont متقدمة: شلال/خط/مؤشر ROE + مقارنة قطاعية + توصيات + تصدير PDF
- شاشة تحليل السيناريوهات: مثالي/طبيعي/أسوأ + حساسية Tornado + خط/شريط/مساحة + PDF + حفظ JSON/DB
- ميزة المعايير المرجعية المتقدمة: أفضل الممارسات + معيار دولي + نقاط قوة/ضعف + اتجاه عبر السنوات + مقارنة منافسين (جدولا reference_standards + competitor_data)
- لوحة التحكم المتقدمة: 6 بطاقات KPI بحالة لونية + 4 رسوم (إيرادات شهرية/ربعية + مصروفات + ربحية + رادار) + تنبيهات (شذوذ/أداء/معايير/إجراءات) + تخصيص كامل + حفظ تخطيطات DB (جدول dashboard_layouts) + تصدير PDF/Excel
- ميزة الامتثال الضريبي الجزائري: نسبة TVA 6% (intermediate) + ترحيل رصيد TVA + دفعات IBS المقدمة (أشهر 3,6,11) + تصفية IBS + بيانات DAS + قوالب إقرارات G50/G57/DAS مع تصدير PDF/Excel (modules/tax_reports.py + تبويب إقرارات في tax_view.py)
- محرك الرؤى الذكية AI (شاشة 24): تنبؤ 3-6 أشهر (خطي/متوسط متحرك/تجانس أسي + فترات ثقة 95%) + كشف شذوذ (z-score للأرباح + IQR للمعاملات) + أنماط (اتجاه/موسمية/دورات/مؤشرات مخاطر) + توصيات ذكية + تنبيهات (خطر/تحذير/فرصة/إجراء) + تصدير PDF/Excel (modules/ai_insights.py + ui/views/ai_insights_view.py — pandas/numpy فقط بدون sklearn)
- تحليل ربحية مراكز التكلفة (شاشة 25): مراكز (قسم/مشروع/فرع/خط إنتاج) + توزيع مباشر/غير مباشر (إيرادات/عدد موظفين/مساحة/متساوٍ) + تحليل ربحية + مقارنات (سابقة/ميزانية/معايير) + اتجاه متعدد الفترات + تقارير/توصيات + تصدير PDF/Excel (modules/cost_center_profitability.py + ui/views/cost_center_profitability_view.py)
- تحسين أداء شامل (v3.1.6): تحميل كسول للمشاهد (main_window.py) + PEP 562 للوحدات (modules/__init__.py) + تجمّع اتصالات DB (db_connection.py + close_pool) + دفعات executemany (db_operations.py) + لوحة تحكم بلا إعادة رسم (dashboard.py) — إقلاع 778→49ms، RSS 128→45MB، حفظ DB 4.6×، قراءة 17× (التفاصيل: docs/PERFORMANCE_REPORT.md)
- تعدد العملات (شاشة 26): 7 عملات افتراضية + أسعار صرف + تحويل + تقرير متعدد العملات + تصدير CSV (modules/currency.py + ui/views/currency_view.py + حالة في app_state.py)
- المزامنة السحابية والنسخ الاحتياطي (شاشة 27): وجهات مزامنة (Dropbox/OneDrive/Drive) + snapshot مع checksum + تشفير اختياري بكلمة مرور (AES-GCM) + نسخ احتياطي تلقائي مع تدوير + استرجاع/سحب + سجل عمليات DB (modules/cloud_sync.py + ui/views/cloud_sync_view.py — جدول cloud_sync_state)
- الشركات التجريبية (شاشة 28): 4 شركات (تجارية/خدمات/إنتاج/استيراد-تصدير) ببيانات مالية وضريبية متسقة + مولّد معاملات شهرية (12 شهراً بأوزان موسمية) + تحميل شركة للتطبيق + تقارير مُعدّة مسبقاً (ميزانية/دخل/نسب) + تصدير بيانات CSV + قوالب استيراد CSV متوافقة مع DataImporter (modules/demo_data.py + modules/demo_templates.py + ui/views/demo_data_view.py)
- تحسينات UI/UX (شاشات 28): اختصارات كاملة (Ctrl+1..0، Ctrl+Shift+1..0، Ctrl+Shift+A، F2..F8 للشاشات 21-28، Ctrl+T للثيم، F1 للاختصارات) + قائمة "عرض" ديناميكية بكل الشاشات 28 + نافذة اختصارات كاملة + انتقالات تلاشي عند تغيير الشاشة + مؤشر تحميل في شريط الحالة + رسائل خطأ موحّدة مع إجراء مقترح مترجم (ui/widgets/messages.py + ربط أخطاء الطباعة/التصدير/الاختبارات) + تحسينات إتاحة/تباين بالثيمات الثلاثة (focus/disabled/ComboBox/ToolTip + تباين نص داكن)
- شاشة اختبار المستخدمين (شاشة 29): 4 مجموعات مستخدمين × 5 سيناريوهات + ملاحظات/مقترحات/أعطال بتصنيفات/أولويات/حالات + درجة رضا بقيود + تحليل مفصّل + تقارير (تعقيبات/قائمة أعطال/طلبات تحسين/ملخص) + بيانات تجريبية + تصدير/استيراد JSON + CSV/Excel/PDF + حفظ/تحميل DB (modules/user_testing.py + ui/views/user_testing_view.py — قنوات DB عبر get_connection)
- 1350 اختباراً كلها ناجحة عبر `python -m pytest tests -q` (1127 عبر `python -m unittest discover -s tests`)
- تغطية الوحدات: **100%** عبر `python -m coverage run --source=modules --omit="modules/__init__.py" -m pytest tests -q` (5768 سطراً، 0 مفقود — كانت 73% ثم 99%)
- التغطية الشاملة: 20 ملف اختبار جديد (test_edge_errors, test_cashflow, test_comparative, test_backup, test_bank_print, test_breakeven_costcenter, test_reporting_modules, test_email_currency, test_importers, test_excel_export, test_reporting_extra, test_user_manager, test_update_checker_extra, test_cloud_sync_extra, test_tax_reminders_extra, test_tax_reports_extra, test_small_gaps) — الميزات الست (DuPont/Scenarios/Benchmarks/AI/Tax/Anomaly) + cashflow + comparative عند 100% + قائمة أخطاء مفصّلة في PROJECT_MAP.md
- اختبار التكامل (جلسة v3.1.6): 3 ملفات جديدة — test_integration_workflow.py (9: رحلات مستخدم كاملة + إدارة حالة + اتساق تدفق البيانات) + test_integration_database.py (18: سلامة/معاملات/تزامن/نسخ-استرجاع) + test_integration_performance.py (10: 1000+ معاملة + مستخدمون متزامنون + بيانات كبيرة + إجهاد ذاكرة) — كشفت 3 أخطاء منتج أُصلحت (working_capital لا يُخزَّن في analysis.py، delete_analysis يفشل مع notes في db_operations.py، backup.py يفقد بيانات WAL) + تقرير docs/INTEGRATION_REPORT.md
- شاشة اختبار المستخدمين (جلسة v3.1.6): test_user_testing.py (66: جلسات/ملاحظات/رضا/تقارير/JSON/DB/أعطال تصدير) — user_testing.py وصل 100% + إصلاح تصدير PDF عند غياب خط عربي (cp1252 fallback)
- جلسة التصحيحات النهائية (2026-08-01): إصلاح 13 خللاً (print_manager/landscape، bank_sync رأس الملف، report_templates deepcopy، reporting Amiri، update_checker download+fallback، user_manager token=None، scheduled_backup vault.enc+meta، backup SQL/تحقق sqlite، data_import disconnect+محجوزات، currency no-op، tax_reminders فرع ميت، i18n v3.1.6) + مراجعة أمان (PBKDF2 100k/salt، تخزين مشفّر SMTP/API، HTTPS فقط — كلها سليمة) → **تغطية 100%**
- إصلاح واحد ضمن جلسة التغطية: `modules/comparative.py generate_report` كان يرمي KeyError مع بيانات ناقصة → `.get(item/ratio, 0)`
- i18n: 1874 مفتاحاً × 3 لغات (AR/EN/FR) — مجموعات متطابقة (أُزيل مفتاح partners_col_type2 الميت)
- Nuitka onefile: dist_nuitka/run_ui.dist/SmartAccounting.exe (78.3 MB)
- Inno Setup: installer_output/SmartAccounting-Setup-v3.1.6.exe (51.5 MB)
- ZIP: installer_output/SmartAccounting-v3.1.6-win64.zip (82.9 MB)
- رُفع assets إلى GitHub release v3.1.6
- auto-update: يشير version.json إلى v3.1.6 (تاريخ 2026-08-02)
- الموقع docs/ (GitHub Pages) رُفّع: badge v3.1.6 + روابط تحميل v3.1.6 + 29 شاشة/1350 اختبار/30 وحدة + سجل v3.1.6
- التحديث عبر wscript/VBS مخفي تماماً (بدون نافذة cmd)
- ملاحظة: Smart App Control على جهاز التطوير يحجب exe غير موقّع حديث البناء (لم يُحل بعد)
