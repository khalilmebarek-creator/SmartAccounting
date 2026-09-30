# ØªØ­Ù„ÙŠÙ„ Ù…Ø±Ø§ÙƒØ² Ø§Ù„ØªÙƒÙ„ÙØ©
# ======================

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QDoubleSpinBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QAbstractSpinBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from ui.charts import PgChartWidget, draw_grouped_bar
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from ui.views._base import BaseView
from modules.cost_center import CostCenterAnalyzer


class NoWheelSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox Ø¨Ù„Ø§ ØªØ¹Ø¯ÙŠÙ„ Ø¨Ø£Ø³Ø·ÙˆØ§Ù†Ø© Ø§Ù„Ù…Ø§ÙˆØ³ â€” Ø§Ù„ØªØ¹Ø¯ÙŠÙ„ Ø¨Ø§Ù„ÙƒØªØ§Ø¨Ø© ÙÙ‚Ø·."""

    def wheelEvent(self, event):
        event.ignore()


class CostCenterView(BaseView):
    """ÙˆØ§Ø¬Ù‡Ø© ØªØ­Ù„ÙŠÙ„ Ù…Ø±Ø§ÙƒØ² Ø§Ù„ØªÙƒÙ„ÙØ©"""

    MAX_CENTERS = 10

    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.setup_ui()

    def setup_ui(self):
        self._make_header("cost_center_title", "cost_center_subtitle")

        # 1. Ø¨Ø·Ø§Ù‚Ø© Ø¥Ø¯Ø®Ø§Ù„ Ø¨ÙŠØ§Ù†Ø§Øª Ø§Ù„Ù…Ø±Ø§ÙƒØ²
        input_card = self._make_card("cost_center_input")
        self.center_table = QTableWidget()
        self.center_table.setColumnCount(4)
        self.center_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_headcount"),
        ])
        self.center_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.center_table.verticalHeader().setVisible(False)
        self.center_table.verticalHeader().setDefaultSectionSize(44)
        self.center_table.setRowCount(self.MAX_CENTERS)
        self.center_table.setMinimumHeight(44 * 6 + 40)

        self._center_data = []
        for i in range(self.MAX_CENTERS):
            name_edit = QLineEdit()
            name_edit.setPlaceholderText(t("cost_center_placeholder").format(n=i + 1))
            name_edit.setMinimumHeight(40)
            name_edit.setFrame(False)
            name_edit.setStyleSheet("border: none; background: transparent;")
            self.center_table.setCellWidget(i, 0, name_edit)

            costs_spin = NoWheelSpinBox()
            costs_spin.setRange(0, 1_000_000_000)
            costs_spin.setDecimals(0)
            costs_spin.setGroupSeparatorShown(True)
            costs_spin.setMinimumHeight(40)
            costs_spin.setFrame(False)
            costs_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            costs_spin.setStyleSheet("border: none; background: transparent;")
            self.center_table.setCellWidget(i, 1, costs_spin)

            rev_spin = NoWheelSpinBox()
            rev_spin.setRange(0, 1_000_000_000)
            rev_spin.setDecimals(0)
            rev_spin.setGroupSeparatorShown(True)
            rev_spin.setMinimumHeight(40)
            rev_spin.setFrame(False)
            rev_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            rev_spin.setStyleSheet("border: none; background: transparent;")
            self.center_table.setCellWidget(i, 2, rev_spin)

            hc_spin = NoWheelSpinBox()
            hc_spin.setRange(1, 10000)
            hc_spin.setDecimals(0)
            hc_spin.setValue(5)
            hc_spin.setMinimumHeight(40)
            hc_spin.setFrame(False)
            hc_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            hc_spin.setStyleSheet("border: none; background: transparent;")
            self.center_table.setCellWidget(i, 3, hc_spin)

            self._center_data.append((name_edit, costs_spin, rev_spin, hc_spin))

        input_card.layout().addWidget(self.center_table)
        self._main_layout.addWidget(input_card)

        # 2. Ø²Ø± Ø§Ù„ØªØ­Ù„ÙŠÙ„
        self.run_btn = QPushButton(t("cost_center_run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.run_analysis)
        self._main_layout.addWidget(self.run_btn)

        # 3. Ø¨Ø·Ø§Ù‚Ø§Øª Ø§Ù„Ø¥Ø­ØµØ§Ø¦ÙŠØ§Øª
        stats = QHBoxLayout()
        self._stat_costs, self._val_costs = self._make_stat(t("cost_center_total_costs"))
        self._stat_rev, self._val_rev = self._make_stat(t("cost_center_total_revenue"))
        self._stat_profit, self._val_profit = self._make_stat(t("cost_center_total_profit"))
        self._stat_rank, self._val_rank = self._make_stat(t("cost_center_ranking"))
        rank_font = QFont()
        rank_font.setPointSize(12)
        rank_font.setBold(True)
        self._val_rank.setFont(rank_font)
        for s in (self._stat_costs, self._stat_rev, self._stat_profit, self._stat_rank):
            stats.addWidget(s, 1)
        self._main_layout.addLayout(stats)

        # 4. Ø¬Ø¯ÙˆÙ„ Ø§Ù„Ù†ØªØ§Ø¦Ø¬
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_profit"),
            t("cost_center_margin"), t("cost_center_efficiency"),
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setMinimumHeight(44 * 5 + 30)
        self._main_layout.addWidget(self.results_table)

        # 5. Ø§Ù„Ø±Ø³Ù… Ø§Ù„Ø¨ÙŠØ§Ù†ÙŠ
        self.chart = PgChartWidget(t("cost_center_chart_title"))
        self.chart.setMinimumHeight(280)
        self._main_layout.addWidget(self.chart)

    def _collect_centers(self):
        centers = []
        for name_edit, costs_spin, rev_spin, hc_spin in self._center_data:
            name = name_edit.text().strip()
            if name and costs_spin.value() > 0:
                centers.append({
                    "name": name,
                    "costs": costs_spin.value(),
                    "revenue": rev_spin.value(),
                    "headcount": int(hc_spin.value())
                })
        return centers

    def run_analysis(self):
        centers = self._collect_centers()
        if not centers:
            QMessageBox.warning(self, t("warning"), t("forecast_no_data"))
            return

        self.analyzer = CostCenterAnalyzer(state.financial_data)
        self.analyzer.define_centers(centers)
        summary = self.analyzer.get_summary()

        self._val_costs.setText(f"{summary['total_costs']:,.0f}")
        self._val_rev.setText(f"{summary['total_revenue']:,.0f}")
        self._val_profit.setText(f"{summary['total_profit']:,.0f}")
        if summary['total_profit'] < 0:
            self._val_profit.setStyleSheet(f"color: {ThemeColors.get('error')};")
        else:
            self._val_profit.setStyleSheet(f"color: {ThemeColors.get('success')};")

        ranked = self.analyzer.rank_by_efficiency()
        self._val_rank.setText(ranked[0]["name"] if ranked else "--")

        items = self.analyzer.centers
        self.results_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.results_table.setItem(i, 0, QTableWidgetItem(item["name"]))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{item['costs']:,.0f}"))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{item['revenue']:,.0f}"))

            profit_item = QTableWidgetItem(f"{item['profit']:,.0f}")
            profit_item.setForeground(
                QColor(ThemeColors.get('error')) if item["profit"] < 0
                else QColor(ThemeColors.get('success'))
            )
            self.results_table.setItem(i, 3, profit_item)

            margin_item = QTableWidgetItem(f"{item['margin_pct']:.1f}%")
            margin_item.setForeground(
                QColor(ThemeColors.get('error')) if item["margin_pct"] < 0
                else QColor(ThemeColors.get('text'))
            )
            self.results_table.setItem(i, 4, margin_item)

            self.results_table.setItem(i, 5, QTableWidgetItem(f"{item['efficiency']:.2f}x"))

        self._draw_chart(items)

    def _draw_chart(self, items):
        labels = [item["name"][:12] for item in items]
        costs = [item["costs"] for item in items]
        revenues = [item["revenue"] for item in items]

        draw_grouped_bar(self.chart.plot_item, labels, [
            {"label": t("cost_center_costs"), "values": costs, "color": ThemeColors.get('error')},
            {"label": t("cost_center_revenue"), "values": revenues, "color": ThemeColors.get('success')},
        ])

    def retranslate(self):
        self.center_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_headcount")
        ])
        self.results_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_profit"),
            t("cost_center_margin"), t("cost_center_efficiency")
        ])
        self.run_btn.setText(t("cost_center_run"))

    def refresh(self):
        pass
