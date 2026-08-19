# تحليل نقطة التعادل
# ====================

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox, QFormLayout, QMessageBox,
    QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (QFont)

import pyqtgraph as pg
from ui.charts import (PgChartWidget, draw_line,
    _text_color, _chart_bg, _hex_to_rgb, _mk_brush, _mk_pen, _mk_text_item)

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.breakeven import BreakEvenAnalyzer


class BreakEvenView(QWidget):
    """واجهة تحليل نقطة التعادل"""

    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(t("breakeven_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("breakeven_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        input_group = QGroupBox(t("breakeven_result_title"))
        input_layout = QFormLayout()

        self.fixed_costs = QDoubleSpinBox()
        self.fixed_costs.setRange(0, 1_000_000_000)
        self.fixed_costs.setDecimals(0)
        self.fixed_costs.setGroupSeparatorShown(True)
        input_layout.addRow(t("breakeven_fixed_costs"), self.fixed_costs)

        self.vc_ratio = QDoubleSpinBox()
        self.vc_ratio.setRange(0, 100)
        self.vc_ratio.setValue(60)
        self.vc_ratio.setSuffix(" %")
        input_layout.addRow(t("breakeven_vc_ratio"), self.vc_ratio)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        self.run_btn = QPushButton(t("breakeven_run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.run_analysis)
        main_layout.addWidget(self.run_btn)

        results_group = QGroupBox(t("breakeven_result_title"))
        results_layout = QGridLayout()

        self.labels = {}
        self._result_titles = {}
        fields = [
            ("breakeven_point", "breakeven_point"),
            ("breakeven_safety_margin", "breakeven_safety_margin"),
            ("breakeven_safety_pct", "breakeven_safety_pct"),
            ("breakeven_cm_ratio", "breakeven_cm_ratio"),
            ("breakeven_leverage", "breakeven_leverage"),
            ("breakeven_status", "breakeven_status"),
        ]
        for i, (key, label_key) in enumerate(fields):
            lbl = QLabel(t(label_key))
            lbl.setObjectName("cardTitle")
            self._result_titles[key] = lbl
            val = QLabel("--")
            val.setObjectName("cardValue")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            val.setFont(font)
            results_layout.addWidget(lbl, i, 0)
            results_layout.addWidget(val, i, 1)
            self.labels[key] = val

        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        self.chart = PgChartWidget(t("breakeven_chart_title"))
        self.chart.setMinimumHeight(300)
        main_layout.addWidget(self.chart)

        self.setLayout(main_layout)

    def run_analysis(self):
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("forecast_no_data"))
            return

        self.analyzer = BreakEvenAnalyzer(state.financial_data)
        result = self.analyzer.calculate(
            fixed_costs=self.fixed_costs.value(),
            variable_cost_ratio=self.vc_ratio.value() / 100
        )

        if "error" in result:
            QMessageBox.warning(self, t("error"), result["error"])
            return

        self.labels["breakeven_point"].setText(f"{result['breakeven_revenue']:,.0f} DZD")
        self.labels["breakeven_safety_margin"].setText(f"{result['margin_of_safety']:,.0f} DZD")
        self.labels["breakeven_safety_pct"].setText(f"{result['margin_of_safety_pct']:.1f}%")
        self.labels["breakeven_cm_ratio"].setText(f"{result['contribution_margin_ratio']:.1f}%")
        self.labels["breakeven_leverage"].setText(f"{result['operating_leverage']:.2f}")
        status_text = t("breakeven_profitable") if result["is_profitable"] else t("breakeven_not_profitable")
        self.labels["breakeven_status"].setText(status_text)

        color = ThemeColors.get('success') if result["is_profitable"] else ThemeColors.get('error')
        self.labels["breakeven_status"].setStyleSheet(f"color: {color}; font-weight: bold;")

        self._draw_chart(result)

    def _draw_chart(self, result):
        self.chart.clear_plot()
        pi = self.chart.plot_item

        rev = result["current_revenue"]
        be = result["breakeven_revenue"]
        fc = result["fixed_costs"]
        cm_ratio = result["contribution_margin_ratio"] / 100

        max_rev = max(rev, be) * 1.5

        x = [0, max_rev]
        total_cost = [fc, fc + max_rev * (1 - cm_ratio)]
        total_rev_line = [0, max_rev]

        draw_line(pi, x, [total_rev_line, total_cost],
                  labels=['Revenue', 'Total Cost'],
                  colors=[ThemeColors.get('info'), ThemeColors.get('error')])

        from pyqtgraph import InfiniteLine
        be_line = InfiniteLine(pos=(be, 0), angle=90,
                               pen=_mk_pen(ThemeColors.get('warning'), 2))
        pi.addItem(be_line)
        be_lbl = _mk_text_item(f"BE: {be:,.0f}", be, max(total_rev_line[-1], total_cost[-1]) * 0.95,
                                color=ThemeColors.get('warning'), size=8)
        pi.addItem(be_lbl)

        if rev > be:
            fill_x = [be, rev]
            fill_y1 = [fc + be * (1 - cm_ratio), fc + rev * (1 - cm_ratio)]
            fill_y2 = [be, rev]
            item_lower = pi.plot(fill_x, fill_y1, pen=None)
            r, g, b = _hex_to_rgb(ThemeColors.get('success'))
            item_lower.setBrush(pg.mkBrush(r, g, b, 40))
            item_lower.setFillLevel(0)
            item_upper = pi.plot(fill_x, fill_y2, pen=None)
            item_upper.setBrush(pg.mkBrush(r, g, b, 40))
            item_upper.setFillLevel(0)
        elif rev < be:
            fill_x = [rev, be]
            fill_y1 = [rev * (1 - cm_ratio) + fc, fc + be * (1 - cm_ratio)]
            fill_y2 = [rev, be]
            item_lower = pi.plot(fill_x, fill_y1, pen=None)
            r, g, b = _hex_to_rgb(ThemeColors.get('error'))
            item_lower.setBrush(pg.mkBrush(r, g, b, 40))
            item_lower.setFillLevel(0)
            item_upper = pi.plot(fill_x, fill_y2, pen=None)
            item_upper.setBrush(pg.mkBrush(r, g, b, 40))
            item_upper.setFillLevel(0)

        title = t("breakeven_chart_title") if t("breakeven_chart_title") != "breakeven_chart_title" else "Break-Even Chart"
        self.chart.title_label.setText(title)

    def retranslate(self):
        self.title.setText(t("breakeven_title"))
        self.subtitle.setText(t("breakeven_subtitle"))
        self.run_btn.setText(t("breakeven_run"))
        for key in self._result_titles:
            self._result_titles[key].setText(t(key))

    def refresh(self):
        pass
