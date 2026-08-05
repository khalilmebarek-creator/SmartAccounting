"""Module 2: data-at-rest encryption (AES-256-GCM + Argon2id).

Pure library with zero new dependencies (``cryptography >= 41`` provides
Argon2id). The cloud-sync payload encryption is upgraded to use it while
remaining fully backward-compatible with legacy PBKDF2 snapshots.
"""

from .filecrypt import (
    MAGIC,
    EncryptionError,
    decrypt_bytes,
    decrypt_file,
    encrypt_bytes,
    encrypt_file,
    is_encrypted_blob,
)

__all__ = [
    "MAGIC",
    "EncryptionError",
    "encrypt_bytes",
    "decrypt_bytes",
    "encrypt_file",
    "decrypt_file",
    "is_encrypted_blob",
]
