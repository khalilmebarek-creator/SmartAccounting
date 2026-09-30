# واجهة إدارة اشتراكات البائع
# ============================
# توليد مفاتيح ترخيص موقّعة للعملاء + تتبع الاشتراكات.

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QHBoxLayout, QPushButton, QLineEdit,
    QComboBox, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules import vendor_store


class VendorView(BaseView):
    """لوحة إدارة اشتراكات البائع"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("vendor_title", "vendor_subtitle")

        # بطاقة إضافة عميل
        form_card = self._make_card("vendor_add_client")
        form = QHBoxLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("vendor_name_ph"))
        self.name_input.setMinimumHeight(40)
        form.addLayout(self._labeled_field("vendor_name", self.name_input), 2)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText(t("vendor_email_ph"))
        self.email_input.setMinimumHeight(40)
        form.addLayout(self._labeled_field("vendor_email", self.email_input), 2)

        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["Free", "Pro", "Enterprise"])
        self.tier_combo.setMinimumHeight(40)
        form.addLayout(self._labeled_field("vendor_tier", self.tier_combo), 1)

        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 3650)
        self.days_spin.setValue(365)
        self.days_spin.setMinimumHeight(40)
        form.addLayout(self._labeled_field("vendor_days", self.days_spin), 1)

        self.hwid_input = QLineEdit()
        self.hwid_input.setPlaceholderText(t("vendor_hwid_ph"))
        self.hwid_input.setMinimumHeight(40)
        form.addLayout(self._labeled_field("vendor_hwid", self.hwid_input), 2)

        form_card.layout().addLayout(form)

        self.generate_btn = QPushButton(t("vendor_generate"))
        self.generate_btn.setObjectName("primaryBtn")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.clicked.connect(self._add_client)
        form_card.layout().addWidget(self.generate_btn)

        self._main_layout.addWidget(form_card)

        # جدول العملاء
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels([
            t("vendor_tbl_name"), t("vendor_tbl_email"), t("vendor_tbl_tier"),
            t("vendor_tbl_days"), t("vendor_tbl_key"), t("vendor_tbl_date"),
        ])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.clients_table.verticalHeader().setVisible(False)
        self.clients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.clients_table.setMinimumHeight(44 * 6 + 30)
        self._main_layout.addWidget(self.clients_table)

        del_row = QHBoxLayout()
        self.delete_btn = QPushButton(t("vendor_delete"))
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self._delete_selected)
        del_row.addWidget(self.delete_btn)
        del_row.addStretch()
        self._main_layout.addLayout(del_row)

    def _add_client(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, t("warning"), t("vendor_name_required"))
            return
        tier = self.tier_combo.currentText().lower()
        days = self.days_spin.value()
        email = self.email_input.text().strip()
        hwid = self.hwid_input.text().strip()
        try:
            record = vendor_store.add_client(name, email, tier, days, hwid)
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))
            return

        QMessageBox.information(
            self, t("success"),
            f"{t('vendor_key_generated')}\n\n{record['key']}"
        )
        self.name_input.clear()
        self.email_input.clear()
        self.refresh()

    def _delete_selected(self):
        row = self.clients_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("warning"), t("vendor_select_client"))
            return
        client_id = self.clients_table.item(row, 5).data(Qt.ItemDataRole.UserRole)
        vendor_store.delete_client(client_id)
        self.refresh()

    def refresh(self):
        clients = vendor_store.list_clients()
        self.clients_table.setRowCount(len(clients))
        for i, c in enumerate(clients):
            self.clients_table.setItem(i, 0, QTableWidgetItem(c.get("name", "")))
            self.clients_table.setItem(i, 1, QTableWidgetItem(c.get("email", "")))
            self.clients_table.setItem(i, 2, QTableWidgetItem(c.get("tier", "")))
            self.clients_table.setItem(i, 3, QTableWidgetItem(str(c.get("days", ""))))
            key_item = QTableWidgetItem(c.get("key", ""))
            key_item.setToolTip(c.get("key", ""))
            self.clients_table.setItem(i, 4, key_item)
            date_item = QTableWidgetItem(c.get("issued_at", ""))
            date_item.setData(Qt.ItemDataRole.UserRole, c.get("id", ""))
            self.clients_table.setItem(i, 5, date_item)

    def retranslate(self):
        self.clients_table.setHorizontalHeaderLabels([
            t("vendor_tbl_name"), t("vendor_tbl_email"), t("vendor_tbl_tier"),
            t("vendor_tbl_days"), t("vendor_tbl_key"), t("vendor_tbl_date"),
        ])
        self.generate_btn.setText(t("vendor_generate"))
        self.delete_btn.setText(t("vendor_delete"))
