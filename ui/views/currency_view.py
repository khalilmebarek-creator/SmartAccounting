# واجهة تعدد العملات
# ====================
# إدارة العملات + أسعار الصرف + محول + تقرير متعدد العملات + تصدير CSV

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QLineEdit, QDoubleSpinBox, QMessageBox, QFileDialog, QHeaderView,
    QHBoxLayout
)
from ui.views._base import BaseView
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.currency import CurrencyEngine, currency_engine

_ITEM_KEYS = {
    "revenue": "revenue",
    "cost_of_goods_sold": "currency_item_cogs",
    "gross_profit": "currency_item_gross_profit",
    "operating_expenses": "currency_item_opex",
    "operating_income": "currency_item_operating_income",
    "interest_expense": "currency_item_interest",
    "tax_expense": "currency_item_tax_expense",
    "net_income": "net_income",
    "current_assets": "current_assets",
    "non_current_assets": "currency_item_non_current_assets",
    "total_assets": "total_assets",
    "current_liabilities": "current_liabilities",
    "non_current_liabilities": "currency_item_non_current_liabilities",
    "total_liabilities": "total_liabilities",
    "share_capital": "currency_item_share_capital",
    "retained_earnings": "currency_item_retained_earnings",
    "total_equity": "currency_item_total_equity",
    "cash": "cash",
    "inventory": "inventory",
    "average_receivables": "currency_item_avg_receivables",
    "average_payables": "currency_item_avg_payables",
}


