# تقرير تدقيق تباعد الواجهات — UI Spacing Audit Report

> جلسة التوحيد الشامل للواجهات (2026-08-05) — الإصدار v3.1.8+
> النطاق: الشاشات الـ35 + الثيمات الثلاثة (فاتح / داكن / متدرّج)

## 1. الخلاصة التنفيذية

- **قبل الجلسة:** قيم تباعد متناثرة (3/4/5/8/10/15/20) مكتوبة يدوياً في ~40 ملفاً،
  وبطاقات وأزرار بأحجام متفاوتة عبر الشاشات والثيمات.
- **بعد الجلسة:** مصدر واحد للمعايير (`ui/constants.py`) + تطبيق موحّد عبر
  `apply_standard_layout()` + أحجام دنيا متطابقة في الثيمات الثلاثة.
- **النتيجة:** 1877 اختباراً ناجحاً (1862 سابقة + 15 جديدة) وتغطية modules 100%،
  وكل الشاشات الـ35 تلتزم بالحدود الهندسية الدنيا.

## 2. المنهجية

1. **Audit AST:** جرد برمجي لكل استدعاءات `setSpacing`/`setContentsMargins` في
   `ui/views/*.py` (39 ملفاً) لتصنيف القيم الضيقة.
2. **تصنيف الاستثناءات المقصودة:** أغلفة `QScrollArea` (`(0,0,0,0)` + spacing 0)
   وصروح متلاصقة مقصودة (spacing 5) — لم تُلمس.
3. **لقطات BEFORE/AFTER:** تصيير الشاشات الـ35 offscreen بدقة 1280×740، BEFORE
   بالـ QSS القديم (من HEAD) وAFTER بالجديد.
4. **مقارنة pixel-diff:** فرق بكسل فعلي (عتبة ΔRGB>12) بين اللقطتين.
5. **Geometry QA:** فحص هندسي مباشر لارتفاعات كل الحقول والأزرار الظاهرة في كل شاشة.
6. **اختبارات انحدار:** مجموعة كاملة 1877 + تغطية 100%.

## 3. التوحيد المطبَّق على الشاشات

### 3.1 الشاشات التي ورثت المعايير تلقائياً (17 شاشة عبر BaseView)

ورثت مستويات page/card/stat من `ui/views/_base.py` — لا حاجة لتغييرات فردية:
dashboard, ratios, audit, reports, settings, chat, comparative, cashflow, security,
zscore, forecasting, budget, cost_center, breakeven, data_import, bank_sync,
benchmarks.

### 3.2 توحيد التباعد الضيق (3-5 → 8)

| الملف | الموضع | قبل | بعد |
|---|---|---|---|
| `audit_view.py` | تخطيط النص التفصيلي | 3 | 5 |
| `audit_view.py` | تخطيط بطاقة الإحصائيات | 3 | 8 |
| `advanced_dashboard_view.py` | بطاقات KPI | 4 | 8 |
| `dashboard.py` | بطاقة الملخص | 5 | 8 |
| `analysis_view.py` | بطاقة المكوّنات | 5 | 8 |
| `scenarios_view.py` | بطاقة النتائج | 5 | 8 |
| `tax_calendar_view.py` | بطاقة الشهر | 4 | 8 |
| `tax_view.py` | نماذج IFU/الرسم/الإيجارات (×3) | 4 | 8 |
| `chat_view.py` | عمود الأزرار | 5 | 8 |
| `login_view.py` | صف كلمة المرور + زر العين | 4 | 5 (مقصود) |

## 4. توحيد الثيمات الثلاثة (QSS)

### 4.1 المشكلة المكتشفة — نموذج صندوق Qt

`min-height` في QSS يُضاف فوق الـ padding الرأسي (الكلي = content + padding + border).
كتابة `min-height: 38px` مع `padding: 11px` أعلى/أسفل أنتج **زراً بارتفاع 62px**
وحقولاً 58px — تضخيم يزيد التمرير على الشاشات الصغيرة.

### 4.2 الإصلاح

