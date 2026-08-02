# اختبارات محرك المزامنة السحابية والنسخ الاحتياطي
# ================================================

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FakeState:
    """محاكاة بسيطة لـ AppState"""

    def __init__(self):
        self.company_name = "Test Co"
        self.company_name_fr = ""
        self.fiscal_year = 2025
        self.company_rc = ""
        self.company_nif = ""
        self.company_address = ""
        self.company_phone = ""
        self.company_email = ""
        self.company_legal_form = ""
        self.company_activity_type = ""
        self.company_bank_account = ""
        self.financial_data = {"revenue": 1000000}
        self.ratios = {"roe": 15.0}
        self.dupont = {}
        self.working_capital = {}
        self.audit_result = None
        self.tax_data = {}
        self.tax_summary = None
        self.tax_obligations = []
        self.scenarios = {}

    def save_data(self):
        pass

    def save_settings(self):
        pass


def _make_engine(tmp):
    """محرك بإعدادات ومسار نسخ احتياطي وسجل معزولين."""
    import sqlite3
    import modules.cloud_sync as cs
    cs.SYNC_SETTINGS_FILE = os.path.join(tmp, "sync_settings.json")
    cs.DEFAULT_BACKUP_DIR = os.path.join(tmp, "backups")

    class _Store:
        """مخزن SQLite مؤقت خفيف بديل عن تجمّع الاتصالات."""
        def __init__(self, path):
            self.conn = sqlite3.connect(path)
        def execute(self, query, params=None):
            cur = self.conn.cursor()
            cur.execute(query, params or ())
            self.conn.commit()
        def fetch_all(self, query, params=None):
            cur = self.conn.cursor()
            cur.execute(query, params or ())
            return cur.fetchall()

    store = _Store(os.path.join(tmp, "sync_history.db"))
    engine = cs.CloudSyncEngine(store=store)
    engine._settings = None
    return engine


