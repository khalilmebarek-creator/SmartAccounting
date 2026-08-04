# نموذج إدخال البيانات المالية
# ================================

import re

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QSpinBox,
    QPushButton, QGroupBox, QMessageBox, QFileDialog,
    QComboBox, QScrollArea,
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QSize, QThread,
)
from PyQt5.QtGui import (QDragEnterEvent, QDropEvent)

from modules import CalculationEngine, DataValidator
from modules.fraud_detection import fraud_detector
from ui.widgets.loading_overlay import LoadingOverlay
from modules.email_notifier import email_notifier
from modules.activity_log import activity_log
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from ui.widgets.toast import toast_success, toast_error, toast_warning, toast_info
from ui.widgets.undo_redo import UndoRedoStack

MAX_TEXT_LENGTH = 200


class _BackgroundCheckWorker(QThread):
    """Worker لتشغيل فحص الاحتيال والإيميل في خيط منفصل"""
    finished = pyqtSignal(list)

    def __init__(self, data, previous_data):
        super().__init__()
        self.data = data
        self.previous_data = previous_data

    def run(self):
        new_alerts = []
        for field, value in self.data.items():
            old = self.previous_data.get(field, value)
            if old != value:
                alerts = fraud_detector.check_data_change(field, old, value, user="data_entry")
                new_alerts.extend(alerts)
        bs_alerts = fraud_detector.check_balance_sheet(self.data, user="data_entry")
        new_alerts.extend(bs_alerts)
        for field, value in self.data.items():
            post_audit = fraud_detector.check_after_audit(field, value, user="data_entry")
            new_alerts.extend(post_audit)
        rapid = fraud_detector.check_rapid_edits(user="data_entry")
        new_alerts.extend(rapid)
        self.finished.emit(new_alerts)


def _sanitize_text(text: str) -> str:
    """Remove dangerous characters and trim length."""
    text = text.strip()
    text = re.sub(r'[<>"\';\\]', '', text)
    return text[:MAX_TEXT_LENGTH]


