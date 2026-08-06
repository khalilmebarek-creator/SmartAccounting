"""Module 1 — Licensing & Activation tests.

Covers: tiers + feature gates, hardware fingerprint, RSA key generation,
license key encode/decode/verify, expiry + grace + read-only, offline
activation store, embedded public key, and the 5 sample vendor keys.
"""

from __future__ import annotations

import base64
import datetime
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commercial.licensing.activation import LicenseStore  # noqa: E402
from commercial.licensing.errors import (  # noqa: E402
    LicenseFileError,
    LicenseHardwareMismatchError,
    LicenseInvalidError,
    LicenseSignatureError,
)
from commercial.licensing.expiry import (  # noqa: E402
    GRACE_DAYS,
    days_remaining,
    expiry_from_today,
    in_grace,
    is_expired,
    is_read_only,
    parse_expiry,
)
from commercial.licensing.hardware_id import (  # noqa: E402
    fingerprint,
    fingerprint_from_components,
)
from commercial.licensing.license import (  # noqa: E402
    decode_key,
    embedded_public_key,
    encode_key,
    generate_keypair,
    load_private_key,
    load_public_key,
    new_license_payload,
    payload_serialize,
    sign_payload,
    verify_signature,
)
from commercial.licensing.tier import FEATURES, Tier, feature_enabled  # noqa: E402

TEST_HWID = "ab" * 32
OTHER_HWID = "cd" * 32


@pytest.fixture(scope="module")
def keypair():
    private_pem, public_pem = generate_keypair()
    return load_private_key(private_pem), load_public_key(public_pem), public_pem


@pytest.fixture()
def payload(keypair):
    return new_license_payload(Tier.PRO, TEST_HWID, "Acme SARL", expiry_from_today(365))


# ---------------------------------------------------------------- tiers
class TestTier:
    def test_parse_valid(self):
        assert Tier.parse("pro") == Tier.PRO
        assert Tier.parse("ENTERPRISE") == Tier.ENTERPRISE
        assert Tier.parse("free") == Tier.FREE

    def test_parse_invalid_defaults_free(self):
        assert Tier.parse("ultra") == Tier.FREE
        assert Tier.parse("") == Tier.FREE

    def test_rank_order(self):
        assert Tier.FREE.rank < Tier.PRO.rank < Tier.ENTERPRISE.rank

    def test_at_least(self):
        assert Tier.ENTERPRISE.at_least(Tier.PRO)
        assert Tier.PRO.at_least(Tier.PRO)
        assert not Tier.FREE.at_least(Tier.PRO)

    def test_feature_enabled_gates(self):
        assert feature_enabled("cloud_sync", Tier.PRO)
        assert not feature_enabled("cloud_sync", Tier.FREE)
        assert feature_enabled("api_access", Tier.ENTERPRISE)
        assert not feature_enabled("api_access", Tier.PRO)

    def test_unknown_feature_defaults_enabled(self):
        assert feature_enabled("totally_new_feature", Tier.FREE)

    def test_features_map_has_expected_keys(self):
        assert set(FEATURES) == {"cloud_sync", "multi_device", "ai_unlimited", "api_access", "audit_trail"}


# ---------------------------------------------------------------- hardware id
class TestHardwareId:
    def test_fingerprint_sha256_hex(self):
        value = fingerprint()
        assert len(value) == 64
        int(value, 16)

    def test_fingerprint_cached_deterministic(self):
        assert fingerprint() == fingerprint()

    def test_from_components_deterministic(self):
        a = fingerprint_from_components("001122334455", "Intel i7", "S12345")
        b = fingerprint_from_components("001122334455", "Intel i7", "S12345")
        assert a == b
        assert len(a) == 64

    def test_from_components_differs_on_any_source(self):
        base = fingerprint_from_components("001122334455", "Intel i7", "S12345")
        assert base != fingerprint_from_components("009988776655", "Intel i7", "S12345")
        assert base != fingerprint_from_components("001122334455", "AMD", "S12345")
        assert base != fingerprint_from_components("001122334455", "Intel i7", "OTHER")

    def test_from_components_normalizes_case_and_spaces(self):
        assert fingerprint_from_components("AA:BB", "X", "y") == fingerprint_from_components("aabb", "X", "y")


