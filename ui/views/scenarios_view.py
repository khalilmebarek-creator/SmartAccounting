# عرض تحليل السيناريوهات المالية
# ================================

from ui.views._path import _  # noqa: F401 — ensures project root on sys.path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QSizePolicy, QScrollArea, QPushButton,
    QComboBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.scenarios import ScenarioAnalyzer


def _chart_text_color():
    return ThemeColors.get("chart_text")


def _chart_edge_color():
    return ThemeColors.get("chart_edge")


class ScenarioChart(QFrame):
    """كارت يحتوي على رسم بياني"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.figure.patch.set_facecolor(ThemeColors.get("chart_bg"))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def set_title(self, title):
        self.title_label.setText(title)

    def clear_chart(self):
        self.figure.clear()
        plt.close(self.figure)
        self.canvas.draw()


class ScenariosView(QWidget):
    """واجهة تحليل السيناريوهات المالية"""

    _METRIC_KEYS = [
        'revenue', 'cogs', 'operating_expenses', 'gross_profit',
        'net_income', 'net_profit_margin', 'asset_turnover', 'roa', 'roe',
    ]
    _METRIC_FMT = {
        'revenue': ('scn_revenue', '{:,.2f}'),
        'cogs': ('scn_cogs', '{:,.2f}'),
        'operating_expenses': ('scn_opex', '{:,.2f}'),
        'gross_profit': ('scn_gross_profit', '{:,.2f}'),
        'net_income': ('scn_net_income', '{:,.2f}'),
        'net_profit_margin': ('scn_npm', '{:.2f}%'),
        'asset_turnover': ('scn_at', '{:.4f}'),
        'roa': ('scn_roa', '{:.2f}%'),
        'roe': ('scn_roe', '{:.2f}%'),
    }

    def __init__(self):
        super().__init__()
        self.analyzer = None
        self._scenarios = None
        self._sensitivity = None
        self._tornado = None
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dashboardScroll")

        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # ===== العنوان =====
        self.title = QLabel(t("scn_title"))
        self.title.setObjectName("headerTitle")
        content_layout.addWidget(self.title)

        self.subtitle = QLabel(t("scn_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        content_layout.addWidget(self.subtitle)

        # ===== الافتراضات =====
        self.assumptions_title = QLabel(t("scn_assumptions"))
        self.assumptions_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.assumptions_title)

        assumptions_grid = QGridLayout()
        assumptions_grid.setSpacing(15)

        best_frame = QFrame()
        best_frame.setObjectName("card")
        best_layout = QVBoxLayout(best_frame)
        best_layout.setSpacing(10)
        self.best_title = QLabel(t("scn_best_title"))
        self.best_title.setObjectName("cardTitle")
        best_layout.addWidget(self.best_title)
        self.best_desc = QLabel(t("scn_best_desc"))
        self.best_desc.setObjectName("cardSubtitle")
        self.best_desc.setWordWrap(True)
        best_layout.addWidget(self.best_desc)
        best_layout.addSpacing(4)
        best_layout.addWidget(QLabel(t("scn_best_revenue")))
        self.best_revenue = QDoubleSpinBox()
        self.best_revenue.setRange(-100, 200)
        self.best_revenue.setValue(20)
        self.best_revenue.setSuffix(" %")
        best_layout.addWidget(self.best_revenue)
        best_layout.addWidget(QLabel(t("scn_best_cost")))
        self.best_cost = QDoubleSpinBox()
        self.best_cost.setRange(-100, 200)
        self.best_cost.setValue(-10)
        self.best_cost.setSuffix(" %")
        best_layout.addWidget(self.best_cost)
        best_layout.addWidget(QLabel(t("scn_best_efficiency")))
        self.best_efficiency = QDoubleSpinBox()
        self.best_efficiency.setRange(-100, 200)
        self.best_efficiency.setValue(15)
        self.best_efficiency.setSuffix(" %")
        best_layout.addWidget(self.best_efficiency)
        assumptions_grid.addWidget(best_frame, 0, 0)

        worst_frame = QFrame()
        worst_frame.setObjectName("card")
        worst_layout = QVBoxLayout(worst_frame)
        worst_layout.setSpacing(10)
        self.worst_title = QLabel(t("scn_worst_title"))
        self.worst_title.setObjectName("cardTitle")
        worst_layout.addWidget(self.worst_title)
        self.worst_desc = QLabel(t("scn_worst_desc"))
        self.worst_desc.setObjectName("cardSubtitle")
        self.worst_desc.setWordWrap(True)
        worst_layout.addWidget(self.worst_desc)
        worst_layout.addSpacing(4)
        worst_layout.addWidget(QLabel(t("scn_worst_revenue")))
        self.worst_revenue = QDoubleSpinBox()
        self.worst_revenue.setRange(-100, 200)
        self.worst_revenue.setValue(-20)
        self.worst_revenue.setSuffix(" %")
        worst_layout.addWidget(self.worst_revenue)
        worst_layout.addWidget(QLabel(t("scn_worst_cost")))
        self.worst_cost = QDoubleSpinBox()
        self.worst_cost.setRange(-100, 200)
        self.worst_cost.setValue(15)
        self.worst_cost.setSuffix(" %")
        worst_layout.addWidget(self.worst_cost)
        worst_layout.addWidget(QLabel(t("scn_worst_efficiency")))
        self.worst_efficiency = QDoubleSpinBox()
        self.worst_efficiency.setRange(-100, 200)
        self.worst_efficiency.setValue(-10)
        self.worst_efficiency.setSuffix(" %")
        worst_layout.addWidget(self.worst_efficiency)
        assumptions_grid.addWidget(worst_frame, 0, 1)

        content_layout.addLayout(assumptions_grid)

        # ===== زر التشغيل =====
        self.run_btn = QPushButton(t("scn_run"))
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.setMinimumHeight(42)
        self.run_btn.clicked.connect(self.run_simulation)
        content_layout.addWidget(self.run_btn)

        # ===== النتائج =====
        self.results_title = QLabel(t("scn_results"))
        self.results_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.results_title)

        results_grid = QGridLayout()
        results_grid.setSpacing(15)
        self.best_card = self._make_result_card(t("scn_best_case"), "#2ECC71")
        results_grid.addWidget(self.best_card, 0, 0)
        self.base_card = self._make_result_card(t("scn_base_case"), "#3498DB")
        results_grid.addWidget(self.base_card, 0, 1)
        self.worst_card = self._make_result_card(t("scn_worst_case"), "#E74C3C")
        results_grid.addWidget(self.worst_card, 0, 2)
        content_layout.addLayout(results_grid)

        # ===== جدول المقارنة =====
        self.comparison_title = QLabel(t("scn_comparison"))
        self.comparison_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.comparison_title)

        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(5)
        self.comparison_table.setHorizontalHeaderLabels([
            t("scn_metric"), t("scn_best_col"), t("scn_base_col"),
            t("scn_worst_col"), t("scn_best_delta")
        ])
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.comparison_table.setEditTriggers(QTableWidget.NoEditTriggers)
        content_layout.addWidget(self.comparison_table)

        # ===== الرسوم البيانية =====
        self.charts_title = QLabel(t("scn_charts"))
        self.charts_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.charts_title)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)
        self.chart_line = ScenarioChart(t("scn_chart_line"))
        charts_grid.addWidget(self.chart_line, 0, 0)
        self.chart_bar = ScenarioChart(t("scn_chart_bar"))
        charts_grid.addWidget(self.chart_bar, 0, 1)
        self.chart_area = ScenarioChart(t("scn_chart_area"))
        charts_grid.addWidget(self.chart_area, 1, 0)
        content_layout.addLayout(charts_grid)

        # ===== تحليل الحساسية =====
        self.sensitivity_title = QLabel(t("scn_sensitivity"))
        self.sensitivity_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.sensitivity_title)

        sensitivity_ctrl_row = QHBoxLayout()
        sensitivity_ctrl_row.setSpacing(10)
        sensitivity_ctrl_row.addWidget(QLabel(t("scn_sensitivity_var")))
        self.sensitivity_var = QComboBox()
        self.sensitivity_var.addItem(t("scn_variable_revenue"), "revenue")
        self.sensitivity_var.addItem(t("scn_variable_cost"), "cost")
        self.sensitivity_var.addItem(t("scn_variable_efficiency"), "efficiency")
        sensitivity_ctrl_row.addWidget(self.sensitivity_var)
        sensitivity_ctrl_row.addWidget(QLabel(t("scn_sensitivity_range")))
        self.sensitivity_range = QDoubleSpinBox()
        self.sensitivity_range.setRange(1, 100)
        self.sensitivity_range.setValue(20)
        self.sensitivity_range.setSuffix(" %")
        sensitivity_ctrl_row.addWidget(self.sensitivity_range)
        self.sensitivity_update_btn = QPushButton(t("scn_sensitivity_update"))
        self.sensitivity_update_btn.setObjectName("secondaryBtn")
        self.sensitivity_update_btn.clicked.connect(self.update_sensitivity)
        sensitivity_ctrl_row.addWidget(self.sensitivity_update_btn)
        sensitivity_ctrl_row.addStretch()
        content_layout.addLayout(sensitivity_ctrl_row)

        sensitivity_grid = QGridLayout()
        sensitivity_grid.setSpacing(15)
        self.chart_tornado = ScenarioChart(t("scn_sensitivity_tornado"))
        sensitivity_grid.addWidget(self.chart_tornado, 0, 0)

        steps_frame = QFrame()
        steps_frame.setObjectName("card")
        steps_layout = QVBoxLayout(steps_frame)
        steps_layout.setContentsMargins(15, 15, 15, 15)
        steps_title = QLabel(t("scn_sensitivity_steps"))
        steps_title.setObjectName("sectionTitle")
        steps_layout.addWidget(steps_title)
        self.sensitivity_table = QTableWidget()
        self.sensitivity_table.setColumnCount(4)
        self.sensitivity_table.setHorizontalHeaderLabels([
            t("scn_sensitivity_pct"), t("scn_sensitivity_net"),
            t("scn_sensitivity_npm"), t("scn_sensitivity_roe")
        ])
        self.sensitivity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sensitivity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        steps_layout.addWidget(self.sensitivity_table)
        sensitivity_grid.addWidget(steps_frame, 0, 1)
        content_layout.addLayout(sensitivity_grid)

        # ===== أزرار الحفظ/التحميل/التصدير =====
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self.save_json_btn = QPushButton(t("scn_save_json"))
        self.save_json_btn.clicked.connect(self.save_scenarios_json)
        action_row.addWidget(self.save_json_btn)
        self.load_json_btn = QPushButton(t("scn_load_json"))
        self.load_json_btn.clicked.connect(self.load_scenarios_json)
        action_row.addWidget(self.load_json_btn)
        self.save_db_btn = QPushButton(t("scn_save_db"))
        self.save_db_btn.clicked.connect(self.save_scenarios_db)
        action_row.addWidget(self.save_db_btn)
        action_row.addStretch()
        self.export_btn = QPushButton(t("scn_export_pdf"))
        self.export_btn.setObjectName("pdfBtn")
        self.export_btn.setMinimumWidth(220)
        self.export_btn.clicked.connect(self.export_pdf)
        action_row.addWidget(self.export_btn)
        content_layout.addLayout(action_row)

        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _make_result_card(self, title, accent):
        """كارت نتيجة سيناريو: صافي الربح + المؤشرات"""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(250, 170)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)
        card.setLayout(layout)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        layout.addWidget(title_label)

        self._make_value_labels(layout, t("scn_net_income"), "--", accent, "net")

        outcome_label = QLabel("--")
        outcome_label.setObjectName("cardDesc")
        outcome_label.setStyleSheet(f"font-size: 11pt; color: {accent};")
        layout.addWidget(outcome_label)

        self._make_value_labels(layout, t("scn_npm"), "--", "#888", "npm")
        self._make_value_labels(layout, t("scn_roe"), "--", "#888", "roe")

        layout.addStretch()

        card.title_label = title_label
        card.outcome_label = outcome_label
        return card

    def _make_value_labels(self, layout, caption, value, color, attr):
        """إضافة سطر (تسمية + قيمة) داخل كارت النتيجة"""
        row = QHBoxLayout()
        cap = QLabel(caption)
        cap.setObjectName("cardSubtitle")
        val = QLabel(value)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        val.setFont(font)
        val.setStyleSheet(f"color: {color};")
        row.addWidget(cap)
        row.addStretch()
        row.addWidget(val)
        layout.addLayout(row)
        parent = layout.parentWidget()
        if parent is not None:
            setattr(parent, f"{attr}_label", val)

    # ===== المنطق =====

    def _has_data(self):
        return state.has_data()

    def _build_rates(self):
        best = {
            'revenue_change_pct': self.best_revenue.value() / 100,
            'cost_change_pct': self.best_cost.value() / 100,
            'efficiency_change_pct': self.best_efficiency.value() / 100,
        }
        worst = {
            'revenue_change_pct': self.worst_revenue.value() / 100,
            'cost_change_pct': self.worst_cost.value() / 100,
            'efficiency_change_pct': self.worst_efficiency.value() / 100,
        }
        return best, worst

    def run_simulation(self):
        """تشغيل المحاكاة الثلاثية"""
        if not self._has_data():
            QMessageBox.warning(self, t("scn_title"), t("scn_no_data"))
            return

        best, worst = self._build_rates()
        self.analyzer = ScenarioAnalyzer(state.financial_data, state.ratios)
        self._scenarios = self.analyzer.build_scenarios(best=best, worst=worst)
        state.scenarios = self._scenarios
        self._render_all()

    def refresh(self):
        """تحديث الواجهة بالبيانات الحالية"""
        if not self._has_data():
            self.subtitle.setText(t("scn_no_data"))
            self._disable_actions()
            self._clear_all()
            return

        self._enable_actions()
        self.analyzer = ScenarioAnalyzer(state.financial_data, state.ratios)
        if self._scenarios or state.scenarios:
            self._scenarios = self._scenarios or state.scenarios
            self._render_all()
        else:
            best, worst = self._build_rates()
            self._scenarios = self.analyzer.build_scenarios(best=best, worst=worst)
            state.scenarios = self._scenarios
            self._render_all()

    def _render_all(self):
        """رسم كل شيء من self._scenarios"""
        if not self._scenarios:
            return
        self._fill_cards()
        self._fill_comparison()
        self._draw_line_chart()
        self._draw_bar_chart()
        self._draw_area_chart()
        self.update_sensitivity()

    def _fill_cards(self):
        sc = self._scenarios
        for sc_type, card in [("best", self.best_card), ("base", self.base_card), ("worst", self.worst_card)]:
            data = sc.get(sc_type, {})
            card.net_label.setText(f"{data.get('net_income', 0):,.2f}")
            card.npm_label.setText(f"{data.get('net_profit_margin', 0):.2f}%")
            card.roe_label.setText(f"{data.get('roe', 0):.2f}%")
            outcome = data.get('outcome', 'base')
            card.outcome_label.setText(t(f"scn_outcome_{outcome}"))

    def _fill_comparison(self):
        comparison = self.analyzer.compare_scenarios(self._scenarios)
        self.comparison_table.setRowCount(len(self._METRIC_KEYS))
        for row_idx, metric in enumerate(self._METRIC_KEYS):
            label_key, fmt = self._METRIC_FMT[metric]
            data = comparison[metric]
            items = [
                t(label_key),
                fmt.format(data['best']),
                fmt.format(data['base']),
                fmt.format(data['worst']),
                f"{data['best_delta']:+,.2f}",
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter if col else Qt.AlignLeft | Qt.AlignVCenter)
                if col == 4:
                    color = QColor("#2ECC71") if data['best_delta'] >= 0 else QColor("#E74C3C")
                    item.setForeground(color)
                self.comparison_table.setItem(row_idx, col, item)

    def _scenario_axis_labels(self):
        return [t("scn_best_case"), t("scn_base_case"), t("scn_worst_case")]

    def _draw_line_chart(self):
        self.chart_line.figure.clear()
        ax = self.chart_line.figure.add_subplot(111)
        labels = self._scenario_axis_labels()
        revenue = [self._scenarios[k]['revenue'] for k in ("best", "base", "worst")]
        net = [self._scenarios[k]['net_income'] for k in ("best", "base", "worst")]
        x = range(3)
        ax.plot(x, revenue, 'o-', color='#3498DB', linewidth=2, label=t("scn_revenue"), markersize=6)
        ax.plot(x, net, 's-', color='#2ECC71', linewidth=2, label=t("scn_net_income"), markersize=6)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=9)
        ax.legend(fontsize=9, frameon=False)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(t("scn_chart_line"), fontsize=11, fontweight='bold', pad=10)
        self.chart_line.figure.tight_layout()
        self.chart_line.canvas.draw()

    def _draw_bar_chart(self):
        self.chart_bar.figure.clear()
        ax = self.chart_bar.figure.add_subplot(111)
        labels = self._scenario_axis_labels()
        npm = [self._scenarios[k]['net_profit_margin'] for k in ("best", "base", "worst")]
        roe = [self._scenarios[k]['roe'] for k in ("best", "base", "worst")]
        x = range(3)
        width = 0.35
        bars1 = ax.bar([i - width/2 for i in x], npm, width, color='#3498DB',
                       edgecolor=_chart_edge_color(), linewidth=0.5, label=t("scn_npm"))
        bars2 = ax.bar([i + width/2 for i in x], roe, width, color='#F39C12',
                       edgecolor=_chart_edge_color(), linewidth=0.5, label=t("scn_roe"))
        for bars in (bars1, bars2):
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.5,
                        f'{bar.get_height():.1f}', ha='center', va='bottom',
                        fontsize=8, color=_chart_text_color())
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=9)
        ax.legend(fontsize=9, frameon=False)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(t("scn_chart_bar"), fontsize=11, fontweight='bold', pad=10)
        self.chart_bar.figure.tight_layout()
        self.chart_bar.canvas.draw()

    def _draw_area_chart(self):
        self.chart_area.figure.clear()
        ax = self.chart_area.figure.add_subplot(111)
        labels = self._scenario_axis_labels()
        revenue = [self._scenarios[k]['revenue'] for k in ("best", "base", "worst")]
        net = [self._scenarios[k]['net_income'] for k in ("best", "base", "worst")]
        x = [0, 1, 2]
        ax.fill_between(x, revenue, color='#3498DB', alpha=0.25, label=t("scn_revenue"))
        ax.plot(x, revenue, color='#3498DB', linewidth=1.5)
        ax.fill_between(x, net, color='#2ECC71', alpha=0.35, label=t("scn_net_income"))
        ax.plot(x, net, color='#2ECC71', linewidth=1.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.legend(fontsize=9, frameon=False)
        ax.grid(True, axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(t("scn_chart_area"), fontsize=11, fontweight='bold', pad=10)
        self.chart_area.figure.tight_layout()
        self.chart_area.canvas.draw()

    def update_sensitivity(self):
        """تحديث تحليل الحساسية (تورنادو + جدول)"""
        if not self.analyzer or not self._scenarios:
            return
        variable = self.sensitivity_var.currentData() or "revenue"
        range_pct = self.sensitivity_range.value() / 100
        try:
            self._tornado = self.analyzer.tornado_analysis(range_pct=range_pct)
            self._sensitivity = self.analyzer.sensitivity_analysis(variable)
        except ValueError:
            self._sensitivity = []
            self._tornado = []
        self._draw_tornado()
        self._fill_sensitivity_table()

    def _draw_tornado(self):
        self.chart_tornado.figure.clear()
        ax = self.chart_tornado.figure.add_subplot(111)
        if not self._tornado or not self._scenarios:
            ax.text(0.5, 0.5, t("scn_no_data"), ha='center', va='center',
                    fontsize=10, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
            self.chart_tornado.figure.tight_layout()
            self.chart_tornado.canvas.draw()
            return

        base = self._scenarios['base']['net_income']
        labels = {
            'revenue': t("scn_variable_revenue"),
            'cost': t("scn_variable_cost"),
            'efficiency': t("scn_variable_efficiency"),
        }
        names = [labels.get(r['variable'], r['variable']) for r in self._tornado]
        y_pos = range(len(self._tornado))
        for i, row in enumerate(self._tornado):
            low = row['low_net']
            high = row['high_net']
            left = min(low, high, base)
            width = max(low, high, base) - left
            color = '#E74C3C' if high < base else '#2ECC71'
            ax.barh(i, width, left=left, color=color, height=0.6,
                    edgecolor=_chart_edge_color(), linewidth=0.5)
        ax.axvline(base, color='#3498DB', linestyle='--', linewidth=1.2)
        ax.text(base, len(self._tornado) - 0.2, f" {t('scn_base_case')}: {base:,.0f}",
                fontsize=8, color='#3498DB')
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(names, fontsize=9)
        ax.set_xlabel(t("scn_tornado_effect"), fontsize=9)
        ax.grid(True, axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(t("scn_sensitivity_tornado"), fontsize=11, fontweight='bold', pad=10)
        self.chart_tornado.figure.tight_layout()
        self.chart_tornado.canvas.draw()

    def _fill_sensitivity_table(self):
        rows = self._sensitivity or []
        self.sensitivity_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            items = [
                f"{row['pct_change'] * 100:+.1f}%",
                f"{row['net_income']:,.2f}",
                f"{row['net_profit_margin']:.2f}%",
                f"{row['roe']:.2f}%",
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.sensitivity_table.setItem(row_idx, col, item)

    # ===== حفظ / تحميل =====

    def save_scenarios_json(self):
        if not self._scenarios:
            QMessageBox.warning(self, t("scn_title"), t("scn_export_empty"))
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, t("scn_save_json"), "scenarios.json", "JSON (*.json)"
        )
        if not filename:
            return
        if ScenarioAnalyzer.save_scenarios(self._scenarios, filename):
            QMessageBox.information(self, t("scn_title"), t("scn_saved"))
        else:
            QMessageBox.critical(self, t("scn_title"), t("scn_save_error"))

    def load_scenarios_json(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, t("scn_load_json"), "", "JSON (*.json)"
        )
        if not filename:
            return
        loaded = ScenarioAnalyzer.load_scenarios(filename)
        if not loaded:
            QMessageBox.critical(self, t("scn_title"), t("scn_load_error"))
            return
        self._scenarios = loaded
        state.scenarios = loaded
        self._render_all()
        QMessageBox.information(self, t("scn_title"), t("scn_loaded"))

    def save_scenarios_db(self):
        if not self._scenarios:
            QMessageBox.warning(self, t("scn_title"), t("scn_export_empty"))
            return
        from database import save_analysis, save_scenario_results
        fiscal_year_id = save_analysis(
            company_name=state.company_name,
            fiscal_year=state.fiscal_year,
            financial_data=state.financial_data,
            ratios=state.ratios
        )
        if not fiscal_year_id:
            QMessageBox.critical(self, t("scn_title"), t("scn_save_db_error"))
            return
        if save_scenario_results(fiscal_year_id, self._scenarios):
            QMessageBox.information(self, t("scn_title"), t("scn_saved_db"))
        else:
            QMessageBox.critical(self, t("scn_title"), t("scn_save_db_error"))

    # ===== PDF =====

    def _build_report_text(self):
        from modules.reporting import ReportGenerator
        comparison = self.analyzer.compare_scenarios(self._scenarios)
        sensitivity = self._sensitivity or self.analyzer.sensitivity_analysis('revenue')
        reporter = ReportGenerator(state.company_name or t("de_company_default"), state.fiscal_year)
        return reporter.generate_scenario_report(self._scenarios, comparison, sensitivity)

    def export_pdf(self):
        if not self._scenarios:
            QMessageBox.warning(self, t("scn_title"), t("scn_export_empty"))
            return
        default_name = f"Scenario_Report_{state.company_name or 'Company'}_{state.fiscal_year}.pdf"
        filename, _ = QFileDialog.getSaveFileName(
            self, t("scn_export_pdf"), default_name, "PDF (*.pdf)"
        )
        if not filename:
            return
        from modules.reporting import ReportGenerator
        reporter = ReportGenerator(state.company_name or t("de_company_default"), state.fiscal_year)
        ok = reporter.export_to_pdf(self._build_report_text(), filename)
        if ok:
            QMessageBox.information(self, t("scn_title"), t("scn_export_success"))
        else:
            QMessageBox.critical(self, t("scn_title"), t("scn_export_error"))

    # ===== مساعدات =====

    def _disable_actions(self):
        for btn in (self.run_btn, self.save_json_btn, self.load_json_btn,
                    self.save_db_btn, self.export_btn, self.sensitivity_update_btn):
            btn.setEnabled(False)

    def _enable_actions(self):
        for btn in (self.run_btn, self.save_json_btn, self.load_json_btn,
                    self.save_db_btn, self.export_btn, self.sensitivity_update_btn):
            btn.setEnabled(True)

    def _clear_all(self):
        for chart in (self.chart_line, self.chart_bar, self.chart_area, self.chart_tornado):
            chart.figure.clear()
            plt.close(chart.figure)
            chart.canvas.draw()
        self.comparison_table.setRowCount(0)
        self.sensitivity_table.setRowCount(0)
        for card in (self.best_card, self.base_card, self.worst_card):
            card.net_label.setText("--")
            card.npm_label.setText("--")
            card.roe_label.setText("--")
            card.outcome_label.setText("--")

    def retranslate(self):
        """تحديث النصوص عند تغيير اللغة"""
        self.title.setText(t("scn_title"))
        self.subtitle.setText(t("scn_subtitle"))
        self.assumptions_title.setText(t("scn_assumptions"))
        self.best_title.setText(t("scn_best_title"))
        self.best_desc.setText(t("scn_best_desc"))
        self.worst_title.setText(t("scn_worst_title"))
        self.worst_desc.setText(t("scn_worst_desc"))
        self.run_btn.setText(t("scn_run"))
        self.results_title.setText(t("scn_results"))
        self.best_card.title_label.setText(t("scn_best_case"))
        self.base_card.title_label.setText(t("scn_base_case"))
        self.worst_card.title_label.setText(t("scn_worst_case"))
        self.comparison_title.setText(t("scn_comparison"))
        self.comparison_table.setHorizontalHeaderLabels([
            t("scn_metric"), t("scn_best_col"), t("scn_base_col"),
            t("scn_worst_col"), t("scn_best_delta")
        ])
        self.charts_title.setText(t("scn_charts"))
        self.chart_line.set_title(t("scn_chart_line"))
        self.chart_bar.set_title(t("scn_chart_bar"))
        self.chart_area.set_title(t("scn_chart_area"))
        self.sensitivity_title.setText(t("scn_sensitivity"))
        self.sensitivity_update_btn.setText(t("scn_sensitivity_update"))
        self.chart_tornado.set_title(t("scn_sensitivity_tornado"))
        self.sensitivity_table.setHorizontalHeaderLabels([
            t("scn_sensitivity_pct"), t("scn_sensitivity_net"),
            t("scn_sensitivity_npm"), t("scn_sensitivity_roe")
        ])
        self.save_json_btn.setText(t("scn_save_json"))
        self.load_json_btn.setText(t("scn_load_json"))
        self.save_db_btn.setText(t("scn_save_db"))
        self.export_btn.setText(t("scn_export_pdf"))
        self.sensitivity_var.blockSignals(True)
        current_var = self.sensitivity_var.currentData()
        self.sensitivity_var.clear()
        for label_key, code in [("scn_variable_revenue", "revenue"),
                                ("scn_variable_cost", "cost"),
                                ("scn_variable_efficiency", "efficiency")]:
            self.sensitivity_var.addItem(t(label_key), code)
        if current_var:
            index = self.sensitivity_var.findData(current_var)
            if index >= 0:
                self.sensitivity_var.setCurrentIndex(index)
        self.sensitivity_var.blockSignals(False)
        self.refresh()
