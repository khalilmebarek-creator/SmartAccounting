# Loading overlay widget
# ======================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor


class LoadingOverlay(QWidget):
    """Full-parent overlay with spinner text + progress bar."""

    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(0, 0, 0, 120);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        self.status_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedWidth(300)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: #4CAF50;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px; background: transparent;")
        layout.addWidget(self.detail_label)

        self.hide()

    def show_message(self, text, detail=""):
        self.status_label.setText(text)
        self.detail_label.setText(detail)
        self.setFixedSize(self.parent().size())
        self.show()
        self.raise_()

    def set_progress(self, value):
        self.progress.setRange(0, 100)
        self.progress.setValue(value)

    def set_indeterminate(self):
        self.progress.setRange(0, 0)

    def update_detail(self, text):
        self.detail_label.setText(text)

    def resizeEvent(self, event):
        if self.parent():
            self.setFixedSize(self.parent().size())
        super().resizeEvent(event)


class SpinnerWidget(QWidget):
    """Simple animated dots spinner as a label replacement."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dots = 0
        self._label = QLabel("●○○○○")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("color: #4CAF50; font-size: 18px; background: transparent;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)

    def start(self):
        self._dots = 0
        self._timer.start(300)
        self.show()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _animate(self):
        self._dots = (self._dots + 1) % 5
        text = "●" + "○" * self._dots + "○" * (4 - self._dots)
        self._label.setText(text)
