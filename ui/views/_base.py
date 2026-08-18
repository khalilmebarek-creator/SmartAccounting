# Base view class with common layout helpers
# ===========================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QScrollArea
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFont

from ui.resources.i18n import t
from ui.constants import (
    PAGE_MARGINS, PAGE_SPACING, CARD_MARGINS, CARD_SPACING,
    STAT_MARGINS, STAT_SPACING, apply_standard_layout,
)


def _clear_nested(layout):
    """تفرّغ layout بعمق (عناصرها و layouts الفرعية) دون تكرار لا نهائي."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        child = item.layout()
        if child is not None:
            _clear_nested(child)


def wrap_in_scroll(widget):
    """لفّ أي widget في QScrollArea — للشاشات التي لا ترث BaseView."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setWidget(widget)
    scroll._wrapped_view = widget
    return scroll


class BaseView(QWidget):
    """Base class for all views — provides common layout and helper methods."""

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        self._main_layout = QVBoxLayout(container)
        self._main_layout.setContentsMargins(*PAGE_MARGINS)
        self._main_layout.setSpacing(PAGE_SPACING)

        self._scroll.setWidget(container)
        outer.addWidget(self._scroll)

    def _make_header(self, title_key: str, subtitle_key: str = None) -> QLabel:
        """Add a standard title + optional subtitle to the layout."""
        title = QLabel(t(title_key))
        title.setObjectName("headerTitle")
        self._main_layout.addWidget(title)

        if subtitle_key:
            sub = QLabel(t(subtitle_key))
            sub.setObjectName("headerSubtitle")
            self._main_layout.addWidget(sub)

        return title

    def _make_card(self, title_key: str = None) -> QFrame:
        """Create a styled card frame."""
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout()
        apply_standard_layout(layout, "card")

        if title_key:
            lbl = QLabel(t(title_key))
            lbl.setObjectName("cardTitle")
            font = QFont()
            font.setBold(True)
            font.setPointSize(13)
            lbl.setFont(font)
            layout.addWidget(lbl)

        card.setLayout(layout)
        return card

    def _make_stat_card(self, title: str, value: str = "0", color: str = "#333") -> QFrame:
        """Create a stat card with title + large value."""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout()
        apply_standard_layout(layout, "stat")

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 11px; color: #888;")
        lbl_value = QLabel(value)
        lbl_value.setObjectName("statValue")
        font = QFont()
        font.setBold(True)
        font.setPointSize(18)
        lbl_value.setFont(font)
        lbl_value.setStyleSheet(f"color: {color};")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)

        frame.setLayout(layout)
        return frame

    def _make_stat(self, title: str) -> tuple:
        """بطاقة إحصائية مدمجة (15pt) — ترجع (الإطار, ملصق القيمة)."""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 11px; color: #888;")
        lbl_value = QLabel("0")
        lbl_value.setObjectName("statValue")
        font = QFont()
        font.setBold(True)
        font.setPointSize(15)
        lbl_value.setFont(font)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        frame.setLayout(layout)
        return frame, lbl_value

    @staticmethod
    def _labeled_field(label_key: str, widget) -> QVBoxLayout:
        """حقل بعنوان صغير فوقه — لقراءة أوضح داخل النماذج."""
        box = QVBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(4)
        lbl = QLabel(t(label_key))
        lbl.setStyleSheet("font-size: 11px; color: #888;")
        box.addWidget(lbl)
        box.addWidget(widget)
        return box

    def _clear_layout(self):
        """أزل كل العناصر من _main_layout لإعادة بنائها (تُستخدم عند retranslate)."""
        layout = self._main_layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            child = item.layout()
            if child is not None:
                _clear_nested(child)
