# فحص التحديثات
# ==============

import hashlib
import getpass
import json
import os
import shutil
import socket
import sys
import tempfile
import urllib.request
import urllib.error
from typing import Dict, Optional, Tuple, Callable

from config import APP_VERSION
from utils.app_logger import get_logger

log = get_logger("update_checker")

# رابط فحص التحديثات
VERSION_URL = "https://khalilmebarek-creator.github.io/SmartAccounting/version.json"
FALLBACK_URL = None  # يُحدَّث تلقائياً من config

# لاحقة ملف النسخة الاحتياطية قبل التحديث (لخيار التراجع)
ROLLBACK_SUFFIX = ".previous.exe"


class UpdateChecker:
    """فحص التحديثات المتاحة"""

    def __init__(self, current_version: str = None):
        self.current_version = current_version or APP_VERSION
        self.remote_version = None
        self.changelog = []
        self.download_url = None
        self.installer_url = None
        self.rollout_pct = 100
        self.last_error = None

    def check_for_updates(self, timeout: int = 5) -> Tuple[bool, Optional[Dict]]:
        """
        فحص التحديثات من الإنترنت
        Returns: (has_update, version_info)
        """
        self.last_error = None
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
                    self.rollout_pct = int(data.get("rollout", 100) or 100)

                    has_update = self._compare_versions(
                        self.remote_version, self.current_version
                    )

                    log.info(
                        f"Update check: current={self.current_version}, "
                        f"remote={self.remote_version}, has_update={has_update}, "
                        f"rollout={self.rollout_pct}%"
                    )

                    self.last_error = None
                    return has_update, data

            except urllib.error.HTTPError as e:
                self.last_error = {
                    "url": url, "type": "http",
                    "status": e.code, "error": str(e),
                }
                log.warning(f"HTTP {e.code} checking {url}")
                continue
            except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
                self.last_error = {
                    "url": url, "type": "network", "status": None, "error": str(e),
                }
                log.debug(f"Failed to check {url}: {e}")
                continue
            except Exception as e:
                self.last_error = {
                    "url": url, "type": "unknown", "status": None, "error": str(e),
                }
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

    def is_rollout_eligible(self) -> bool:
        """توزيع تدريجي: هل هذا الجهاز مؤهل لعرض التحديث؟
        مبني على hash ثابت (مستخدم+جهاز) حتى لا يتردد القرار بين الجلسات."""
        pct = int(self.rollout_pct if self.rollout_pct is not None else 100)
        if pct >= 100:
            return True
        if pct <= 0:
            return False
        seed = f"{getpass.getuser()}@{socket.gethostname()}"
        bucket = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16) % 100 + 1
        return bucket <= pct

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
            "rollout_pct": self.rollout_pct,
            "eligible": self.is_rollout_eligible(),
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


def download_installer(
    installer_url: str,
    progress_callback: Callable = None,
    output_path: str = None,
    chunk_size: int = 8192,
) -> Optional[str]:
    """
    تحميل ملف التثبيت مع إظهار التقدم
    progress_callback: دالة تستقبل (downloaded_bytes, total_bytes)
    output_path: مسار الحفظ (اختياري — افتراضياً Temp)
    Returns: مسار الملف المحمل أو None عند الفشل
    """
    path = None
    f = None
    ok = False
    try:
        req = urllib.request.Request(
            installer_url,
            headers={"User-Agent": "SmartAccounting/updater"},
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0

            if output_path:
                path = output_path
                f = open(path, "wb")
            else:
                suffix = ".exe" if ".exe" in installer_url else ".zip"
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                path = tmp.name
                f = tmp

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback:
                    progress_callback(downloaded, total)

            ok = True
            log.info(f"Downloaded installer: {path} ({downloaded} bytes)")
            return path

    except Exception as e:
        log.error(f"Download failed: {e}")
        return None

    finally:
        if f is not None:
            try:
                f.close()
            except Exception:
                pass
            if not ok and path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


def _default_executable() -> Optional[str]:
    """مسار exe الحالي (فقط عند التشغيل المُجمّع)."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return None


def backup_current_executable(exe_path: str = None) -> Optional[str]:
    """نسخ احتياطي للإصدار الحالي قبل التحديث (لخيار التراجع)."""
    exe = exe_path or _default_executable()
    if not exe or not os.path.exists(exe):
        return None
    target = exe + ROLLBACK_SUFFIX
    try:
        shutil.copy2(exe, target)
        log.info(f"Rollback backup created: {target}")
        return target
    except Exception as e:
        log.error(f"Failed to backup current exe: {e}")
        return None


def has_rollback_backup(exe_path: str = None) -> bool:
    """هل توجد نسخة احتياطية يمكن التراجع إليها؟"""
    exe = exe_path or _default_executable()
    if not exe:
        return False
    return os.path.exists(exe + ROLLBACK_SUFFIX)


def restore_previous_executable(exe_path: str = None) -> bool:
    """استعادة النسخة السابقة فوق النسخة الحالية."""
    exe = exe_path or _default_executable()
    if not exe:
        return False
    src = exe + ROLLBACK_SUFFIX
    if not os.path.exists(src):
        log.warning("No rollback backup found")
        return False
    try:
        shutil.copy2(src, exe)
        log.info(f"Restored previous executable from {src}")
        return True
    except Exception as e:
        log.error(f"Rollback failed: {e}")
        return False


def cleanup_rollback(exe_path: str = None) -> bool:
    """حذف النسخة الاحتياطية بعد نجاح التحديث."""
    exe = exe_path or _default_executable()
    if not exe:
        return False
    src = exe + ROLLBACK_SUFFIX
    try:
        if os.path.exists(src):
            os.remove(src)
            log.info("Rollback backup cleaned")
        return True
    except Exception as e:
        log.error(f"Cleanup rollback failed: {e}")
        return False
