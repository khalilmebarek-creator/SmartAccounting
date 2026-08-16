# دليل الاستخدام التفاعلي
# ========================
# 7 أقسام موجّهة للمستخدم النهائي — بلا أي ذكر للكود أو بنية المشروع.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QTabWidget, QTextBrowser,
    QVBoxLayout, QWidget,
)

from ui.resources.i18n import t
from utils.app_logger import get_logger

log = get_logger("guide")

_TABS = 7


class GuideDialog(QWidget):
    """نافذة دليل الاستخدام (QWidget بنافذة منبثقة — متوافقة مع الاختبارات)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("guide_title"))
        self.setWindowFlag(Qt.Dialog, True)
        self.resize(720, 560)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.tabs = QTabWidget()
        for i in range(1, _TABS + 1):
            page = QTextBrowser()
            page.setOpenExternalLinks(False)
            page.setHtml(t(f"guide_body_{i}"))
            self.tabs.addTab(page, t(f"guide_tab_{i}"))
        layout.addWidget(self.tabs)

        nav = QHBoxLayout()
        self.prev_btn = QPushButton(t("guide_prev"))
        self.prev_btn.clicked.connect(self._go_prev)
        self.next_btn = QPushButton(t("guide_next"))
        self.next_btn.clicked.connect(self._go_next)
        close_btn = QPushButton(t("guide_close"))
        close_btn.clicked.connect(self.close)
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        nav.addStretch()
        nav.addWidget(close_btn)
        layout.addLayout(nav)

        self.setLayout(layout)
        self._update_nav()
        log.info("guide opened")

    def _go_prev(self):
        if self.tabs.currentIndex() > 0:
            self.tabs.setCurrentIndex(self.tabs.currentIndex() - 1)
        self._update_nav()

    def _go_next(self):
        if self.tabs.currentIndex() < self.tabs.count() - 1:
            self.tabs.setCurrentIndex(self.tabs.currentIndex() + 1)
        self._update_nav()

    def _update_nav(self):
        self.prev_btn.setEnabled(self.tabs.currentIndex() > 0)
        self.next_btn.setEnabled(
            self.tabs.currentIndex() < self.tabs.count() - 1)
