# UI Style Guide — معايير الواجهة الموحدة

> المرجع الإلزامي لبناء أي شاشة أو بطاقة أو نموذج جديد في التطبيق.
> الإصدار: v3.1.8+ (جلسة التوحيد 2026-08-05)

## 1. المصدر الموحد: `ui/constants.py`

كل قيم التباعد والهوامش والأحجام الدنيا موجودة في **مكان واحد** وهو `ui/constants.py`،
وكل شاشة جديدة **يجب** أن تستخدمها عبر `apply_standard_layout()` بدل كتابة أرقام مبعثرة.

### 1.1 مستويات التباعد (Spacing)

| الثابت | القيمة | الاستخدام |
|---|---|---|
| `SPACING_TIGHT` | 5 | صفوف مصغّرة داخل البطاقات (نادر جداً) |
| `SPACING_NORMAL` | 8 | حقول قريبة ضمن نفس المجموعة |
| `SPACING_MEDIUM` | 10 | بين المجموعات الفرعية / الأزرار |
| `SPACING_LARGE` | 15 | بين المجموعات الكبيرة |
| `SPACING_XLARGE` | 20 | فواصل الصفحة الرئيسية |

### 1.2 الهوامش (Margins)

| الثابت | القيمة |
|---|---|
| `MARGIN_SMALL` | 5 |
| `MARGIN_NORMAL` | 10 |
| `MARGIN_LARGE` | 15 |
| `MARGIN_XLARGE` | 20 |

### 1.3 الأحجام الدنيا (Min Heights)

| الثابت | القيمة | ملاحظة |
|---|---|---|
| `MIN_HEIGHT_FIELD` | 40 | QLineEdit/QComboBox/QSpinBox — **الارتفاع الكلي** |
| `MIN_HEIGHT_BUTTON` | 40 | QPushButton — الارتفاع الكلي |
| `MIN_HEIGHT_TEXTBOX` | 80 | QTextEdit |

> **هام — نموذج صندوق Qt QSS:** في Qt، `min-height` في QSS يُضاف فوق الـ padding
> الرأسي (الكلي = content + padding + border). لذلك لا تكتب `min-height` مع padding
> رأسي موجب في نفس القاعدة، وإلا تتضخم العناصر (مثال حقيقي: 38px min-height +
> 11px padding أعلى/أسفل = زر 62px). القاعدة المطبقة في الثيمات الثلاثة:
> `padding` رأسي = 0 + `min-height` = 40 → ارتفاع فعلي 42-44px.

### 1.4 أنماط الحاويات الجاهزة — `apply_standard_layout(layout, level)`

| المستوى | الهامش | التباعد |
|---|---|---|
| `page` (الافتراضي) | `(20, 20, 20, 20)` | 15 |
| `card` | `(16, 12, 16, 12)` | 10 |
| `stat` | `(16, 12, 16, 12)` | 8 |
| `form` | `(15, 10, 15, 10)` | 8 |

```python
from ui.constants import apply_standard_layout

root = QVBoxLayout(self)
apply_standard_layout(root, "page")          # شاشة كاملة
apply_standard_layout(card_layout, "card")   # داخل QFrame#card
apply_standard_layout(stat_layout, "stat")   # بطاقة إحصائية مصغّرة
apply_standard_layout(form_layout, "form")   # نموذج داخل بطاقة
```

## 2. قاعدة الهرمية في BaseView (`ui/views/_base.py`)

- `BaseView` يطبّق مستوى `page` تلقائياً على التخطيط الرئيسي (20/15).
- `_make_card()` يطبّق مستوى `card` على بطاقات `QFrame#card`.
- `_make_stat_card()` يطبّق مستوى `stat` على البطاقات الإحصائية المصغّرة.
- أي شاشة ترث `BaseView` تحصل على المعايير تلقائياً (17 شاشة حالياً).

## 3. الثيمات (QSS)

ثلاثة ملفات في `ui/resources/` تُطبَّق عبر `apply_theme()` في `main_window.py`:

- `style.qss` — فاتح
- `style_dark.qss` — داكن
- `style_modern.qss` — متدرّج زجاجي

### 3.1 القيم الموحدة في الثيمات الثلاثة

| العنصر | min-height | padding رأسي |
|---|---|---|
| QLineEdit / QDoubleSpinBox / QSpinBox | 40px | 0 |
| QComboBox | 40px | 0 |
| QPushButton | 40px | 0 |
| QTextEdit / QPlainTextEdit | 40px | 0 (في الثيمات التي تصيغها) |

النتيجة الفعلية المقاسة (minSizeHint):
- حقول: **42-44px** (حسب سماكة الحد لكل ثيم)
- أزرار: **42px**

## 4. قواعد إلزامية للشاشات الجديدة

1. **استخدم `apply_standard_layout`** للمستويات الأربعة — لا أرقام مبعثرة.
2. **لا تكتب تباعداً < 8** خارج أغلفة التمرير. الاستثناءات المقصودة الوحيدة:
   - `QScrollArea` wrapper: `setContentsMargins(0,0,0,0)` + `setSpacing(0)`
     (مع `setWidgetResizable(True)`) — موجود في `analysis_view.py` و`scenarios_view.py`
     و`data_entry.py`.
   - صفوف مصغّرة متلاصقة (مثل حقل + زر عين في `login_view.py`: spacing 5).
3. **لا تكتب min-height مع padding رأسي** في نفس قاعدة QSS (راجع §1.3).
4. أزرار `QPushButton` بدون `min-width` تصغّر — استخدم `MIN_WIDTH_BUTTON`/`MIN_WIDTH_SMALL_BUTTON`.
5. **لا تستخدم `setStyleSheet` مفصلاً على مستوى الشاشة** يتجاوز المعايير العامة؛
   استخدمه للتلوين الديناميكي فقط (ألوان حالة، خطوط مخصصة).

## 5. التحقق (QA)

- `python -m pytest tests/test_ui_constants.py -q` — 15 اختباراً (ثوابت + مستويات + منع التباعد الضيق).
- Geometry QA (دليل مؤقت في ملفات العمل): كل QLineEdit/QSpinBox/QPushButton ظاهر
  في كل شاشة من الـ35 يجب أن يكون ≥ 40px حقولاً / ≥ 38px أزراراً.
  > ملاحظة: العناصر الداخلية للمكونات المركبة (الحقل الداخلي لـ QDateEdit/QDoubleSpinBox
  > و QComboBox) لا تُحسب — ارتفاعها الداخلي 18px طبيعي، والمكوّن الخارجي 40-44px.
- المجموعة الكاملة: `python -m pytest tests -q` → 1877 اختباراً.
