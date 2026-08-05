# CHANGELOG — commercial/encryption

## v1.0.0 (2026-08-05)

- Argon2id key derivation (cryptography built-in, no new dependency; 64 MiB / 3 iterations / 1 lane defaults).
- Versioned AES-256-GCM blob format (magic + params + salt + nonce in AAD) for bytes and files.
- Atomic file writes; `EncryptionError` for wrong passphrase, tampering, malformed input, I/O.
- Cloud sync snapshots upgraded to Argon2id with automatic legacy PBKDF2 fallback (old backups keep working).
- Tests: 30 in `tests/test_encryption.py`.
