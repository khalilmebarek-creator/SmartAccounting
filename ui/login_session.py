"""Login session persistence - remembers last email."""

import json
import os

SESSION_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "login_session.json"
)


def save_login_email(email: str):
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_email": email}, f)
    except Exception:
        pass


def load_login_email() -> str:
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("last_email", "")
    except Exception:
        pass
    return ""


def clear_login_email():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception:
        pass
