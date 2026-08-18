# تحليل مراكز التكلفة
# ======================

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDoubleSpinBox, QLineEdit, QTableWidget,
    QTableWidgetItem, QGroupBox, QHeaderView, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.cost_center import CostCenterAnalyzer


class CostCenterView(QWidget):
    """واجهة تحليل مراكز التكلفة"""

    MAX_CENTERS = 10

    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(t("cost_center_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("cost_center_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        input_group = QGroupBox(t("cost_center_title"))
        input_layout = QVBoxLayout()

        self.center_table = QTableWidget()
        self.center_table.setColumnCount(4)
        self.center_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_headcount")
        ])
        self.center_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.center_table.setRowCount(5)

        self._center_data = []
        for i in range(5):
            name_edit = QLineEdit()
            name_edit.setPlaceholderText(t("cost_center_placeholder").format(n=i + 1))
            self.center_table.setCellWidget(i, 0, name_edit)

            costs_spin = QDoubleSpinBox()
            costs_spin.setRange(0, 1_000_000_000)
            costs_spin.setDecimals(0)
            costs_spin.setGroupSeparatorShown(True)
            self.center_table.setCellWidget(i, 1, costs_spin)

            rev_spin = QDoubleSpinBox()
            rev_spin.setRange(0, 1_000_000_000)
            rev_spin.setDecimals(0)
            rev_spin.setGroupSeparatorShown(True)
            self.center_table.setCellWidget(i, 2, rev_spin)

            hc_spin = QDoubleSpinBox()
            hc_spin.setRange(1, 10000)
            hc_spin.setDecimals(0)
            hc_spin.setValue(5)
            self.center_table.setCellWidget(i, 3, hc_spin)

            self._center_data.append((name_edit, costs_spin, rev_spin, hc_spin))

        input_layout.addWidget(self.center_table)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        self.run_btn = QPushButton(t("cost_center_run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.run_analysis)
        main_layout.addWidget(self.run_btn)

        summary_layout = QHBoxLayout()
        self.card_total_costs = QLabel("--")
        self.card_total_rev = QLabel("--")
        self.card_total_profit = QLabel("--")
        self.card_ranking = QLabel("--")
        for card_label, card_val in [
            (t("cost_center_total_costs"), self.card_total_costs),
            (t("cost_center_total_revenue"), self.card_total_rev),
            (t("cost_center_total_profit"), self.card_total_profit),
            (t("cost_center_ranking"), self.card_ranking),
        ]:
            frame = QGroupBox(card_label)
            frame.setObjectName("card")
            vl = QVBoxLayout()
            font = QFont()
            font.setPointSize(14)
            font.setBold(True)
            card_val.setFont(font)
            card_val.setAlignment(Qt.AlignCenter)
            vl.addWidget(card_val)
            frame.setLayout(vl)
            summary_layout.addWidget(frame)
        main_layout.addLayout(summary_layout)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_profit"),
            t("cost_center_margin"), t("cost_center_efficiency")
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setMinimumHeight(44 * 5 + 30)
        main_layout.addWidget(self.results_table)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor(ThemeColors.get("chart_bg"))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(280)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

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

        self.card_total_costs.setText(f"{summary['total_costs']:,.0f}")
        self.card_total_rev.setText(f"{summary['total_revenue']:,.0f}")
        self.card_total_profit.setText(f"{summary['total_profit']:,.0f}")
        ranked = self.analyzer.rank_by_efficiency()
        self.card_ranking.setText(ranked[0]["name"] if ranked else "--")

        items = self.analyzer.centers
        self.results_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.results_table.setItem(i, 0, QTableWidgetItem(item["name"]))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{item['costs']:,.0f}"))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{item['revenue']:,.0f}"))

            profit_item = QTableWidgetItem(f"{item['profit']:,.0f}")
            if item["profit"] < 0:
                profit_item.setForeground(QColor(ThemeColors.get('error')))
            else:
                profit_item.setForeground(QColor(ThemeColors.get('success')))
            self.results_table.setItem(i, 3, profit_item)

            self.results_table.setItem(i, 4, QTableWidgetItem(f"{item['margin_pct']:.1f}%"))
            self.results_table.setItem(i, 5, QTableWidgetItem(f"{item['efficiency']:.2f}x"))

        self._draw_chart(items)

    def _draw_chart(self, items):
        import matplotlib.pyplot as plt
        plt.close(self.figure)
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        labels = [item["name"][:12] for item in items]
        costs = [item["costs"] for item in items]
        revenues = [item["revenue"] for item in items]

        x = range(len(labels))
        width = 0.35

        ax.bar([i - width / 2 for i in x], costs, width, label=t("cost_center_costs"),
               color=ThemeColors.get('error'), alpha=0.8)
        ax.bar([i + width / 2 for i in x], revenues, width, label=t("cost_center_revenue"),
               color=ThemeColors.get('success'), alpha=0.8)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.figure.tight_layout()
        self.canvas.draw()

    def retranslate(self):
        self.title.setText(t("cost_center_title"))
        self.subtitle.setText(t("cost_center_subtitle"))
        self.run_btn.setText(t("cost_center_run"))
        self.center_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_headcount")
        ])
        self.results_table.setHorizontalHeaderLabels([
            t("cost_center_name"), t("cost_center_costs"),
            t("cost_center_revenue"), t("cost_center_profit"),
            t("cost_center_margin"), t("cost_center_efficiency")
        ])

    def refresh(self):
        pass
