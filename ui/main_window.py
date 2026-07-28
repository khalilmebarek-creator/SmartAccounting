# النافذة الرئيسية
# =================

import sys
import os

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QLabel, QStatusBar,
    QApplication, QMessageBox, QAction, QFileDialog,
    QShortcut, QDialog, QDialogButtonBox, QFormLayout,
    QPushButton
)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QKeySequence

from ui.views.data_entry import DataEntryView
from ui.views.dashboard import DashboardView
from ui.views.ratios_view import RatiosView
from ui.views.analysis_view import DuPontView
from ui.views.audit_view import AuditView
from ui.views.reports_view import ReportsView
from ui.views.settings_view import SettingsView
from ui.views.chat_view import ChatView
from ui.views.tax_view import TaxView
from ui.views.comparative_view import ComparativeView
from ui.views.cashflow_view import CashFlowView
from ui.views.security_view import SecurityView
from ui.views.zscore_view import ZScoreView
from ui.views.login_view import LoginView
from ui.views.forecasting_view import ForecastingView
from ui.views.budget_view import BudgetView
from ui.views.cost_center_view import CostCenterView
from ui.views.breakeven_view import BreakEvenView
from ui.views.benchmarks_view import BenchmarkView
from ui.views.tax_calendar_view import TaxCalendarView
from ui.views.data_import_view import DataImportView
from ui.views.bank_sync_view import BankSyncView
from ui.widgets.alert_banner import AlertBanner
from modules.activity_log import activity_log
from modules.user_manager import user_manager
from utils.app_logger import get_logger
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t, Translator


