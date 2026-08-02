# Unit tests for modules/backup.py (BackupManager) and
# modules/scheduled_backup.py (ScheduledBackup).

import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modules.backup as backup
import modules.scheduled_backup as sb
from modules.backup import BackupManager, MAX_BACKUPS
from modules.scheduled_backup import ScheduledBackup


# ==================== backup.py ====================

class TestBackupManager(unittest.TestCase):
    """Tests for the BackupManager class in modules/backup.py."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_dir = os.path.join(self.tmp.name, "db")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "platform.db")
        self._db_path_patcher = mock.patch.object(
            backup.config, "DATABASE_PATH", self.db_path
        )
        self._db_path_patcher.start()

    def tearDown(self):
        self._db_path_patcher.stop()
        self.tmp.cleanup()

    def test_init_sets_db_path(self):
        manager = BackupManager()
        self.assertEqual(manager.db_path, self.db_path)

    def test_backup_with_existing_db_copies_file(self):
        # قاعدة بيانات حقيقية → النسخة الاحتياطية قاعدة SQLite صالحة وتحوي البيانات
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t VALUES (7)")
        conn.commit()
        conn.close()
        target = os.path.join(self.tmp.name, "out", "copy.db")
        manager = BackupManager()
        ok, path = manager.backup(target)
        self.assertTrue(ok)
        self.assertEqual(path, target)
        self.assertTrue(os.path.exists(target))
        conn2 = sqlite3.connect(target)
        try:
            value = conn2.execute("SELECT id FROM t").fetchone()[0]
            self.assertEqual(value, 7)
        finally:
            conn2.close()

    def test_backup_with_missing_db_creates_empty_sqlite(self):
        target = os.path.join(self.tmp.name, "out", "empty.db")
        manager = BackupManager()
        ok, path = manager.backup(target)
        self.assertTrue(ok)
        self.assertEqual(path, target)
        conn = sqlite3.connect(target)
        conn.close()

    def test_backup_exception_returns_false(self):
        target = os.path.join(self.tmp.name, "out", "copy.db")
        manager = BackupManager()
        with mock.patch.object(backup.os, "makedirs",
                               side_effect=OSError("no space")):
            ok, message = manager.backup(target)
        self.assertFalse(ok)
        self.assertIn("no space", message)

    def test_auto_backup_creates_timestamped_backup(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t VALUES (1)")
        conn.commit()
        conn.close()
        manager = BackupManager()
        ok, path = manager.auto_backup("pre")
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(path))
        self.assertIn("backups", path)
        self.assertIn("pre_", os.path.basename(path))
        self.assertTrue(path.endswith(".db"))
        # النسخة الاحتياطية قابلة للفتح كقاعدة SQLite
        conn2 = sqlite3.connect(path)
        try:
            value = conn2.execute("SELECT id FROM t").fetchone()[0]
            self.assertEqual(value, 1)
        finally:
            conn2.close()

    def test_auto_backup_exception_returns_false(self):
        manager = BackupManager()
        with mock.patch.object(backup.os, "makedirs",
                               side_effect=OSError("boom")):
            ok, message = manager.auto_backup("pre")
        self.assertFalse(ok)
        self.assertIn("boom", message)

    def test_rotate_backups_removes_oldest(self):
        backup_dir = os.path.join(self.tmp.name, "rot")
        os.makedirs(backup_dir, exist_ok=True)
        base = 1600000000
        for i in range(12):
            path = os.path.join(backup_dir, f"bk_{i:02d}.db")
            with open(path, "wb") as f:
                f.write(b"x")
            os.utime(path, (base + i, base + i))
        manager = BackupManager()
        manager._rotate_backups(backup_dir)
        remaining = [f for f in os.listdir(backup_dir) if f.endswith(".db")]
        self.assertEqual(len(remaining), MAX_BACKUPS)

    def test_rotate_backups_remove_failure_swallowed(self):
        backup_dir = os.path.join(self.tmp.name, "rot")
        os.makedirs(backup_dir, exist_ok=True)
        for i in range(12):
            with open(os.path.join(backup_dir, f"bk_{i:02d}.db"), "wb") as f:
                f.write(b"x")
            os.utime(os.path.join(backup_dir, f"bk_{i:02d}.db"),
                     (1600000000 + i, 1600000000 + i))
        manager = BackupManager()
        with mock.patch.object(backup.os, "remove",
                               side_effect=OSError("locked")):
            manager._rotate_backups(backup_dir)  # must not raise
        self.assertEqual(len(os.listdir(backup_dir)), 12)

    def test_rotate_backups_listdir_exception_swallowed(self):
        manager = BackupManager()
        with mock.patch.object(backup.os, "listdir",
                               side_effect=OSError("boom")):
            manager._rotate_backups(self.tmp.name)  # must not raise

    def test_restore_success_restores_database(self):
        manager = BackupManager()
        with open(self.db_path, "wb") as f:
            f.write(b"original")
        backup_file = os.path.join(self.tmp.name, "snap.db")
        conn = sqlite3.connect(backup_file)
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t VALUES (42)")
        conn.commit()
        conn.close()
        ok, message = manager.restore(backup_file)
        self.assertTrue(ok)
        self.assertEqual(message, "Database restored successfully")
        conn2 = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(conn2.execute("SELECT id FROM t").fetchone()[0], 42)
        finally:
            conn2.close()
        pre_dir = os.path.join(self.db_dir, "backups")
        self.assertTrue(os.path.exists(pre_dir))
        self.assertTrue(any(f.startswith("pre_restore_")
                            for f in os.listdir(pre_dir)))

    def test_restore_corrupt_backup_returns_false(self):
        with open(self.db_path, "wb") as f:
            f.write(b"original")
        backup_file = os.path.join(self.tmp.name, "corrupt.db")
        with open(backup_file, "wb") as f:
            f.write(b"not a sqlite database at all")
        manager = BackupManager()
        ok, message = manager.restore(backup_file)
        self.assertFalse(ok)
        self.assertIn("valid", message.lower())
        with open(self.db_path, "rb") as f:
            self.assertEqual(f.read(), b"original")

    def test_is_valid_sqlite_read_error_returns_false(self):
        path = os.path.join(self.tmp.name, "bad_header.db")
        with open(path, "wb") as f:
            f.write(b"SQLite format 3\x00" + b"garbage" * 200)
        manager = BackupManager()
        self.assertFalse(manager._is_valid_sqlite(path))

    def test_restore_missing_backup_returns_false(self):
        manager = BackupManager()
        missing = os.path.join(self.tmp.name, "nope.db")
        ok, message = manager.restore(missing)
        self.assertFalse(ok)
        self.assertIn("not found", message)

    def test_restore_exception_returns_false(self):
        with open(self.db_path, "wb") as f:
            f.write(b"original")
        backup_file = os.path.join(self.tmp.name, "snap.db")
        conn = sqlite3.connect(backup_file)
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.commit()
        conn.close()
        manager = BackupManager()
        with mock.patch.object(backup.shutil, "copy2",
                               side_effect=OSError("disk fail")):
            ok, message = manager.restore(backup_file)
        self.assertFalse(ok)
        self.assertIn("disk fail", message)

    def test_list_backups_returns_metadata(self):
        backup_dir = os.path.join(self.tmp.name, "lst")
        os.makedirs(backup_dir, exist_ok=True)
        for name in ("a.db", "b.db", "notes.txt"):
            with open(os.path.join(backup_dir, name), "w",
                      encoding="utf-8") as f:
                f.write("data")
        manager = BackupManager()
        result = manager.list_backups(backup_dir)
        self.assertEqual(len(result), 2)
        names = {entry["name"] for entry in result}
        self.assertEqual(names, {"a.db", "b.db"})
        for entry in result:
            self.assertIn("size", entry)
            self.assertIn("date", entry)

    def test_list_backups_exception_returns_empty(self):
        manager = BackupManager()
        with mock.patch.object(backup.os, "listdir",
                               side_effect=OSError("boom")):
            result = manager.list_backups(self.tmp.name)
        self.assertEqual(result, [])

    def test_export_all_to_json(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE accounts (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO accounts VALUES (1, 'cash')")
        conn.commit()
        conn.close()
        out_dir = os.path.join(self.tmp.name, "export")
        os.makedirs(out_dir, exist_ok=True)
        manager = BackupManager()
        ok, count = manager.export_all_to_json(out_dir)
        self.assertTrue(ok)
        self.assertGreaterEqual(count, 1)
        json_file = os.path.join(out_dir, "accounts.json")
        self.assertTrue(os.path.exists(json_file))
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data[0]["name"], "cash")

    def test_export_all_to_json_invalid_db_returns_false(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            f.write("this is not a sqlite database at all")
        out_dir = os.path.join(self.tmp.name, "export")
        os.makedirs(out_dir, exist_ok=True)
        manager = BackupManager()
        ok, message = manager.export_all_to_json(out_dir)
        self.assertFalse(ok)
        self.assertIn("database", str(message).lower())

    def test_export_all_to_json_special_table_name(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('CREATE TABLE "chart of accounts" (id INTEGER)')
        conn.execute('INSERT INTO "chart of accounts" VALUES (5)')
        conn.commit()
        conn.close()
        out_dir = os.path.join(self.tmp.name, "export2")
        os.makedirs(out_dir, exist_ok=True)
        manager = BackupManager()
        ok, count = manager.export_all_to_json(out_dir)
        self.assertTrue(ok)
        self.assertGreaterEqual(count, 1)
        json_file = os.path.join(out_dir, "chartofaccounts.json")
        self.assertTrue(os.path.exists(json_file))
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data[0]["id"], 5)

    def test_import_from_json_success(self):
        json_file = os.path.join(self.tmp.name, "accounts.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"id": 1, "name": "cash"},
                       {"id": 2, "name": "bank"}], f)
        manager = BackupManager()
        ok, message = manager.import_from_json(json_file)
        self.assertTrue(ok)
        self.assertIn("Imported 2 rows", message)
        conn = sqlite3.connect(self.db_path)
        count = conn.execute(
            "SELECT COUNT(*) FROM [accounts]"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(count, 2)

    def test_import_from_json_empty_data_returns_false(self):
        json_file = os.path.join(self.tmp.name, "accounts.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        manager = BackupManager()
        ok, message = manager.import_from_json(json_file)
        self.assertFalse(ok)
        self.assertIn("No data found", message)

    def test_import_from_json_invalid_file_returns_false(self):
        json_file = os.path.join(self.tmp.name, "accounts.json")
        with open(json_file, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        manager = BackupManager()
        ok, message = manager.import_from_json(json_file)
        self.assertFalse(ok)

    def test_import_from_json_commit_failure_rolls_back(self):
        json_file = os.path.join(self.tmp.name, "accounts.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"id": 1}], f)
        manager = BackupManager()
        conn_mock = mock.MagicMock()
        conn_mock.commit.side_effect = RuntimeError("commit failed")
        conn_mock.rollback.side_effect = RuntimeError("rollback failed")
        with mock.patch.object(backup.sqlite3, "connect",
                               return_value=conn_mock):
            ok, message = manager.import_from_json(json_file)
        self.assertFalse(ok)
        self.assertIn("commit failed", message)
        conn_mock.rollback.assert_called_once()


# ==================== scheduled_backup.py ====================

class TestScheduledBackup(unittest.TestCase):
    """Tests for the ScheduledBackup class in modules/scheduled_backup.py."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        self.backup_dir = os.path.join(root, "backups")
        self.settings_file = os.path.join(root, "backup_settings.json")
        self.db_file = os.path.join(root, "accounting.db")
        self.users_file = os.path.join(root, "users.json")
        self.vault_file = os.path.join(root, "vault.enc")
        self._patchers = [
            mock.patch.object(sb, "BACKUP_DIR", self.backup_dir),
            mock.patch.object(sb, "SETTINGS_FILE", self.settings_file),
            mock.patch.object(sb, "DB_FILE", self.db_file),
            mock.patch.object(sb, "USERS_FILE", self.users_file),
            mock.patch.object(sb, "VAULT_FILE", self.vault_file),
        ]
        for patcher in self._patchers:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self._patchers):
            patcher.stop()
        self.tmp.cleanup()

    def test_load_settings_returns_defaults_when_file_missing(self):
        sched = ScheduledBackup()
        self.assertEqual(sched._settings, sb.DEFAULT_SETTINGS)

    def test_load_settings_merges_with_defaults(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump({"interval_minutes": 30}, f)
        sched = ScheduledBackup()
        self.assertEqual(sched._settings["interval_minutes"], 30)
        self.assertTrue(sched._settings["enabled"])

    def test_load_settings_corrupt_file_falls_back_to_defaults(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            f.write("{not valid json")
        sched = ScheduledBackup()
        self.assertEqual(sched._settings, sb.DEFAULT_SETTINGS)

    def test_save_settings_writes_file(self):
        sched = ScheduledBackup()
        sched._save_settings()
        self.assertTrue(os.path.exists(self.settings_file))
        with open(self.settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["interval_minutes"], 60)

    def test_save_settings_exception_is_swallowed(self):
        sched = ScheduledBackup()
        with mock.patch("builtins.open",
                        side_effect=OSError("disk full")):
            sched._save_settings()  # must not raise

    def test_start_schedules_timer(self):
        sched = ScheduledBackup()
        sched.start()
        self.assertTrue(sched.is_running())
        sched.stop()

    def test_start_restarts_timer(self):
        sched = ScheduledBackup()
        sched.start()
        first = sched._timer
        sched.start()
        self.assertTrue(sched.is_running())
        self.assertIsNotNone(sched._timer)
        sched.stop()

    def test_start_disabled_does_not_schedule(self):
        sched = ScheduledBackup()
        sched._settings["enabled"] = False
        sched.start()
        self.assertFalse(sched.is_running())

    def test_stop_timer_when_none_is_noop(self):
        sched = ScheduledBackup()
        sched._stop_timer()
        self.assertIsNone(sched._timer)

    def test_on_timer_runs_backup_and_restarts(self):
        sched = ScheduledBackup()
        with mock.patch.object(sched, "_run_backup") as run_mock, \
                mock.patch.object(sched, "start") as start_mock:
            sched._on_timer()
        run_mock.assert_called_once()
        start_mock.assert_called_once()

    def test_run_backup_success(self):
        sched = ScheduledBackup()
        with mock.patch.object(sched, "_create_backup",
                               return_value="backup_x"), \
                mock.patch.object(sched, "_cleanup_old_backups") as clean_mock:
            sched._run_backup()
        self.assertEqual(sched._backup_count, 1)
        self.assertIsNotNone(sched._last_backup)
        clean_mock.assert_called_once()

    def test_run_backup_with_empty_filename(self):
        sched = ScheduledBackup()
        with mock.patch.object(sched, "_create_backup", return_value=""):
            sched._run_backup()
        self.assertEqual(sched._backup_count, 0)
        self.assertIsNone(sched._last_backup)

    def test_run_backup_exception_is_swallowed(self):
        sched = ScheduledBackup()
        with mock.patch.object(sched, "_create_backup",
                               side_effect=RuntimeError("boom")):
            sched._run_backup()
        self.assertEqual(sched._backup_count, 0)

    def test_create_backup_copies_all_sources(self):
        for path in (self.db_file, self.users_file, self.vault_file):
            with open(path, "w", encoding="utf-8") as f:
                f.write("data")
        sched = ScheduledBackup()
        name = sched._create_backup()
        self.assertTrue(name.startswith("backup_"))
        bdir = os.path.join(self.backup_dir, name)
        for fname in ("accounting.db", "users.json", "vault.enc", "meta.json"):
            self.assertTrue(os.path.exists(os.path.join(bdir, fname)),
                            f"missing {fname}")
        with open(os.path.join(bdir, "meta.json"), "r",
                  encoding="utf-8") as f:
            meta = json.load(f)
        self.assertIn("files", meta)
        self.assertEqual(meta["timestamp"], name.replace("backup_", ""))

    def test_create_backup_with_missing_sources(self):
        sched = ScheduledBackup()
        name = sched._create_backup()
        bdir = os.path.join(self.backup_dir, name)
        self.assertFalse(os.path.exists(os.path.join(bdir, "accounting.db")))
        self.assertTrue(os.path.exists(os.path.join(bdir, "meta.json")))

    def test_create_backup_vault_excluded(self):
        with open(self.vault_file, "w", encoding="utf-8") as f:
            f.write("secret")
        sched = ScheduledBackup()
        sched._settings["include_vault"] = False
        name = sched._create_backup()
        self.assertFalse(
            os.path.exists(os.path.join(self.backup_dir, name, "vault.enc"))
        )

    def test_cleanup_removes_oldest_dirs(self):
        sched = ScheduledBackup()
        sched._settings["max_backups"] = 3
        for i in range(5):
            os.makedirs(os.path.join(self.backup_dir, f"backup_{i}"))
        sched._cleanup_old_backups()
        remaining = [d for d in os.listdir(self.backup_dir)
                     if d.startswith("backup_")]
        self.assertEqual(len(remaining), 3)

    def test_cleanup_missing_backup_dir_returns(self):
        sched = ScheduledBackup()
        with mock.patch.object(sb, "BACKUP_DIR",
                               os.path.join(self.tmp.name, "nope")):
            sched._cleanup_old_backups()  # must not raise

    def test_cleanup_rmtree_error_is_swallowed(self):
        sched = ScheduledBackup()
        sched._settings["max_backups"] = 0
        for i in range(2):
            os.makedirs(os.path.join(self.backup_dir, f"backup_{i}"))
        with mock.patch.object(sb.shutil, "rmtree",
                               side_effect=OSError("locked")):
            sched._cleanup_old_backups()  # must not raise

    def test_manual_backup_creates_backup(self):
        sched = ScheduledBackup()
        name = sched.manual_backup()
        self.assertTrue(name.startswith("backup_"))
        self.assertTrue(os.path.exists(os.path.join(self.backup_dir, name)))

    def test_get_backups_missing_dir_returns_empty(self):
        sched = ScheduledBackup()
        with mock.patch.object(sb, "BACKUP_DIR",
                               os.path.join(self.tmp.name, "nope")):
            self.assertEqual(sched.get_backups(), [])

    def test_get_backups_returns_meta(self):
        sched = ScheduledBackup()
        name = sched.manual_backup()
        backups = sched.get_backups()
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0]["name"], name)
        self.assertNotEqual(backups[0]["created"], "unknown")
        self.assertIn("files", backups[0])

    def test_get_backups_corrupt_meta_uses_defaults(self):
        bdir = os.path.join(self.backup_dir, "backup_bad")
        os.makedirs(bdir, exist_ok=True)
        with open(os.path.join(bdir, "meta.json"), "w",
                  encoding="utf-8") as f:
            f.write("{corrupt")
        sched = ScheduledBackup()
        backups = sched.get_backups()
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0]["created"], "unknown")
        self.assertEqual(backups[0]["files"], [])

    def test_restore_backup_success(self):
        bdir = os.path.join(self.backup_dir, "backup_restore")
        os.makedirs(bdir, exist_ok=True)
        with open(os.path.join(bdir, "accounting.db"), "w",
                  encoding="utf-8") as f:
            f.write("db-bytes")
        with open(os.path.join(bdir, "users.json"), "w",
                  encoding="utf-8") as f:
            f.write("users-bytes")
        sched = ScheduledBackup()
        self.assertTrue(sched.restore_backup("backup_restore"))
        with open(self.db_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "db-bytes")
        with open(self.users_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "users-bytes")

    def test_restore_backup_without_extra_files(self):
        bdir = os.path.join(self.backup_dir, "backup_db_only")
        os.makedirs(bdir, exist_ok=True)
        with open(os.path.join(bdir, "accounting.db"), "w",
                  encoding="utf-8") as f:
            f.write("db-bytes")
        sched = ScheduledBackup()
        self.assertTrue(sched.restore_backup("backup_db_only"))
        self.assertFalse(os.path.exists(self.users_file))

    def test_restore_backup_restores_vault(self):
        bdir = os.path.join(self.backup_dir, "backup_vault")
        os.makedirs(bdir, exist_ok=True)
        with open(os.path.join(bdir, "vault.enc"), "w",
                  encoding="utf-8") as f:
            f.write("vault-bytes")
        sched = ScheduledBackup()
        self.assertTrue(sched.restore_backup("backup_vault"))
        with open(self.vault_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "vault-bytes")

    def test_create_backup_meta_includes_itself(self):
        sched = ScheduledBackup()
        name = sched._create_backup()
        bdir = os.path.join(self.backup_dir, name)
        with open(os.path.join(bdir, "meta.json"), "r",
                  encoding="utf-8") as f:
            meta = json.load(f)
        self.assertIn("meta.json", meta["files"])

    def test_restore_backup_missing_returns_false(self):
        sched = ScheduledBackup()
        self.assertFalse(sched.restore_backup("backup_nope"))

    def test_get_settings_returns_copy(self):
        sched = ScheduledBackup()
        settings = sched.get_settings()
        self.assertEqual(settings, sb.DEFAULT_SETTINGS)
        settings["interval_minutes"] = 999
        self.assertEqual(sched._settings["interval_minutes"], 60)

    def test_update_settings_when_not_running(self):
        sched = ScheduledBackup()
        sched.update_settings({"interval_minutes": 45})
        self.assertEqual(sched.get_settings()["interval_minutes"], 45)
        self.assertTrue(os.path.exists(self.settings_file))
        self.assertFalse(sched.is_running())

    def test_update_settings_when_running_restarts(self):
        sched = ScheduledBackup()
        sched.start()
        sched.update_settings({"interval_minutes": 90})
        self.assertTrue(sched.is_running())
        self.assertEqual(sched.get_settings()["interval_minutes"], 90)
        sched.stop()


if __name__ == "__main__":
    unittest.main()
