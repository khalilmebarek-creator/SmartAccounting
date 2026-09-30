# اختبار إدارة اشتراكات البائع
# ==============================
import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modules.vendor_store as vendor_store


class TestVendorStore(unittest.TestCase):
    """توليد مفاتيح موقّعة + تتبع العملاء (حفظ/حذف/عرض)."""

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self._tmp.close()
        self._orig = vendor_store.VENDOR_FILE
        vendor_store.VENDOR_FILE = self._tmp.name

    def tearDown(self):
        vendor_store.VENDOR_FILE = self._orig
        try:
            os.remove(self._tmp.name)
        except OSError:
            pass

    def test_generate_key_verifies_with_public_key(self):
        from commercial.licensing.license import load_public_key, decode_key
        key = vendor_store.generate_key("Acme SARL", "pro", 365)
        self.assertIsInstance(key, str)
        self.assertGreater(len(key), 20)
        pub_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "commercial", "licensing", "pub_key.pem",
        )
        with open(pub_path, "rb") as f:
            pub = load_public_key(f.read())
        payload = decode_key(key, pub)
        self.assertEqual(payload["licensee"], "Acme SARL")
        self.assertEqual(payload["tier"], "pro")

    def test_add_and_list_clients(self):
        record = vendor_store.add_client("Client A", "a@test.dz", "pro", 90)
        self.assertIn("key", record)
        self.assertEqual(record["tier"], "pro")
        clients = vendor_store.list_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]["name"], "Client A")

    def test_delete_client_removes(self):
        record = vendor_store.add_client("Client B", "b@test.dz", "enterprise", 180)
        self.assertTrue(vendor_store.delete_client(record["id"]))
        self.assertEqual(vendor_store.list_clients(), [])

    def test_delete_unknown_returns_false(self):
        self.assertFalse(vendor_store.delete_client("nonexistent"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
