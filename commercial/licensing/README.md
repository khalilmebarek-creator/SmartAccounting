# commercial/licensing — Module 1: Licensing & Activation

RSA-2048 signed license keys with **offline activation** (no phone-home),
built for the Algerian market where internet is unreliable.

## Architecture

| File | Role |
|---|---|
| `tier.py` | `Tier` enum (FREE/PRO/ENTERPRISE) + `feature_enabled()` gates |
| `hardware_id.py` | machine fingerprint: MAC + CPU + disk serial -> SHA-256 |
| `expiry.py` | expiry checks, 14-day grace, then read-only mode |
| `license.py` | RSA-2048 key pair, canonical payload, encode/decode/verify keys |
| `activation.py` | `LicenseStore` — challenge, save, load, read-only check |
| `keygen.py` | **vendor-only CLI** (never shipped): key pair + license issuing |
| `license_dialog.py` | UI: paste key -> activate -> restart (logic in pure functions) |
| `pub_key.pem` | embedded client public key (safe to commit) |
| `errors.py` | exception hierarchy (`LicenseError` root) |

## Activation flow (offline)

1. App shows its hardware id (Help -> License).
2. Customer sends that id to the vendor (email/WhatsApp).
3. Vendor runs the offline keygen for that id + tier + duration.
4. Customer pastes the key -> verified locally (signature + hardware binding) -> saved to `license.dat` -> restart.

## Vendor keygen

```bash
python -m commercial.licensing.keygen --new-keypair   # once; private key stays offline
python -m commercial.licensing.keygen --hwid <hex> --tier pro --days 365 --licensee "Acme SARL"
python -m commercial.licensing.keygen --sample        # 5 demo keys for a test machine
```

- Private key: `commercial/keys/private_key.pem` — **gitignored, never commit.**
- Demo keys: `commercial/keys/sample_keys.txt` (bound to a fake hardware id).

## Security notes

- Key payload is canonical JSON signed with RSA PKCS#1 v1.5 SHA-256; tampering fails verification.
- Keys are hardware-bound: pasting a key for another machine is rejected locally.
- The human format in the master prompt (`XXXX-XXXX-XXXX-XXXX-XXXX`) cannot carry a
  256-byte RSA signature; real keys are longer, grouped by 5 chars (`---` separates payload/signature).
- Tier is inside the signed payload — cannot be elevated by editing files.

## Tests

`python -m pytest tests/test_licensing.py -q` — 67 tests, **99% coverage** on this package:

```bash
python -m coverage run --source=commercial.licensing -m pytest tests/test_licensing.py -q
python -m coverage report --fail-under=95
```
