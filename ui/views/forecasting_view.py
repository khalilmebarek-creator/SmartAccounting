# التنبؤ المالي
# =============

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFormLayout, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.forecasting import FinancialForecaster


class ForecastingView(QWidget):
    """واجهة التنبؤ المالي"""

    def __init__(self):
        super().__init__()
        self.forecaster = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(t("forecast_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("forecast_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        input_group = QGroupBox(t("forecast_growth_rates"))
        input_layout = QFormLayout()

        self.optimistic = QDoubleSpinBox()
        self.optimistic.setRange(-50, 100)
        self.optimistic.setValue(15)
        self.optimistic.setSuffix(" %")
        input_layout.addRow(t("forecast_optimistic"), self.optimistic)

        self.base_rate = QDoubleSpinBox()
        self.base_rate.setRange(-50, 100)
        self.base_rate.setValue(8)
        self.base_rate.setSuffix(" %")
        input_layout.addRow(t("forecast_base"), self.base_rate)

        self.pessimistic = QDoubleSpinBox()
        self.pessimistic.setRange(-50, 100)
        self.pessimistic.setValue(3)
        self.pessimistic.setSuffix(" %")
        input_layout.addRow(t("forecast_pessimistic"), self.pessimistic)

        self.years_spin = QDoubleSpinBox()
        self.years_spin.setRange(1, 10)
        self.years_spin.setValue(5)
        self.years_spin.setDecimals(0)
        input_layout.addRow(t("forecast_years"), self.years_spin)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        self.run_btn = QPushButton(t("forecast_run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setMinimumHeight(42)
        self.run_btn.clicked.connect(self.run_forecast)
        main_layout.addWidget(self.run_btn)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            t("forecast_year"), t("forecast_optimistic"),
            t("forecast_base"), t("forecast_pessimistic")
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.results_table)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor(ThemeColors.get("chart_bg"))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

    def run_forecast(self):
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("forecast_no_data"))
            return

        self.forecaster = FinancialForecaster(state.financial_data, state.ratios)
        rates = [
            self.pessimistic.value() / 100,
            self.base_rate.value() / 100,
            self.optimistic.value() / 100,
        ]
        years = int(self.years_spin.value())

        proj_opt = self.forecaster.project_revenue([rates[2]] * years)
        proj_base = self.forecaster.project_revenue([rates[1]] * years)
        proj_pess = self.forecaster.project_revenue([rates[0]] * years)

        self._fill_table(proj_opt, proj_base, proj_pess, years)
        self._draw_chart(proj_opt, proj_base, proj_pess, years)

    def _fill_table(self, proj_opt, proj_base, proj_pess, years):
        self.results_table.setRowCount(years)
        for i in range(years):
            year_item = QTableWidgetItem(f"+{i + 1}")
            year_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(i, 0, year_item)
            for col, proj in [(1, proj_opt), (2, proj_base), (3, proj_pess)]:
                if "error" not in proj and i < len(proj["projections"]):
                    val = proj["projections"][i]["projected_revenue"]
                    item = QTableWidgetItem(f"{val:,.0f}")
                else:
                    item = QTableWidgetItem("--")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.results_table.setItem(i, col, item)

    def _draw_chart(self, proj_opt, proj_base, proj_pess, years):
        import matplotlib.pyplot as plt
        plt.close(self.figure)
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        base_rev = state.financial_data.get("revenue", 0)
        x = [0] + list(range(1, years + 1))

        for proj, color, label in [
            (proj_opt, ThemeColors.get('success'), t("forecast_optimistic")),
            (proj_base, ThemeColors.get('info'), t("forecast_base")),
            (proj_pess, ThemeColors.get('error'), t("forecast_pessimistic")),
        ]:
            if "error" not in proj:
                y = [base_rev] + [p["projected_revenue"] for p in proj["projections"]]
                ax.plot(x, y, 'o-', color=color, linewidth=2, label=label, markersize=6)

        ax.set_title(t("forecast_chart_title"), fontsize=11, fontweight='bold')
        ax.set_xlabel(t("forecast_years_ahead"))
        ax.set_ylabel(t("forecast_revenue"))
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.figure.tight_layout()
        self.canvas.draw()

    def retranslate(self):
        self.title.setText(t("forecast_title"))
        self.subtitle.setText(t("forecast_subtitle"))
        self.run_btn.setText(t("forecast_run"))
        self.results_table.setHorizontalHeaderLabels([
            t("forecast_year"), t("forecast_optimistic"),
            t("forecast_base"), t("forecast_pessimistic")
        ])

    def refresh(self):
        pass
