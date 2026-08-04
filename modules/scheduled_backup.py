"""Scheduled automatic backup system."""

import os
import shutil
import json
import threading
from datetime import datetime
from utils.app_logger import get_logger
import config

logger = get_logger("scheduled_backup")

BACKUP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backups"
)
SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backup_settings.json"
)

MAX_BACKUPS = 10

DB_FILE = config.DATABASE_PATH
USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "users.json"
)
VAULT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "vault.enc"
)

DEFAULT_SETTINGS = {
    "enabled": True,
    "interval_minutes": 60,
    "max_backups": MAX_BACKUPS,
    "backup_dir": BACKUP_DIR,
    "include_users": True,
    "include_vault": True,
}


class ScheduledBackup:
    """Automatic backup scheduler using threading.Timer."""

    def __init__(self):
        self._settings = self._load_settings()
        self._timer = None
        self._last_backup = None
        self._backup_count = 0
        self._lock = threading.Lock()
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def _load_settings(self) -> dict:
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return {**DEFAULT_SETTINGS, **json.load(f)}
            except Exception:
                pass
        return dict(DEFAULT_SETTINGS)

    def _save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save backup settings: {e}")

    def start(self):
        if not self._settings.get("enabled", True):
            return
        interval_s = self._settings.get("interval_minutes", 60) * 60
        with self._lock:
            self._stop_timer()
            self._timer = threading.Timer(interval_s, self._on_timer)
            self._timer.daemon = True
            self._timer.start()
        logger.info(f"Scheduled backup started: every {self._settings['interval_minutes']} min")

    def _stop_timer(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _on_timer(self):
        self._run_backup()
        self.start()

    def stop(self):
        with self._lock:
            self._stop_timer()
        logger.info("Scheduled backup stopped")

    def is_running(self) -> bool:
        with self._lock:
            return self._timer is not None

    def _run_backup(self):
        try:
            filename = self._create_backup()
            if filename:
                self._last_backup = datetime.now().isoformat()
                self._backup_count += 1
                self._cleanup_old_backups()
                logger.info(f"Auto-backup completed: {filename}")
        except Exception as e:
            logger.error(f"Auto-backup failed: {e}")

    def _create_backup(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        os.makedirs(backup_path, exist_ok=True)

        if os.path.exists(DB_FILE):
            shutil.copy2(DB_FILE, os.path.join(backup_path, "accounting.db"))

        if self._settings.get("include_users", True) and os.path.exists(USERS_FILE):
            shutil.copy2(USERS_FILE, os.path.join(backup_path, "users.json"))

        if self._settings.get("include_vault", True) and os.path.exists(VAULT_FILE):
            shutil.copy2(VAULT_FILE, os.path.join(backup_path, "vault.enc"))

        meta = {
            "timestamp": timestamp,
            "created": datetime.now().isoformat(),
        }
        meta_path = os.path.join(backup_path, "meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        meta["files"] = sorted(os.listdir(backup_path))
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return backup_name

    def _cleanup_old_backups(self):
        max_bk = self._settings.get("max_backups", MAX_BACKUPS)
        if not os.path.exists(BACKUP_DIR):
            return
        dirs = sorted(
            [d for d in os.listdir(BACKUP_DIR) if d.startswith("backup_")],
            reverse=True
        )
        for old_dir in dirs[max_bk:]:
            old_path = os.path.join(BACKUP_DIR, old_dir)
            try:
                shutil.rmtree(old_path)
                logger.info(f"Removed old backup: {old_dir}")
            except Exception as e:
                logger.error(f"Failed to remove backup {old_dir}: {e}")

    def manual_backup(self) -> str:
        filename = self._create_backup()
        self._cleanup_old_backups()
        return filename

    def get_backups(self) -> list:
        if not os.path.exists(BACKUP_DIR):
            return []
        backups = []
        for d in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if d.startswith("backup_"):
                meta_path = os.path.join(BACKUP_DIR, d, "meta.json")
                meta = {}
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r") as f:
                            meta = json.load(f)
                    except Exception:
                        pass
                backups.append({
                    "name": d,
                    "created": meta.get("created", "unknown"),
                    "files": meta.get("files", []),
                })
        return backups

    def restore_backup(self, backup_name: str) -> bool:
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        if not os.path.exists(backup_path):
            return False

        db_src = os.path.join(backup_path, "accounting.db")
        if os.path.exists(db_src):
            shutil.copy2(db_src, DB_FILE)

        users_src = os.path.join(backup_path, "users.json")
        if os.path.exists(users_src):
            shutil.copy2(users_src, USERS_FILE)

        vault_src = os.path.join(backup_path, "vault.enc")
        if os.path.exists(vault_src):
            shutil.copy2(vault_src, VAULT_FILE)

        logger.info(f"Restored from backup: {backup_name}")
        return True

    def get_settings(self) -> dict:
        return dict(self._settings)

    def update_settings(self, updates: dict):
        self._settings.update(updates)
        self._save_settings()
        if self.is_running():
            self.stop()
            self.start()


scheduled_backup = ScheduledBackup()
