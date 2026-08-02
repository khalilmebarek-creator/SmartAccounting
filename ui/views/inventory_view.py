# واجهة المخزون
# =============
# عناصر المخزون + الحركات (إدخال/إخراج) + الأسهم والتنبيهات + تصدير CSV + حفظ قاعدة البيانات

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit,
    QMessageBox, QFileDialog, QHeaderView, QFrame
)
from PyQt5.QtCore import QDate

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.inventory import InventoryManager, inventory_manager


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class InventoryView(BaseView):
    """واجهة إدارة المخزون"""

    def __init__(self):
        super().__init__()
        self._engine = inventory_manager
        if not self._engine.load_db():
            self._engine = InventoryManager()
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
        self._make_header("inventory_title", "inventory_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_items = self._make_stat(t("inventory_stat_items"))
        f2, self.stat_stock_value = self._make_stat(t("inventory_stat_value"))
        f3, self.stat_low = self._make_stat(t("inventory_stat_low"))
        for w in (f1, f2, f3):
            stats.addWidget(w)
        stats.addStretch()
        self._main_layout.addLayout(stats)

        # إضافة عنصر
        add_card = self._make_card("inventory_add_item")
        form = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(t("inventory_name"))
        self.sku_edit = QLineEdit()
        self.sku_edit.setPlaceholderText(t("inventory_sku"))
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText(t("inventory_category"))
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText(t("inventory_unit"))
        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0, 1e12)
        self.qty_spin.setDecimals(2)
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 1e12)
        self.cost_spin.setDecimals(2)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1e12)
        self.price_spin.setDecimals(2)
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(0, 1e12)
        self.min_spin.setDecimals(2)
        add_btn = QPushButton(t("inventory_add_btn"))
        add_btn.clicked.connect(self._add_item)
        for w in (self.name_edit, self.sku_edit, self.category_edit,
                  self.unit_edit, self.qty_spin, self.cost_spin,
                  self.price_spin, self.min_spin, add_btn):
            form.addWidget(w)
        add_card.layout().addLayout(form)
        self._main_layout.addWidget(add_card)

        # جدول العناصر
        list_card = self._make_card("inventory_items")
        actions = QHBoxLayout()
        self.low_only_check = QComboBox()
        self.low_only_check.addItems([t("inventory_all"), t("inventory_low_only")])
        self.low_only_check.currentIndexChanged.connect(self.refresh)
        actions.addWidget(self.low_only_check)
        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText(t("inventory_filter_category"))
        self.category_filter.textChanged.connect(self.refresh)
        actions.addWidget(self.category_filter)
        export_btn = QPushButton(t("inventory_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        actions.addWidget(export_btn)
        save_btn = QPushButton(t("inventory_save_db"))
        save_btn.clicked.connect(self._save_db)
        actions.addWidget(save_btn)
        clear_btn = QPushButton(t("inventory_clear"))
        clear_btn.clicked.connect(self._clear_all)
        actions.addWidget(clear_btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            t("inventory_col_id"), t("inventory_col_sku"),
            t("inventory_col_name"), t("inventory_col_category"),
            t("inventory_col_qty"), t("inventory_col_avg_cost"),
            t("inventory_col_value"),
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.itemSelectionChanged.connect(self._on_select_item)
        list_card.layout().addWidget(self.items_table)
        self._main_layout.addWidget(list_card)

        # حركة
        mov_card = self._make_card("inventory_movement")
        mov_form = QHBoxLayout()
        self.mov_date = QDateEdit(QDate.currentDate())
        self.mov_date.setCalendarPopup(True)
        self.mov_date.setDisplayFormat("yyyy-MM-dd")
        self.mov_type = QComboBox()
        self.mov_type.addItems([t("inventory_in"), t("inventory_out")])
        self.mov_qty = QDoubleSpinBox()
        self.mov_qty.setRange(0.01, 1e12)
        self.mov_qty.setDecimals(2)
        self.mov_cost = QDoubleSpinBox()
        self.mov_cost.setRange(0, 1e12)
        self.mov_cost.setDecimals(2)
        self.mov_ref = QLineEdit()
        self.mov_ref.setPlaceholderText(t("inventory_ref"))
        mov_add_btn = QPushButton(t("inventory_mov_add"))
        mov_add_btn.clicked.connect(self._add_movement)
        for w in (self.mov_date, self.mov_type, self.mov_qty, self.mov_cost,
                  self.mov_ref, mov_add_btn):
            mov_form.addWidget(w)
        mov_card.layout().addLayout(mov_form)

        self.mov_table = QTableWidget()
        self.mov_table.setColumnCount(5)
        self.mov_table.setHorizontalHeaderLabels([
            t("inventory_col_date"), t("inventory_col_type"),
            t("inventory_col_qty"), t("inventory_col_cost"),
            t("inventory_col_ref"),
        ])
        self.mov_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mov_table.setEditTriggers(QTableWidget.NoEditTriggers)
        mov_card.layout().addWidget(self.mov_table)
        self._main_layout.addWidget(mov_card)

        self._main_layout.addStretch()

    def _selected_item_id(self):
        row = self.items_table.currentRow()
        if row < 0:
            return None
        item = self.items_table.item(row, 0)
        return int(item.text()) if item else None

    def _on_select_item(self):
        self.refresh_movements()

    def _add_item(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, t("inventory_title"), t("inventory_name_required"))
            return
        try:
            self._engine.add_item(
                name, sku=self.sku_edit.text().strip(),
                category=self.category_edit.text().strip(),
                unit=self.unit_edit.text().strip(),
                quantity=self.qty_spin.value(),
                cost_price=self.cost_spin.value(),
                sale_price=self.price_spin.value(),
                min_quantity=self.min_spin.value(),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("inventory_title"), str(exc))
            return
        self.name_edit.clear()
        self.sku_edit.clear()
        self.category_edit.clear()
        self.unit_edit.clear()
        self.refresh()

    def _add_movement(self):
        item_id = self._selected_item_id()
        if item_id is None:
            QMessageBox.warning(self, t("inventory_title"), t("inventory_select_first"))
            return
        movement_type = "in" if self.mov_type.currentIndex() == 0 else "out"
        try:
            self._engine.add_movement(
                item_id, self.mov_date.date().toString("yyyy-MM-dd"),
                movement_type, self.mov_qty.value(),
                unit_cost=self.mov_cost.value(), reference=self.mov_ref.text().strip(),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("inventory_title"), str(exc))
            return
        self.mov_ref.clear()
        self.refresh()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("inventory_export_csv"), "inventory.csv", "CSV Files (*.csv)")
        if not path:
            return
        import csv
        try:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["id", "sku", "name", "category", "quantity",
                                 "avg_cost", "value"])
                for item in self._engine.list_items():
                    writer.writerow([
                        item["id"], item.get("sku") or "", _plain(item["name"]),
                        item.get("category") or "", item["quantity"],
                        item.get("avg_cost") or 0.0,
                        self._engine.item_value(item["id"])])
            QMessageBox.information(self, t("inventory_title"), t("inventory_export_ok"))
        except Exception as exc:
            QMessageBox.warning(self, t("inventory_title"), str(exc))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("inventory_title"), t("inventory_saved"))
        else:
            QMessageBox.warning(self, t("inventory_title"), t("inventory_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("inventory_title"), t("inventory_clear_confirm")) != \
                QMessageBox.Yes:
            return
        self._engine.clear()
        self.refresh()

    def refresh(self):
        low_only = hasattr(self, "low_only_check") and \
            self.low_only_check.currentIndex() == 1
        category = self.category_filter.text().strip() if hasattr(
            self, "category_filter") else ""
        if low_only:
            items = self._engine.low_stock_items()
        else:
            items = self._engine.list_items()
            if category:
                items = [i for i in items if (i.get("category") or "") == category]
        self.items_table.setRowCount(len(items))
        total_value = 0.0
        for row, item in enumerate(items):
            value = self._engine.item_value(item["id"])
            total_value += value
            self.items_table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.items_table.setItem(row, 1, QTableWidgetItem(item.get("sku") or ""))
            self.items_table.setItem(row, 2, QTableWidgetItem(_plain(item["name"])))
            self.items_table.setItem(row, 3, QTableWidgetItem(item.get("category") or ""))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"{item['quantity']:,.2f}"))
            self.items_table.setItem(
                row, 5, QTableWidgetItem(f"{item.get('avg_cost') or 0:,.2f}"))
            self.items_table.setItem(row, 6, QTableWidgetItem(f"{value:,.2f}"))

        self.stat_items.setText(str(len(self._engine.list_items())))
        self.stat_stock_value.setText(f"{self._engine.stock_value():,.2f}")
        self.stat_low.setText(str(len(self._engine.low_stock_items())))

        self.refresh_movements()

    def refresh_movements(self):
        item_id = self._selected_item_id()
        moves = self._engine.movement_history(item_id) if item_id else []
        self.mov_table.setRowCount(len(moves))
        for row, mv in enumerate(moves):
            self.mov_table.setItem(row, 0, QTableWidgetItem(mv["date"]))
            self.mov_table.setItem(
                row, 1, QTableWidgetItem(
                    t("inventory_in") if mv["type"] == "in"
                    else t("inventory_out")))
            self.mov_table.setItem(row, 2, QTableWidgetItem(f"{mv['quantity']:,.2f}"))
            self.mov_table.setItem(
                row, 3, QTableWidgetItem(f"{mv.get('unit_cost') or 0:,.2f}"))
            self.mov_table.setItem(row, 4, QTableWidgetItem(mv.get("reference") or ""))
