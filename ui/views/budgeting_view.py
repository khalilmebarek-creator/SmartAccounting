# واجهة الميزانية
# ===============
# بنود الميزانية + مقارنة بالفعلي + تحليل الانحراف + تصدير CSV + حفظ قاعدة البيانات

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QMessageBox, QFileDialog, QHeaderView, QFrame, QTextEdit
)

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.budgeting import BudgetManager, budget_manager


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class BudgetingView(BaseView):
    """واجهة الميزانية"""

    def __init__(self):
        super().__init__()
        self._engine = budget_manager
        if not self._engine.load_db():
            self._engine = BudgetManager()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("budgeting_title", "budgeting_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_items = self._make_stat(t("budgeting_stat_items"))
        f2, self.stat_planned = self._make_stat(t("budgeting_stat_planned"))
        f3, self.stat_actual = self._make_stat(t("budgeting_stat_actual"))
        f4, self.stat_variance = self._make_stat(t("budgeting_stat_variance"))
        for w in (f1, f2, f3, f4):
            stats.addWidget(w)
        self._main_layout.addLayout(stats)

        # إضافة بند
        add_card = self._make_card("budgeting_add")
        form = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(2026)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(t("budgeting_item_name"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            t("budgeting_cat_expense"), t("budgeting_cat_revenue"),
            t("budgeting_cat_investment")])
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(-1e12, 1e12)
        self.amount_spin.setDecimals(2)
        add_btn = QPushButton(t("budgeting_add_btn"))
        add_btn.clicked.connect(self._add_item)
        for w in (self.year_spin, self.name_edit, self.category_combo,
                  self.amount_spin, add_btn):
            form.addWidget(w)
        add_card.layout().addLayout(form)
        self._main_layout.addWidget(add_card)

        # جدول البنود
        list_card = self._make_card("budgeting_items")
        actions = QHBoxLayout()
        self.list_year = QSpinBox()
        self.list_year.setRange(2000, 2100)
        self.list_year.setValue(2026)
        self.list_year.valueChanged.connect(self.refresh)
        actions.addWidget(QLabel(t("budgeting_year")))
        actions.addWidget(self.list_year)
        export_btn = QPushButton(t("budgeting_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        actions.addWidget(export_btn)
        save_btn = QPushButton(t("budgeting_save_db"))
        save_btn.clicked.connect(self._save_db)
        actions.addWidget(save_btn)
        clear_btn = QPushButton(t("budgeting_clear"))
        clear_btn.clicked.connect(self._clear_all)
        actions.addWidget(clear_btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([
            t("budgeting_col_id"), t("budgeting_col_name"),
            t("budgeting_col_category"), t("budgeting_col_amount"),
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        list_card.layout().addWidget(self.items_table)
        self._main_layout.addWidget(list_card)

        # المقارنة بالفعلي
        cmp_card = self._make_card("budgeting_compare")
        cmp_form = QHBoxLayout()
        self.actual_input = QTextEdit()
        self.actual_input.setPlaceholderText(t("budgeting_actual_placeholder"))
        self.actual_input.setMaximumHeight(90)
        cmp_btn = QPushButton(t("budgeting_compare_btn"))
        cmp_btn.clicked.connect(self._compare)
        cmp_form.addWidget(self.actual_input)
        cmp_form.addWidget(cmp_btn)
        cmp_card.layout().addLayout(cmp_form)

        self.compare_table = QTableWidget()
        self.compare_table.setColumnCount(5)
        self.compare_table.setHorizontalHeaderLabels([
            t("budgeting_col_name"), t("budgeting_col_planned"),
            t("budgeting_col_actual"), t("budgeting_col_variance"),
            t("budgeting_col_execution"),
        ])
        self.compare_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.compare_table.setEditTriggers(QTableWidget.NoEditTriggers)
        cmp_card.layout().addWidget(self.compare_table)
        self._main_layout.addWidget(cmp_card)

        self._main_layout.addStretch()

    def _add_item(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, t("budgeting_title"), t("budgeting_name_required"))
            return
        categories = ("expense", "revenue", "investment")
        try:
            self._engine.set_budget_item(
                self.year_spin.value(), name, self.amount_spin.value(),
                category=categories[self.category_combo.currentIndex()])
        except Exception as exc:
            QMessageBox.critical(self, t("budgeting_title"), str(exc))
            return
        self.name_edit.clear()
        self.amount_spin.setValue(0.0)
        self.refresh()

    def _parse_actuals(self):
        actuals = {}
        for line in self.actual_input.toPlainText().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 2:
                continue
            name = parts[0].strip()
            try:
                value = float(parts[1].strip())
            except ValueError:
                continue
            actuals[name] = value
        return actuals

    def _compare(self):
        actuals = self._parse_actuals()
        year = self.list_year.value()
        if not actuals:
            QMessageBox.warning(self, t("budgeting_title"), t("budgeting_actual_required"))
            return
        try:
            rows = self._engine.compare_to_actuals(year, actuals)
        except Exception as exc:
            QMessageBox.critical(self, t("budgeting_title"), str(exc))
            return
        self.compare_table.setRowCount(len(rows))
        for r, item in enumerate(rows):
            self.compare_table.setItem(r, 0, QTableWidgetItem(_plain(item["item_name"])))
            self.compare_table.setItem(r, 1, QTableWidgetItem(f"{item['planned']:,.2f}"))
            self.compare_table.setItem(r, 2, QTableWidgetItem(f"{item['actual']:,.2f}"))
            self.compare_table.setItem(r, 3, QTableWidgetItem(f"{item['variance']:,.2f}"))
            self.compare_table.setItem(
                r, 4, QTableWidgetItem(f"{item['execution_pct']:,.0f}%"))
        self.refresh()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("budgeting_export_csv"), "budget.csv", "CSV Files (*.csv)")
        if not path:
            return
        if self._engine.export_csv(path, self.list_year.value()):
            QMessageBox.information(self, t("budgeting_title"), t("budgeting_export_ok"))
        else:
            QMessageBox.warning(self, t("budgeting_title"), t("budgeting_export_fail"))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("budgeting_title"), t("budgeting_saved"))
        else:
            QMessageBox.warning(self, t("budgeting_title"), t("budgeting_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("budgeting_title"), t("budgeting_clear_confirm")) != \
                QMessageBox.Yes:
            return
        self._engine.clear()
        self.refresh()

    def refresh(self):
        year = self.list_year.value()
        items = self._engine.get_budget(year)
        self.items_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.items_table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.items_table.setItem(row, 1, QTableWidgetItem(_plain(item["item_name"])))
            self.items_table.setItem(
                row, 2, QTableWidgetItem(
                    t("budgeting_cat_%s" % item["category"])))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['amount']:,.2f}"))

        totals = self._engine.totals(year)
        self.stat_items.setText(str(totals["count"]))
        self.stat_planned.setText(f"{totals['total']:,.2f}")

        actuals = self._parse_actuals()
        if actuals:
            variance = self._engine.variance_summary(year, actuals)
            self.stat_actual.setText(f"{variance['actual_total']:,.2f}")
            self.stat_variance.setText(f"{variance['variance_total']:,.2f}")
        else:
            self.stat_actual.setText("0.00")
            self.stat_variance.setText("0.00")
