"""Argon2id key derivation for data-at-rest encryption.

Uses ``cryptography``'s built-in Argon2id (available since cryptography 41)
so no extra dependency is required. Default parameters follow OWASP
recommendations for interactive logins (64 MiB, 3 iterations, 1 lane).

API note: on this environment ``Argon2id(salt, length, iterations, lanes,
memory_cost)`` is the supported constructor signature (PHC-style).
"""

from __future__ import annotations

from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

KEY_LENGTH = 32  # AES-256

# OWASP-recommended interactive parameters (memory_cost is in KiB).
DEFAULT_MEMORY_COST = 65536  # 64 MiB
DEFAULT_TIME_COST = 3
DEFAULT_PARALLELISM = 1


def derive_argon2id_key(
    passphrase: str,
    salt: bytes,
    *,
    memory_cost: int = DEFAULT_MEMORY_COST,
    time_cost: int = DEFAULT_TIME_COST,
    parallelism: int = DEFAULT_PARALLELISM,
) -> bytes:
    """Derive a 32-byte AES key from a passphrase using Argon2id.

    ``salt`` must be unique per encrypted blob (16 bytes recommended);
    the derivation is deterministic for identical inputs.
    """
    kdf = Argon2id(
        salt=salt,
        length=KEY_LENGTH,
        iterations=time_cost,
        lanes=parallelism,
        memory_cost=memory_cost,
    )
    return kdf.derive((passphrase or "").encode("utf-8"))
