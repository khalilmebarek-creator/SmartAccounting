# Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª Ø§Ù„Ù…Ø´Ø±ÙˆØ¹
# ===============

import os

APP_TITLE = "Ø§Ù„Ù…Ù†ØµØ© Ø§Ù„Ù…Ø­Ø§Ø³Ø¨ÙŠØ© Ø§Ù„Ø°ÙƒÙŠØ©"
APP_VERSION = "3.2.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = "accounting_platform.db"
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)

DEFAULT_ADMIN_PASSWORD = os.environ.get("SAP_ADMIN_PASSWORD", "") or "change_me_on_first_login"