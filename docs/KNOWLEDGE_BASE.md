# بنك المعرفة — المنصة المحاسبية الذكية

> نقطة الدخول الموحّدة لكل وثائق المشروع. الإصدار v3.1.7.

---

## 1. ابدأ هنا

| الوثيقة | الوصف |
|---------|-------|
| [`USER_GUIDE.md`](USER_GUIDE.md) | دليل المستخدم: كل الشاشات الـ 29 + ميزات جديدة + أفضل الممارسات + FAQ |
| [`INSTALLATION_GUIDE.md`](../INSTALLATION_GUIDE.md) | التثبيت (مثبّت/محمول) + المتطلبات + التحقق |
| [`DEPLOYMENT_GUIDE.md`](../DEPLOYMENT_GUIDE.md) | النشر والتحديث التلقائي |
| [`TROUBLESHOOTING.md`](../TROUBLESHOOTING.md) | استكشاف الأخطاء المتقدم |

## 2. التوثيق التقني (للمطورين)

| الوثيقة | الوصف |
|---------|-------|
| [`API_REFERENCE.md`](API_REFERENCE.md) | مرجع الواجهات البرمجية الكامل (37 وحدة، 325 عملية) + أمثلة |
| [`api/openapi.yaml`](api/openapi.yaml) | مواصفات OpenAPI 3.0 (تُفتح في Swagger UI) |
| [`api/index.html`](api/index.html) | عارض Swagger UI عبر موقع docs/ |
| [`ARCHITECTURE.md`](../ARCHITECTURE.md) | البنية المعمارية والطبقات |
| [`PROJECT_MAP.md`](../PROJECT_MAP.md) | خريطة المشروع + سجل الإصدارات + ملخص الاختبارات |
| [`AGENTS.md`](../AGENTS.md) | بروتوكول العمل ومبادئ التعديل |

## 3. أدلة التحليلات المالية

| الدليل | المحتوى |
|--------|---------|
| [`BREAKEVEN_GUIDE.md`](../BREAKEVEN_GUIDE.md) | نقطة التعادل وحساباتها |
| [`BUDGET_MANAGEMENT_GUIDE.md`](../BUDGET_MANAGEMENT_GUIDE.md) | الموازنة والانحرافات |
| [`FORECASTING_GUIDE.md`](../FORECASTING_GUIDE.md) | التنبؤ المالي |
| [`COST_CENTER_GUIDE.md`](../COST_CENTER_GUIDE.md) | مراكز التكلفة |
| [`ADVANCED_DASHBOARD_ANALYTICS.md`](../ADVANCED_DASHBOARD_ANALYTICS.md) | لوحة التحكم المتقدمة |
| [`PLAN_TAX_MODULE.md`](../PLAN_TAX_MODULE.md) | خطة وحدة الضرائب |

## 4. تقارير الجودة

| التقرير | المحتوى |
|---------|---------|
| [`INTEGRATION_REPORT.md`](INTEGRATION_REPORT.md) | اختبار التكامل والأداء (3 أخطاء أُصلحت) |
| [`PERFORMANCE_REPORT.md`](PERFORMANCE_REPORT.md) | تحسينات الأداء (إقلاع 15×، ذاكرة -65%) |
| [`Smart_Accounting_Platform_Report.pdf`](Smart_Accounting_Platform_Report.pdf) | التقرير الرسمي الشامل |

## 5. سكربتات الفيديوهات التعليمية

- [`tutorials/`](tutorials/) — 4 سكربتات جاهزة لأدوات توليد الفيديو بالذكاء الاصطناعي:
  1. جولة الميزات (Feature Walkthrough)
  2. سير عمل التحليل المالي (Analysis Workflows)
  3. توليد التقارير (Report Generation)
  4. نصائح وخدع (Tips & Tricks)

---

## الأسئلة الشائعة المختصرة

**ما الإصدار الحالي؟** v3.1.7 (إعدادات الإصدار: 3.1.7 في `config.py`).

**كم عدد الاختبارات؟** 1800 اختباراً ناجحاً (1787 سابقة + 4 أداء في test_startup_perf.py + 9 تصدير في test_exporters.py) + تغطية وحدات 100% (`modules/` بالكامل).

**كيف أجرب الأداة بأرقام جاهزة؟** شاشة الشركات التجريبية (Ctrl+Shift+A).

**كيف أوثّق ملاحظات المستخدمين؟** شاشة اختبار المستخدمين (F9) مع تصدير PDF/Excel/DB.

**كيف أحصل على تحديثات؟** التحقق التلقائي عند التشغيل + تحميل من صفحة الإصدارات.

---

*آخر تحديث: 2026-08-03 — جلسة رفع الإصدار (v3.1.7).*