class DataEntryView(QWidget):
    """واجهة إدخال البيانات المالية"""

    # Signals
    data_calculated = pyqtSignal()  # ينطلق بعد الحساب

    def __init__(self):
        super().__init__()
        self._previous_data = {}
        self._undo_stack = UndoRedoStack(max_size=50)
        self.setAcceptDrops(True)
        self.setup_ui()
        if state.financial_data:
            self._load_from_state()
        self._push_undo()

    def setup_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self._build_header(main_layout)
        self._build_company_group(main_layout)
        self._build_balance_group(main_layout)
        self._build_income_group(main_layout)
        self._build_actions_bar(main_layout)

        self._set_spin_tooltips()


        self.validation_label = QLabel()
        self.validation_label.setObjectName("cardSubtitle")
        self.validation_label.setWordWrap(True)
        main_layout.addWidget(self.validation_label)

        main_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        inner = QWidget()
        inner.setLayout(main_layout)
        scroll.setWidget(inner)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.overlay = LoadingOverlay(self)

        self._setup_tab_order()
        self._connect_validation_signals()
    def _build_header(self, main_layout):
        """عنوان الصفحة"""

        # العنوان
        self.title = QLabel(t("data_entry_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("data_entry_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

    def _build_company_group(self, main_layout):
        """معلومات الشركة"""

        # ===== معلومات الشركة =====
        self.company_group = QGroupBox(t("de_company_info"))
        company_layout = QGridLayout()
        company_layout.setSpacing(12)
        company_layout.setContentsMargins(15, 20, 15, 15)

        # Row 0: Company Name AR
        self.company_name_label = QLabel(t("company_name"))
        self.company_name_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_name_label, 0, 0)
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText(t("de_company_placeholder"))
        self.company_name.setMinimumWidth(250)
        company_layout.addWidget(self.company_name, 0, 1)

        self.company_name_fr_label = QLabel(t("company_name_fr"))
        self.company_name_fr_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_name_fr_label, 0, 2)
        self.company_name_fr = QLineEdit()
        self.company_name_fr.setPlaceholderText(t("de_company_placeholder_fr"))
        self.company_name_fr.setMinimumWidth(250)
        company_layout.addWidget(self.company_name_fr, 0, 3)

        # Row 1: Fiscal Year + NIF
        self.fiscal_year_label = QLabel(t("fiscal_year"))
        self.fiscal_year_label.setMinimumWidth(140)
        company_layout.addWidget(self.fiscal_year_label, 1, 0)
        self.fiscal_year = QSpinBox()
        self.fiscal_year.setRange(2000, 2100)
        self.fiscal_year.setValue(2024)
        self.fiscal_year.setMinimumWidth(160)
        self.fiscal_year.setAlignment(Qt.AlignLeft)
        company_layout.addWidget(self.fiscal_year, 1, 1)

        self.company_nif_label = QLabel(t("company_nif"))
        self.company_nif_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_nif_label, 1, 2)
        self.company_nif = QLineEdit()
        self.company_nif.setPlaceholderText(t("company_nif_placeholder"))
        self.company_nif.setMinimumWidth(250)
        company_layout.addWidget(self.company_nif, 1, 3)

        # Row 2: RC + Legal Form
        self.company_rc_label = QLabel(t("company_rc"))
        self.company_rc_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_rc_label, 2, 0)
        self.company_rc = QLineEdit()
        self.company_rc.setPlaceholderText(t("company_rc_placeholder"))
        self.company_rc.setMinimumWidth(250)
        company_layout.addWidget(self.company_rc, 2, 1)

        self.company_legal_form_label = QLabel(t("company_legal_form"))
        self.company_legal_form_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_legal_form_label, 2, 2)
        self.company_legal_form = QComboBox()
        self.company_legal_form.addItems([
            "", "SARL", "SARL-AU", "SAS", "SA", "SNC", "SCS", "SCI", t("de_other")
        ])
        self.company_legal_form.setMinimumWidth(250)
        company_layout.addWidget(self.company_legal_form, 2, 3)

        # Row 3: Activity Type + Bank Account
        self.company_activity_label = QLabel(t("company_activity_type"))
        self.company_activity_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_activity_label, 3, 0)
        self.company_activity = QComboBox()
        self.company_activity.addItems([
            "", t("tax_activity_production"), t("tax_activity_construction"), t("tax_activity_other")
        ])
        self.company_activity.setMinimumWidth(250)
        company_layout.addWidget(self.company_activity, 3, 1)

        self.company_bank_label = QLabel(t("company_bank_account"))
        self.company_bank_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_bank_label, 3, 2)
        self.company_bank = QLineEdit()
        self.company_bank.setPlaceholderText(t("company_bank_placeholder"))
        self.company_bank.setMinimumWidth(250)
        company_layout.addWidget(self.company_bank, 3, 3)

        # Row 4: Address
        self.company_address_label = QLabel(t("company_address"))
        self.company_address_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_address_label, 4, 0)
        self.company_address = QLineEdit()
        self.company_address.setPlaceholderText(t("company_address_placeholder"))
        company_layout.addWidget(self.company_address, 4, 1, 1, 3)

        # Row 5: Phone + Email
        self.company_phone_label = QLabel(t("company_phone"))
        self.company_phone_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_phone_label, 5, 0)
        self.company_phone = QLineEdit()
        self.company_phone.setPlaceholderText(t("company_phone_placeholder"))
        self.company_phone.setMinimumWidth(250)
        company_layout.addWidget(self.company_phone, 5, 1)

        self.company_email_label = QLabel(t("company_email"))
        self.company_email_label.setMinimumWidth(140)
        company_layout.addWidget(self.company_email_label, 5, 2)
        self.company_email = QLineEdit()
        self.company_email.setPlaceholderText(t("company_email_placeholder"))
        self.company_email.setMinimumWidth(250)
        company_layout.addWidget(self.company_email, 5, 3)

        company_layout.setColumnStretch(1, 1)
        company_layout.setColumnStretch(3, 1)

        self.company_group.setLayout(company_layout)
        main_layout.addWidget(self.company_group)

    def _build_balance_group(self, main_layout):
        """بيانات الميزانية"""

        # ===== بيانات الميزانية =====
        self.balance_group = QGroupBox(t("de_balance_sheet"))
        balance_layout = QGridLayout()
        balance_layout.setSpacing(12)
        balance_layout.setContentsMargins(15, 20, 15, 15)

        balance_layout.setColumnStretch(0, 0)
        balance_layout.setColumnStretch(1, 1)
        balance_layout.setColumnStretch(2, 0)
        balance_layout.setColumnStretch(3, 1)
        balance_layout.setColumnStretch(4, 0)
        balance_layout.setColumnStretch(5, 1)

        # Row 1
        self.current_assets_label = QLabel(t("current_assets"))
        self.current_assets_label.setMinimumWidth(120)
        balance_layout.addWidget(self.current_assets_label, 0, 0)
        self.current_assets = self._make_spin()
        self.current_assets.setMinimumWidth(160)
        balance_layout.addWidget(self.current_assets, 0, 1)

        self.inventory_label = QLabel(t("inventory"))
        self.inventory_label.setMinimumWidth(120)
        balance_layout.addWidget(self.inventory_label, 0, 2)
        self.inventory = self._make_spin()
        self.inventory.setMinimumWidth(160)
        balance_layout.addWidget(self.inventory, 0, 3)

        self.current_liabilities_label = QLabel(t("current_liabilities"))
        self.current_liabilities_label.setMinimumWidth(120)
        balance_layout.addWidget(self.current_liabilities_label, 0, 4)
        self.current_liabilities = self._make_spin()
        self.current_liabilities.setMinimumWidth(160)
        balance_layout.addWidget(self.current_liabilities, 0, 5)

        # Row 2
        self.total_assets_label = QLabel(t("total_assets"))
        self.total_assets_label.setMinimumWidth(120)
        balance_layout.addWidget(self.total_assets_label, 1, 0)
        self.total_assets = self._make_spin()
        self.total_assets.setMinimumWidth(160)
        balance_layout.addWidget(self.total_assets, 1, 1)

        self.total_liabilities_label = QLabel(t("total_liabilities"))
        self.total_liabilities_label.setMinimumWidth(120)
        balance_layout.addWidget(self.total_liabilities_label, 1, 2)
        self.total_liabilities = self._make_spin()
        self.total_liabilities.setMinimumWidth(160)
        balance_layout.addWidget(self.total_liabilities, 1, 3)

        self.equity_label = QLabel(t("equity"))
        self.equity_label.setMinimumWidth(120)
        balance_layout.addWidget(self.equity_label, 1, 4)
        self.equity = self._make_spin()
        self.equity.setMinimumWidth(160)
        balance_layout.addWidget(self.equity, 1, 5)

        # Row 3
        self.cash_label = QLabel(t("cash"))
        self.cash_label.setMinimumWidth(120)
        balance_layout.addWidget(self.cash_label, 2, 0)
        self.cash = self._make_spin()
        self.cash.setMinimumWidth(160)
        balance_layout.addWidget(self.cash, 2, 1)

        self.balance_group.setLayout(balance_layout)
        main_layout.addWidget(self.balance_group)

    def _build_income_group(self, main_layout):
        """قائمة الدخل"""

        # ===== قائمة الدخل =====
        self.income_group = QGroupBox(t("de_income_statement"))
        income_layout = QGridLayout()
        income_layout.setSpacing(12)
        income_layout.setContentsMargins(15, 20, 15, 15)

        income_layout.setColumnStretch(0, 0)
        income_layout.setColumnStretch(1, 1)
        income_layout.setColumnStretch(2, 0)
        income_layout.setColumnStretch(3, 1)
        income_layout.setColumnStretch(4, 0)
        income_layout.setColumnStretch(5, 1)

        self.revenue_label = QLabel(t("revenue"))
        self.revenue_label.setMinimumWidth(120)
        income_layout.addWidget(self.revenue_label, 0, 0)
        self.revenue = self._make_spin()
        self.revenue.setMinimumWidth(160)
        income_layout.addWidget(self.revenue, 0, 1)

        self.cogs_label = QLabel(t("de_cogs_short"))
        self.cogs_label.setMinimumWidth(120)
        income_layout.addWidget(self.cogs_label, 0, 2)
        self.cogs = self._make_spin()
        self.cogs.setMinimumWidth(160)
        income_layout.addWidget(self.cogs, 0, 3)

        self.gross_profit_label = QLabel(t("de_gross_profit"))
        self.gross_profit_label.setMinimumWidth(120)
        income_layout.addWidget(self.gross_profit_label, 0, 4)
        self.gross_profit = self._make_spin()
        self.gross_profit.setMinimumWidth(160)
        income_layout.addWidget(self.gross_profit, 0, 5)

        self.net_income_label = QLabel(t("net_income"))
        self.net_income_label.setMinimumWidth(120)
        income_layout.addWidget(self.net_income_label, 1, 0)
        self.net_income = self._make_spin()
        self.net_income.setMinimumWidth(160)
        income_layout.addWidget(self.net_income, 1, 1)

        self.avg_receivables_label = QLabel(t("de_avg_receivables"))
        self.avg_receivables_label.setMinimumWidth(120)
        income_layout.addWidget(self.avg_receivables_label, 1, 2)
        self.avg_receivables = self._make_spin()
        self.avg_receivables.setMinimumWidth(160)
        income_layout.addWidget(self.avg_receivables, 1, 3)

        self.avg_inventory_label = QLabel(t("de_avg_inventory"))
        self.avg_inventory_label.setMinimumWidth(120)
        income_layout.addWidget(self.avg_inventory_label, 1, 4)
        self.avg_inventory = self._make_spin()
        self.avg_inventory.setMinimumWidth(160)
        income_layout.addWidget(self.avg_inventory, 1, 5)

        # Row 2
        self.operating_expenses_label = QLabel(t("de_operating_expenses"))
        self.operating_expenses_label.setMinimumWidth(120)
        income_layout.addWidget(self.operating_expenses_label, 2, 0)
        self.operating_expenses = self._make_spin()
        self.operating_expenses.setMinimumWidth(160)
        income_layout.addWidget(self.operating_expenses, 2, 1)

        self.avg_payables_label = QLabel(t("de_avg_payables"))
        self.avg_payables_label.setMinimumWidth(120)
        income_layout.addWidget(self.avg_payables_label, 2, 2)
        self.avg_payables = self._make_spin()
        self.avg_payables.setMinimumWidth(160)
        income_layout.addWidget(self.avg_payables, 2, 3)

        self.income_group.setLayout(income_layout)
        main_layout.addWidget(self.income_group)

    def _build_actions_bar(self, main_layout):
        """أزرار الإجراءات"""

        # ===== أزرار الإجراءات =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.calculate_btn = QPushButton(t("btn_calculate"))
        self.calculate_btn.setObjectName("primaryBtn")
        self.calculate_btn.setMinimumSize(QSize(160, 42))
        self.calculate_btn.setToolTip(t("tip_calculate"))
        self.calculate_btn.clicked.connect(self.calculate_ratios)
        buttons_layout.addWidget(self.calculate_btn)

        self.save_btn = QPushButton(t("btn_save_db"))
        self.save_btn.setObjectName("successBtn")
        self.save_btn.setMinimumSize(QSize(160, 42))
        self.save_btn.setToolTip(t("tip_save_db"))
        self.save_btn.clicked.connect(self.save_to_db)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton(t("btn_clear"))
        self.clear_btn.setObjectName("dangerBtn")
        self.clear_btn.setMinimumSize(QSize(140, 42))
        self.clear_btn.setToolTip(t("tip_clear"))
        self.clear_btn.clicked.connect(self.clear_fields)
        buttons_layout.addWidget(self.clear_btn)

        self.import_btn = QPushButton(t("btn_import_excel"))
        self.import_btn.setObjectName("secondaryBtn")
        self.import_btn.setMinimumSize(QSize(160, 42))
        self.import_btn.setToolTip(t("tip_import_excel"))
        self.import_btn.clicked.connect(self.import_from_excel)
        buttons_layout.addWidget(self.import_btn)

        self.demo_btn = QPushButton(t("btn_load_demo"))
        self.demo_btn.setObjectName("secondaryBtn")
        self.demo_btn.setMinimumSize(QSize(160, 42))
        self.demo_btn.setToolTip(t("tip_load_demo"))
        self.demo_btn.clicked.connect(self.load_default_data)
        buttons_layout.addWidget(self.demo_btn)

        buttons_layout.addSpacing(20)

        self.undo_btn = QPushButton("↩ Undo")
        self.undo_btn.setObjectName("secondaryBtn")
        self.undo_btn.setMinimumSize(QSize(80, 36))
        self.undo_btn.setToolTip("Ctrl+Z")
        self.undo_btn.clicked.connect(self._undo)
        buttons_layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("↪ Redo")
        self.redo_btn.setObjectName("secondaryBtn")
        self.redo_btn.setMinimumSize(QSize(80, 36))
        self.redo_btn.setToolTip("Ctrl+Y")
        self.redo_btn.clicked.connect(self._redo)
        buttons_layout.addWidget(self.redo_btn)

        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)

    def _setup_tab_order(self):
        fields = [
            self.company_name, self.company_name_fr,
            self.fiscal_year, self.company_nif,
            self.company_rc, self.company_legal_form,
            self.company_activity, self.company_bank,
            self.company_address, self.company_phone,
            self.company_email,
            self.current_assets, self.inventory,
            self.current_liabilities, self.cash,
            self.total_assets, self.total_liabilities, self.equity,
            self.revenue, self.cogs,
            self.gross_profit, self.operating_expenses,
            self.net_income, self.avg_receivables,
            self.avg_inventory, self.avg_payables,
        ]
        for i in range(len(fields) - 1):
            self.setTabOrder(fields[i], fields[i + 1])

    def _make_spin(self):
        """إنشاء spin box للأرقام المالية"""
        spin = QDoubleSpinBox()
        spin.setRange(0, 1_000_000_000)
        spin.setDecimals(2)
        spin.setSingleStep(1000)
        spin.setAlignment(Qt.AlignLeft)
        spin.setGroupSeparatorShown(True)
        # لا تُعرض "0.00" قبل أن يدخل المستخدم رقماً (تُعرض تسمية الإدخال مكانها)
        spin.setSpecialValueText(t("de_enter_amount"))
        return spin

    def _set_spin_tooltips(self):
        """تعيين tooltips لحقول الأرقام المالية"""
        tips = {
            self.current_assets: "tip_current_assets",
            self.inventory: "tip_inventory",
            self.current_liabilities: "tip_current_liabilities",
            self.cash: "tip_cash",
            self.total_assets: "tip_total_assets",
            self.total_liabilities: "tip_total_liabilities",
            self.equity: "tip_equity",
            self.revenue: "tip_revenue",
            self.cogs: "tip_cogs",
            self.gross_profit: "tip_gross_profit",
            self.operating_expenses: "tip_operating_expenses",
            self.net_income: "tip_net_income",
            self.avg_receivables: "tip_avg_receivables",
            self.avg_inventory: "tip_avg_inventory",
            self.avg_payables: "tip_avg_payables",
        }
        for widget, key in tips.items():
            widget.setToolTip(t(key))

    def retranslate(self):
        """تحديث جميع النصوص عند تغيير اللغة"""
        self.title.setText(t("data_entry_title"))
        self.subtitle.setText(t("data_entry_subtitle"))
        self.company_group.setTitle(t("de_company_info"))
        self.company_name_label.setText(t("company_name"))
        self.company_name.setPlaceholderText(t("de_company_placeholder"))
        self.company_name_fr_label.setText(t("company_name_fr"))
        self.company_name_fr.setPlaceholderText(t("de_company_placeholder_fr"))
        self.fiscal_year_label.setText(t("fiscal_year"))
        self.company_nif_label.setText(t("company_nif"))
        self.company_nif.setPlaceholderText(t("company_nif_placeholder"))
        self.company_rc_label.setText(t("company_rc"))
        self.company_rc.setPlaceholderText(t("company_rc_placeholder"))
        self.company_legal_form_label.setText(t("company_legal_form"))
        self.company_activity_label.setText(t("company_activity_type"))
        self.company_bank_label.setText(t("company_bank_account"))
        self.company_bank.setPlaceholderText(t("company_bank_placeholder"))
        self.company_address_label.setText(t("company_address"))
        self.company_address.setPlaceholderText(t("company_address_placeholder"))
        self.company_phone_label.setText(t("company_phone"))
        self.company_phone.setPlaceholderText(t("company_phone_placeholder"))
        self.company_email_label.setText(t("company_email"))
        self.company_email.setPlaceholderText(t("company_email_placeholder"))
        self.balance_group.setTitle(t("de_balance_sheet"))
        self.current_assets_label.setText(t("current_assets"))
        self.inventory_label.setText(t("inventory"))
        self.current_liabilities_label.setText(t("current_liabilities"))
        self.cash_label.setText(t("cash"))
        self.total_assets_label.setText(t("total_assets"))
        self.total_liabilities_label.setText(t("total_liabilities"))
        self.equity_label.setText(t("equity"))
        self.income_group.setTitle(t("de_income_statement"))
        self.revenue_label.setText(t("revenue"))
        self.cogs_label.setText(t("de_cogs_short"))
        self.gross_profit_label.setText(t("de_gross_profit"))
        self.operating_expenses_label.setText(t("de_operating_expenses"))
        self.net_income_label.setText(t("net_income"))
        self.avg_receivables_label.setText(t("de_avg_receivables"))
        self.avg_inventory_label.setText(t("de_avg_inventory"))
        self.avg_payables_label.setText(t("de_avg_payables"))
        self.calculate_btn.setText(t("btn_calculate"))
        self.save_btn.setText(t("btn_save_db"))
        self.clear_btn.setText(t("btn_clear"))
        self.import_btn.setText(t("btn_import_excel"))
        self._validate()

    def _connect_validation_signals(self):
        """Connect valueChanged signals to validation."""
        self.total_assets.valueChanged.connect(self._validate)
        self.total_liabilities.valueChanged.connect(self._validate)
        self.equity.valueChanged.connect(self._validate)
        self.revenue.valueChanged.connect(self._validate)
        self.cogs.valueChanged.connect(self._validate)
        self.net_income.valueChanged.connect(self._validate)

    def _validate(self):
        """Real-time validation of balance sheet equation and key checks."""
        if getattr(self, '_suppress_validation', False):
            return
        warnings = []
        ta = self.total_assets.value()
        tl = self.total_liabilities.value()
        eq = self.equity.value()

        if ta > 0 and tl > 0 and eq > 0:
            diff = abs(ta - (tl + eq))
            if diff > 1:
                warnings.append(
                    f"⚠️ {t('de_validation_balance')}: "
                    f"{t('total_assets')} ({ta:,.0f}) ≠ {t('total_liabilities')} + {t('equity')} ({tl + eq:,.0f})"
                )

        rev = self.revenue.value()
        cogs = self.cogs.value()
        ni = self.net_income.value()
        if rev > 0 and cogs > rev:
            warnings.append(f"⚠️ {t('de_validation_cogs_high')}")

        if warnings:
            self.validation_label.setText("\n".join(warnings))
            self.validation_label.setStyleSheet(f"color: {ThemeColors.get('error')}; font-weight: bold;")
        else:
            self.validation_label.setText("")
            self.validation_label.setStyleSheet("")

    def _load_from_state(self):
        """تحميل البيانات من AppState (بعد إعادة فتح التطبيق)"""
        self._suppress_validation = True
        fd = state.financial_data
        self.company_name.setText(state.company_name)
        self.company_name_fr.setText(getattr(state, 'company_name_fr', ''))
        self.fiscal_year.setValue(state.fiscal_year)
        self.company_nif.setText(getattr(state, 'company_nif', ''))
        self.company_rc.setText(getattr(state, 'company_rc', ''))
        self.company_bank.setText(getattr(state, 'company_bank_account', ''))
        self.company_address.setText(getattr(state, 'company_address', ''))
        self.company_phone.setText(getattr(state, 'company_phone', ''))
        self.company_email.setText(getattr(state, 'company_email', ''))
        legal = getattr(state, 'company_legal_form', '')
        idx = self.company_legal_form.findText(legal)
        if idx >= 0:
            self.company_legal_form.setCurrentIndex(idx)
        act = getattr(state, 'company_activity_type', 0)
        if isinstance(act, int):
            self.company_activity.setCurrentIndex(act)
        self.current_assets.setValue(fd.get('current_assets', 0) or 0)
        self.inventory.setValue(fd.get('inventory', 0) or 0)
        self.current_liabilities.setValue(fd.get('current_liabilities', 0) or 0)
        self.cash.setValue(fd.get('cash', 0) or 0)
        self.total_assets.setValue(fd.get('total_assets', 0) or 0)
        self.total_liabilities.setValue(fd.get('total_liabilities', 0) or 0)
        self.equity.setValue(fd.get('equity', 0) or 0)
        self.revenue.setValue(fd.get('revenue', 0) or 0)
        self.cogs.setValue(fd.get('cost_of_goods_sold', 0) or 0)
        self.gross_profit.setValue(fd.get('gross_profit', 0) or 0)
        self.operating_expenses.setValue(fd.get('operating_expenses', 0) or 0)
        self.net_income.setValue(fd.get('net_income', 0) or 0)
        self.avg_receivables.setValue(fd.get('average_receivables', 0) or 0)
        self.avg_inventory.setValue(fd.get('average_inventory', 0) or 0)
        self.avg_payables.setValue(fd.get('average_payables', 0) or 0)
        self._suppress_validation = False
        if state.ratios:
            self.save_btn.setEnabled(True)

    def showEvent(self, event):
        super().showEvent(event)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(50, self.refresh)

    def refresh(self):
        """تحديث الواجهة من AppState عند العودة للشاشة"""
        if state.financial_data:
            self._load_from_state()

    def load_default_data(self):
        """تحميل بيانات تجريبية افتراضية"""
        self.company_name.setText("شركة اختبار للمحاسبة")
        self.company_name_fr.setText("Test Accounting LLC")
        self.fiscal_year.setValue(2024)
        self.company_nif.setText("1234567890")
        self.company_rc.setText("01/00-123456")
        self.company_legal_form.setCurrentIndex(1)
        self.company_activity.setCurrentIndex(3)
        self.company_bank.setText("00799999 0001234567 01")
        self.company_address.setText("شارع الأمير عبد القادر، الجزائر العاصمة")
        self.company_phone.setText("+213 555 123 456")
        self.company_email.setText("contact@accounting-test.dz")
        self.current_assets.setValue(100000)
        self.inventory.setValue(20000)
        self.current_liabilities.setValue(50000)
        self.cash.setValue(8000)
        self.total_assets.setValue(500000)
        self.total_liabilities.setValue(200000)
        self.equity.setValue(300000)
        self.revenue.setValue(200000)
        self.cogs.setValue(120000)
        self.gross_profit.setValue(30000)
        self.operating_expenses.setValue(15000)
        self.net_income.setValue(15000)
        self.avg_receivables.setValue(40000)
        self.avg_inventory.setValue(25000)
        self.avg_payables.setValue(18000)

    def get_data(self):
        """جمع كل البيانات من الحقول"""
        return {
            'company_name': _sanitize_text(self.company_name.text()),
            'company_name_fr': _sanitize_text(self.company_name_fr.text()),
            'fiscal_year': self.fiscal_year.value(),
            'company_nif': self.company_nif.text(),
            'company_rc': self.company_rc.text(),
            'company_legal_form': self.company_legal_form.currentText(),
            'company_activity_type': self.company_activity.currentIndex(),
            'company_bank_account': self.company_bank.text(),
            'company_address': self.company_address.text(),
            'company_phone': self.company_phone.text(),
            'company_email': self.company_email.text(),
            'current_assets': self.current_assets.value(),
            'inventory': self.inventory.value(),
            'current_liabilities': self.current_liabilities.value(),
            'cash': self.cash.value(),
            'total_assets': self.total_assets.value(),
            'total_liabilities': self.total_liabilities.value(),
            'equity': self.equity.value(),
            'revenue': self.revenue.value(),
            'cost_of_goods_sold': self.cogs.value(),
            'gross_profit': self.gross_profit.value(),
            'operating_expenses': self.operating_expenses.value(),
            'net_income': self.net_income.value(),
            'average_receivables': self.avg_receivables.value(),
            'average_inventory': self.avg_inventory.value(),
            'average_payables': self.avg_payables.value()
        }

    def _validate_and_get_data(self):
        """التحقق من البيانات وإرجاعها"""
        data = self.get_data()
        validator = DataValidator()
        if not validator.validate_financial_statement(data):
            self.overlay.hide()
            toast_error(self, t("de_invalid_data") + "\n" + "\n".join(validator.get_errors()))
            return None
        return data

    def _run_calculation(self, data):
        """تشغيل المحرك الحسابي"""
        engine = CalculationEngine(data)
        ratios = engine.calculate_all_ratios(data)
        if ratios is None:
            self.overlay.hide()
            toast_error(self, t("de_calc_fail"))
            return None
        return ratios

    def _update_state(self, data, ratios):
        """تحديث AppState بالبيانات الجديدة"""
        state.company_name = self.company_name.text() or t("de_company_default")
        state.company_name_fr = self.company_name_fr.text()
        state.fiscal_year = self.fiscal_year.value()
        state.company_nif = self.company_nif.text()
        state.company_rc = self.company_rc.text()
        state.company_legal_form = self.company_legal_form.currentText()
        state.company_activity_type = self.company_activity.currentIndex()
        state.company_bank_account = self.company_bank.text()
        state.company_address = self.company_address.text()
        state.company_phone = self.company_phone.text()
        state.company_email = self.company_email.text()
        state.financial_data = data
        state.ratios = ratios

        from modules import FinancialAnalyzer
        analyzer = FinancialAnalyzer(data)
        state.dupont = analyzer.dupont_analysis(
            data['net_income'], data['revenue'],
            data['total_assets'], data['equity']
        )
        state.working_capital = analyzer.working_capital_analysis(
            data['current_assets'], data['current_liabilities'], data['inventory']
        )

    def _run_fraud_checks(self, data):
        """تشغيل فحص الشذوذ"""
        new_alerts = []
        for field, value in data.items():
            old = self._previous_data.get(field, value)
            if old != value:
                alerts = fraud_detector.check_data_change(field, old, value, user="data_entry")
                new_alerts.extend(alerts)
        bs_alerts = fraud_detector.check_balance_sheet(data, user="data_entry")
        new_alerts.extend(bs_alerts)
        for field, value in data.items():
            post_audit = fraud_detector.check_after_audit(field, value, user="data_entry")
            new_alerts.extend(post_audit)
        rapid = fraud_detector.check_rapid_edits(user="data_entry")
        new_alerts.extend(rapid)
        self._previous_data = dict(data)
        return new_alerts

    def _notify_high_alerts(self, alerts):
        """إرسال إشعارات للتنبيهات الحرجة"""
        for a in alerts:
            if a["severity"] == "high":
                email_notifier.send_alert(a)

    def calculate_ratios(self):
        """حساب النسب المالية"""
        self.overlay.show_message(t("de_calc_overlay"), t("de_calc_overlay_detail"))
        try:
            data = self._validate_and_get_data()
            if data is None:
                return

            ratios = self._run_calculation(data)
            if ratios is None:
                return

            self._update_state(data, ratios)
            self.save_btn.setEnabled(True)
            self.data_calculated.emit()

            self._check_worker = _BackgroundCheckWorker(data, self._previous_data)
            self._check_worker.finished.connect(self._on_checks_done)
            self._previous_data = dict(data)
            self._check_worker.start()

            activity_log.log("calculate_ratios", f"company={state.company_name}, year={state.fiscal_year}")
            self.overlay.hide()
            toast_success(
                self,
                f"✅ {t('de_calc_success')}\n"
                f"ROE: {ratios['roe']}% | Current Ratio: {ratios['current_ratio']} | NPM: {ratios['net_profit_margin']}%"
            )
        except Exception as e:
            self.overlay.hide()
            raise

    def _on_checks_done(self, alerts):
        """استقبال نتائج فحص الاحتيال من الخيط الخلفي"""
        for a in alerts:
            if a.get("severity") == "high":
                email_notifier.send_alert(a)

    def save_to_db(self):
        """حفظ التحليل في قاعدة البيانات"""
        if not state.has_data():
            toast_warning(self, t("de_no_data_save"))
            return

        self.overlay.show_message(t("de_save_overlay"), t("de_save_overlay_detail"))
        try:
            from database import save_analysis
            fiscal_year_id = save_analysis(
                company_name=state.company_name,
                fiscal_year=state.fiscal_year,
                financial_data=state.financial_data,
                ratios=state.ratios
            )
            self.overlay.hide()
            if fiscal_year_id:
                activity_log.log("save_to_db", f"company={state.company_name}, year={state.fiscal_year}, id={fiscal_year_id}")
                toast_success(
                    self,
                    f"✅ {t('de_save_success_msg')} | ID: {fiscal_year_id}"
                )
            else:
                toast_error(self, t("de_save_fail"))
        except Exception as e:
            self.overlay.hide()
            toast_error(self, f"{t('de_save_error')} {e}")

    def clear_fields(self):
        """مسح كل الحقول"""
        reply = QMessageBox.question(
            self, t("de_clear_confirm_title"),
            t("de_clear_confirm"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        self.company_name.clear()
        self.company_name_fr.clear()
        self.fiscal_year.setValue(2024)
        self.company_nif.clear()
        self.company_rc.clear()
        self.company_legal_form.setCurrentIndex(0)
        self.company_activity.setCurrentIndex(0)
        self.company_bank.clear()
        self.company_address.clear()
        self.company_phone.clear()
        self.company_email.clear()
        for spin in [self.current_assets, self.inventory, self.current_liabilities,
                    self.cash, self.total_assets, self.total_liabilities, self.equity,
                    self.revenue, self.cogs, self.gross_profit, self.operating_expenses,
                    self.net_income, self.avg_receivables, self.avg_inventory,
                    self.avg_payables]:
            spin.setValue(0)
        state.clear()
        activity_log.log("clear_fields", "All fields cleared")
        self.save_btn.setEnabled(False)
        self._undo_stack.clear()
        toast_info(self, "🗑️ Fields cleared")

    def import_from_excel(self):
        """استيراد بيانات من Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, t("de_import_title"), "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            from modules import DataImporter
            importer = DataImporter()

            if file_path.endswith('.csv'):
                success = importer.import_from_csv(file_path)
            else:
                success = importer.import_from_excel(file_path)

            if success:
                data = importer.get_data()
                if data is not None and len(data) > 0:
                    first_row = data.iloc[0].to_dict()
                    self._fill_from_dict(first_row)
                    self._push_undo()
                    toast_success(self, t("de_import_success").format(count=len(data)))
                else:
                    toast_warning(self, t("de_import_empty"))
            else:
                toast_error(self, t("de_import_fail"))
        except Exception as e:
            toast_error(self, f"{t('de_import_error')} {e}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile().lower()
                if path.endswith(('.csv', '.xlsx', '.xls')):
                    event.acceptProposedAction()
                    self.setStyleSheet(f"DataEntryView {{ border: 2px dashed {ThemeColors.get('success')}; }}")
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.csv', '.xlsx', '.xls')):
                self._import_file(path)
                return
        toast_warning(self, t("de_import_drop_hint"))

    def _import_file(self, file_path):
        try:
            from modules import DataImporter
            importer = DataImporter()
            if file_path.lower().endswith('.csv'):
                success = importer.import_from_csv(file_path)
            else:
                success = importer.import_from_excel(file_path)
            if success:
                data = importer.get_data()
                if data is not None and len(data) > 0:
                    first_row = data.iloc[0].to_dict()
                    self._fill_from_dict(first_row)
                    self._push_undo()
                    toast_success(self, t("de_import_rows").format(count=len(data)))
                else:
                    toast_warning(self, t("de_import_empty"))
            else:
                toast_error(self, t("de_import_failed"))
        except Exception as e:
            toast_error(self, t("de_import_error").format(error=e))

    def _fill_from_dict(self, data):
        """ملء الحقول من dict"""
        mapping = {
            'current_assets': self.current_assets,
            'inventory': self.inventory,
            'current_liabilities': self.current_liabilities,
            'cash': self.cash,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'equity': self.equity,
            'revenue': self.revenue,
            'cost_of_goods_sold': self.cogs,
            'gross_profit': self.gross_profit,
            'operating_expenses': self.operating_expenses,
            'net_income': self.net_income,
            'average_receivables': self.avg_receivables,
            'average_inventory': self.avg_inventory,
            'average_payables': self.avg_payables
        }
        for key, widget in mapping.items():
            if key in data:
                try:
                    widget.setValue(float(data[key]))
                except (ValueError, TypeError):
                    pass

        text_mapping = {
            'company_name': self.company_name,
            'company_name_fr': self.company_name_fr,
            'company_nif': self.company_nif,
            'company_rc': self.company_rc,
            'company_bank_account': self.company_bank,
            'company_address': self.company_address,
            'company_phone': self.company_phone,
            'company_email': self.company_email,
        }
        for key, widget in text_mapping.items():
            if key in data and data[key]:
                widget.setText(str(data[key]))

    def _get_current_state(self):
        data = {}
        for spin in ['current_assets', 'inventory', 'current_liabilities',
                     'cash', 'total_assets', 'total_liabilities', 'equity',
                     'revenue', 'cogs', 'gross_profit', 'operating_expenses',
                     'net_income', 'avg_receivables', 'avg_inventory',
                     'avg_payables']:
            data[spin] = getattr(self, spin).value()
        for txt in ['company_name', 'company_name_fr', 'company_nif',
                    'company_rc', 'company_bank', 'company_address',
                    'company_phone', 'company_email']:
            data[txt] = getattr(self, txt).text()
        data['fiscal_year'] = self.fiscal_year.value()
        data['legal_form'] = self.company_legal_form.currentIndex()
        data['activity'] = self.company_activity.currentIndex()
        return data

    def _restore_state(self, saved):
        spin_map = {
            'current_assets': self.current_assets, 'inventory': self.inventory,
            'current_liabilities': self.current_liabilities, 'cash': self.cash,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities, 'equity': self.equity,
            'revenue': self.revenue, 'cogs': self.cogs, 'gross_profit': self.gross_profit,
            'operating_expenses': self.operating_expenses,
            'net_income': self.net_income, 'avg_receivables': self.avg_receivables,
            'avg_inventory': self.avg_inventory, 'avg_payables': self.avg_payables
        }
        for k, w in spin_map.items():
            if k in saved:
                w.setValue(saved[k])
        txt_map = {
            'company_name': self.company_name, 'company_name_fr': self.company_name_fr,
            'company_nif': self.company_nif, 'company_rc': self.company_rc,
            'company_bank': self.company_bank, 'company_address': self.company_address,
            'company_phone': self.company_phone, 'company_email': self.company_email
        }
        for k, w in txt_map.items():
            if k in saved:
                w.setText(saved[k])
        if 'fiscal_year' in saved:
            self.fiscal_year.setValue(saved['fiscal_year'])
        if 'legal_form' in saved:
            self.company_legal_form.setCurrentIndex(saved['legal_form'])
        if 'activity' in saved:
            self.company_activity.setCurrentIndex(saved['activity'])

    def _push_undo(self):
        self._undo_stack.push(self._get_current_state())

    def _undo(self):
        current = self._get_current_state()
        restored = self._undo_stack.undo(current)
        if restored is not None:
            self._restore_state(restored)
            toast_info(self, "↩ Undo")

    def _redo(self):
        current = self._get_current_state()
        restored = self._undo_stack.redo(current)
        if restored is not None:
            self._restore_state(restored)
            toast_info(self, "↪ Redo")
