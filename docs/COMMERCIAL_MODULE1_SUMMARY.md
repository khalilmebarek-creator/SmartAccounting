# v4.0 Commercial Build — Module 1 Summary (Licensing & Activation)

> **Status: DONE** — tested, 5 sample keys issued. Date: 2026-08-05.

## Decisions

1. **Offline challenge-response activation** (per prompt): app shows hardware id → vendor signs a key offline → user pastes → verified locally. No server needed for the DZ market.
2. **Key format**: `payload---signature`, base64 grouped in 5-char chunks. The prompt's `XXXX-XXXX-XXXX-XXXX-XXXX` cannot physically hold an RSA-2048 signature (256 bytes) — documented in the README; the grouped style preserves copy-paste safety.
3. **RSA PKCS#1 v1.5 SHA-256** over canonical JSON payload (tier, licensee, expiry, hwid, issued, uid) — tier is inside the signature, so it cannot be elevated locally.
4. **Hardware binding** = MAC + CPU + disk serial → SHA-256, with defensive fallbacks so the fingerprint stays stable.
5. **Grace model**: 14 days after expiry, then read-only. The startup nudge appears **only** when past grace — unlicensed users are FREE tier with zero nagging (no regression).
6. **UI**: dialog under Help menu (`menu_license`), logic extracted into pure functions (`describe_license`, `try_activate`) because QDialog construction hangs under pytest on this Windows/Python 3.13 environment (verified with minimal probes — QWidget works, QDialog doesn't).
7. **Vendor tooling**: `python -m commercial.licensing.keygen`; private key in `commercial/keys/` (gitignored); 5 sample keys bound to a **fake** hardware id (safe deliverable).
8. **Tier gates** exist as an API (`feature_enabled`) but **no existing v3.1.8 feature is locked** in this module — enforcement comes with later modules.

## Gotchas

- urlsafe-base64 emits `-` characters that collide with the group separator → switched to standard base64.
- `QApplication([])` hangs under pytest on this machine; must use `QApplication(sys.argv)` (and even then QDialog itself hangs → pragma + pure-function testing).
- PowerShell disk-serial probe adds ~0.5-1s on first call → `lru_cache` on `fingerprint()`.
- RSA signatures make keys ~690 chars; whitespace-tolerant decode handles email/WhatsApp line wraps.

## Next steps

- **Module 2 (Encryption)**: AES-256-GCM + Argon2id over user data files; `license.dat` stays plaintext (it is self-verifying).
- Enforcement hooks: gate cloud sync / AI quota behind `feature_enabled()`.
- PyInstaller migration (per owner decision) — bundling `commercial/` + `--hidden-import` for the lazy dialog import.
