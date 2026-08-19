"""Remember-me session tests: encrypted saved credentials + auto-login.

TDD for the "save account and password" feature on the login/register
screen: when enabled, the app skips the login screen on next launch.

Security design: the password is NEVER stored in plaintext — it is
encrypted with AES-256-GCM using a key derived from the machine hardware
fingerprint (commercial.licensing.hardware_id), so the saved session only
works on the device where it was created.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEventLoop, QTimer

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from config import DEFAULT_ADMIN_PASSWORD
from ui.app_state import state
from ui.resources.i18n import Translator
import ui.login_session as login_session
import modules.user_manager as um
from modules.user_manager import _hash_password


def _pump(ms=30):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def _set_language(lang):
    Translator.set_language(lang)
    state.language = lang


class TempSessionMixin:

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp(prefix="login_session_test_")
        self._session_file = os.path.join(self._tmpdir, "login_session.json")
        patcher = mock.patch.object(login_session, "SESSION_FILE", self._session_file)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(shutil.rmtree, self._tmpdir, True)

    def _write_raw(self, payload: dict):
        with open(self._session_file, "w", encoding="utf-8") as f:
            json.dump(payload, f)


class TestLoginSessionStore(TempSessionMixin, unittest.TestCase):
    """Pure storage layer: encrypted remember-me payload."""

    def test_save_remember_creates_encrypted_blob(self):
        login_session.save_login_session("user@x.com", "Secret#123", True)
        with open(self._session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["last_email"], "user@x.com")
        self.assertIn("saved_password", data)
        self.assertNotEqual(data["saved_password"], "Secret#123")

    def test_plaintext_password_never_written_to_disk(self):
        login_session.save_login_session("user@x.com", "Secret#123", True)
        with open(self._session_file, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"Secret#123", raw)

    def test_roundtrip_remember(self):
        login_session.save_login_session("user@x.com", "Secret#123", True)
        email, password = login_session.load_login_session()
        self.assertEqual(email, "user@x.com")
        self.assertEqual(password, "Secret#123")

    def test_save_without_remember_keeps_email_only(self):
        login_session.save_login_session("user@x.com", "Secret#123", False)
        email, password = login_session.load_login_session()
        self.assertEqual(email, "user@x.com")
        self.assertEqual(password, "")

    def test_legacy_email_only_file(self):
        self._write_raw({"last_email": "legacy@x.com"})
        email, password = login_session.load_login_session()
        self.assertEqual(email, "legacy@x.com")
        self.assertEqual(password, "")

    def test_missing_file_returns_empty(self):
        email, password = login_session.load_login_session()
        self.assertEqual((email, password), ("", ""))

    def test_corrupted_file_returns_empty_safely(self):
        with open(self._session_file, "w", encoding="utf-8") as f:
            f.write("not json {{{")
        email, password = login_session.load_login_session()
        self.assertEqual((email, password), ("", ""))

    def test_other_device_cannot_decrypt_password(self):
        login_session.save_login_session("user@x.com", "Secret#123", True)
        with mock.patch.object(login_session, "_device_fingerprint", return_value="other-device"):
            email, password = login_session.load_login_session()
        self.assertEqual(email, "user@x.com")
        self.assertEqual(password, "")

    def test_clear_saved_password_keeps_email(self):
        login_session.save_login_session("user@x.com", "Secret#123", True)
        login_session.clear_saved_password()
        email, password = login_session.load_login_session()
        self.assertEqual(email, "user@x.com")
        self.assertEqual(password, "")

    def test_save_login_email_legacy_still_works(self):
        login_session.save_login_email("old@x.com")
        self.assertEqual(login_session.load_login_email(), "old@x.com")

    def test_save_login_session_falls_back_when_encryption_fails(self):
        with mock.patch.object(login_session, "encrypt_bytes",
                               side_effect=Exception("crypto down")):
            login_session.save_login_session("user@x.com", "Secret#123", True)
        email, password = login_session.load_login_session()
        self.assertEqual(email, "user@x.com")
        self.assertEqual(password, "")

    def test_load_corrupted_saved_password_returns_empty(self):
        login_session.save_login_session("user@x.com", "Secret#123", True)
        with open(self._session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["saved_password"] = "!!!not-base64!!!"
        with open(self._session_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        email, password = login_session.load_login_session()
        self.assertEqual((email, password), ("", ""))

    def test_clear_saved_password_on_corrupt_file_is_safe(self):
        self._write_raw({"last_email": "x", "saved_password": "@@@@", "fingerprint_hash": "y"})
        login_session.clear_saved_password()
        email, password = login_session.load_login_session()
        self.assertEqual((email, password), ("x", ""))

    def test_save_login_email_silent_on_io_error(self):
        with mock.patch("builtins.open", side_effect=OSError("readonly")):
            login_session.save_login_email("x@x.com")
        self.assertEqual(login_session.load_login_email(), "")

    def test_load_login_email_on_corrupt_file_returns_empty(self):
        with open(self._session_file, "w", encoding="utf-8") as f:
            f.write("{broken")
        self.assertEqual(login_session.load_login_email(), "")

    def test_clear_saved_password_silent_on_io_error(self):
        login_session.save_login_session("user@x.com", "Secret#123", True)
        with mock.patch("builtins.open", side_effect=OSError("readonly")):
            login_session.clear_saved_password()

    def test_clear_login_email_removes_file(self):
        login_session.save_login_email("gone@x.com")
        login_session.clear_login_email()
        self.assertFalse(os.path.exists(self._session_file))

    def test_clear_login_email_silent_on_io_error(self):
        login_session.save_login_email("x@x.com")
        with mock.patch("ui.login_session.os.remove", side_effect=OSError("locked")):
            login_session.clear_login_email()
        login_session.save_login_email("kept@x.com")
        self.assertEqual(login_session.load_login_email(), "kept@x.com")


class TestLoginViewRemember(unittest.TestCase):
    """UI wiring: checkboxes + saving session on successful login."""

    def setUp(self):
        _set_language("ar")
        um.user_manager._users = {}
        um.user_manager._current_user = None
        um.user_manager._users["admin"] = {
            "password": _hash_password(DEFAULT_ADMIN_PASSWORD),
            "role": um.ROLE_ADMIN,
            "created": "2024-01-01",
            "display_name": "Admin",
            "email": "admin@accounting.local",
            "must_change_password": False,
        }

    def tearDown(self):
        state.clear()

    def test_login_page_has_remember_checkbox(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertTrue(hasattr(view, "login_remember"))
        self.assertTrue(view.login_remember.isEnabled())

    def test_register_page_has_remember_checkbox(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertTrue(hasattr(view, "reg_remember"))
        self.assertTrue(view.reg_remember.isEnabled())

    def test_do_login_saves_session_when_checked(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.login_email.setText("admin@accounting.local")
        view.login_password.setText(DEFAULT_ADMIN_PASSWORD)
        view.login_remember.setChecked(True)
        with mock.patch.object(um.user_manager, "needs_password_change", return_value=False), \
                mock.patch("ui.views.login_view.save_login_session") as mock_save:
            view.do_login()
        mock_save.assert_called_once()
        _, _, remember = mock_save.call_args[0]
        self.assertTrue(remember)

    def test_do_login_no_session_when_unchecked(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.login_email.setText("admin@accounting.local")
        view.login_password.setText(DEFAULT_ADMIN_PASSWORD)
        view.login_remember.setChecked(False)
        with mock.patch.object(um.user_manager, "needs_password_change", return_value=False), \
                mock.patch("ui.views.login_view.save_login_session") as mock_save:
            view.do_login()
        mock_save.assert_called_once()
        _, _, remember = mock_save.call_args[0]
        self.assertFalse(remember)

    def test_go_to_login_propagates_remember_state(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.reg_remember.setChecked(True)
        view._go_to_login_from_register()
        self.assertTrue(view.login_remember.isChecked())

    def test_do_register_propagates_remember_state(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.reg_email.setText("new@x.com")
        view.reg_password.setText("Strong#123")
        view.reg_remember.setChecked(True)
        with mock.patch.object(um.user_manager, "register", return_value=(True, "ok")):
            view.do_register()
        self.assertTrue(view.login_remember.isChecked())
        self.assertEqual(view.stack.currentIndex(), 0)


class TestMainWindowAutoLogin(TempSessionMixin, unittest.TestCase):
    """Full-window behaviour: skip login screen when a valid session exists."""

    def setUp(self):
        super().setUp()
        _set_language("ar")
        um.user_manager._users = {}
        um.user_manager._current_user = None
        um.user_manager._users["admin"] = {
            "password": _hash_password(DEFAULT_ADMIN_PASSWORD),
            "role": um.ROLE_ADMIN,
            "created": "2024-01-01",
            "display_name": "Admin",
            "email": "admin@accounting.local",
            "must_change_password": False,
        }

    def tearDown(self):
        state.clear()
        if getattr(self, "win", None) is not None:
            self.win.close()

    def _build_window(self):
        from ui.main_window import MainWindow
        self.win = MainWindow()
        if hasattr(self.win, "auto_save_timer"):
            self.win.auto_save_timer.stop()

    def test_auto_login_with_valid_session(self):
        login_session.save_login_session("admin@accounting.local", DEFAULT_ADMIN_PASSWORD, True)
        self._build_window()
        _pump(60)
        self.assertIsNotNone(um.user_manager.get_current_user())
        self.assertEqual(um.user_manager.get_current_user()["username"], "admin")
        self.assertIsNot(self.win.content.currentWidget(), self.win.login_view)
        self.assertGreater(self.win.content.currentIndex(), 0)

    def test_no_auto_login_without_session(self):
        self._build_window()
        _pump(60)
        self.assertIsNone(um.user_manager.get_current_user())
        self.assertEqual(self.win.content.currentIndex(), 0)

    def test_no_auto_login_with_wrong_password(self):
        login_session.save_login_session("admin@accounting.local", "WrongPass#99", True)
        self._build_window()
        _pump(60)
        self.assertIsNone(um.user_manager.get_current_user())
        self.assertEqual(self.win.content.currentIndex(), 0)

    def test_no_auto_login_when_password_change_required(self):
        um.user_manager._users["admin"]["must_change_password"] = True
        login_session.save_login_session("admin@accounting.local", DEFAULT_ADMIN_PASSWORD, True)
        self._build_window()
        _pump(60)
        self.assertIsNone(um.user_manager.get_current_user())
        self.assertEqual(self.win.content.currentIndex(), 0)

    def test_do_logout_clears_saved_password(self):
        login_session.save_login_session("admin@accounting.local", DEFAULT_ADMIN_PASSWORD, True)
        self._build_window()
        _pump(60)
        self.assertIsNotNone(um.user_manager.get_current_user())
        self.win._do_logout()
        email, password = login_session.load_login_session()
        self.assertEqual(email, "admin@accounting.local")
        self.assertEqual(password, "")
        self.assertEqual(self.win.content.currentIndex(), 0)


if __name__ == "__main__":
    unittest.main()
