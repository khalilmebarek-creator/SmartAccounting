# اتصال قاعدة البيانات SQLite
# ===========================

import sqlite3
import threading
import time
from contextlib import contextmanager
import config
from utils.app_logger import get_logger

logger = get_logger("db_connection")

DB_TIMEOUT = 10
DB_RETRY_ATTEMPTS = 3
DB_RETRY_DELAY = 0.5

# تجمّع الاتصالات: path -> sqlite3.Connection
# إعادة استخدام الاتصال بدلاً من فتح/إغلاق لكل عملية (تحسين أداء DB)
_pool = {}
_pool_lock = threading.Lock()


def _is_alive(connection):
    try:
        connection.execute("SELECT 1")
        return True
    except Exception:
        return False


class DatabaseConnection:
    """فئة للاتصال بقاعدة البيانات SQLite"""

    def __init__(self):
        self.connection = None
        self.cursor = None
        self._lock = threading.Lock()

    def connect(self):
        if self.connection is not None:
            return True
        for attempt in range(1, DB_RETRY_ATTEMPTS + 1):
            try:
                db_path = config.DATABASE_PATH
                with _pool_lock:
                    pooled = _pool.get(db_path)
                if pooled is not None and _is_alive(pooled):
                    self.connection = pooled
                    self.cursor = pooled.cursor()
                    return True
                if pooled is not None:
                    with _pool_lock:
                        if _pool.get(db_path) is pooled:
                            del _pool[db_path]
                    try:
                        pooled.close()
                    except Exception:
                        pass
                connection = sqlite3.connect(db_path, timeout=DB_TIMEOUT)
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute("PRAGMA foreign_keys = ON")
                with _pool_lock:
                    _pool[db_path] = connection
                self.connection = connection
                self.cursor = connection.cursor()
                return True
            except Exception as e:
                logger.error(f"Connection failed (attempt {attempt}/{DB_RETRY_ATTEMPTS}): {e}")
                self.connection = None
                self.cursor = None
                if attempt < DB_RETRY_ATTEMPTS:
                    time.sleep(DB_RETRY_DELAY * attempt)
        return False

    def disconnect(self):
        with self._lock:
            self.connection = None
            self.cursor = None

    def execute(self, query, params=None):
        if self.connection is None or self.cursor is None:
            logger.error("Execute called with no active connection")
            return False
        for attempt in range(1, DB_RETRY_ATTEMPTS + 1):
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                self.connection.commit()
                return True
            except sqlite3.OperationalError as e:
                logger.error(f"Execute error (attempt {attempt}): {e}")
                if attempt < DB_RETRY_ATTEMPTS:
                    time.sleep(DB_RETRY_DELAY)
                    try:
                        self.connection.rollback()
                    except Exception:
                        pass
                else:
                    try:
                        self.connection.rollback()
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"Execute error (not retried): {e}")
                try:
                    self.connection.rollback()
                except Exception:
                    pass
                return False
        return False

    def fetch_all(self, query, params=None):
        if self.connection is None or self.cursor is None:
            logger.error("fetch_all called with no active connection")
            return []
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return []

    def fetch_one(self, query, params=None):
        if self.connection is None or self.cursor is None:
            logger.error("fetch_one called with no active connection")
            return None
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"Fetch one error: {e}")
            return None

    def table_exists(self, table_name):
        result = self.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return result is not None

    def row_count(self, table_name):
        if not self.table_exists(table_name):
            return 0
        result = self.fetch_one(f"SELECT COUNT(*) FROM [{table_name}]")
        return result[0] if result else 0


db = DatabaseConnection()


def close_pool():
    """إغلاق كل الاتصالات المُجمّعة (للاختبارات وعند تبديل ملف قاعدة البيانات)"""
    with _pool_lock:
        for connection in list(_pool.values()):
            try:
                connection.close()
            except Exception as e:
                logger.error(f"close_pool error: {e}")
        _pool.clear()
    if db.connection is not None:
        db.connection = None
        db.cursor = None


@contextmanager
def get_connection():
    conn = DatabaseConnection()
    try:
        if conn.connect():
            yield conn
        else:
            raise ConnectionError("Failed to connect to database")
    finally:
        conn.disconnect()
