# النافذة الرئيسية
# =================

import sys
import os

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QLabel, QStatusBar,
    QMessageBox, QAction, QFileDialog, QShortcut,
    QDialog, QDialogButtonBox, QFormLayout, QPushButton,
    QTableWidget, QTabBar,
    QApplication,
)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import (QIcon, QKeySequence, QFont, QColor)

from ui.views.login_view import LoginView
from ui.widgets.alert_banner import AlertBanner
from ui.login_session import load_login_session, clear_saved_password
from modules.activity_log import activity_log
from modules.user_manager import user_manager
from utils.app_logger import get_logger
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t, Translator
from config import APP_VERSION


def _lazy_view_factory(module_name, class_name):
    """إنشاء دالة تُحمّل المشهد عند الطلب فقط (تحميل كسول لتقليل زمن الإقلاع والذاكرة)"""
    def _create_view():
        from importlib import import_module
        module = import_module(module_name)
        return getattr(module, class_name)()
    return _create_view


class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""

    log = get_logger("main_window")
    update_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._pending_update_info = {}
        self.update_ready.connect(self._show_update_safe)
        self.setup_ui()
        self.apply_style()
        self.apply_language()
        self._connect_settings_signals()
        self._check_for_updates()

    def _connect_settings_signals(self):
        """ربط إشارات تغيير الإعدادات
        (تتم الربط بشكل كسول في _get_or_create_view عند إنشاء SettingsView)"""
        pass

    def _check_for_updates(self):
        """فحص التحديثات عند بدء التشغيل"""
        try:
            from modules.update_checker import check_updates_async
            check_updates_async(callback=self._on_update_check_done, timeout=3)
        except Exception:
            pass

    def _show_update_safe(self, info: dict):
        """عرض رسالة التحديث بأمان عبر signal"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("تحديث متاح | Update Available")
            msg.setText(
                f"نسخة جديدة متاحة: {info.get('remote', '')}\n"
                f"النسخة الحالية: {APP_VERSION}\n\n"
                f"التحديثات:\n" + "\n".join(f"• {c}" for c in info.get('changelog', []))
            )
            msg.setInformativeText("هل تريد تحميل التحديث؟")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.Yes:
                self._perform_update(info)
        except Exception:
            pass

    def _perform_update(self, info: dict):
        """تحميل التحديث → تشغيل المثبت → إعادة التشغيل تلقائياً"""
        from PyQt5.QtWidgets import QProgressDialog
        from modules.update_checker import download_installer, backup_current_executable

        installer_url = info.get("installer_url") or info.get("download_url")
        if not installer_url:
            return

        # نسخ احتياطي للإصدار الحالي قبل التحديث (لخيار التراجع)
        try:
            backup_current_executable()
        except Exception:
            pass

        self.close()

        progress = QProgressDialog(
            "جاري تحميل التحديث...\nDownloading update...",
            None, 0, 100
        )
        progress.setWindowTitle("تحديث | Update")
        progress.setWindowModality(2)
        progress.setMinimumWidth(400)
        progress.show()

        class DownloadThread(QThread):
            progress_signal = pyqtSignal(int, int)
            done_signal = pyqtSignal(str)

            def __init__(self, url):
                super().__init__()
                self.url = url

            def run(self):
                def _progress(downloaded, total):
                    self.progress_signal.emit(downloaded, total)
                path = download_installer(self.url, progress_callback=_progress)
                self.done_signal.emit(path if path else "")

        self._dl_thread = DownloadThread(installer_url)
        self._dl_thread.progress_signal.connect(
            lambda d, t: progress.setValue(int(d / max(t, 1) * 100))
        )
        self._dl_thread.done_signal.connect(
            lambda path: self._on_download_done(path, progress)
        )
        self._dl_thread.start()

    def _on_download_done(self, path: str, progress):
        """تشغيل المثبت → إعادة التشغيل بعد التثبيت"""
        progress.close()
        from PyQt5.QtWidgets import QApplication, QMessageBox
        import subprocess, os, sys, uuid

        if not path or not os.path.exists(path):
            QMessageBox.critical(
                self, t("update_error_title"), t("update_error_download")
            )
            QApplication.quit()
            return

        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.argv[0])
            exe_path = os.path.join(exe_dir, "SmartAccounting.exe")
        else:
            exe_path = ""

        bat_path = os.path.join(
            os.environ["TEMP"], f"smart_update_{uuid.uuid4().hex[:8]}.bat"
        )
        with open(bat_path, "w") as f:
            f.write(f'@echo off\n')
            f.write(f'timeout /t 2 /nobreak >nul\n')
            f.write(f'start /wait "" "{path}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART\n')
            if exe_path:
                f.write(f'start "" "{exe_path}"\n')
            f.write(f'del "%~f0"\n')

        vbs_path = os.path.join(
            os.environ["TEMP"], f"smart_update_{uuid.uuid4().hex[:8]}.vbs"
        )
        with open(vbs_path, "w") as f:
            f.write('Set shell = CreateObject("WScript.Shell")\n')
            f.write(f'shell.Run "{bat_path}", 0, False\n')

        subprocess.Popen(
            ["wscript.exe", vbs_path],
            shell=False, creationflags=subprocess.CREATE_NO_WINDOW
        )
        QApplication.quit()

    def _on_update_check_done(self, has_update: bool, info: dict):
        """الاستجابة لفحص التحديثات — من background thread"""
        if has_update and info and info.get("eligible", True):
            self.update_ready.emit(info)

    def _perform_rollback(self):
        """استعادة النسخة السابقة (تراجع) — نسخ احتياطي قبل آخر تحديث"""
        from PyQt5.QtWidgets import QMessageBox, QApplication
        from modules.update_checker import has_rollback_backup

        if not getattr(sys, 'frozen', False):
            QMessageBox.information(
                self, t("update_rollback_title"), t("update_rollback_dev")
            )
            return
        if not has_rollback_backup():
            QMessageBox.information(
                self, t("update_rollback_title"), t("update_rollback_none")
            )
            return

        answer = QMessageBox.question(
            self, t("update_rollback_title"), t("update_rollback_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        import subprocess, uuid
        exe_path = sys.executable
        bat = os.path.join(os.environ["TEMP"], f"smart_rollback_{uuid.uuid4().hex[:8]}.bat")
        with open(bat, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 /nobreak >nul\n")
            f.write(f'copy /Y "{exe_path}.previous.exe" "{exe_path}" >nul\n')
            f.write(f'start "" "{exe_path}"\n')
            f.write("del \"%~f0\"\n")

        vbs = os.path.join(os.environ["TEMP"], f"smart_rollback_{uuid.uuid4().hex[:8]}.vbs")
        with open(vbs, "w") as f:
            f.write('Set shell = CreateObject("WScript.Shell")\n')
            f.write(f'shell.Run "{bat}", 0, False\n')

        subprocess.Popen(
            ["wscript.exe", vbs],
            shell=False, creationflags=subprocess.CREATE_NO_WINDOW
        )
        QApplication.quit()

    def setup_ui(self):
        """إنشاء الواجهة الرئيسية"""
        self.setWindowTitle(t("window_title"))
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(
            min(1200, screen.width()),
            min(800, screen.height()),
        )
        
        # App icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setLayoutDirection(
            Qt.RightToLeft if state.language == "ar" else Qt.LeftToRight
        )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._lazy_views = {}
        self._view_anims = {}
        self._current_allowed_screens = None
        from ui.views.view_registry import VIEW_REGISTRY
        self._view_factories = {
            vid: (name, _lazy_view_factory(module, cls))
            for vid, (name, module, cls) in VIEW_REGISTRY.items()
        }

        self.create_menu_bar()

        # --- Header Bar ---
        self.header_bar = QWidget()
        self.header_bar.setObjectName("headerBar")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 0, 16, 0)
        self.ribbon_toggle = QPushButton("▲")
        self.ribbon_toggle.setObjectName("ribbonToggleBtn")
        self.ribbon_toggle.setFixedSize(28, 28)
        self.ribbon_toggle.setToolTip("إظهار/إخفاء الشريط")
        self.ribbon_toggle.clicked.connect(self._toggle_ribbon)
        self.header_title = QLabel(t("window_title"))
        self.header_title.setObjectName("headerTitle")
        self.header_section = QLabel("")
        self.header_section.setObjectName("headerSub")
        header_layout.addWidget(self.ribbon_toggle)
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.header_section)
        self.header_bar.setLayout(header_layout)
        main_layout.addWidget(self.header_bar)

        # --- Ribbon ---
        self.ribbon_widget = QWidget()
        self.ribbon_widget.setObjectName("ribbonWidget")
        ribbon_layout = QVBoxLayout()
        ribbon_layout.setContentsMargins(0, 0, 0, 0)
        ribbon_layout.setSpacing(0)

        self.ribbon_tabs = QTabBar()
        self.ribbon_tabs.setObjectName("ribbonTabs")
        self.ribbon_tabs.setDrawBase(True)
        self.ribbon_tabs.setExpanding(True)
        self.ribbon_tabs.setUsesScrollButtons(False)

        self.ribbon_panels = QStackedWidget()
        self.ribbon_panels.setObjectName("ribbonPanels")

        ribbon_layout.addWidget(self.ribbon_tabs)
        ribbon_layout.addWidget(self.ribbon_panels)
        self.ribbon_widget.setLayout(ribbon_layout)
        self._build_ribbon()
        self.ribbon_tabs.currentChanged.connect(self.ribbon_panels.setCurrentIndex)
        main_layout.addWidget(self.ribbon_widget)

        # --- Content ---
        self.content = QStackedWidget()
        self.content.setObjectName("contentStack")

        self.alert_banner = AlertBanner()
        self.alert_banner.view_clicked.connect(lambda: self._go_to_view(12))
        main_layout.addWidget(self.alert_banner)
        main_layout.addWidget(self.content, 1)

        self.login_view = LoginView()
        self.login_view.login_success.connect(self._on_login_success)

        self.content.addWidget(self.login_view)

        for _ in range(1, 38):
            placeholder = QWidget()
            self.content.addWidget(placeholder)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(t("status_ready"))
        self.version_label = QLabel(f"v{APP_VERSION}")
        self.version_label.setObjectName("versionLabel")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.status_bar.addPermanentWidget(self.version_label)

        self._setup_shortcuts()
        self._setup_auto_save()
        self._setup_theme_toggle()

        self.alert_banner.hide()
        self.content.setCurrentIndex(0)

        QTimer.singleShot(0, self._try_auto_login)

    def _setup_auto_save(self):
        """Auto-save data every 30 seconds."""
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)

    def _auto_save(self):
        state.save_data()

    def _setup_theme_toggle(self):
        """Add dark/light toggle button in status bar."""
        self.theme_toggle_btn = QPushButton(t("theme_toggle"))
        self.theme_toggle_btn.setObjectName("themeToggleBtn")
        self.theme_toggle_btn.setMaximumHeight(24)
        self.theme_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.theme_toggle_btn.clicked.connect(self._toggle_theme)
        self.status_bar.addPermanentWidget(self.theme_toggle_btn)

    def _toggle_theme(self):
        themes = ["light", "dark", "modern"]
        idx = themes.index(state.theme) if state.theme in themes else 0
        state.theme = themes[(idx + 1) % 3]
        state.save_settings()
        self.apply_theme()

    def _on_login_success(self):
        """After successful login, show main content."""
        user = user_manager.get_current_user()
        self._current_allowed_screens = user_manager.get_allowed_screens(
            user["username"]) if user else None
        self._build_ribbon()
        self.ribbon_widget.show()
        self.alert_banner.show()
        self.content.setCurrentIndex(1)
        self._get_or_create_view(1)
        self._go_to_view(1)
        welcome = t("login_logged_in")
        self.status_bar.showMessage(f"{welcome}: {user['display_name']} ({user['role']})")
        self.log.info(f"User logged in: {user['username']} ({user['role']})")
        activity_log.log("login", f"user={user['username']}, role={user['role']}")

    def _is_view_allowed(self, view_id: int) -> bool:
        """هل الشاشة مسموحة للمستخدم الحالي (None = كل الشاشات)؟"""
        if self._current_allowed_screens is None:
            return True
        return view_id in self._current_allowed_screens

    def _try_auto_login(self):
        """Skip the login screen when a valid remember-me session exists."""
        try:
            email, password = load_login_session()
            if not email or not password:
                return
            ok, _code, _extra = user_manager.login(email, password)
            if ok and not user_manager.needs_password_change():
                self.login_view.login_email.setText(email)
                self._on_login_success()
            elif ok:
                user_manager.logout()
        except Exception as exc:
            self.log.error(f"Auto-login failed: {exc}")

    def _do_logout(self):
        user = user_manager.get_current_user()
        username = user["username"] if user else "unknown"
        user_manager.logout()
        clear_saved_password()
        self._current_allowed_screens = None
        self.ribbon_widget.hide()
        self.alert_banner.hide()
        self.content.setCurrentIndex(0)
        self.login_view.login_error.setText("")
        self.login_view.login_error.setStyleSheet(f"color: {ThemeColors.get('error')}; font-size: 13px;")
        self.log.info(f"User logged out: {username}")
        activity_log.log("logout", f"user={username}")

    def show_shortcuts_dialog(self):
        """Show keyboard shortcuts dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle(t("shortcuts_title"))
        dialog.setMinimumWidth(400)
        layout = QFormLayout(dialog)

        shortcuts = [
            (t("shortcut_calc"), "Ctrl+R"),
            (t("shortcut_save"), "Ctrl+S"),
            (t("shortcut_print"), "Ctrl+P"),
            (t("shortcut_export"), "Ctrl+E"),
            (t("shortcut_settings"), "Ctrl+,"),
            (t("shortcut_quit"), "Ctrl+Q"),
            (t("shortcut_logout"), "Ctrl+L"),
            (t("shortcut_theme"), "Ctrl+T"),
            (t("shortcut_views_title"), "F1"),
        ]

        for action, key in shortcuts:
            layout.addRow(action, QLabel(f"<b>{key}</b>"))

        view_keys = [
            "Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+4", "Ctrl+5",
            "Ctrl+6", "Ctrl+7", "Ctrl+8", "Ctrl+9", "Ctrl+0",
            "Ctrl+Shift+1", "Ctrl+Shift+2", "Ctrl+Shift+3",
            "Ctrl+Shift+4", "Ctrl+Shift+5", "Ctrl+Shift+6",
            "Ctrl+Shift+7", "Ctrl+Shift+8", "Ctrl+Shift+9",
            "Ctrl+Shift+0", "Ctrl+Shift+A",
            "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
            "F10", "F11", "F12",
            "Ctrl+Shift+B", "Ctrl+Shift+C", "Ctrl+Shift+D",
            "Ctrl+Shift+E",
            "Ctrl+Shift+F",
            "Ctrl+Shift+G",
            "Ctrl+Shift+H",
        ]
        labels = [t(f"sidebar_{self._view_factories[vid][0]}") for vid in sorted(self._view_factories)]
        for action, key in zip(labels, view_keys):
            layout.addRow(action, QLabel(f"<b>{key}</b>"))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addRow(buttons)
        dialog.exec_()

    def _setup_shortcuts(self):
        """اختصارات لوحة المفاتيح — تشير لمعرّف الشاشة (1-35) لا صف الشريط"""
        QShortcut(QKeySequence("Ctrl+P"), self, self.print_current_view)
        QShortcut(QKeySequence("Ctrl+E"), self, self.export_dashboard_pdf)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self._go_to_view(1))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self._go_to_view(2))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self._go_to_view(3))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self._go_to_view(4))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self._go_to_view(5))
        QShortcut(QKeySequence("Ctrl+6"), self, lambda: self._go_to_view(6))
        QShortcut(QKeySequence("Ctrl+7"), self, lambda: self._go_to_view(7))
        QShortcut(QKeySequence("Ctrl+8"), self, lambda: self._go_to_view(8))
        QShortcut(QKeySequence("Ctrl+9"), self, lambda: self._go_to_view(9))
        QShortcut(QKeySequence("Ctrl+0"), self, lambda: self._go_to_view(10))
        QShortcut(QKeySequence("Ctrl+Shift+1"), self, lambda: self._go_to_view(11))
        QShortcut(QKeySequence("Ctrl+Shift+2"), self, lambda: self._go_to_view(12))
        QShortcut(QKeySequence("Ctrl+Shift+3"), self, lambda: self._go_to_view(13))
        QShortcut(QKeySequence("Ctrl+Shift+4"), self, lambda: self._go_to_view(14))
        QShortcut(QKeySequence("Ctrl+Shift+5"), self, lambda: self._go_to_view(15))
        QShortcut(QKeySequence("Ctrl+Shift+6"), self, lambda: self._go_to_view(16))
        QShortcut(QKeySequence("Ctrl+Shift+7"), self, lambda: self._go_to_view(17))
        QShortcut(QKeySequence("Ctrl+Shift+8"), self, lambda: self._go_to_view(18))
        QShortcut(QKeySequence("Ctrl+Shift+9"), self, lambda: self._go_to_view(19))
        QShortcut(QKeySequence("Ctrl+Shift+0"), self, lambda: self._go_to_view(20))
        QShortcut(QKeySequence("Ctrl+Shift+A"), self, lambda: self._go_to_view(21))
        QShortcut(QKeySequence("F2"), self, lambda: self._go_to_view(22))
        QShortcut(QKeySequence("F3"), self, lambda: self._go_to_view(23))
        QShortcut(QKeySequence("F4"), self, lambda: self._go_to_view(24))
        QShortcut(QKeySequence("F5"), self, lambda: self._go_to_view(25))
        QShortcut(QKeySequence("F6"), self, lambda: self._go_to_view(26))
        QShortcut(QKeySequence("F7"), self, lambda: self._go_to_view(27))
        QShortcut(QKeySequence("F8"), self, lambda: self._go_to_view(28))
        QShortcut(QKeySequence("F9"), self, lambda: self._go_to_view(29))
        QShortcut(QKeySequence("F10"), self, lambda: self._go_to_view(30))
        QShortcut(QKeySequence("F11"), self, lambda: self._go_to_view(31))
        QShortcut(QKeySequence("F12"), self, lambda: self._go_to_view(32))
        QShortcut(QKeySequence("Ctrl+Shift+B"), self, lambda: self._go_to_view(33))
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, lambda: self._go_to_view(34))
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, lambda: self._go_to_view(35))
        QShortcut(QKeySequence("Ctrl+Shift+E"), self, lambda: self._go_to_view(36))
        QShortcut(QKeySequence("Ctrl+Shift+F"), self, lambda: self._go_to_view(37))
        QShortcut(QKeySequence("Ctrl+Shift+G"), self, lambda: self._go_to_view(38))
        QShortcut(QKeySequence("Ctrl+Shift+H"), self, lambda: self._go_to_view(39))
        QShortcut(QKeySequence("Ctrl+T"), self, self._toggle_theme)
        QShortcut(QKeySequence("F1"), self, self.show_shortcuts_dialog)
        QShortcut(QKeySequence("Ctrl+L"), self, self._do_logout)

    def _make_action(self, text, shortcut=None, slot=None):
        """إنشاء QAction مع إعدادات مشتركة"""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        if slot:
            action.triggered.connect(slot)
        return action

    def _build_menu_items(self, menubar):
        """بناء عناصر شريط القوائم (مستخدم في الإنشاء والتجديد)"""
        file_menu = menubar.addMenu(t("menu_file"))
        file_menu.addAction(self._make_action(t("menu_print"), "Ctrl+P", self.print_current_view))
        file_menu.addAction(self._make_action(t("menu_export_dashboard"), "Ctrl+E", self.export_dashboard_pdf))
        file_menu.addSeparator()
        file_menu.addAction(self._make_action(t("login_logout"), "Ctrl+L", self._do_logout))
        file_menu.addAction(self._make_action(t("menu_exit"), "Ctrl+Q", self.close))

        analysis_menu = menubar.addMenu(t("menu_analysis"))
        analysis_menu.addAction(self._make_action(
            t("menu_calc"), "Ctrl+R",
            lambda: self._get_or_create_view(1).calculate_ratios()
        ))
        analysis_menu.addAction(self._make_action(
            t("menu_save_db"), "Ctrl+S",
            lambda: self._get_or_create_view(1).save_to_db()
        ))

        view_menu = menubar.addMenu(t("menu_view"))
        view_keys = [
            "Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+4", "Ctrl+5",
            "Ctrl+6", "Ctrl+7", "Ctrl+8", "Ctrl+9", "Ctrl+0",
            "Ctrl+Shift+1", "Ctrl+Shift+2", "Ctrl+Shift+3",
            "Ctrl+Shift+4", "Ctrl+Shift+5", "Ctrl+Shift+6",
            "Ctrl+Shift+7", "Ctrl+Shift+8", "Ctrl+Shift+9",
            "Ctrl+Shift+0", "Ctrl+Shift+A",
            "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
            "F10", "F11", "F12",
            "Ctrl+Shift+B", "Ctrl+Shift+C", "Ctrl+Shift+D",
            "Ctrl+Shift+E",
            "Ctrl+Shift+F",
            "Ctrl+Shift+G",
            "Ctrl+Shift+H",
        ]
        view_ids = sorted(self._view_factories.keys())
        for i, vid in enumerate(view_ids):
            label = t(f"sidebar_{self._view_factories[vid][0]}")
            key = view_keys[i] if i < len(view_keys) else None
            view_menu.addAction(self._make_action(
                label, key,
                (lambda v: lambda: self._go_to_view(v))(vid)
            ))
        view_menu.addSeparator()
        view_menu.addAction(self._make_action(t("view_theme"), "Ctrl+T", self._toggle_theme))

        settings_menu = menubar.addMenu(t("menu_settings"))
        settings_menu.addAction(self._make_action(
            t("menu_settings"), "Ctrl+,",
            lambda: self._go_to_view(7)
        ))

        help_menu = menubar.addMenu(t("menu_help"))
        help_menu.addAction(self._make_action(t("menu_guide"), slot=self.show_guide_dialog))
        help_menu.addAction(self._make_action(t("menu_license"), slot=self.show_license_dialog))
        help_menu.addAction(self._make_action(t("menu_about"), slot=self.show_about))
        help_menu.addAction(self._make_action(t("menu_tests"), slot=self.run_tests))
        help_menu.addAction(self._make_action(t("menu_rollback"), slot=self._perform_rollback))

    def show_license_dialog(self):
        """فتح حوار تفعيل الترخيص (Module 1 - Licensing)."""
        from commercial.licensing.license_dialog import LicenseDialog
        LicenseDialog(self).exec_()

    def show_guide_dialog(self):
        """فتح دليل الاستخدام التفاعلي (بدون كود/بنية — للمستخدم النهائي)."""
        from ui.views.guide_view import GuideDialog
        dialog = GuideDialog(self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.show()

    def create_menu_bar(self):
        """إنشاء شريط القوائم"""
        self._build_menu_items(self.menuBar())

    def _normalize_table_rows(self, view):
        """توحيد ارتفاع صفوف الجداول (44px) حسب المعيار الموحد"""
        for table in view.findChildren(QTableWidget):
            table.verticalHeader().setDefaultSectionSize(44)

    def _get_or_create_view(self, index):
        if index in self._lazy_views:
            return self._lazy_views[index]
        if index not in self._view_factories:
            return None
        name, factory = self._view_factories[index]
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(t("status_loading"))
        try:
            view = factory()
        except Exception:
            import traceback as _tb
            self.log.error("Failed to load view %s (index=%d):\n%s",
                           name, index, _tb.format_exc())
            raise
        self._lazy_views[index] = view
        self._normalize_table_rows(view)
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(t("status_ready"))

        if name == "data_entry":
            view.data_calculated.connect(self.on_data_calculated)
        elif name == "settings":
            view.settings_changed.connect(self.on_settings_changed)
        elif name == "dashboard":
            view.export_pdf_clicked.connect(self.export_dashboard_pdf)
        elif name == "tax":
            view.data_changed.connect(self.on_tax_data_changed)

        self.content.removeWidget(self.content.widget(index))
        self.content.insertWidget(index, view)
        self.log.info(f"Lazy-loaded view: {name} (index={index})")
        return view

    # مجموعات الشريط الجانبي: (مفتاح i18n للمجموعة، [معرّفات الشاشات 1-35])
    _RIBBON_TABS = (
        ("nav_group_main", (1, 2, 23)),
        ("nav_group_accounting", (30, 31, 32, 33, 34, 35, 36, 37)),
        ("nav_group_analysis", (3, 4, 10, 11, 13, 14, 15, 16, 25)),
        ("nav_group_reports", (17, 18, 22, 38)),
        ("nav_group_tax", (9, 19)),
        ("nav_group_tools", (8, 24, 5, 6, 20, 21, 26, 27, 39)),
        ("nav_group_system", (7, 12, 28, 29)),
    )

    def _build_ribbon(self):
        """بناء الشريط الأفقي — تبويبات + أزرار أيقونية (تُرشّح حسب صلاحيات المستخدم)"""
        self.ribbon_tabs.blockSignals(True)
        # مسح التبويبات القديمة
        while self.ribbon_tabs.count():
            self.ribbon_tabs.removeTab(0)
        while self.ribbon_panels.count():
            w = self.ribbon_panels.widget(0)
            self.ribbon_panels.removeWidget(w)
            w.deleteLater()
        self.ribbon_view_to_tab = {}
        for tab_idx, (group_key, view_ids) in enumerate(self._RIBBON_TABS):
            allowed_ids = [vid for vid in view_ids if self._is_view_allowed(vid)]
            if not allowed_ids:
                continue
            self.ribbon_tabs.addTab(t(group_key))
            panel = QWidget()
            panel_layout = QHBoxLayout()
            panel_layout.setContentsMargins(8, 4, 8, 4)
            panel_layout.setSpacing(4)
            for vid in allowed_ids:
                name = self._view_factories[vid][0]
                label = t(f"sidebar_{name}")
                icon = label.split(" ", 1)[0] if " " in label else ""
                text = label.split(" ", 1)[1] if " " in label else label
                btn = QPushButton(f"{icon}\n{text}")
                btn.setObjectName("ribbonBtn")
                btn.setMinimumSize(72, 58)
                btn.setMaximumSize(120, 64)
                btn.setFlat(True)
                btn.clicked.connect(lambda checked, v=vid: self._go_to_view(v))
                panel_layout.addWidget(btn)
                self.ribbon_view_to_tab[vid] = tab_idx
            panel_layout.addStretch()
            panel.setLayout(panel_layout)
            self.ribbon_panels.addWidget(panel)
        self.ribbon_tabs.blockSignals(False)

    def _toggle_ribbon(self):
        """إظهار/إخفاء الشريط"""
        visible = self.ribbon_widget.isVisible()
        self.ribbon_widget.setVisible(not visible)
        self.ribbon_toggle.setText("▼" if visible else "▲")

    def _go_to_view(self, view_id):
        """الانتقال لشاشة بمعرّفها وتفعيل التبويب المناسب"""
        if not self._is_view_allowed(view_id):
            self.log.warning("Blocked view %d (not allowed for current user)", view_id)
            return
        tab_idx = self.ribbon_view_to_tab.get(view_id)
        if tab_idx is not None:
            self.ribbon_tabs.setCurrentIndex(tab_idx)
        self._get_or_create_view(view_id)
        self.content.setCurrentIndex(view_id)
        current = self.content.currentWidget()
        if current and hasattr(current, 'refresh'):
            current.refresh()
        self._fade_in_view(current)
        if hasattr(self, 'header_section'):
            name = self._view_factories.get(view_id, ("",))[0]
            self.header_section.setText(t(f"sidebar_{name}"))

    def _fade_in_view(self, widget):
        """انتقال ناعم (تلاشي) عند تغيير الشاشة — بضمانة أمان ضد بقاء الشاشة سوداء"""
        if widget is None:
            return
        try:
            from PyQt5.QtWidgets import QGraphicsOpacityEffect
            from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer

            # إيقاف أي تلاشٍ سابق على نفس الشاشة حتى لا يُتلفف أثناء طيرانه
            # ويبقى التأثير عالقاً عند شفافية منخفضة (شاشة سوداء)
            prev = self._view_anims.pop(id(widget), None)
            if prev is not None:
                prev.stop()
                prev.deleteLater()
            widget.setGraphicsEffect(None)

            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(180)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)

            def _remove():
                # أزل مرجع الأنيميشن وتأثيره فقط إذا ما زال هذا الأنيميشن هو الحالي
                if self._view_anims.get(id(widget)) is anim:
                    self._view_anims.pop(id(widget), None)
                if widget.graphicsEffect() is effect:
                    widget.setGraphicsEffect(None)

            anim.finished.connect(_remove)
            # ضمانة إضافية: حتى لو لم يُبعث finished (جهاز بطيء)، أزل التأثير
            # بعد انتهاء مدة الأنيميشن لضمان عدم بقاء الشاشة سوداء أبداً
            QTimer.singleShot(300, _remove)
            self._view_anims[id(widget)] = anim
            anim.start()
        except Exception:
            pass

    def on_data_calculated(self):
        """يتم استدعاؤها عند حساب النسب"""
        activity_log.log("ratios_calculated", state.summary())
        self._get_or_create_view(2).refresh()
        self._get_or_create_view(3).refresh()
        self._get_or_create_view(4).refresh()
        self._get_or_create_view(13).load_from_state()
        self._go_to_view(2)
        self.status_bar.showMessage(
            f"{t('status_calculated')} | {state.summary()}"
        )
        self._check_fraud_alerts()

    def on_settings_changed(self):
        """عند تغيير الإعدادات"""
        activity_log.log("settings_changed", f"lang={state.language}, theme={state.theme}")
        self.apply_language()
        self.apply_theme()
        for idx, view in self._lazy_views.items():
            if hasattr(view, 'refresh') and idx in (2, 3, 4):
                try:
                    view.refresh()
                except Exception:
                    pass

    def on_tax_data_changed(self):
        """عند تغيير بيانات الضرائب"""
        if state.tax_summary:
            total_taxes = state.tax_summary.get('total_taxes', 0)
            activity_log.log("tax_calculated", f"total_taxes={total_taxes}")
            self.status_bar.showMessage(
                f"💰 {t('tax_total_taxes')}: {total_taxes:,.0f} DZD"
            )
        self._check_fraud_alerts()

    def _check_fraud_alerts(self):
        """Check for new high-severity fraud alerts and show banner."""
        from modules.fraud_detection import fraud_detector
        counts = fraud_detector.get_alert_count()
        if counts.get("high", 0) > 0:
            self.alert_banner.show_alert(
                f"🔴 {counts['high']} {t('security_high_alerts')}"
            )

    def apply_language(self):
        """تطبيق اللغة على كل الواجهات"""
        Translator.set_language(state.language)
        is_rtl = state.language == "ar"
        self.setLayoutDirection(Qt.RightToLeft if is_rtl else Qt.LeftToRight)

        self.setWindowTitle(t("window_title"))

        current_view = self.content.currentIndex()
        self._build_ribbon()
        if current_view > 0:
            self._go_to_view(current_view)

        self._rebuild_menu_bar()

        self.status_bar.showMessage(t("status_ready"))

        for idx in self._lazy_views:
            view = self._lazy_views[idx]
            if hasattr(view, 'retranslate'):
                view.retranslate()
        if hasattr(self, 'login_view') and hasattr(self.login_view, 'retranslate'):
            self.login_view.retranslate()
        if hasattr(self, 'alert_banner') and hasattr(self.alert_banner, 'retranslate'):
            self.alert_banner.retranslate()

    def _rebuild_menu_bar(self):
        """إعادة بناء شريط القوائم"""
        menubar = self.menuBar()
        menubar.clear()
        self._build_menu_items(menubar)

    def apply_theme(self):
        """تطبيق الثيم (modern/dark/light)"""
        if state.theme == "dark":
            style_file = "style_dark.qss"
        elif state.theme == "light":
            style_file = "style.qss"
        else:
            # "modern" أو أي قيمة افتراضية → الثيم العصري
            style_file = "style_modern.qss"

        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'resources', style_file
        )
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())

    def apply_style(self):
        """تطبيق ملف الستايل"""
        self.apply_theme()

    def print_current_view(self):
        """طباعة الواجهة الحالية"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle(t("menu_print"))

        if dialog.exec_() == QPrintDialog.Accepted:
            try:
                from PyQt5.QtGui import QPainter
                painter = QPainter(printer)
                self.content.currentWidget().render(painter)
                painter.end()
                self.status_bar.showMessage(t("print_success"))
            except Exception as e:
                from ui.widgets.messages import show_error
                show_error(
                    self, t("print_failed"),
                    hint_key="hint_print_failed", exc=e
                )

    def export_dashboard_pdf(self):
        """تصدير لوحة التحكم كـ PDF"""
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("dashboard_no_data"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, t("export_dashboard_title"), "dashboard.pdf",
            "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        try:
            from matplotlib.backends.backend_pdf import PdfPages

            with PdfPages(file_path) as pdf:
                for chart_widget in [
                    self._get_or_create_view(2).chart_ratios,
                    self._get_or_create_view(2).chart_profitability,
                    self._get_or_create_view(2).chart_dupont,
                    self._get_or_create_view(2).chart_balance,
                    self._get_or_create_view(2).chart_expenses,
                    self._get_or_create_view(2).chart_radar,
                    self._get_or_create_view(2).chart_zscore,
                    self._get_or_create_view(2).chart_liquidity,
                ]:
                    fig = chart_widget.figure
                    pdf.savefig(fig, dpi=150, bbox_inches='tight')

            QMessageBox.information(
                self, t("success"),
                f"✅ {t('reports_success')}\n{file_path}"
            )
        except Exception as e:
            from ui.widgets.messages import show_error
            show_error(
                self, t("export_failed"),
                hint_key="hint_export_failed", exc=e
            )

    def show_about(self):
        about_html = f"""<h2>{t('about_name')}</h2>
        <p><b>{t('about_version')}</b></p>
        <p><b>{t('about_lang')}</b></p>
        <hr>
        <p><b>{t('about_features')}</b></p>
        <ul>
            <li>{t('about_feat_1')}</li>
            <li>{t('about_feat_2')}</li>
            <li>{t('about_feat_3')}</li>
            <li>{t('about_feat_4')}</li>
            <li>{t('about_feat_5')}</li>
            <li>{t('about_feat_6')}</li>
            <li>{t('about_feat_7')}</li>
            <li>{t('about_feat_8')}</li>
            <li>{t('about_feat_9')}</li>
            <li>{t('about_feat_10')}</li>
            <li>{t('about_feat_11')}</li>
        </ul>
        <p><b>{t('about_developer')}</b></p>
        """
        QMessageBox.about(self, t("about_title"), about_html)

    def run_tests(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, 'tests/run_all_tests.py'],
            capture_output=True, text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        output = result.stdout + result.stderr
        if "OK" in output and result.returncode == 0:
            QMessageBox.information(
                self, t("tests_title"),
                t("tests_success") + "\n\n" +
                (output.split('📊')[1].split('='*70)[0] if '📊' in output else output)
            )
        else:
            from ui.widgets.messages import show_warning
            show_warning(
                self, t("tests_fail"),
                hint_key="hint_tests_failed"
            )

    def closeEvent(self, event):
        """حفظ البيانات عند إغلاق النافذة"""
        state.save_data()
        event.accept()
