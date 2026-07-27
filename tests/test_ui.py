"""UI tests for login, user manager, and key views."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from modules.user_manager import UserManager, ROLE_ADMIN, _hash_password


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.um = UserManager()
        self.um._users = {}
        self.um._current_user = None
        self.um._users["admin"] = {
            "password": _hash_password("Admin@1234"),
            "role": ROLE_ADMIN,
            "created": "2024-01-01",
            "display_name": "Admin",
            "email": "admin@test.com"
        }

    def test_login_success(self):
        ok, code, extra = self.um.login("admin@test.com", "Admin@1234")
        self.assertTrue(ok)
        self.assertEqual(code, "ok")
        self.assertTrue(self.um.is_logged_in())

    def test_login_wrong_password(self):
        ok, code, extra = self.um.login("admin@test.com", "wrong")
        self.assertFalse(ok)
        self.assertEqual(code, "err_wrong_password")

    def test_login_nonexistent_email(self):
        ok, code, extra = self.um.login("nobody@test.com", "pass")
        self.assertFalse(ok)
        self.assertEqual(code, "err_email_not_found")

    def test_login_lockout(self):
        for _ in range(5):
            self.um.login("admin@test.com", "wrong")
        ok, code, extra = self.um.login("admin@test.com", "wrong")
        self.assertFalse(ok)
        self.assertEqual(code, "err_locked")
        self.assertIn("minutes", extra)

    def test_logout(self):
        self.um.login("admin@test.com", "Admin@1234")
        self.um.logout()
        self.assertFalse(self.um.is_logged_in())
        self.assertIsNone(self.um.get_current_user())

    def test_register_success(self):
        ok, code = self.um.register("user1@test.com", "Test@1234", "User One")
        self.assertTrue(ok)
        _, udata = self.um._find_by_email("user1@test.com")
        self.assertIsNotNone(udata)
        self.assertEqual(udata["email"], "user1@test.com")

    def test_register_role_default_viewer(self):
        ok, code = self.um.register("newuser1@test.com", "Test@1234", "New User")
        self.assertTrue(ok)
        _, udata = self.um._find_by_email("newuser1@test.com")
        self.assertIsNotNone(udata)
        self.assertEqual(udata["role"], "viewer")

    def test_register_role_explicit_admin(self):
        from modules.user_manager import ROLE_ADMIN
        ok, code = self.um.register("admin2@test.com", "Test@1234", "Admin2", ROLE_ADMIN)
        self.assertTrue(ok)
        _, udata = self.um._find_by_email("admin2@test.com")
        self.assertIsNotNone(udata)
        self.assertEqual(udata["role"], ROLE_ADMIN)

    def test_register_duplicate_email(self):
        ok, code = self.um.register("admin@test.com", "Test@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_email_exists")

    def test_register_invalid_email(self):
        ok, code = self.um.register("not-an-email", "Test@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_invalid_email")

    def test_register_weak_password(self):
        ok, code = self.um.register("newuser@test.com", "ab")
        self.assertFalse(ok)
        self.assertIn("password", code)

    def test_register_password_no_upper(self):
        ok, code = self.um.register("newuser@test.com", "test@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_password_no_upper")

    def test_register_password_no_digit(self):
        ok, code = self.um.register("newuser@test.com", "Test@abcd")
        self.assertFalse(ok)
        self.assertEqual(code, "err_password_no_digit")

    def test_change_password_success(self):
        self.um.login("admin@test.com", "Admin@1234")
        ok, code = self.um.change_password("admin", "Admin@1234", "NewPass@1234")
        self.assertTrue(ok)
        ok2, _, _ = self.um.login("admin@test.com", "NewPass@1234")
        self.assertTrue(ok2)

    def test_change_password_wrong_old(self):
        self.um.login("admin@test.com", "Admin@1234")
        ok, code = self.um.change_password("admin", "WrongOld", "NewPass@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_wrong_password")

    def test_delete_user(self):
        self.um.register("user2@test.com", "Test@1234")
        username, _ = self.um._find_by_email("user2@test.com")
        ok, msg = self.um.delete_user(username)
        self.assertTrue(ok)

    def test_cannot_delete_admin(self):
        ok, msg = self.um.delete_user("admin")
        self.assertFalse(ok)

    def test_is_admin(self):
        self.um.login("admin@test.com", "Admin@1234")
        self.assertTrue(self.um.is_admin())

    def test_get_all_users(self):
        users = self.um.get_all_users()
        self.assertGreaterEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "admin")

    def test_reset_password_by_email(self):
        ok, code = self.um.reset_password_by_email("admin@test.com", "Reset@1234")
        self.assertTrue(ok)
        udata = self.um._users["admin"]
        self.assertTrue(udata.get("must_change_password"))
        ok2, _, _ = self.um.login("admin@test.com", "Reset@1234")
        self.assertTrue(ok2)

    def test_reset_password_email_not_found(self):
        ok, code = self.um.reset_password_by_email("ghost@test.com", "Reset@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_email_not_found")

    def test_permissions_admin_has_all(self):
        from modules.user_manager import ROLE_ADMIN, PERMISSIONS
        self.um.login("admin@test.com", "Admin@1234")
        for perm in PERMISSIONS[ROLE_ADMIN]:
            self.assertTrue(self.um.has_permission(perm))

    def test_permissions_viewer_limited(self):
        from modules.user_manager import ROLE_VIEWER, PERMISSIONS
        self.um.register("viewer@test.com", "Test@1234", "Viewer")
        self.um._current_user = {"username": "viewer", "role": ROLE_VIEWER}
        for perm in PERMISSIONS[ROLE_VIEWER]:
            self.assertTrue(self.um.has_permission(perm))
        self.assertFalse(self.um.has_permission("manage_users"))
        self.assertFalse(self.um.has_permission("enter_data"))

    def test_generate_otp(self):
        from modules.user_manager import generate_otp
        otp = generate_otp(6)
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())


class TestReportTemplates(unittest.TestCase):

    def test_get_all_templates(self):
        from modules.report_templates import report_templates
        templates = report_templates.get_all_templates()
        self.assertGreaterEqual(len(templates), 5)

    def test_get_template(self):
        from modules.report_templates import report_templates
        t = report_templates.get_template("financial_summary")
        self.assertIsNotNone(t)
        self.assertIn("sections", t)

    def test_create_custom_template(self):
        from modules.report_templates import report_templates
        ok = report_templates.create_template("custom_test", {
            "name": "Test", "sections": ["summary"]
        })
        self.assertTrue(ok)
        report_templates.delete_template("custom_test")


class TestScheduledBackup(unittest.TestCase):

    def test_manual_backup(self):
        from modules.scheduled_backup import scheduled_backup
        filename = scheduled_backup.manual_backup()
        self.assertIsNotNone(filename)
        self.assertTrue(filename.startswith("backup_"))

    def test_get_backups(self):
        from modules.scheduled_backup import scheduled_backup
        scheduled_backup.manual_backup()
        backups = scheduled_backup.get_backups()
        self.assertGreater(len(backups), 0)


class TestLoginUI(unittest.TestCase):

    def test_login_view_creation(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertIsNotNone(view)
        self.assertEqual(view.stack.currentIndex(), 0)

    def test_login_view_switch_to_register(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.stack.setCurrentIndex(1)
        self.assertEqual(view.stack.currentIndex(), 1)

    def test_register_no_role_selector(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertFalse(hasattr(view, 'reg_role'))

    def test_forgot_link_hidden_initially(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertTrue(view.forgot_link.isHidden())

    def test_forgot_link_shows_on_error(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.show()
        view.login_email.setText("wrong@test.com")
        view.login_password.setText("wrong")
        view.do_login()
        self.assertTrue(view.forgot_link.isVisible())


if __name__ == "__main__":
    unittest.main(verbosity=2)
