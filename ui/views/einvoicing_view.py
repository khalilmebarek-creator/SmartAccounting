# واجهة الفواتير الإلكترونية
# ==========================
# توقيع رقمي + رمز QR + تحقق سلامة + تصدير JSON + حفظ قاعدة البيانات

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QDoubleSpinBox, QDateEdit,
    QMessageBox, QFileDialog, QHeaderView, QFrame, QTextEdit
)
from PyQt5.QtCore import QDate

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.einvoicing import EInvoiceManager, einvoice_manager


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class EInvoicingView(BaseView):

    def __init__(self):
        super().__init__()
        self._engine = einvoice_manager
        if not self._engine.load_db():
            self._engine = EInvoiceManager()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("einvoice_title", "einvoice_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_count = self._make_stat(t("einvoice_stat_count"))
        f2, self.stat_total = self._make_stat(t("einvoice_stat_total"))
        f3, self.stat_verified = self._make_stat(t("einvoice_stat_verified"))
        for w in (f1, f2, f3):
            stats.addWidget(w)
        stats.addStretch()
        self._main_layout.addLayout(stats)

        add_card = self._make_card("einvoice_add")
        form = QHBoxLayout()
        self.customer_edit = QLineEdit()
        self.customer_edit.setPlaceholderText(t("einvoice_customer"))
        self.taxid_edit = QLineEdit()
        self.taxid_edit.setPlaceholderText(t("einvoice_customer_tax_id"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        add_btn = QPushButton(t("einvoice_add_btn"))
        add_btn.clicked.connect(self._add_invoice)
        for w in (self.customer_edit, self.taxid_edit, self.date_edit, add_btn):
            form.addWidget(w)
        add_card.layout().addLayout(form)
        self._main_layout.addWidget(add_card)

        list_card = self._make_card("einvoice_list")
        actions = QHBoxLayout()
        for label, slot in [
            ("einvoice_generate", self._generate),
            ("einvoice_verify", self._verify),
            ("einvoice_export_json", self._export_json),
            ("einvoice_save_db", self._save_db),
            ("einvoice_clear", self._clear_all),
        ]:
            btn = QPushButton(t(label))
            btn.clicked.connect(slot)
            actions.addWidget(btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(6)
        self.invoice_table.setHorizontalHeaderLabels([
            t("einvoice_col_number"),
            t("einvoice_col_customer"),
            t("einvoice_col_date"),
            t("einvoice_col_total"),
            t("einvoice_col_status"),
            t("einvoice_col_hash"),
        ])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invoice_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.invoice_table.itemSelectionChanged.connect(self._on_selection)
        list_card.layout().addWidget(self.invoice_table)

        self._detail_text = QTextEdit()
        self._detail_text.setReadOnly(True)
        self._detail_text.setMaximumHeight(140)
        self._detail_text.setPlaceholderText(t("einvoice_detail_placeholder"))
        list_card.layout().addWidget(self._detail_text)

        self._main_layout.addWidget(list_card)
        self._main_layout.addStretch()

    def _add_invoice(self):
        customer = self.customer_edit.text().strip()
        if not customer:
            QMessageBox.warning(self, t("einvoice_title"),
                                t("einvoice_customer_required"))
            return
        try:
            self._engine.create(
                customer,
                customer_tax_id=self.taxid_edit.text().strip(),
                invoice_date=self.date_edit.date().toString("yyyy-MM-dd"),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("einvoice_title"), str(exc))
            return
        self.customer_edit.clear()
        self.taxid_edit.clear()
        self.refresh()

    def _generate(self):
        row = self.invoice_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("einvoice_title"),
                                t("einvoice_select_row"))
            return
        inv_id = int(self.invoice_table.item(row, 0).data(0) or 0)
        try:
            inv = self._engine.generate(inv_id)
            QMessageBox.information(
                self, t("einvoice_title"),
                t("einvoice_generated").format(inv["number"]))
        except Exception as exc:
            QMessageBox.critical(self, t("einvoice_title"), str(exc))
            return
        self.refresh()
        self._show_detail(inv_id)

    def _verify(self):
        row = self.invoice_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("einvoice_title"),
                                t("einvoice_select_row"))
            return
        inv_id = int(self.invoice_table.item(row, 0).data(0) or 0)
        ok, msg = self._engine.verify(inv_id)
        if ok:
            self._engine.update_status(inv_id, "verified")
            self.refresh()
        QMessageBox.information(
            self, t("einvoice_verify_title"),
            t("einvoice_verified") if ok else t("einvoice_verify_failed") + f"\n{msg}")

    def _export_json(self):
        row = self.invoice_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("einvoice_title"),
                                t("einvoice_select_row"))
            return
        inv_id = int(self.invoice_table.item(row, 0).data(0) or 0)
        inv = self._engine.get_invoice(inv_id)
        if not inv:
            return
        default_name = f"einvoice_{inv['number']}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, t("einvoice_export_json"), default_name,
            "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._engine.export_json(inv_id))
            QMessageBox.information(self, t("einvoice_title"),
                                    t("einvoice_export_ok"))
        except Exception as exc:
            QMessageBox.warning(self, t("einvoice_title"), str(exc))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("einvoice_title"),
                                    t("einvoice_saved"))
        else:
            QMessageBox.warning(self, t("einvoice_title"),
                                t("einvoice_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("einvoice_title"),
                t("einvoice_clear_confirm")) != QMessageBox.Yes:
            return
        self._engine.clear()
        self._detail_text.clear()
        self.refresh()

    def _on_selection(self):
        row = self.invoice_table.currentRow()
        if row < 0:
            self._detail_text.clear()
            return
        inv_id = int(self.invoice_table.item(row, 0).data(0) or 0)
        self._show_detail(inv_id)

    def _show_detail(self, inv_id):
        inv = self._engine.get_invoice(inv_id)
        if not inv:
            self._detail_text.clear()
            return
        lines = [
            f"{t('einvoice_col_number')}: {inv['number']}",
            f"{t('einvoice_col_customer')}: {inv['customer']}",
            f"{t('einvoice_col_date')}: {inv['date']}  {t('einvoice_col_status')}: {inv['status']}",
            f"{t('einvoice_detail_hash')}: {inv['hash'] or '-'}",
            f"--- {t('einvoice_detail_items')} ({len(inv['items'])}):",
        ]
        for it in inv["items"]:
            lines.append(
                f"  {it['description']}  x{it['quantity']}  @{it['unit_price']:,.2f}"
                f"  TVA {it['tva_rate']*100:.0f}%  = {it['total']:,.2f}")
        lines.append(
            f"{t('einvoice_detail_subtotal')}: {inv['subtotal']:,.2f}  "
            f"TVA: {inv['tva_total']:,.2f}  "
            f"{t('einvoice_detail_total')}: {inv['grand_total']:,.2f}")
        if inv["qr_data"]:
            lines.append(f"--- QR: {inv['qr_data']}")
        self._detail_text.setPlainText("\n".join(lines))

    def refresh(self):
        invoices = self._engine.list_invoices()
        self.invoice_table.setRowCount(len(invoices))
        total_amount = 0.0
        verified_count = 0
        for row, inv in enumerate(invoices):
            total_amount += inv.get("grand_total") or 0
            if inv.get("status") == "verified":
                verified_count += 1
            id_item = QTableWidgetItem(inv["number"])
            id_item.setData(0, inv["id"])
            self.invoice_table.setItem(row, 0, id_item)
            self.invoice_table.setItem(row, 1, QTableWidgetItem(_plain(inv["customer"])))
            self.invoice_table.setItem(row, 2, QTableWidgetItem(inv["date"]))
            self.invoice_table.setItem(row, 3, QTableWidgetItem(
                f"{inv['grand_total']:,.2f}"))
            self.invoice_table.setItem(row, 4, QTableWidgetItem(inv["status"]))
            self.invoice_table.setItem(row, 5, QTableWidgetItem(
                (inv.get("hash") or "")[:16]))

        self.stat_count.setText(str(len(invoices)))
        self.stat_total.setText(f"{total_amount:,.2f}")
        self.stat_verified.setText(str(verified_count))
