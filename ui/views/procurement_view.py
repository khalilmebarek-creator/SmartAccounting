# واجهة المشتريات
# ===============
# طلبات شراء + موردين + بنود + تصدير CSV + حفظ قاعدة البيانات

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit,
    QMessageBox, QFileDialog, QHeaderView, QFrame
)
from PyQt5.QtCore import QDate

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.procurement import ProcurementManager, procurement_manager


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class ProcurementView(BaseView):

    def __init__(self):
        super().__init__()
        self._engine = procurement_manager
        if not self._engine.load_db():
            self._engine = ProcurementManager()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("procurement_title", "procurement_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_orders = self._make_stat(t("procurement_stat_orders"))
        f2, self.stat_total = self._make_stat(t("procurement_stat_total"))
        f3, self.stat_pending = self._make_stat(t("procurement_stat_pending"))
        for w in (f1, f2, f3):
            stats.addWidget(w)
        stats.addStretch()
        self._main_layout.addLayout(stats)

        add_card = self._make_card("procurement_add_order")
        form = QHBoxLayout()
        self.supplier_edit = QLineEdit()
        self.supplier_edit.setPlaceholderText(t("procurement_supplier"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.ref_edit = QLineEdit()
        self.ref_edit.setPlaceholderText(t("procurement_reference"))
        add_btn = QPushButton(t("procurement_add_btn"))
        add_btn.clicked.connect(self._add_order)
        for w in (self.supplier_edit, self.date_edit, self.ref_edit, add_btn):
            form.addWidget(w)
        add_card.layout().addLayout(form)
        self._main_layout.addWidget(add_card)

        list_card = self._make_card("procurement_orders_list")
        actions = QHBoxLayout()
        export_btn = QPushButton(t("procurement_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        save_btn = QPushButton(t("procurement_save_db"))
        save_btn.clicked.connect(self._save_db)
        clear_btn = QPushButton(t("procurement_clear"))
        clear_btn.clicked.connect(self._clear_all)
        actions.addWidget(export_btn)
        actions.addWidget(save_btn)
        actions.addWidget(clear_btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels([
            t("procurement_col_id"),
            t("procurement_col_supplier"),
            t("procurement_col_date"),
            t("procurement_col_amount"),
            t("procurement_col_status"),
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        list_card.layout().addWidget(self.orders_table)
        self._main_layout.addWidget(list_card)

        self._main_layout.addStretch()

    def _add_order(self):
        supplier = self.supplier_edit.text().strip()
        if not supplier:
            QMessageBox.warning(self, t("procurement_title"),
                                t("procurement_supplier_required"))
            return
        try:
            self._engine.add_order(
                supplier,
                self.date_edit.date().toString("yyyy-MM-dd"),
                reference=self.ref_edit.text().strip(),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("procurement_title"), str(exc))
            return
        self.supplier_edit.clear()
        self.ref_edit.clear()
        self.refresh()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("procurement_export_csv"), "procurement.csv",
            "CSV Files (*.csv)")
        if not path:
            return
        import csv
        try:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["id", "supplier", "date", "reference",
                                 "status", "total", "items"])
                for order in self._engine.list_orders():
                    writer.writerow([
                        order["id"], _plain(order.get("supplier") or ""),
                        order.get("date") or "",
                        order.get("reference") or "",
                        order.get("status") or "",
                        f"{order.get('grand_total') or 0:,.2f}",
                        order.get("item_count", 0),
                    ])
            QMessageBox.information(self, t("procurement_title"),
                                    t("procurement_export_ok"))
        except Exception as exc:
            QMessageBox.warning(self, t("procurement_title"), str(exc))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("procurement_title"),
                                    t("procurement_saved"))
        else:
            QMessageBox.warning(self, t("procurement_title"),
                                t("procurement_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("procurement_title"),
                t("procurement_clear_confirm")) != QMessageBox.Yes:
            return
        self._engine.clear()
        self.refresh()

    def refresh(self):
        orders = self._engine.list_orders()
        self.orders_table.setRowCount(len(orders))
        total_amount = 0.0
        pending_count = 0
        for row, order in enumerate(orders):
            total_amount += order.get("grand_total") or 0
            if order.get("status") == "pending":
                pending_count += 1
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order["id"])))
            self.orders_table.setItem(row, 1, QTableWidgetItem(_plain(order.get("supplier") or "")))
            self.orders_table.setItem(row, 2, QTableWidgetItem(order.get("date") or ""))
            self.orders_table.setItem(row, 3, QTableWidgetItem(
                f"{order.get('grand_total') or 0:,.2f}"))
            self.orders_table.setItem(row, 4, QTableWidgetItem(order.get("status") or ""))

        self.stat_orders.setText(str(len(orders)))
        self.stat_total.setText(f"{total_amount:,.2f}")
        self.stat_pending.setText(str(pending_count))
