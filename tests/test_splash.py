# اختبار نافذة الإقلاع (Splash Screen)
# =====================================
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)


class TestModernSplashScreen(unittest.TestCase):
    """نافذة الإقلاع: بنية سليمة + شريط تقدّم يعمل + رسائل قابلة للتحديث."""

    def setUp(self):
        from ui.splash import ModernSplashScreen
        self.splash = ModernSplashScreen()

    def tearDown(self):
        self.splash.close()
        self.splash.deleteLater()
        QApplication.processEvents()

    def test_splash_has_splash_window_flags(self):
        flags = self.splash.windowFlags()
        self.assertTrue(flags & Qt.WindowType.SplashScreen)
        self.assertTrue(flags & Qt.WindowType.FramelessWindowHint)

    def test_splash_fixed_size(self):
        from ui.splash import ModernSplashScreen
        self.assertEqual(self.splash.width(), ModernSplashScreen.WIDTH)
        self.assertEqual(self.splash.height(), ModernSplashScreen.HEIGHT)

    def test_progress_bar_starts_at_zero(self):
        bar = self.splash.progress_bar
        self.assertEqual(bar.minimum(), 0)
        self.assertEqual(bar.maximum(), 100)
        self.assertEqual(bar.value(), 0)

    def test_update_progress_updates_bar_and_status(self):
        self.splash.update_progress(50, "اختبار")
        self.assertEqual(self.splash.progress_bar.value(), 50)
        self.assertEqual(self.splash.status_label.text(), "اختبار")

    def test_title_label_uses_app_name(self):
        from ui.resources.i18n import t
        title = self.splash.findChild(QLabel, "splashTitle")
        self.assertIsNotNone(title)
        self.assertEqual(title.text(), t("app_name"))

    def test_animated_logo_is_present(self):
        from ui.splash import AnimatedBarLogo
        logo = self.splash.logo
        self.assertIsInstance(logo, AnimatedBarLogo)
        self.assertEqual(logo.width(), 180)
        self.assertEqual(logo.height(), 120)


if __name__ == "__main__":
    unittest.main(verbosity=2)
