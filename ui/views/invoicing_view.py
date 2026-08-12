# واجهة الفواتير
# ==============
# إنشاء فواتير بيع/شراء + عناصر + TVA + تغيير الحالة + التصدير + حفظ قاعدة البيانات

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit,
    QMessageBox, QFileDialog, QHeaderView, QFrame
)
from PyQt5.QtCore import QDate, Qt

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.invoicing import InvoiceManager, invoice_manager

_STATUSES = ("draft", "sent", "paid", "overdue", "cancelled")


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class InvoicingView(BaseView):
    """واجهة الفواتير"""

    def __init__(self):
        super().__init__()
        self._engine = invoice_manager
        if not self._engine.load_db():
            self._engine = InvoiceManager()
        self._pending_items = []
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
        self._make_header("invoicing_title", "invoicing_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_count = self._make_stat(t("invoicing_stat_count"))
        f2, self.stat_subtotal = self._make_stat(t("invoicing_stat_subtotal"))
        f3, self.stat_tva = self._make_stat(t("invoicing_stat_tva"))
        f4, self.stat_total = self._make_stat(t("invoicing_stat_total"))
        for w in (f1, f2, f3, f4):
            stats.addWidget(w)
        self._main_layout.addLayout(stats)

        # إنشاء فاتورة
        create_card = self._make_card("invoicing_create")
        form = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems([t("invoicing_sale"), t("invoicing_purchase")])
        self.partner_combo = QComboBox()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.tva_combo = QComboBox()
        self.tva_combo.addItems(["19%", "9%", "6%", "0%"])
        create_btn = QPushButton(t("invoicing_create_btn"))
        create_btn.clicked.connect(self._create_invoice)
        for lbl_key, w in (("invoicing_col_type", self.type_combo),
                           ("invoicing_col_partner", self.partner_combo),
                           ("invoicing_col_date", self.date_edit),
                           ("invoicing_col_tva", self.tva_combo)):
            form.addLayout(self._labeled_field(lbl_key, w))
        form.addWidget(create_btn, 0, Qt.AlignBottom)
        create_card.layout().addLayout(form)
        self._main_layout.addWidget(create_card)

        # عناصر الفاتورة
        items_card = self._make_card("invoicing_items")
        item_form = QHBoxLayout()
        self.item_desc = QLineEdit()
        self.item_desc.setPlaceholderText(t("invoicing_item_desc"))
        self.item_qty = QDoubleSpinBox()
        self.item_qty.setRange(0.01, 1e12)
        self.item_qty.setValue(1.0)
        self.item_qty.setDecimals(2)
        self.item_price = QDoubleSpinBox()
        self.item_price.setRange(0, 1e12)
        self.item_price.setDecimals(2)
        add_item_btn = QPushButton(t("invoicing_add_item"))
        add_item_btn.clicked.connect(self._add_pending_item)
        for lbl_key, w in (("invoicing_item_desc", self.item_desc),
                           ("invoicing_col_qty", self.item_qty),
                           ("invoicing_col_price", self.item_price)):
            item_form.addLayout(self._labeled_field(lbl_key, w))
        item_form.addWidget(add_item_btn, 0, Qt.AlignBottom)
        items_card.layout().addLayout(item_form)

        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(4)
        self.pending_table.setHorizontalHeaderLabels([
            t("invoicing_col_desc"), t("invoicing_col_qty"),
            t("invoicing_col_price"), t("invoicing_col_amount"),
        ])
        self.pending_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pending_table.setEditTriggers(QTableWidget.NoEditTriggers)
        items_card.layout().addWidget(self.pending_table)
        self._main_layout.addWidget(items_card)

        # جدول الفواتير
        list_card = self._make_card("invoicing_list")
        actions = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItem(t("invoicing_all_statuses"))
        for st in _STATUSES:
            self.status_combo.addItem(t("invoicing_status_%s" % st))
        self.status_combo.currentIndexChanged.connect(self.refresh)
        actions.addWidget(self.status_combo)
        self.status_change = QComboBox()
        for st in _STATUSES:
            self.status_change.addItem(t("invoicing_status_%s" % st))
        change_btn = QPushButton(t("invoicing_change_status"))
        change_btn.clicked.connect(self._change_status)
        actions.addWidget(self.status_change)
        actions.addWidget(change_btn)
        export_btn = QPushButton(t("invoicing_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        actions.addWidget(export_btn)
        save_btn = QPushButton(t("invoicing_save_db"))
        save_btn.clicked.connect(self._save_db)
        actions.addWidget(save_btn)
        clear_btn = QPushButton(t("invoicing_clear"))
        clear_btn.clicked.connect(self._clear_all)
        actions.addWidget(clear_btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            t("invoicing_col_number"), t("invoicing_col_type"),
            t("invoicing_col_partner"), t("invoicing_col_date"),
            t("invoicing_col_status"), t("invoicing_col_tva"),
            t("invoicing_col_total"),
        ])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        list_card.layout().addWidget(self.invoices_table)
        self._main_layout.addWidget(list_card)

        self._main_layout.addStretch()

    def refresh_partners(self):
        from modules.partners import partner_manager
        current = self.partner_combo.currentData()
        self.partner_combo.blockSignals(True)
        self.partner_combo.clear()
        partners = partner_manager.list_partners()
        self.partner_combo.addItem(t("invoicing_no_partner"), None)
        for p in partners:
            label = f"{p['name']} ({t('partners_customer') if p['type'] == 'customer' else t('partners_supplier')})"
            self.partner_combo.addItem(label, p["id"])
        if current is not None:
            idx = self.partner_combo.findData(current)
            if idx >= 0:
                self.partner_combo.setCurrentIndex(idx)
        self.partner_combo.blockSignals(False)

    def _add_pending_item(self):
        desc = self.item_desc.text().strip()
        if not desc:
            QMessageBox.warning(self, t("invoicing_title"), t("invoicing_item_required"))
            return
        self._pending_items.append({
            "description": desc,
            "quantity": self.item_qty.value(),
            "unit_price": self.item_price.value(),
        })
        self.item_desc.clear()
        self.item_price.setValue(0.0)
        self._render_pending()

    def _render_pending(self):
        self.pending_table.setRowCount(len(self._pending_items))
        for row, it in enumerate(self._pending_items):
            amount = it["quantity"] * it["unit_price"]
            self.pending_table.setItem(row, 0, QTableWidgetItem(_plain(it["description"])))
            self.pending_table.setItem(row, 1, QTableWidgetItem(f"{it['quantity']:,.2f}"))
            self.pending_table.setItem(row, 2, QTableWidgetItem(f"{it['unit_price']:,.2f}"))
            self.pending_table.setItem(row, 3, QTableWidgetItem(f"{amount:,.2f}"))

    def _create_invoice(self):
        partner_id = self.partner_combo.currentData()
        if not self._pending_items:
            QMessageBox.warning(self, t("invoicing_title"), t("invoicing_no_items"))
            return
        if partner_id is None:
            QMessageBox.warning(self, t("invoicing_title"), t("invoicing_select_partner"))
            return
        tva_rate = float(self.tva_combo.currentText().replace("%", "")) / 100.0
        invoice_type = "sale" if self.type_combo.currentIndex() == 0 else "purchase"
        try:
            self._engine.create_invoice(
                invoice_type, partner_id,
                self.date_edit.date().toString("yyyy-MM-dd"),
                list(self._pending_items), tva_rate=tva_rate,
            )
        except Exception as exc:
            QMessageBox.critical(self, t("invoicing_title"), str(exc))
            return
        self._pending_items = []
        self._render_pending()
        self.refresh()

    def _change_status(self):
        row = self.invoices_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("invoicing_title"), t("invoicing_select_first"))
            return
        inv = self._invoices[row]
        status = _STATUSES[self.status_change.currentIndex()]
        self._engine.update_status(inv["id"], status)
        self.refresh()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("invoicing_export_csv"), "invoices.csv", "CSV Files (*.csv)")
        if not path:
            return
        if self._engine.export_csv(path):
            QMessageBox.information(self, t("invoicing_title"), t("invoicing_export_ok"))
        else:
            QMessageBox.warning(self, t("invoicing_title"), t("invoicing_export_fail"))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("invoicing_title"), t("invoicing_saved"))
        else:
            QMessageBox.warning(self, t("invoicing_title"), t("invoicing_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("invoicing_title"), t("invoicing_clear_confirm")) != \
                QMessageBox.Yes:
            return
        self._engine.clear()
        self.refresh()

    def refresh(self):
        self.refresh_partners()
        status = None
        if hasattr(self, "status_combo") and self.status_combo.currentIndex() > 0:
            status = _STATUSES[self.status_combo.currentIndex() - 1]
        invoices = self._engine.list_invoices(status=status)
        self._invoices = invoices
        self.invoices_table.setRowCount(len(invoices))
        for row, inv in enumerate(invoices):
            self.invoices_table.setItem(row, 0, QTableWidgetItem(inv["number"]))
            self.invoices_table.setItem(
                row, 1, QTableWidgetItem(
                    t("invoicing_sale") if inv["type"] == "sale"
                    else t("invoicing_purchase")))
            self.invoices_table.setItem(
                row, 2, QTableWidgetItem(str(inv.get("partner_id") or "")))
            self.invoices_table.setItem(row, 3, QTableWidgetItem(inv["date"]))
            self.invoices_table.setItem(
                row, 4, QTableWidgetItem(t("invoicing_status_%s" % inv["status"])))
            self.invoices_table.setItem(
                row, 5, QTableWidgetItem(f"{inv['tva_rate'] * 100:.0f}%"))
            self.invoices_table.setItem(row, 6, QTableWidgetItem(f"{inv['total']:,.2f}"))

        totals = self._engine.totals()
        self.stat_count.setText(str(totals["count"]))
        self.stat_subtotal.setText(f"{totals['subtotal']:,.2f}")
        self.stat_tva.setText(f"{totals['tva_amount']:,.2f}")
        self.stat_total.setText(f"{totals['total']:,.2f}")
