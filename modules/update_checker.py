# فحص التحديثات
# ==============

import json
import urllib.request
import urllib.error
from typing import Dict, Optional, Tuple

from config import APP_VERSION
from utils.app_logger import get_logger

log = get_logger("update_checker")

# رابط فحص التحديثات
VERSION_URL = "https://khalilmebarek-creator.github.io/SmartAccounting/version.json"
FALLBACK_URL = None  # يُحدَّث تلقائياً من config


class UpdateChecker:
    """فحص التحديثات المتاحة"""

    def __init__(self, current_version: str = None):
        self.current_version = current_version or APP_VERSION
        self.remote_version = None
        self.changelog = []
        self.download_url = None
        self.installer_url = None

    def check_for_updates(self, timeout: int = 5) -> Tuple[bool, Optional[Dict]]:
        """
        فحص التحديثات من الإنترنت
        Returns: (has_update, version_info)
        """
        urls_to_try = [VERSION_URL]
        if FALLBACK_URL:
            urls_to_try.append(FALLBACK_URL)

        for url in urls_to_try:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": f"SmartAccounting/{self.current_version}"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))

                    self.remote_version = data.get("version", "0.0.0")
                    self.changelog = data.get("changelog", [])
                    self.download_url = data.get("download_url")
                    self.installer_url = data.get("installer_url")

                    has_update = self._compare_versions(
                        self.remote_version, self.current_version
                    )

                    log.info(
                        f"Update check: current={self.current_version}, "
                        f"remote={self.remote_version}, has_update={has_update}"
                    )

                    return has_update, data

            except (urllib.error.URLError, json.JSONDecodeError, Exception) as e:
                log.debug(f"Failed to check {url}: {e}")
                continue

        log.debug("All update check URLs failed")
        return False, None

    def _compare_versions(self, remote: str, local: str) -> bool:
        """مقارنة الإصدارات"""
        try:
            remote_parts = [int(x) for x in remote.split(".")]
            local_parts = [int(x) for x in local.split(".")]

            for r, l in zip(remote_parts, local_parts):
                if r > l:
                    return True
                elif r < l:
                    return False

            return len(remote_parts) > len(local_parts)
        except (ValueError, AttributeError):
            return False

    def get_update_info(self) -> Optional[Dict]:
        """الحصول على معلومات التحديث"""
        if not self.remote_version:
            return None

        return {
            "current": self.current_version,
            "remote": self.remote_version,
            "changelog": self.changelog,
            "download_url": self.download_url,
            "installer_url": self.installer_url,
            "has_update": self._compare_versions(
                self.remote_version, self.current_version
            ),
        }


def check_updates_async(callback=None, timeout: int = 5):
    """
    فحص التحديثات بشكل غير متزامن
    callback: دالة تُستدعى بالنتيجة (has_update, info)
    """
    import threading

    def _check():
        checker = UpdateChecker()
        has_update, data = checker.check_for_updates(timeout=timeout)
        if callback:
            callback(has_update, checker.get_update_info())

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
    return thread
