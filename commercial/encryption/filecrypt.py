"""Versioned AES-256-GCM file-at-rest encryption.

On-disk format (all parameters embedded, so files decrypt without config):

    MAGIC(5) | KDF_ID(1) | MEMORY_COST(4) | TIME_COST(4) | PARALLELISM(1)
    | SALT_LEN(1) | NONCE_LEN(1) | SALT | NONCE | CIPHERTEXT || TAG(16)

The GCM tag authenticates the full header (used as AAD) + ciphertext, so any
tampering with the blob — including the KDF parameters — fails decryption.
"""

from __future__ import annotations

import os
import struct
import tempfile
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .kdf import derive_argon2id_key

MAGIC = b"SACF1"
KDF_ARGON2ID = 1
_VERSION = 1

_HEADER = struct.Struct(">5sBIIBBB")  # magic, kdf, memory_cost, time_cost, par, salt_len, nonce_len
SALT_LEN = 16
NONCE_LEN = 12


class EncryptionError(Exception):
    """Raised for any encryption/decryption failure (bad passphrase, tampering, I/O)."""


def is_encrypted_blob(raw: bytes) -> bool:
    """True when ``raw`` starts with the versioned encryption magic."""
    return len(raw) >= len(MAGIC) and raw[: len(MAGIC)] == MAGIC


def _build_blob(
    data: bytes, passphrase: str, memory_cost: int, time_cost: int, parallelism: int
) -> bytes:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    header = _HEADER.pack(
        MAGIC, KDF_ARGON2ID, memory_cost, time_cost, parallelism, SALT_LEN, NONCE_LEN
    )
    aad = header + salt + nonce
    key = derive_argon2id_key(
        passphrase, salt, memory_cost=memory_cost, time_cost=time_cost, parallelism=parallelism
    )
    ciphertext = AESGCM(key).encrypt(nonce, data, aad)
    return aad + ciphertext


def _parse_blob(blob: bytes) -> Tuple[bytes, str, dict]:
    if len(blob) < _HEADER.size + SALT_LEN + NONCE_LEN:
        raise EncryptionError("encrypted blob is too short")
    (magic, kdf_id, memory_cost, time_cost, parallelism, salt_len, nonce_len) = _HEADER.unpack(
        blob[:_HEADER.size]
    )
    if magic != MAGIC:
        raise EncryptionError("unknown encryption format")
    if kdf_id != KDF_ARGON2ID:
        raise EncryptionError(f"unsupported KDF id {kdf_id}")
    if salt_len != SALT_LEN or nonce_len != NONCE_LEN:
        raise EncryptionError("invalid blob header lengths")
    header_end = _HEADER.size + salt_len + nonce_len
    if len(blob) <= header_end:
        raise EncryptionError("encrypted blob is truncated")
    salt = blob[_HEADER.size : _HEADER.size + salt_len]
    nonce = blob[header_end - nonce_len : header_end]
    params = {
        "salt": salt,
        "memory_cost": memory_cost,
        "time_cost": time_cost,
        "parallelism": parallelism,
    }
    return blob[:header_end], nonce, params


def encrypt_bytes(
    data: bytes,
    passphrase: str,
    *,
    memory_cost: int = 65536,
    time_cost: int = 3,
    parallelism: int = 1,
) -> bytes:
    """Encrypt ``data`` into a self-describing encrypted blob."""
    return _build_blob(data, passphrase, memory_cost, time_cost, parallelism)


def decrypt_bytes(blob: bytes, passphrase: str) -> bytes:
    """Decrypt a blob produced by :func:`encrypt_bytes`.

    Raises :class:`EncryptionError` on wrong passphrase, tampering or
    malformed input.
    """
    aad, nonce, params = _parse_blob(blob)
    try:
        key = derive_argon2id_key(passphrase, **params)
        return AESGCM(key).decrypt(nonce, blob[len(aad):], aad)
    except Exception as exc:  # InvalidTag, ValueError from bad lengths
        raise EncryptionError("decryption failed: wrong passphrase or tampered data") from exc


def encrypt_file(src: str, dst: str, passphrase: str, **params) -> None:
    """Encrypt the file at ``src`` into ``dst`` (atomic write)."""
    try:
        with open(src, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        raise EncryptionError(f"cannot read {src}: {exc}") from exc
    blob = encrypt_bytes(data, passphrase, **params)
    _atomic_write(dst, blob)


def decrypt_file(src: str, dst: str, passphrase: str) -> None:
    """Decrypt the file at ``src`` into ``dst`` (atomic write, no partial file)."""
    try:
        with open(src, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        raise EncryptionError(f"cannot read {src}: {exc}") from exc
    data = decrypt_bytes(blob, passphrase)
    _atomic_write(dst, data)


def _atomic_write(path: str, data: bytes) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_path, path)
    except OSError as exc:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise EncryptionError(f"cannot write {path}: {exc}") from exc
