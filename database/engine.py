# محرك SQLAlchemy Core
# ====================

from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from utils.app_logger import get_logger
import config

logger = get_logger("sa_engine")

_engine = None
_engine_path = None

def get_engine():
    global _engine, _engine_path
    current_path = config.DATABASE_PATH
    if _engine is not None and _engine_path == current_path:
        return _engine
    if _engine is not None:
        _engine.dispose()
    _engine = create_engine(
        f"sqlite:///{current_path}",
        connect_args={"timeout": 10},
        poolclass=StaticPool,
        echo=False,
    )
    _engine_path = current_path
    @event.listens_for(_engine, "connect")
    def _set_pragmas(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    logger.info("SQLAlchemy engine created for %s", current_path)
    return _engine

def dispose_engine():
    global _engine, _engine_path
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _engine_path = None
        logger.info("SQLAlchemy engine disposed")
