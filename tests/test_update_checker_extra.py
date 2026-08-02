# Additional unit tests for modules/update_checker.py.
# Covers: fallback URL handling, generic errors, version comparison edge cases,
# get_update_info without a check, async check, installer download (with/without
# progress, temp/output paths, failures), frozen executable detection, and
# rollback backup/restore/cleanup error paths. All network calls are mocked.

import json
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modules.update_checker as uc


def _mock_response(payload, content_length=None):
    resp = mock.MagicMock()
    ctx = resp.__enter__.return_value
    if content_length is None:
        ctx.headers.get.return_value = "0"
    else:
        ctx.headers.get.return_value = str(content_length)
    ctx.read.return_value = payload
    return resp


class TestCheckForUpdatesExtra(unittest.TestCase):
    """Tests for fallback URL and generic error handling."""

    def setUp(self):
        self.checker = uc.UpdateChecker(current_version="3.1.4")

    def test_fallback_url_used_after_primary_failure(self):
        err = urllib.error.HTTPError("url", 500, "server error", None, None)
        resp = _mock_response(json.dumps({"version": "9.9.9"}).encode("utf-8"))
        with mock.patch("modules.update_checker.FALLBACK_URL",
                        "https://fallback.example/version.json"):
            with mock.patch("modules.update_checker.urllib.request.urlopen",
                            side_effect=[err, resp]):
                has_update, data = self.checker.check_for_updates(timeout=1)
        self.assertTrue(has_update)
        self.assertEqual(data["version"], "9.9.9")
        self.assertIsNone(self.checker.last_error)

    def test_generic_exception_records_unknown_error(self):
        with mock.patch("modules.update_checker.urllib.request.urlopen",
                        side_effect=RuntimeError("boom")):
            has_update, data = self.checker.check_for_updates(timeout=1)
        self.assertFalse(has_update)
        self.assertIsNone(data)
        self.assertEqual(self.checker.last_error["type"], "unknown")
        self.assertIsNone(self.checker.last_error["status"])


class TestCompareVersions(unittest.TestCase):
    """Tests for version comparison edge cases."""

    def setUp(self):
        self.checker = uc.UpdateChecker(current_version="3.1.4")

    def test_remote_older_returns_false(self):
        self.assertFalse(self.checker._compare_versions("3.1.2", "3.1.4"))

    def test_equal_parts_remote_longer_returns_true(self):
        self.assertTrue(self.checker._compare_versions("3.1.4.1", "3.1.4"))

    def test_equal_parts_local_longer_returns_false(self):
        self.assertFalse(self.checker._compare_versions("3.1", "3.1.4"))

    def test_identical_versions_returns_false(self):
        self.assertFalse(self.checker._compare_versions("3.1.4", "3.1.4"))

    def test_malformed_remote_returns_false(self):
        self.assertFalse(self.checker._compare_versions("abc", "3.1.4"))
        self.assertFalse(self.checker._compare_versions("3.a.1", "3.1.4"))

    def test_none_remote_returns_false(self):
        self.assertFalse(self.checker._compare_versions(None, "3.1.4"))

    def test_get_update_info_without_check_returns_none(self):
        self.checker = uc.UpdateChecker(current_version="3.1.4")
        self.assertIsNone(self.checker.get_update_info())


class TestCheckUpdatesAsync(unittest.TestCase):
    """Tests for the async update check."""

    def test_async_check_invokes_callback(self):
        resp = _mock_response(json.dumps({"version": "9.9.9"}).encode("utf-8"))
        received = {}

        def callback(has_update, info):
            received["has_update"] = has_update
            received["info"] = info

        with mock.patch("modules.update_checker.urllib.request.urlopen",
                        return_value=resp):
            thread = uc.check_updates_async(callback=callback, timeout=1)
            thread.join(timeout=10)
        self.assertFalse(thread.is_alive())
        self.assertTrue(received.get("has_update", False))
        self.assertEqual(received["info"]["remote"], "9.9.9")

    def test_async_check_without_callback(self):
        resp = _mock_response(json.dumps({"version": "9.9.9"}).encode("utf-8"))
        with mock.patch("modules.update_checker.urllib.request.urlopen",
                        return_value=resp):
            thread = uc.check_updates_async(timeout=1)
            thread.join(timeout=10)
        self.assertFalse(thread.is_alive())


