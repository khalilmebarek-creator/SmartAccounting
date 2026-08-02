"""User authentication, role management, and permissions."""

import hashlib
import hmac
import os
import re
import json
import time
import random
import string
from datetime import datetime, timedelta

from utils.app_logger import get_logger
import config

logger = get_logger("user_manager")

USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "users.json"
)

ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_ACCOUNTANT = "accountant"
ROLE_VIEWER = "viewer"

ALL_ROLES = [ROLE_ADMIN, ROLE_MANAGER, ROLE_ACCOUNTANT, ROLE_VIEWER]

PERMISSIONS = {
    ROLE_ADMIN: [
        "manage_users", "manage_settings", "view_dashboard", "enter_data",
        "run_analysis", "view_reports", "export_reports", "manage_backup",
        "view_audit_log", "manage_tax", "view_chat", "manage_templates",
        "view_forecast", "view_budget", "view_cost_center", "view_breakeven",
    ],
    ROLE_MANAGER: [
        "view_dashboard", "enter_data", "run_analysis", "view_reports",
        "export_reports", "view_audit_log", "manage_tax", "view_chat",
        "view_forecast", "view_budget", "view_cost_center", "view_breakeven",
    ],
    ROLE_ACCOUNTANT: [
        "view_dashboard", "enter_data", "run_analysis", "view_reports",
        "export_reports", "manage_tax", "view_chat",
    ],
    ROLE_VIEWER: [
        "view_dashboard", "view_reports", "view_chat",
    ],
}

SESSION_TIMEOUT_HOURS = 4
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
MIN_PASSWORD_LENGTH = 8

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + dk.hex()


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except (ValueError, AttributeError):
        return False


def _is_legacy_hash(stored: str) -> bool:
    return len(stored) == 64 and ":" not in stored


def validate_password_strength(password: str) -> tuple:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, "err_password_short"
    if not re.search(r"[A-Z]", password):
        return False, "err_password_no_upper"
    if not re.search(r"[a-z]", password):
        return False, "err_password_no_lower"
    if not re.search(r"\d", password):
        return False, "err_password_no_digit"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]", password):
        return False, "err_password_no_special"
    return True, ""


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))


def generate_otp(length=6) -> str:
    return "".join(random.choices(string.digits, k=length))


