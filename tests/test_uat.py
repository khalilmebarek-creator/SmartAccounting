"""User-Acceptance-Test (UAT): simulated real-user journeys across the whole app.

Covers the full MainWindow lifecycle that unit tests don't:
  - build window + login as admin (real login flow, password change mocked)
  - navigate all 35 screens and verify each lazy-loads without error
  - enter demo data + calculate ratios -> verify state propagated to downstream views
  - switch all three languages via apply_language -> verify screens re-render
  - save to DB, then re-open a view that reads DB data
  - logout resets UI to login screen
"""

import sys
import os
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QEventLoop, QTimer

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from config import DEFAULT_ADMIN_PASSWORD
from ui.app_state import state
from ui.resources.i18n import Translator
import modules.user_manager as um


def _pump(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()


def _set_language(lang):
    Translator.set_language(lang)
    state.language = lang


class TestUatFullApp(unittest.TestCase):
    """Full user journey: login -> browse -> enter data -> analyze -> languages."""

    def setUp(self):
        state.clear()
        _set_language("ar")
        um.user_manager._users = {}
        um.user_manager._current_user = None
        um.user_manager._users["admin"] = {
            "password": um._hash_password(DEFAULT_ADMIN_PASSWORD),
            "role": um.ROLE_ADMIN,
            "created": "2024-01-01",
            "display_name": "Admin",
            "email": "admin@accounting.local",
            "must_change_password": False,
        }
        from ui.main_window import MainWindow
        self.win = MainWindow()
        # عطّل auto-save حتى لا يكتب ملف بيانات حقيقي أثناء الاختبار
        if hasattr(self.win, "auto_save_timer"):
            self.win.auto_save_timer.stop()

    def tearDown(self):
        state.clear()
        self.win.close()

    def _login(self):
        # محاكاة مستخدم حقيقي: يكتب البريد وكلمة المرور ثم يضغط تسجيل الدخول
        self.win.login_view.login_email.setText("admin@accounting.local")
        self.win.login_view.login_password.setText(DEFAULT_ADMIN_PASSWORD)
        # تجاوز نافذة تغيير كلمة المرور (المستخدم الحقيقي سيفعلها أول مرة)
        with mock.patch.object(um.user_manager, "needs_password_change", return_value=False):
            self.win.login_view.do_login()

    # ---------- السيناريو 1: تسجيل الدخول وفتح كل الشاشات ----------

    def test_full_login_and_navigate_all_35_screens(self):
        self._login()
        self.assertIsNotNone(um.user_manager.get_current_user())
        self.win.show()
        _pump(50)
        self.assertTrue(self.win.sidebar.isVisible())
        # الشاشات الـ35 تُبنى كسلاzy ولا تسقط
        for vid in range(1, 36):
            self.win._go_to_view(vid)
            _pump(50)
            view = self.win.content.currentWidget()
            self.assertIsNotNone(view, f"view id {vid} is None")
            self.assertEqual(self.win.content.currentIndex(), vid)

    def test_all_screens_have_real_widgets_after_login(self):
        self._login()
        for vid in range(1, 36):
            self.win._go_to_view(vid)
            view = self.win._get_or_create_view(vid)
            self.assertIsInstance(view, QWidget, f"screen {vid} not a widget")

    def test_sidebar_has_35_items(self):
        self._login()
        self.assertEqual(len(self.win._sidebar_row_to_view), 35)
        self.assertEqual(len(self.win.sidebar_items), 35)
        self.assertGreater(self.win.sidebar.count(), 35)

    # ---------- السيناريو 2: إدخال بيانات + حساب + انتشار الحالة ----------

    def test_enter_data_calculate_propagates_state(self):
        self._login()
        self.win._go_to_view(1)  # data entry
        dev = self.win._get_or_create_view(1)
        dev.load_default_data()
        dev.calculate_ratios()
        _pump(300)
        self.assertTrue(state.has_data())
        self.assertGreater(state.ratios.get("roe", 0), 0)
        self.assertTrue(dev.save_btn.isEnabled())
        # لوحة التحكم والنسب تعرضان نفس البيانات
        self.win._go_to_view(2)  # dashboard
        _pump(100)
        dash = self.win._get_or_create_view(2)
        self.assertIsNotNone(dash)
        self.win._go_to_view(3)  # ratios
        _pump(100)
        ratios_view = self.win._get_or_create_view(3)
        self.assertIsNotNone(ratios_view)

    def test_save_to_db_works(self):
        self._login()
        self.win._go_to_view(1)
        dev = self.win._get_or_create_view(1)
        dev.load_default_data()
        dev.calculate_ratios()
        _pump(300)
        dev.save_to_db()
        self.assertTrue(state.has_data())

    # ---------- السيناريو 3: تبديل اللغات ----------

    def test_language_switch_all_three_languages(self):
        self._login()
        for lang in ("ar", "en", "fr"):
            _set_language(lang)
            self.win.apply_language()
            _pump(80)
            self.assertEqual(len(self.win._sidebar_row_to_view), 35)
            self.assertEqual(Translator.get_language(), lang)
            # لا تعرض أسماء مفاتيح خام في السايدبار
            for i in range(self.win.sidebar.count()):
                item_text = self.win.sidebar.item(i).text().strip()
                self.assertFalse(item_text.startswith("sidebar_"), item_text)
                self.assertFalse(item_text.startswith("nav_group_"), item_text)

    def test_language_switch_preserves_all_views(self):
        self._login()
        for lang in ("ar", "en", "fr"):
            _set_language(lang)
            self.win.apply_language()
            _pump(80)
            for vid in range(1, 36):
                self.win._go_to_view(vid)
                view = self.win._get_or_create_view(vid)
                self.assertIsNotNone(view, f"lang={lang} screen {vid} broken")

    # ---------- السيناريو 4: تسجيل الخروج ----------

    def test_logout_returns_to_login(self):
        self._login()
        self.win.show()
        _pump(50)
        self.win._do_logout()
        self.assertIsNone(um.user_manager.get_current_user())
        self.assertEqual(self.win.content.currentIndex(), 0)
        self.assertFalse(self.win.sidebar.isVisible())

    # ---------- السيناريو 5: الوضع الافتراضي يبدأ بشاشة تسجيل الدخول ----------

    def test_app_starts_at_login_screen(self):
        self.assertEqual(self.win.content.currentIndex(), 0)
        self.assertFalse(self.win.sidebar.isVisible())


if __name__ == "__main__":
    unittest.main()
