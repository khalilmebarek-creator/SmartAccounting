# واجهة العملاء والموردين
# ========================
# إدارة العملاء/الموردين + المعاملات + الأرصدة + تقادم الديون + تصدير CSV + حفظ قاعدة بيانات

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit,
    QMessageBox, QFileDialog, QHeaderView, QFrame
)
from PyQt6.QtCore import QDate, Qt

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.partners import PartnerManager, partner_manager

_TX_TYPES = ("invoice", "payment", "credit_note", "debit_note")


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class PartnersView(BaseView):
    """واجهة العملاء والموردين"""

    def __init__(self):
        super().__init__()
        self._engine = partner_manager
        if not self._engine.load_db():
            self._engine = PartnerManager()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("partners_title", "partners_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_partners = self._make_stat(t("partners_stat_partners"))
        f2, self.stat_receivable = self._make_stat(t("partners_stat_receivable"))
        f3, self.stat_payable = self._make_stat(t("partners_stat_payable"))
        f4, self.stat_net = self._make_stat(t("partners_stat_net"))
        for w in (f1, f2, f3, f4):
            stats.addWidget(w)
        self._main_layout.addLayout(stats)

        # إضافة شريك
        add_card = self._make_card("partners_add")
        row1 = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems([t("partners_customer"), t("partners_supplier")])
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(t("partners_name"))
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText(t("partners_phone"))
        row1.addLayout(self._labeled_field("partners_col_type", self.type_combo))
        row1.addLayout(self._labeled_field("partners_name", self.name_edit))
        row1.addLayout(self._labeled_field("partners_phone", self.phone_edit))
        add_card.layout().addLayout(row1)
        row2 = QHBoxLayout()
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText(t("partners_email"))
        self.tax_edit = QLineEdit()
        self.tax_edit.setPlaceholderText(t("partners_tax_id"))
        add_btn = QPushButton(t("partners_add_btn"))
        add_btn.clicked.connect(self._add_partner)
        row2.addLayout(self._labeled_field("partners_email", self.email_edit))
        row2.addLayout(self._labeled_field("partners_tax_id", self.tax_edit))
        row2.addWidget(add_btn, 0, Qt.AlignmentFlag.AlignBottom)
        add_card.layout().addLayout(row2)
        self._main_layout.addWidget(add_card)

        # جدول الشركاء
        list_card = self._make_card("partners_list")
        actions = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(t("partners_search"))
        self.search_edit.textChanged.connect(self.refresh)
        actions.addWidget(self.search_edit)
        export_btn = QPushButton(t("partners_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        actions.addWidget(export_btn)
        save_btn = QPushButton(t("partners_save_db"))
        save_btn.clicked.connect(self._save_db)
        actions.addWidget(save_btn)
        clear_btn = QPushButton(t("partners_clear"))
        clear_btn.clicked.connect(self._clear_all)
        actions.addWidget(clear_btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.partners_table = QTableWidget()
        self.partners_table.setColumnCount(6)
        self.partners_table.setHorizontalHeaderLabels([
            t("partners_col_id"), t("partners_col_type"), t("partners_col_name"),
            t("partners_col_phone"), t("partners_col_email"),
            t("partners_col_balance"),
        ])
        self.partners_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.partners_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.partners_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.partners_table.itemSelectionChanged.connect(self._on_select_partner)
        self.partners_table.setMinimumHeight(44 * 6 + 30)
        list_card.layout().addWidget(self.partners_table)
        self._main_layout.addWidget(list_card)

        # معاملة + تقادم
        row = QHBoxLayout()
        tx_card = self._make_card("partners_tx")
        tx_row1 = QHBoxLayout()
        self.tx_date = QDateEdit(QDate.currentDate())
        self.tx_date.setCalendarPopup(True)
        self.tx_date.setDisplayFormat("yyyy-MM-dd")
        self.tx_type = QComboBox()
        self.tx_type.addItems([t("partners_tx_%s" % tx) for tx in _TX_TYPES])
        tx_row1.addLayout(self._labeled_field("partners_col_date", self.tx_date))
        tx_row1.addLayout(self._labeled_field("partners_col_type", self.tx_type))
        tx_card.layout().addLayout(tx_row1)
        tx_row2 = QHBoxLayout()
        self.tx_amount = QDoubleSpinBox()
        self.tx_amount.setRange(-1e12, 1e12)
        self.tx_amount.setDecimals(2)
        self.tx_ref = QLineEdit()
        self.tx_ref.setPlaceholderText(t("partners_tx_reference"))
        tx_add_btn = QPushButton(t("partners_tx_add"))
        tx_add_btn.clicked.connect(self._add_transaction)
        tx_row2.addLayout(self._labeled_field("partners_col_amount", self.tx_amount))
        tx_row2.addLayout(self._labeled_field("partners_tx_reference", self.tx_ref))
        tx_row2.addWidget(tx_add_btn, 0, Qt.AlignmentFlag.AlignBottom)
        tx_card.layout().addLayout(tx_row2)

        self.tx_table = QTableWidget()
        self.tx_table.setColumnCount(5)
        self.tx_table.setHorizontalHeaderLabels([
            t("partners_col_date"), t("partners_col_type"),
            t("partners_col_amount"), t("partners_col_reference"),
            t("partners_col_notes"),
        ])
        self.tx_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tx_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tx_table.setMinimumHeight(44 * 5 + 30)
        tx_card.layout().addWidget(self.tx_table)
        row.addWidget(tx_card)

        aging_card = self._make_card("partners_aging")
        self.aging_table = QTableWidget()
        self.aging_table.setColumnCount(5)
        self.aging_table.setHorizontalHeaderLabels([
            t("partners_col_name"), t("partners_aging_current"),
            t("partners_aging_30"), t("partners_aging_60"),
            t("partners_aging_90"),
        ])
        self.aging_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.aging_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.aging_table.setMinimumHeight(44 * 5 + 30)
        aging_card.layout().addWidget(self.aging_table)
        row.addWidget(aging_card)
        self._main_layout.addLayout(row)

        self._main_layout.addStretch()

    def _selected_partner_id(self):
        row = self.partners_table.currentRow()
        if row < 0:
            return None
        item = self.partners_table.item(row, 0)
        return int(item.text()) if item else None

    def _on_select_partner(self):
        self.refresh_transactions()

    def _add_partner(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, t("partners_title"), t("partners_name_required"))
            return
        try:
            self._engine.add_partner(
                "customer" if self.type_combo.currentIndex() == 0 else "supplier",
                name, phone=self.phone_edit.text().strip(),
                email=self.email_edit.text().strip(),
                tax_id=self.tax_edit.text().strip(),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("partners_title"), str(exc))
            return
        self.name_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
        self.tax_edit.clear()
        self.refresh()

    def _add_transaction(self):
        partner_id = self._selected_partner_id()
        if partner_id is None:
            QMessageBox.warning(self, t("partners_title"), t("partners_select_first"))
            return
        tx_type = _TX_TYPES[self.tx_type.currentIndex()]
        try:
            self._engine.add_transaction(
                partner_id,
                self.tx_date.date().toString("yyyy-MM-dd"),
                tx_type, self.tx_amount.value(),
                reference=self.tx_ref.text().strip(),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("partners_title"), str(exc))
            return
        self.tx_ref.clear()
        self.tx_amount.setValue(0.0)
        self.refresh()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("partners_export_csv"), "partners.csv", "CSV Files (*.csv)")
        if not path:
            return
        import csv
        try:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["id", "type", "name", "phone", "email", "balance"])
                for p in self._engine.list_partners():
                    writer.writerow([p["id"], p["type"], _plain(p["name"]),
                                     _plain(p.get("phone") or ""),
                                     _plain(p.get("email") or ""),
                                     p["balance"]])
            QMessageBox.information(self, t("partners_title"), t("partners_export_ok"))
        except Exception as exc:
            QMessageBox.warning(self, t("partners_title"), str(exc))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("partners_title"), t("partners_saved"))
        else:
            QMessageBox.warning(self, t("partners_title"), t("partners_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("partners_title"), t("partners_clear_confirm")) != \
                QMessageBox.StandardButton.Yes:
            return
        self._engine.clear()
        self.refresh()

    def refresh(self):
        query = self.search_edit.text().strip() if hasattr(self, "search_edit") else ""
        partners = self._engine.search_partners(query) if query \
            else self._engine.list_partners()
        self.partners_table.setRowCount(len(partners))
        total_receivable = 0.0
        total_payable = 0.0
        for row, p in enumerate(partners):
            self.partners_table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
            self.partners_table.setItem(
                row, 1, QTableWidgetItem(
                    t("partners_customer") if p["type"] == "customer"
                    else t("partners_supplier")))
            self.partners_table.setItem(row, 2, QTableWidgetItem(_plain(p["name"])))
            self.partners_table.setItem(row, 3, QTableWidgetItem(p.get("phone") or ""))
            self.partners_table.setItem(row, 4, QTableWidgetItem(p.get("email") or ""))
            balance = p.get("balance") or 0.0
            self.partners_table.setItem(
                row, 5, QTableWidgetItem(f"{balance:,.2f}"))
            if p["type"] == "customer":
                total_receivable += balance
            else:
                total_payable += balance

        self.stat_partners.setText(str(len(partners)))
        self.stat_receivable.setText(f"{total_receivable:,.2f}")
        self.stat_payable.setText(f"{total_payable:,.2f}")
        self.stat_net.setText(f"{total_receivable - total_payable:,.2f}")

        aging = self._engine.aging(QDate.currentDate().toString("yyyy-MM-dd")) or []
        self.aging_table.setRowCount(len(aging))
        for row, bucket in enumerate(aging):
            self.aging_table.setItem(row, 0, QTableWidgetItem(_plain(bucket.get("name") or "")))
            self.aging_table.setItem(row, 1, QTableWidgetItem(f"{bucket.get('current') or 0:,.2f}"))
            self.aging_table.setItem(row, 2, QTableWidgetItem(f"{bucket.get('days_31_60') or 0:,.2f}"))
            self.aging_table.setItem(row, 3, QTableWidgetItem(f"{bucket.get('days_61_90') or 0:,.2f}"))
            self.aging_table.setItem(row, 4, QTableWidgetItem(f"{bucket.get('days_90_plus') or 0:,.2f}"))

        self.refresh_transactions()

    def refresh_transactions(self):
        partner_id = self._selected_partner_id()
        txs = self._engine.list_transactions(partner_id) if partner_id else []
        self.tx_table.setRowCount(len(txs))
        for row, tx in enumerate(txs):
            self.tx_table.setItem(row, 0, QTableWidgetItem(tx["date"]))
            self.tx_table.setItem(
                row, 1, QTableWidgetItem(t("partners_tx_%s" % tx["type"])))
            self.tx_table.setItem(row, 2, QTableWidgetItem(f"{tx['amount']:,.2f}"))
            self.tx_table.setItem(row, 3, QTableWidgetItem(tx.get("reference") or ""))
            self.tx_table.setItem(row, 4, QTableWidgetItem(tx.get("notes") or ""))
