# واجهة الإعدادات
# ================

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox,
    QGroupBox, QMessageBox, QFrame, QSizePolicy, QFileDialog, QFormLayout, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ui.app_state import state
from ui.resources.i18n import t
from modules.email_notifier import email_notifier
from ui.widgets.toast import toast_success, toast_error, toast_warning, toast_info


class SettingsView(QWidget):
    """واجهة الإعدادات"""

    settings_changed = pyqtSignal()
    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(30)

        self._build_header()
        self._build_lang_group()
        self._build_theme_group()
        self._build_ai_group()
        self._build_separator()
        self._build_email_group()
        self._build_backup_group()
        self._build_separator2()
        self._build_reset_group()
        self._build_demo_group()
        self._build_save_bar()


        container.setLayout(self.main_layout)
        scroll.setWidget(container)
        outer.addWidget(scroll)
        self.setLayout(outer)

    def _build_header(self):
        """العنوان"""

        self.title_label = QLabel(t("settings_title"))
        self.title_label.setObjectName("headerTitle")
        self.main_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("settings_subtitle"))
        self.subtitle_label.setObjectName("headerSubtitle")
        self.main_layout.addWidget(self.subtitle_label)

    def _build_lang_group(self):
        """إعدادات اللغة"""

        # === Language Group ===
        self.lang_group = QGroupBox(t("settings_language"))
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(15)
        lang_layout.setContentsMargins(20, 25, 20, 20)

        self.lang_combo_label = QLabel(t("settings_language"))
        self.lang_combo_label.setMinimumWidth(140)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["العربية", "English", "Français"])
        self.lang_combo.setMinimumWidth(200)
        self.lang_combo.setMinimumHeight(36)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_combo_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()

        self.lang_group.setLayout(lang_layout)
        self.main_layout.addWidget(self.lang_group)

    def _build_theme_group(self):
        """إعدادات الثيم"""

        # === Theme Group ===
        self.theme_group = QGroupBox(t("settings_theme"))
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(15)
        theme_layout.setContentsMargins(20, 25, 20, 20)

        self.theme_combo_label = QLabel(t("settings_theme"))
        self.theme_combo_label.setMinimumWidth(140)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([t("settings_theme_light"), t("settings_theme_dark")])
        self.theme_combo.setMinimumWidth(200)
        self.theme_combo.setMinimumHeight(36)
        theme_layout.addWidget(self.theme_combo_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        self.theme_group.setLayout(theme_layout)
        self.main_layout.addWidget(self.theme_group)

    def _build_ai_group(self):
        """إعدادات الذكاء الاصطناعي"""

        # === AI Settings Group ===
        self.ai_group = QGroupBox(t("settings_ai"))
        ai_layout = QVBoxLayout()
        ai_layout.setSpacing(18)
        ai_layout.setContentsMargins(20, 25, 20, 20)

        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.setSpacing(15)
        self.api_key_label = QLabel(t("settings_api_key"))
        self.api_key_label.setMinimumWidth(140)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setMinimumHeight(36)
        api_key_layout.addWidget(self.api_key_label)
        api_key_layout.addWidget(self.api_key_input, 1)
        ai_layout.addLayout(api_key_layout)

        # API URL
        api_url_layout = QHBoxLayout()
        api_url_layout.setSpacing(15)
        self.api_url_label = QLabel(t("settings_api_url"))
        self.api_url_label.setMinimumWidth(140)
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.openai.com/v1/chat/completions")
        self.api_url_input.setMinimumHeight(36)
        api_url_layout.addWidget(self.api_url_label)
        api_url_layout.addWidget(self.api_url_input, 1)
        ai_layout.addLayout(api_url_layout)

        # Model
        model_layout = QHBoxLayout()
        model_layout.setSpacing(15)
        self.model_label = QLabel(t("settings_model"))
        self.model_label.setMinimumWidth(140)
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems([
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
            "deepseek-chat",
        ])
        self.model_combo.setMinimumHeight(36)
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_combo, 1)
        ai_layout.addLayout(model_layout)

        # Toggle show/hide key
        self.toggle_key_btn = QPushButton(t("settings_show_key"))
        self.toggle_key_btn.setFixedWidth(160)
        self.toggle_key_btn.setMinimumHeight(36)
        self.toggle_key_btn.clicked.connect(self.toggle_key_visibility)
        ai_layout.addWidget(self.toggle_key_btn)

        self.ai_group.setLayout(ai_layout)
        self.main_layout.addWidget(self.ai_group)

    def _build_separator(self):
        """الفاصل الأول"""

        # === Separator ===
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setObjectName("separator")
        self.main_layout.addWidget(self.separator)

    def _build_email_group(self):
        """إعدادات البريد"""

        # === Email Configuration ===
        self.email_group = QGroupBox(t("settings_email_config"))
        email_layout = QFormLayout()
        email_layout.setSpacing(18)
        email_layout.setContentsMargins(20, 25, 20, 20)
        email_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.smtp_server_input = QLineEdit(email_notifier.smtp_server)
        self.smtp_server_input.setPlaceholderText("smtp.gmail.com")
        self.smtp_server_input.setMinimumHeight(36)
        email_layout.addRow(t("settings_smtp_server"), self.smtp_server_input)

        self.smtp_port_input = QLineEdit(str(email_notifier.smtp_port))
        self.smtp_port_input.setPlaceholderText("587")
        self.smtp_port_input.setMinimumHeight(36)
        email_layout.addRow(t("settings_smtp_port"), self.smtp_port_input)

        self.sender_email_input = QLineEdit(email_notifier.sender_email)
        self.sender_email_input.setPlaceholderText("alerts@company.com")
        self.sender_email_input.setMinimumHeight(36)
        email_layout.addRow(t("settings_sender_email"), self.sender_email_input)

        self.sender_password_input = QLineEdit(email_notifier.sender_password)
        self.sender_password_input.setEchoMode(QLineEdit.Password)
        self.sender_password_input.setPlaceholderText("••••••••")
        self.sender_password_input.setMinimumHeight(36)
        email_layout.addRow(t("settings_sender_password"), self.sender_password_input)

        self.manager_email_input = QLineEdit(email_notifier.manager_email)
        self.manager_email_input.setPlaceholderText("manager@company.com")
        self.manager_email_input.setMinimumHeight(36)
        email_layout.addRow(t("settings_manager_email"), self.manager_email_input)

        self.email_group.setLayout(email_layout)
        self.main_layout.addWidget(self.email_group)

    def _build_backup_group(self):
        """النسخ الاحتياطي"""

        # === Backup Group ===
        self.backup_group = QGroupBox(t("backup_title"))
        backup_layout = QVBoxLayout()
        backup_layout.setSpacing(15)
        backup_layout.setContentsMargins(20, 25, 20, 20)

        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.setSpacing(15)

        self.backup_btn = QPushButton(t("backup_create"))
        self.backup_btn.setObjectName("primaryBtn")
        self.backup_btn.setMinimumHeight(42)
        self.backup_btn.clicked.connect(self._create_backup)
        backup_btn_layout.addWidget(self.backup_btn)

        self.restore_btn = QPushButton(t("backup_restore"))
        self.restore_btn.setObjectName("secondaryBtn")
        self.restore_btn.setMinimumHeight(42)
        self.restore_btn.clicked.connect(self._restore_backup)
        backup_btn_layout.addWidget(self.restore_btn)

        backup_layout.addLayout(backup_btn_layout)

        json_btn_layout = QHBoxLayout()
        json_btn_layout.setSpacing(15)

        self.export_json_btn = QPushButton(t("backup_export_json"))
        self.export_json_btn.setObjectName("secondaryBtn")
        self.export_json_btn.setMinimumHeight(42)
        self.export_json_btn.clicked.connect(self._export_json)
        json_btn_layout.addWidget(self.export_json_btn)

        self.import_json_btn = QPushButton(t("backup_import_json"))
        self.import_json_btn.setObjectName("secondaryBtn")
        self.import_json_btn.setMinimumHeight(42)
        self.import_json_btn.clicked.connect(self._import_json)
        json_btn_layout.addWidget(self.import_json_btn)

        backup_layout.addLayout(json_btn_layout)
        self.backup_group.setLayout(backup_layout)
        self.main_layout.addWidget(self.backup_group)

    def _build_separator2(self):
        """الفاصل الثاني"""

        # === Separator 2 ===
        self.separator2 = QFrame()
        self.separator2.setFrameShape(QFrame.HLine)
        self.separator2.setObjectName("separator")
        self.main_layout.addWidget(self.separator2)

    def _build_reset_group(self):
        """إعادة تعيين البيانات"""

        # === Reset All Data ===
        self.reset_group = QGroupBox(t("settings_reset_all"))
        reset_layout = QHBoxLayout()
        reset_layout.setSpacing(15)
        reset_layout.setContentsMargins(20, 25, 20, 20)

        self.reset_btn = QPushButton(t("settings_reset_all"))
        self.reset_btn.setObjectName("dangerBtn")
        self.reset_btn.setMinimumHeight(42)
        self.reset_btn.clicked.connect(self._reset_all_data)
        reset_layout.addWidget(self.reset_btn)
        reset_layout.addStretch()

        self.reset_group.setLayout(reset_layout)
        self.main_layout.addWidget(self.reset_group)

    def _build_demo_group(self):
        """البيانات التجريبية"""

        # === Demo Data ===
        self.demo_group = QGroupBox(t("settings_load_demo"))
        demo_layout = QHBoxLayout()
        demo_layout.setSpacing(15)
        demo_layout.setContentsMargins(20, 25, 20, 20)

        self.demo_btn = QPushButton(t("settings_load_demo"))
        self.demo_btn.setMinimumHeight(42)
        self.demo_btn.clicked.connect(self._load_demo_data)
        demo_layout.addWidget(self.demo_btn)
        demo_layout.addStretch()

        self.demo_group.setLayout(demo_layout)
        self.main_layout.addWidget(self.demo_group)

    def _build_save_bar(self):
        """زر الحفظ"""

        # === Save Button ===
        save_layout = QHBoxLayout()
        save_layout.setContentsMargins(0, 10, 0, 0)
        save_layout.addStretch()

        self.save_btn = QPushButton(t("settings_save"))
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.setMinimumWidth(200)
        self.save_btn.setMinimumHeight(48)
        self.save_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_btn)

        self.main_layout.addLayout(save_layout)


    def load_current_settings(self):
        """تحميل الإعدادات الحالية"""
        lang_map = {"ar": "العربية", "en": "English", "fr": "Français"}
        idx = self.lang_combo.findText(lang_map.get(state.language, "English"))
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

        theme_idx = 0 if state.theme == "light" else 1
        self.theme_combo.setCurrentIndex(theme_idx)

        self.api_key_input.setText(state.api_key)
        self.api_url_input.setText(state.api_url)
        idx = self.model_combo.findText(state.model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.setEditText(state.model)

    def on_language_changed(self, index):
        lang_map = {"العربية": "ar", "English": "en", "Français": "fr"}
        lang_text = self.lang_combo.currentText()
        lang_code = lang_map.get(lang_text, "en")
        state.language = lang_code
        state.save_settings()
        self.language_changed.emit(lang_code)
        self.retranslate()

    def save_settings(self):
        """حفظ الإعدادات"""
        lang_text = self.lang_combo.currentText()
        if lang_text == "العربية":
            state.language = "ar"
        elif lang_text == "Français":
            state.language = "fr"
        else:
            state.language = "en"

        theme_text = self.theme_combo.currentText()
        if "فاتح" in theme_text or "Light" in theme_text:
            state.theme = "light"
        else:
            state.theme = "dark"

        state.api_key = self.api_key_input.text().strip()
        state.api_url = self.api_url_input.text().strip() or "https://api.openai.com/v1/chat/completions"
        state.model = self.model_combo.currentText().strip() or "gpt-4o-mini"

        email_notifier.configure(
            self.smtp_server_input.text(),
            self.smtp_port_input.text(),
            self.sender_email_input.text(),
            self.sender_password_input.text(),
            self.manager_email_input.text()
        )

        state.save_settings()
        self.settings_changed.emit()

        toast_success(self, f"✅ {t('settings_save')}")

    def toggle_key_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.toggle_key_btn.setText(t("settings_hide_key"))
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.toggle_key_btn.setText(t("settings_show_key"))

    def retranslate(self):
        self.title_label.setText(t("settings_title"))
        self.subtitle_label.setText(t("settings_subtitle"))
        self.lang_group.setTitle(t("settings_language"))
        self.lang_combo_label.setText(t("settings_language"))
        self.theme_group.setTitle(t("settings_theme"))
        self.theme_combo_label.setText(t("settings_theme"))
        self.ai_group.setTitle(t("settings_ai"))
        self.api_key_label.setText(t("settings_api_key"))
        self.api_url_label.setText(t("settings_api_url"))
        self.model_label.setText(t("settings_model"))
        self.save_btn.setText(t("settings_save"))

        is_key_visible = self.api_key_input.echoMode() == QLineEdit.Normal
        self.toggle_key_btn.setText(
            t("settings_hide_key") if is_key_visible else t("settings_show_key")
        )

        current_theme_idx = self.theme_combo.currentIndex()
        self.theme_combo.clear()
        self.theme_combo.addItems([t("settings_theme_light"), t("settings_theme_dark")])
        self.theme_combo.setCurrentIndex(current_theme_idx)
        self.backup_group.setTitle(t("backup_title"))
        self.backup_btn.setText(t("backup_create"))
        self.restore_btn.setText(t("backup_restore"))
        self.export_json_btn.setText(t("backup_export_json"))
        self.import_json_btn.setText(t("backup_import_json"))
        self.reset_group.setTitle(t("settings_reset_all"))
        self.reset_btn.setText(t("settings_reset_all"))

    def _create_backup(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("backup_create"), "backup.db", "Database Files (*.db)")
        if not path:
            return
        self._run_backup("backup", path)

    def _restore_backup(self):
        reply = QMessageBox.question(
            self, t("confirm"), t("backup_restore_confirm"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, t("backup_restore"), "", "Database Files (*.db)")
        if not path:
            return
        self._run_backup("restore", path)

    def _export_json(self):
        directory = QFileDialog.getExistingDirectory(self, t("backup_export_json"))
        if not directory:
            return
        self._run_backup("export_json", directory)

    def _import_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("backup_import_json"), "", "JSON Files (*.json)")
        if not path:
            return
        self._run_backup("import_json", path)

    def _run_backup(self, action: str, path: str):
        from modules.backup import BackupManager
        bm = BackupManager()
        if action == "backup":
            ok, _ = bm.backup(path)
        elif action == "restore":
            ok, _ = bm.restore(path)
        elif action == "export_json":
            ok, _ = bm.export_all_to_json(path)
        elif action == "import_json":
            ok, _ = bm.import_from_json(path)
        else:
            return
        if ok:
            toast_success(self, t("backup_success"))
        else:
            toast_error(self, t("backup_fail"))

    def _reset_all_data(self):
        reply = QMessageBox.question(
            self, t("confirm"), t("settings_reset_confirm"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        from modules.backup import BackupManager
        bm = BackupManager()
        bm.auto_backup("pre_reset")
        state.clear()
        toast_warning(self, t("settings_reset_success"))

    def _load_demo_data(self):
        reply = QMessageBox.question(
            self, t("confirm"), t("settings_demo_confirm"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        from modules.demo_data import DemoData
        demo = DemoData.get_data()
        state.company_name = demo["company_name"]
        state.fiscal_year = demo["fiscal_year"]
        state.financial_data = demo["financial_data"]
        state.tax_summary = demo["tax_summary"]
        from modules.calculations import CalculationEngine
        from modules.analysis import FinancialAnalyzer
        engine = CalculationEngine()
        state.ratios = engine.calculate_all_ratios(state.financial_data)
        analyzer = FinancialAnalyzer(state.financial_data)
        fd = state.financial_data
        analyzer.dupont_analysis(
            net_income=fd.get('net_income', 0),
            revenue=fd.get('revenue', 0),
            total_assets=fd.get('total_assets', 0),
            equity=fd.get('equity', 0),
        )
        state.dupont = analyzer.analysis_results.get('dupont', {})
        analyzer.working_capital_analysis(
            current_assets=fd.get('current_assets', 0),
            current_liabilities=fd.get('current_liabilities', 0),
            inventory=fd.get('inventory', 0),
        )
        state.working_capital = analyzer.analysis_results.get('working_capital', {})
        toast_success(self, t("settings_demo_success"))
