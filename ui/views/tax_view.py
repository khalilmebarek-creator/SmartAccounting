# واجهة النظام الجبائي الجزائري
# ==============================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDoubleSpinBox, QComboBox, QGroupBox, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QMessageBox, QTextEdit,
    QTabWidget, QFormLayout, QHeaderView, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.tax import TaxEngine


class TaxView(QWidget):
    """واجهة النظام الجبائي الجزائري"""

    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tax_engine = TaxEngine()
        self.last_simulation = None
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
        idx = self.tva_rate_combo.currentIndex()
        if idx == 0:
            rate_type = "standard"
        elif idx == 1:
            rate_type = "reduced"
        else:
            rate_type = "zero"
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

        current_tab = self.tabs.currentIndex()
        self.tabs.setTabText(0, t("tax_tab_simulation"))
        self.tabs.setTabText(1, t("tax_tab_calculators"))
        self.tabs.setTabText(2, t("tax_tab_obligations"))
        self.tabs.setCurrentIndex(current_tab)