class CurrencyView(BaseView):
    """إدارة تعدد العملات"""

    def __init__(self):
        super().__init__()
        self._engine = CurrencyEngine(
            base_currency=currency_engine.base_currency,
            rates=currency_engine.rates,
            currencies=currency_engine.currencies,
        )
        self.setup_ui()
        self.refresh()

    # ===== البناء =====

    def setup_ui(self):
        self._make_header("currency_title", "currency_subtitle")

        # 1) الإعدادات
        settings_card = self._make_card("currency_settings")
        base_row = QHBoxLayout()
        base_row.addWidget(QLabel(t("currency_base")))
        self.base_combo = QComboBox()
        self.base_combo.currentTextChanged.connect(self._on_base_changed)
        base_row.addWidget(self.base_combo)
        base_row.addStretch()
        settings_card.layout().addLayout(base_row)

        self.rates_table = QTableWidget()
        self.rates_table.setColumnCount(4)
        self.rates_table.setHorizontalHeaderLabels([
            t("currency_table_code"), t("currency_table_name"),
            t("currency_table_symbol"), t("currency_table_rate"),
        ])
        self.rates_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rates_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rates_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.rates_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        settings_card.layout().addWidget(self.rates_table)

        add_row = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(t("currency_code"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("currency_name"))
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText(t("currency_symbol"))
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0.0001, 1_000_000_000.0)
        self.rate_input.setDecimals(6)
        self.rate_input.setValue(1.0)
        self.rate_input.setPrefix(t("currency_rate") + " ")
        add_btn = QPushButton(t("currency_add"))
        add_btn.clicked.connect(self._add_currency)
        del_btn = QPushButton(t("currency_delete"))
        del_btn.clicked.connect(self._delete_currency)
        save_btn = QPushButton(t("currency_save"))
        save_btn.clicked.connect(self._save)
        for w in (self.code_input, self.name_input, self.symbol_input,
                  self.rate_input, add_btn, del_btn, save_btn):
            add_row.addWidget(w)
        settings_card.layout().addLayout(add_row)
        self._main_layout.addWidget(settings_card)

        # 2) المحول
        conv_card = self._make_card("currency_converter")
        conv_row = QHBoxLayout()
        conv_row.addWidget(QLabel(t("currency_amount")))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.0, 1e15)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(1000.0)
        conv_row.addWidget(self.amount_input)
        conv_row.addWidget(QLabel(t("currency_from")))
        self.from_combo = QComboBox()
        conv_row.addWidget(self.from_combo)
        conv_row.addWidget(QLabel(t("currency_to")))
        self.to_combo = QComboBox()
        conv_row.addWidget(self.to_combo)
        convert_btn = QPushButton(t("currency_convert"))
        convert_btn.clicked.connect(self._convert)
        conv_row.addWidget(convert_btn)
        conv_card.layout().addLayout(conv_row)
        self.convert_result = QLabel("")
        self.convert_result.setObjectName("statValue")
        self.convert_result.setStyleSheet(
            f"color: {ThemeColors.get('success')}; font-size: 16px;"
        )
        conv_card.layout().addWidget(self.convert_result)
        self._main_layout.addWidget(conv_card)

        # 3) التقرير متعدد العملات
        report_card = self._make_card("currency_report")
        rep_row = QHBoxLayout()
        rep_row.addWidget(QLabel(t("currency_report_target")))
        self.report_combo = QComboBox()
        self.report_combo.currentTextChanged.connect(self._refresh_report)
        rep_row.addWidget(self.report_combo)
        rep_row.addStretch()
        export_btn = QPushButton(t("currency_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        rep_row.addWidget(export_btn)
        report_card.layout().addLayout(rep_row)

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels([
            t("currency_table_name"), t("currency_table_rate"),
            t("currency_report_target"),
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        report_card.layout().addWidget(self.report_table)
        self.no_data_label = QLabel(t("currency_no_data"))
        self.no_data_label.setStyleSheet("color: #888;")
        report_card.layout().addWidget(self.no_data_label)
        self._main_layout.addWidget(report_card)

        self._main_layout.addStretch()

    # ===== التحديث =====

    def refresh(self):
        codes = self._engine.supported_currencies()
        self.base_combo.blockSignals(True)
        self.base_combo.clear()
        self.base_combo.addItems(codes)
        self.base_combo.setCurrentText(self._engine.base_currency)
        self.base_combo.blockSignals(False)

        for combo in (self.from_combo, self.to_combo, self.report_combo):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(codes)
            combo.blockSignals(False)
        self.from_combo.setCurrentText(self._engine.base_currency)
        self.to_combo.setCurrentText(
            next((c for c in codes if c != self._engine.base_currency), self._engine.base_currency)
        )
        self.report_combo.setCurrentText(
            next((c for c in codes if c != self._engine.base_currency), self._engine.base_currency)
        )

        self._refresh_rates_table()
        self._refresh_report()

    def _refresh_rates_table(self):
        codes = self._engine.supported_currencies()
        self.rates_table.setRowCount(len(codes))
        for row, code in enumerate(codes):
            meta = self._engine.currencies.get(code, {})
            self.rates_table.setItem(row, 0, QTableWidgetItem(code))
            self.rates_table.setItem(
                row, 1,
                QTableWidgetItem(meta.get("name_ar", code) or code),
            )
            self.rates_table.setItem(
                row, 2, QTableWidgetItem(meta.get("symbol", code) or code),
            )
            self.rates_table.setItem(
                row, 3,
                QTableWidgetItem(f"{self._engine.get_rate(code):,.4f}"),
            )

    def _refresh_report(self):
        target = self.report_combo.currentText() or self._engine.base_currency
        rows = self._engine.report(state.financial_data, target)
        if not rows:
            self.report_table.setRowCount(0)
            self.no_data_label.show()
            return
        self.no_data_label.hide()
        self.report_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            label_key = _ITEM_KEYS.get(row["item"], row["item"])
            self.report_table.setItem(r, 0, QTableWidgetItem(t(label_key)))
            self.report_table.setItem(
                r, 1, QTableWidgetItem(f"{row['amount']:,.2f} {self._engine.symbol(self._engine.base_currency)}")
            )
            self.report_table.setItem(
                r, 2, QTableWidgetItem(f"{row['converted']:,.2f} {self._engine.symbol(target)}")
            )

    # ===== الإجراءات =====

    def _on_base_changed(self, code):
        if code:
            self._engine.set_base_currency(code)
            self._persist()
            self._refresh_rates_table()
            self._refresh_report()

    def _add_currency(self):
        code = self.code_input.text().strip().upper()
        name = self.name_input.text().strip()
        symbol = self.symbol_input.text().strip()
        rate = self.rate_input.value()
        if not code:
            return
        self._engine.add_currency(code, name or None, symbol or None, rate)
        self.code_input.clear()
        self.name_input.clear()
        self.symbol_input.clear()
        self._persist()
        self.refresh()

    def _delete_currency(self):
        row = self.rates_table.currentRow()
        if row < 0:
            return
        code = self.rates_table.item(row, 0).text()
        if not self._engine.remove_currency(code):
            return
        self._persist()
        self.refresh()

    def _convert(self):
        amount = self.amount_input.value()
        from_code = self.from_combo.currentText()
        to_code = self.to_combo.currentText()
        result = self._engine.convert(amount, from_code, to_code)
        self.convert_result.setText(
            f"{t('currency_result')} {amount:,.2f} {self._engine.symbol(from_code)} "
            f"= {result:,.2f} {self._engine.symbol(to_code)}"
        )

    def _persist(self):
        """مزامنة الحالة مع المحرك العام وحفظ الإعدادات."""
        currency_engine.load_from_dict(self._engine.to_dict())
        state.save_settings()

    def _save(self):
        self._persist()
        QMessageBox.information(self, t("currency_title"), t("currency_saved"))

    def _export_csv(self):
        target = self.report_combo.currentText() or self._engine.base_currency
        rows = self._engine.report(state.financial_data, target)
        if not rows:
            QMessageBox.information(self, t("currency_title"), t("currency_no_data"))
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("currency_export_csv"),
            f"multi_currency_report_{target}.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        import csv
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Item", f"Amount ({self._engine.base_currency})",
                             f"Converted ({target})"])
            for row in rows:
                label_key = _ITEM_KEYS.get(row["item"], row["item"])
                writer.writerow([
                    t(label_key),
                    f"{row['amount']:.2f}",
                    f"{row['converted']:.2f}",
                ])
        QMessageBox.information(self, t("currency_title"),
                                f"{t('currency_saved')}\n{path}")
