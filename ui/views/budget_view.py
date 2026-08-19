# التخطيط والمتابعة المالية
# ===========================

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QHeaderView, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import pyqtgraph as pg
from ui.charts import (PgChartWidget, draw_grouped_bar,
    _text_color, _chart_bg, _mk_brush, _mk_pen, _mk_text_item)

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.budget import BudgetPlanner


class BudgetView(QWidget):
    """واجهة التخطيط والمتابعة المالية"""

    def __init__(self):
        super().__init__()
        self.planner = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(t("budget_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("budget_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        input_group = QGroupBox(t("budget_categories"))
        input_layout = QVBoxLayout()

        self.input_table = QTableWidget()
        self.input_table.setColumnCount(2)
        self.input_table.setHorizontalHeaderLabels([t("budget_category"), t("budget_amount")])
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.input_table.verticalHeader().setDefaultSectionSize(44)
        self.input_table.setMinimumHeight(44 * 6 + 30)

        categories = [
            t("budget_cat_revenue"), t("budget_cat_cogs"),
            t("budget_cat_opex"), t("budget_cat_salaries"),
            t("budget_cat_marketing"), t("budget_cat_admin")
        ]
        self.input_table.setRowCount(len(categories))
        self._budget_spins = []
        for i, cat in enumerate(categories):
            cat_item = QTableWidgetItem(cat)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.input_table.setItem(i, 0, cat_item)
            spin = QDoubleSpinBox()
            spin.setRange(0, 1_000_000_000)
            spin.setDecimals(0)
            spin.setGroupSeparatorShown(True)
            self._budget_spins.append(spin)
            self.input_table.setCellWidget(i, 1, spin)

        input_layout.addWidget(self.input_table)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        self.run_btn = QPushButton(t("budget_run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.run_budget)
        main_layout.addWidget(self.run_btn)

        summary_layout = QHBoxLayout()
        self.card_budgeted = QLabel("--")
        self.card_actual = QLabel("--")
        self.card_util = QLabel("--")
        self.card_alerts = QLabel("--")
        cards = [
            (t("budget_total_budgeted"), self.card_budgeted),
            (t("budget_total_actual"), self.card_actual),
            (t("budget_utilization"), self.card_util),
            (t("budget_alert_count"), self.card_alerts),
        ]
        for card_label, card_val in cards:
            frame = QGroupBox(card_label)
            frame.setObjectName("card")
            frame.setMinimumHeight(60)
            frame.setMinimumWidth(150)
            vl = QVBoxLayout()
            font = QFont()
            font.setPointSize(16)
            font.setBold(True)
            card_val.setFont(font)
            card_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vl.addWidget(card_val)
            frame.setLayout(vl)
            summary_layout.addWidget(frame)
        main_layout.addLayout(summary_layout)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            t("budget_category"), t("budget_amount"),
            t("budget_actual"), t("budget_variance"), t("budget_status")
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setDefaultSectionSize(44)
        self.results_table.setMinimumHeight(44 * 6 + 30)
        self.results_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(self.results_table)

        self.chart = PgChartWidget("Budget")
        self.chart.setMinimumHeight(280)
        main_layout.addWidget(self.chart)

        self.setLayout(main_layout)

    def _cat_keys(self):
        return [
            "revenue", "cost_of_goods_sold", "operating_expenses",
            "salaries", "marketing", "admin_expenses"
        ]

    def run_budget(self):
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("forecast_no_data"))
            return

        self.planner = BudgetPlanner(state.financial_data)
        categories = {}
        keys = self._cat_keys()
        for i, spin in enumerate(self._budget_spins):
            if i < len(keys):
                categories[keys[i]] = {"budgeted": spin.value()}

        self.planner.create_annual_budget(categories)
        summary = self.planner.get_summary()
        alerts = self.planner.get_alerts()

        self.card_budgeted.setText(f"{summary['total_budgeted']:,.0f}")
        self.card_actual.setText(f"{summary['total_actual']:,.0f}")
        self.card_util.setText(f"{summary['utilization_pct']:.1f}%")
        self.card_alerts.setText(f"{len(alerts)}")

        items = self.planner.budget_items
        self.results_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.results_table.setItem(i, 0, QTableWidgetItem(item["category"]))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{item['budgeted']:,.0f}"))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{item['actual']:,.0f}"))
            var_item = QTableWidgetItem(f"{item['variance']:,.0f}")
            if item["variance"] > 0:
                var_item.setForeground(QColor(ThemeColors.get('error')))
            elif item["variance"] < 0:
                var_item.setForeground(QColor(ThemeColors.get('success')))
            self.results_table.setItem(i, 3, var_item)
            status_item = QTableWidgetItem(item["status"])
            self.results_table.setItem(i, 4, status_item)

        self._draw_chart(items)

    def _draw_chart(self, items):
        labels = [item["category"][:10] for item in items]
        budgeted = [item["budgeted"] for item in items]
        actual = [item["actual"] for item in items]

        draw_grouped_bar(self.chart.plot_item, labels, [
            {"label": t("budget_amount"), "values": budgeted, "color": ThemeColors.get('info')},
            {"label": t("budget_actual"), "values": actual, "color": ThemeColors.get('warning')},
        ])

    def retranslate(self):
        self.title.setText(t("budget_title"))
        self.subtitle.setText(t("budget_subtitle"))
        self.run_btn.setText(t("budget_run"))
        self.results_table.setHorizontalHeaderLabels([
            t("budget_category"), t("budget_amount"),
            t("budget_actual"), t("budget_variance"), t("budget_status")
        ])

    def refresh(self):
        pass