class TestDownloadInstaller(unittest.TestCase):
    """Tests for the installer downloader."""

    def test_download_to_output_path_with_progress(self):
        resp = mock.MagicMock()
        ctx = resp.__enter__.return_value
        ctx.headers.get.return_value = "100"
        ctx.read.side_effect = [b"x" * 50, b"y" * 50, b""]
        progress = []
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "setup.exe")
            with mock.patch("modules.update_checker.urllib.request.urlopen",
                            return_value=resp):
                path = uc.download_installer(
                    "https://example.com/setup.exe",
                    progress_callback=lambda d, t: progress.append((d, t)),
                    output_path=out,
                )
            self.assertEqual(path, out)
            with open(out, "rb") as f:
                self.assertEqual(len(f.read()), 100)
        self.assertEqual(progress, [(50, 100), (100, 100)])

    def test_download_without_output_path_uses_temp_file(self):
        resp = mock.MagicMock()
        ctx = resp.__enter__.return_value
        ctx.headers.get.return_value = "0"
        ctx.read.side_effect = [b"data", b""]
        with mock.patch("modules.update_checker.urllib.request.urlopen",
                        return_value=resp):
            path = uc.download_installer("https://example.com/app.zip")
        self.assertIsNotNone(path)
        self.assertTrue(path.endswith(".zip"))
        try:
            with open(path, "rb") as f:
                self.assertEqual(f.read(), b"data")
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_download_failure_returns_none(self):
        with mock.patch("modules.update_checker.urllib.request.urlopen",
                        side_effect=urllib.error.URLError("down")):
            self.assertIsNone(uc.download_installer("https://example.com/setup.exe"))

    def test_download_read_error_returns_none(self):
        resp = mock.MagicMock()
        resp.__enter__.return_value.read.side_effect = OSError("connection reset")
        with mock.patch("modules.update_checker.urllib.request.urlopen",
                        return_value=resp):
            self.assertIsNone(uc.download_installer("https://example.com/setup.exe"))

    def test_download_read_error_closes_and_removes_partial(self):
        resp = mock.MagicMock()
        ctx = resp.__enter__.return_value
        ctx.headers.get.return_value = "100"
        ctx.read.side_effect = [b"partial-data", OSError("connection reset")]
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "setup.exe")
            with mock.patch("modules.update_checker.urllib.request.urlopen",
                            return_value=resp):
                path = uc.download_installer(
                    "https://example.com/setup.exe", output_path=out
                )
            self.assertIsNone(path)
            self.assertFalse(os.path.exists(out))

    def test_download_read_error_removes_temp_partial(self):
        resp = mock.MagicMock()
        ctx = resp.__enter__.return_value
        ctx.headers.get.return_value = "100"
        ctx.read.side_effect = [b"partial-data", OSError("connection reset")]
        with mock.patch("modules.update_checker.urllib.request.urlopen",
                        return_value=resp):
            path = uc.download_installer("https://example.com/app.zip")
        self.assertIsNone(path)

    def test_download_cleanup_close_error_swallowed(self):
        resp = mock.MagicMock()
        ctx = resp.__enter__.return_value
        ctx.headers.get.return_value = "100"
        ctx.read.side_effect = [b"partial", OSError("reset")]
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "setup.exe")
            with mock.patch("modules.update_checker.urllib.request.urlopen",
                            return_value=resp), \
                 mock.patch("builtins.open") as open_mock:
                open_mock.return_value.close.side_effect = OSError("close boom")
                path = uc.download_installer(
                    "https://example.com/setup.exe", output_path=out
                )
            self.assertIsNone(path)

    def test_download_cleanup_remove_error_swallowed(self):
        resp = mock.MagicMock()
        ctx = resp.__enter__.return_value
        ctx.headers.get.return_value = "100"
        ctx.read.side_effect = [b"partial", OSError("reset")]
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "setup.exe")
            with open(out, "wb") as f:
                f.write(b"pre-existing")
            with mock.patch("modules.update_checker.urllib.request.urlopen",
                            return_value=resp), \
                 mock.patch("modules.update_checker.os.remove",
                            side_effect=OSError("locked")):
                path = uc.download_installer(
                    "https://example.com/setup.exe", output_path=out
                )
            self.assertIsNone(path)

    def test_download_no_progress_callback(self):
        resp = mock.MagicMock()
        ctx = resp.__enter__.return_value
        ctx.headers.get.return_value = "4"
        ctx.read.side_effect = [b"test", b""]
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "app.exe")
            with mock.patch("modules.update_checker.urllib.request.urlopen",
                            return_value=resp):
                path = uc.download_installer(
                    "https://example.com/app.exe", output_path=out
                )
            self.assertEqual(path, out)


class TestDefaultExecutable(unittest.TestCase):
    """Tests for frozen-executable detection."""

    def test_default_executable_when_frozen(self):
        with mock.patch("modules.update_checker.sys.frozen", True, create=True):
            with mock.patch("modules.update_checker.sys.executable",
                            "C:/App/SmartAccounting.exe"):
                self.assertEqual(
                    uc._default_executable(), "C:/App/SmartAccounting.exe"
                )

    def test_default_executable_when_not_frozen(self):
        if getattr(sys, "frozen", False):
            self.skipTest("cannot test non-frozen mode while frozen")
        self.assertIsNone(uc._default_executable())


class TestRollbackErrorPaths(unittest.TestCase):
    """Tests for backup/restore/cleanup error paths."""

    def test_backup_error_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = os.path.join(tmp, "app.exe")
            with open(exe, "wb") as f:
                f.write(b"old")
            with mock.patch("modules.update_checker.shutil.copy2",
                            side_effect=OSError("denied")):
                self.assertIsNone(uc.backup_current_executable(exe_path=exe))

    def test_has_rollback_backup_without_exe(self):
        with mock.patch("modules.update_checker._default_executable",
                        return_value=None):
            self.assertFalse(uc.has_rollback_backup())

    def test_restore_without_exe(self):
        with mock.patch("modules.update_checker._default_executable",
                        return_value=None):
            self.assertFalse(uc.restore_previous_executable())

    def test_restore_copy_error_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = os.path.join(tmp, "app.exe")
            with open(exe, "wb") as f:
                f.write(b"new")
            backup = uc.backup_current_executable(exe_path=exe)
            self.assertIsNotNone(backup)
            with mock.patch("modules.update_checker.shutil.copy2",
                            side_effect=OSError("denied")):
                self.assertFalse(uc.restore_previous_executable(exe_path=exe))

    def test_cleanup_without_exe(self):
        with mock.patch("modules.update_checker._default_executable",
                        return_value=None):
            self.assertFalse(uc.cleanup_rollback())

    def test_cleanup_remove_error_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = os.path.join(tmp, "app.exe")
            with open(exe, "wb") as f:
                f.write(b"new")
            uc.backup_current_executable(exe_path=exe)
            self.assertTrue(os.path.exists(exe + uc.ROLLBACK_SUFFIX))
            with mock.patch("modules.update_checker.os.remove",
                            side_effect=OSError("denied")):
                self.assertFalse(uc.cleanup_rollback(exe_path=exe))


if __name__ == "__main__":
    unittest.main()
