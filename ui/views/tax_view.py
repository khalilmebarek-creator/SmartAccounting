# واجهة النظام الجبائي الجزائري
# ==============================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QDoubleSpinBox, QComboBox,
    QGroupBox, QFrame, QTableWidget, QTableWidgetItem,
    QMessageBox, QTextEdit, QTabWidget, QFormLayout,
    QHeaderView, QSplitter, QFileDialog, QInputDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (QColor)

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.tax import TaxEngine
from modules import tax_years
from modules.tax_reports import tax_declaration_generator
from datetime import datetime


class TaxView(QWidget):
    """واجهة النظام الجبائي الجزائري"""

    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tax_engine = TaxEngine()
        self.last_simulation = None
        self._current_declaration = None
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = QLabel(t("tax_title"))
        self.title_label.setObjectName("headerTitle")
        self.main_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(t("tax_subtitle"))
        self.subtitle_label.setObjectName("headerSubtitle")
        self.main_layout.addWidget(self.subtitle_label)

        config_year = self.tax_engine.get_config_year()
        year_label = QLabel(f"{t('tax_config_year')} {config_year}")
        year_label.setObjectName("subtitleLabel")
        self.main_layout.addWidget(year_label)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.main_layout.addWidget(self.tabs)

        self._build_simulation_tab()
        self._build_tax_calculators_tab()
        self._build_obligations_tab()
        self._build_declarations_tab()
        self._build_years_tab()

        self.setLayout(self.main_layout)

    def _build_simulation_tab(self):
        """بناء تبويب المحاكاة الشاملة"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        input_group = QGroupBox(t("tax_input_group"))
        form = QFormLayout()
        form.setSpacing(10)

        self.revenue_input = QDoubleSpinBox()
        self.revenue_input.setRange(0, 999999999999)
        self.revenue_input.setDecimals(0)
        self.revenue_input.setGroupSeparatorShown(True)
        self.revenue_input.setSuffix(" DZD")
        form.addRow(t("tax_revenue"), self.revenue_input)

        self.cogs_input = QDoubleSpinBox()
        self.cogs_input.setRange(0, 999999999999)
        self.cogs_input.setDecimals(0)
        self.cogs_input.setGroupSeparatorShown(True)
        self.cogs_input.setSuffix(" DZD")
        form.addRow(t("tax_cogs"), self.cogs_input)

        self.opex_input = QDoubleSpinBox()
        self.opex_input.setRange(0, 999999999999)
        self.opex_input.setDecimals(0)
        self.opex_input.setGroupSeparatorShown(True)
        self.opex_input.setSuffix(" DZD")
        form.addRow(t("tax_opex"), self.opex_input)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        form.addRow(sep)

        self.assets_input = QDoubleSpinBox()
        self.assets_input.setRange(0, 999999999999)
        self.assets_input.setDecimals(0)
        self.assets_input.setGroupSeparatorShown(True)
        self.assets_input.setSuffix(" DZD")
        form.addRow(t("tax_assets"), self.assets_input)

        self.liabilities_input = QDoubleSpinBox()
        self.liabilities_input.setRange(0, 999999999999)
        self.liabilities_input.setDecimals(0)
        self.liabilities_input.setGroupSeparatorShown(True)
        self.liabilities_input.setSuffix(" DZD")
        form.addRow(t("tax_liabilities"), self.liabilities_input)

        self.equity_input = QDoubleSpinBox()
        self.equity_input.setRange(0, 999999999999)
        self.equity_input.setDecimals(0)
        self.equity_input.setGroupSeparatorShown(True)
        self.equity_input.setSuffix(" DZD")
        form.addRow(t("tax_equity"), self.equity_input)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setObjectName("separator")
        form.addRow(sep2)

        self.employees_input = QDoubleSpinBox()
        self.employees_input.setRange(0, 99999)
        self.employees_input.setDecimals(0)
        form.addRow(t("tax_employees"), self.employees_input)

        self.avg_salary_input = QDoubleSpinBox()
        self.avg_salary_input.setRange(0, 99999999)
        self.avg_salary_input.setDecimals(0)
        self.avg_salary_input.setGroupSeparatorShown(True)
        self.avg_salary_input.setSuffix(" DZD")
        form.addRow(t("tax_avg_salary"), self.avg_salary_input)

        self.activity_combo = QComboBox()
        self.activity_combo.addItems([
            t("tax_activity_production"),
            t("tax_activity_construction"),
            t("tax_activity_other")
        ])
        form.addRow(t("tax_activity_type"), self.activity_combo)

        self.construction_check = QPushButton(t("tax_is_construction"))
        self.construction_check.setCheckable(True)
        self.construction_check.setMinimumHeight(35)
        form.addRow("", self.construction_check)

        input_group.setLayout(form)
        left_layout.addWidget(input_group)

        self.simulate_btn = QPushButton(t("tax_simulate"))
        self.simulate_btn.setObjectName("primaryBtn")
        self.simulate_btn.setMinimumHeight(50)
        self.simulate_btn.clicked.connect(self.run_simulation)
        left_layout.addWidget(self.simulate_btn)

        self.save_btn = QPushButton(t("tax_save_simulation"))
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self.save_simulation)
        left_layout.addWidget(self.save_btn)

        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        results_group = QGroupBox(t("tax_summary_title"))
        results_layout = QVBoxLayout()

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels([t("tax_table_item"), t("tax_table_value")])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        results_layout.addWidget(self.results_table)

        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMinimumHeight(200)
        self.detail_text.setObjectName("detailText")
        right_layout.addWidget(self.detail_text)

        splitter.addWidget(right_widget)
        splitter.setSizes([400, 500])

        layout.addWidget(splitter)
        self.tabs.addTab(tab, t("tax_tab_simulation"))

    def _build_tax_calculators_tab(self):
        """بناء تبويب الآلات الحاسبة"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        calcs_layout = QHBoxLayout()

        # IBS Calculator
        ibs_group = QGroupBox(t("tax_ibs_group"))
        ibs_layout = QFormLayout()
        ibs_layout.setSpacing(8)

        self.ibs_income_input = QDoubleSpinBox()
        self.ibs_income_input.setRange(0, 999999999999)
        self.ibs_income_input.setDecimals(0)
        self.ibs_income_input.setGroupSeparatorShown(True)
        self.ibs_income_input.setSuffix(" DZD")
        ibs_layout.addRow(t("tax_ibs_income_label"), self.ibs_income_input)

        self.ibs_activity_combo = QComboBox()
        self.ibs_activity_combo.addItems([
            t("tax_activity_production"),
            t("tax_activity_construction"),
            t("tax_activity_other")
        ])
        ibs_layout.addRow(t("tax_activity_type"), self.ibs_activity_combo)

        self.ibs_calc_btn = QPushButton(t("tax_calc_ibs"))
        self.ibs_calc_btn.setMinimumHeight(40)
        self.ibs_calc_btn.clicked.connect(self.calc_ibs)
        ibs_layout.addRow(self.ibs_calc_btn)

        self.ibs_result_label = QLabel("")
        self.ibs_result_label.setWordWrap(True)
        self.ibs_result_label.setObjectName("resultLabel")
        ibs_layout.addRow("", self.ibs_result_label)

        ibs_group.setLayout(ibs_layout)
        calcs_layout.addWidget(ibs_group)

        # TVA Calculator
        tva_group = QGroupBox(t("tax_tva_group"))
        tva_layout = QFormLayout()
        tva_layout.setSpacing(8)

        self.tva_amount_input = QDoubleSpinBox()
        self.tva_amount_input.setRange(0, 999999999999)
        self.tva_amount_input.setDecimals(0)
        self.tva_amount_input.setGroupSeparatorShown(True)
        self.tva_amount_input.setSuffix(" DZD")
        tva_layout.addRow(t("tax_amount_excl"), self.tva_amount_input)

        self.tva_rate_combo = QComboBox()
        self.tva_rate_combo.addItems([
            t("tax_rate_standard"),
            t("tax_rate_reduced"),
            t("tax_rate_intermediate"),
            t("tax_rate_zero")
        ])
        tva_layout.addRow(t("tax_tva_rate_label"), self.tva_rate_combo)

        self.tva_calc_btn = QPushButton(t("tax_calc_tva"))
        self.tva_calc_btn.setMinimumHeight(40)
        self.tva_calc_btn.clicked.connect(self.calc_tva)
        tva_layout.addRow(self.tva_calc_btn)

        self.tva_result_label = QLabel("")
        self.tva_result_label.setWordWrap(True)
        self.tva_result_label.setObjectName("resultLabel")
        tva_layout.addRow("", self.tva_result_label)

        tva_group.setLayout(tva_layout)
        calcs_layout.addWidget(tva_group)

        # IRG Calculator
        irg_group = QGroupBox(t("tax_irg_group"))
        irg_layout = QFormLayout()
        irg_layout.setSpacing(8)

        self.irg_salary_input = QDoubleSpinBox()
        self.irg_salary_input.setRange(0, 99999999)
        self.irg_salary_input.setDecimals(0)
        self.irg_salary_input.setGroupSeparatorShown(True)
        self.irg_salary_input.setSuffix(" DZD")
        irg_layout.addRow(t("tax_gross_salary"), self.irg_salary_input)

        self.irg_calc_btn = QPushButton(t("tax_calc_irg"))
        self.irg_calc_btn.setMinimumHeight(40)
        self.irg_calc_btn.clicked.connect(self.calc_irg)
        irg_layout.addRow(self.irg_calc_btn)

        self.irg_result_label = QLabel("")
        self.irg_result_label.setWordWrap(True)
        self.irg_result_label.setObjectName("resultLabel")
        irg_layout.addRow("", self.irg_result_label)

        irg_group.setLayout(irg_layout)
        calcs_layout.addWidget(irg_group)

        layout.addLayout(calcs_layout)

        calcs_layout2 = QHBoxLayout()

        # CNAS Calculator
        cnas_group = QGroupBox(t("tax_cnas_group"))
        cnas_layout = QFormLayout()
        cnas_layout.setSpacing(8)

        self.cnas_salary_input = QDoubleSpinBox()
        self.cnas_salary_input.setRange(0, 99999999)
        self.cnas_salary_input.setDecimals(0)
        self.cnas_salary_input.setGroupSeparatorShown(True)
        self.cnas_salary_input.setSuffix(" DZD")
        cnas_layout.addRow(t("tax_gross_salary"), self.cnas_salary_input)

        self.cnas_calc_btn = QPushButton(t("tax_calc_cnas"))
        self.cnas_calc_btn.setMinimumHeight(40)
        self.cnas_calc_btn.clicked.connect(self.calc_cnas)
        cnas_layout.addRow(self.cnas_calc_btn)

        self.cnas_result_label = QLabel("")
        self.cnas_result_label.setWordWrap(True)
        self.cnas_result_label.setObjectName("resultLabel")
        cnas_layout.addRow("", self.cnas_result_label)

        cnas_group.setLayout(cnas_layout)
        calcs_layout2.addWidget(cnas_group)

        # CNAC Calculator
        cnac_group = QGroupBox(t("tax_cnac_group"))
        cnac_layout = QFormLayout()
        cnac_layout.setSpacing(8)

        self.cnac_salary_input = QDoubleSpinBox()
        self.cnac_salary_input.setRange(0, 99999999)
        self.cnac_salary_input.setDecimals(0)
        self.cnac_salary_input.setGroupSeparatorShown(True)
        self.cnac_salary_input.setSuffix(" DZD")
        cnac_layout.addRow(t("tax_gross_salary"), self.cnac_salary_input)

        self.cnac_calc_btn = QPushButton(t("tax_calc_cnac"))
        self.cnac_calc_btn.setMinimumHeight(40)
        self.cnac_calc_btn.clicked.connect(self.calc_cnac)
        cnac_layout.addRow(self.cnac_calc_btn)

        self.cnac_result_label = QLabel("")
        self.cnac_result_label.setWordWrap(True)
        self.cnac_result_label.setObjectName("resultLabel")
        cnac_layout.addRow("", self.cnac_result_label)

        cnac_group.setLayout(cnac_layout)
        calcs_layout2.addWidget(cnac_group)

        # Payroll Summary
        payroll_group = QGroupBox(t("tax_payroll_group"))
        payroll_layout = QFormLayout()
        payroll_layout.setSpacing(8)

        self.payroll_salary_input = QDoubleSpinBox()
        self.payroll_salary_input.setRange(0, 99999999)
        self.payroll_salary_input.setDecimals(0)
        self.payroll_salary_input.setGroupSeparatorShown(True)
        self.payroll_salary_input.setSuffix(" DZD")
        payroll_layout.addRow(t("tax_gross_salary"), self.payroll_salary_input)

        self.payroll_calc_btn = QPushButton(t("tax_payroll_calc"))
        self.payroll_calc_btn.setMinimumHeight(40)
        self.payroll_calc_btn.clicked.connect(self.calc_payroll)
        payroll_layout.addRow(self.payroll_calc_btn)

        self.payroll_result_label = QLabel("")
        self.payroll_result_label.setWordWrap(True)
        self.payroll_result_label.setObjectName("resultLabel")
        payroll_layout.addRow("", self.payroll_result_label)

        payroll_group.setLayout(payroll_layout)
        calcs_layout2.addWidget(payroll_group)

        layout.addLayout(calcs_layout2)
        layout.addStretch()

        self.tabs.addTab(tab, t("tax_tab_calculators"))

    def _build_obligations_tab(self):
        """بناء تبويب الالتزامات الجبائية"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()

        self.oblig_month_label = QLabel(t("tax_month"))
        self.oblig_month_combo = QComboBox()
        months_list = [
            "", t("tax_month_jan"), t("tax_month_feb"), t("tax_month_mar"),
            t("tax_month_apr"), t("tax_month_may"), t("tax_month_jun"),
            t("tax_month_jul"), t("tax_month_aug"), t("tax_month_sep"),
            t("tax_month_oct"), t("tax_month_nov"), t("tax_month_dec")
        ]
        self.oblig_month_combo.addItems(months_list)

        self.oblig_show_btn = QPushButton(t("tax_oblig_show"))
        self.oblig_show_btn.setMinimumHeight(40)
        self.oblig_show_btn.clicked.connect(self.show_obligations)

        header_layout.addWidget(self.oblig_month_label)
        header_layout.addWidget(self.oblig_month_combo)
        header_layout.addWidget(self.oblig_show_btn)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        self.oblig_table = QTableWidget()
        self.oblig_table.setColumnCount(4)
        self.oblig_table.setHorizontalHeaderLabels([
            t("tax_oblig_type"), t("tax_oblig_day"),
            t("tax_oblig_amount"), t("tax_oblig_status")
        ])
        self.oblig_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.oblig_table.setAlternatingRowColors(True)
        self.oblig_table.verticalHeader().setVisible(False)
        self.oblig_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.oblig_table)

        from ui.widgets.table_filter import TableFilterWidget
        self.oblig_filter = TableFilterWidget(self.oblig_table, t("filter_placeholder"))
        layout.addWidget(self.oblig_filter)

        self.oblig_info = QTextEdit()
        self.oblig_info.setReadOnly(True)
        self.oblig_info.setMaximumHeight(120)
        self.oblig_info.setObjectName("infoText")
        self.oblig_info.setHtml(f"""
        <b>{t('tax_oblig_info')}</b><br>
        • {t('tax_oblig_info_day')}
        """)
        layout.addWidget(self.oblig_info)

        layout.addStretch()
        self.tabs.addTab(tab, t("tax_tab_obligations"))

    def _build_declarations_tab(self):
        """بناء تبويب الإقرارات الجبائية (G50/G57/DAS)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        self.decl_company_group = QGroupBox(t("taxdecl_company_group"))
        company_form = QFormLayout()
        company_form.setSpacing(8)

        self.decl_name_input = QLineEdit(state.company_name)
        company_form.addRow(t("taxdecl_company_name"), self.decl_name_input)

        self.decl_nif_input = QLineEdit(state.company_nif)
        company_form.addRow(t("taxdecl_nif"), self.decl_nif_input)

        self.decl_rc_input = QLineEdit(state.company_rc)
        company_form.addRow(t("taxdecl_rc"), self.decl_rc_input)

        self.decl_ai_input = QLineEdit()
        company_form.addRow(t("taxdecl_ai"), self.decl_ai_input)

        self.decl_address_input = QLineEdit(state.company_address)
        company_form.addRow(t("taxdecl_address"), self.decl_address_input)

        self.decl_dgi_input = QLineEdit()
        company_form.addRow(t("taxdecl_dgi"), self.decl_dgi_input)

        self.decl_company_group.setLayout(company_form)
        self.decl_company_form = company_form
        left_layout.addWidget(self.decl_company_group)

        self.decl_period_group = QGroupBox(t("taxdecl_period_group"))
        period_form = QFormLayout()
        period_form.setSpacing(8)

        self.decl_type_combo = QComboBox()
        self.decl_type_combo.addItems([
            t("taxdecl_g50"), t("taxdecl_g57"), t("taxdecl_das")
        ])
        self.decl_type_combo.currentIndexChanged.connect(self._on_decl_type_changed)
        period_form.addRow(t("taxdecl_type"), self.decl_type_combo)

        self.decl_month_combo = QComboBox()
        self.decl_month_combo.addItems([
            t("tax_month_jan"), t("tax_month_feb"), t("tax_month_mar"),
            t("tax_month_apr"), t("tax_month_may"), t("tax_month_jun"),
            t("tax_month_jul"), t("tax_month_aug"), t("tax_month_sep"),
            t("tax_month_oct"), t("tax_month_nov"), t("tax_month_dec")
        ])
        period_form.addRow(t("taxdecl_month"), self.decl_month_combo)

        self.decl_year_combo = QComboBox()
        current_year = datetime.now().year
        year_items = [str(y) for y in range(current_year + 1, current_year - 5, -1)]
        self.decl_year_combo.addItems(year_items)
        fy_text = str(state.fiscal_year)
        if fy_text in year_items:
            self.decl_year_combo.setCurrentText(fy_text)
        period_form.addRow(t("taxdecl_year"), self.decl_year_combo)

        self.decl_period_group.setLayout(period_form)
        self.decl_period_form = period_form
        left_layout.addWidget(self.decl_period_group)

        self.decl_data_group = QGroupBox(t("taxdecl_data_group"))
        data_form = QFormLayout()
        data_form.setSpacing(8)

        def _money_input():
            spin = QDoubleSpinBox()
            spin.setRange(0, 999999999999)
            spin.setDecimals(0)
            spin.setGroupSeparatorShown(True)
            spin.setSuffix(" DZD")
            return spin

        self.decl_turnover_lbl = QLabel(t("taxdecl_turnover"))
        self.decl_turnover_input = _money_input()
        data_form.addRow(self.decl_turnover_lbl, self.decl_turnover_input)

        self.decl_collected_lbl = QLabel(t("taxdecl_collected"))
        self.decl_collected_input = _money_input()
        data_form.addRow(self.decl_collected_lbl, self.decl_collected_input)

        self.decl_deductible_lbl = QLabel(t("taxdecl_deductible"))
        self.decl_deductible_input = _money_input()
        data_form.addRow(self.decl_deductible_lbl, self.decl_deductible_input)

        self.decl_credit_lbl = QLabel(t("taxdecl_previous_credit"))
        self.decl_credit_input = _money_input()
        data_form.addRow(self.decl_credit_lbl, self.decl_credit_input)

        self.decl_taxable_lbl = QLabel(t("taxdecl_taxable"))
        self.decl_taxable_input = _money_input()
        data_form.addRow(self.decl_taxable_lbl, self.decl_taxable_input)

        self.decl_activity_lbl = QLabel(t("taxdecl_activity"))
        self.decl_activity_combo = QComboBox()
        self.decl_activity_combo.addItems([
            t("tax_activity_production"),
            t("tax_activity_construction"),
            t("tax_activity_other")
        ])
        data_form.addRow(self.decl_activity_lbl, self.decl_activity_combo)

        self.decl_acomptes_lbl = QLabel(t("taxdecl_acomptes_paid"))
        self.decl_acomptes_input = _money_input()
        data_form.addRow(self.decl_acomptes_lbl, self.decl_acomptes_input)

        self.decl_payroll_lbl = QLabel(t("taxdecl_payroll"))
        self.decl_payroll_input = _money_input()
        data_form.addRow(self.decl_payroll_lbl, self.decl_payroll_input)

        self.decl_employees_lbl = QLabel(t("taxdecl_employees"))
        self.decl_employees_input = QDoubleSpinBox()
        self.decl_employees_input.setRange(0, 99999)
        self.decl_employees_input.setDecimals(0)
        data_form.addRow(self.decl_employees_lbl, self.decl_employees_input)

        self.decl_avg_salary_lbl = QLabel(t("taxdecl_avg_salary"))
        self.decl_avg_salary_input = _money_input()
        data_form.addRow(self.decl_avg_salary_lbl, self.decl_avg_salary_input)

        data_group = self.decl_data_group
        data_group.setLayout(data_form)
        left_layout.addWidget(data_group)

        btn_layout = QHBoxLayout()
        self.decl_prefill_btn = QPushButton(t("taxdecl_prefill"))
        self.decl_prefill_btn.clicked.connect(self._prefill_declaration)
        btn_layout.addWidget(self.decl_prefill_btn)
        self.decl_generate_btn = QPushButton(t("taxdecl_generate"))
        self.decl_generate_btn.setObjectName("primaryBtn")
        self.decl_generate_btn.setMinimumHeight(40)
        self.decl_generate_btn.clicked.connect(self._generate_declaration)
        btn_layout.addWidget(self.decl_generate_btn)
        left_layout.addLayout(btn_layout)

        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        self.decl_preview_group = QGroupBox(t("taxdecl_preview_group"))
        preview_layout = QVBoxLayout()
        self.decl_preview = QTextEdit()
        self.decl_preview.setReadOnly(True)
        self.decl_preview.setObjectName("detailText")
        self.decl_preview.setPlaceholderText(t("taxdecl_preview_empty"))
        preview_layout.addWidget(self.decl_preview)
        self.decl_preview_group.setLayout(preview_layout)
        right_layout.addWidget(self.decl_preview_group)

        export_layout = QHBoxLayout()
        export_layout.addStretch()
        self.decl_export_pdf_btn = QPushButton(t("taxdecl_export_pdf"))
        self.decl_export_pdf_btn.clicked.connect(self._export_declaration_pdf)
        export_layout.addWidget(self.decl_export_pdf_btn)
        self.decl_export_excel_btn = QPushButton(t("taxdecl_export_excel"))
        self.decl_export_excel_btn.clicked.connect(self._export_declaration_excel)
        export_layout.addWidget(self.decl_export_excel_btn)
        right_layout.addLayout(export_layout)

        splitter.addWidget(right_widget)
        splitter.setSizes([430, 480])

        layout.addWidget(splitter)
        self.tabs.addTab(tab, t("taxdecl_tab"))
        self._on_decl_type_changed(0)

    def _build_years_tab(self):
        """بناء تبويب السنوات الجبائية + الحاسبات الجديدة (IFU/تكوين/اقتطاع)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # --- إدارة السنوات ---
        years_group = QGroupBox(t("tax_tab_years"))
        years_form = QFormLayout()
        years_form.setSpacing(8)

        self.years_active_label = QLabel(t("tax_years_active"))
        years_form.addRow(self.years_active_label, QLabel(""))

        self.years_combo = QComboBox()
        self.reload_years_combo()
        years_form.addRow(t("tax_years_available"), self.years_combo)

        btn_row = QHBoxLayout()
        self.years_switch_btn = QPushButton(t("tax_years_switch"))
        self.years_switch_btn.clicked.connect(self.switch_year)
        btn_row.addWidget(self.years_switch_btn)
        self.years_add_btn = QPushButton(t("tax_years_add"))
        self.years_add_btn.clicked.connect(self.add_year)
        btn_row.addWidget(self.years_add_btn)
        self.years_delete_btn = QPushButton(t("tax_years_delete"))
        self.years_delete_btn.clicked.connect(self.delete_year)
        btn_row.addWidget(self.years_delete_btn)
        years_form.addRow(btn_row)

        years_group.setLayout(years_form)
        layout.addWidget(years_group)

        source_label = QLabel(t("tax_years_source_note"))
        source_label.setObjectName("subtitleLabel")
        source_label.setWordWrap(True)
        layout.addWidget(source_label)

        # --- محرر JSON ---
        editor_group = QGroupBox(t("tax_years_editor_title"))
        editor_layout = QVBoxLayout()

        hint_label = QLabel(t("tax_years_edit_hint"))
        hint_label.setWordWrap(True)
        hint_label.setObjectName("subtitleLabel")
        editor_layout.addWidget(hint_label)

        self.years_editor = QTextEdit()
        self.years_editor.setObjectName("detailText")
        self.years_editor.setMinimumHeight(220)
        editor_layout.addWidget(self.years_editor)

        editor_btns = QHBoxLayout()
        self.years_load_btn = QPushButton(t("tax_years_available"))
        self.years_load_btn.setText("↻")
        self.years_load_btn.setToolTip(t("tax_years_available"))
        self.years_load_btn.clicked.connect(self.load_editor_from_year)
        editor_btns.addWidget(self.years_load_btn)
        self.years_validate_btn = QPushButton(t("tax_years_validate"))
        self.years_validate_btn.clicked.connect(self.validate_year_config)
        editor_btns.addWidget(self.years_validate_btn)
        self.years_save_btn = QPushButton(t("tax_years_save"))
        self.years_save_btn.clicked.connect(self.save_year_config)
        editor_btns.addWidget(self.years_save_btn)
        self.years_import_btn = QPushButton(t("tax_years_import"))
        self.years_import_btn.clicked.connect(self.import_year_json)
        editor_btns.addWidget(self.years_import_btn)
        self.years_export_btn = QPushButton(t("tax_years_export"))
        self.years_export_btn.clicked.connect(self.export_year_json)
        editor_btns.addWidget(self.years_export_btn)
        editor_layout.addLayout(editor_btns)

        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)

        # --- الحاسبات الجديدة ---
        calcs_group = QGroupBox(t("tax_newtaxes_group"))
        calcs_layout = QVBoxLayout()
        calcs_layout.setSpacing(10)

        # IFU
        ifu_box = QGroupBox(t("tax_ifu_group"))
        ifu_form = QFormLayout()
        ifu_form.setSpacing(8)
        self.ifu_turnover_input = QDoubleSpinBox()
        self.ifu_turnover_input.setRange(0, 999999999999)
        self.ifu_turnover_input.setDecimals(0)
        self.ifu_turnover_input.setGroupSeparatorShown(True)
        self.ifu_turnover_input.setSuffix(" DZD")
        ifu_form.addRow(t("tax_ifu_turnover"), self.ifu_turnover_input)
        self.ifu_regime_combo = QComboBox()
        self.ifu_regime_combo.addItems([
            t("tax_ifu_regime_auto"), t("tax_ifu_regime_production"),
            t("tax_ifu_regime_other")
        ])
        ifu_form.addRow(t("tax_ifu_regime"), self.ifu_regime_combo)
        self.ifu_calc_btn = QPushButton(t("tax_ifu_calc"))
        self.ifu_calc_btn.clicked.connect(self.calc_ifu)
        ifu_form.addRow(self.ifu_calc_btn)
        self.ifu_result_label = QLabel("")
        self.ifu_result_label.setWordWrap(True)
        self.ifu_result_label.setObjectName("resultLabel")
        ifu_form.addRow("", self.ifu_result_label)
        ifu_hint = QLabel(t("tax_ifu_max_hint"))
        ifu_hint.setObjectName("subtitleLabel")
        ifu_form.addRow(ifu_hint)
        ifu_box.setLayout(ifu_form)
        calcs_layout.addWidget(ifu_box)

        # رسم التكوين والتمهين
        form_box = QGroupBox(t("tax_formation_group"))
        form_form = QFormLayout()
        form_form.setSpacing(8)
        self.form_payroll_input = QDoubleSpinBox()
        self.form_payroll_input.setRange(0, 999999999999)
        self.form_payroll_input.setDecimals(0)
        self.form_payroll_input.setGroupSeparatorShown(True)
        self.form_payroll_input.setSuffix(" DZD")
        form_form.addRow(t("tax_formation_payroll"), self.form_payroll_input)
        self.form_budget_input = QDoubleSpinBox()
        self.form_budget_input.setRange(0, 999999999999)
        self.form_budget_input.setDecimals(0)
        self.form_budget_input.setGroupSeparatorShown(True)
        self.form_budget_input.setSuffix(" DZD")
        form_form.addRow(t("tax_formation_budget"), self.form_budget_input)
        self.form_apprentice_input = QDoubleSpinBox()
        self.form_apprentice_input.setRange(0, 999999999999)
        self.form_apprentice_input.setDecimals(0)
        self.form_apprentice_input.setGroupSeparatorShown(True)
        self.form_apprentice_input.setSuffix(" DZD")
        form_form.addRow(t("tax_apprenticeship_budget"), self.form_apprentice_input)
        self.form_calc_btn = QPushButton(t("tax_formation_calc"))
        self.form_calc_btn.clicked.connect(self.calc_formation_tax)
        form_form.addRow(self.form_calc_btn)
        self.form_result_label = QLabel("")
        self.form_result_label.setWordWrap(True)
        self.form_result_label.setObjectName("resultLabel")
        form_form.addRow("", self.form_result_label)
        form_hint = QLabel(t("tax_formation_hint"))
        form_hint.setObjectName("subtitleLabel")
        form_hint.setWordWrap(True)
        form_form.addRow(form_hint)
        form_box.setLayout(form_form)
        calcs_layout.addWidget(form_box)

        # الاقتطاع على الإيجارات
        rent_box = QGroupBox(t("tax_rental_group"))
        rent_form = QFormLayout()
        rent_form.setSpacing(8)
        self.rent_amount_input = QDoubleSpinBox()
        self.rent_amount_input.setRange(0, 999999999999)
        self.rent_amount_input.setDecimals(0)
        self.rent_amount_input.setGroupSeparatorShown(True)
        self.rent_amount_input.setSuffix(" DZD")
        rent_form.addRow(t("tax_rental_amount"), self.rent_amount_input)
        self.rent_kind_combo = QComboBox()
        self.rent_kind_combo.addItems([
            t("tax_rental_residential"), t("tax_rental_commercial"),
            t("tax_rental_professional"), t("tax_rental_agricultural"),
            t("tax_rental_unbuilt")
        ])
        rent_form.addRow(t("tax_rental_kind"), self.rent_kind_combo)
        self.rent_calc_btn = QPushButton(t("tax_rental_calc"))
        self.rent_calc_btn.clicked.connect(self.calc_rental_withholding)
        rent_form.addRow(self.rent_calc_btn)
        self.rent_result_label = QLabel("")
        self.rent_result_label.setWordWrap(True)
        self.rent_result_label.setObjectName("resultLabel")
        rent_form.addRow("", self.rent_result_label)
        rent_hint = QLabel(t("tax_rental_provisional_hint"))
        rent_hint.setObjectName("subtitleLabel")
        rent_hint.setWordWrap(True)
        rent_form.addRow(rent_hint)
        rent_box.setLayout(rent_form)
        calcs_layout.addWidget(rent_box)

        calcs_group.setLayout(calcs_layout)
        layout.addWidget(calcs_group)

        layout.addStretch()
        self.tabs.addTab(tab, t("tax_tab_years"))
        self.load_editor_from_year()

    # ==================== Year Management ====================

    def reload_years_combo(self):
        """تحديث قائمة السنوات"""
        self.years_combo.clear()
        for year in self.tax_engine.list_years():
            self.years_combo.addItem(str(year))
        current = self.tax_engine.get_config_year()
        index = self.years_combo.findText(str(current))
        if index >= 0:
            self.years_combo.setCurrentIndex(index)

    def switch_year(self):
        """تفعيل السنة المختارة"""
        text = self.years_combo.currentText()
        if not text:
            QMessageBox.warning(self, t("error"), t("tax_years_no_selection"))
            return
        year = int(text)
        if self.tax_engine.set_year(year):
            self.load_editor_from_year()
            self.years_active_label.setText(f"{t('tax_years_active')} {year}")
            QMessageBox.information(self, t("success"),
                                    f"{t('tax_years_switched')} {year}")
        else:
            QMessageBox.warning(self, t("error"), t("tax_years_no_selection"))

    def add_year(self):
        """إضافة سنة جديدة بنسخ أحدث سنة"""
        latest = self.tax_engine.list_years()
        if not latest:
            QMessageBox.warning(self, t("error"), t("tax_years_new_fail"))
            return
        src = max(latest)
        year, ok = QInputDialog.getInt(
            self, t("tax_years_add"), t("tax_years_new_prompt"),
            minValue=src + 1, maxValue=2100)
        if not ok:
            return
        if tax_years.copy_year(src, year):
            self.reload_years_combo()
            self.years_combo.setCurrentText(str(year))
            self.tax_engine.set_year(year)
            self.load_editor_from_year()
            self.years_active_label.setText(t("tax_years_active") + f" {year}")
            QMessageBox.information(self, t("success"), t("tax_years_new_copied"))
        else:
            QMessageBox.warning(self, t("error"), t("tax_years_new_fail"))

    def delete_year(self):
        """حذف السنة الحالية (مع حماية آخر سنة)"""
        text = self.years_combo.currentText()
        if not text:
            QMessageBox.warning(self, t("error"), t("tax_years_no_selection"))
            return
        year = int(text)
        years = self.tax_engine.list_years()
        if len(years) <= 1:
            QMessageBox.warning(self, t("error"), t("tax_years_clone_warn"))
            return
        if QMessageBox.question(
                self, t("tax_years_delete"),
                f"{t('tax_years_delete')} {year}?") != QMessageBox.Yes:
            return
        if tax_years.delete_year(year):
            years_left = self.tax_engine.list_years()
            self.reload_years_combo()
            if years_left:
                self.tax_engine.set_year(max(years_left))
                self.years_active_label.setText(
                    t("tax_years_active") + f" {max(years_left)}")
            self.load_editor_from_year()
            QMessageBox.information(self, t("success"), t("tax_years_deleted"))
        else:
            QMessageBox.warning(self, t("error"), t("tax_years_delete_fail"))

    def load_editor_from_year(self):
        """تحميل إعدادات السنة المختارة في المحرر"""
        text = self.years_combo.currentText() if hasattr(self, "years_combo") else ""
        year = int(text) if text.isdigit() else self.tax_engine.get_config_year()
        data = tax_years.load_year(year)
        if data is not None:
            import json
            self.years_editor.setPlainText(
                json.dumps(data, ensure_ascii=False, indent=2))
        else:
            self.years_editor.setPlainText(t("tax_years_no_selection"))

    def validate_year_config(self):
        """التحقق من سلامة الإعدادات في المحرر"""
        import json
        try:
            data = json.loads(self.years_editor.toPlainText())
        except (ValueError, TypeError):
            QMessageBox.warning(self, t("error"), t("tax_years_imported_fail"))
            return
        errors = tax_years.validate_year_config(data)
        if errors:
            msg = "\n".join("• " + e for e in errors)
            QMessageBox.warning(self, t("tax_years_invalid"), msg)
        else:
            QMessageBox.information(self, t("success"), t("tax_years_valid"))

    def save_year_config(self):
        """حفظ إعدادات السنة الحالية"""
        import json
        text = self.years_combo.currentText()
        if not text:
            QMessageBox.warning(self, t("error"), t("tax_years_no_selection"))
            return
        year = int(text)
        try:
            data = json.loads(self.years_editor.toPlainText())
        except (ValueError, TypeError):
            QMessageBox.warning(self, t("error"), t("tax_years_imported_fail"))
            return
        errors = tax_years.validate_year_config(data)
        if errors:
            msg = "\n".join("• " + e for e in errors)
            QMessageBox.warning(self, t("tax_years_invalid"), msg)
            return
        if tax_years.save_year(year, data):
            self.tax_engine.set_year(year)
            QMessageBox.information(self, t("success"), t("tax_years_saved_ok"))
        else:
            QMessageBox.warning(self, t("error"), t("tax_years_saved_fail"))

    def import_year_json(self):
        """استيراد إعدادات سنة من ملف JSON"""
        text = self.years_combo.currentText()
        if not text:
            QMessageBox.warning(self, t("error"), t("tax_years_no_selection"))
            return
        year = int(text)
        path, _ = QFileDialog.getOpenFileName(
            self, t("tax_years_import"), "", "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            QMessageBox.warning(self, t("error"), t("tax_years_imported_fail"))
            return
        data, errors = tax_years.import_year_from_json(content)
        if errors:
            QMessageBox.warning(self, t("error"),
                                t("tax_years_imported_fail") + "\n" + "\n".join(errors))
            return
        data["year"] = year
        if tax_years.save_year(year, data):
            self.tax_engine.set_year(year)
            self.load_editor_from_year()
            QMessageBox.information(self, t("success"), t("tax_years_imported_ok"))
        else:
            QMessageBox.warning(self, t("error"), t("tax_years_saved_fail"))

    def export_year_json(self):
        """تصدير إعدادات السنة الحالية إلى ملف JSON"""
        text = self.years_combo.currentText()
        if not text:
            QMessageBox.warning(self, t("error"), t("tax_years_no_selection"))
            return
        year = int(text)
        path, _ = QFileDialog.getSaveFileName(
            self, t("tax_years_export"),
            f"tax_config_{year}.json", "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.years_editor.toPlainText())
            QMessageBox.information(self, t("success"), t("tax_years_saved_ok"))
        except OSError:
            QMessageBox.warning(self, t("error"), t("tax_years_saved_fail"))

    # ==================== New Tax Calculators ====================

    def calc_ifu(self):
        """حساب الضريبة الجزافية الوحيدة IFU"""
        turnover = self.ifu_turnover_input.value()
        regimes = ["auto", "production", "other"]
        idx = self.ifu_regime_combo.currentIndex()
        regime = regimes[idx] if 0 <= idx < len(regimes) else "other"
        result = self.tax_engine.calculate_ifu(turnover, regime)
        min_mark = " ⚠️" if result["minimum_applied"] else ""
        self.ifu_result_label.setText(
            f"<b>{t('tax_ifu_amount')}</b> {result['tax_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_ibs_rate')}</b> {result['rate']*100:.1f}%{min_mark}")

    def calc_formation_tax(self):
        """حساب رسم التكوين المهني والتمهين"""
        payroll = self.form_payroll_input.value()
        budget = self.form_budget_input.value()
        apprentice = self.form_apprentice_input.value()
        result = self.tax_engine.calculate_formation_tax(payroll, budget, apprentice)
        self.form_result_label.setText(
            f"<b>{t('tax_formation_formation')}</b> {result['formation_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_formation_apprenticeship')}</b> {result['apprenticeship_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_formation_total')}</b> {result['total']:,.0f} DZD")

    def calc_rental_withholding(self):
        """حساب الاقتطاع من المصدر على الإيجارات"""
        rent = self.rent_amount_input.value()
        kinds = ["residential", "commercial", "professional", "agricultural", "unbuilt"]
        idx = self.rent_kind_combo.currentIndex()
        kind = kinds[idx] if 0 <= idx < len(kinds) else "residential"
        result = self.tax_engine.calculate_rental_withholding(rent, kind)
        prov = t("tax_rental_provisional_hint") if result["provisional"] else ""
        self.rent_result_label.setText(
            f"<b>{t('tax_rental_amount_o')}</b> {result['withholding_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_ibs_rate')}</b> {result['rate']*100:.0f}%<br>{prov}")

    def _on_decl_type_changed(self, index):
        """إظهار حقول الإدخال حسب نوع الإقرار"""
        is_g50 = index == 0
        is_g57 = index == 1
        is_das = index == 2

        for w in [
            self.decl_turnover_lbl, self.decl_turnover_input,
            self.decl_collected_lbl, self.decl_collected_input,
            self.decl_deductible_lbl, self.decl_deductible_input,
            self.decl_credit_lbl, self.decl_credit_input,
        ]:
            w.setVisible(is_g50)

        for w in [
            self.decl_taxable_lbl, self.decl_taxable_input,
            self.decl_activity_lbl, self.decl_activity_combo,
            self.decl_acomptes_lbl, self.decl_acomptes_input,
        ]:
            w.setVisible(is_g57)

        for w in [
            self.decl_payroll_lbl, self.decl_payroll_input,
            self.decl_employees_lbl, self.decl_employees_input,
            self.decl_avg_salary_lbl, self.decl_avg_salary_input,
        ]:
            w.setVisible(is_das)

        self.decl_month_combo.setVisible(is_g50)

    def _prefill_declaration(self):
        """تعبئة الحقول من آخر محاكاة"""
        if not self.last_simulation:
            QMessageBox.warning(self, t("error"), t("tax_enter_revenue"))
            return
        sim = self.last_simulation
        revenue = sim.get("revenue", 0)
        rate = self.tax_engine.get_tva_rates().get("standard", 0.19)

        self.decl_turnover_input.setValue(revenue / 12 if revenue else 0)
        self.decl_collected_input.setValue(revenue * rate if revenue else 0)
        self.decl_deductible_input.setValue(0)
        self.decl_taxable_input.setValue(sim.get("taxable_income", 0))

        ibs_tax = sim.get("ibs", {}).get("tax_amount", 0)
        self.decl_acomptes_input.setValue(round(ibs_tax / 3, 2) if ibs_tax else 0)

        employees = sim.get("employees", {})
        if isinstance(employees, dict):
            count = employees.get("count", 0)
            avg_salary = employees.get("avg_salary", 0)
            self.decl_employees_input.setValue(count)
            self.decl_avg_salary_input.setValue(avg_salary)
            self.decl_payroll_input.setValue(count * avg_salary)

    def _build_declaration_data(self):
        """بناء بيانات الإقرار من الحقول"""
        company_info = {
            "company_name": self.decl_name_input.text().strip(),
            "nif": self.decl_nif_input.text().strip(),
            "rc": self.decl_rc_input.text().strip(),
            "ai": self.decl_ai_input.text().strip(),
            "address": self.decl_address_input.text().strip(),
            "dgi_center": self.decl_dgi_input.text().strip(),
        }
        year = int(self.decl_year_combo.currentText())
        idx = self.decl_type_combo.currentIndex()

        if idx == 0:
            decl_type = "g50"
            data = {
                "header": tax_declaration_generator.build_header(company_info, year),
                "month": self.decl_month_combo.currentIndex() + 1,
                "year": year,
                "monthly_turnover": self._get_float(self.decl_turnover_input),
                "tva_collected": self._get_float(self.decl_collected_input),
                "tva_deductible": self._get_float(self.decl_deductible_input),
                "previous_credit": self._get_float(self.decl_credit_input),
            }
        elif idx == 1:
            decl_type = "g57"
            data = {
                "header": tax_declaration_generator.build_header(company_info, year),
                "taxable_income": self._get_float(self.decl_taxable_input),
                "acomptes_paid": self._get_float(self.decl_acomptes_input),
                "activity_type": self._get_activity_type(self.decl_activity_combo),
            }
        else:
            decl_type = "das"
            data = {
                "header": tax_declaration_generator.build_header(company_info, year),
                "monthly_payroll": self._get_float(self.decl_payroll_input),
                "number_of_employees": int(self._get_float(self.decl_employees_input) or 0),
                "avg_salary": self._get_float(self.decl_avg_salary_input),
            }
        return decl_type, data

    def _generate_declaration(self):
        """توليد ومعاينة الإقرار"""
        decl_type, data = self._build_declaration_data()
        declaration = tax_declaration_generator.generate(decl_type, data)
        self._current_declaration = declaration
        self.decl_preview.setPlainText(tax_declaration_generator.render_text(declaration))

    def _export_declaration_pdf(self):
        """تصدير الإقرار إلى PDF"""
        if not self._current_declaration:
            QMessageBox.warning(self, t("error"), t("taxdecl_no_data"))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t("taxdecl_export_pdf"), "declaration.pdf", "PDF Files (*.pdf)"
        )
        if not file_path:
            return
        if tax_declaration_generator.export_pdf(self._current_declaration, file_path):
            QMessageBox.information(self, t("success"), f"✅ {t('taxdecl_success')}\n{file_path}")
        else:
            QMessageBox.critical(self, t("error"), t("taxdecl_success"))

    def _export_declaration_excel(self):
        """تصدير الإقرار إلى Excel"""
        if not self._current_declaration:
            QMessageBox.warning(self, t("error"), t("taxdecl_no_data"))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t("taxdecl_export_excel"), "declaration.xlsx", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return
        if tax_declaration_generator.export_excel(self._current_declaration, file_path):
            QMessageBox.information(self, t("success"), f"✅ {t('taxdecl_success')}\n{file_path}")
        else:
            QMessageBox.critical(self, t("error"), t("taxdecl_success"))

    def _get_float(self, input_field):
        """استخراج قيمة عددية من حقل"""
        try:
            if isinstance(input_field, QDoubleSpinBox):
                return input_field.value()
            text = input_field.text().strip().replace(",", "")
            if not text:
                return 0.0
            return float(text)
        except (ValueError, AttributeError):
            return None

    def _get_activity_type(self, combo):
        """استخراج نوع النشاط من القائمة"""
        idx = combo.currentIndex()
        if idx == 0:
            return "production"
        elif idx == 1:
            return "construction"
        return "other"

    def _populate_results_table(self, results):
        """ملء جدول النتائج"""
        rows = [
            (t("tax_res_revenue"), f"{results.get('revenue', 0):,.0f} DZD"),
            (t("tax_res_gross_profit"), f"{results.get('gross_profit', 0):,.0f} DZD"),
            (t("tax_res_operating"), f"{results.get('operating_income', 0):,.0f} DZD"),
            (t("tax_res_taxable"), f"{results.get('taxable_income', 0):,.0f} DZD"),
            ("", ""),
            (t("tax_res_ibs"), f"{results.get('ibs', {}).get('tax_amount', 0):,.0f} DZD"),
            (t("tax_res_rate"), f"{results.get('ibs', {}).get('effective_rate', 0):.2f}%"),
            ("", ""),
            (t("tax_res_cnas"), f"{results.get('cnas_annual', 0):,.0f} DZD"),
            (t("tax_res_cnac"), f"{results.get('cnac_annual', 0):,.0f} DZD"),
            (t("tax_res_irg"), f"{results.get('irg_annual', 0):,.0f} DZD"),
            (t("tax_res_vf"), f"{results.get('vf_annual', 0):,.0f} DZD"),
            ("", ""),
            (t("tax_res_total"), f"{results.get('total_taxes', 0):,.0f} DZD"),
            (t("tax_res_burden"), f"{results.get('tax_burden_pct', 0):.2f}%"),
            (t("tax_res_net"), f"{results.get('net_income_after_taxes', 0):,.0f} DZD"),
        ]

        self.results_table.setRowCount(len(rows))
        for i, (label, value) in enumerate(rows):
            label_item = QTableWidgetItem(label)
            value_item = QTableWidgetItem(value)
            label_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            value_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            if i == 12:
                label_item.setForeground(QColor(ThemeColors.get('error')))
                value_item.setForeground(QColor(ThemeColors.get('error')))
                font = label_item.font()
                font.setBold(True)
                label_item.setFont(font)
                value_item.setFont(font)
            elif i == 14:
                label_item.setForeground(QColor(ThemeColors.get('success')))
                value_item.setForeground(QColor(ThemeColors.get('success')))
                font = label_item.font()
                font.setBold(True)
                label_item.setFont(font)
                value_item.setFont(font)
            self.results_table.setItem(i, 0, label_item)
            self.results_table.setItem(i, 1, value_item)

    def _build_detail_text(self, results):
        """بناء النص التفصيلي"""
        ibs = results.get("ibs", {})
        employees = results.get("employees", {})
        lines = [
            f"<b>{t('tax_detail_title')} — {results.get('config_year', '')}</b>",
            f"<b>🏢 IBS ({ibs.get('activity_type', '')}):</b>",
            f"  {t('tax_detail_income')} {ibs.get('taxable_income', 0):,.0f} DZD",
            f"  {t('tax_detail_rate')} {ibs.get('rate_used', 0)*100:.0f}%",
            f"  {t('tax_detail_tax')} {ibs.get('tax_amount', 0):,.0f} DZD",
            f"  {t('tax_detail_minimum')} {t('tax_detail_yes') if ibs.get('minimum_applied') else t('tax_detail_no')}",
        ]
        if isinstance(employees, dict) and employees.get("count", 0) > 0:
            emp = employees
            lines.append(f"<b>{t('tax_detail_employees')} ({emp['count']}):</b>")
            cnas_e = emp.get("cnas_per_employee", {})
            irg_e = emp.get("irg_per_employee", {})
            lines.append(f"  {t('tax_detail_cnas')} {cnas_e.get('employer_amount', 0):,.0f} / {cnas_e.get('employee_amount', 0):,.0f}")
            lines.append(f"  {t('tax_detail_irg')} {irg_e.get('monthly_irg', 0):,.0f}")
            lines.append(f"  {t('tax_detail_net_salary')} {emp.get('net_salary_per_employee', 0):,.0f}")
        return "<br>".join(lines)

    # ==================== Simulation ====================

    def run_simulation(self):
        """تشغيل المحاكاة الشاملة"""
        revenue = self._get_float(self.revenue_input)
        cogs = self._get_float(self.cogs_input)
        opex = self._get_float(self.opex_input)
        assets = self._get_float(self.assets_input)
        liabilities = self._get_float(self.liabilities_input)
        equity = self._get_float(self.equity_input)
        employees = self._get_float(self.employees_input)
        avg_salary = self._get_float(self.avg_salary_input)

        if revenue is None or cogs is None or opex is None:
            QMessageBox.warning(self, t("error"), t("tax_enter_all"))
            return

        activity_type = self._get_activity_type(self.activity_combo)
        is_construction = self.construction_check.isChecked()

        result = self.tax_engine.simulate(
            revenue=revenue, cogs=cogs, operating_expenses=opex,
            total_assets=assets or 0, total_liabilities=liabilities or 0,
            equity=equity or 0, number_of_employees=int(employees or 0),
            avg_salary=avg_salary or 0, activity_type=activity_type,
            is_construction=is_construction
        )

        self.last_simulation = result
        self._populate_results_table(result)
        self.detail_text.setHtml(self._build_detail_text(result))

        state.tax_summary = result
        self.data_changed.emit()

        from modules.fraud_detection import fraud_detector
        if state.financial_data and result:
            fraud_detector.check_tax_consistency(state.financial_data, result)

    def save_simulation(self):
        """حفظ المحاكاة"""
        if not self.last_simulation:
            QMessageBox.warning(self, t("error"), t("tax_enter_revenue"))
            return
        state.tax_summary = self.last_simulation
        self.data_changed.emit()
        QMessageBox.information(self, t("success"), t("tax_simulation_saved"))

    # ==================== Tax Calculators ====================

    def calc_ibs(self):
        """حساب IBS"""
        income = self._get_float(self.ibs_income_input)
        if income is None:
            QMessageBox.warning(self, t("error"), t("tax_enter_all"))
            return
        activity = self._get_activity_type(self.ibs_activity_combo)
        result = self.tax_engine.calculate_ibs(income, activity)
        self.ibs_result_label.setText(
            f"<b>{t('tax_ibs_amount')}</b> {result['tax_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_ibs_effective')}</b> {result['effective_rate']:.2f}%<br>"
            f"<b>{t('tax_ibs_rate')}</b> {result['rate_used']*100:.0f}%"
        )

    def calc_tva(self):
        """حساب TVA"""
        amount = self._get_float(self.tva_amount_input)
        if amount is None:
            QMessageBox.warning(self, t("error"), t("tax_enter_all"))
            return
        rate_types = ["standard", "reduced", "intermediate", "zero"]
        idx = self.tva_rate_combo.currentIndex()
        rate_type = rate_types[idx] if 0 <= idx < len(rate_types) else "standard"
        result = self.tax_engine.calculate_tva(amount, rate_type)
        self.tva_result_label.setText(
            f"<b>{t('tax_tva_amount')}</b> {result['tva_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_total_with_tva')}</b> {result['total_with_tax']:,.0f} DZD<br>"
            f"<b>{t('tax_rate_label')}</b> {result['rate_used']*100:.0f}%"
        )

    def calc_irg(self):
        """حساب IRG"""
        salary = self._get_float(self.irg_salary_input)
        if salary is None:
            QMessageBox.warning(self, t("error"), t("tax_enter_all"))
            return
        annual = salary * 12
        result = self.tax_engine.calculate_irg(annual)
        net_before_irg = salary - result["monthly_irg"]
        self.irg_result_label.setText(
            f"<b>{t('tax_irg_monthly')}</b> {result['monthly_irg']:,.0f} DZD<br>"
            f"<b>{t('tax_irg_effective')}</b> {result['effective_rate']:.2f}%<br>"
            f"<b>{t('tax_irg_marginal')}</b> {result['marginal_rate']*100:.0f}%<br>"
            f"<b>{t('tax_irg_net_monthly')}</b> {result['net_monthly']:,.0f} DZD"
        )

    def calc_cnas(self):
        """حساب CNAS"""
        salary = self._get_float(self.cnas_salary_input)
        if salary is None:
            QMessageBox.warning(self, t("error"), t("tax_enter_all"))
            return
        result = self.tax_engine.calculate_cnas(salary)
        self.cnas_result_label.setText(
            f"<b>{t('tax_cnas_employer')}</b> {result['employer_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_cnas_employee')}</b> {result['employee_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_cnas_total')}</b> {result['total']:,.0f} DZD<br>"
            f"<b>{t('tax_net_before_irg')}</b> {result['net_salary_before_irg']:,.0f} DZD"
        )

    def calc_cnac(self):
        """حساب CNAC"""
        salary = self._get_float(self.cnac_salary_input)
        if salary is None:
            QMessageBox.warning(self, t("error"), t("tax_enter_all"))
            return
        result = self.tax_engine.calculate_cnac(salary)
        self.cnac_result_label.setText(
            f"<b>{t('tax_cnac_employer')}</b> {result['employer_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_cnac_employee')}</b> {result['employee_amount']:,.0f} DZD<br>"
            f"<b>{t('tax_cnac_total')}</b> {result['total']:,.0f} DZD"
        )

    def calc_payroll(self):
        """حساب الرواتب الشامل"""
        salary = self._get_float(self.payroll_salary_input)
        if salary is None:
            QMessageBox.warning(self, t("error"), t("tax_enter_all"))
            return
        is_construction = self.construction_check.isChecked()
        result = self.tax_engine.calculate_payroll(salary, is_construction)
        irg = result.get("irg", {})
        self.payroll_result_label.setText(
            f"<b>{t('tax_gross_salary')}</b> {result['gross_salary']:,.0f} DZD<br>"
            f"<b>{t('tax_cnas_total')}</b> {result['cnas']['total']:,.0f} DZD<br>"
            f"<b>{t('tax_cnac_total')}</b> {result['cnac']['total']:,.0f} DZD<br>"
            f"<b>{t('tax_irg_monthly')}</b> {irg.get('monthly_irg', 0):,.0f} DZD<br>"
            f"<b>{t('tax_vf_amount')}</b> {result['vf']['amount']:,.0f} DZD<br>"
            f"<b>─────────────────</b><br>"
            f"<b>{t('tax_net_before_irg')}</b> {result['total_deductions_employee']:,.0f} DZD<br>"
            f"<b>{t('tax_irg_net_monthly')}</b> <span style='color: {ThemeColors.get('success')}; font-size: 13pt;'>{result['net_salary']:,.0f} DZD</span><br>"
            f"<b>{t('tax_total_cost')}</b> {result['total_cost_employer']:,.0f} DZD"
        )

    # ==================== Obligations ====================

    def show_obligations(self):
        """عرض الالتزامات الجبائية"""
        month = self.oblig_month_combo.currentIndex()
        if month == 0:
            obligations = []
            for m in range(1, 13):
                obligations.extend(self.tax_engine.get_obligations(m))
        else:
            obligations = self.tax_engine.get_obligations(month)

        self.oblig_table.setRowCount(len(obligations))
        self.oblig_table.setHorizontalHeaderLabels([
            t("tax_oblig_type"),
            t("tax_oblig_day"),
            t("tax_oblig_amount"),
            t("tax_oblig_status")
        ])
        for i, ob in enumerate(obligations):
            type_item = QTableWidgetItem(ob.get("tax_type", ""))
            day_item = QTableWidgetItem(str(ob.get("due_day", 20)))
            amount_item = QTableWidgetItem(f"{ob.get('amount', 0):,.0f} DZD")
            status_item = QTableWidgetItem(ob.get("status", ""))

            type_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            day_item.setTextAlignment(Qt.AlignCenter)
            amount_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            status_item.setTextAlignment(Qt.AlignCenter)

            status = ob.get("status", "")
            if status == "paid":
                status_item.setForeground(QColor(ThemeColors.get('success')))
            elif status == "overdue":
                status_item.setForeground(QColor(ThemeColors.get('error')))
            else:
                status_item.setForeground(QColor(ThemeColors.get('warning')))

            self.oblig_table.setItem(i, 0, type_item)
            self.oblig_table.setItem(i, 1, day_item)
            self.oblig_table.setItem(i, 2, amount_item)
            self.oblig_table.setItem(i, 3, status_item)

    # ==================== Retranslate ====================

    def retranslate(self):
        """تحديث الترجمات"""
        self.title_label.setText(t("tax_title"))
        self.subtitle_label.setText(t("tax_subtitle"))
        self.simulate_btn.setText(t("tax_simulate"))
        self.save_btn.setText(t("tax_save_simulation"))
        self.ibs_calc_btn.setText(t("tax_calc_ibs"))
        self.tva_calc_btn.setText(t("tax_calc_tva"))
        self.irg_calc_btn.setText(t("tax_calc_irg"))
        self.cnas_calc_btn.setText(t("tax_calc_cnas"))
        self.cnac_calc_btn.setText(t("tax_calc_cnac"))
        self.payroll_calc_btn.setText(t("tax_payroll_calc"))
        self.oblig_show_btn.setText(t("tax_oblig_show"))

        self.results_table.setHorizontalHeaderLabels([t("tax_table_item"), t("tax_table_value")])
        self.oblig_table.setHorizontalHeaderLabels([
            t("tax_oblig_type"), t("tax_oblig_day"),
            t("tax_oblig_amount"), t("tax_oblig_status")
        ])

        current_month = self.oblig_month_combo.currentIndex()
        self.oblig_month_combo.clear()
        self.oblig_month_combo.addItems([
            "", t("tax_month_jan"), t("tax_month_feb"), t("tax_month_mar"),
            t("tax_month_apr"), t("tax_month_may"), t("tax_month_jun"),
            t("tax_month_jul"), t("tax_month_aug"), t("tax_month_sep"),
            t("tax_month_oct"), t("tax_month_nov"), t("tax_month_dec")
        ])
        self.oblig_month_combo.setCurrentIndex(current_month)

        self.oblig_info.setHtml(f"""
        <b>{t('tax_oblig_info')}</b><br>
        • {t('tax_oblig_info_day')}
        """)

        current_rate = self.tva_rate_combo.currentIndex()
        self.tva_rate_combo.clear()
        self.tva_rate_combo.addItems([
            t("tax_rate_standard"),
            t("tax_rate_reduced"),
            t("tax_rate_intermediate"),
            t("tax_rate_zero")
        ])
        self.tva_rate_combo.setCurrentIndex(current_rate)

        self.decl_company_group.setTitle(t("taxdecl_company_group"))
        self.decl_period_group.setTitle(t("taxdecl_period_group"))
        self.decl_data_group.setTitle(t("taxdecl_data_group"))
        self.decl_preview_group.setTitle(t("taxdecl_preview_group"))

        company_fields = [
            (self.decl_name_input, "taxdecl_company_name"),
            (self.decl_nif_input, "taxdecl_nif"),
            (self.decl_rc_input, "taxdecl_rc"),
            (self.decl_ai_input, "taxdecl_ai"),
            (self.decl_address_input, "taxdecl_address"),
            (self.decl_dgi_input, "taxdecl_dgi"),
        ]
        for field, key in company_fields:
            label = self.decl_company_form.labelForField(field)
            if label:
                label.setText(t(key))

        current_type = self.decl_type_combo.currentIndex()
        self.decl_type_combo.blockSignals(True)
        self.decl_type_combo.clear()
        self.decl_type_combo.addItems([
            t("taxdecl_g50"), t("taxdecl_g57"), t("taxdecl_das")
        ])
        self.decl_type_combo.setCurrentIndex(current_type)
        self.decl_type_combo.blockSignals(False)
        label = self.decl_period_form.labelForField(self.decl_type_combo)
        if label:
            label.setText(t("taxdecl_type"))

        current_month = self.decl_month_combo.currentIndex()
        self.decl_month_combo.clear()
        self.decl_month_combo.addItems([
            t("tax_month_jan"), t("tax_month_feb"), t("tax_month_mar"),
            t("tax_month_apr"), t("tax_month_may"), t("tax_month_jun"),
            t("tax_month_jul"), t("tax_month_aug"), t("tax_month_sep"),
            t("tax_month_oct"), t("tax_month_nov"), t("tax_month_dec")
        ])
        self.decl_month_combo.setCurrentIndex(current_month)
        label = self.decl_period_form.labelForField(self.decl_month_combo)
        if label:
            label.setText(t("taxdecl_month"))
        label = self.decl_period_form.labelForField(self.decl_year_combo)
        if label:
            label.setText(t("taxdecl_year"))

        current_activity = self.decl_activity_combo.currentIndex()
        self.decl_activity_combo.clear()
        self.decl_activity_combo.addItems([
            t("tax_activity_production"),
            t("tax_activity_construction"),
            t("tax_activity_other")
        ])
        self.decl_activity_combo.setCurrentIndex(current_activity)

        data_labels = [
            (self.decl_turnover_lbl, "taxdecl_turnover"),
            (self.decl_collected_lbl, "taxdecl_collected"),
            (self.decl_deductible_lbl, "taxdecl_deductible"),
            (self.decl_credit_lbl, "taxdecl_previous_credit"),
            (self.decl_taxable_lbl, "taxdecl_taxable"),
            (self.decl_activity_lbl, "taxdecl_activity"),
            (self.decl_acomptes_lbl, "taxdecl_acomptes_paid"),
            (self.decl_payroll_lbl, "taxdecl_payroll"),
            (self.decl_employees_lbl, "taxdecl_employees"),
            (self.decl_avg_salary_lbl, "taxdecl_avg_salary"),
        ]
        for label, key in data_labels:
            label.setText(t(key))

        self.decl_prefill_btn.setText(t("taxdecl_prefill"))
        self.decl_generate_btn.setText(t("taxdecl_generate"))
        self.decl_export_pdf_btn.setText(t("taxdecl_export_pdf"))
        self.decl_export_excel_btn.setText(t("taxdecl_export_excel"))
        self.decl_preview.setPlaceholderText(t("taxdecl_preview_empty"))

        current_tab = self.tabs.currentIndex()
        self.tabs.setTabText(0, t("tax_tab_simulation"))
        self.tabs.setTabText(1, t("tax_tab_calculators"))
        self.tabs.setTabText(2, t("tax_tab_obligations"))
        self.tabs.setTabText(3, t("taxdecl_tab"))
        self.tabs.setTabText(4, t("tax_tab_years"))
        self.tabs.setCurrentIndex(current_tab)
