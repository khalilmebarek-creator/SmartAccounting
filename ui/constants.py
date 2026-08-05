"""Unified UI Spacing & Layout Standards.

المرجع الموحّد للتباعد والهوامش والأحجام الدنيا في كل شاشات التطبيق.
كل شاشة جديدة يجب أن تستخدم هذه المعايير عبر `apply_standard_layout`.
"""

# ============================================================
# Spacing بين العناصر
# ============================================================
SPACING_TIGHT = 5       # عناصر شديدة القرب (صفوف مصغّرة داخل البطاقات)
SPACING_NORMAL = 8      # تباعد عادي (حقول قريبة ضمن نفس المجموعة)
SPACING_MEDIUM = 10     # تباعد متوسط (بين المجموعات الفرعية / الأزرار)
SPACING_LARGE = 15      # تباعد كبير (بين المجموعات الكبيرة)
SPACING_XLARGE = 20     # تباعد كبير جداً (فواصل الصفحة الرئيسية)

# ============================================================
# هوامش الحاويات
# ============================================================
MARGIN_SMALL = 5
MARGIN_NORMAL = 10
MARGIN_LARGE = 15
MARGIN_XLARGE = 20

# الهامش في جميع جهات الصفحة الرئيسية (يُمزج مع التمرير اللازم)
PAGE_MARGIN = MARGIN_XLARGE

# ============================================================
# الأحجام الدنيا للعناصر (px)
# ============================================================
# ملاحظة Qt QSS: `min-height` في QSS يُضاف فوق الـ padding الرأسي
# (content + padding + border). لذلك القيم هنا تمثل الارتفاع الكلي
# المستهدف، وتُنفَّذ في QSS عبر padding رأسي = 0 + min-height = القيمة.
MIN_HEIGHT_FIELD = 40        # QLineEdit, QComboBox, QSpinBox... (إجمالي)
MIN_HEIGHT_BUTTON = 40       # QPushButton (إجمالي)
MIN_HEIGHT_TEXTBOX = 80      # QTextEdit
MIN_WIDTH_BUTTON = 100       # زر عادي
MIN_WIDTH_SMALL_BUTTON = 80  # زر صغير

# ============================================================
# Padding داخلي (px)
# ============================================================
PADDING_FIELD = 6
PADDING_BUTTON = 8
PADDING_GROUP = 10
PADDING_CARD = 16

# ============================================================
# أنماط الحاويات الجاهزة
# ============================================================
# مستوى الصفحة الرئيسية (خارج أي بطاقة أو ScrollArea)
PAGE_MARGINS = (PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
PAGE_SPACING = SPACING_LARGE

# مستوى البطاقة QFrame#card
CARD_MARGINS = (PADDING_CARD, 12, PADDING_CARD, 12)
CARD_SPACING = SPACING_MEDIUM

# مستوى البطاقة الإحصائية المصغّرة (Stat/Widget)
STAT_MARGINS = (16, 12, 16, 12)
STAT_SPACING = SPACING_NORMAL

# مستوى النموذج داخل بطاقة
FORM_MARGINS = (MARGIN_LARGE, MARGIN_NORMAL, MARGIN_LARGE, MARGIN_NORMAL)
FORM_SPACING = SPACING_NORMAL


def apply_standard_layout(layout, level="page"):
    """طبّق معايير التباعد والهوامش الموحدة على layout.

    المستويات المدعومة: page / card / stat / form.
    """
    if level == "card":
        layout.setContentsMargins(*CARD_MARGINS)
        layout.setSpacing(CARD_SPACING)
    elif level == "stat":
        layout.setContentsMargins(*STAT_MARGINS)
        layout.setSpacing(STAT_SPACING)
    elif level == "form":
        layout.setContentsMargins(*FORM_MARGINS)
        layout.setSpacing(FORM_SPACING)
    else:  # page (الافتراضي)
        layout.setContentsMargins(*PAGE_MARGINS)
        layout.setSpacing(PAGE_SPACING)
    return layout