class TestSnapshotIO(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cloudsync_")
        self.engine = _make_engine(self.tmp)
        self.state = FakeState()

    def test_snapshot_write_read_roundtrip(self):
        import modules.cloud_sync as cs
        payload = cs._build_payload(self.state)
        path = self.engine._write_snapshot(self.tmp, payload)
        result = self.engine.read_snapshot(path)
        self.assertEqual(result["company_name"], "Test Co")
        self.assertEqual(result["financial_data"], {"revenue": 1000000})

    def test_build_and_apply_payload(self):
        import modules.cloud_sync as cs
        payload = cs._build_payload(self.state)
        other = FakeState()
        other.financial_data = {}
        cs._apply_payload(other, payload)
        self.assertEqual(other.company_name, "Test Co")
        self.assertEqual(other.financial_data, {"revenue": 1000000})
        self.assertEqual(other.ratios, {"roe": 15.0})

    def test_encrypted_snapshot_roundtrip(self):
        import modules.cloud_sync as cs
        payload = {"company_name": "Secret", "format": 1, "timestamp": 1.0}
        encoded = cs.encrypt_payload(payload, "mypass")
        self.assertNotIn("Secret", encoded)
        self.assertEqual(cs.decrypt_payload(encoded, "mypass"), payload)

    def test_encrypted_snapshot_wrong_passphrase(self):
        import modules.cloud_sync as cs
        encoded = cs.encrypt_payload({"a": 1}, "right")
        with self.assertRaises(Exception):
            cs.decrypt_payload(encoded, "wrong")

    def test_read_snapshot_detects_checksum_change(self):
        import modules.cloud_sync as cs
        wrapper = {
            "app": cs.APP_ID, "format": 1, "timestamp": 1.0,
            "encrypted": False, "checksum": "deadbeef",
            "data": json.dumps({"a": 1}),
        }
        path = os.path.join(self.tmp, "bad_snapshot.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(wrapper))
        with self.assertRaises(ValueError):
            self.engine.read_snapshot(path)


class TestCloudSyncEngine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cloudsync_")
        self.engine = _make_engine(self.tmp)
        self.state = FakeState()

    def test_add_and_list_destination(self):
        dest_path = os.path.join(self.tmp, "cloud")
        os.makedirs(dest_path)
        dest = self.engine.add_destination("Dropbox", dest_path, auto=True)
        dests = self.engine.list_destinations()
        self.assertEqual(len(dests), 1)
        self.assertEqual(dests[0]["name"], "Dropbox")
        self.assertTrue(dests[0]["auto"])

    def test_remove_destination(self):
        dest = self.engine.add_destination("Drive", self.tmp)
        self.engine.remove_destination(dest["id"])
        self.assertEqual(self.engine.list_destinations(), [])

    def test_push_creates_snapshot_file(self):
        dest_path = os.path.join(self.tmp, "cloud")
        os.makedirs(dest_path)
        dest = self.engine.add_destination("Cloud", dest_path)
        results = self.engine.push(self.state)
        self.assertTrue(results)
        self.assertTrue(results[0]["ok"])
        snaps = self.engine.list_snapshots(dest_path)
        self.assertEqual(len(snaps), 1)
        self.assertGreater(snaps[0]["size"], 0)

    def test_push_all_destinations(self):
        for i in range(2):
            p = os.path.join(self.tmp, f"cloud{i}")
            os.makedirs(p)
            self.engine.add_destination(f"D{i}", p)
        results = self.engine.push(self.state)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["ok"] for r in results))

    def test_pull_restores_state(self):
        dest_path = os.path.join(self.tmp, "cloud")
        os.makedirs(dest_path)
        dest = self.engine.add_destination("Cloud", dest_path)
        self.engine.push(self.state)
        self.state.company_name = "Changed"
        self.state.financial_data = {"revenue": 0}
        snap = self.engine.list_snapshots(dest_path)[0]
        self.engine.pull(self.state, dest["id"], snap["name"])
        self.assertEqual(self.state.company_name, "Test Co")
        self.assertEqual(self.state.financial_data, {"revenue": 1000000})

    def test_backup_local_and_restore(self):
        result = self.engine.backup_local(self.state)
        self.assertTrue(os.path.exists(result["path"]))
        self.state.company_name = "Changed"
        self.engine.restore_backup(self.state, os.path.basename(result["path"]))
        self.assertEqual(self.state.company_name, "Test Co")

    def test_prune_keeps_max_backups(self):
        import modules.cloud_sync as cs
        for i in range(5):
            payload = {"app": cs.APP_ID, "format": 1,
                       "timestamp": float(i), "company_name": f"C{i}"}
            self.engine._write_snapshot(self.tmp, payload)
        self.engine._prune(self.tmp, 2)
        snaps = self.engine.list_snapshots(self.tmp)
        self.assertEqual(len(snaps), 2)

    def test_auto_backup_disabled(self):
        self.assertFalse(self.engine.auto_backup_due())

    def test_auto_backup_due_when_interval_elapsed(self):
        self.engine.set_setting("auto_backup", True)
        self.engine.set_setting("auto_backup_interval_hours", 1)
        self.engine.set_setting("last_auto_backup_at", 0)
        self.assertTrue(self.engine.auto_backup_due())

    def test_history_logged_after_push(self):
        dest_path = os.path.join(self.tmp, "cloud")
        os.makedirs(dest_path)
        self.engine.add_destination("Cloud", dest_path)
        self.engine.push(self.state)
        history = self.engine.history()
        self.assertTrue(any(h["action"] == "push" and h["status"] == "ok"
                            for h in history))

    def test_restore_from_file(self):
        import modules.cloud_sync as cs
        payload = cs._build_payload(self.state)
        path = os.path.join(self.tmp, "exported_snapshot.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.engine._snapshot_file(payload))
        self.state.company_name = "Changed"
        self.engine.restore_from_file(self.state, path)
        self.assertEqual(self.state.company_name, "Test Co")


if __name__ == "__main__":
    unittest.main(verbosity=2)
