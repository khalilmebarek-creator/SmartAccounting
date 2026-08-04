# شاشة تكامل البنوك واستيراد كشف الحساب
# ========================================

import os
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QFrame, QLineEdit, QMessageBox, QHeaderView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from ui.views._base import BaseView
from ui.resources.i18n import t
from ui.app_state import ThemeColors
from modules.bank_sync import bank_sync


class BankSyncView(BaseView):

    def __init__(self):
        super().__init__()
        self._selected_file = None
        self._import_result = None
        self._setup_ui()

    def _setup_ui(self):
        self._make_header("bank_title", "bank_subtitle")

        toolbar = QHBoxLayout()
        self.btn_select = QPushButton(t("bank_select_file"))
        self.btn_select.clicked.connect(self._select_file)
        self.btn_detect = QPushButton(t("bank_auto_detect"))
        self.btn_detect.clicked.connect(self._auto_detect)
        self.btn_import = QPushButton(t("bank_import"))
        self.btn_import.clicked.connect(self._do_import)
        self.btn_import.setEnabled(False)
        toolbar.addWidget(self.btn_select)
        toolbar.addWidget(self.btn_detect)
        toolbar.addWidget(self.btn_import)
        toolbar.addStretch()
        self._main_layout.addLayout(toolbar)

        config_frame = QFrame()
        config_frame.setObjectName("card")
        config_layout = QHBoxLayout()

        config_layout.addWidget(QLabel(t("bank_select")))
        self.combo_bank = QComboBox()
        banks = bank_sync.get_bank_list()
        for b in banks:
            self.combo_bank.addItem(f"{b['code']} - {b['name_en']}", b["code"])
        self.combo_bank.insertItem(0, t("bank_auto"))
        self.combo_bank.setCurrentIndex(0)
        config_layout.addWidget(self.combo_bank)

        config_layout.addWidget(QLabel(t("bank_account_id")))
        self.txt_account = QLineEdit()
        self.txt_account.setPlaceholderText(t("bank_account_ph"))
        self.txt_account.setMaximumWidth(200)
        config_layout.addWidget(self.txt_account)
        config_layout.addStretch()
        config_frame.setLayout(config_layout)
        self._main_layout.addWidget(config_frame)

        self.file_label = QLabel(t("bank_no_file"))
        self.file_label.setObjectName("headerSubtitle")
        self._main_layout.addWidget(self.file_label)

        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QHBoxLayout()
        self.lbl_count = QLabel(f"{t('bank_count')}: 0")
        self.lbl_debit = QLabel(f"{t('bank_total_debit')}: 0")
        self.lbl_credit = QLabel(f"{t('bank_total_credit')}: 0")
        self.lbl_net = QLabel(f"{t('bank_net')}: 0")
        for lbl in [self.lbl_count, self.lbl_debit, self.lbl_credit, self.lbl_net]:
            lbl.setStyleSheet("font-size: 13px; padding: 5px;")
            stats_layout.addWidget(lbl)
        stats_frame.setLayout(stats_layout)
        self._main_layout.addWidget(stats_frame)

        tx_frame = QFrame()
        tx_frame.setObjectName("card")
        tx_layout = QVBoxLayout()
        tx_title = QLabel(t("bank_transactions"))
        tx_title.setObjectName("cardTitle")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        tx_title.setFont(font)
        tx_layout.addWidget(tx_title)

        self.tx_table = QTableWidget()
        self.tx_table.setAlternatingRowColors(True)
        self.tx_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tx_layout.addWidget(self.tx_table)
        tx_frame.setLayout(tx_layout)
        self._main_layout.addWidget(tx_frame)

        recon_frame = QFrame()
        recon_frame.setObjectName("card")
        recon_layout = QVBoxLayout()
        recon_title = QLabel(t("bank_reconcile"))
        recon_title.setObjectName("cardTitle")
        recon_title.setFont(font)
        recon_layout.addWidget(recon_title)

        recon_stats = QHBoxLayout()
        self.lbl_matched = QLabel(f"{t('bank_matched')}: 0")
        self.lbl_unmatched_bank = QLabel(f"{t('bank_unmatched_bank')}: 0")
        self.lbl_unmatched_book = QLabel(f"{t('bank_unmatched_book')}: 0")
        self.lbl_match_rate = QLabel(f"{t('bank_match_rate')}: 0%")
        for lbl in [self.lbl_matched, self.lbl_unmatched_bank, self.lbl_unmatched_book, self.lbl_match_rate]:
            lbl.setStyleSheet("font-size: 13px; padding: 5px;")
            recon_stats.addWidget(lbl)
        recon_layout.addLayout(recon_stats)
        recon_frame.setLayout(recon_layout)
        self._main_layout.addWidget(recon_frame)

        self._main_layout.addStretch()

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("bank_select_file"),
            "",
            f"{t('bank_csv')} (*.csv);;{t('bank_all')} (*)"
        )
        if not path:
            return

        self._selected_file = path
        filename = os.path.basename(path)
        self.file_label.setText(f"📂 {filename}")
        self.btn_import.setEnabled(True)

    def _auto_detect(self):
        if not self._selected_file:
            QMessageBox.information(self, t("bank_info"), t("bank_select_first"))
            return

        detected = bank_sync.detect_bank(self._selected_file)
        if detected:
            for i in range(self.combo_bank.count()):
                if self.combo_bank.itemData(i) == detected:
                    self.combo_bank.setCurrentIndex(i)
                    break
            QMessageBox.information(
                self, t("bank_detected"),
                f"{t('bank_detected_msg')}: {detected}"
            )
        else:
            QMessageBox.warning(self, t("bank_not_detected"), t("bank_not_detected_msg"))

    def _do_import(self):
        if not self._selected_file:
            return

        bank_code = self.combo_bank.currentData()
        if bank_code is None or self.combo_bank.currentIndex() == 0:
            bank_code = None

        account_id = self.txt_account.text().strip()

        result = bank_sync.import_bank_statement(
            self._selected_file, bank_code=bank_code, account_id=account_id
        )
        self._import_result = result

        transactions = result.get("transactions", [])
        self.lbl_count.setText(f"{t('bank_count')}: {result.get('count', 0)}")

        total_debit = result.get("total_debit", 0)
        total_credit = result.get("total_credit", 0)
        net = total_credit - total_debit

        self.lbl_debit.setText(f"{t('bank_total_debit')}: {total_debit:,.2f}")
        self.lbl_credit.setText(f"{t('bank_total_credit')}: {total_credit:,.2f}")
        self.lbl_net.setText(f"{t('bank_net')}: {net:,.2f}")

        if net >= 0:
            self.lbl_net.setStyleSheet("color: #27AE60; font-size: 13px; font-weight: bold; padding: 5px;")
        else:
            self.lbl_net.setStyleSheet("color: #E74C3C; font-size: 13px; font-weight: bold; padding: 5px;")

        self._populate_table(transactions)

        errors = result.get("errors", [])
        if errors:
            QMessageBox.warning(
                self, t("bank_import_errors"),
                "\n".join(errors[:5])
            )
        elif transactions:
            QMessageBox.information(
                self, t("bank_import_success"),
                f"{t('bank_imported')}: {len(transactions)}"
            )

    def _populate_table(self, transactions):
        self.tx_table.clear()
        if not transactions:
            return

        headers = [
            t("bank_col_date"), t("bank_col_desc"),
            t("bank_col_debit"), t("bank_col_credit"), t("bank_col_balance")
        ]
        self.tx_table.setColumnCount(len(headers))
        self.tx_table.setHorizontalHeaderLabels(headers)
        self.tx_table.setRowCount(len(transactions))

        for i, tx in enumerate(transactions):
            date_item = QTableWidgetItem(tx.get("date", ""))
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.tx_table.setItem(i, 0, date_item)

            desc_item = QTableWidgetItem(tx.get("description", ""))
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.tx_table.setItem(i, 1, desc_item)

            for j, key in enumerate(["debit", "credit", "balance"], start=2):
                val = tx.get(key, 0)
                item = QTableWidgetItem(f"{val:,.2f}" if val else "—")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if key == "credit" and val > 0:
                    item.setForeground(QColor(ThemeColors.get("success")))
                elif key == "debit" and val > 0:
                    item.setForeground(QColor(ThemeColors.get("error")))
                self.tx_table.setItem(i, j, item)

    def refresh(self):
        pass

    def retranslate(self):
        self._clear_layout()
        self._setup_ui()
