# واجهة الشركات التجريبية
# =========================
# شركات تجريبية (تجارية/خدمات/إنتاج/استيراد-تصدير) + معاملات شهرية نموذجية
# + تقارير مُعدّة مسبقاً + قوالب استيراد/تصدير CSV

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QHeaderView, QHBoxLayout, QTextEdit, QGridLayout,
)
from ui.views._base import BaseView
from ui.app_state import state
from ui.resources.i18n import t
from modules.demo_data import DemoData
from modules.demo_templates import (
    write_templates, export_company_csv, generate_demo_reports,
)
from modules.calculations import CalculationEngine


class DemoDataView(BaseView):
    """عرض وتحميل الشركات التجريبية والمعاملات النموذجية"""

    def __init__(self):
        super().__init__()
        self._companies = DemoData.list_companies()
        self._engine = CalculationEngine()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("demo_title", "demo_subtitle")

        # 1) اختيار الشركة
        select_card = self._make_card("demo_select_company")
        select_row = QHBoxLayout()
        select_row.addWidget(QLabel(t("demo_company")))
        self.company_combo = QComboBox()
        self.company_combo.currentIndexChanged.connect(self._on_company_changed)
        select_row.addWidget(self.company_combo, 1)
        self.load_btn = QPushButton(t("demo_load"))
        self.load_btn.setObjectName("primaryBtn")
        self.load_btn.clicked.connect(self._load_company)
        select_row.addWidget(self.load_btn)
        select_card.layout().addLayout(select_row)
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #888;")
        select_card.layout().addWidget(self.desc_label)
        self._main_layout.addWidget(select_card)

        # 2) بطاقات المؤشرات
        stats_grid = QGridLayout()
        stats_grid.setSpacing(12)
        self.stat_revenue = self._make_stat_card(t("demo_revenue"))
        self.stat_net_income = self._make_stat_card(t("demo_net_income"))
        self.stat_assets = self._make_stat_card(t("demo_total_assets"))
        self.stat_roe = self._make_stat_card(t("demo_roe"))
        for i, stat in enumerate((self.stat_revenue, self.stat_net_income,
                                  self.stat_assets, self.stat_roe)):
            stats_grid.addWidget(stat, 0, i)
        self._main_layout.addLayout(stats_grid)

        # 3) المعاملات الشهرية النموذجية
        tx_card = self._make_card("demo_monthly_title")
        self.tx_table = QTableWidget()
        self.tx_table.setColumnCount(9)
        self.tx_table.setHorizontalHeaderLabels([
            t("demo_month"), t("demo_revenue"), t("demo_cogs"),
            t("demo_opex"), t("demo_net_income"), t("demo_cash"),
            t("demo_ar"), t("demo_inventory"), t("demo_payables"),
        ])
        self.tx_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tx_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tx_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tx_table.verticalHeader().setDefaultSectionSize(44)
        self.tx_table.setMinimumHeight(44 * 13 + 40)
        tx_card.layout().addWidget(self.tx_table)
        self._main_layout.addWidget(tx_card)

        # 4) تقرير مُعد مسبقاً
        report_card = self._make_card("demo_report_title")
        actions_row = QHBoxLayout()
        self.report_btn = QPushButton(t("demo_report_btn"))
        self.report_btn.clicked.connect(self._show_report)
        actions_row.addWidget(self.report_btn)
        self.export_btn = QPushButton(t("demo_export_btn"))
        self.export_btn.clicked.connect(self._export_csv)
        actions_row.addWidget(self.export_btn)
        self.templates_btn = QPushButton(t("demo_templates_btn"))
        self.templates_btn.clicked.connect(self._generate_templates)
        actions_row.addWidget(self.templates_btn)
        actions_row.addStretch()
        report_card.layout().addLayout(actions_row)

        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setMinimumHeight(220)
        report_card.layout().addWidget(self.report_preview)
        self._main_layout.addWidget(report_card)

        self._main_layout.addStretch()

    # ===== التحديث =====

    def refresh(self):
        self.company_combo.blockSignals(True)
        self.company_combo.clear()
        for company in self._companies:
            label = t("demo_industry_" + company["industry"])
            self.company_combo.addItem(
                f"{company['company_name']} — {label}", company["id"]
            )
        self.company_combo.blockSignals(False)
        if self._companies:
            self.company_combo.setCurrentIndex(0)
            self._on_company_changed(0)

    def _current_company_id(self):
        return self.company_combo.currentData()

    def _current_company(self):
        return DemoData.get_company(self._current_company_id())

    def _on_company_changed(self, _index):
        company = self._current_company()
        if not company:
            return
        fd = company["financial_data"]
        self.stat_revenue.layout().itemAt(1).widget().setText(
            f"{fd.get('revenue', 0):,.0f}"
        )
        self.stat_net_income.layout().itemAt(1).widget().setText(
            f"{fd.get('net_income', 0):,.0f}"
        )
        self.stat_assets.layout().itemAt(1).widget().setText(
            f"{fd.get('total_assets', 0):,.0f}"
        )
        ratios = self._engine.calculate_all_ratios(fd) or {}
        self.stat_roe.layout().itemAt(1).widget().setText(
            f"{ratios.get('roe', 0):.2f}%"
        )
        self.desc_label.setText(t("demo_industry_desc_" + company["industry"]))
        self._refresh_tx_table(company["id"])
        self._refresh_report_preview(company["id"])

    def _refresh_tx_table(self, company_id):
        rows = DemoData.get_monthly_transactions(company_id)
        self.tx_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.tx_table.setItem(r, 0, QTableWidgetItem(str(row["month"])))
            for col, key in enumerate(
                    ("revenue", "cost_of_goods_sold", "operating_expenses",
                     "net_income", "cash", "accounts_receivable",
                     "inventory", "accounts_payable"), start=1):
                self.tx_table.setItem(
                    r, col, QTableWidgetItem(f"{row[key]:,.0f}")
                )

    def _refresh_report_preview(self, company_id):
        reports = generate_demo_reports(company_id)
        if not reports:
            self.report_preview.setPlainText(t("demo_error"))
            return
        preview = (
            reports.get("balance_sheet", "")
            + "\n\n" + reports.get("income_statement", "")
            + "\n\n" + reports.get("ratios", "")
        )
        self.report_preview.setPlainText(preview)

    # ===== الإجراءات =====

    def _load_company(self):
        company_id = self._current_company_id()
        if not company_id:
            return
        reply = QMessageBox.question(
            self, t("confirm"), t("demo_load_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        if DemoData.load_company(state, company_id):
            QMessageBox.information(self, t("demo_title"), t("demo_loaded"))
        else:
            QMessageBox.critical(self, t("demo_title"), t("demo_error"))

    def _show_report(self):
        company_id = self._current_company_id()
        if not company_id:
            return
        self._refresh_report_preview(company_id)
        QMessageBox.information(self, t("demo_report_title"), t("demo_report_generated"))

    def _export_csv(self):
        company_id = self._current_company_id()
        if not company_id:
            return
        directory = QFileDialog.getExistingDirectory(
            self, t("demo_export_btn"), ""
        )
        if not directory:
            return
        paths = export_company_csv(directory, company_id)
        if paths:
            QMessageBox.information(
                self, t("demo_title"),
                f"{t('demo_exported')}\n" + "\n".join(paths)
            )

    def _generate_templates(self):
        directory = QFileDialog.getExistingDirectory(
            self, t("demo_templates_btn"), ""
        )
        if not directory:
            return
        paths = write_templates(directory)
        if paths:
            QMessageBox.information(
                self, t("demo_title"),
                f"{t('demo_templates_generated')}\n" + "\n".join(paths)
            )
