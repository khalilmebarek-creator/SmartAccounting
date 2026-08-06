# نقطة الدخول لواجهة PyQt5
# ===========================

import sys
import os
import traceback
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CRASH_SENTINEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".crash_pending"
)

logger = logging.getLogger("run_ui")


def _global_exception_hook(exc_type, exc_value, exc_tb):
    """Handle uncaught exceptions: log + write crash sentinel for recovery."""
    import time as _time
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.critical("Uncaught exception:\n%s", tb_str)
    try:
        with open(CRASH_SENTINEL, "w", encoding="utf-8") as f:
            f.write(f"timestamp={_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"error_type={exc_type.__name__}\n")
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def _cleanup_crash_sentinel():
    """Remove crash sentinel file if app starts successfully."""
    try:
        if os.path.exists(CRASH_SENTINEL):
            os.remove(CRASH_SENTINEL)
    except Exception:
        pass


def main():
    """تشغيل الواجهة الرسومية"""
    import ctypes
    MUTEX_NAME = "SmartAccountingMutex"
    ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)

    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont

    sys.excepthook = _global_exception_hook

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationVersion("2.5.0")

    from ui.app_state import state
    from ui.resources.i18n import Translator, t
    Translator.set_language(state.language)

    font = QFont("Segoe UI", 10)
    app.setFont(font)
    app.setApplicationName(t("app_name"))

    from ui.main_window import MainWindow
    window = MainWindow()
    window.showMaximized()

    _cleanup_crash_sentinel()

    window.status_bar.showMessage(t("status_ready") + " 🚀")

    _nudge_license_check(window)

    sys.exit(app.exec_())


def _nudge_license_check(window):
    """Show license dialog at expiration, or warning when expiring soon.

    Non-blocking and fully guarded: without a valid pub key or licensing
    package the app must start exactly as before (no regression).
    """
    try:
        from PyQt5.QtCore import QTimer
        from PyQt5.QtWidgets import QMessageBox
        from commercial.licensing.activation import LicenseStore
        from commercial.licensing.expiry import days_remaining
        store = LicenseStore()
        if store.is_read_only():
            from commercial.licensing.license_dialog import LicenseDialog
            QTimer.singleShot(800, lambda: LicenseDialog(window, store=store).exec_())
            return
        state = store.load()
        if state is None or state.expiry is None:
            return
        remaining = days_remaining(state.expiry)
        if 1 <= remaining <= 7:
            from ui.resources.i18n import t
            QTimer.singleShot(1000, lambda: QMessageBox.information(
                window, t("license_expiring_title"),
                t("license_expiring_msg").format(remaining)))
    except Exception:
        pass


if __name__ == "__main__":
    main()
