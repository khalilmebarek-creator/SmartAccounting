# إدارة اشتراكات البائع (Vendor Store)
# =====================================
# تتبع العملاء + توليد مفاتيح ترخيص موقّعة RSA لكل عميل.
# المفتاح الخاص للبائع في commercial/keys/ (gitignored) — لا يُرفع أبداً.

import json
import os
import uuid
from datetime import datetime

from utils.app_logger import get_logger

log = get_logger("vendor_store")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR_FILE = os.path.join(BASE_DIR, "data", "vendor_clients.json")

_PLACEHOLDER_HWID = "0" * 64


def _load():
    try:
        with open(VENDOR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"clients": []}


def _save(data):
    os.makedirs(os.path.dirname(VENDOR_FILE), exist_ok=True)
    with open(VENDOR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_key(name, tier, days, hardware_id=""):
    """توليد مفتاح ترخيص موقّع لعميل. يعيد سلسلة المفتاح."""
    from commercial.licensing.keygen import _load_or_create_private_key, issue_key
    from commercial.licensing.tier import Tier

    hwid = (hardware_id or "").strip() or _PLACEHOLDER_HWID
    private_pem = _load_or_create_private_key()
    return issue_key(hwid, Tier.parse(tier), int(days), name, private_pem)


def add_client(name, email, tier, days, hardware_id=""):
    """إضافة عميل وتوليد مفتاحه. يعيد السجل الكامل (مع المفتاح)."""
    key = generate_key(name, tier, days, hardware_id)
    record = {
        "id": uuid.uuid4().hex[:8],
        "name": name.strip(),
        "email": email.strip(),
        "tier": tier,
        "days": int(days),
        "hardware_id": (hardware_id or "").strip() or _PLACEHOLDER_HWID,
        "key": key,
        "issued_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    data = _load()
    data["clients"].append(record)
    _save(data)
    log.info("Client added: %s (tier=%s)", record["name"], record["tier"])
    return record


def list_clients():
    """قائمة العملاء (الأحدث أولاً)."""
    clients = _load().get("clients", [])
    return list(reversed(clients))


def delete_client(client_id):
    """حذف عميل بمعرّفه. يعيد True عند النجاح."""
    data = _load()
    before = len(data["clients"])
    data["clients"] = [c for c in data["clients"] if c.get("id") != client_id]
    _save(data)
    return len(data["clients"]) < before
