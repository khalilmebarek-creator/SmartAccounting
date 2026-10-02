# اختبارات ذاكرة التنبؤ التكيفي (التعلّم الذاتي)
# ================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import forecast_memory


def test_record_and_get_memory_error():
    """تسجيل خطأ ثم قراءته يعيد القيمة المسجلة"""
    mem = {}
    forecast_memory.record_outcome("profit", "linear", 5.5, memory=mem)
    assert forecast_memory.get_memory_error(mem, "profit", "linear") == 5.5


def test_record_outcome_moving_average():
    """التسجيل المتكرر يستخدم متوسطاً متحركاً (0.7*prev + 0.3*new)"""
    mem = {}
    forecast_memory.record_outcome("revenue", "linear", 10.0, memory=mem)
    forecast_memory.record_outcome("revenue", "linear", 20.0, memory=mem)
    assert forecast_memory.get_memory_error(mem, "revenue", "linear") == round(0.7 * 10.0 + 0.3 * 20.0, 4)


def test_get_memory_error_default_none():
    """غياب السجل يعيد None (الافتراضي)"""
    assert forecast_memory.get_memory_error({}, "profit", "linear") is None


def test_memory_persist_roundtrip(tmp_path):
    """حفظ ثم تحميل من ملف مؤقت يعيد نفس المحتوى"""
    mem = {"profit": {"linear": 3.3, "moving_average": 4.4}}
    path = os.path.join(str(tmp_path), "mem.json")
    assert forecast_memory.save_memory(mem, path=path) is True
    loaded = forecast_memory.load_memory(path=path)
    assert loaded == mem


def test_record_outcome_ignores_infinity():
    """القيمة اللانهائية لا تُسجّل"""
    mem = {}
    forecast_memory.record_outcome("profit", "linear", float("inf"), memory=mem)
    assert "profit" not in mem


def test_get_memory_error_non_dict():
    """ذاكرة غير dict تعيد الافتراضي (None)"""
    assert forecast_memory.get_memory_error(None, "profit", "linear") is None
    assert forecast_memory.get_memory_error([], "profit", "linear", default=9) == 9


def test_save_memory_failure(tmp_path):
    """الكتابة إلى مسار غير صالح تعيد False (بدون انهيار)"""
    assert forecast_memory.save_memory({"a": 1}, path=str(tmp_path)) is False


def test_record_outcome_persists_to_disk(tmp_path):
    """التسجيل بدون تمرير memory يكتب إلى القرص"""
    path = os.path.join(str(tmp_path), "mem.json")
    mem = forecast_memory.record_outcome("profit", "linear", 5.5, path=path)
    assert mem["profit"]["linear"] == 5.5
    assert os.path.isfile(path)
    loaded = forecast_memory.load_memory(path)
    assert loaded["profit"]["linear"] == 5.5