- padding رأسي → **0** (بقاء الأفقي كما هو)
- `min-height` → **40px** في القواعد: QLineEdit/QDoubleSpinBox/QSpinBox + QComboBox + QPushButton
  (+ QTextEdit/QPlainTextEdit في الثيم المتدرّج)

### 4.3 الارتفاعات الفعلية المقاسة (minSizeHint)

| العنصر | قبل | بعد (الثلاثة ثيمات) |
|---|---|---|
| QLineEdit | 40px | 44px (42px متدرّج) |
| QDoubleSpinBox | 40px | 44px (42px متدرّج) |
| QComboBox | 39px | 44px (42px متدرّج) |
| QPushButton | 38px | 42px |

زيادة متواضعة موحّدة +4px تقريباً لكل عنصر، بأهداف منطقة نقر مريحة.

## 5. أدلة التحقق

### 5.1 المقارنة البصرية (pixel-diff BEFORE/AFTER)

- **12 شاشة** تغيّرت بكسلّياً (1% - 14.5% من البكسلات) — الأهم:
  inventory 14.5%، invoicing 14.3%، budgeting 13.7%، partners 13.7%،
  ledger/payroll 12.0%، cloud_sync 11.5%، currency 10.8%، demo_data 8.5%،
  user_testing 5.0%، tax_calendar 4.9%، advanced_dashboard 2.4%، chat 1.1%، login 0.01%.
- الشاشات «المتطابقة» هي الشاشات الفارغة/الجدولية التي لا تحتوي حقولاً وأزراراً
  مصفّفة (لا تغيّر في الألوان ولا في هندسة عناصر ظاهرة).
- الإجمالي: 3.55% من بكسلات اللقطات الـ35 تغيّرت.

### 5.2 Geometry QA (الشاشات الـ35)

- كل QLineEdit/QDoubleSpinBox/QSpinBox/QPushButton ظاهر: **≥ 40px** (حقول) و **≥ 38px** (أزرار).
- الاستثناء الصحيح الوحيد: الحقول الداخلية للمكونات المركبة (داخل QDateEdit/
  QDoubleSpinBox/QComboBox) بارتفاعها الطبيعي 18px — المكوّن الخارجي نفسه 40-44px.

### 5.3 الاختبارات

- `tests/test_ui_constants.py` — 15 اختباراً: ترتيب مستويات التباعد، قيم الهوامش،
  min-heights، مستويات page/card/stat/form في `apply_standard_layout`، معايير
  BaseView، ومنع أي `setSpacing < 5` خارج أغلفة `QScrollArea` (فشل أولاً على
  `analysis_view.py` و`scenarios_view.py` ثم أُصلح بالكشف الدقيق عن أغلفة التمرير
  عبر AST على مستوى الدالة).
- المجموعة الكاملة: **1877 passed** في 42.6 ثانية.
- التغطية: **100%** (7233 سطراً في modules، 0 مفقود).

## 6. الملفات المتغيّرة

| الملف | التغيير |
|---|---|
| `ui/constants.py` | **جديد** — المصدر الموحد للمعايير + `apply_standard_layout()` |
| `ui/views/_base.py` | BaseView على المستويات page/card/stat من constants |
| `ui/views/audit_view.py` وغيرها (9 ملفات) | توحيد التباعد الضيق |
| `ui/resources/style.qss` / `style_dark.qss` / `style_modern.qss` | min-height 40 + padding رأسي 0 |
| `tests/test_ui_constants.py` | **جديد** — 15 اختباراً |

## 7. قرارات لم تُتّخذ (لجلسات لاحقة)

- إعادة بناء Nuitka/mثبّتات v3.1.8 لتضمين تغييرات الواجهة — تُنفَّذ مع رفع الإصدار القادم.
- لقطات BEFORE/AFTER (35+35 PNG) محفوظة خارج الريبو (مجلد عمل مؤقت) كمرجع للجلسة؛
  يمكن نسخ عينات قليلة إلى `docs/` عند الحاجة.
