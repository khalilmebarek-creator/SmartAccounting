# إدارة إصدارات النظام الجبائي عبر السنوات
# ============================================
# كل سنة لها ملف JSON مستقل (modules/config_years/tax_config_<year>.json)
# الوظائف: قائمة السنوات، تحميل، حفظ، نسخ، حذف، تحقق، استيراد/تصدير JSON

import json
import os
from datetime import datetime

YEAR_PREFIX = "tax_config_"
ACTIVE_POINTER = ".active_year"

YEARS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_years")

# حقول إلزامية للتحقق من سلامة ملف سنة
_REQUIRED_KEYS = ("ibs", "tva", "irg", "cnas", "cnac", "versement_forfaitaire")


class TaxYearError(Exception):
    """خطأ في معالجة ملف سنة جبائية"""
    pass


def _ensure_dir():
    os.makedirs(YEARS_DIR, exist_ok=True)


def year_filename(year):
    """اسم ملف سنة جبائية"""
    return f"{YEAR_PREFIX}{int(year)}.json"


def year_path(year):
    """المسار الكامل لملف سنة"""
    return os.path.join(YEARS_DIR, year_filename(year))


def list_years():
    """قائمة السنوات المتوفرة (تصاعدي). Returns: list[int]"""
    _ensure_dir()
    years = []
    for name in os.listdir(YEARS_DIR):
        if name.startswith(YEAR_PREFIX) and name.endswith(".json"):
            num = name[len(YEAR_PREFIX):-5]
            if num.isdigit():
                years.append(int(num))
    return sorted(years)


def load_year(year):
    """تحميل إعدادات سنة. Returns: dict | None"""
    path = year_path(year)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        data["year"] = int(year)
        return data
    except (OSError, ValueError):
        return None


def save_year(year, config):
    """حفظ إعدادات سنة. Returns: bool"""
    try:
        _ensure_dir()
        data = dict(config) if isinstance(config, dict) else {}
        data["year"] = int(year)
        path = year_path(year)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, ValueError):
        return False


def copy_year(src_year, dst_year, config=None):
    """نسخ إعدادات سنة إلى سنة أخرى. Returns: bool"""
    try:
        src = load_year(src_year) if config is None else config
        if src is None:
            return False
        data = json.loads(json.dumps(src))
        data["year"] = int(dst_year)
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        return save_year(dst_year, data)
    except (OSError, ValueError, TypeError):
        return False


def delete_year(year):
    """حذف سنة (يحافظ على آخر سنة؟). Returns: bool"""
    path = year_path(year)
    if not os.path.isfile(path):
        return False
    try:
        os.remove(path)
        return True
    except OSError:
        return False


def get_active_year(default_year=None):
    """السنة النشطة الحالية. Returns: int | None"""
    if default_year is None:
        default_year = datetime.now().year
    _ensure_dir()
    pointer = os.path.join(YEARS_DIR, ACTIVE_POINTER)
    if os.path.isfile(pointer):
        try:
            with open(pointer, "r", encoding="utf-8") as f:
                value = f.read().strip()
            if value.isdigit():
                return int(value)
        except OSError:
            pass
    return default_year


def set_active_year(year):
    """تبديل السنة النشطة. Returns: bool"""
    try:
        _ensure_dir()
        pointer = os.path.join(YEARS_DIR, ACTIVE_POINTER)
        with open(pointer, "w", encoding="utf-8") as f:
            f.write(str(int(year)))
        return True
    except (OSError, ValueError):
        return False


def validate_year_config(config):
    """تحقق من سلامة إعدادات سنة. Returns: list[str] (أخطاء)"""
    errors = []
    if not isinstance(config, dict):
        return ["config is not a dict"]

    for key in _REQUIRED_KEYS:
        if key not in config:
            errors.append(f"missing key '{key}'")

    irg = config.get("irg", {})
    brackets = irg.get("brackets", [])
    if not brackets:
        errors.append("irg.brackets is empty")
    prev = None
    for b in brackets:
        bmin = b.get("min", 0)
        bmax = b.get("max")
        rate = b.get("rate", 0)
        if not (0.0 <= rate <= 1.0):
            errors.append(f"invalid irg rate {rate}")
        if prev is not None and bmin <= prev:
            errors.append("irg brackets must be strictly increasing")
        if bmax is not None and bmax <= bmin:
            errors.append("irg bracket max must be > min")
        prev = bmin

    for section in ("ibs", "tva"):
        rates = config.get(section, {}).get("rates", {})
        for label, rate in rates.items():
            if not isinstance(rate, (int, float)) or not (0.0 <= float(rate) <= 1.0):
                errors.append(f"{section}.rates.{label} invalid: {rate}")

    vf = config.get("versement_forfaitaire", {})
    for label in ("standard_rate", "construction_rate"):
        rate = vf.get(label, 0)
        if not isinstance(rate, (int, float)) or not (0.0 <= float(rate) <= 1.0):
            errors.append(f"versement_forfaitaire.{label} invalid: {rate}")

    ifu = config.get("ifu", {})
    ifu_rates = ifu.get("rates", {})
    for label, rate in ifu_rates.items():
        if not isinstance(rate, (int, float)) or not (0.0 <= float(rate) <= 1.0):
            errors.append(f"ifu.rates.{label} invalid: {rate}")

    return errors


def export_year_to_json(year):
    """تصدير إعدادات سنة كنص JSON. Returns: str | None"""
    data = load_year(year)
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, indent=2)


def import_year_from_json(text, year=None):
    """استيراد إعدادات سنة من نص JSON. Returns: tuple(dict|None, errors list)"""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None, ["invalid JSON"]
    if not isinstance(data, dict):
        return None, ["expected JSON object"]

    errors = validate_year_config(data)
    if errors:
        return None, errors
    if year is not None:
        data["year"] = int(year)
    return data, []