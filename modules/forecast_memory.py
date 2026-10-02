# ذاكرة التنبؤ التكيفي (التعلّم الذاتي)
# ========================================
# تخزين سجل الأداء التراكمي لكل طريقة تنبؤ/مقياس في ملف JSON
# (نفس نمط tax_years/vendor_store) — يتحسّن الاختيار عبر الجلسات.

import json
import os

from utils.app_logger import get_logger

log = get_logger("forecast_memory")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "forecast_memory.json")


def load_memory(path=None):
    """تحميل ذاكرة الأداء. يعيد dict (فارغ عند الغياب/الفساد)."""
    p = path or MEMORY_FILE
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_memory(memory, path=None):
    """حفظ ذاكرة الأداء. يعيد True عند النجاح."""
    p = path or MEMORY_FILE
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        return True
    except OSError as exc:
        log.warning("save_memory failed: %s", exc)
        return False


def get_memory_error(memory, metric, method, default=None):
    """متوسط الخطأ المسجّل لطريقة على مقياس معيّن (None عند الغياب)."""
    if not isinstance(memory, dict):
        return default
    bucket = memory.get(metric)
    if not isinstance(bucket, dict):
        return default
    return bucket.get(method, default)


def record_outcome(metric, method, error, memory=None, path=None):
    """تسجيل خطأ مرصود في الذاكرة كمتوسط متحرك (0.7*prev + 0.3*new).

    عند تمرير `memory` يتم التعديل في الذاكرة المعطاة دون حفظ؛ وإلا
    تُحمَّل الذاكرة من القرص وتُحفظ تلقائياً. يعيد dict الذاكرة النهائي.
    """
    if error is None or error == float("inf"):
        return memory if memory is not None else load_memory(path)

    mem = memory if memory is not None else load_memory(path)
    bucket = mem.setdefault(metric, {})
    prev = bucket.get(method)
    if prev is None:
        bucket[method] = round(float(error), 4)
    else:
        bucket[method] = round(0.7 * float(prev) + 0.3 * float(error), 4)

    if memory is None:
        save_memory(mem, path)
    return mem
