# محرك المزامنة السحابية والنسخ الاحتياطي
# =========================================
# - وجهات مزامنة (مجلدات سحابية مثل Dropbox / OneDrive / Google Drive)
# - دفعة snapshot كاملة للبيانات المالية مع checksum (تشفير اختياري بكلمة مرور)
# - سحب/استرجاع من snapshot أو من ملف نسخة احتياطية
# - نسخ احتياطي تلقائي محلي مع تدوير
# - سجل عمليات المزامنة في قاعدة البيانات

import base64
import hashlib
import json
import os
import tempfile
import time

from database.db_connection import db
from utils.app_logger import get_logger

log = get_logger("cloud_sync")

SYNC_TABLE = "cloud_sync_state"
FORMAT_VERSION = 1
APP_ID = "SmartAccounting"

# إعدادات المزامنة المحفوظة في ملف JSON مستقل
SYNC_SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cloud_sync_settings.json"
)
DEFAULT_BACKUP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "backups"
)
MAX_BACKUPS = 20

# ملح ثابت لمشتقة المفتاح من كلمة المرور
_SALT = b"smart_accounting_sync_v1"


def _derive_key(passphrase):
    return hashlib.pbkdf2_hmac(
        "sha256", (passphrase or "").encode("utf-8"), _SALT, 120000, dklen=32
    )


# ==================== payload encryption (Argon2id, v2) ====================
# Module 2 upgrade: new blobs use Argon2id via commercial/encryption;
# legacy PBKDF2 blobs keep decrypting through the fallback path below.


def encrypt_payload(payload, passphrase):
    """تشفير نص JSON payload بكلمة مرور عبر AES-GCM (Argon2id) → سلسلة base64."""
    from commercial.encryption import encrypt_bytes
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(encrypt_bytes(data, passphrase)).decode("ascii")


