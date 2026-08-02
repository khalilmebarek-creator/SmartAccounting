# واجهة دفتر الأستاذ العام
# ==========================
# قيود يومية + دفتر أستاذ لكل حساب + ميزان المراجعة + تصدير CSV + حفظ قاعدة بيانات

from ui.views._path import _  # noqa: F401

import os

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDateEdit, QDoubleSpinBox, QMessageBox,
    QFileDialog, QHeaderView, QFrame
)
from PyQt5.QtCore import QDate

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.ledger import LedgerBook, ledger_book


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class LedgerView(BaseView):
    """واجهة دفتر الأستاذ العام"""

    def __init__(self):
        super().__init__()
        self._engine = ledger_book
        if not self._engine.load_db():
            self._engine = LedgerBook()
        self.setup_ui()
        self.refresh()

    @staticmethod
    def _make_stat(title):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 11px; color: #888;")
        lbl_value = QLabel("0")
        lbl_value.setObjectName("statValue")
        from PyQt5.QtGui import QFont
        font = QFont()
        font.setBold(True)
        font.setPointSize(15)
        lbl_value.setFont(font)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        frame.setLayout(layout)
        return frame, lbl_value

    def setup_ui(self):
        self._make_header("ledger_title", "ledger_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_entries = self._make_stat(t("ledger_stat_entries"))
        f2, self.stat_debit = self._make_stat(t("ledger_stat_debit"))
        f3, self.stat_credit = self._make_stat(t("ledger_stat_credit"))
        f4, self.stat_balanced = self._make_stat(t("ledger_stat_balanced"))
        for w in (f1, f2, f3, f4):
            stats.addWidget(w)
        self._main_layout.addLayout(stats)

        # إدخال قيد
        entry_card = self._make_card("ledger_entry")
        form = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.account_edit = QLineEdit()
        self.account_edit.setPlaceholderText(t("ledger_account_code"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText(t("ledger_description"))
        self.debit_spin = QDoubleSpinBox()
        self.debit_spin.setRange(0, 1e12)
        self.debit_spin.setDecimals(2)
        self.credit_spin = QDoubleSpinBox()
        self.credit_spin.setRange(0, 1e12)
        self.credit_spin.setDecimals(2)
        add_btn = QPushButton(t("ledger_add_entry"))
        add_btn.clicked.connect(self._add_entry)
        for w in (self.date_edit, self.account_edit, self.desc_edit,
                  self.debit_spin, self.credit_spin, add_btn):
            form.addWidget(w)
        entry_card.layout().addLayout(form)
        self._main_layout.addWidget(entry_card)

        # جدول القيود
        list_card = self._make_card("ledger_entries")
        actions = QHBoxLayout()
        self.account_filter = QLineEdit()
        self.account_filter.setPlaceholderText(t("ledger_filter_account"))
        self.account_filter.textChanged.connect(self.refresh)
        actions.addWidget(self.account_filter)
        export_btn = QPushButton(t("ledger_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        actions.addWidget(export_btn)
        save_btn = QPushButton(t("ledger_save_db"))
        save_btn.clicked.connect(self._save_db)
        actions.addWidget(save_btn)
        clear_btn = QPushButton(t("ledger_clear"))
        clear_btn.clicked.connect(self._clear_all)
        actions.addWidget(clear_btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(7)
        self.entries_table.setHorizontalHeaderLabels([
            t("ledger_col_id"), t("ledger_col_date"), t("ledger_col_account"),
            t("ledger_col_description"), t("ledger_col_debit"),
            t("ledger_col_credit"), t("ledger_col_reference"),
        ])
        self.entries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.entries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entries_table.setEditTriggers(QTableWidget.NoEditTriggers)
        list_card.layout().addWidget(self.entries_table)
        self._main_layout.addWidget(list_card)

        # ميزان المراجعة
        tb_card = self._make_card("ledger_trial_balance")
        self.tb_table = QTableWidget()
        self.tb_table.setColumnCount(4)
        self.tb_table.setHorizontalHeaderLabels([
            t("ledger_col_account"), t("ledger_col_name"),
            t("ledger_col_debit"), t("ledger_col_credit"),
        ])
        self.tb_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tb_table.setEditTriggers(QTableWidget.NoEditTriggers)
        tb_card.layout().addWidget(self.tb_table)
        self._main_layout.addWidget(tb_card)

        self._main_layout.addStretch()

    def _add_entry(self):
        date_text = self.date_edit.date().toString("yyyy-MM-dd")
        account = self.account_edit.text().strip()
        if not account:
            QMessageBox.warning(self, t("ledger_title"), t("ledger_account_required"))
            return
        try:
            self._engine.add_entry(
                date_text, account,
                debit=self.debit_spin.value(),
                credit=self.credit_spin.value(),
                description=self.desc_edit.text().strip(),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("ledger_title"), str(exc))
            return
        self.desc_edit.clear()
        self.debit_spin.setValue(0.0)
        self.credit_spin.setValue(0.0)
        self.refresh()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("ledger_export_csv"), "ledger.csv", "CSV Files (*.csv)")
        if not path:
            return
        if self._engine.export_csv(path):
            QMessageBox.information(self, t("ledger_title"), t("ledger_export_ok"))
        else:
            QMessageBox.warning(self, t("ledger_title"), t("ledger_export_fail"))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("ledger_title"), t("ledger_saved"))
        else:
            QMessageBox.warning(self, t("ledger_title"), t("ledger_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("ledger_title"), t("ledger_clear_confirm")) != \
                QMessageBox.Yes:
            return
        self._engine.clear()
        self.refresh()

    def refresh(self):
        filter_acc = self.account_filter.text().strip() if hasattr(
            self, "account_filter") else ""
        entries = self._engine.get_entries(account_code=filter_acc or None)
        self.entries_table.setRowCount(len(entries))
        for row, e in enumerate(entries):
            self.entries_table.setItem(row, 0, QTableWidgetItem(str(e["id"])))
            self.entries_table.setItem(row, 1, QTableWidgetItem(e["date"]))
            self.entries_table.setItem(row, 2, QTableWidgetItem(e["account_code"]))
            self.entries_table.setItem(row, 3, QTableWidgetItem(e["description"]))
            self.entries_table.setItem(row, 4, QTableWidgetItem(f"{e['debit']:,.2f}"))
            self.entries_table.setItem(row, 5, QTableWidgetItem(f"{e['credit']:,.2f}"))
            self.entries_table.setItem(row, 6, QTableWidgetItem(e.get("reference") or ""))

        tb = self._engine.trial_balance()
        self.stat_entries.setText(str(tb["entry_count"]))
        self.stat_debit.setText(f"{tb['total_debit']:,.2f}")
        self.stat_credit.setText(f"{tb['total_credit']:,.2f}")
        self.stat_balanced.setText(
            t("ledger_yes") if tb["balanced"] else t("ledger_no"))

        summary = self._engine.accounts_summary()
        self.tb_table.setRowCount(len(summary))
        for row, acc in enumerate(summary):
            self.tb_table.setItem(row, 0, QTableWidgetItem(acc["account_code"]))
            self.tb_table.setItem(row, 1, QTableWidgetItem(acc["account_name"]))
            self.tb_table.setItem(row, 2, QTableWidgetItem(f"{acc['debit']:,.2f}"))
            self.tb_table.setItem(row, 3, QTableWidgetItem(f"{acc['credit']:,.2f}"))
