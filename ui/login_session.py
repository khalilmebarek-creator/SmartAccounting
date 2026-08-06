"""Login session persistence - remembers last email + optional saved credentials.

The "remember me" password is NEVER stored in plaintext: it is encrypted
with AES-256-GCM (commercial/encryption) using a key derived from the
machine hardware fingerprint, so a saved session only works on the device
where it was created.
"""

import hashlib
import json
import os

from commercial.encryption.filecrypt import encrypt_bytes, decrypt_bytes, EncryptionError
from commercial.licensing.hardware_id import fingerprint as _device_fingerprint

SESSION_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "login_session.json"
)

_SAVE_MEMORY_COST = 16384
_SAVE_TIME_COST = 1


def _device_key() -> str:
    """Device-bound passphrase: SHA-256 of the hardware fingerprint."""
    return hashlib.sha256(_device_fingerprint().encode("utf-8")).hexdigest()


def _device_fingerprint_hash() -> str:
    return hashlib.sha256(_device_fingerprint().encode("utf-8")).hexdigest()


def save_login_email(email: str):
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_email": email}, f)
    except Exception:
        pass


def save_login_session(email: str, password: str, remember: bool):
    """Persist the session.

    When ``remember`` is True the password is stored encrypted, bound to
    this machine. Otherwise only the email is kept (legacy behaviour).
    """
    try:
        if not remember:
            save_login_email(email)
            return
        import base64
        blob = encrypt_bytes(
            password.encode("utf-8"), _device_key(),
            memory_cost=_SAVE_MEMORY_COST, time_cost=_SAVE_TIME_COST,
        )
        payload = {
            "last_email": email,
            "fingerprint_hash": _device_fingerprint_hash(),
            "saved_password": base64.b64encode(blob).decode("ascii"),
        }
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        save_login_email(email)


def load_login_session() -> tuple:
    """Return ``(email, password)`` from a saved session.

    The password is empty when no remember-me session exists, when the
    file belongs to another device, or when decryption fails.
    """
    try:
        import base64
        if not os.path.exists(SESSION_FILE):
            return "", ""
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        email = data.get("last_email", "")
        blob_b64 = data.get("saved_password", "")
        if not blob_b64:
            return email, ""
        if data.get("fingerprint_hash", "") != _device_fingerprint_hash():
            return email, ""
        password = decrypt_bytes(base64.b64decode(blob_b64), _device_key()).decode("utf-8")
        return email, password
    except Exception:
        return "", ""


def clear_saved_password():
    """Drop the saved password but keep the remembered email."""
    try:
        email = ""
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            email = data.get("last_email", "")
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_email": email}, f)
    except Exception:
        pass


def load_login_email() -> str:
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("last_email", "")
    except Exception:
        pass
    return ""


def clear_login_email():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception:
        pass