def decrypt_payload(encoded, passphrase):
    """فك تشفير نص snapshot إلى payload dict أصلي (يدعم التنسيق القديم)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from commercial.encryption import EncryptionError, decrypt_bytes, is_encrypted_blob
    raw = base64.b64decode(encoded)
    if is_encrypted_blob(raw):
        return json.loads(decrypt_bytes(raw, passphrase).decode("utf-8"))
    iv, ct = raw[:12], raw[12:]
    cipher = AESGCM(_derive_key(passphrase))
    try:
        return json.loads(cipher.decrypt(iv, ct, None).decode("utf-8"))
    except Exception as exc:  # InvalidTag على المفاتيح القديمة الخطأ
        raise EncryptionError("decryption failed: wrong passphrase or tampered data") from exc


def _atomic_write(path, text):
    dir_name = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            log.debug("Failed to remove temp file during cleanup", exc_info=True)
        raise


def _safe_json_read(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error("Failed to read %s: %s", path, e)
        return default


def _build_payload(state):
    """التقاط الحالة الكاملة للبيانات المالية + العملات في payload قابل للنقل."""
    currency = {}
    try:
        from modules.currency import currency_engine
        currency = {
            "base_currency": currency_engine.base_currency,
            "currencies": currency_engine.currencies,
            "rates": currency_engine.rates,
        }
    except Exception as e:
        log.warning("Currency snapshot unavailable: %s", e)
    return {
        "app": APP_ID,
        "format": FORMAT_VERSION,
        "timestamp": time.time(),
        "company_name": state.company_name,
        "company_name_fr": state.company_name_fr,
        "fiscal_year": state.fiscal_year,
        "company_rc": state.company_rc,
        "company_nif": state.company_nif,
        "company_address": state.company_address,
        "company_phone": state.company_phone,
        "company_email": state.company_email,
        "company_legal_form": state.company_legal_form,
        "company_activity_type": state.company_activity_type,
        "company_bank_account": state.company_bank_account,
        "financial_data": state.financial_data,
        "ratios": state.ratios,
        "dupont": state.dupont,
        "working_capital": state.working_capital,
        "audit_result": state.audit_result,
        "tax_data": state.tax_data,
        "tax_summary": state.tax_summary,
        "tax_obligations": state.tax_obligations,
        "scenarios": state.scenarios,
        "currency": currency,
    }


def _apply_payload(state, payload):
    """تطبيق payload على حالة التطبيق الحالية + الحفظ."""
    state.company_name = payload.get("company_name", state.company_name)
    state.company_name_fr = payload.get("company_name_fr", state.company_name_fr)
    state.fiscal_year = payload.get("fiscal_year", state.fiscal_year)
    state.company_rc = payload.get("company_rc", state.company_rc)
    state.company_nif = payload.get("company_nif", state.company_nif)
    state.company_address = payload.get("company_address", state.company_address)
    state.company_phone = payload.get("company_phone", state.company_phone)
    state.company_email = payload.get("company_email", state.company_email)
    state.company_legal_form = payload.get("company_legal_form", state.company_legal_form)
    state.company_activity_type = payload.get("company_activity_type", state.company_activity_type)
    state.company_bank_account = payload.get("company_bank_account", state.company_bank_account)
    state.financial_data = payload.get("financial_data", state.financial_data)
    state.ratios = payload.get("ratios", state.ratios)
    state.dupont = payload.get("dupont", state.dupont)
    state.working_capital = payload.get("working_capital", state.working_capital)
    state.audit_result = payload.get("audit_result", state.audit_result)
    state.tax_data = payload.get("tax_data", state.tax_data)
    state.tax_summary = payload.get("tax_summary", state.tax_summary)
    state.tax_obligations = payload.get("tax_obligations", state.tax_obligations)
    state.scenarios = payload.get("scenarios", state.scenarios)
    currency = payload.get("currency") or {}
    if currency:
        try:
            from modules.currency import currency_engine
            currency_engine.load_from_dict(currency)
        except Exception as e:
            log.warning("Currency restore failed: %s", e)
    state.save_data()
    state.save_settings()
    return True


class CloudSyncEngine:
    """محرك المزامنة السحابية والنسخ الاحتياطي المحلي"""

    def __init__(self, store=None):
        self._store = store  # بديل DatabaseConnection للاختبارات (اختياري)
        self._settings = None

    def _conn(self):
        """إرجاع اتصال السجل (المخزن المخصص أو اتصال التطبيق)."""
        if self._store is not None:
            return self._store
        if db.connection is None:
            try:
                db.connect()
            except Exception as e:
                log.error("DB connect failed for sync store: %s", e)
        return db

    # ==================== الإعدادات ====================

    def _load_settings(self):
        if self._settings is None:
            data = _safe_json_read(SYNC_SETTINGS_FILE, {}) or {}
            self._settings = {
                "destinations": data.get("destinations", []),
                "auto_backup": data.get("auto_backup", False),
                "auto_backup_interval_hours": data.get("auto_backup_interval_hours", 24),
                "max_backups": data.get("max_backups", MAX_BACKUPS),
                "last_auto_backup_at": data.get("last_auto_backup_at", 0),
                "passphrase": data.get("passphrase", ""),
            }
        return self._settings

    def _save_settings(self):
        s = self._settings or self._load_settings()
        try:
            _atomic_write(SYNC_SETTINGS_FILE, json.dumps(
                s, ensure_ascii=False, indent=2
            ))
        except Exception as e:
            log.error("Failed to save sync settings: %s", e)

    def settings(self):
        return dict(self._load_settings())

    def set_setting(self, key, value):
        s = self._load_settings()
        s[key] = value
        self._save_settings()

    def get_passphrase(self):
        s = self._load_settings()
        return s.get("passphrase", "")

    def set_passphrase(self, passphrase):
        self.set_setting("passphrase", passphrase or "")

    # ==================== قاعدة البيانات (السجل) ====================

    def _init_db(self):
        conn = self._conn()
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {SYNC_TABLE} ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "ts REAL NOT NULL,"
            "action TEXT NOT NULL,"
            "destination TEXT DEFAULT '',"
            "status TEXT NOT NULL,"
            "size INTEGER DEFAULT 0,"
            "error TEXT DEFAULT ''"
            ")"
        )

    def _log(self, action, destination, status, size=0, error=""):
        try:
            self._init_db()
            self._conn().execute(
                f"INSERT INTO {SYNC_TABLE} (ts, action, destination, status, size, error)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (time.time(), action, destination or "", status, int(size or 0), error or ""),
            )
        except Exception as e:
            log.error("Failed to log sync event: %s", e)

    def history(self, limit=50):
        try:
            self._init_db()
            rows = self._conn().fetch_all(
                f"SELECT ts, action, destination, status, size, error"
                f" FROM {SYNC_TABLE} ORDER BY ts DESC LIMIT ?",
                (int(limit),),
            )
            return [
                {
                    "ts": r[0], "action": r[1], "destination": r[2],
                    "status": r[3], "size": r[4], "error": r[5],
                }
                for r in rows
            ]
        except Exception as e:
            log.error("Failed to read sync history: %s", e)
            return []

    def clear_history(self):
        try:
            self._init_db()
            self._conn().execute(f"DELETE FROM {SYNC_TABLE}")
        except Exception as e:
            log.error("Failed to clear sync history: %s", e)

    # ==================== الوجهات ====================

    def list_destinations(self):
        return [dict(d) for d in self._load_settings()["destinations"]]

    def add_destination(self, name, path, auto=False):
        s = self._load_settings()
        dest = {
            "id": int(time.time() * 1000),
            "name": name or os.path.basename(os.path.normpath(path)) or "Cloud",
            "path": path,
            "auto": bool(auto),
        }
        s["destinations"].append(dest)
        self._save_settings()
        return dest

    def remove_destination(self, dest_id):
        s = self._load_settings()
        s["destinations"] = [
            d for d in s["destinations"] if d.get("id") != int(dest_id)
        ]
        self._save_settings()

    def set_destination_auto(self, dest_id, auto):
        s = self._load_settings()
        for d in s["destinations"]:
            if d.get("id") == int(dest_id):
                d["auto"] = bool(auto)
                break
        self._save_settings()

    # ==================== snapshot ====================

    def _snapshot_file(self, payload, passphrase=None, dest_name=""):
        raw = json.dumps(payload, ensure_ascii=False)
        wrapper = {
            "app": APP_ID,
            "format": FORMAT_VERSION,
            "timestamp": payload.get("timestamp", time.time()),
            "destination": dest_name,
            "encrypted": bool(passphrase),
            "checksum": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "data": encrypt_payload(payload, passphrase) if passphrase else raw,
        }
        return json.dumps(wrapper, ensure_ascii=False)

    def _write_snapshot(self, directory, payload, passphrase=None, dest_name=""):
        os.makedirs(directory, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        stamp += "_" + str(int((time.time() % 1) * 1000000)).zfill(6)
        filename = f"smart_accounting_snapshot_{stamp}.json"
        path = os.path.join(directory, filename)
        _atomic_write(path, self._snapshot_file(payload, passphrase, dest_name))
        return path

    def read_snapshot(self, path, passphrase=None):
        """قراءة snapshot وتأكيد checksum → payload أو رفع خطأ."""
        with open(path, "r", encoding="utf-8") as f:
            wrapper = json.load(f)
        if wrapper.get("app") != APP_ID:
            raise ValueError("invalid_snapshot")
        if wrapper.get("encrypted"):
            if not passphrase:
                raise ValueError("passphrase_required")
            payload = decrypt_payload(wrapper["data"], passphrase)
            raw = json.dumps(payload, ensure_ascii=False)
        else:
            payload = json.loads(wrapper["data"])
            raw = wrapper["data"]
        if hashlib.sha256(raw.encode("utf-8")).hexdigest() != wrapper.get("checksum"):
            raise ValueError("checksum_mismatch")
        return payload

    def list_snapshots(self, directory):
        if not directory or not os.path.isdir(directory):
            return []
        snaps = []
        for name in os.listdir(directory):
            if name.startswith("smart_accounting_snapshot_") and name.endswith(".json"):
                path = os.path.join(directory, name)
                try:
                    stat = os.stat(path)
                    with open(path, "r", encoding="utf-8") as f:
                        wrapper = json.load(f)
                    snaps.append({
                        "path": path,
                        "name": name,
                        "size": stat.st_size,
                        "timestamp": wrapper.get("timestamp", stat.st_mtime),
                        "encrypted": bool(wrapper.get("encrypted")),
                    })
                except Exception as e:
                    log.warning("Skip unreadable snapshot %s: %s", name, e)
        snaps.sort(key=lambda s: s["timestamp"], reverse=True)
        return snaps

    def _prune(self, directory, keep):
        snaps = self.list_snapshots(directory)
        for snap in snaps[keep:]:
            try:
                os.remove(snap["path"])
                log.info("Pruned old snapshot %s", snap["name"])
            except OSError as e:
                log.error("Failed to prune %s: %s", snap["name"], e)

    # ==================== العمليات ====================

    def push(self, state, dest_id=None, passphrase=None):
        """دفع snapshot إلى وجهة محددة (أو كل الوجهات إذا dest_id None)."""
        destinations = self.list_destinations()
        if dest_id is not None:
            destinations = [d for d in destinations if d.get("id") == int(dest_id)]
        if not destinations:
            return []
        payload = _build_payload(state)
        passphrase = self.get_passphrase() if passphrase is None else passphrase
        results = []
        for dest in destinations:
            try:
                path = self._write_snapshot(
                    dest["path"], payload, passphrase, dest.get("name", "")
                )
                self._prune(dest["path"], MAX_BACKUPS)
                size = os.path.getsize(path)
                self._log("push", dest.get("name"), "ok", size)
                results.append({"dest": dest.get("name"), "ok": True,
                                "path": path, "size": size})
            except Exception as e:
                log.error("Push to %s failed: %s", dest.get("name"), e)
                self._log("push", dest.get("name"), "error", 0, str(e))
                results.append({"dest": dest.get("name"), "ok": False, "error": str(e)})
        return results

    def pull(self, state, dest_id, snapshot_name, passphrase=None):
        """استرجاع snapshot محدد من وجهة → payload (لا يعدّل الحالة)."""
        dest = next(
            (d for d in self.list_destinations() if d.get("id") == int(dest_id)),
            None,
        )
        if not dest:
            raise ValueError("destination_not_found")
        path = os.path.join(dest["path"], snapshot_name)
        passphrase = self.get_passphrase() if passphrase is None else passphrase
        payload = self.read_snapshot(path, passphrase)
        _apply_payload(state, payload)
        self._log("pull", dest.get("name"), "ok")
        return payload

    def backup_local(self, state, passphrase=None):
        """نسخة احتياطية محلية فورية مع تدوير."""
        payload = _build_payload(state)
        passphrase = self.get_passphrase() if passphrase is None else passphrase
        try:
            path = self._write_snapshot(DEFAULT_BACKUP_DIR, payload, passphrase)
            keep = self._load_settings().get("max_backups", MAX_BACKUPS)
            self._prune(DEFAULT_BACKUP_DIR, keep)
            size = os.path.getsize(path)
            self._log("backup", "local", "ok", size)
            return {"path": path, "size": size}
        except Exception as e:
            log.error("Local backup failed: %s", e)
            self._log("backup", "local", "error", 0, str(e))
            raise

    def restore_backup(self, state, snapshot_name, passphrase=None):
        """استرجاع نسخة احتياطية محلية (ينسخ إلى البيانات الحالية)."""
        path = os.path.join(DEFAULT_BACKUP_DIR, snapshot_name)
        passphrase = self.get_passphrase() if passphrase is None else passphrase
        payload = self.read_snapshot(path, passphrase)
        _apply_payload(state, payload)
        self._log("restore", "local", "ok")
        return payload

    def restore_from_file(self, state, path, passphrase=None):
        """استرجاع من ملف snapshot خارجي."""
        passphrase = self.get_passphrase() if passphrase is None else passphrase
        payload = self.read_snapshot(path, passphrase)
        _apply_payload(state, payload)
        self._log("restore", os.path.basename(path), "ok")
        return payload

    # ==================== التلقائي ====================

    def auto_backup_due(self):
        s = self._load_settings()
        if not s.get("auto_backup"):
            return False
        interval = max(1, int(s.get("auto_backup_interval_hours", 24)))
        last = float(s.get("last_auto_backup_at", 0))
        return (time.time() - last) >= interval * 3600

    def run_auto_backup(self, state):
        """تشغيل النسخ التلقائي إذا كان مستحقاً (آمن للاستدعاء من الإقلاع)."""
        if not self.auto_backup_due():
            return None
        try:
            result = self.backup_local(state)
            self.set_setting("last_auto_backup_at", time.time())
            return result
        except Exception as e:
            log.error("Auto backup failed: %s", e)
            return None

    def status(self):
        s = self._load_settings()
        history = self.history(limit=1)
        last_event = history[0] if history else None
        return {
            "destinations": len(s.get("destinations", [])),
            "auto_backup": bool(s.get("auto_backup")),
            "max_backups": int(s.get("max_backups", MAX_BACKUPS)),
            "last_event": last_event,
            "has_passphrase": bool(s.get("passphrase")),
            "backup_dir": DEFAULT_BACKUP_DIR,
        }


cloud_sync_engine = CloudSyncEngine()
