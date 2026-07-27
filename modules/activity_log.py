"""Enhanced activity log with detailed audit trail."""

import json
import os
import time
import uuid
from datetime import datetime
from collections import deque
from utils.app_logger import get_logger

logger = get_logger("activity_log")

LOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(LOG_DIR, "activity_log.json")
AUDIT_DIR = os.path.join(LOG_DIR, "audit_trails")

MAX_ENTRIES = 500
FLUSH_INTERVAL = 5.0
FLUSH_THRESHOLD = 10

ACTION_CATEGORIES = {
    "auth": "المصادقة",
    "data": "إدخال البيانات",
    "analysis": "التحليل",
    "report": "التقارير",
    "settings": "الإعدادات",
    "user_mgmt": "إدارة المستخدمين",
    "backup": "النسخ الاحتياطي",
    "security": "الأمان",
}


class ActivityLog:
    """Enhanced audit trail with user tracking and change details."""

    def __init__(self):
        self._entries = deque(maxlen=MAX_ENTRIES)
        self._dirty = False
        self._last_flush = time.time()
        self._pending_count = 0
        self._current_user = "system"
        self._load()
        os.makedirs(AUDIT_DIR, exist_ok=True)

    def _load(self):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._entries = deque(data[-MAX_ENTRIES:], maxlen=MAX_ENTRIES)
            except json.JSONDecodeError as e:
                logger.error(f"Corrupted activity log: {e}")
            except Exception as e:
                logger.error(f"Failed to load activity log: {e}")

    def _save(self):
        tmp_path = LOG_FILE + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(list(self._entries), f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, LOG_FILE)
            self._dirty = False
            self._pending_count = 0
            self._last_flush = time.time()
        except Exception as e:
            logger.error(f"Failed to save activity log: {e}")

    def _maybe_flush(self):
        self._pending_count += 1
        now = time.time()
        if (self._pending_count >= FLUSH_THRESHOLD or
                (now - self._last_flush) >= FLUSH_INTERVAL):
            self._save()

    def set_current_user(self, username: str):
        self._current_user = username or "system"

    def flush(self):
        if self._dirty:
            self._save()

    def log(self, action, details="", category="data", user=None,
            old_value=None, new_value=None, ip_address="local"):
        entry = {
            "id": str(uuid.uuid4())[:8],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user or self._current_user,
            "action": action,
            "details": details,
            "category": category,
            "ip": ip_address,
        }
        if old_value is not None:
            entry["old_value"] = str(old_value)
        if new_value is not None:
            entry["new_value"] = str(new_value)
        self._entries.append(entry)
        self._dirty = True
        self._maybe_flush()
        return entry["id"]

    def log_change(self, entity: str, entity_id: str, field: str,
                   old_value, new_value, user=None):
        return self.log(
            action=f"edit_{entity}",
            details=f"Changed {field} for {entity}#{entity_id}",
            category="data",
            user=user,
            old_value=old_value,
            new_value=new_value,
        )

    def log_auth(self, action: str, username: str, success: bool, ip="local"):
        status = "SUCCESS" if success else "FAILED"
        return self.log(
            action=f"auth_{action}_{status.lower()}",
            details=f"{action} for {username}: {status}",
            category="auth",
            user=username,
            ip_address=ip,
        )

    def log_export(self, format_type: str, filename: str, user=None):
        return self.log(
            action="export",
            details=f"Exported {format_type}: {filename}",
            category="report",
            user=user,
        )

    def log_backup(self, action: str, filename: str = ""):
        return self.log(
            action=f"backup_{action}",
            details=f"Backup {action}: {filename}",
            category="backup",
        )

    def get_entries(self, limit=50, category=None, user=None, action=None):
        entries = list(self._entries)
        if category:
            entries = [e for e in entries if e.get("category") == category]
        if user:
            entries = [e for e in entries if e.get("user") == user]
        if action:
            entries = [e for e in entries if action in e.get("action", "")]
        return entries[-limit:]

    def get_summary(self) -> dict:
        entries = list(self._entries)
        summary = {
            "total": len(entries),
            "by_category": {},
            "by_user": {},
            "recent_actions": [],
        }
        for e in entries:
            cat = e.get("category", "other")
            summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1
            usr = e.get("user", "unknown")
            summary["by_user"][usr] = summary["by_user"].get(usr, 0) + 1
        summary["recent_actions"] = [
            {"action": e["action"], "user": e["user"], "time": e["time"]}
            for e in entries[-10:]
        ]
        return summary

    def export_audit_trail(self, filename: str = None) -> str:
        if not filename:
            filename = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(AUDIT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(list(self._entries), f, ensure_ascii=False, indent=2)
        return filepath

    def clear(self):
        self._entries.clear()
        self._save()


activity_log = ActivityLog()
