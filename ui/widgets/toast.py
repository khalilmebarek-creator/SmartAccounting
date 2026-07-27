# Toast notification widget
# =========================

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont


class Toast(QWidget):
    """Lightweight auto-dismissing notification bar."""

    _instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedHeight(48)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)

        self.label = QLabel()
        self.label.setWordWrap(True)
        font = QFont("Segoe UI", 10)
        self.label.setFont(font)
        layout.addWidget(self.label)

        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)

        self._fade_in = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_in.setDuration(200)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)

        self._fade_out = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_out.setDuration(350)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)
        self._fade_out.finished.connect(self.hide)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss)

    def _apply_style(self, msg_type):
        colors = {
            "success": ("#1B5E20", "#C8E6C9", "#2E7D32"),
            "error": ("#B71C1C", "#FFCDD2", "#D32F2F"),
            "warning": ("#E65100", "#FFF3E0", "#EF6C00"),
            "info": ("#0D47A1", "#BBDEFB", "#1565C0"),
        }
        fg, bg, border = colors.get(msg_type, colors["info"])
        self.label.setStyleSheet(f"color: {fg}; background: transparent;")
        self.setStyleSheet(
            f"Toast {{ background: {bg}; border: 1px solid {border}; border-radius: 8px; }}"
        )

    def show_message(self, text, msg_type="info", duration=3000):
        self.label.setText(text)
        self._apply_style(msg_type)
        self.adjustSize()

        if self.parent():
            pw = self.parent().width()
            self.setFixedWidth(min(max(self.sizeHint().width() + 30, 300), 500))
            x = (pw - self.width()) // 2
            y = self.parent().height() - self.height() - 20
            self.move(x, y)

        self.show()
        self.raise_()
        self._fade_in.stop()
        self._fade_out.stop()
        self._opacity.setOpacity(1.0)
        self._fade_in.start()
        self._timer.start(duration)

    def _dismiss(self):
        self._fade_out.start()

    @staticmethod
    def show_in(parent, text, msg_type="info", duration=3000):
        toast = Toast(parent)
        toast.show_message(text, msg_type, duration)
        return toast


def toast_success(parent, text, duration=3000):
    return Toast.show_in(parent, text, "success", duration)


def toast_error(parent, text, duration=4000):
    return Toast.show_in(parent, text, "error", duration)


def toast_warning(parent, text, duration=3500):
    return Toast.show_in(parent, text, "warning", duration)


def toast_info(parent, text, duration=3000):
    return Toast.show_in(parent, text, "info", duration)
