# اختبارات تحسينات التحديث التلقائي
# ===================================
# - التوزيع التدريجي (gradual rollout)
# - معالجة الأخطاء المنظمة
# - النسخ الاحتياطي للتراجع + الاستعادة

import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUpdateCheckerRollout(unittest.TestCase):
    """اختبارات التوزيع التدريجي للتحديثات"""

    def setUp(self):
        from modules.update_checker import UpdateChecker
        self.checker = UpdateChecker(current_version="3.1.4")

    def test_rollout_100_always_eligible(self):
        self.checker.rollout_pct = 100
        self.assertTrue(self.checker.is_rollout_eligible())

    def test_rollout_0_never_eligible(self):
        self.checker.rollout_pct = 0
        self.assertFalse(self.checker.is_rollout_eligible())

    def test_rollout_deterministic(self):
        self.checker.rollout_pct = 50
        self.assertEqual(
            self.checker.is_rollout_eligible(),
            self.checker.is_rollout_eligible(),
        )

    def test_rollout_parse_from_data(self):
        with patch("modules.update_checker.urllib.request.urlopen") as mock_open:
            mock_resp = mock_open.return_value.__enter__.return_value
            mock_resp.read.return_value = json.dumps({
                "version": "3.1.6", "rollout": 25,
            }).encode("utf-8")
            has_update, data = self.checker.check_for_updates(timeout=1)
            self.assertTrue(has_update)
            self.assertEqual(self.checker.rollout_pct, 25)

    def test_rollout_default_100_when_missing(self):
        with patch("modules.update_checker.urllib.request.urlopen") as mock_open:
            mock_resp = mock_open.return_value.__enter__.return_value
            mock_resp.read.return_value = json.dumps({"version": "3.1.6"}).encode("utf-8")
            self.checker.check_for_updates(timeout=1)
            self.assertEqual(self.checker.rollout_pct, 100)


class TestUpdateCheckerErrors(unittest.TestCase):
    """اختبارات معالجة الأخطاء المنظمة"""

    def setUp(self):
        from modules.update_checker import UpdateChecker
        self.checker = UpdateChecker(current_version="3.1.4")

    def test_http_error_sets_last_error(self):
        import urllib.error
        err = urllib.error.HTTPError("url", 404, "Not Found", None, None)
        with patch("modules.update_checker.urllib.request.urlopen", side_effect=err):
            has_update, data = self.checker.check_for_updates(timeout=1)
            self.assertFalse(has_update)
            self.assertIsNone(data)
            self.assertIsNotNone(self.checker.last_error)
            self.assertEqual(self.checker.last_error["type"], "http")
            self.assertEqual(self.checker.last_error["status"], 404)

    def test_network_error_sets_last_error(self):
        import urllib.error
        err = urllib.error.URLError("boom")
        with patch("modules.update_checker.urllib.request.urlopen", side_effect=err):
            has_update, data = self.checker.check_for_updates(timeout=1)
            self.assertFalse(has_update)
            self.assertEqual(self.checker.last_error["type"], "network")

    def test_success_resets_last_error(self):
        with patch("modules.update_checker.urllib.request.urlopen") as mock_open:
            mock_resp = mock_open.return_value.__enter__.return_value
            mock_resp.read.return_value = json.dumps({"version": "3.1.6"}).encode("utf-8")
            self.checker.check_for_updates(timeout=1)
            self.assertIsNone(self.checker.last_error)

    def test_success_after_fallback_resets_last_error(self):
        import urllib.error
        err = urllib.error.HTTPError("url", 503, "Unavailable", None, None)
        resp = mock.MagicMock()
        resp.__enter__.return_value.read.return_value = json.dumps(
            {"version": "3.1.6"}
        ).encode("utf-8")
        with patch("modules.update_checker.VERSION_URL", "https://a.example/v.json"), \
             patch("modules.update_checker.FALLBACK_URL", "https://b.example/v.json"), \
             patch("modules.update_checker.urllib.request.urlopen",
                   side_effect=[err, resp]):
            has_update, data = self.checker.check_for_updates(timeout=1)
        self.assertTrue(has_update)
        self.assertIsNone(self.checker.last_error)

    def test_get_update_info_includes_eligibility(self):
        with patch("modules.update_checker.urllib.request.urlopen") as mock_open:
            mock_resp = mock_open.return_value.__enter__.return_value
            mock_resp.read.return_value = json.dumps({
                "version": "3.1.6", "rollout": 100,
            }).encode("utf-8")
            self.checker.check_for_updates(timeout=1)
            info = self.checker.get_update_info()
            self.assertIn("eligible", info)
            self.assertIn("rollout_pct", info)


class TestUpdateRollback(unittest.TestCase):
    """اختبارات النسخ الاحتياطي للتراجع والاستعادة"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="sa_rollback_")
        self.exe_path = os.path.join(self.tmpdir, "SmartAccounting.exe")
        with open(self.exe_path, "wb") as f:
            f.write(b"NEW_VERSION_BYTES")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_backup_creates_previous_file(self):
        from modules.update_checker import backup_current_executable, has_rollback_backup
        target = backup_current_executable(exe_path=self.exe_path)
        self.assertIsNotNone(target)
        self.assertTrue(os.path.exists(target))
        self.assertTrue(target.endswith(".previous.exe"))
        self.assertTrue(has_rollback_backup(exe_path=self.exe_path))

    def test_restore_previous_overwrites_current(self):
        from modules.update_checker import (
            backup_current_executable, restore_previous_executable,
        )
        backup_current_executable(exe_path=self.exe_path)
        with open(self.exe_path, "wb") as f:
            f.write(b"BROKEN_BYTES")
        ok = restore_previous_executable(exe_path=self.exe_path)
        self.assertTrue(ok)
        with open(self.exe_path, "rb") as f:
            self.assertEqual(f.read(), b"NEW_VERSION_BYTES")

    def test_restore_when_no_backup_fails(self):
        from modules.update_checker import restore_previous_executable
        self.assertFalse(restore_previous_executable(exe_path=self.exe_path))

    def test_backup_missing_exe_returns_none(self):
        from modules.update_checker import backup_current_executable
        self.assertIsNone(
            backup_current_executable(exe_path=os.path.join(self.tmpdir, "missing.exe"))
        )

    def test_cleanup_removes_backup(self):
        from modules.update_checker import (
            backup_current_executable, cleanup_rollback, has_rollback_backup,
        )
        backup_current_executable(exe_path=self.exe_path)
        self.assertTrue(has_rollback_backup(exe_path=self.exe_path))
        self.assertTrue(cleanup_rollback(exe_path=self.exe_path))
        self.assertFalse(has_rollback_backup(exe_path=self.exe_path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