# ---------------------------------------------------------------- license keys
class TestLicenseKey:
    def test_roundtrip(self, keypair, payload):
        private, public, _ = keypair
        key = encode_key(payload, private)
        decoded = decode_key(key, public)
        assert decoded["tier"] == "pro"
        assert decoded["licensee"] == "Acme SARL"
        assert decoded["hwid"] == TEST_HWID
        assert decoded["exp"] == payload["exp"]
        assert decoded["v"] == "1"

    def test_key_format_grouped(self, keypair, payload):
        private, _, _ = keypair
        key = encode_key(payload, private)
        assert "---" in key
        for part in key.split("---"):
            for group in part.split("-"):
                assert len(group) <= 5
        assert "--" not in key.replace("---", "")

    def test_whitespace_tolerant_paste(self, keypair, payload):
        private, public, _ = keypair
        key = encode_key(payload, private)
        wrapped = "\n".join(key[i : i + 50] for i in range(0, len(key), 50))
        assert decode_key(wrapped, public)["licensee"] == "Acme SARL"

    def test_signature_mismatch_rejected(self, keypair, payload):
        private, public, other_public_pem = keypair
        foreign_private = load_private_key(generate_keypair()[0])
        key = encode_key(payload, foreign_private)
        with pytest.raises(LicenseSignatureError):
            decode_key(key, public)

    def test_payload_signature_verifies(self, keypair, payload):
        private, public, _ = keypair
        key = encode_key(payload, private)
        raw_payload, raw_sig = key.split("---")
        p = json.loads(base64.b64decode(raw_payload.replace("-", "")))
        sig = base64.b64decode(raw_sig.replace("-", ""))
        assert verify_signature(p, sig, public)

    def test_serialize_is_canonical(self, payload):
        assert payload_serialize(payload) == payload_serialize(dict(payload))

    @pytest.mark.parametrize(
        "bad_key",
        [
            "",
            "   ",
            "!!!---!!!",
            "abc",
            "abc---def",
            "eyJ---eZUpu-" * 2,
        ],
    )
    def test_malformed_keys_rejected(self, keypair, bad_key):
        _, public, _ = keypair
        with pytest.raises(LicenseInvalidError):
            decode_key(bad_key, public)

    def test_new_payload_defaults(self):
        p = new_license_payload(Tier.ENTERPRISE, TEST_HWID, "B", "2027-01-01")
        assert p["tier"] == "enterprise"
        assert p["iss"] == datetime.date.today().isoformat()
        assert len(p["uid"]) == 12


# ---------------------------------------------------------------- expiry
class TestExpiry:
    def test_parse_variants(self):
        d = datetime.date(2027, 1, 1)
        assert parse_expiry("2027-01-01") == d
        assert parse_expiry(d) == d
        assert parse_expiry(datetime.datetime(2027, 1, 1, 12, 0)) == d

    def test_days_remaining(self):
        today = datetime.date(2026, 8, 5)
        assert days_remaining("2026-08-10", today) == 5
        assert days_remaining("2026-08-05", today) == 0
        assert days_remaining("2026-08-01", today) == -4

    def test_is_expired(self):
        today = datetime.date(2026, 8, 5)
        assert is_expired("2026-08-04", today)
        assert not is_expired("2026-08-05", today)

    def test_grace_boundaries(self):
        today = datetime.date(2026, 8, 5)
        assert in_grace("2026-08-01", today)
        assert in_grace("2026-08-04", today)
        assert not in_grace("2026-07-01", today)
        assert not is_read_only("2026-08-01", today)
        assert is_read_only("2026-07-21", today)
        assert not is_read_only("2026-07-22", today)
        assert GRACE_DAYS == 14

    def test_expiry_from_today(self):
        today = datetime.date(2026, 8, 5)
        assert expiry_from_today(10, today) == "2026-08-15"
        assert expiry_from_today(-3, today) == "2026-08-02"


