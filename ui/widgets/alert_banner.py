"""Alert Banner — shows fraud alerts at the top of the main window."""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import (pyqtSignal)
from ui.resources.i18n import t


class AlertBanner(QWidget):
    """A dismissible alert banner that appears when there are high-severity alerts."""

    dismiss_clicked = pyqtSignal()
    view_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("alertBanner")
        self.setVisible(False)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)

        self.icon_label = QLabel("🔴")
        layout.addWidget(self.icon_label)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 1)

        self.view_btn = QPushButton()
        self.view_btn.clicked.connect(self.view_clicked.emit)
        layout.addWidget(self.view_btn)

        self.dismiss_btn = QPushButton("✕")
        self.dismiss_btn.setMaximumWidth(30)
        self.dismiss_btn.clicked.connect(self._dismiss)
        layout.addWidget(self.dismiss_btn)

    def show_alert(self, message, button_text=None):
        self.message_label.setText(message)
        self.view_btn.setText(button_text or t("alert_view_btn"))
        self.setVisible(True)

    def retranslate(self):
        if self.isVisible():
            self.view_btn.setText(t("alert_view_btn"))

    def _dismiss(self):
        self.setVisible(False)
        self.dismiss_clicked.emit()