class UserManager:
    def __init__(self):
        self._users = {}
        self._current_user = None
        self._failed_attempts = {}
        self._lockout_until = {}
        self._otp_store = {}
        self._reset_tokens = {}
        self._load()

    def _load(self):
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "_users" in data:
                    self._users = data["_users"]
                    self._reset_tokens = data.get("_reset_tokens", {})
                else:
                    self._users = data
            except Exception as e:
                logger.error(f"Failed to load users: {e}")
                self._users = {}
        if not self._users:
            self._users = {
                "admin": {
                    "password": _hash_password(config.DEFAULT_ADMIN_PASSWORD),
                    "role": ROLE_ADMIN,
                    "created": datetime.now().isoformat(),
                    "display_name": "Admin",
                    "email": "admin@accounting.local",
                    "must_change_password": True,
                    "two_factor_enabled": False,
                }
            }
            self._save()
            logger.info("Default admin created with forced password change")

    def _save(self):
        try:
            data = {
                "_users": self._users,
                "_reset_tokens": self._reset_tokens,
            }
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")

    def _find_by_email(self, email: str):
        email = email.strip().lower()
        for uname, udata in self._users.items():
            if udata.get("email", "").lower() == email:
                return uname, udata
        return None, None

    def _migrate_legacy_password(self, username: str, password: str) -> bool:
        if username in self._users and _is_legacy_hash(self._users[username]["password"]):
            old_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
            if self._users[username]["password"] == old_hash:
                self._users[username]["password"] = _hash_password(password)
                self._save()
                logger.info(f"Migrated legacy password for user: {username}")
                return True
        return False

    def login(self, email: str, password: str) -> tuple:
        email = email.strip().lower()
        username, udata = self._find_by_email(email)

        if username is None:
            return False, "err_email_not_found", {}

        if username in self._lockout_until:
            if datetime.now() < self._lockout_until[username]:
                remaining = (self._lockout_until[username] - datetime.now()).seconds // 60 + 1
                return False, "err_locked", {"minutes": remaining}
            else:
                self._lockout_until.pop(username, None)
                self._failed_attempts.pop(username, None)

        if not _verify_password(password, udata["password"]):
            if self._migrate_legacy_password(username, password):
                pass
            else:
                self._failed_attempts[username] = self._failed_attempts.get(username, 0) + 1
                if self._failed_attempts[username] >= MAX_FAILED_ATTEMPTS:
                    self._lockout_until[username] = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
                    logger.warning(f"Account locked: {username} after {MAX_FAILED_ATTEMPTS} failures")
                    return False, "err_locked", {"minutes": LOCKOUT_MINUTES}
                remaining = MAX_FAILED_ATTEMPTS - self._failed_attempts[username]
                return False, "err_wrong_password", {"attempts": remaining}

        self._failed_attempts.pop(username, None)
        self._lockout_until.pop(username, None)

        if udata.get("two_factor_enabled", False):
            otp = generate_otp()
            self._otp_store[username] = {
                "otp": otp,
                "expires": (datetime.now() + timedelta(minutes=5)).isoformat(),
                "user_data": {
                    "username": username,
                    "role": udata["role"],
                    "display_name": udata.get("display_name", username),
                    "email": udata.get("email", ""),
                    "login_time": time.time(),
                    "must_change_password": udata.get("must_change_password", False),
                }
            }
            logger.info(f"2FA OTP generated for: {username}")
            return False, "otp_required", {"email": udata.get("email", "")}

        self._current_user = {
            "username": username,
            "role": udata["role"],
            "display_name": udata.get("display_name", username),
            "email": udata.get("email", ""),
            "login_time": time.time(),
            "must_change_password": udata.get("must_change_password", False),
        }
        logger.info(f"User logged in: {username}")
        return True, "ok", {}

    def verify_otp(self, username: str, otp_code: str) -> tuple:
        username = username.strip().lower()
        if username not in self._otp_store:
            return False, "err_otp_expired"

        store = self._otp_store[username]
        if datetime.now() > datetime.fromisoformat(store["expires"]):
            del self._otp_store[username]
            return False, "err_otp_expired"

        if store["otp"] != otp_code:
            return False, "err_otp_wrong"

        self._current_user = store["user_data"]
        del self._otp_store[username]
        logger.info(f"2FA verified for: {username}")
        return True, "ok", {}

    def generate_and_send_otp(self, email: str) -> tuple:
        email = email.strip().lower()
        username, udata = self._find_by_email(email)
        if username is None:
            return False, "err_email_not_found"
        otp = generate_otp()
        self._otp_store[username] = {
            "otp": otp,
            "expires": (datetime.now() + timedelta(minutes=5)).isoformat(),
        }
        logger.info(f"OTP for {email}: {otp}")
        return True, otp

    def enable_two_factor(self, username: str, enabled: bool = True):
        username = username.strip().lower()
        if username in self._users:
            self._users[username]["two_factor_enabled"] = enabled
            self._save()

    def logout(self):
        user = self._current_user
        if user:
            logger.info(f"User logged out: {user['username']}")
        self._current_user = None

    def register(self, email: str, password: str, display_name: str = "", role: str = ROLE_VIEWER) -> tuple:
        email = email.strip().lower()
        if not email or not password:
            return False, "err_empty_fields"
        if not validate_email(email):
            return False, "err_invalid_email"
        ok, err = validate_password_strength(password)
        if not ok:
            return False, err
        _, existing = self._find_by_email(email)
        if existing:
            return False, "err_email_exists"
        if role not in ALL_ROLES:
            role = ROLE_VIEWER
        username = email.split("@")[0]
        base = username
        counter = 1
        while username in self._users:
            username = f"{base}{counter}"
            counter += 1
        self._users[username] = {
            "password": _hash_password(password),
            "role": role,
            "created": datetime.now().isoformat(),
            "display_name": display_name or base,
            "email": email,
            "two_factor_enabled": False,
        }
        self._save()
        logger.info(f"Registered new user: {username} ({email}) role={role}")
        return True, "ok"

    def change_password(self, username: str, old_password: str, new_password: str) -> tuple:
        username = username.strip().lower()
        if username not in self._users:
            return False, "err_user_not_found"
        if not _verify_password(old_password, self._users[username]["password"]):
            return False, "err_wrong_password"
        ok, err = validate_password_strength(new_password)
        if not ok:
            return False, err
        self._users[username]["password"] = _hash_password(new_password)
        self._users[username]["must_change_password"] = False
        self._save()
        if self._current_user and self._current_user["username"] == username:
            self._current_user["must_change_password"] = False
        logger.info(f"Password changed for: {username}")
        return True, "ok"

    def reset_password_by_email(self, email: str, new_password: str) -> tuple:
        email = email.strip().lower()
        username, udata = self._find_by_email(email)
        if username is None:
            return False, "err_email_not_found"
        ok, err = validate_password_strength(new_password)
        if not ok:
            return False, err
        self._users[username]["password"] = _hash_password(new_password)
        self._users[username]["must_change_password"] = True
        self._save()
        logger.info(f"Password reset for: {username} via email")
        return True, "ok"

    def request_password_reset(self, email: str) -> tuple:
        import secrets, time
        email = email.strip().lower()
        username, _ = self._find_by_email(email)
        if username is None:
            return False, "err_email_not_found"
        token = f"{secrets.randbelow(9000) + 1000}"
        if not hasattr(self, '_reset_tokens'):
            self._reset_tokens = {}
        self._reset_tokens[email] = {
            "token": token,
            "expires_at": time.time() + 1800,
            "username": username,
        }
        self._save()
        logger.info(f"Password reset requested for: {email}")
        return True, {"token": token, "email": email}

    def confirm_password_reset(self, email: str, token: str, new_password: str) -> tuple:
        import time
        email = email.strip().lower()
        if not hasattr(self, '_reset_tokens') or email not in self._reset_tokens:
            return False, "err_reset_no_request"
        record = self._reset_tokens[email]
        if time.time() > record["expires_at"]:
            del self._reset_tokens[email]
            self._save()
            return False, "err_reset_expired"
        if token is None or record["token"] != token.strip():
            return False, "err_reset_invalid_token"
        ok, err = validate_password_strength(new_password)
        if not ok:
            return False, err
        username = record["username"]
        self._users[username]["password"] = _hash_password(new_password)
        self._users[username]["must_change_password"] = False
        del self._reset_tokens[email]
        self._save()
        logger.info(f"Password reset confirmed for: {username}")
        return True, "ok"

    def needs_password_change(self) -> bool:
        return self._current_user and self._current_user.get("must_change_password", False)

    def delete_user(self, username: str) -> tuple:
        username = username.strip().lower()
        if username == "admin":
            return False, "err_cannot_delete_admin"
        if username not in self._users:
            return False, "err_user_not_found"
        del self._users[username]
        self._save()
        return True, "ok"

    def get_current_user(self):
        return self._current_user

    def is_admin(self) -> bool:
        return self._current_user and self._current_user["role"] == ROLE_ADMIN

    def has_permission(self, permission: str) -> bool:
        if not self._current_user:
            return False
        role = self._current_user.get("role", ROLE_VIEWER)
        return permission in PERMISSIONS.get(role, [])

    def get_role_permissions(self, role: str) -> list:
        return PERMISSIONS.get(role, [])

    def is_logged_in(self) -> bool:
        if self._current_user is None:
            return False
        login_time = self._current_user.get("login_time", 0)
        if time.time() - login_time > SESSION_TIMEOUT_HOURS * 3600:
            logger.info(f"Session expired for: {self._current_user['username']}")
            self._current_user = None
            return False
        return True

    def get_all_users(self) -> list:
        return [
            {"username": k, "role": v["role"], "display_name": v.get("display_name", k),
             "email": v.get("email", ""), "two_factor_enabled": v.get("two_factor_enabled", False)}
            for k, v in self._users.items()
        ]


user_manager = UserManager()
