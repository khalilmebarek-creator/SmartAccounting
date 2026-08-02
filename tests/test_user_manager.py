# Unit tests for modules/user_manager.py.
# Covers: password hashing/verification, password strength validation,
# role management, permissions, login/lockout, 2FA OTP, registration,
# password change/reset, and session expiry.

import hashlib
import json
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_ADMIN_PASSWORD
import modules.user_manager as um


def _strong_password():
    return "Strong@123"


def _legacy_sha256(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class TestUserManager(unittest.TestCase):
    """Tests for the UserManager authentication and permission system."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_users_file = um.USERS_FILE
        um.USERS_FILE = os.path.join(self._tmp.name, "users.json")
        self.manager = um.UserManager()
        self.admin_email = "admin@accounting.local"
        self.admin_password = DEFAULT_ADMIN_PASSWORD

    def tearDown(self):
        um.USERS_FILE = self._orig_users_file
        self._tmp.cleanup()

    # ---------- password hashing / verification ----------

    def test_hash_and_verify_roundtrip(self):
        hashed = um._hash_password("Secret@123")
        self.assertIn(":", hashed)
        self.assertTrue(um._verify_password("Secret@123", hashed))
        self.assertFalse(um._verify_password("wrong", hashed))

    def test_verify_password_malformed_stored_value(self):
        self.assertFalse(um._verify_password("x", "no-colon"))
        self.assertFalse(um._verify_password("x", None))

    # ---------- password strength validation ----------

    def test_password_strength_short(self):
        self.assertEqual(
            um.validate_password_strength("Ab1!"), (False, "err_password_short")
        )

    def test_password_strength_no_upper(self):
        self.assertEqual(
            um.validate_password_strength("abc12345!"), (False, "err_password_no_upper")
        )

    def test_password_strength_no_lower(self):
        self.assertEqual(
            um.validate_password_strength("ABC12345!"), (False, "err_password_no_lower")
        )

    def test_password_strength_no_digit(self):
        self.assertEqual(
            um.validate_password_strength("Abcdefgh!"), (False, "err_password_no_digit")
        )

    def test_password_strength_no_special(self):
        self.assertEqual(
            um.validate_password_strength("Abcdefg1"), (False, "err_password_no_special")
        )

    def test_password_strength_valid(self):
        self.assertEqual(um.validate_password_strength("Abcdefg1!"), (True, ""))

    def test_validate_email(self):
        self.assertTrue(um.validate_email("user.name@example.com"))
        self.assertFalse(um.validate_email("not-an-email"))
        self.assertFalse(um.validate_email(""))

    # ---------- loading / default admin ----------

    def test_default_admin_created_when_no_file(self):
        self.assertIn("admin", self.manager._users)
        admin = self.manager._users["admin"]
        self.assertEqual(admin["role"], um.ROLE_ADMIN)
        self.assertTrue(admin["must_change_password"])
        self.assertFalse(admin["two_factor_enabled"])

    def test_load_legacy_dict_without_users_key(self):
        legacy = {
            "bob": {
                "password": um._hash_password("Bob@1234"),
                "role": "viewer",
                "email": "bob@example.com",
            }
        }
        with open(um.USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(legacy, f)
        manager = um.UserManager()
        self.assertEqual(manager._users, legacy)
        self.assertNotIn("admin", manager._users)

    def test_load_legacy_list_format(self):
        legacy = [{"username": "bob", "role": "viewer"}]
        with open(um.USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(legacy, f)
        manager = um.UserManager()
        self.assertEqual(manager._users, legacy)

    def test_load_corrupted_file_falls_back_to_default_admin(self):
        with open(um.USERS_FILE, "w", encoding="utf-8") as f:
            f.write("{ not valid json")
        manager = um.UserManager()
        self.assertIn("admin", manager._users)

    def test_save_error_is_silent(self):
        um.USERS_FILE = os.path.join(self._tmp.name, "missing_dir", "users.json")
        result = self.manager.register(
            "save.fail@example.com", _strong_password(), "SaveFail"
        )
        self.assertEqual(result, (True, "ok"))

    # ---------- login ----------

    def test_login_success_default_admin(self):
        result = self.manager.login(self.admin_email, self.admin_password)
        self.assertEqual(result, (True, "ok", {}))
        current = self.manager.get_current_user()
        self.assertEqual(current["username"], "admin")
        self.assertEqual(current["role"], um.ROLE_ADMIN)
        self.assertTrue(current["must_change_password"])

    def test_login_unknown_email(self):
        self.assertEqual(
            self.manager.login("nobody@nowhere.com", "x"),
            (False, "err_email_not_found", {}),
        )

    def test_login_wrong_password(self):
        result = self.manager.login(self.admin_email, "WrongPass@1")
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "err_wrong_password")
        self.assertEqual(result[2], {"attempts": 4})

    def test_login_lockout_after_max_failures(self):
        for _ in range(5):
            self.manager.login(self.admin_email, "WrongPass@1")
        result = self.manager.login(self.admin_email, "WrongPass@1")
        self.assertEqual(result[1], "err_locked")
        self.assertEqual(result[2], {"minutes": um.LOCKOUT_MINUTES})

    def test_login_locked_account_before_expiry(self):
        self.manager._lockout_until["admin"] = datetime.now() + timedelta(minutes=10)
        result = self.manager.login(self.admin_email, self.admin_password)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "err_locked")
        self.assertIn("minutes", result[2])

    def test_login_after_lockout_expiry_clears_state(self):
        self.manager._lockout_until["admin"] = datetime.now() - timedelta(minutes=1)
        self.manager._failed_attempts["admin"] = 5
        result = self.manager.login(self.admin_email, self.admin_password)
        self.assertEqual(result, (True, "ok", {}))
        self.assertNotIn("admin", self.manager._lockout_until)
        self.assertNotIn("admin", self.manager._failed_attempts)

    def test_login_case_insensitive_email(self):
        result = self.manager.login("  ADMIN@ACCOUNTING.LOCAL ", self.admin_password)
        self.assertEqual(result, (True, "ok", {}))

    # ---------- legacy password migration ----------

    def test_login_migrates_legacy_sha256_password(self):
        self.manager._users["legacy"] = {
            "password": _legacy_sha256("Legacy@123"),
            "role": "viewer",
            "email": "legacy@example.com",
            "display_name": "Legacy",
        }
        result = self.manager.login("legacy@example.com", "Legacy@123")
        self.assertEqual(result, (True, "ok", {}))
        self.assertIn(":", self.manager._users["legacy"]["password"])

    def test_login_wrong_legacy_password_increments_attempts(self):
        self.manager._users["legacy"] = {
            "password": _legacy_sha256("Legacy@123"),
            "role": "viewer",
            "email": "legacy@example.com",
            "display_name": "Legacy",
        }
        result = self.manager.login("legacy@example.com", "WrongLegacy@1")
        self.assertEqual(result[1], "err_wrong_password")
        self.assertEqual(self.manager._failed_attempts["legacy"], 1)

    # ---------- 2FA / OTP ----------

    def test_login_with_two_factor_returns_otp_required(self):
        self.manager.enable_two_factor("admin", True)
        result = self.manager.login(self.admin_email, self.admin_password)
        self.assertEqual(result[0], False)
        self.assertEqual(result[1], "otp_required")
        self.assertIn("email", result[2])

    def test_verify_otp_success_completes_login(self):
        self.manager.enable_two_factor("admin", True)
        self.manager.login(self.admin_email, self.admin_password)
        otp = self.manager._otp_store["admin"]["otp"]
        result = self.manager.verify_otp("ADMIN", otp)
        self.assertEqual(result, (True, "ok", {}))
        self.assertEqual(self.manager.get_current_user()["username"], "admin")

    def test_verify_otp_without_request(self):
        result = self.manager.verify_otp("admin", "123456")
        self.assertEqual(result, (False, "err_otp_expired"))

    def test_verify_otp_expired(self):
        self.manager._otp_store["admin"] = {
            "otp": "123456",
            "expires": (datetime.now() - timedelta(minutes=1)).isoformat(),
        }
        result = self.manager.verify_otp("admin", "123456")
        self.assertEqual(result, (False, "err_otp_expired"))

    def test_verify_otp_wrong_code(self):
        self.manager._otp_store["admin"] = {
            "otp": "123456",
            "expires": (datetime.now() + timedelta(minutes=5)).isoformat(),
        }
        result = self.manager.verify_otp("admin", "999999")
        self.assertEqual(result, (False, "err_otp_wrong"))

    def test_generate_and_send_otp_success(self):
        result = self.manager.generate_and_send_otp(self.admin_email)
        self.assertTrue(result[0])
        self.assertEqual(len(result[1]), 6)
        self.assertEqual(self.manager._otp_store["admin"]["otp"], result[1])

    def test_generate_and_send_otp_unknown_email(self):
        result = self.manager.generate_and_send_otp("ghost@nowhere.com")
        self.assertEqual(result, (False, "err_email_not_found"))

    def test_enable_two_factor(self):
        self.manager.enable_two_factor("admin", True)
        self.assertTrue(self.manager._users["admin"]["two_factor_enabled"])
        self.manager.enable_two_factor("admin", False)
        self.assertFalse(self.manager._users["admin"]["two_factor_enabled"])

    # ---------- logout ----------

    def test_logout_clears_current_user(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.manager.logout()
        self.assertIsNone(self.manager.get_current_user())

    # ---------- registration ----------

    def test_register_success(self):
        result = self.manager.register("new.user@example.com", _strong_password(), "New User")
        self.assertEqual(result, (True, "ok"))
        user = self.manager._users["new.user"]
        self.assertEqual(user["role"], um.ROLE_VIEWER)
        self.assertEqual(user["email"], "new.user@example.com")
        self.assertEqual(user["display_name"], "New User")

    def test_register_empty_fields(self):
        result = self.manager.register("", "")
        self.assertEqual(result, (False, "err_empty_fields"))

    def test_register_invalid_email(self):
        result = self.manager.register("not-an-email", _strong_password())
        self.assertEqual(result, (False, "err_invalid_email"))

    def test_register_weak_password(self):
        result = self.manager.register("weak@example.com", "weak")
        self.assertEqual(result, (False, "err_password_short"))

    def test_register_duplicate_email(self):
        result = self.manager.register(self.admin_email, _strong_password())
        self.assertEqual(result, (False, "err_email_exists"))

    def test_register_invalid_role_defaults_to_viewer(self):
        result = self.manager.register("r@example.com", _strong_password(), role="superuser")
        self.assertEqual(result, (True, "ok"))
        self.assertEqual(self.manager._users["r"]["role"], um.ROLE_VIEWER)

    def test_register_duplicate_username_gets_suffix(self):
        self.manager.register("john@first.com", _strong_password())
        self.manager.register("john@second.com", _strong_password())
        self.assertIn("john", self.manager._users)
        self.assertIn("john1", self.manager._users)

    def test_register_user_can_login(self):
        self.manager.register("carol@example.com", _strong_password(), role=um.ROLE_MANAGER)
        result = self.manager.login("carol@example.com", _strong_password())
        self.assertEqual(result, (True, "ok", {}))

    # ---------- change password ----------

    def test_change_password_success(self):
        self.manager.login(self.admin_email, self.admin_password)
        result = self.manager.change_password(
            "admin", self.admin_password, "NewStrong@456"
        )
        self.assertEqual(result, (True, "ok"))
        self.assertFalse(self.manager._users["admin"]["must_change_password"])
        login = self.manager.login(self.admin_email, "NewStrong@456")
        self.assertEqual(login, (True, "ok", {}))

    def test_change_password_unknown_user(self):
        result = self.manager.change_password("ghost", "x", "NewStrong@456")
        self.assertEqual(result, (False, "err_user_not_found"))

    def test_change_password_wrong_old_password(self):
        result = self.manager.change_password("admin", "WrongOld@1", "NewStrong@456")
        self.assertEqual(result, (False, "err_wrong_password"))

    def test_change_password_weak_new_password(self):
        result = self.manager.change_password("admin", self.admin_password, "weak")
        self.assertEqual(result, (False, "err_password_short"))

    # ---------- reset password by email ----------

    def test_reset_password_by_email_success(self):
        result = self.manager.reset_password_by_email(
            self.admin_email, "ResetNew@123"
        )
        self.assertEqual(result, (True, "ok"))
        self.assertTrue(self.manager._users["admin"]["must_change_password"])
        login = self.manager.login(self.admin_email, "ResetNew@123")
        self.assertEqual(login, (True, "ok", {}))

    def test_reset_password_by_email_unknown(self):
        result = self.manager.reset_password_by_email("ghost@nowhere.com", "ResetNew@123")
        self.assertEqual(result, (False, "err_email_not_found"))

    def test_reset_password_by_email_weak(self):
        result = self.manager.reset_password_by_email(self.admin_email, "weak")
        self.assertEqual(result, (False, "err_password_short"))

    # ---------- request / confirm password reset ----------

    def test_request_password_reset_success(self):
        result = self.manager.request_password_reset(self.admin_email)
        self.assertTrue(result[0])
        self.assertEqual(result[1]["email"], self.admin_email)
        self.assertTrue(result[1]["token"].isdigit())
        record = self.manager._reset_tokens[self.admin_email]
        self.assertEqual(record["username"], "admin")
        self.assertEqual(record["token"], result[1]["token"])

    def test_request_password_reset_unknown_email(self):
        result = self.manager.request_password_reset("ghost@nowhere.com")
        self.assertEqual(result, (False, "err_email_not_found"))

    def test_request_password_reset_recreates_missing_token_store(self):
        del self.manager._reset_tokens
        result = self.manager.request_password_reset(self.admin_email)
        self.assertTrue(result[0])
        self.assertIn(self.admin_email, self.manager._reset_tokens)

    def test_confirm_password_reset_success(self):
        self.manager.request_password_reset(self.admin_email)
        token = self.manager._reset_tokens[self.admin_email]["token"]
        result = self.manager.confirm_password_reset(
            self.admin_email, token, "Confirm@789"
        )
        self.assertEqual(result, (True, "ok"))
        self.assertFalse(self.manager._users["admin"]["must_change_password"])
        login = self.manager.login(self.admin_email, "Confirm@789")
        self.assertEqual(login, (True, "ok", {}))

    def test_confirm_password_reset_without_request(self):
        result = self.manager.confirm_password_reset(
            self.admin_email, "1234", "Confirm@789"
        )
        self.assertEqual(result, (False, "err_reset_no_request"))

    def test_confirm_password_reset_expired(self):
        self.manager.request_password_reset(self.admin_email)
        self.manager._reset_tokens[self.admin_email]["expires_at"] = time.time() - 100
        result = self.manager.confirm_password_reset(
            self.admin_email, "1234", "Confirm@789"
        )
        self.assertEqual(result, (False, "err_reset_expired"))

    def test_confirm_password_reset_invalid_token(self):
        self.manager.request_password_reset(self.admin_email)
        result = self.manager.confirm_password_reset(
            self.admin_email, "9999", "Confirm@789"
        )
        self.assertEqual(result, (False, "err_reset_invalid_token"))

    def test_confirm_password_reset_weak_password(self):
        self.manager.request_password_reset(self.admin_email)
        token = self.manager._reset_tokens[self.admin_email]["token"]
        result = self.manager.confirm_password_reset(self.admin_email, token, "weak")
        self.assertEqual(result, (False, "err_password_short"))

    def test_confirm_password_reset_none_token_returns_invalid(self):
        self.manager.request_password_reset(self.admin_email)
        result = self.manager.confirm_password_reset(
            self.admin_email, None, "Confirm@789"
        )
        self.assertEqual(result, (False, "err_reset_invalid_token"))

    # ---------- password-change flag ----------

    def test_needs_password_change_default_admin(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.assertTrue(self.manager.needs_password_change())
        self.manager.change_password("admin", self.admin_password, "NewStrong@456")
        self.assertFalse(self.manager.needs_password_change())

    def test_needs_password_change_no_session(self):
        self.assertFalse(self.manager.needs_password_change())

    # ---------- user deletion ----------

    def test_delete_user_success(self):
        self.manager.register("doomed@example.com", _strong_password())
        result = self.manager.delete_user("doomed")
        self.assertEqual(result, (True, "ok"))
        self.assertNotIn("doomed", self.manager._users)

    def test_delete_admin_forbidden(self):
        result = self.manager.delete_user("admin")
        self.assertEqual(result, (False, "err_cannot_delete_admin"))

    def test_delete_unknown_user(self):
        result = self.manager.delete_user("ghost")
        self.assertEqual(result, (False, "err_user_not_found"))

    # ---------- permissions ----------

    def test_has_permission_without_session(self):
        self.assertFalse(self.manager.has_permission("view_dashboard"))

    def test_has_permission_admin_allowed(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.assertTrue(self.manager.has_permission("manage_users"))
        self.assertTrue(self.manager.has_permission("view_dashboard"))

    def test_has_permission_denied_for_unknown_permission(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.assertFalse(self.manager.has_permission("nonexistent_permission"))

    def test_has_permission_viewer_denied(self):
        self.manager.register("peek@example.com", _strong_password(), role=um.ROLE_VIEWER)
        self.manager.login("peek@example.com", _strong_password())
        self.assertFalse(self.manager.has_permission("manage_users"))
        self.assertTrue(self.manager.has_permission("view_dashboard"))

    def test_get_role_permissions_known_role(self):
        perms = self.manager.get_role_permissions(um.ROLE_ADMIN)
        self.assertIn("manage_users", perms)
        self.assertIn("manage_settings", perms)

    def test_get_role_permissions_unknown_role(self):
        self.assertEqual(self.manager.get_role_permissions("nope"), [])

    # ---------- session state ----------

    def test_is_admin(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.assertTrue(self.manager.is_admin())
        self.manager.logout()
        self.assertFalse(self.manager.is_admin())

    def test_is_logged_in_true(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.assertTrue(self.manager.is_logged_in())

    def test_is_logged_in_false_when_no_user(self):
        self.assertFalse(self.manager.is_logged_in())

    def test_is_logged_in_expired_session(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.manager._current_user["login_time"] = time.time() - 5 * 3600
        self.assertFalse(self.manager.is_logged_in())
        self.assertIsNone(self.manager.get_current_user())

    def test_is_logged_in_within_timeout(self):
        self.manager.login(self.admin_email, self.admin_password)
        self.manager._current_user["login_time"] = time.time() - 3 * 3600
        self.assertTrue(self.manager.is_logged_in())

    # ---------- misc ----------

    def test_get_all_users_returns_sanitized_list(self):
        self.manager.register("list@example.com", _strong_password(), "List User")
        users = self.manager.get_all_users()
        admin = next(u for u in users if u["username"] == "admin")
        self.assertNotIn("password", admin)
        self.assertIn("email", admin)
        self.assertIn("role", admin)


if __name__ == "__main__":
    unittest.main()
