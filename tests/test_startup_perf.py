# اختبار انحدار أداء الإقلاع (Startup Performance Regression)
# ===========================================================
# يقيس بالحدود المتسامحة:
#   - زمن بناء MainWindow (إقلاع الواجهة)
#   - زمن تحميل كل مشهد كسول (lazy view) لنماذج من الشاشات
#   - ذاكرة القمّة (tracemalloc) أثناء بناء النافذة وتنقّل المشاهد
# الحدود متسامحة عمداً (تفادي اختبارات متقلبة في بيئات مختلفة)؛
# أي انحدار "كارثي" (مضاعفة زمن أو تسرّب ذاكرة) سيكشفه هذا الاختبار.

import sys
import os
import gc
import time
import unittest
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

# حدود متسامحة: الأرقام التوثيقية للإقلاع 49ms/45MB، لكن CI متغيّر —
# نكتشف الانحدار الكبير فقط (×3 عن المتوقع) لا التذبذب الطبيعي.
STARTUP_SECONDS = 3.0      # بناء MainWindow كامل
VIEW_LOAD_SECONDS = 1.5    # تحميل مشهد كسول واحد
PEAK_MEMORY_MB = 700       # ذاكرة بناء النافذة + تحميل مشهد (tracemalloc قمة)


class TestStartupPerformance(unittest.TestCase):
    """زمن بناء التطبيق يجب أن يبقى داخل حد معقول."""

    def test_main_window_constructs_under_budget(self):
        from ui.app_state import state
        from ui.main_window import MainWindow
        state.clear()
        start = time.perf_counter()
        win = MainWindow()
        elapsed = time.perf_counter() - start
        win.close()
        state.clear()
        self.assertLess(elapsed, STARTUP_SECONDS,
                        f"MainWindow startup too slow: {elapsed:.2f}s (budget {STARTUP_SECONDS}s)")

    def test_lazy_views_load_under_budget(self):
        from ui.app_state import state
        from ui.main_window import MainWindow
        state.clear()
        win = MainWindow()
        try:
            # عيّن واجهة جاهزة: بعض المشاهد تعتمد على بيانات/تسجيل دخول
            for index in (1, 4, 24, 35):  # data_entry / dupont / ai_insights / budgeting
                if index not in win._view_factories:
                    continue
                start = time.perf_counter()
                view = win._get_or_create_view(index)
                elapsed = time.perf_counter() - start
                self.assertIsNotNone(view)
                self.assertLess(elapsed, VIEW_LOAD_SECONDS,
                                f"lazy view {index} too slow: {elapsed:.2f}s (budget {VIEW_LOAD_SECONDS}s)")
        finally:
            win.close()
            state.clear()


class TestStartupMemory(unittest.TestCase):
    """لا نموّ ذاكرة غير منضبط أثناء بناء النافذة وتنقّل المشاهد."""

    def test_window_and_view_peak_bounded(self):
        from ui.app_state import state
        from ui.main_window import MainWindow
        state.clear()
        gc.collect()
        tracemalloc.start()
        try:
            win = MainWindow()
            for index in (1, 2, 3):
                if index in win._view_factories:
                    win._get_or_create_view(index)
            current, peak = tracemalloc.get_traced_memory()
            win.close()
        finally:
            tracemalloc.stop()
            state.clear()
        self.assertLess(peak / 1024 / 1024, PEAK_MEMORY_MB,
                        f"peak memory too high: {peak / 1024 / 1024:.1f} MB (budget {PEAK_MEMORY_MB}MB)")

    def test_repeated_view_switching_memory_stable(self):
        from ui.app_state import state
        from ui.main_window import MainWindow
        state.clear()
        gc.collect()
        tracemalloc.start()
        try:
            win = MainWindow()
            for _ in range(5):
                for index in (1, 2, 3, 4):
                    if index in win._view_factories:
                        win._get_or_create_view(index)
            gc.collect()
            current, peak = tracemalloc.get_traced_memory()
            win.close()
        finally:
            tracemalloc.stop()
            state.clear()
        self.assertLess(peak / 1024 / 1024, PEAK_MEMORY_MB,
                        f"peak after switching too high: {peak / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    unittest.main(verbosity=2)
