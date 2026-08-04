from ui.app_state import state, ThemeColors
from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QFrame, QMessageBox, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import (Qt)
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.resources.i18n import t
from modules.calculations import CalculationEngine


class ZScoreView(QWidget):

    def __init__(self):
        super().__init__()
        self.engine = CalculationEngine()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title = QLabel(t("zs_title"))
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        subtitle = QLabel(t("zs_subtitle"))
        subtitle.setObjectName("headerSubtitle")
        layout.addWidget(subtitle)

        fields_group = QGroupBox(t("zs_components"))
        fields_layout = QGridLayout()
        fields_layout.setSpacing(12)
        fields_layout.setContentsMargins(20, 25, 20, 20)

        self.inputs = {}
        self._labels = {}
        fields = [
            ("working_capital", "zs_working_capital"),
            ("retained_earnings", "zs_retained_earnings"),
            ("ebit", "zs_ebit"),
            ("market_value_equity", "zs_market_value"),
            ("book_value_debt", "zs_book_debt"),
            ("sales", "zs_sales"),
            ("total_assets", "zs_total_assets"),
        ]

        for i, (key, label_key) in enumerate(fields):
            row, col = divmod(i, 2)
            lbl = QLabel(t(label_key))
            lbl.setMinimumWidth(200)
            self._labels[label_key] = lbl
            inp = QLineEdit()
            inp.setPlaceholderText("0")
            inp.setMinimumHeight(36)
            inp.setMinimumWidth(180)
            self.inputs[key] = inp
            fields_layout.addWidget(lbl, row, col * 2)
            fields_layout.addWidget(inp, row, col * 2 + 1)

        fields_group.setLayout(fields_layout)
        layout.addWidget(fields_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.calc_btn = QPushButton(t("zs_calculate"))
        self.calc_btn.setObjectName("primaryBtn")
        self.calc_btn.setMinimumWidth(200)
        self.calc_btn.setMinimumHeight(44)
        self.calc_btn.clicked.connect(self.calculate)
        btn_layout.addWidget(self.calc_btn)
        layout.addLayout(btn_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        layout.addWidget(sep)

        self.result_label = QLabel("")
        self.result_label.setObjectName("headerTitle")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setMinimumHeight(50)
        layout.addWidget(self.result_label)

        self.interp_label = QLabel("")
        self.interp_label.setObjectName("headerSubtitle")
        self.interp_label.setAlignment(Qt.AlignCenter)
        self.interp_label.setMinimumHeight(36)
        layout.addWidget(self.interp_label)

        self.chart_frame = QFrame()
        self.chart_layout = QVBoxLayout()
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_frame.setLayout(self.chart_layout)
        layout.addWidget(self.chart_frame, 1)

        self.setLayout(layout)

    def _get_val(self, key):
        try:
            return float(self.inputs[key].text().strip() or "0")
        except ValueError:
            return 0

    def calculate(self):
        try:
            d = {k: self._get_val(k) for k in self.inputs}
            if d["total_assets"] == 0:
                QMessageBox.warning(self, t("warning"), t("zs_no_data"))
                return

            result = self.engine.z_score(**d)
            self._show_result(result)
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("zscore_view").error(f"Z-Score calculation failed: {e}")
            QMessageBox.critical(self, t("error"), str(e))

    def _show_result(self, result):
        status = result["status"]
        z = result["z_score"]

        if status == "safe":
            color = "#2ecc71"
            status_text = t("zs_safe")
            interp = t("zs_interpretation_safe")
        elif status == "grey":
            color = "#f39c12"
            status_text = t("zs_grey")
            interp = t("zs_interpretation_grey")
        else:
            color = "#e74c3c"
            status_text = t("zs_danger")
            interp = t("zs_interpretation_danger")

        self.result_label.setText(f"{t('zs_result')}: {z}  —  {status_text}")
        self.result_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        self.interp_label.setText(interp)

        self._draw_chart(z, result["components"])

    def _draw_chart(self, z_score, components):
        for i in range(self.chart_layout.count()):
            w = self.chart_layout.itemAt(i).widget()
            if w:
                if hasattr(w, 'figure'):
                    import matplotlib.pyplot as plt
                    plt.close(w.figure)
                w.setParent(None)
                w.deleteLater()

        fig = Figure(figsize=(8, 4), dpi=100, facecolor='none')
        fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.15)
        ax = fig.add_subplot(111)

        ax.axhspan(0, 1.81, color='#e74c3c', alpha=0.15)
        ax.axhspan(1.81, 2.99, color='#f39c12', alpha=0.15)
        ax.axhspan(2.99, 5.0, color='#2ecc71', alpha=0.15)
        ax.axhline(y=1.81, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.7)
        ax.axhline(y=2.99, color='#2ecc71', linestyle='--', linewidth=1, alpha=0.7)

        components_names = ['X1', 'X2', 'X3', 'X4', 'X5']
        components_vals = [components.get(f'x{i+1}', 0) for i in range(5)]
        weights = [1.2, 1.4, 3.3, 0.6, 1.0]
        weighted = [v * w for v, w in zip(components_vals, weights)]

        bars = ax.bar(components_names, weighted, color='#3498db', alpha=0.8, width=0.5, edgecolor=ThemeColors.get('chart_edge'), linewidth=0.5)

        ax.plot([], [], 'o', color=ThemeColors.get('chart_edge'), label=f'Z = {z_score}')
        ax.legend(loc='upper right', fontsize=10, framealpha=0.8)

        ax.set_ylim(0, max(5.0, z_score + 0.5))
        ax.set_ylabel('Weighted Value', fontsize=10)
        ax.set_title('Altman Z-Score Breakdown', fontsize=12, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='both', labelsize=9)

        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(300)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chart_layout.addWidget(canvas)

    def load_from_state(self):
        fd = state.financial_data
        if not fd:
            return

        total_assets = fd.get("total_assets", 0)
        current_assets = fd.get("current_assets", 0)
        current_liabilities = fd.get("current_liabilities", 0)
        equity = fd.get("equity", 0)
        revenue = fd.get("revenue", 0)
        net_income = fd.get("net_income", 0)
        total_liabilities = fd.get("total_liabilities", 0)

        working_capital = current_assets - current_liabilities
        retained_earnings = net_income
        ebit = net_income
        book_debt = total_liabilities
        market_value = equity if equity > 0 else total_assets * 0.5

        self.inputs["working_capital"].setText(str(int(working_capital)))
        self.inputs["retained_earnings"].setText(str(int(retained_earnings)))
        self.inputs["ebit"].setText(str(int(ebit)))
        self.inputs["market_value_equity"].setText(str(int(market_value)))
        self.inputs["book_value_debt"].setText(str(int(book_debt)))
        self.inputs["sales"].setText(str(int(revenue)))
        self.inputs["total_assets"].setText(str(int(total_assets)))

    def retranslate(self):
        title = self.findChild(QLabel, "headerTitle")
        if title:
            title.setText(t("zs_title"))
        subtitle = self.findChild(QLabel, "headerSubtitle")
        if subtitle:
            subtitle.setText(t("zs_subtitle"))
        for key, lbl in self._labels.items():
            lbl.setText(t(key))
        self.calc_btn.setText(t("zs_calculate"))
