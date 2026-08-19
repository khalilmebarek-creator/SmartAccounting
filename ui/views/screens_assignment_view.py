# حوار توزيع الشاشات على العضو
# ==============================
# المدير يحدد الشاشات المسموحة لكل عضو (1 و2 إجباريتان).

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from modules.user_manager import user_manager
from ui.resources.i18n import t
from ui.views.view_registry import VIEW_REGISTRY
from utils.app_logger import get_logger

log = get_logger("screens_assignment")


class ScreensAssignmentDialog(QWidget):
    """نافذة اختيار الشاشات لعضو (QWidget منبثقة — متوافقة مع الاختبارات)."""

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self._username = username
        self.setWindowTitle(t("screens_assign_title"))
        self.setWindowFlag(Qt.WindowType.Dialog, True)
        self.resize(420, 640)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        header = QLabel(t("screens_assign_header"))
        header.setWordWrap(True)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(4)

        current = user_manager.get_allowed_screens(username)
        self._checks = {}
        for vid in sorted(VIEW_REGISTRY):
            name = VIEW_REGISTRY[vid][0]
            cb = QCheckBox(t(f"sidebar_{name}"))
            cb.setChecked(current is None or vid in current)
            if vid in (1, 2):
                cb.setChecked(True)
                cb.setEnabled(False)
                cb.setToolTip(t("screens_required_tip"))
            inner_layout.addWidget(cb)
            self._checks[vid] = cb

        inner.setLayout(inner_layout)
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        note = QLabel(t("screens_assign_note"))
        note.setWordWrap(True)
        note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(note)

        buttons = QHBoxLayout()
        save_btn = QPushButton(t("screens_assign_save"))
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton(t("btn_cancel"))
        cancel_btn.clicked.connect(self.close)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)
        log.info("assignment dialog opened for %s", username)

    def _save(self):
        chosen = [vid for vid, cb in self._checks.items() if cb.isChecked()]
        if user_manager.set_allowed_screens(self._username, chosen):
            log.info("screens saved for %s: %s", self._username, chosen)
            self.close()
