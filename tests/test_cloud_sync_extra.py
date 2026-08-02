# Supplemental unit tests for modules/cloud_sync.py.
# Covers the exception branches and edge cases not exercised by
# tests/test_cloud_sync.py. Test-only: nothing under modules/ is modified.

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modules.cloud_sync as cs
from modules.cloud_sync import CloudSyncEngine


class _Store:
    """Lightweight in-memory/file SQLite store standing in for the DB pool."""

    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=None):
        cur = self.conn.cursor()
        cur.execute(query, params or ())
        self.conn.commit()

    def fetch_all(self, query, params=None):
        cur = self.conn.cursor()
        cur.execute(query, params or ())
        return cur.fetchall()


class FakeState:
    """Simple stand-in for AppState."""

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


class CloudSyncExtraBase(unittest.TestCase):
    """Shared setup: isolated settings file, backup dir and history DB."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cloudsync_extra_")
        self.addCleanup(self.tmp.cleanup)
        cs.SYNC_SETTINGS_FILE = os.path.join(self.tmp.name, "sync_settings.json")
        cs.DEFAULT_BACKUP_DIR = os.path.join(self.tmp.name, "backups")
        self.store = _Store(
            sqlite3.connect(os.path.join(self.tmp.name, "history.db"))
        )
        self.engine = CloudSyncEngine(store=self.store)
        self.engine._settings = None
        self.state = FakeState()

    def tearDown(self):
        try:
            self.store.conn.close()
        except Exception:
            pass


class TestAtomicIO(CloudSyncExtraBase):

    def test_atomic_write_cleans_temp_on_failure(self):
        target = os.path.join(self.tmp.name, "out.json")
        with mock.patch.object(cs.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                cs._atomic_write(target, '{"a": 1}')
        leftovers = [n for n in os.listdir(self.tmp.name) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])

    def test_atomic_write_ignores_cleanup_failure(self):
        target = os.path.join(self.tmp.name, "out.json")
        with mock.patch.object(cs.os, "replace", side_effect=OSError("replace failed")), \
             mock.patch.object(cs.os, "remove", side_effect=OSError("remove failed")):
            with self.assertRaises(OSError):
                cs._atomic_write(target, '{"a": 1}')

    def test_safe_json_read_invalid_json_returns_default(self):
        bad = os.path.join(self.tmp.name, "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        self.assertEqual(cs._safe_json_read(bad, {"fallback": 1}), {"fallback": 1})
        with open(bad, "w", encoding="utf-8") as f:
            f.write("")
        self.assertEqual(cs._safe_json_read(bad, []), [])


class TestPayloadBranches(CloudSyncExtraBase):

    def test_build_payload_handles_currency_import_failure(self):
        with mock.patch.dict(sys.modules, {"modules.currency": None}):
            payload = cs._build_payload(self.state)
        self.assertEqual(payload["currency"], {})
        self.assertEqual(payload["company_name"], "Test Co")

    def test_apply_payload_handles_currency_restore_failure(self):
        payload = {
            "company_name": "X Co",
            "currency": {"base_currency": "USD", "currencies": {}, "rates": {}},
        }
        with mock.patch("modules.currency.currency_engine") as mock_ce:
            mock_ce.load_from_dict.side_effect = Exception("restore boom")
            result = cs._apply_payload(self.state, payload)
        self.assertTrue(result)
        self.assertEqual(self.state.company_name, "X Co")


class TestConnectionAndSettings(CloudSyncExtraBase):

    def test_conn_connects_when_db_connection_is_none(self):
        engine = CloudSyncEngine(store=None)
        mock_db = mock.Mock()
        mock_db.connection = None
        with mock.patch.object(cs, "db", mock_db):
            result = engine._conn()
        self.assertIs(result, mock_db)
        mock_db.connect.assert_called_once()

    def test_conn_handles_db_connect_failure(self):
        engine = CloudSyncEngine(store=None)
        mock_db = mock.Mock()
        mock_db.connection = None
        mock_db.connect.side_effect = Exception("db down")
        with mock.patch.object(cs, "db", mock_db):
            result = engine._conn()
        self.assertIs(result, mock_db)
        mock_db.connect.assert_called_once()

    def test_save_settings_handles_write_failure(self):
        self.engine._load_settings()
        with mock.patch.object(cs, "_atomic_write", side_effect=OSError("disk full")):
            self.engine._save_settings()
        self.assertFalse(os.path.exists(cs.SYNC_SETTINGS_FILE))

    def test_settings_returns_copy(self):
        self.engine.set_setting("auto_backup", True)
        s = self.engine.settings()
        self.assertTrue(s["auto_backup"])
        self.assertEqual(
            set(s.keys()),
            {"destinations", "auto_backup", "auto_backup_interval_hours",
             "max_backups", "last_auto_backup_at", "passphrase"},
        )
        s["auto_backup"] = False
        self.assertTrue(self.engine.settings()["auto_backup"])

    def test_set_passphrase_handles_none(self):
        self.engine.set_passphrase("s3cret")
        self.assertEqual(self.engine.get_passphrase(), "s3cret")
        self.engine.set_passphrase(None)
        self.assertEqual(self.engine.get_passphrase(), "")
        self.engine.set_passphrase("")
        self.assertEqual(self.engine.get_passphrase(), "")


class TestHistoryErrors(CloudSyncExtraBase):

    def test_log_swallows_store_errors(self):
        with mock.patch.object(self.engine, "_init_db",
                               side_effect=RuntimeError("init failed")):
            self.engine._log("push", "dest", "ok", 10)
        self.assertEqual(self.engine.history(), [])

    def test_history_returns_empty_on_store_error(self):
        with mock.patch.object(self.engine, "_init_db",
                               side_effect=RuntimeError("init failed")):
            self.assertEqual(self.engine.history(), [])

    def test_clear_history_success(self):
        self.engine._log("push", "d", "ok")
        self.assertEqual(len(self.engine.history()), 1)
        self.engine.clear_history()
        self.assertEqual(self.engine.history(), [])

    def test_clear_history_swallows_store_errors(self):
        with mock.patch.object(self.engine, "_init_db",
                               side_effect=RuntimeError("init failed")):
            self.engine.clear_history()


class TestDestinations(CloudSyncExtraBase):

    def test_set_destination_auto_toggles_flag(self):
        dest = self.engine.add_destination("Dropbox", self.tmp.name)
        self.assertFalse(dest["auto"])
        self.engine.set_destination_auto(dest["id"], True)
        self.assertTrue(self.engine.list_destinations()[0]["auto"])

    def test_set_destination_auto_unknown_id_is_safe(self):
        dest = self.engine.add_destination("Drive", self.tmp.name)
        self.engine.set_destination_auto(dest["id"] + 12345, True)
        self.assertFalse(self.engine.list_destinations()[0]["auto"])


class TestSnapshotReading(CloudSyncExtraBase):

    def test_read_snapshot_rejects_foreign_app(self):
        path = os.path.join(self.tmp.name, "foreign.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"app": "Other", "format": 1}, f)
        with self.assertRaisesRegex(ValueError, "invalid_snapshot"):
            self.engine.read_snapshot(path)

    def test_read_snapshot_encrypted_requires_passphrase(self):
        payload = {"app": cs.APP_ID, "format": 1, "timestamp": 1.0,
                   "company_name": "Secret"}
        path = self.engine._write_snapshot(self.tmp.name, payload, passphrase="pw")
        with self.assertRaisesRegex(ValueError, "passphrase_required"):
            self.engine.read_snapshot(path)

    def test_read_snapshot_encrypted_with_passphrase(self):
        payload = {"app": cs.APP_ID, "format": 1, "timestamp": 1.0,
                   "company_name": "Secret", "financial_data": {"revenue": 5}}
        path = self.engine._write_snapshot(self.tmp.name, payload, passphrase="pw")
        result = self.engine.read_snapshot(path, "pw")
        self.assertEqual(result["company_name"], "Secret")
        self.assertEqual(result["financial_data"], {"revenue": 5})

    def test_list_snapshots_missing_directory(self):
        self.assertEqual(
            self.engine.list_snapshots(os.path.join(self.tmp.name, "nope")), [])
        self.assertEqual(self.engine.list_snapshots(""), [])

    def test_list_snapshots_skips_unreadable(self):
        bad = os.path.join(self.tmp.name, "smart_accounting_snapshot_bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("{broken json")
        payload = {"app": cs.APP_ID, "format": 1, "timestamp": 1.0,
                   "company_name": "G"}
        good = self.engine._write_snapshot(self.tmp.name, payload)
        snaps = self.engine.list_snapshots(self.tmp.name)
        self.assertEqual(len(snaps), 1)
        self.assertEqual(snaps[0]["name"], os.path.basename(good))

    def test_prune_handles_remove_failure(self):
        payload = {"app": cs.APP_ID, "format": 1, "timestamp": 1.0,
                   "company_name": "C"}
        path = self.engine._write_snapshot(self.tmp.name, payload)
        with mock.patch.object(cs.os, "remove", side_effect=OSError("locked")):
            self.engine._prune(self.tmp.name, 0)
        self.assertTrue(os.path.exists(path))


class TestOperations(CloudSyncExtraBase):

    def test_push_filters_by_destination(self):
        p1 = os.path.join(self.tmp.name, "c1")
        p2 = os.path.join(self.tmp.name, "c2")
        os.makedirs(p1)
        os.makedirs(p2)
        d1 = self.engine.add_destination("Alpha", p1)
        d2 = self.engine.add_destination("Beta", p2)
        if d2["id"] == d1["id"]:
            d2["id"] = d1["id"] + 1
            self.engine._save_settings()
        results = self.engine.push(self.state, dest_id=d1["id"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["dest"], "Alpha")
        self.assertTrue(results[0]["ok"])

    def test_push_unknown_destination_returns_empty(self):
        self.assertEqual(self.engine.push(self.state, dest_id=123456789), [])

    def test_push_with_no_destinations_returns_empty(self):
        self.assertEqual(self.engine.push(self.state), [])

    def test_push_handles_write_failure(self):
        self.engine.add_destination("Cloud", self.tmp.name)
        with mock.patch.object(self.engine, "_write_snapshot",
                               side_effect=IOError("no space")):
            results = self.engine.push(self.state)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["ok"])
        self.assertEqual(results[0]["dest"], "Cloud")
        self.assertIn("no space", results[0]["error"])
        hist = self.engine.history()
        self.assertTrue(any(h["action"] == "push" and h["status"] == "error"
                            for h in hist))

    def test_pull_raises_for_unknown_destination(self):
        with self.assertRaisesRegex(ValueError, "destination_not_found"):
            self.engine.pull(self.state, 999999, "whatever.json")

    def test_backup_local_handles_write_failure(self):
        with mock.patch.object(self.engine, "_write_snapshot",
                               side_effect=IOError("disk error")):
            with self.assertRaises(IOError):
                self.engine.backup_local(self.state)
        hist = self.engine.history()
        self.assertTrue(any(h["action"] == "backup" and h["status"] == "error"
                            for h in hist))


class TestAutoBackupAndStatus(CloudSyncExtraBase):

    def _make_auto_due(self):
        self.engine.set_setting("auto_backup", True)
        self.engine.set_setting("auto_backup_interval_hours", 1)
        self.engine.set_setting("last_auto_backup_at", 0)

    def test_run_auto_backup_not_due(self):
        self.assertIsNone(self.engine.run_auto_backup(self.state))

    def test_run_auto_backup_due_success(self):
        self._make_auto_due()
        result = self.engine.run_auto_backup(self.state)
        self.assertIsNotNone(result)
        self.assertIn("path", result)
        self.assertGreater(self.engine.settings()["last_auto_backup_at"], 0)

    def test_run_auto_backup_failure(self):
        self._make_auto_due()
        with mock.patch.object(self.engine, "backup_local",
                               side_effect=IOError("boom")):
            self.assertIsNone(self.engine.run_auto_backup(self.state))

    def test_status_without_history(self):
        status = self.engine.status()
        self.assertIsNone(status["last_event"])
        self.assertEqual(status["destinations"], 0)
        self.assertFalse(status["auto_backup"])
        self.assertFalse(status["has_passphrase"])

    def test_status_with_last_event(self):
        self.engine.add_destination("Cloud", self.tmp.name)
        self.engine.push(self.state)
        status = self.engine.status()
        self.assertEqual(status["destinations"], 1)
        self.assertIsNotNone(status["last_event"])
        self.assertEqual(status["last_event"]["action"], "push")
        self.assertEqual(status["last_event"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
