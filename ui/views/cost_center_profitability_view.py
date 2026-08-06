# واجهة ربحية مراكز التكلفة
# ============================
# تعريف مراكز التكلفة + توزيع التكاليف + تحليل الربحية + المقارنات + التقارير

from ui.views._path import _  # noqa: F401

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_pdf import PdfPages

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QLineEdit, QDoubleSpinBox, QMessageBox,
    QFileDialog, QHeaderView, QGroupBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from ui.views._base import BaseView
from ui.views.dashboard import ChartWidget, _chart_text_color
from ui.app_state import ThemeColors
from ui.resources.i18n import t
from modules.cost_center_profitability import CostCenterProfitabilityEngine

_CENTER_TYPES = ["department", "project", "branch", "production_line"]
_TYPE_LABEL_KEYS = [
    "cost_profit_type_department",
    "cost_profit_type_project",
    "cost_profit_type_branch",
    "cost_profit_type_production_line",
]
_REC_TYPE_KEYS = {
    "loss_warning": "cost_profit_rec_loss",
    "high_indirect": "cost_profit_rec_high_indirect",
    "low_margin": "cost_profit_rec_low_margin",
    "top_performer": "cost_profit_rec_top",
    "high_cost_per_head": "cost_profit_rec_high_cost",
}
_CHANGE_KEYS = {
    "improved": "cost_profit_change_improved",
    "declined": "cost_profit_change_declined",
    "stable": "cost_profit_change_stable",
}
_STATUS_KEYS = {
    "above": "cost_profit_status_above",
    "below": "cost_profit_status_below",
    "meets": "cost_profit_status_meets",
}
_DIRECTION_KEYS = {
    "up": "cost_profit_direction_up",
    "down": "cost_profit_direction_down",
    "flat": "cost_profit_direction_flat",
}


def _plain(title):
    return "".join(ch for ch in (title or "") if ord(ch) < 0xFFFF)


