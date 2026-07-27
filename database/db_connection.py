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


class DatabaseConnection:
    """فئة للاتصال بقاعدة البيانات SQLite"""

    def __init__(self):
        self.connection = None
        self.cursor = None
        self._lock = threading.Lock()

    def connect(self):
        for attempt in range(1, DB_RETRY_ATTEMPTS + 1):
            try:
                db_path = config.DATABASE_PATH
                self.connection = sqlite3.connect(db_path, timeout=DB_TIMEOUT)
                self.connection.execute("PRAGMA journal_mode=WAL")
                self.connection.execute("PRAGMA foreign_keys = ON")
                self.cursor = self.connection.cursor()
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
            if self.connection:
                try:
                    self.connection.close()
                except Exception as e:
                    logger.error(f"Disconnect error: {e}")
                finally:
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
