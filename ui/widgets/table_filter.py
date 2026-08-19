"""Reusable table filter/search widget for QTableWidget."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import (pyqtSignal)
from ui.resources.i18n import t


class TableFilterWidget(QWidget):
    """A search bar that filters rows in a QTableWidget by text content."""

    filter_changed = pyqtSignal(str)

    def __init__(self, table, placeholder="", parent=None):
        super().__init__(parent)
        self.table = table
        self._setup_ui(placeholder)

    def _setup_ui(self, placeholder):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        icon_label = QLabel("🔍")
        layout.addWidget(icon_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder or t("filter_placeholder"))
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search_input)

        self.count_label = QLabel()
        self.count_label.setObjectName("subtitleLabel")
        layout.addWidget(self.count_label)

    def _apply_filter(self, text):
        text = text.lower().strip()
        visible = 0
        total = self.table.rowCount()

        for row in range(total):
            show = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    show = True
                    break
            self.table.setRowHidden(row, not show)
            if show:
                visible += 1

        self.count_label.setText(f"{visible}/{total}")
        self.filter_changed.emit(text)

    def clear(self):
        self.search_input.clear()
