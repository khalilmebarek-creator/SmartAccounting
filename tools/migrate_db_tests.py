# -*- coding: utf-8 -*-
"""Migrate test DB isolation from old raw-sqlite singleton to SQLAlchemy engine."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [
    "tests/test_database.py",
    "tests/test_integration_database.py",
    "tests/test_integration_performance.py",
    "tests/test_scenarios.py",
    "tests/test_advanced_dashboard.py",
    "tests/test_reference_standards.py",
]

# Block to replace in setup: old references re-init
OLD_SETUP = """        from database import db_connection as db_conn_module
        from database import repository
        from database import repository
        new_db = DatabaseConnection()
        db_conn_module.db = new_db
        db_operations.db = new_db
        db_schema.db = new_db"""

NEW_SETUP = """        from database.engine import dispose_engine
        dispose_engine()"""

# Teardown: replace close_pool via db_conn_module with dispose_engine
OLD_TEARDOWN = """        from database import db_connection as db_conn_module
        db_conn_module.close_pool()"""

NEW_TEARDOWN = """        from database.engine import dispose_engine
        dispose_engine()"""


def fix_file(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    orig = content

    content = content.replace(OLD_SETUP, NEW_SETUP)
    content = content.replace(OLD_TEARDOWN, NEW_TEARDOWN)

    # Handle test_integration_database.py line 332 bare close_pool()
    content = content.replace(
        "        close_pool()\n",
        "        from database.engine import dispose_engine\n        dispose_engine()\n",
    )

    if content != orig:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        return True
    return False


for f in FILES:
    p = os.path.join(ROOT, f)
    if fix_file(p):
        print(f"Updated {f}")
    else:
        print(f"No change: {f}")