class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""

    log = get_logger("main_window")

    def __init__(self):
        super().__init__()
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

    def _show_update_safe(self):
        """عرض رسالة التحديث بأمان من أي thread"""
        try:
            info = getattr(self, '_pending_update_info', None)
            if not info:
                return
            from PyQt5.QtWidgets import QMessageBox
            from config import APP_VERSION
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
                import webbrowser
                webbrowser.open(info.get('download_url', 'https://github.com'))
        except Exception:
            pass

    def _on_update_check_done(self, has_update: bool, info: dict):
        """الاستجابة لفحص التحديثات — من background thread"""
        if has_update and info:
            self._pending_update_info = info
            try:
                from PyQt5.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(
                    self, "_show_update_safe", Qt.QueuedConnection,
                )
            except Exception:
                pass

    def setup_ui(self):
        """إنشاء الواجهة الرئيسية"""
        self.setWindowTitle(t("window_title"))
        self.setGeometry(100, 100, 1440, 880)
        self.setMinimumSize(QSize(1100, 650))
        
        # App icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setLayoutDirection(
            Qt.RightToLeft if state.language == "ar" else Qt.LeftToRight
        )

        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._lazy_views = {}
        self._view_factories = {
            1: ("data_entry", DataEntryView),
            2: ("dashboard", DashboardView),
            3: ("ratios", RatiosView),
            4: ("dupont", DuPontView),
            5: ("audit", AuditView),
            6: ("reports", ReportsView),
            7: ("settings", SettingsView),
            8: ("chat", ChatView),
            9: ("tax", TaxView),
            10: ("comparative", ComparativeView),
            11: ("cashflow", CashFlowView),
            12: ("security", SecurityView),
            13: ("zscore", ZScoreView),
            14: ("forecast", ForecastingView),
            15: ("budget", BudgetView),
            16: ("cost_center", CostCenterView),
            17: ("breakeven", BreakEvenView),
            18: ("benchmarks", BenchmarkView),
            19: ("tax_calendar", TaxCalendarView),
            20: ("data_import", DataImportView),
            21: ("bank_sync", BankSyncView),
        }

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        self.sidebar.setIconSize(QSize(20, 20))

        self.sidebar_items = [
            t("sidebar_data_entry"),
            t("sidebar_dashboard"),
            t("sidebar_ratios"),
            t("sidebar_dupont"),
            t("sidebar_audit"),
            t("sidebar_reports"),
            t("sidebar_settings"),
            t("sidebar_chat"),
            t("sidebar_tax"),
            t("sidebar_comparative"),
            t("sidebar_cashflow"),
            t("sidebar_security"),
            t("sidebar_zscore"),
            t("sidebar_forecast"),
            t("sidebar_budget"),
            t("sidebar_cost_center"),
            t("sidebar_breakeven"),
            t("sidebar_benchmarks"),
            t("sidebar_tax_calendar"),
            t("sidebar_data_import"),
            t("sidebar_bank_sync"),
        ]

        self.sidebar.blockSignals(True)
        self.sidebar.addItems(self.sidebar_items)
        self.sidebar.blockSignals(False)
        self.sidebar.currentRowChanged.connect(self.change_view)

        main_layout.addWidget(self.sidebar)

        self.content = QStackedWidget()
        self.content.setObjectName("contentStack")

        content_wrapper = QVBoxLayout()
        content_wrapper.setContentsMargins(0, 0, 0, 0)
        content_wrapper.setSpacing(0)

        self.alert_banner = AlertBanner()
        self.alert_banner.view_clicked.connect(lambda: self.sidebar.setCurrentRow(11))
        content_wrapper.addWidget(self.alert_banner)
        content_wrapper.addWidget(self.content, 1)

        content_container = QWidget()
        content_container.setLayout(content_wrapper)
        main_layout.addWidget(content_container, 1)

        self.login_view = LoginView()
        self.login_view.login_success.connect(self._on_login_success)

        self.content.addWidget(self.login_view)

        for i in range(1, 22):
            placeholder = QWidget()
            self.content.addWidget(placeholder)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(t("status_ready"))

        self._setup_shortcuts()
        self._setup_auto_save()
        self._setup_theme_toggle()

        self.sidebar.blockSignals(True)
        self.sidebar.setCurrentRow(0)
        self.sidebar.blockSignals(False)
        self.sidebar.hide()
        self.alert_banner.hide()
        self.content.setCurrentIndex(0)

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
        state.theme = "dark" if state.theme == "light" else "light"
        state.save_settings()
        self.apply_theme()

    def _on_login_success(self):
        """After successful login, show main content."""
        user = user_manager.get_current_user()
        self.sidebar.show()
        self.alert_banner.show()
        self.content.setCurrentIndex(1)
        self._get_or_create_view(1)
        self.sidebar.setCurrentRow(0)
        welcome = t("login_logged_in")
        self.status_bar.showMessage(f"{welcome}: {user['display_name']} ({user['role']})")
        self.log.info(f"User logged in: {user['username']} ({user['role']})")
        activity_log.log("login", f"user={user['username']}, role={user['role']}")

    def _do_logout(self):
        user = user_manager.get_current_user()
        username = user["username"] if user else "unknown"
        user_manager.logout()
        self.sidebar.hide()
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
            (t("sidebar_data_entry"), "Ctrl+1"),
            (t("sidebar_dashboard"), "Ctrl+2"),
            (t("sidebar_ratios"), "Ctrl+3"),
            (t("sidebar_dupont"), "Ctrl+4"),
            (t("sidebar_audit"), "Ctrl+5"),
            (t("sidebar_reports"), "Ctrl+6"),
            (t("sidebar_settings"), "Ctrl+7"),
            (t("sidebar_chat"), "Ctrl+8"),
            (t("sidebar_tax"), "Ctrl+9"),
            (t("sidebar_comparative"), "Ctrl+0"),
            (t("sidebar_cashflow"), "Ctrl+Shift+1"),
            (t("sidebar_security"), "Ctrl+Shift+2"),
            (t("sidebar_zscore"), "Ctrl+Shift+3"),
        ]

        for action, key in shortcuts:
            layout.addRow(action, QLabel(f"<b>{key}</b>"))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addRow(buttons)
        dialog.exec_()

    def _setup_shortcuts(self):
        """اختصارات لوحة المفاتيح"""
        QShortcut(QKeySequence("Ctrl+P"), self, self.print_current_view)
        QShortcut(QKeySequence("Ctrl+E"), self, self.export_dashboard_pdf)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.sidebar.setCurrentRow(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.sidebar.setCurrentRow(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.sidebar.setCurrentRow(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.sidebar.setCurrentRow(3))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self.sidebar.setCurrentRow(4))
        QShortcut(QKeySequence("Ctrl+6"), self, lambda: self.sidebar.setCurrentRow(5))
        QShortcut(QKeySequence("Ctrl+7"), self, lambda: self.sidebar.setCurrentRow(6))
        QShortcut(QKeySequence("Ctrl+8"), self, lambda: self.sidebar.setCurrentRow(7))
        QShortcut(QKeySequence("Ctrl+9"), self, lambda: self.sidebar.setCurrentRow(8))
        QShortcut(QKeySequence("Ctrl+0"), self, lambda: self.sidebar.setCurrentRow(9))
        QShortcut(QKeySequence("Ctrl+Shift+1"), self, lambda: self.sidebar.setCurrentRow(10))
        QShortcut(QKeySequence("Ctrl+Shift+2"), self, lambda: self.sidebar.setCurrentRow(11))
        QShortcut(QKeySequence("Ctrl+Shift+3"), self, lambda: self.sidebar.setCurrentRow(12))
        QShortcut(QKeySequence("Ctrl+Shift+4"), self, lambda: self.sidebar.setCurrentRow(13))
        QShortcut(QKeySequence("Ctrl+Shift+5"), self, lambda: self.sidebar.setCurrentRow(14))
        QShortcut(QKeySequence("Ctrl+Shift+6"), self, lambda: self.sidebar.setCurrentRow(15))
        QShortcut(QKeySequence("Ctrl+Shift+7"), self, lambda: self.sidebar.setCurrentRow(16))
        QShortcut(QKeySequence("Ctrl+Shift+8"), self, lambda: self.sidebar.setCurrentRow(17))
        QShortcut(QKeySequence("Ctrl+Shift+9"), self, lambda: self.sidebar.setCurrentRow(18))
        QShortcut(QKeySequence("Ctrl+Shift+0"), self, lambda: self.sidebar.setCurrentRow(19))
        QShortcut(QKeySequence("Ctrl+Shift+A"), self, lambda: self.sidebar.setCurrentRow(20))
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

        settings_menu = menubar.addMenu(t("menu_settings"))
        settings_menu.addAction(self._make_action(
            t("menu_settings"), "Ctrl+,",
            lambda: self.sidebar.setCurrentRow(6)
        ))

        help_menu = menubar.addMenu(t("menu_help"))
        help_menu.addAction(self._make_action(t("menu_about"), slot=self.show_about))
        help_menu.addAction(self._make_action(t("menu_tests"), slot=self.run_tests))

    def create_menu_bar(self):
        """إنشاء شريط القوائم"""
        self._build_menu_items(self.menuBar())

    def _get_or_create_view(self, index):
        if index in self._lazy_views:
            return self._lazy_views[index]
        if index not in self._view_factories:
            return None
        name, cls = self._view_factories[index]
        view = cls()
        self._lazy_views[index] = view

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

    def change_view(self, index):
        """تغيير الواجهة المعروضة"""
        if not hasattr(self, 'content') or self.content is None:
            return
        self._get_or_create_view(index + 1)
        self.content.setCurrentIndex(index + 1)
        current = self.content.currentWidget()
        if current and hasattr(current, 'refresh'):
            current.refresh()

    def on_data_calculated(self):
        """يتم استدعاؤها عند حساب النسب"""
        activity_log.log("ratios_calculated", state.summary())
        self._get_or_create_view(2).refresh()
        self._get_or_create_view(3).refresh()
        self._get_or_create_view(4).refresh()
        self._get_or_create_view(13).load_from_state()
        self.sidebar.setCurrentRow(1)
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

        self.sidebar.blockSignals(True)
        self.sidebar.clear()
        self.sidebar_items = [
            t("sidebar_data_entry"),
            t("sidebar_dashboard"),
            t("sidebar_ratios"),
            t("sidebar_dupont"),
            t("sidebar_audit"),
            t("sidebar_reports"),
            t("sidebar_settings"),
            t("sidebar_chat"),
            t("sidebar_tax"),
            t("sidebar_comparative"),
            t("sidebar_cashflow"),
            t("sidebar_security"),
            t("sidebar_zscore"),
            t("sidebar_forecast"),
            t("sidebar_budget"),
            t("sidebar_cost_center"),
            t("sidebar_breakeven"),
            t("sidebar_benchmarks"),
            t("sidebar_tax_calendar"),
            t("sidebar_data_import"),
            t("sidebar_bank_sync"),
        ]
        self.sidebar.addItems(self.sidebar_items)
        current_idx = self.content.currentIndex()
        self.sidebar.setCurrentRow(current_idx - 1 if current_idx > 0 else 0)
        self.sidebar.blockSignals(False)

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
                QMessageBox.critical(self, t("error"), f"{e}")

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
            import matplotlib.pyplot as plt

            with PdfPages(file_path) as pdf:
                for chart_widget in [
                    self._get_or_create_view(2).chart_ratios,
                    self._get_or_create_view(2).chart_profitability,
                    self._get_or_create_view(2).chart_dupont,
                    self._get_or_create_view(2).chart_balance,
                    self._get_or_create_view(2).chart_expenses,
                ]:
                    fig = chart_widget.figure
                    pdf.savefig(fig, dpi=150, bbox_inches='tight')

            QMessageBox.information(
                self, t("success"),
                f"✅ {t('reports_success')}\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, t("error"), f"{e}")

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
            QMessageBox.warning(
                self, t("tests_title"),
                t("tests_fail")
            )

    def closeEvent(self, event):
        """حفظ البيانات عند إغلاق النافذة"""
        state.save_data()
        event.accept()