class CostCenterProfitabilityView(BaseView):
    """تحليل ربحية مراكز التكلفة المتقدم"""

    MAX_CENTERS = 8
    MAX_PERIODS = 4

    def __init__(self):
        super().__init__()
        self._engine = CostCenterProfitabilityEngine()
        self._result = None
        self._comparison = None
        self._trend = None
        self.setup_ui()
        self.refresh()

    # ===== البناء =====

    def setup_ui(self):
        self.title_label = self._make_header("cost_profit_title", "cost_profit_subtitle")

        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addStretch()
        self.export_pdf_btn = QPushButton(t("cost_profit_export_pdf"))
        self.export_pdf_btn.setObjectName("secondaryBtn")
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        controls.addWidget(self.export_pdf_btn)
        self.export_excel_btn = QPushButton(t("cost_profit_export_excel"))
        self.export_excel_btn.setObjectName("secondaryBtn")
        self.export_excel_btn.clicked.connect(self._export_excel)
        controls.addWidget(self.export_excel_btn)
        self._main_layout.addLayout(controls)

        self._build_centers_group()
        self._build_allocate_group()

        self.no_data_label = QLabel(t("cost_profit_no_data"))
        self.no_data_label.setObjectName("card")
        self.no_data_label.setWordWrap(True)
        self.no_data_label.setAlignment(Qt.AlignCenter)
        self.no_data_label.setMinimumHeight(100)
        self.no_data_label.setStyleSheet("padding: 20px; font-size: 14px;")
        self.no_data_label.hide()
        self._main_layout.addWidget(self.no_data_label)

        self.tabs = QTabWidget()
        self._build_analysis_tab()
        self._build_comparison_tab()
        self._build_trend_tab()
        self._build_reports_tab()
        self._build_recommendations_tab()
        self._main_layout.addWidget(self.tabs, 1)
        self._set_headers()

    def _build_centers_group(self):
        group = QGroupBox(t("cost_profit_group_centers"))
        layout = QVBoxLayout(group)

        self.center_table = QTableWidget()
        self.center_table.setColumnCount(6)
        self.center_table.setRowCount(self.MAX_CENTERS)
        self.center_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.center_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.center_table.verticalHeader().setDefaultSectionSize(44)
        self.center_table.setMinimumHeight(44 * self.MAX_CENTERS + 40)

        self._center_data = []
        for i in range(self.MAX_CENTERS):
            name_edit = QLineEdit()
            name_edit.setPlaceholderText(t("cost_profit_add_period").format(n=i + 1))
            self.center_table.setCellWidget(i, 0, name_edit)

            type_combo = QComboBox()
            type_combo.addItems([t(k) for k in _TYPE_LABEL_KEYS])
            self.center_table.setCellWidget(i, 1, type_combo)

            rev_spin = self._spin()
            self.center_table.setCellWidget(i, 2, rev_spin)

            direct_spin = self._spin()
            self.center_table.setCellWidget(i, 3, direct_spin)

            hc_spin = self._spin()
            hc_spin.setMaximum(10000)
            self.center_table.setCellWidget(i, 4, hc_spin)

            area_spin = self._spin()
            self.center_table.setCellWidget(i, 5, area_spin)

            self._center_data.append((name_edit, type_combo, rev_spin, direct_spin, hc_spin, area_spin))

        layout.addWidget(self.center_table)
        self._main_layout.addWidget(group)

    def _spin(self):
        spin = QDoubleSpinBox()
        spin.setRange(0, 1_000_000_000)
        spin.setDecimals(0)
        spin.setGroupSeparatorShown(True)
        return spin

    def _build_allocate_group(self):
        group = QGroupBox(t("cost_profit_group_allocate"))
        row = QHBoxLayout(group)
        row.setSpacing(10)

        self.indirect_label = QLabel(t("cost_profit_indirect_total"))
        row.addWidget(self.indirect_label)
        self.indirect_spin = self._spin()
        self.indirect_spin.setMaximumWidth(180)
        row.addWidget(self.indirect_spin)

        self.method_label = QLabel(t("cost_profit_method"))
        row.addWidget(self.method_label)
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            t("cost_profit_method_revenue"),
            t("cost_profit_method_headcount"),
            t("cost_profit_method_area"),
            t("cost_profit_method_equal"),
        ])
        row.addWidget(self.method_combo)

        self.target_label = QLabel(t("cost_profit_target_margin"))
        row.addWidget(self.target_label)
        self.target_spin = QDoubleSpinBox()
        self.target_spin.setRange(0, 100)
        self.target_spin.setDecimals(1)
        self.target_spin.setValue(10.0)
        self.target_spin.setMaximumWidth(90)
        row.addWidget(self.target_spin)

        row.addStretch()
        self.run_btn = QPushButton(t("cost_profit_run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.run_analysis)
        row.addWidget(self.run_btn)

        self._main_layout.addWidget(group)

    # ===== تبويب التحليل =====

    def _build_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        cards_row = QHBoxLayout()
        self.card_revenue = self._stat_card("--")
        self.card_costs = self._stat_card("--")
        self.card_profit = self._stat_card("--")
        self.card_margin = self._stat_card("--")
        self.card_best = self._stat_card("--")
        self.card_worst = self._stat_card("--")
        for card in (self.card_revenue, self.card_costs, self.card_profit,
                     self.card_margin, self.card_best, self.card_worst):
            cards_row.addWidget(card)
        layout.addLayout(cards_row)

        self.analysis_table = QTableWidget(0, 10)
        self.analysis_table.setObjectName("dataTable")
        self.analysis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.analysis_table)

        self.chart_profitability = ChartWidget("")
        self.chart_profitability.canvas.setMinimumHeight(280)
        layout.addWidget(self.chart_profitability)

        self.tabs.addTab(tab, t("cost_profit_tab_analysis"))

    def _stat_card(self, value):
        from PyQt5.QtWidgets import QFrame
        frame = QFrame()
        frame.setObjectName("card")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 12, 16, 12)
        lbl = QLabel("--")
        lbl.setObjectName("cardValue")
        lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(lbl)
        frame.value_label = lbl
        frame.title_label = QLabel("")
        frame.title_label.setStyleSheet("font-size: 11px; color: #888;")
        frame.title_label.setAlignment(Qt.AlignCenter)
        v.insertWidget(0, frame.title_label)
        frame.setProperty("_value", value)
        return frame

    # ===== تبويب المقارنات =====

    def _build_comparison_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        prev_group = QGroupBox(t("cost_profit_group_compare_prev"))
        prev_layout = QVBoxLayout(prev_group)
        self.prev_table = QTableWidget(0, 3)
        self.prev_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._prev_data = []
        prev_layout.addWidget(self.prev_table)
        top_row.addWidget(prev_group, 1)

        budget_group = QGroupBox(t("cost_profit_group_budget"))
        budget_layout = QVBoxLayout(budget_group)
        self.budget_table = QTableWidget(0, 3)
        self.budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._budget_data = []
        budget_layout.addWidget(self.budget_table)
        top_row.addWidget(budget_group, 1)

        layout.addLayout(top_row)

        self.compare_btn = QPushButton(t("cost_profit_compare_btn"))
        self.compare_btn.setObjectName("primaryBtn")
        self.compare_btn.setMinimumHeight(40)
        self.compare_btn.clicked.connect(self.run_comparison)
        layout.addWidget(self.compare_btn)

        self.comparison_table = QTableWidget(0, 8)
        self.comparison_table.setObjectName("dataTable")
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.comparison_table)

        self.standards_table = QTableWidget(0, 4)
        self.standards_table.setObjectName("dataTable")
        self.standards_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.standards_table)

        self.tabs.addTab(tab, t("cost_profit_tab_comparison"))

    # ===== تبويب الاتجاه =====

    def _build_trend_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        self.period_table = QTableWidget(self.MAX_PERIODS, 3)
        self.period_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._period_data = []
        for i in range(self.MAX_PERIODS):
            label_item = QTableWidgetItem(t("cost_profit_add_period").format(n=i + 1))
            self.period_table.setItem(i, 0, label_item)
            rev_spin = self._spin()
            self.period_table.setCellWidget(i, 1, rev_spin)
            cost_spin = self._spin()
            self.period_table.setCellWidget(i, 2, cost_spin)
            self._period_data.append((label_item, rev_spin, cost_spin))
        layout.addWidget(self.period_table)

        self.trend_btn = QPushButton(t("cost_profit_run"))
        self.trend_btn.setObjectName("primaryBtn")
        self.trend_btn.setMinimumHeight(40)
        self.trend_btn.clicked.connect(self.run_trend)
        layout.addWidget(self.trend_btn)

        info_row = QHBoxLayout()
        self.card_direction = self._stat_card("--")
        self.card_growth = self._stat_card("--")
        info_row.addWidget(self.card_direction)
        info_row.addWidget(self.card_growth)
        layout.addLayout(info_row)

        self.chart_trend = ChartWidget("")
        self.chart_trend.canvas.setMinimumHeight(280)
        layout.addWidget(self.chart_trend)

        self.tabs.addTab(tab, t("cost_profit_tab_trend"))

    # ===== تبويب التقارير =====

    def _build_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        self.ranking_title = QLabel(t("cost_profit_ranking"))
        self.ranking_title.setObjectName("sectionTitle")
        layout.addWidget(self.ranking_title)
        self.ranking_table = QTableWidget(0, 7)
        self.ranking_table.setObjectName("dataTable")
        self.ranking_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.ranking_table)

        self.variance_title = QLabel(t("cost_profit_variance_report"))
        self.variance_title.setObjectName("sectionTitle")
        layout.addWidget(self.variance_title)
        self.variance_table = QTableWidget(0, 6)
        self.variance_table.setObjectName("dataTable")
        self.variance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.variance_table)

        layout.addStretch()
        self.tabs.addTab(tab, t("cost_profit_tab_reports"))

    # ===== تبويب التوصيات =====

    def _build_recommendations_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        self.rec_table = QTableWidget(0, 3)
        self.rec_table.setObjectName("dataTable")
        self.rec_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.rec_table)
        layout.addStretch()
        self.tabs.addTab(tab, t("cost_profit_tab_recommendations"))

    def _set_headers(self):
        self.center_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_type"), t("cost_profit_revenue"),
            t("cost_profit_direct_costs"), t("cost_profit_headcount"), t("cost_profit_area"),
        ])
        self.analysis_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_type"), t("cost_profit_revenue"),
            t("cost_profit_direct_costs"), t("cost_profit_allocated"),
            t("cost_profit_total_cost"), t("cost_profit_profit"),
            t("cost_profit_margin"), t("cost_profit_revenue_share"),
            t("cost_profit_profit_share"),
        ])
        self.prev_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_prev_revenue"), t("cost_profit_prev_costs"),
        ])
        self.budget_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_budget_revenue"), t("cost_profit_budget_costs"),
        ])
        self.comparison_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_prev_revenue"), t("cost_profit_rev_delta"),
            t("cost_profit_prev_costs"), t("cost_profit_prev_profit"),
            t("cost_profit_profit_delta"), t("cost_profit_change"), t("cost_profit_variance"),
        ])
        self.standards_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_standard_margin"),
            t("cost_profit_margin"), t("cost_profit_status"),
        ])
        self.period_table.setHorizontalHeaderLabels([
            t("cost_profit_period"), t("cost_profit_trend_revenue"), t("cost_profit_trend_costs"),
        ])
        self.ranking_table.setHorizontalHeaderLabels([
            t("cost_profit_ranking"), t("cost_profit_name"), t("cost_profit_revenue"),
            t("cost_profit_total_cost"), t("cost_profit_profit"),
            t("cost_profit_margin"), t("cost_profit_revenue_share"),
        ])
        self.variance_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_budget_revenue"), t("cost_profit_revenue"),
            t("cost_profit_variance"), t("cost_profit_budget_costs"),
            t("cost_profit_profit_delta"),
        ])
        self.rec_table.setHorizontalHeaderLabels([
            t("cost_profit_rec_center"), t("cost_profit_rec_type"), t("cost_profit_rec_message"),
        ])

    # ===== الجمع والتحليل =====

    def _method(self):
        return ["revenue", "headcount", "area", "equal"][self.method_combo.currentIndex()]

    def _collect_centers(self):
        centers = []
        for name_edit, type_combo, rev_spin, direct_spin, hc_spin, area_spin in self._center_data:
            name = name_edit.text().strip()
            if name and (rev_spin.value() > 0 or direct_spin.value() > 0):
                centers.append({
                    "name": name,
                    "type": _CENTER_TYPES[type_combo.currentIndex()],
                    "revenue": rev_spin.value(),
                    "direct_costs": direct_spin.value(),
                    "headcount": hc_spin.value(),
                    "area": area_spin.value(),
                })
        return centers

    def _collect_prev(self):
        return [{"name": cw[0].text().strip(), "revenue": cw[1].value(), "costs": cw[2].value()}
                for cw in self._prev_data if cw[0].text().strip()]

    def _collect_budget(self):
        return [{"name": cw[0].text().strip(), "revenue": cw[1].value(), "costs": cw[2].value()}
                for cw in self._budget_data if cw[0].text().strip()]

    def _collect_periods(self):
        periods = []
        for label_item, rev_spin, cost_spin in self._period_data:
            if rev_spin.value() > 0 or cost_spin.value() > 0:
                periods.append([{"name": label_item.text(), "revenue": rev_spin.value(),
                                 "costs": cost_spin.value()}])
        return periods

    def refresh(self):
        """إعادة التحليل عند تغيّر البيانات/اللغة"""
        if self._result is None:
            self.no_data_label.show()
            self.tabs.hide()
        else:
            self.no_data_label.hide()
            self.tabs.show()

    def run_analysis(self):
        centers = self._collect_centers()
        if not centers:
            QMessageBox.warning(self, t("warning"), t("cost_profit_no_data"))
            return

        self._engine.set_standards(self.target_spin.value())
        self._result = self._engine.analyze(
            centers,
            indirect_total=self.indirect_spin.value(),
            method=self._method(),
            target_margin_pct=self.target_spin.value(),
        )
        self._fill_analysis()
        self._autofill_comparison_tables()
        self._fill_recommendations()
        self.no_data_label.hide()
        self.tabs.show()

    def _fill_analysis(self):
        summary = self._result["summary"]
        self._set_card(self.card_revenue, t("cost_profit_total_revenue"),
                       f"{summary['total_revenue']:,.0f}")
        self._set_card(self.card_costs, t("cost_profit_total_costs"),
                       f"{summary['total_costs']:,.0f}")
        self._set_card(self.card_profit, t("cost_profit_total_profit"),
                       f"{summary['total_profit']:,.0f}")
        self._set_card(self.card_margin, t("cost_profit_overall_margin"),
                       f"{summary['overall_margin_pct']:.1f}%")
        self._set_card(self.card_best, t("cost_profit_best_center"),
                       summary["best_center"] or "--")
        self._set_card(self.card_worst, t("cost_profit_worst_center"),
                       summary["worst_center"] or "--")

        centers = self._result["centers"]
        self.analysis_table.setRowCount(len(centers))
        for row, c in enumerate(centers):
            self.analysis_table.setItem(row, 0, QTableWidgetItem(c["name"]))
            self.analysis_table.setItem(row, 1, QTableWidgetItem(
                t(_TYPE_LABEL_KEYS[_CENTER_TYPES.index(c["type"])])))
            self._money(self.analysis_table, row, 2, c["revenue"])
            self._money(self.analysis_table, row, 3, c["direct_costs"])
            self._money(self.analysis_table, row, 4, c["indirect_costs"])
            self._money(self.analysis_table, row, 5, c["total_costs"])
            profit_item = self._money(self.analysis_table, row, 6, c["profit"])
            profit_item.setForeground(QColor(
                ThemeColors.get("error") if c["profit"] < 0 else ThemeColors.get("success")))
            self.analysis_table.setItem(row, 7, QTableWidgetItem(f"{c['margin_pct']:.1f}%"))
            self.analysis_table.setItem(row, 8, QTableWidgetItem(f"{c['revenue_share_pct']:.1f}%"))
            self.analysis_table.setItem(row, 9, QTableWidgetItem(f"{c['profit_share_pct']:.1f}%"))

        self._draw_profitability_chart(centers)

    def _set_card(self, card, title, value):
        card.title_label.setText(title)
        card.value_label.setText(value)

    def _money(self, table, row, col, value):
        item = QTableWidgetItem(f"{value:,.0f}")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(row, col, item)
        return item

    def _draw_profitability_chart(self, centers):
        fig = self.chart_profitability.figure
        fig.clear()
        text_color = _chart_text_color()
        bg = ThemeColors.get("chart_bg")
        fig.patch.set_facecolor(bg)

        ax1 = fig.add_subplot(1, 2, 1)
        ax1.set_facecolor(bg)
        ax1.tick_params(colors=text_color)
        for spine in ax1.spines.values():
            spine.set_color(text_color)
        labels = [c["name"][:12] for c in centers]
        x = range(len(labels))
        width = 0.28
        ax1.bar([i - width for i in x], [c["revenue"] for c in centers], width,
                label=t("cost_profit_revenue"), color="#27AE60", alpha=0.85)
        ax1.bar([i for i in x], [c["total_costs"] for c in centers], width,
                label=t("cost_profit_total_costs"), color="#E74C3C", alpha=0.85)
        ax1.bar([i + width for i in x], [c["profit"] for c in centers], width,
                label=t("cost_profit_profit"), color="#2196F3", alpha=0.85)
        ax1.set_xticks(list(x))
        ax1.set_xticklabels([_plain(l) for l in labels], rotation=45, ha='right', fontsize=8,
                            color=text_color)
        ax1.legend(fontsize=7, labelcolor=text_color)
        ax1.grid(True, alpha=0.3, axis='y')

        ax2 = fig.add_subplot(1, 2, 2)
        ax2.set_facecolor(bg)
        ax2.tick_params(colors=text_color)
        for spine in ax2.spines.values():
            spine.set_color(text_color)
        margins = [c["margin_pct"] for c in centers]
        colors = ["#27AE60" if m >= 0 else "#E74C3C" for m in margins]
        ax2.bar(list(x), margins, color=colors, alpha=0.85)
        ax2.axhline(0, color=text_color, linewidth=0.8)
        ax2.set_xticks(list(x))
        ax2.set_xticklabels([_plain(l) for l in labels], rotation=45, ha='right', fontsize=8,
                            color=text_color)
        ax2.set_ylabel(t("cost_profit_margin"), color=text_color)
        ax2.grid(True, alpha=0.3, axis='y')

        fig.tight_layout()
        self.chart_profitability.canvas.draw()
        self.chart_profitability.set_title(t("cost_profit_tab_analysis"))

    def _autofill_comparison_tables(self):
        names = [c["name"] for c in self._result["centers"]]
        self.prev_table.setRowCount(len(names))
        self.budget_table.setRowCount(len(names))
        self._prev_data = []
        self._budget_data = []
        for i, name in enumerate(names):
            prev_name = QLineEdit(name)
            prev_rev = self._spin()
            prev_cost = self._spin()
            self.prev_table.setCellWidget(i, 0, prev_name)
            self.prev_table.setCellWidget(i, 1, prev_rev)
            self.prev_table.setCellWidget(i, 2, prev_cost)
            self._prev_data.append((prev_name, prev_rev, prev_cost))

            bud_name = QLineEdit(name)
            bud_rev = self._spin()
            bud_cost = self._spin()
            self.budget_table.setCellWidget(i, 0, bud_name)
            self.budget_table.setCellWidget(i, 1, bud_rev)
            self.budget_table.setCellWidget(i, 2, bud_cost)
            self._budget_data.append((bud_name, bud_rev, bud_cost))

    # ===== المقارنات =====

    def run_comparison(self):
        if self._result is None:
            QMessageBox.warning(self, t("warning"), t("cost_profit_no_data"))
            return
        prev = self._collect_prev()
        budget = self._collect_budget()
        self._comparison = {
            "previous": self._engine.compare_previous(prev) if prev else [],
            "budget": self._engine.compare_budget(budget) if budget else [],
            "standards": self._engine.compare_standards(),
        }
        self._fill_comparison()
        self._fill_reports()

    def _fill_comparison(self):
        prev_rows = self._comparison["previous"]
        budget_rows = self._comparison["budget"]
        self.comparison_table.setRowCount(len(prev_rows))
        for row, r in enumerate(prev_rows):
            self.comparison_table.setItem(row, 0, QTableWidgetItem(r["name"]))
            self._money(self.comparison_table, row, 1, r["prev_revenue"])
            self._money(self.comparison_table, row, 2, r["revenue_delta"])
            self._money(self.comparison_table, row, 3, r["profit"])
            self._money(self.comparison_table, row, 4, r["prev_profit"])
            self._money(self.comparison_table, row, 5, r["profit_delta"])
            self.comparison_table.setItem(row, 6, QTableWidgetItem(t(_CHANGE_KEYS[r["change"]])))
            self._money(self.comparison_table, row, 7, r["revenue"])

        self.standards_table.setRowCount(len(self._comparison["standards"]))
        for row, s in enumerate(self._comparison["standards"]):
            self.standards_table.setItem(row, 0, QTableWidgetItem(s["name"]))
            self.standards_table.setItem(row, 1, QTableWidgetItem(f"{s['target_margin_pct']:.1f}%"))
            self.standards_table.setItem(row, 2, QTableWidgetItem(f"{s['margin_pct']:.1f}%"))
            self.standards_table.setItem(row, 3, QTableWidgetItem(t(_STATUS_KEYS[s["status"]])))

    def _fill_reports(self):
        reports = self._engine.get_reports()
        ranked = reports["ranking"]
        self.ranking_table.setRowCount(len(ranked))
        for row, c in enumerate(ranked):
            self.ranking_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.ranking_table.setItem(row, 1, QTableWidgetItem(c["name"]))
            self._money(self.ranking_table, row, 2, c["revenue"])
            self._money(self.ranking_table, row, 3, c["total_costs"])
            self._money(self.ranking_table, row, 4, c["profit"])
            self.ranking_table.setItem(row, 5, QTableWidgetItem(f"{c['margin_pct']:.1f}%"))
            self.ranking_table.setItem(row, 6, QTableWidgetItem(f"{c['revenue_share_pct']:.1f}%"))

        budget_rows = self._comparison["budget"] if self._comparison else []
        self.variance_table.setRowCount(len(budget_rows))
        for row, r in enumerate(budget_rows):
            self.variance_table.setItem(row, 0, QTableWidgetItem(r["name"]))
            self._money(self.variance_table, row, 1, r["budget_revenue"])
            self._money(self.variance_table, row, 2, r["revenue"])
            self._money(self.variance_table, row, 3, r["revenue_variance"])
            self._money(self.variance_table, row, 4, r["profit"])
            self._money(self.variance_table, row, 5, r["profit_variance"])

    def _fill_recommendations(self):
        if self._result is None:
            return
        recs = self._engine.get_recommendations()
        self.rec_table.setRowCount(len(recs))
        for row, r in enumerate(recs):
            self.rec_table.setItem(row, 0, QTableWidgetItem(r["center"]))
            self.rec_table.setItem(row, 1, QTableWidgetItem(t(_REC_TYPE_KEYS.get(r["type"], r["type"]))))
            self.rec_table.setItem(row, 2, QTableWidgetItem(r["message"]))

    # ===== الاتجاه =====

    def run_trend(self):
        periods = self._collect_periods()
        if len(periods) < 2:
            QMessageBox.warning(self, t("warning"), t("cost_profit_no_data"))
            return
        self._trend = self._engine.trend_analysis(periods)
        self._fill_trend()

    def _fill_trend(self):
        trend = self._trend
        self._set_card(self.card_direction, t("cost_profit_direction"),
                       t(_DIRECTION_KEYS[trend["direction"]]))
        self._set_card(self.card_growth, t("cost_profit_growth_rate"),
                       f"{trend['growth_rate_pct']:+.1f}%")
        self._draw_trend_chart(trend["periods"])

    def _draw_trend_chart(self, periods):
        fig = self.chart_trend.figure
        fig.clear()
        text_color = _chart_text_color()
        bg = ThemeColors.get("chart_bg")
        fig.patch.set_facecolor(bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg)
        ax.tick_params(colors=text_color)
        for spine in ax.spines.values():
            spine.set_color(text_color)
        x = [p["period"] for p in periods]
        ax.plot(x, [p["revenue"] for p in periods], marker="o", color="#2196F3",
                label=t("cost_profit_trend_revenue"))
        ax.plot(x, [p["costs"] for p in periods], marker="s", color="#E74C3C",
                label=t("cost_profit_trend_costs"))
        ax.plot(x, [p["profit"] for p in periods], marker="^", color="#27AE60",
                label=t("cost_profit_trend_profit"))
        ax.set_xticks(x)
        ax.set_ylabel(t("cost_profit_total_costs"), color=text_color)
        ax.legend(fontsize=8, labelcolor=text_color)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        self.chart_trend.canvas.draw()
        self.chart_trend.set_title(t("cost_profit_tab_trend"))

    # ===== تصدير =====

    def _export_pdf(self):
        if self._result is None:
            QMessageBox.warning(self, t("warning"), t("cost_profit_no_data"))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t("cost_profit_export_pdf"), "cost_center_profitability.pdf",
            "PDF Files (*.pdf)")
        if not file_path:
            return
        try:
            with PdfPages(file_path) as pdf:
                for chart in (self.chart_profitability, self.chart_trend):
                    if chart.figure.axes:
                        chart.figure.canvas.draw()
                        pdf.savefig(chart.figure, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, t("success"),
                                    f"✅ {t('cost_profit_export_success')}\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _export_excel(self):
        if self._result is None:
            QMessageBox.warning(self, t("warning"), t("cost_profit_no_data"))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t("cost_profit_export_excel"), "cost_center_profitability.xlsx",
            "Excel Files (*.xlsx)")
        if not file_path:
            return
        try:
            self._write_excel(file_path)
            QMessageBox.information(self, t("success"),
                                    f"✅ {t('cost_profit_export_success')}\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _write_excel(self, file_path):
        from ui.exporters import add_excel_sheet, new_workbook

        wb = new_workbook()

        add_excel_sheet(
            wb, "Profitability",
            ["Center", "Type", "Revenue", "Direct", "Allocated",
             "Total Cost", "Profit", "Margin %", "Rev Share %", "Profit Share %"],
            [[c["name"], c["type"], c["revenue"], c["direct_costs"],
              c["indirect_costs"], c["total_costs"], c["profit"],
              c["margin_pct"], c["revenue_share_pct"], c["profit_share_pct"]]
             for c in self._result["centers"]],
        )

        reports = self._engine.get_reports()
        add_excel_sheet(
            wb, "Ranking",
            ["Rank", "Center", "Revenue", "Total Cost", "Profit", "Margin %"],
            [[idx, c["name"], c["revenue"], c["total_costs"], c["profit"],
              c["margin_pct"]]
             for idx, c in enumerate(reports["ranking"], start=1)],
        )

        add_excel_sheet(
            wb, "Comparisons",
            ["Center", "Prev Revenue", "Revenue Delta", "Prev Profit",
             "Profit Delta", "Change", "Variance"],
            [[r["name"], r["prev_revenue"], r["revenue_delta"],
              r["prev_profit"], r["profit_delta"], r["change"],
              r["revenue_delta"]]
             for r in (self._comparison["previous"] if self._comparison else [])],
        )

        add_excel_sheet(
            wb, "Standards",
            ["Center", "Target %", "Margin %", "Status"],
            [[s["name"], s["target_margin_pct"], s["margin_pct"], s["status"]]
             for s in (self._comparison["standards"] if self._comparison else [])],
        )

        add_excel_sheet(
            wb, "Recommendations",
            ["Center", "Type", "Message"],
            [[r["center"], r["type"], r["message"]]
             for r in self._engine.get_recommendations()],
        )

        wb.save(file_path)

    # ===== اللغة =====

    def retranslate(self):
        self.title_label.setText(t("cost_profit_title"))

        type_idx = [self.center_table.cellWidget(i, 1).currentIndex() for i in range(self.MAX_CENTERS)]
        self.center_table.setHorizontalHeaderLabels([
            t("cost_profit_name"), t("cost_profit_type"), t("cost_profit_revenue"),
            t("cost_profit_direct_costs"), t("cost_profit_headcount"), t("cost_profit_area"),
        ])
        for i in range(self.MAX_CENTERS):
            combo = self.center_table.cellWidget(i, 1)
            combo.blockSignals(True)
            combo.clear()
            combo.addItems([t(k) for k in _TYPE_LABEL_KEYS])
            combo.setCurrentIndex(type_idx[i])
            combo.blockSignals(False)

        self.indirect_label.setText(t("cost_profit_indirect_total"))
        self.method_label.setText(t("cost_profit_method"))
        self.target_label.setText(t("cost_profit_target_margin"))
        method_idx = self.method_combo.currentIndex()
        self.method_combo.blockSignals(True)
        self.method_combo.clear()
        self.method_combo.addItems([
            t("cost_profit_method_revenue"),
            t("cost_profit_method_headcount"),
            t("cost_profit_method_area"),
            t("cost_profit_method_equal"),
        ])
        self.method_combo.setCurrentIndex(method_idx)
        self.method_combo.blockSignals(False)
        self.run_btn.setText(t("cost_profit_run"))
        self.compare_btn.setText(t("cost_profit_compare_btn"))
        self.trend_btn.setText(t("cost_profit_run"))
        self.export_pdf_btn.setText(t("cost_profit_export_pdf"))
        self.export_excel_btn.setText(t("cost_profit_export_excel"))
        self.no_data_label.setText(t("cost_profit_no_data"))

        self._set_headers()
        self.tabs.setTabText(0, t("cost_profit_tab_analysis"))
        self.tabs.setTabText(1, t("cost_profit_tab_comparison"))
        self.tabs.setTabText(2, t("cost_profit_tab_trend"))
        self.tabs.setTabText(3, t("cost_profit_tab_reports"))
        self.tabs.setTabText(4, t("cost_profit_tab_recommendations"))

        if self._result:
            self._fill_analysis()
            if self._comparison:
                self._fill_comparison()
            if self._trend:
                self._fill_trend()
