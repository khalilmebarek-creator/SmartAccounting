# CHANGELOG — commercial/licensing

## v1.0.0 (2026-08-05)

- RSA-2048 license keys, format: grouped base64 `payload---signature` (5-char groups, whitespace-tolerant paste).
- Offline activation via challenge-response; `LicenseStore` (atomic `license.dat` write).
- Machine fingerprint: MAC + CPU + disk serial, SHA-256, defensive fallbacks.
- Tiers FREE/PRO/ENTERPRISE + `feature_enabled()` gates (cloud_sync/multi_device/ai_unlimited/api_access/audit_trail).
- Expiry + 14-day grace + read-only mode; startup nudge only when past grace (non-blocking).
- Vendor CLI `keygen` (key pair generation, issuing, 5 sample keys).
- License dialog wired to Help menu (menu_license) — logic in pure, tested functions.
- i18n: +21 keys x 3 languages (1986 -> 2007).
- Tests: 67 in `tests/test_licensing.py`, coverage 99%.
