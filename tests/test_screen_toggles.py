"""Tests for per-user screen assignment (admin distributes screens)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

import modules.user_manager as um
from modules.user_manager import user_manager, ROLE_ADMIN, ROLE_VIEWER


class TestScreenAssignment(unittest.TestCase):

    def setUp(self):
        user_manager._users = {}
        user_manager._users["admin"] = {
            "password": "x", "role": ROLE_ADMIN, "created": "2026",
            "display_name": "Admin", "email": "admin@test.dz",
        }
        user_manager._users["member"] = {
            "password": "x", "role": ROLE_VIEWER, "created": "2026",
            "display_name": "Member", "email": "member@test.dz",
        }

    def test_admin_always_all_screens(self):
        self.assertIsNone(user_manager.get_allowed_screens("admin"))

    def test_user_without_field_gets_all(self):
        self.assertIsNone(user_manager.get_allowed_screens("member"))

    def test_set_and_get_roundtrip(self):
        self.assertTrue(user_manager.set_allowed_screens("member", [3, 9, 20]))
        allowed = user_manager.get_allowed_screens("member")
        self.assertEqual(allowed, [1, 2, 3, 9, 20])

    def test_mandatory_screens_always_included(self):
        user_manager.set_allowed_screens("member", [30])
        allowed = user_manager.get_allowed_screens("member")
        self.assertIn(1, allowed)
        self.assertIn(2, allowed)

    def test_unknown_user_returns_none(self):
        self.assertIsNone(user_manager.get_allowed_screens("ghost"))

    def test_set_unknown_user_fails(self):
        self.assertFalse(user_manager.set_allowed_screens("ghost", [3]))

    def test_list_users_excludes_passwords(self):
        users = user_manager.list_users()
        self.assertEqual(len(users), 2)
        for u in users:
            self.assertNotIn("password", u)

    def test_non_int_entries_filtered(self):
        user_manager.set_allowed_screens("member", [3, "x", None, 9])
        allowed = user_manager.get_allowed_screens("member")
        self.assertEqual(allowed, [1, 2, 3, 9])


class TestMainWindowScreenFilter(unittest.TestCase):
    """التحقق أن شريط الشاشات وحراسة التنقل يحترمان التوزيع."""

    def setUp(self):
        user_manager._users = {}
        user_manager._users["member"] = {
            "password": um._hash_password("Passw0rd!"),
            "role": ROLE_VIEWER, "created": "2026",
            "display_name": "Member", "email": "member@test.dz",
            "must_change_password": False,
        }
        user_manager.set_allowed_screens("member", [3, 9])
        from ui.main_window import MainWindow
        self.win = MainWindow()
        if hasattr(self.win, "auto_save_timer"):
            self.win.auto_save_timer.stop()

    def tearDown(self):
        user_manager._users = {}
        user_manager._current_user = None
        self.win.close()

    def _login_member(self):
        self.win.login_view.login_email.setText("member@test.dz")
        self.win.login_view.login_password.setText("Passw0rd!")
        import unittest.mock as mock
        with mock.patch.object(user_manager, "needs_password_change",
                               return_value=False):
            self.win.login_view.do_login()

    def test_ribbon_contains_only_allowed_views(self):
        self._login_member()
        visible = set(self.win.ribbon_view_to_tab.keys())
        self.assertIn(3, visible)
        self.assertIn(9, visible)
        self.assertIn(1, visible)
        self.assertIn(2, visible)
        self.assertNotIn(10, visible)
        self.assertNotIn(39, visible)

    def test_go_to_view_blocks_disallowed(self):
        self._login_member()
        self.win._go_to_view(10)
        self.assertNotEqual(self.win.content.currentIndex(), 10)

    def test_go_to_view_allows_assigned(self):
        self._login_member()
        self.win._go_to_view(3)
        self.assertEqual(self.win.content.currentIndex(), 3)

    def test_admin_sees_all_views(self):
        user_manager._users["admin"] = {
            "password": um._hash_password("Passw0rd!"),
            "role": ROLE_ADMIN, "created": "2026",
            "display_name": "Admin", "email": "admin@test.dz",
            "must_change_password": False,
        }
        self.win.login_view.login_email.setText("admin@test.dz")
        self.win.login_view.login_password.setText("Passw0rd!")
        import unittest.mock as mock
        with mock.patch.object(user_manager, "needs_password_change",
                               return_value=False):
            self.win.login_view.do_login()
        self.assertIn(39, self.win.ribbon_view_to_tab)


if __name__ == "__main__":
    unittest.main()
