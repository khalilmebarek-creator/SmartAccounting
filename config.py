# إعدادات المشروع
# ===============

import os

APP_TITLE = "المنصة المحاسبية الذكية"
APP_VERSION = "3.1.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = "accounting_platform.db"
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)

DEFAULT_ADMIN_PASSWORD = os.environ.get("SAP_ADMIN_PASSWORD", "Admin@1234")