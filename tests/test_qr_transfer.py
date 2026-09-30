# اختبار نقل البيانات عبر QR
# ==============================
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.app_state import state


class TestQrTransfer(unittest.TestCase):
    """gzip + base64 ثم توليد QR — جولة ذهاب وإياب سليمة."""

    def setUp(self):
        state.clear()

    def tearDown(self):
        state.clear()

    def test_encode_decode_roundtrip(self):
        import modules.qr_transfer as qr
        payload = {"company_name": "شركة", "ratios": {"roe": 12.5}, "n": 42}
        encoded = qr.encode_payload(payload)
        self.assertIsInstance(encoded, str)
        decoded = qr.decode_payload(encoded)
        self.assertEqual(decoded, payload)

    def test_gzip_reduces_redundant_data(self):
        import modules.qr_transfer as qr
        import json
        payload = {"financial_data": [{"revenue": 1000, "cogs": 500} for _ in range(50)]}
        raw = json.dumps(payload).encode("utf-8")
        encoded = qr.encode_payload(payload)
        self.assertLess(len(encoded), len(raw))

    def test_make_qr_png_returns_bytes(self):
        import modules.qr_transfer as qr
        png = qr.make_qr_png(qr.encode_payload({"a": 1}))
        self.assertIsInstance(png, bytes)
        self.assertTrue(png[:8] == b"\x89PNG\r\n\x1a\n", "should be PNG signature")

    def test_build_payload_has_core_keys(self):
        import modules.qr_transfer as qr
        state.company_name = "شركة اختبار"
        payload = qr.build_payload()
        self.assertIn("financial_data", payload)
        self.assertIn("ratios", payload)
        self.assertEqual(payload["company_name"], "شركة اختبار")

    def test_empty_payload_roundtrip(self):
        import modules.qr_transfer as qr
        encoded = qr.encode_payload({})
        self.assertEqual(qr.decode_payload(encoded), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