# ---------------------------------------------------------------- activation store
class TestActivation:
    def test_save_and_load(self, tmp_path, keypair):
        private, public, _ = keypair
        store = LicenseStore(path=str(tmp_path / "license.dat"), public_key=public, hardware_id=TEST_HWID)
        key = encode_key(new_license_payload(Tier.PRO, TEST_HWID, "X", expiry_from_today(30)), private)
        state = store.save(key)
        assert state.tier == Tier.PRO
        assert state.licensee == "X"
        assert (tmp_path / "license.dat").exists()
        reloaded = LicenseStore(path=str(tmp_path / "license.dat"), public_key=public, hardware_id=TEST_HWID)
        loaded = reloaded.load()
        assert loaded is not None
        assert loaded.tier == Tier.PRO
        assert loaded.expiry is not None

    def test_load_missing_returns_none(self, tmp_path, keypair):
        _, public, _ = keypair
        store = LicenseStore(path=str(tmp_path / "nope.dat"), public_key=public, hardware_id=TEST_HWID)
        assert store.load() is None

    def test_hardware_mismatch_rejected(self, tmp_path, keypair):
        private, public, _ = keypair
        store = LicenseStore(path=str(tmp_path / "license.dat"), public_key=public, hardware_id=OTHER_HWID)
        key = encode_key(new_license_payload(Tier.PRO, TEST_HWID, "X", expiry_from_today(30)), private)
        with pytest.raises(LicenseHardwareMismatchError):
            store.save(key)

    def test_expired_license_read_only(self, tmp_path, keypair):
        private, public, _ = keypair
        path = str(tmp_path / "license.dat")
        store = LicenseStore(path=path, public_key=public, hardware_id=TEST_HWID)
        key = encode_key(
            new_license_payload(Tier.PRO, TEST_HWID, "X", expiry_from_today(-30)), private
        )
        store.save(key)
        assert store.is_read_only()

    def test_valid_license_not_read_only(self, tmp_path, keypair):
        private, public, _ = keypair
        store = LicenseStore(path=str(tmp_path / "license.dat"), public_key=public, hardware_id=TEST_HWID)
        key = encode_key(
            new_license_payload(Tier.PRO, TEST_HWID, "X", expiry_from_today(30)), private
        )
        store.save(key)
        assert not store.is_read_only()

    def test_no_license_not_read_only(self, tmp_path, keypair):
        _, public, _ = keypair
        store = LicenseStore(path=str(tmp_path / "nope.dat"), public_key=public, hardware_id=TEST_HWID)
        assert not store.is_read_only()

    def test_challenge_contains_hardware_and_date(self, tmp_path, keypair):
        _, public, _ = keypair
        store = LicenseStore(path=str(tmp_path / "license.dat"), public_key=public, hardware_id=TEST_HWID)
        challenge = store.challenge()
        assert challenge["hardware_id"] == TEST_HWID
        assert challenge["date"] == datetime.date.today().isoformat()

    def test_state_perpetual(self, tmp_path, keypair):
        private, public, _ = keypair
        store = LicenseStore(path=str(tmp_path / "license.dat"), public_key=public, hardware_id=TEST_HWID)
        payload = new_license_payload(Tier.ENTERPRISE, TEST_HWID, "Y", "2099-01-01")
        payload.pop("exp")
        key = encode_key(payload, private)
        state = store.save(key)
        assert state.is_perpetual
        assert not store.is_read_only()


