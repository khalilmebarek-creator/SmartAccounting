# -*- coding: utf-8 -*-
# Module 2: Encryption (AES-256-GCM + Argon2id) — tests
# ======================================================
# تشفير الملفات عند التخزين + ترقية KDF المزامنة السحابية إلى Argon2id
# مع دعم القراءة الخلفي للتنسيق القديم (PBKDF2).

import base64
import json
import os
import tempfile
import unittest
from unittest import mock

import pytest

from commercial.encryption import (
    EncryptionError,
    decrypt_bytes,
    decrypt_file,
    encrypt_bytes,
    encrypt_file,
    is_encrypted_blob,
)
from commercial.encryption.kdf import (
    DEFAULT_MEMORY_COST,
    DEFAULT_PARALLELISM,
    DEFAULT_TIME_COST,
    derive_argon2id_key,
)

PASS = "كلمة المرور-123"
PARAMS = dict(memory_cost=8192, time_cost=1, parallelism=1)  # معلمات خفيفة للاختبار


class TestKdf(unittest.TestCase):

    def test_returns_32_bytes(self):
        key = derive_argon2id_key(PASS, b"s" * 16)
        self.assertEqual(len(key), 32)

    def test_deterministic_with_same_salt(self):
        key1 = derive_argon2id_key(PASS, b"s" * 16, **PARAMS)
        key2 = derive_argon2id_key(PASS, b"s" * 16, **PARAMS)
        self.assertEqual(key1, key2)

    def test_differs_by_salt(self):
        key1 = derive_argon2id_key(PASS, b"a" * 16, **PARAMS)
        key2 = derive_argon2id_key(PASS, b"b" * 16, **PARAMS)
        self.assertNotEqual(key1, key2)

    def test_differs_by_passphrase(self):
        key1 = derive_argon2id_key(PASS, b"s" * 16, **PARAMS)
        key2 = derive_argon2id_key("other", b"s" * 16, **PARAMS)
        self.assertNotEqual(key1, key2)

    def test_defaults_exist_and_are_strong(self):
        self.assertGreaterEqual(DEFAULT_MEMORY_COST, 65536)  # 64 MiB
        self.assertGreaterEqual(DEFAULT_TIME_COST, 3)
        self.assertGreaterEqual(DEFAULT_PARALLELISM, 1)

    def test_accepts_utf8_passphrase(self):
        key = derive_argon2id_key("", b"s" * 16, **PARAMS)
        self.assertEqual(len(key), 32)


