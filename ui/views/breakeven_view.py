# تحليل نقطة التعادل
# ====================

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox, QFormLayout, QMessageBox,
    QGridLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QFont)

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        self.run_btn.setMinimumHeight(42)
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
            val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            val.setFont(font)
            results_layout.addWidget(lbl, i, 0)
            results_layout.addWidget(val, i, 1)
            self.labels[key] = val

        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor(ThemeColors.get("chart_bg"))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)
        main_layout.addWidget(self.canvas)

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
        import matplotlib.pyplot as plt
        plt.close(self.figure)
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        rev = result["current_revenue"]
        be = result["breakeven_revenue"]
        fc = result["fixed_costs"]
        cm_ratio = result["contribution_margin_ratio"] / 100

        max_rev = max(rev, be) * 1.5

        x = [0, max_rev]
        total_cost = [fc, fc + max_rev * (1 - cm_ratio)]
        total_rev_line = [0, max_rev]

        ax.plot(x, total_rev_line, 'o-', color=ThemeColors.get('info'), linewidth=2, label='Revenue')
        ax.plot(x, total_cost, 'o-', color=ThemeColors.get('error'), linewidth=2, label='Total Cost')
        ax.axvline(x=be, color=ThemeColors.get('warning'), linestyle='--', linewidth=1.5, label=f'Break-Even: {be:,.0f}')

        if rev > be:
            ax.fill_between([be, rev], [fc + be * (1 - cm_ratio), fc + rev * (1 - cm_ratio)],
                            [be, rev], alpha=0.15, color=ThemeColors.get('success'))
        elif rev < be:
            ax.fill_between([rev, be], [rev, fc + be * (1 - cm_ratio)],
                            [rev * (1 - cm_ratio) + fc, fc + be * (1 - cm_ratio)], alpha=0.15, color=ThemeColors.get('error'))

        ax.set_title(t("breakeven_chart_title") if t("breakeven_chart_title") != "breakeven_chart_title" else "Break-Even Chart",
                     fontsize=11, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.figure.tight_layout()
        self.canvas.draw()

    def retranslate(self):
        self.title.setText(t("breakeven_title"))
        self.subtitle.setText(t("breakeven_subtitle"))
        self.run_btn.setText(t("breakeven_run"))
        for key in self._result_titles:
            self._result_titles[key].setText(t(key))

    def refresh(self):
        pass
