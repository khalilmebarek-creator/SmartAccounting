# v4.0 Commercial Build — Modules 2 & 3 Summary

> **Status: DONE** — 47 new tests, full suite green. Date: 2026-08-05.

## Module 2 — Encryption (data at rest)

- **KDF**: Argon2id via `cryptography` built-in (v49 present) — **zero new
  dependencies**, OWASP defaults (64 MiB / 3 iterations / 1 lane).
- **Format**: self-describing versioned blob `SACF1 | params | salt | nonce | ct||tag`,
  tag authenticates the full header (AAD) → tampering with any byte (even KDF
  params) fails; wrong passphrase and tampering raise the same `EncryptionError`.
- **Adoption — cloud sync snapshots**: `encrypt_payload` now emits Argon2id
  blobs with random per-file salt; `decrypt_payload` auto-detects the format and
  falls back to the legacy PBKDF2 path, so **old backups keep working**
  (verified with a crafted legacy snapshot test).
- **Deferred on purpose** (documented): encrypting `accounting_data.json` would
  break import/export, backup and cloud-sync flows; adoption happens in the
  module that owns those flows. `license.dat` stays plaintext (self-verifying).

## Module 3 — Live tier enforcement

- **`commercial/entitlement.py`**: `current_tier()` (license file → tier, FREE
  when absent/corrupt), `required_tier()`, `feature_allowed()` — the Module-1
  gates now driven by the **activated license**, plus `set_store()/reset()` for
  tests and app wiring.
- **Gates actually enforced** (previously: API only):
  - `cloud_sync` (**PRO**): push/pull actions in CloudSyncView. Local backup,
    destinations, history and passphrase stay FREE (local safety ≠ cloud sync).
  - `ai_unlimited` (**ENTERPRISE**): 6-month forecast removed from the AI
    insights view + PDF/Excel exports blocked; FREE keeps 3-month analysis.
  - Denied action → translated dialog with feature name + required tier +
    hint to Help → License (via `ui.widgets.messages.show_feature_denied`).
- **No surfaces yet** (documented, gates ready): `multi_device`, `api_access`,
  `audit_trail` — the app has no multi-device/API-server/dedicated audit-log
  screen today.
- Unknown features stay enabled (FREE users never lose future features).

## Quality

- **47 new tests** (30 encryption + 17 entitlement incl. view-gate tests with a
  real PRO/ENTERPRISE license) → **1991 total, all green**.
- Coverage: `commercial/` **99%** (2 pre-existing trivial lines), `modules/`
  **100%** (cloud_sync integration covered incl. legacy fallback).
- i18n: **2011 keys × 3** languages (equal sets).
- Gotchas recorded: pytest crashes on QWidget construction without
  `QApplication(sys.argv)` (lesson from Module 1 applied again);
  `QMessageBox.warning` in offscreen tests blocks ~116s — always mock it.

## Next steps

- Module 4: payment integrations (Stripe/CIB/eDahabia) — needs official accounts.
- PyInstaller migration — bundle `commercial/` (plus `--hidden-import` for
  lazy imports); frozen build currently excludes `commercial/` until then.