class TestFileCrypt(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _roundtrip(self, data: bytes, passphrase=PASS):
        blob = encrypt_bytes(data, passphrase, **PARAMS)
        return blob, decrypt_bytes(blob, passphrase)

    def test_roundtrip_unicode(self):
        data = "البيانات المالية 2026 — €1000 😀".encode("utf-8")
        _, out = self._roundtrip(data)
        self.assertEqual(out, data)

    def test_roundtrip_empty(self):
        _, out = self._roundtrip(b"")
        self.assertEqual(out, b"")

    def test_roundtrip_binary(self):
        data = os.urandom(4096)
        _, out = self._roundtrip(data)
        self.assertEqual(out, data)

    def test_blob_is_marked(self):
        blob, _ = self._roundtrip(b"x")
        self.assertTrue(is_encrypted_blob(blob))
        self.assertFalse(is_encrypted_blob(b"plain"))
        self.assertFalse(is_encrypted_blob(b""))

    def test_wrong_passphrase_raises(self):
        blob, _ = self._roundtrip(b"secret")
        with pytest.raises(EncryptionError):
            decrypt_bytes(blob, "wrong")

    def test_tampered_ciphertext_raises(self):
        blob, _ = self._roundtrip(b"secret" * 100)
        tampered = bytearray(blob)
        tampered[-1] ^= 0xFF
        with pytest.raises(EncryptionError):
            decrypt_bytes(bytes(tampered), PASS)

    def test_tampered_header_raises(self):
        blob, _ = self._roundtrip(b"secret")
        tampered = bytearray(blob)
        tampered[20] ^= 0xFF  # داخل رأس التنسيق (salt)
        with pytest.raises(EncryptionError):
            decrypt_bytes(bytes(tampered), PASS)

    def test_truncated_blob_raises(self):
        blob, _ = self._roundtrip(b"secret" * 50)
        with pytest.raises(EncryptionError):
            decrypt_bytes(blob[:40], PASS)

    def test_unknown_magic_raises(self):
        with pytest.raises(EncryptionError):
            decrypt_bytes(b"SACF9" + b"\x00" * 200, PASS)

    def test_unsupported_kdf_raises(self):
        from commercial.encryption.filecrypt import _HEADER
        blob = _HEADER.pack(b"SACF1", 9, 8192, 1, 1, 16, 12) + b"\x00" * 40
        with pytest.raises(EncryptionError, match="KDF"):
            decrypt_bytes(blob, PASS)

    def test_invalid_header_lengths_raises(self):
        from commercial.encryption.filecrypt import _HEADER
        blob = _HEADER.pack(b"SACF1", 1, 8192, 1, 1, 8, 12) + b"\x00" * 40
        with pytest.raises(EncryptionError, match="lengths"):
            decrypt_bytes(blob, PASS)

    def test_truncated_after_header_raises(self):
        from commercial.encryption.filecrypt import _HEADER
        blob = _HEADER.pack(b"SACF1", 1, 8192, 1, 1, 16, 12) + b"\x00" * 28
        with pytest.raises(EncryptionError, match="truncated"):
            decrypt_bytes(blob, PASS)

    def test_params_roundtrip(self):
        blob, _ = self._roundtrip(b"data")
        self.assertIn(b"SACF1", blob)

    def test_encrypt_file_roundtrip(self):
        root = self._tmp.name
        src = os.path.join(root, "data.json")
        enc = os.path.join(root, "data.json.enc")
        dec = os.path.join(root, "data_dec.json")
        with open(src, "wb") as f:
            f.write("{\"a\":1} و عربي".encode("utf-8"))
        encrypt_file(src, enc, PASS, **PARAMS)
        self.assertTrue(os.path.exists(enc))
        with open(enc, "rb") as f:
            self.assertTrue(is_encrypted_blob(f.read()))
        decrypt_file(enc, dec, PASS)
        with open(src, "rb") as f:
            src_bytes = f.read()
        with open(dec, "rb") as f:
            dec_bytes = f.read()
        self.assertEqual(dec_bytes, src_bytes)

    def test_encrypt_file_wrong_passphrase(self):
        root = self._tmp.name
        src = os.path.join(root, "a.txt")
        enc = os.path.join(root, "a.txt.enc")
        dec = os.path.join(root, "b.txt")
        with open(src, "w", encoding="utf-8") as f:
            f.write("hello")
        encrypt_file(src, enc, PASS, **PARAMS)
        with pytest.raises(EncryptionError):
            decrypt_file(enc, dec, "nope")
        self.assertFalse(os.path.exists(dec))  # لا ملف جزئي

    def test_missing_source_raises(self):
        with pytest.raises(EncryptionError):
            encrypt_file(
                os.path.join(self._tmp.name, "missing"),
                os.path.join(self._tmp.name, "out"), PASS, **PARAMS
            )

    def test_decrypt_file_missing_source_raises(self):
        with pytest.raises(EncryptionError):
            decrypt_file(
                os.path.join(self._tmp.name, "missing"),
                os.path.join(self._tmp.name, "out"), PASS
            )

    def test_encrypt_file_write_failure_raises(self):
        src = os.path.join(self._tmp.name, "a.txt")
        enc = os.path.join(self._tmp.name, "a.txt.enc")
        with open(src, "w", encoding="utf-8") as f:
            f.write("x")
        with mock.patch(
            "commercial.encryption.filecrypt.os.replace",
            side_effect=OSError("disk full"),
        ):
            with pytest.raises(EncryptionError):
                encrypt_file(src, enc, PASS, **PARAMS)
        self.assertFalse(os.path.exists(enc))

    def test_encrypt_file_write_failure_cleanup_ignores_remove_error(self):
        src = os.path.join(self._tmp.name, "a.txt")
        enc = os.path.join(self._tmp.name, "a.txt.enc")
        with open(src, "w", encoding="utf-8") as f:
            f.write("x")
        with mock.patch(
            "commercial.encryption.filecrypt.os.replace",
            side_effect=OSError("disk full"),
        ), mock.patch(
            "commercial.encryption.filecrypt.os.remove",
            side_effect=OSError("locked"),
        ):
            with pytest.raises(EncryptionError):
                encrypt_file(src, enc, PASS, **PARAMS)


class TestCloudSyncIntegration(unittest.TestCase):
    """ترقية تشفير المزامنة السحابية إلى Argon2id مع دعم التنسيق القديم."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_roundtrip_new_format(self):
        from modules.cloud_sync import decrypt_payload, encrypt_payload
        payload = {"revenue": 1000, "الاسم": "شركة"}
        encoded = encrypt_payload(payload, "pw")
        self.assertEqual(decrypt_payload(encoded, "pw"), payload)

    def test_wrong_passphrase_new_format(self):
        from modules.cloud_sync import decrypt_payload, encrypt_payload
        encoded = encrypt_payload({"a": 1}, "pw")
        with pytest.raises(EncryptionError):
            decrypt_payload(encoded, "wrong")

    def test_legacy_blob_still_decrypts(self):
        """سنابات قديمة (PBKDF2 + ملح ثابت) تبقى قابلة للفك."""
        import hashlib
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from modules.cloud_sync import _derive_key, decrypt_payload
        payload = {"legacy": True, "value": 42}
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        iv = os.urandom(12)
        cipher = AESGCM(_derive_key("pw"))
        ct = cipher.encrypt(iv, raw, None)
        legacy_encoded = base64.b64encode(iv + ct).decode("ascii")
        self.assertFalse(legacy_encoded.startswith("U0FD"))
        self.assertEqual(decrypt_payload(legacy_encoded, "pw"), payload)
        with pytest.raises(EncryptionError):
            decrypt_payload(legacy_encoded, "bad")

    def test_snapshot_roundtrip_with_passphrase(self):
        from modules.cloud_sync import cloud_sync_engine
        engine = cloud_sync_engine
        payload = {"revenue": 500, "net_income": 120}
        path = engine._write_snapshot(self._tmp.name, payload, passphrase="pw")
        self.assertTrue(os.path.exists(path))
        restored = engine.read_snapshot(path, passphrase="pw")
        self.assertEqual(restored, payload)

    def test_snapshot_legacy_blob_reads(self):
        """سناب بغلاف قديم (data مشفّر PBKDF2) يقرأ عبر مسار الفك التراجعي."""
        import hashlib
        import json
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from modules.cloud_sync import APP_ID, FORMAT_VERSION, _derive_key, cloud_sync_engine
        payload = {"revenue": 7}
        raw = json.dumps(payload, ensure_ascii=False)
        iv = os.urandom(12)
        ct = AESGCM(_derive_key("pw")).encrypt(iv, raw.encode("utf-8"), None)
        legacy_encoded = base64.b64encode(iv + ct).decode("ascii")
        wrapper = {
            "app": APP_ID,
            "format": FORMAT_VERSION,
            "timestamp": 0,
            "destination": "",
            "encrypted": True,
            "checksum": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "data": legacy_encoded,
        }
        path = os.path.join(self._tmp.name, "legacy_snapshot.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(wrapper, f)
        self.assertEqual(cloud_sync_engine.read_snapshot(path, passphrase="pw"), payload)


if __name__ == "__main__":
    unittest.main()
