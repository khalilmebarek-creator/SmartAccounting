"""vault — تشفير البيانات الحساسة على القرص باستخدام AES-GCM."""

import base64
import hashlib
import os
import platform
import logging

log = logging.getLogger("vault")

_SALT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".vault_salt"
)


def _get_machine_key() -> bytes:
    """مفتاح مشتق من معلومات الجهاز."""
    raw = f"{platform.node()}|{platform.machine()}|{platform.processor()}".encode()
    return hashlib.sha256(raw).digest()


def _get_or_create_salt() -> bytes:
    """ملف ملح عشوائي يُنشأ مرة واحدة فقط."""
    if os.path.exists(_SALT_FILE):
        with open(_SALT_FILE, "rb") as f:
            return f.read()
    salt = os.urandom(16)
    try:
        with open(_SALT_FILE, "wb") as f:
            f.write(salt)
        os.chmod(_SALT_FILE, 0o600)
    except Exception as e:
        log.warning("Could not create salt file: %s", e)
    return salt


def _derive_fernet_key() -> bytes:
    """Derive a Fernet-compatible key (URL-safe base64, 32 bytes) from machine + salt."""
    salt = _get_or_create_salt()
    machine = _get_machine_key()
    dk = hashlib.pbkdf2_hmac("sha256", machine, salt, 100000, dklen=32)
    return base64.urlsafe_b64encode(dk)


def encrypt(plaintext: str) -> str:
    """تشفير نص → سلسلة Fernet آمنة للتخزين."""
    if not plaintext:
        return ""
    try:
        from cryptography.fernet import Fernet
        key = _derive_fernet_key()
        f = Fernet(key)
        encrypted = f.encrypt(plaintext.encode("utf-8"))
        return "ENC:" + encrypted.decode("ascii")
    except Exception as e:
        log.error("Encryption failed: %s", e)
        raise


def decrypt(ciphertext: str) -> str:
    """فك تشفير سلسلة Fernet → نص أصلي."""
    if not ciphertext:
        return ""
    if not ciphertext.startswith("ENC:"):
        return ciphertext
    try:
        from cryptography.fernet import Fernet
        key = _derive_fernet_key()
        f = Fernet(key)
        return f.decrypt(ciphertext[4:].encode("ascii")).decode("utf-8")
    except Exception as e:
        log.error("Decryption failed: %s", e)
        raise


def is_encrypted(value: str) -> bool:
    return isinstance(value, str) and value.startswith("ENC:")
