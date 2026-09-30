# نافذة الإقلاع الاحترافية (Splash Screen)
# =========================================
# تظهر عند بدء التطبيق: شعار أعمدة بيانية متحرك + اسم التطبيق + شريط تقدّم
# ثم تُغلق تلقائياً بعد ~3 ثوانٍ ليفتح التطبيق الرئيسي.
# ملاحظة: PyQt6 (تمت الهجرة من PyQt5) — كل التعدادات مُنطّقة بالكامل.

import math

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush

from config import APP_VERSION
from ui.resources.i18n import t


class AnimatedBarLogo(QWidget):
    """شعار أعمدة بيانية متحرك (بارات تطلع وتنزل مثل الإيكولايزر).

    يرسم 5 أعمدة بذيول دائرية بتدرج لوني بنفسجي، تنمو من الصفر عند البدء
    ثم تنبض بشكل مستمر بحركة ساينوس ناعمة — يعطي إحساساً حياً واحترافياً.
    """

    BAR_COUNT = 5
    TARGET_HEIGHTS = (0.42, 0.62, 0.80, 0.92, 1.0)
    TOP_COLOR = "#B388FF"
    BOTTOM_COLOR = "#7C4DFF"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 120)
        self._phase = 0.0
        self._grow = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

    def _tick(self):
        self._phase += 0.16
        self._grow = min(1.0, self._grow + 0.05)
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        gap = w / (self.BAR_COUNT * 2 + 1)
        bar_w = gap * 1.35
        max_bar_h = h * 0.78
        baseline = h - 4

        for i in range(self.BAR_COUNT):
            target = self.TARGET_HEIGHTS[i]
            wave = 1.0 + 0.12 * math.sin(self._phase + i * 0.9)
            bar_h = max(2.0, target * max_bar_h * wave * self._grow)
            x = gap + i * (gap * 2) - bar_w / 2
            y = baseline - bar_h

            grad = QLinearGradient(x, y, x, baseline)
            grad.setColorAt(0.0, QColor(self.TOP_COLOR))
            grad.setColorAt(1.0, QColor(self.BOTTOM_COLOR))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 9, 9)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 28))
        p.drawRoundedRect(QRectF(gap * 0.4, baseline, w - gap * 0.8, 2.5), 1, 1)


class ModernSplashScreen(QWidget):
    """نافذة إقلاع حديثة بتدرج لوني احترافي وشريط تقدّم متحرك."""

    WIDTH = 520
    HEIGHT = 340

    def __init__(self):
        super().__init__()
        self._init_ui()
        self.center()

    def _init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint
        )
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        self.setStyleSheet("""
            ModernSplashScreen {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #0F0F23, stop:0.55 #1A1A35, stop:1 #2A1B5E);
            }
            QLabel#splashTitle { color: #FFFFFF; font-size: 26px; font-weight: bold; background: transparent; }
            QLabel#splashSubtitle { color: #B0BEC5; font-size: 13px; background: transparent; }
            QLabel#splashStatus { color: #E8EAF6; font-size: 12px; background: transparent; }
            QProgressBar {
                border: none;
                background-color: rgba(255,255,255,0.12);
                border-radius: 6px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #7C4DFF;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        layout.addStretch(1)

        self.logo = AnimatedBarLogo()
        logo_row = QVBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(logo_row)

        title = QLabel(t("app_name"))
        title.setObjectName("splashTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(f"{t('splash_subtitle')} · v{APP_VERSION}")
        subtitle.setObjectName("splashSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addStretch(1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel(t("splash_loading"))
        self.status_label.setObjectName("splashStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def center(self):
        """توسيط النافذة على الشاشة الأساسية."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        rect = screen.availableGeometry()
        x = rect.x() + (rect.width() - self.width()) // 2
        y = rect.y() + (rect.height() - self.height()) // 2
        self.move(x, y)

    def update_progress(self, value, message):
        """تحديث شريط التقدّم ونص الحالة ثم معالجة أحداث الواجهة فوراً."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        QApplication.processEvents()
