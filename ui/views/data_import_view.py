# شاشة استيراد البيانات من CSV/Excel
# ====================================

import os
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QFrame, QMessageBox, QHeaderView, QGridLayout,
    QTextEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QFont)

from ui.views._base import BaseView
from ui.resources.i18n import t
from ui.app_state import state
from modules.csv_import import csv_importer


class DataImportView(BaseView):

    MONTHS_AR = [
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]

    def __init__(self):
        super().__init__()
        self._selected_file = None
        self._import_result = None
        self._setup_ui()

    def _setup_ui(self):
        self._make_header("imp_title", "imp_subtitle")

        toolbar = QHBoxLayout()
        self.btn_select = QPushButton(t("imp_select_file"))
        self.btn_select.clicked.connect(self._select_file)
        self.btn_import = QPushButton(t("imp_import"))
        self.btn_import.clicked.connect(self._do_import)
        self.btn_import.setEnabled(False)
        toolbar.addWidget(self.btn_select)
        toolbar.addWidget(self.btn_import)
        toolbar.addStretch()
        self._main_layout.addLayout(toolbar)

        file_frame = QFrame()
        file_frame.setObjectName("card")
        file_layout = QVBoxLayout()
        self.lbl_file = QLabel(t("imp_no_file"))
        self.lbl_file.setObjectName("headerSubtitle")
        file_layout.addWidget(self.lbl_file)

        opts = QHBoxLayout()
        opts.addWidget(QLabel(t("imp_encoding")))
        self.combo_encoding = QComboBox()
        self.combo_encoding.addItems(["UTF-8", "Latin-1", "CP1252", "ISO-8859-1"])
        opts.addWidget(self.combo_encoding)
        opts.addWidget(QLabel(t("imp_language")))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["العربية", "English", "Français"])
        opts.addWidget(self.combo_lang)
        opts.addStretch()
        file_layout.addLayout(opts)
        file_frame.setLayout(file_layout)
        self._main_layout.addWidget(file_frame)

        mapping_frame = QFrame()
        mapping_frame.setObjectName("card")
        mapping_layout = QVBoxLayout()
        mapping_title = QLabel(t("imp_mapping"))
        mapping_title.setObjectName("cardTitle")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        mapping_title.setFont(font)
        mapping_layout.addWidget(mapping_title)

        self.mapping_grid = QGridLayout()
        self.mapping_labels = {}
        self.mapping_combos = {}
        fields = [
            ("date", t("imp_field_date")),
            ("description", t("imp_field_desc")),
            ("debit", t("imp_field_debit")),
            ("credit", t("imp_field_credit")),
            ("amount", t("imp_field_amount")),
            ("account", t("imp_field_account")),
        ]
        for i, (field, label) in enumerate(fields):
            lbl = QLabel(label)
            self.mapping_grid.addWidget(lbl, i, 0)
            combo = QComboBox()
            combo.addItem("—")
            self.mapping_grid.addWidget(combo, i, 1)
            self.mapping_labels[field] = lbl
            self.mapping_combos[field] = combo

        mapping_layout.addLayout(self.mapping_grid)
        mapping_frame.setLayout(mapping_layout)
        self._main_layout.addWidget(mapping_frame)

        preview_frame = QFrame()
        preview_frame.setObjectName("card")
        preview_layout = QVBoxLayout()
        self.preview_title = QLabel(t("imp_preview"))
        self.preview_title.setObjectName("cardTitle")
        self.preview_title.setFont(font)
        preview_layout.addWidget(self.preview_title)

        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        preview_layout.addWidget(self.preview_table)
        preview_frame.setLayout(preview_layout)
        self._main_layout.addWidget(preview_frame)

        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QHBoxLayout()
        self.lbl_total = QLabel(f"{t('imp_stat_total')}: 0")
        self.lbl_imported = QLabel(f"{t('imp_stat_imported')}: 0")
        self.lbl_skipped = QLabel(f"{t('imp_stat_skipped')}: 0")
        self.lbl_errors = QLabel(f"{t('imp_stat_errors')}: 0")
        for lbl in [self.lbl_total, self.lbl_imported, self.lbl_skipped, self.lbl_errors]:
            lbl.setStyleSheet("font-size: 13px; padding: 5px;")
            stats_layout.addWidget(lbl)
        stats_frame.setLayout(stats_layout)
        self._main_layout.addWidget(stats_frame)

        self.errors_text = QTextEdit()
        self.errors_text.setReadOnly(True)
        self.errors_text.setMaximumHeight(100)
        self.errors_text.setPlaceholderText(t("imp_errors_placeholder"))
        self._main_layout.addWidget(self.errors_text)

        self._main_layout.addStretch()

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("imp_select_file"),
            "",
            f"{t('imp_files')} (*.csv *.xlsx *.xls *.tsv);;{t('imp_csv')} (*.csv);;{t('imp_excel')} (*.xlsx *.xls)"
        )
        if not path:
            return

        self._selected_file = path
        filename = os.path.basename(path)
        self.lbl_file.setText(f"📂 {filename}")
        self.btn_import.setEnabled(True)

        lang_codes = ["ar", "en", "fr"]
        lang_idx = self.combo_lang.currentIndex()
        lang = lang_codes[lang_idx]

        file_type = csv_importer.detect_file_type(path)
        if file_type in ("csv", "tsv"):
            headers, rows = csv_importer.read_csv(path)
        elif file_type == "excel":
            headers, rows = csv_importer.read_excel(path)
        else:
            QMessageBox.warning(self, t("imp_error"), t("imp_unsupported"))
            return

        if not headers:
            QMessageBox.warning(self, t("imp_error"), t("imp_no_data"))
            return

        mapping = csv_importer.auto_map_columns(headers, lang)

        for field, combo in self.mapping_combos.items():
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("—")
            for h in headers:
                combo.addItem(h)
            if field in mapping:
                idx = mapping[field] + 1
                if idx < combo.count():
                    combo.setCurrentIndex(idx)
            combo.blockSignals(False)

        self._show_preview(headers, rows)

    def _show_preview(self, headers, rows):
        preview = rows[:10]
        self.preview_table.setRowCount(len(preview))
        self.preview_table.setColumnCount(len(headers))
        self.preview_table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(preview):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.preview_table.setItem(i, j, item)

        self.preview_title.setText(f"{t('imp_preview')} ({len(rows)} {t('imp_rows')})")

    def _do_import(self):
        if not self._selected_file:
            return

        lang_codes = ["ar", "en", "fr"]
        lang = lang_codes[self.combo_lang.currentIndex()]
        encoding = self.combo_encoding.currentText()

        result = csv_importer.import_data(self._selected_file, lang=lang, encoding=encoding)
        self._import_result = result

        stats = result["stats"]
        self.lbl_total.setText(f"{t('imp_stat_total')}: {stats['total']}")
        self.lbl_imported.setText(f"{t('imp_stat_imported')}: {stats['imported']}")
        self.lbl_skipped.setText(f"{t('imp_stat_skipped')}: {stats['skipped']}")
        self.lbl_errors.setText(f"{t('imp_stat_errors')}: {stats['errors']}")

        self.lbl_imported.setStyleSheet("color: #27AE60; font-weight: bold; font-size: 13px; padding: 5px;")
        self.lbl_errors.setStyleSheet("color: #E74C3C; font-size: 13px; padding: 5px;" if stats['errors'] > 0 else "font-size: 13px; padding: 5px;")

        if result["errors"]:
            self.errors_text.setPlainText("\n".join(result["errors"][:20]))
        else:
            self.errors_text.clear()

        if result["data"]:
            self._preview_imported_data(result["data"], result["column_mapping"])

        if stats["imported"] > 0:
            state.data["imported_transactions"] = result["data"]
            state.save_data()
            QMessageBox.information(
                self, t("imp_success"),
                f"{t('imp_imported_count')}: {stats['imported']}"
            )

    def _preview_imported_data(self, data, mapping):
        self.preview_table.clear()
        if not data:
            return

        headers = list(mapping.keys()) if mapping else list(data[0].keys())
        display_headers = [h.upper() for h in headers]
        self.preview_table.setColumnCount(len(headers))
        self.preview_table.setHorizontalHeaderLabels(display_headers)
        self.preview_table.setRowCount(min(len(data), 20))

        for i, record in enumerate(data[:20]):
            for j, field in enumerate(headers):
                val = record.get(field, "")
                if isinstance(val, float):
                    val = f"{val:,.2f}"
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.preview_table.setItem(i, j, item)

    def refresh(self):
        pass

    def retranslate(self):
        self._clear_layout()
        self._setup_ui()
