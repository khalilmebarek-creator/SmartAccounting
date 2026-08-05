# commercial/encryption — Module 2: Data-at-Rest Encryption

AES-256-GCM + **Argon2id** (via `cryptography >= 41` — zero new dependencies).

## Files

| File | Role |
|---|---|
| `kdf.py` | `derive_argon2id_key()` — OWASP-recommended defaults (64 MiB, 3 iterations, 1 lane) |
| `filecrypt.py` | self-describing versioned blob format + `encrypt_bytes/decrypt_bytes/encrypt_file/decrypt_file` |

## Blob format

```
MAGIC(5 "SACF1") | KDF_ID(1) | MEMORY_COST(4) | TIME_COST(4) | PARALLELISM(1)
| SALT_LEN(1) | NONCE_LEN(1) | SALT(16) | NONCE(12) | CIPHERTEXT || TAG(16)
```

The GCM tag authenticates the header (AAD) + ciphertext, so tampering with
any byte — including KDF parameters — fails decryption. A wrong passphrase
and a tampered file raise the same `EncryptionError` (no oracle).

## Adoption: cloud sync payloads

`modules/cloud_sync.py` `encrypt_payload/decrypt_payload` now produce Argon2id
blobs (random per-file salt). Legacy PBKDF2 snapshots still decrypt through an
automatic fallback — old backups keep working, new ones get modern KDF.

## Usage

```python
from commercial.encryption import encrypt_bytes, decrypt_bytes, encrypt_file

blob = encrypt_bytes(data, "my passphrase")
data = decrypt_bytes(blob, "my passphrase")   # EncryptionError on wrong/tampered
encrypt_file("data.json", "data.json.enc", "pw")
decrypt_file("data.json.enc", "data.json.dec", "pw")
```

## Notes

- `license.dat` stays plaintext on purpose: it is self-verifying (RSA).
- `accounting_data.json` adoption is deferred on purpose: encrypting it would
  break import/export, backups and cloud sync flows (documented in summary).
- Tests: `tests/test_encryption.py` (30 tests, incl. tamper/wrong-pass/legacy).
