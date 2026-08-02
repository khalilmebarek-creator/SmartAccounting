import os
import re
import shutil
import sqlite3
import json
from datetime import datetime
from utils.app_logger import get_logger
import config

logger = get_logger("backup")

MAX_BACKUPS = 10


def _sanitize_name(name: str) -> str:
    """Strip to alphanumeric + underscore, must start with letter."""
    clean = re.sub(r'[^a-zA-Z0-9_]', '', name)
    if clean and clean[0].isdigit():
        clean = 't_' + clean
    return clean or 'unknown'


class BackupManager:
    def __init__(self):
        self.db_path = config.DATABASE_PATH

    def backup(self, backup_path):
        try:
            os.makedirs(os.path.dirname(backup_path) or '.', exist_ok=True)
            if os.path.exists(self.db_path):
                # استخدام SQLite Online Backup API للحصول على لقطة متسقة حتى في وضع WAL
                source = sqlite3.connect(self.db_path)
                try:
                    target = sqlite3.connect(backup_path)
                    try:
                        source.backup(target)
                    finally:
                        target.close()
                finally:
                    source.close()
            else:
                conn = sqlite3.connect(backup_path)
                conn.close()
            return (True, backup_path)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return (False, str(e))

    def auto_backup(self, label: str = "pre") -> tuple:
        """Create an automatic timestamped backup."""
        try:
            backup_dir = os.path.join(
                os.path.dirname(self.db_path), "backups"
            )
            os.makedirs(backup_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(backup_dir, f"{label}_{ts}.db")
            result = self.backup(path)
            self._rotate_backups(backup_dir)
            return result
        except Exception as e:
            logger.error(f"Auto-backup failed: {e}")
            return (False, str(e))

    def _rotate_backups(self, backup_dir: str) -> None:
        """Keep only the most recent MAX_BACKUPS backups."""
        try:
            backups = []
            for f in os.listdir(backup_dir):
                if f.endswith(".db"):
                    filepath = os.path.join(backup_dir, f)
                    backups.append((os.path.getmtime(filepath), filepath))
            backups.sort(reverse=True)
            for _, filepath in backups[MAX_BACKUPS:]:
                try:
                    os.remove(filepath)
                    logger.info(f"Removed old backup: {filepath}")
                except OSError as e:
                    logger.warning(f"Failed to remove old backup {filepath}: {e}")
        except Exception as e:
            logger.warning(f"Backup rotation failed: {e}")

    def _is_valid_sqlite(self, path: str) -> bool:
        """تحقق من أن الملف قاعدة SQLite صالحة (رأس سليم + قابل للقراءة)."""
        try:
            with open(path, "rb") as f:
                if f.read(16) != b"SQLite format 3\x00":
                    return False
            conn = sqlite3.connect(path)
            try:
                conn.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()
            finally:
                conn.close()
            return True
        except Exception:
            return False

    def restore(self, backup_path):
        try:
            if not os.path.exists(backup_path):
                return (False, f"Backup file not found: {backup_path}")
            if not self._is_valid_sqlite(backup_path):
                return (False, "Backup file is not a valid SQLite database")
            ok, backup_file = self.auto_backup("pre_restore")
            if ok:
                logger.info(f"Pre-restore backup created: {backup_file}")
            # إغلاق الاتصالات المُجمّعة قبل استبدال الملف (تجنب الأقفال والوهوات القديمة)
            from database.db_connection import close_pool
            close_pool()
            os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)
            shutil.copy2(backup_path, self.db_path)
            return (True, "Database restored successfully")
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return (False, str(e))

    def list_backups(self, directory):
        backups = []
        try:
            for f in os.listdir(directory):
                if f.endswith(".db"):
                    filepath = os.path.join(directory, f)
                    stat = os.stat(filepath)
                    backups.append({
                        "name": f,
                        "size": stat.st_size,
                        "date": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        except Exception as e:
            logger.error(f"List backups failed: {e}")
            return []
        return backups

    def export_all_to_json(self, directory):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            count = 0
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM [{table_name}]")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                json_file = os.path.join(
                    directory, f"{_sanitize_name(table_name)}.json"
                )
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
                count += 1
            return (True, count)
        except Exception as e:
            logger.error(f"Export to JSON failed: {e}")
            return (False, str(e))
        finally:
            if conn:
                conn.close()

    def import_from_json(self, json_file):
        conn = None
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                return (False, "No data found in JSON file")
            table_name = _sanitize_name(
                os.path.splitext(os.path.basename(json_file))[0]
            )
            columns = [_sanitize_name(c) for c in data[0].keys()]
            columns = [c if c else f"col_{i}" for i, c in enumerate(columns)]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            placeholders = ", ".join(["?" for _ in columns])
            cols = ", ".join([f"[{col}]" for col in columns])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS [{table_name}] ({cols})")
            cursor.execute("BEGIN")
            for row in data:
                values = [row.get(col, None) for col in data[0].keys()]
                cursor.execute(
                    f"INSERT INTO [{table_name}] ({cols}) VALUES ({placeholders})",
                    values
                )
            conn.commit()
            return (True, f"Imported {len(data)} rows into {table_name}")
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.error(f"Import from JSON failed: {e}")
            return (False, str(e))
        finally:
            if conn:
                conn.close()
