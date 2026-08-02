# إصلاح ترميز الطرفية على Windows (cp1252) لضمان نجاح الاختبارات
# ===============================================================
# بعض الاختبارات تطبع رموزاً (✅ ❌ 🔄 ...) تفشل على الـ console القديم
# هذا الملف يفعّل UTF-8 تلقائياً عند تشغيل الاختبارات عبر pytest.

import sys


def enable_utf8():
    """إعادة ضبط stdout/stderr على UTF-8 لتجنب UnicodeEncodeError"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


enable_utf8()