# ---------------------------------------------------------------- embedded key + samples
class TestEmbeddedKeyAndSamples:
    def test_embedded_public_key_loads(self):
        key = embedded_public_key()
        assert key.key_size == 2048

    def test_sample_keys_verify_with_embedded_key(self):
        import os as _os
        path = _os.path.join(
            _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
            "commercial", "keys", "sample_keys.txt",
        )
        if not _os.path.exists(path):
            from commercial.licensing.keygen import (
                _load_or_create_private_key, issue_key, SAMPLE_HARDWARE_ID,
            )
            from commercial.licensing.tier import Tier
            private_pem = _load_or_create_private_key()
            lines = []
            for index in range(1, 6):
                key = issue_key(
                    SAMPLE_HARDWARE_ID,
                    Tier.PRO if index % 2 else Tier.ENTERPRISE,
                    days=90 * index,
                    licensee=f"Demo Customer {index}",
                    private_pem=private_pem,
                )
                lines.append(f"  [{index}] {key}")
            _os.makedirs(_os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
        assert os.path.exists(path), "sample_keys.txt must exist (deliverable)"
        lines = open(path, encoding="utf-8").read().splitlines()
        keys = [line.split("] ", 1)[1].strip() for line in lines if "[1]" in line or "[2]" in line or "[3]" in line or "[4]" in line or "[5]" in line]
        assert len(keys) == 5
        pub = embedded_public_key()
        tiers = {decode_key(k, pub)["tier"] for k in keys}
        assert tiers == {"pro", "enterprise"}


# ---------------------------------------------------------------- fallbacks & error branches
class TestHardwareIdFallbacks:
    def test_mac_fallback_on_error(self, monkeypatch):
        from commercial.licensing import hardware_id as hw

        def boom():
            raise RuntimeError("no uuid")

        monkeypatch.setattr(hw.uuid, "getnode", boom)
        assert hw._mac() == "000000000000"

    def test_processor_fallback(self, monkeypatch):
        from commercial.licensing import hardware_id as hw

        def boom():
            raise RuntimeError("no platform")

        monkeypatch.setattr(hw.platform, "processor", lambda: "")
        monkeypatch.setattr(hw.platform, "machine", boom)
        assert hw._processor() == "unknown"

    def test_disk_serial_success(self, monkeypatch):
        from commercial.licensing import hardware_id as hw

        class FakeResult:
            stdout = "SN12345\r\n"

        monkeypatch.setattr(hw.subprocess, "run", lambda *a, **k: FakeResult())
        assert hw._disk_serial() == "SN12345"

    def test_disk_serial_fallback(self, monkeypatch):
        from commercial.licensing import hardware_id as hw

        def boom(*a, **k):
            raise OSError("no powershell")

        monkeypatch.setattr(hw.subprocess, "run", boom)
        assert hw._disk_serial() == ""


class TestLicenseExtraBranches:
    def test_date_objects_in_payload(self, keypair):
        private, public, _ = keypair
        payload = new_license_payload(
            Tier.PRO, TEST_HWID, "X",
            datetime.date(2027, 1, 1), issued=datetime.date(2026, 1, 1),
        )
        decoded = decode_key(encode_key(payload, private), public)
        assert decoded["exp"] == "2027-01-01"
        assert decoded["iss"] == "2026-01-01"

    def test_verify_signature_wrong_key_returns_false(self, keypair, payload):
        private, public, _ = keypair
        foreign_private = load_private_key(generate_keypair()[0])
        assert not verify_signature(payload, sign_payload(payload, foreign_private), public)

    def test_signature_b64_decode_failure(self, keypair):
        _, public, _ = keypair
        payload_b64 = base64.b64encode(payload_serialize(payload := new_license_payload(Tier.PRO, TEST_HWID, "X", expiry_from_today(5)))).decode("ascii")
        with pytest.raises(LicenseInvalidError):
            decode_key(payload_b64 + "---" + "A" * 41, public)

    def test_json_corrupt_payload(self, keypair):
        _, public, _ = keypair
        bad = base64.b64encode(b"definitely-not-json").decode("ascii")
        sig = base64.b64encode(b"B" * 64).decode("ascii")
        with pytest.raises(LicenseInvalidError):
            decode_key(bad + "---" + sig, public)

    def test_missing_signature_separator_rejected(self, keypair, payload):
        private, _, _ = keypair
        key = encode_key(payload, private).replace("---", "-")
        _, public, _ = keypair
        with pytest.raises(LicenseInvalidError):
            decode_key(key, public)


class TestActivationErrorPaths:
    def test_garbage_license_file_raises(self, tmp_path, keypair):
        _, public, _ = keypair
        path = tmp_path / "license.dat"
        path.write_text("garbage", encoding="utf-8")
        store = LicenseStore(path=str(path), public_key=public, hardware_id=TEST_HWID)
        with pytest.raises(LicenseInvalidError):
            store.load()

    def test_license_path_is_directory(self, tmp_path, keypair):
        _, public, _ = keypair
        directory = tmp_path / "a_dir"
        directory.mkdir()
        store = LicenseStore(path=str(directory), public_key=public, hardware_id=TEST_HWID)
        with pytest.raises(LicenseFileError):
            store.load()

    def test_save_into_missing_directory(self, tmp_path, keypair):
        private, public, _ = keypair
        store = LicenseStore(
            path=str(tmp_path / "no_such_dir" / "license.dat"),
            public_key=public,
            hardware_id=TEST_HWID,
        )
        key = encode_key(new_license_payload(Tier.PRO, TEST_HWID, "X", expiry_from_today(5)), private)
        with pytest.raises(LicenseFileError):
            store.save(key)

    def test_corrupt_expiry_in_payload(self, tmp_path, keypair):
        private, public, _ = keypair
        payload = new_license_payload(Tier.PRO, TEST_HWID, "X", "not-a-date")
        key = encode_key(payload, private)
        store = LicenseStore(path=str(tmp_path / "l.dat"), public_key=public, hardware_id=TEST_HWID)
        with pytest.raises(LicenseSignatureError):
            store.save(key)

    def test_is_read_only_swallows_load_errors(self, tmp_path, keypair):
        _, public, _ = keypair
        path = tmp_path / "license.dat"
        path.write_text("garbage", encoding="utf-8")
        store = LicenseStore(path=str(path), public_key=public, hardware_id=TEST_HWID)
        assert store.is_read_only() is False

    def test_expired_payload_verified_but_read_only(self, tmp_path, keypair):
        private, public, _ = keypair
        payload = new_license_payload(Tier.PRO, TEST_HWID, "X", "2026-01-01")
        key = encode_key(payload, private)
        store = LicenseStore(path=str(tmp_path / "l.dat"), public_key=public, hardware_id=TEST_HWID)
        state = store.save(key)
        assert state.expiry == datetime.date(2026, 1, 1)
        assert store.is_read_only()


# ---------------------------------------------------------------- keygen CLI
class TestKeygenCLI:
    def _patch_paths(self, monkeypatch, tmp_path):
        from commercial.licensing import keygen as kg

        keys_dir = str(tmp_path / "keys")
        monkeypatch.setattr(kg, "KEYS_DIR", keys_dir)
        monkeypatch.setattr(kg, "PRIVATE_KEY_FILE", os.path.join(keys_dir, "private_key.pem"))
        monkeypatch.setattr(kg, "PUBLIC_KEY_FILE", str(tmp_path / "pub_key.pem"))
        return kg

    def test_sample_keys_writes_private_and_verifies(self, monkeypatch, tmp_path):
        from commercial.licensing.license import load_public_key

        kg = self._patch_paths(monkeypatch, tmp_path)
        assert kg.main(["--sample"]) == 0
        assert os.path.exists(kg.PRIVATE_KEY_FILE)
        pub = load_public_key(open(kg.PUBLIC_KEY_FILE, "rb").read())
        key = kg.issue_key(
            kg.SAMPLE_HARDWARE_ID, Tier.PRO, 90, "Demo Customer 1",
            open(kg.PRIVATE_KEY_FILE, "rb").read(),
        )
        assert decode_key(key, pub)["tier"] == "pro"

    def test_new_keypair_flag(self, monkeypatch, tmp_path):
        kg = self._patch_paths(monkeypatch, tmp_path)
        assert kg.main(["--new-keypair"]) == 0
        assert os.path.exists(kg.PRIVATE_KEY_FILE)
        assert os.path.exists(kg.PUBLIC_KEY_FILE)

    def test_issue_custom_license(self, monkeypatch, tmp_path, capsys):
        from commercial.licensing.license import load_public_key

        kg = self._patch_paths(monkeypatch, tmp_path)
        kg.main(["--sample"])  # bootstrap key pair
        kg.main(["--hwid", TEST_HWID, "--tier", "enterprise", "--days", "30", "--licensee", "T" ])
        key_line = [l for l in capsys.readouterr().out.splitlines() if l.strip() and "---" in l][-1]
        pub = load_public_key(open(kg.PUBLIC_KEY_FILE, "rb").read())
        assert decode_key(key_line, pub)["tier"] == "enterprise"


# ---------------------------------------------------------------- license dialog logic
from commercial.licensing.license_dialog import (  # noqa: E402
    describe_license,
    tier_label,
    try_activate,
)
from ui.resources.i18n import t  # noqa: E402


class TestLicenseDialogLogic:
    def _store(self, tmp_path, keypair):
        _, public, _ = keypair
        return LicenseStore(
            path=str(tmp_path / "license.dat"), public_key=public, hardware_id=TEST_HWID
        )

    def test_describe_no_license(self, tmp_path, keypair):
        store = self._store(tmp_path, keypair)
        tier, licensee, expiry, hwid = describe_license(store)
        assert tier == t("license_status_no")
        assert expiry == t("license_status_trial")
        assert hwid == TEST_HWID

    def test_describe_active_license(self, tmp_path, keypair):
        private, _, _ = keypair
        store = self._store(tmp_path, keypair)
        key = encode_key(new_license_payload(Tier.PRO, TEST_HWID, "Acme", expiry_from_today(30)), private)
        store.save(key)
        tier, licensee, expiry, _ = describe_license(store)
        assert tier == tier_label(Tier.PRO)
        assert licensee == "Acme"
        assert expiry == store.load().expiry.isoformat()

    def test_describe_perpetual_license(self, tmp_path, keypair):
        private, _, _ = keypair
        store = self._store(tmp_path, keypair)
        payload = new_license_payload(Tier.ENTERPRISE, TEST_HWID, "Y", "2099-01-01")
        payload.pop("exp")
        key = encode_key(payload, private)
        store.save(key)
        _, _, expiry, _ = describe_license(store)
        assert expiry == t("license_perpetual")

    def test_describe_corrupt_file_does_not_raise(self, tmp_path, keypair):
        _, public, _ = keypair
        path = tmp_path / "license.dat"
        path.write_text("garbage", encoding="utf-8")
        store = LicenseStore(path=str(path), public_key=public, hardware_id=TEST_HWID)
        tier, _, expiry, _ = describe_license(store)
        assert tier == t("license_status_no")
        assert expiry == t("license_status_trial")

    def test_try_activate_success(self, tmp_path, keypair):
        private, _, _ = keypair
        store = self._store(tmp_path, keypair)
        key = encode_key(new_license_payload(Tier.PRO, TEST_HWID, "X", expiry_from_today(30)), private)
        ok, state, error = try_activate(store, key)
        assert ok
        assert state is not None and state.tier == Tier.PRO
        assert error is None
        assert store.load() is not None

    def test_try_activate_empty_key(self, tmp_path, keypair):
        store = self._store(tmp_path, keypair)
        ok, state, error = try_activate(store, "   ")
        assert not ok
        assert state is None
        assert error is not None
        assert store.load() is None

    def test_try_activate_invalid_key(self, tmp_path, keypair):
        store = self._store(tmp_path, keypair)
        ok, state, error = try_activate(store, "not-a-key")
        assert not ok
        assert state is None
        assert isinstance(error, LicenseInvalidError)

    def test_try_activate_wrong_hardware(self, tmp_path, keypair):
        private, _, _ = keypair
        store = self._store(tmp_path, keypair)
        key = encode_key(new_license_payload(Tier.PRO, OTHER_HWID, "X", expiry_from_today(30)), private)
        ok, _, error = try_activate(store, key)
        assert not ok
        assert isinstance(error, LicenseHardwareMismatchError)

    def test_tier_label_known_and_fallback(self):
        assert tier_label(Tier.ENTERPRISE) == t("license_tier_enterprise")
        assert tier_label(Tier.FREE) == t("license_tier_free")
