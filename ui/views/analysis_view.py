# عرض تحليل DuPont
# ==================

from ui.views._path import _  # noqa: F401 — ensures project root on sys.path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QSizePolicy, QScrollArea, QPushButton,
    QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Wedge
import matplotlib.pyplot as plt

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules import FinancialAnalyzer, ReportGenerator
from modules.benchmarks import benchmark_analyzer
from database.db_operations import get_company_dupont_history


def _chart_text_color():
    return ThemeColors.get("chart_text")


def _chart_edge_color():
    return ThemeColors.get("chart_edge")


class ChartWidget(QFrame):
    """كارت يحتوي على رسم بياني"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 300)
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


class DuPontView(QWidget):
    """واجهة تحليل DuPont"""

    def __init__(self):
        super().__init__()
        self._sector_code = None
        self.analyzer = None
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

        # العنوان
        self.title = QLabel(t("analysis_title"))
        self.title.setObjectName("headerTitle")
        content_layout.addWidget(self.title)

        self.subtitle = QLabel(t("analysis_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        content_layout.addWidget(self.subtitle)

        # ===== المعادلة =====
        equation_frame = QFrame()
        equation_frame.setObjectName("card")
        equation_layout = QVBoxLayout(equation_frame)

        eq_title = QLabel(t("ana_equation"))
        eq_title.setObjectName("sectionTitle")
        equation_layout.addWidget(eq_title)

        self.equation_label = QLabel(t("ana_equation_formula"))
        eq_font = QFont()
        eq_font.setPointSize(14)
        eq_font.setBold(True)
        self.equation_label.setFont(eq_font)
        self.equation_label.setAlignment(Qt.AlignCenter)
        self.equation_label.setStyleSheet("padding: 15px;")
        self.equation_label.setObjectName("equationLabel")
        equation_layout.addWidget(self.equation_label)

        content_layout.addWidget(equation_frame)

        # ===== المكونات =====
        self.components_title = QLabel(t("ana_components"))
        self.components_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.components_title)

        components_grid = QGridLayout()
        components_grid.setSpacing(15)

        # كارت هامش الربح الصافي
        self.npm_card = self._make_component_card(
            t("ana_npm"),
            "Net Profit Margin",
            "{:.2f}%",
            t("ana_npm_formula")
        )
        components_grid.addWidget(self.npm_card, 0, 0)

        # كارت دوران الأصول
        self.at_card = self._make_component_card(
            t("ana_asset_turnover"),
            "Asset Turnover",
            "{:.4f}",
            t("ana_asset_turnover_formula")
        )
        components_grid.addWidget(self.at_card, 0, 1)

        # كارت الرافعة المالية
        self.em_card = self._make_component_card(
            t("ana_equity_multiplier"),
            "Equity Multiplier",
            "{:.4f}",
            t("ana_equity_multiplier_formula")
        )
        components_grid.addWidget(self.em_card, 0, 2)

        # كارت ROE النهائي
        self.roe_card = self._make_component_card(
            t("ana_roe_label"),
            t("ana_roe_result"),
            "{:.2f}%",
            t("ana_roe_formula")
        )
        self.roe_card.setObjectName("roeCard")
        components_grid.addWidget(self.roe_card, 1, 0, 1, 3)

        content_layout.addLayout(components_grid)

        # ===== الرسوم البيانية =====
        self.charts_title = QLabel(t("ana_charts_title"))
        self.charts_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.charts_title)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)

        self.chart_waterfall = ChartWidget(t("ana_waterfall"))
        charts_grid.addWidget(self.chart_waterfall, 0, 0)

        self.chart_trend = ChartWidget(t("ana_trend"))
        charts_grid.addWidget(self.chart_trend, 0, 1)

        self.chart_gauge = ChartWidget(t("ana_gauge"))
        charts_grid.addWidget(self.chart_gauge, 1, 0, 1, 2)

        content_layout.addLayout(charts_grid)

        # ===== التفسير =====
        self.interpretation_title = QLabel(t("ana_interpretation"))
        self.interpretation_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.interpretation_title)

        self.interpretation_frame = QFrame()
        self.interpretation_frame.setObjectName("card")
        interp_layout = QVBoxLayout(self.interpretation_frame)

        self.interp_label = QLabel("--")
        self.interp_label.setWordWrap(True)
        self.interp_label.setTextFormat(Qt.RichText)
        self.interp_label.setStyleSheet("font-size: 11pt;")
        interp_layout.addWidget(self.interp_label)

        content_layout.addWidget(self.interpretation_frame)

        # ===== مقارنة القطاع =====
        self.industry_title = QLabel(t("ana_industry_title"))
        self.industry_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.industry_title)

        sector_row = QHBoxLayout()
        sector_row.setSpacing(10)
        self.industry_hint = QLabel(t("ana_industry_placeholder"))
        self.industry_hint.setObjectName("cardSubtitle")
        sector_row.addWidget(self.industry_hint)
        self.sector_combo = QComboBox()
        self.sector_combo.setMinimumWidth(260)
        self.sector_combo.currentIndexChanged.connect(self._on_sector_changed)
        sector_row.addWidget(self.sector_combo)
        sector_row.addStretch()
        content_layout.addLayout(sector_row)

        self.chart_industry = ChartWidget(t("ana_industry_title"))
        self.chart_industry.setMinimumSize(350, 320)
        content_layout.addWidget(self.chart_industry)

        self.industry_summary = QLabel(t("ana_industry_no_sector"))
        self.industry_summary.setWordWrap(True)
        self.industry_summary.setStyleSheet("font-size: 11pt;")
        content_layout.addWidget(self.industry_summary)

        # ===== التوصيات =====
        self.rec_title = QLabel(t("ana_recommendations"))
        self.rec_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.rec_title)

        self.rec_frame = QFrame()
        self.rec_frame.setObjectName("card")
        self.rec_layout = QVBoxLayout(self.rec_frame)
        self.rec_layout.setSpacing(8)
        content_layout.addWidget(self.rec_frame)

        # ===== رأس المال العامل =====
        self.wc_title = QLabel(t("ana_wc_title"))
        self.wc_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.wc_title)

        wc_grid = QGridLayout()
        wc_grid.setSpacing(15)

        self.wc_value = self._make_component_card(
            t("ana_wc"),
            "Working Capital",
            "{:,.2f}",
            t("ana_wc_formula")
        )
        wc_grid.addWidget(self.wc_value, 0, 0)

        self.wc_status = self._make_component_card(
            t("ana_wc_status"),
            "Status",
            "{}",
            t("ana_wc_question")
        )
        wc_grid.addWidget(self.wc_status, 0, 1)

        self.wc_cycle = self._make_component_card(
            t("ana_working_cycle"),
            "Operating Cycle",
            "{:,.2f}",
            t("ana_wc_cycle_formula")
        )
        wc_grid.addWidget(self.wc_cycle, 0, 2)

        content_layout.addLayout(wc_grid)

        # ===== زر التصدير =====
        export_row = QHBoxLayout()
        export_row.addStretch()
        self.export_btn = QPushButton(t("ana_export_pdf"))
        self.export_btn.setObjectName("pdfBtn")
        self.export_btn.setMinimumWidth(220)
        self.export_btn.clicked.connect(self.export_pdf)
        export_row.addWidget(self.export_btn)
        content_layout.addLayout(export_row)

        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        self._fill_sector_combo()

    def _fill_sector_combo(self):
        """ملء قائمة القطاعات حسب اللغة الحالية"""
        current = self._sector_code
        self.sector_combo.blockSignals(True)
        self.sector_combo.clear()

        lang_key = {"ar": "name_ar", "en": "name_en", "fr": "name_fr"}.get(state.language, "name_ar")
        self.sector_combo.addItem(t("ana_industry_placeholder"), None)
        for sector in benchmark_analyzer.get_sectors_list():
            self.sector_combo.addItem(sector.get(lang_key, sector["name_en"]), sector["code"])

        if current is not None:
            index = self.sector_combo.findData(current)
            if index >= 0:
                self.sector_combo.setCurrentIndex(index)
        self.sector_combo.blockSignals(False)

    def _on_sector_changed(self):
        self._sector_code = self.sector_combo.currentData()
        self._draw_industry()

    def _make_component_card(self, title, subtitle, format_str, description):
        """إنشاء كارت مكوّن"""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(250, 150)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)

        # العنوان
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        layout.addWidget(title_label)

        # الـ subtitle
        sub_label = QLabel(subtitle)
        sub_label.setObjectName("cardSubtitle")
        layout.addWidget(sub_label)

        # القيمة
        value_label = QLabel("--")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setObjectName("cardValue")
        layout.addWidget(value_label)

        # الوصف
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("cardDesc")
        layout.addWidget(desc_label)

        layout.addStretch()
        card.setLayout(layout)

        # تخزين المراجع
        card.title_label = title_label
        card.sub_label = sub_label
        card.value_label = value_label
        card.desc_label = desc_label
        card.format_str = format_str

        return card

    def _clear_recommendations(self):
        """مسح قائمة التوصيات"""
        while self.rec_layout.count():
            item = self.rec_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _fill_recommendations(self, recommendations):
        """ملء قائمة التوصيات"""
        self._clear_recommendations()
        if not recommendations:
            empty = QLabel("—")
            empty.setObjectName("cardSubtitle")
            self.rec_layout.addWidget(empty)
            return

        colors = {
            'critical': '#E74C3C',
            'warning': '#F39C12',
            'info': '#3498DB',
            'success': '#2ECC71',
        }
        icons = {
            'critical': '🔴',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅',
        }

        for rec in recommendations:
            code = rec.get('code', '')
            message = t(f'ana_rec_{code}') if code.startswith('rec_') else code
            extra = ""
            if rec.get('company_value') is not None:
                current = f"{rec['company_value']:.2f}" if isinstance(rec['company_value'], float) else f"{rec['company_value']}"
                extra = f" — {t('ana_rec_current')}: {current}"
            if rec.get('target') is not None:
                target = f"{rec['target']:.2f}" if isinstance(rec['target'], float) else f"{rec['target']}"
                extra += f" | {t('ana_rec_target')}: {target}"

            row = QLabel(f"{icons.get(rec.get('level'), 'ℹ️')} {message}{extra}")
            row.setWordWrap(True)
            row.setStyleSheet(f"font-size: 11pt; color: {colors.get(rec.get('level'), '#3498DB')};")
            self.rec_layout.addWidget(row)

    def retranslate(self):
        """تحديث النصوص عند تغيير اللغة"""
        self.title.setText(t("analysis_title"))
        self.subtitle.setText(t("analysis_subtitle"))
        self.equation_label.setText(t("ana_equation_formula"))
        self.components_title.setText(t("ana_components"))
        self.npm_card.title_label.setText(t("ana_npm"))
        self.npm_card.desc_label.setText(t("ana_npm_formula"))
        self.at_card.title_label.setText(t("ana_asset_turnover"))
        self.at_card.desc_label.setText(t("ana_asset_turnover_formula"))
        self.em_card.title_label.setText(t("ana_equity_multiplier"))
        self.em_card.desc_label.setText(t("ana_equity_multiplier_formula"))
        self.roe_card.title_label.setText(t("ana_roe_label"))
        self.roe_card.sub_label.setText(t("ana_roe_result"))
        self.charts_title.setText(t("ana_charts_title"))
        self.chart_waterfall.set_title(t("ana_waterfall"))
        self.chart_trend.set_title(t("ana_trend"))
        self.chart_gauge.set_title(t("ana_gauge"))
        self.interpretation_title.setText(t("ana_interpretation"))
        self.industry_title.setText(t("ana_industry_title"))
        self.industry_hint.setText(t("ana_industry_placeholder"))
        self.chart_industry.set_title(t("ana_industry_title"))
        self.rec_title.setText(t("ana_recommendations"))
        self.wc_title.setText(t("ana_wc_title"))
        self.wc_value.title_label.setText(t("ana_wc"))
        self.wc_value.desc_label.setText(t("ana_wc_formula"))
        self.wc_status.title_label.setText(t("ana_wc_status"))
        self.wc_status.desc_label.setText(t("ana_wc_question"))
        self.wc_cycle.title_label.setText(t("ana_working_cycle"))
        self.wc_cycle.desc_label.setText(t("ana_wc_cycle_formula"))
        self.export_btn.setText(t("ana_export_pdf"))
        self._fill_sector_combo()
        self.refresh()

    def _has_data(self):
        return state.has_data() and bool(state.dupont)

    def refresh(self):
        """تحديث البيانات"""
        if not self._has_data():
            self.subtitle.setText(t("dashboard_no_data"))
            self.export_btn.setEnabled(False)
            self._clear_all_charts()
            self._clear_recommendations()
            self.industry_summary.setText(t("ana_industry_no_sector"))
            return

        self.export_btn.setEnabled(True)
        self.analyzer = FinancialAnalyzer(state.financial_data)

        # تحديث الكروت
        self.npm_card.value_label.setText(self.npm_card.format_str.format(state.dupont.get('net_profit_margin', 0)))
        self.at_card.value_label.setText(self.at_card.format_str.format(state.dupont.get('asset_turnover', 0)))
        self.em_card.value_label.setText(self.em_card.format_str.format(state.dupont.get('equity_multiplier', 0)))
        self.roe_card.value_label.setText(self.roe_card.format_str.format(state.dupont.get('roe', 0)))

        # التفسير
        interp = state.dupont.get('analysis', [])
        if interp:
            interp_html = "<br>".join([f"• {item}" for item in interp])
            self.interp_label.setText(interp_html)
        else:
            self.interp_label.setText(t("ana_no_interpretation"))

        # الرسوم البيانية
        self._draw_waterfall()
        self._draw_trend()
        self._draw_gauge()

        # التوصيات (حسب القطاع المختار)
        recommendations = self.analyzer.dupont_recommendations(state.dupont, sector_code=self._sector_code)
        self._fill_recommendations(recommendations)

        # مقارنة القطاع
        self._draw_industry()

        # رأس المال العامل
        if state.working_capital:
            wc = state.working_capital.get('working_capital', 0)
            self.wc_value.value_label.setText(self.wc_value.format_str.format(wc))

            status = state.working_capital.get('status', '')
            self.wc_status.value_label.setText(status)

            cycle = state.working_capital.get('operating_cycle', 0)
            self.wc_cycle.value_label.setText(self.wc_cycle.format_str.format(cycle))

    def _clear_all_charts(self):
        for chart in [self.chart_waterfall, self.chart_trend, self.chart_gauge, self.chart_industry]:
            chart.figure.clear()
            plt.close(chart.figure)
            chart.canvas.draw()

    def _draw_waterfall(self):
        """رسم شلال DuPont"""
        self.chart_waterfall.figure.clear()
        ax = self.chart_waterfall.figure.add_subplot(111)

        dp = state.dupont
        waterfall = self.analyzer.dupont_waterfall(
            dp.get('net_profit_margin', 0),
            dp.get('asset_turnover', 0),
            dp.get('equity_multiplier', 0)
        )

        labels = [t("ana_waterfall_base"), t("ana_waterfall_at"),
                  t("ana_waterfall_em"), t("ana_waterfall_total")]
        values = [waterfall['base'], waterfall['turnover_effect'],
                  waterfall['leverage_effect'], waterfall['total']]

        cum = [0, values[0], values[0] + values[1], values[0] + values[1] + values[2]]
        bottoms = []
        heights = []
        colors = []
        for i, val in enumerate(values):
            if i == 3:
                bottoms.append(0)
                heights.append(val)
                colors.append('#3498DB')
            elif val >= 0:
                bottoms.append(cum[i])
                heights.append(val)
                colors.append('#2ECC71')
            else:
                bottoms.append(cum[i] + val)
                heights.append(abs(val))
                colors.append('#E74C3C')

        bars = ax.bar(labels, heights, bottom=bottoms, color=colors, width=0.6,
                      edgecolor=_chart_edge_color(), linewidth=0.5)

        for i, bar in enumerate(bars):
            y_pos = bar.get_y() + bar.get_height() + 0.02 if i < 3 else bar.get_height() + 0.02
            ax.text(bar.get_x() + bar.get_width() / 2., y_pos,
                    f'{values[i]:.2f}', ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color=_chart_text_color())

        for i in range(3):
            ax.plot([i + 0.4, i + 0.6], [cum[i + 1], cum[i + 1]],
                    color=ThemeColors.get("chart_grid"), lw=1, ls='--')

        all_vals = bottoms + [b + h for b, h in zip(bottoms, heights)]
        low, high = min(min(bottoms), 0), max(all_vals)
        padding = max(abs(high - low) * 0.15, 0.5)
        ax.set_ylim(low - padding, high + padding)

        ax.set_title(t("ana_waterfall"), fontsize=11, fontweight='bold', pad=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.chart_waterfall.figure.tight_layout()
        self.chart_waterfall.canvas.draw()

    def _draw_trend(self):
        """رسم تطور DuPont عبر السنوات"""
        self.chart_trend.figure.clear()
        ax = self.chart_trend.figure.add_subplot(111)

        history = []
        if state.company_name:
            try:
                history = get_company_dupont_history(state.company_name)
            except Exception:
                history = []

        if not history:
            ax.text(0.5, 0.5, t("ana_no_history"), ha='center', va='center',
                    fontsize=10, color=_chart_text_color(), transform=ax.transAxes,
                    wrap=True)
            ax.axis('off')
            self.chart_trend.figure.tight_layout()
            self.chart_trend.canvas.draw()
            return

        years = [h['year'] for h in history]
        roe = [h['roe'] for h in history]
        npm = [h['net_profit_margin'] for h in history]
        at = [h['asset_turnover'] for h in history]
        em = [h['equity_multiplier'] for h in history]

        ax.plot(years, roe, marker='o', color='#F39C12', label=t("ana_waterfall_total"))
        ax.plot(years, npm, marker='s', color='#3498DB', label=t("ana_industry_npm"))
        ax.set_ylabel('%', color=_chart_text_color())
        ax.tick_params(axis='x', labelrotation=0)

        ax2 = ax.twinx()
        ax2.plot(years, at, marker='^', color='#2ECC71', label=t("ana_industry_at"))
        ax2.plot(years, em, marker='D', color='#9B59B6', label=t("ana_industry_em"))
        ax2.set_ylabel('x', color=_chart_text_color())

        ax.grid(axis='y', color=ThemeColors.get("chart_grid"), lw=0.5)
        ax.set_title(t("ana_trend"), fontsize=11, fontweight='bold', pad=10)

        lines = ax.get_lines() + ax2.get_lines()
        ax.legend(lines, [l.get_label() for l in lines], fontsize=8, loc='best',
                  frameon=False)
        self.chart_trend.figure.tight_layout()
        self.chart_trend.canvas.draw()

    def _sector_roe_average(self):
        """متوسط ROE في القطاع المختار"""
        if not self._sector_code:
            return None
        try:
            from modules.benchmarks import ALGERIAN_SECTORS
            bm = ALGERIAN_SECTORS[self._sector_code]["benchmarks"]
            return bm.get("roe", {}).get("avg", 0)
        except Exception:
            return None

    def _draw_gauge(self):
        """رسم مؤشر أداء ROE"""
        self.chart_gauge.figure.clear()
        ax = self.chart_gauge.figure.add_subplot(111)

        roe = state.dupont.get('roe', 0)
        sector_avg = self._sector_roe_average()

        top = max(roe, sector_avg if sector_avg else 0, 20) * 1.25
        if top <= 0:
            top = 25

        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-0.15, 1.15)
        ax.set_aspect('equal')
        ax.axis('off')

        # مناطق ملونة: أحمر → برتقالي → أخضر
        for start_frac, end_frac, color in [
            (0, 0.33, '#E74C3C'), (0.33, 0.66, '#F39C12'), (0.66, 1.0, '#2ECC71')
        ]:
            theta1 = 180 - 180 * start_frac
            theta2 = 180 - 180 * end_frac
            ax.add_patch(Wedge((0, 0), 1.0, theta1, theta2, width=0.13,
                               facecolor=color, edgecolor=_chart_edge_color(), lw=0.5))

        # قيمة sector
        if sector_avg is not None:
            frac = min(sector_avg / top, 1.0)
            ang = 180 - 180 * frac
            r = np.deg2rad(ang)
            ax.plot([0.82 * np.cos(r), 0.95 * np.cos(r)],
                    [0.82 * np.sin(r), 0.95 * np.sin(r)],
                    color='#8E44AD', lw=3)
            ax.text(1.0, 1.0, f"{t('ana_gauge_sector')}: {sector_avg:.1f}%",
                    ha='right', va='top', fontsize=8, color='#8E44AD')

        # الإبرة
        frac = min(roe / top, 1.0)
        ang = 180 - 180 * frac
        r = np.deg2rad(ang)
        ax.plot([0, 0.75 * np.cos(r)], [0, 0.75 * np.sin(r)],
                color='#2C3E50', lw=2.5)
        ax.add_patch(plt.Circle((0, 0), 0.06, color='#2C3E50'))

        ax.text(0, 0.52, f"{roe:.1f}%", ha='center', fontsize=20,
                fontweight='bold', color=_chart_text_color())
        ax.set_title(t("ana_gauge"), fontsize=11, fontweight='bold', pad=10)
        self.chart_gauge.figure.tight_layout()
        self.chart_gauge.canvas.draw()

    def _draw_industry(self):
        """رسم مقارنة مكونات DuPont مع القطاع"""
        self.chart_industry.figure.clear()

        if not self._has_data():
            self.chart_industry.figure.tight_layout()
            self.chart_industry.canvas.draw()
            self.industry_summary.setText(t("ana_industry_no_sector"))
            return

        if not self._sector_code:
            ax = self.chart_industry.figure.add_subplot(111)
            ax.text(0.5, 0.5, t("ana_industry_no_sector"), ha='center', va='center',
                    fontsize=11, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
            self.chart_industry.figure.tight_layout()
            self.chart_industry.canvas.draw()
            self.industry_summary.setText("")
            return

        industry = self.analyzer.dupont_industry_comparison(state.dupont, self._sector_code)

        components = ['roe', 'net_profit_margin', 'asset_turnover', 'equity_multiplier']
        labels = {
            'roe': t('ana_industry_roe'),
            'net_profit_margin': t('ana_industry_npm'),
            'asset_turnover': t('ana_industry_at'),
            'equity_multiplier': t('ana_industry_em'),
        }

        status_colors = {'above': '#2ECC71', 'below': '#E74C3C', 'aligned': '#95A5A6', 'n/a': '#95A5A6'}
        status_text = {'above': t('ana_status_above'), 'below': t('ana_status_below'),
                       'aligned': t('ana_status_aligned'), 'n/a': '—'}

        summary_lines = []
        for idx, component in enumerate(components):
            ax = self.chart_industry.figure.add_subplot(2, 2, idx + 1)
            cmp_data = industry.get(component, {})
            company_val = cmp_data.get('company_value', 0)
            sector_val = cmp_data.get('sector_average', 0)
            status = cmp_data.get('status', 'n/a')

            bars = ax.bar([t('ana_industry_company'), t('ana_industry_avg')],
                          [company_val, sector_val],
                          color=[status_colors.get(status, '#95A5A6'), '#3498DB'],
                          width=0.55, edgecolor=_chart_edge_color(), linewidth=0.5)
            for bar, val in zip(bars, [company_val, sector_val]):
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
                        f'{val:.2f}', ha='center', va='bottom', fontsize=8,
                        color=_chart_text_color())

            ax.set_title(labels[component], fontsize=9, fontweight='bold', pad=6)
            ax.tick_params(axis='x', labelsize=7)
            ax.tick_params(axis='y', labelsize=7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_ylim(0, max(company_val, sector_val) * 1.3 if max(company_val, sector_val) > 0 else 1)

            summary_lines.append(
                f"{labels[component]}: {company_val:.2f} vs {sector_val:.2f} — {status_text.get(status, '—')}"
            )

        self.chart_industry.figure.tight_layout()
        self.chart_industry.canvas.draw()
        self.industry_summary.setText("\n".join(f"• {line}" for line in summary_lines))

    def _build_report_text(self):
        """بناء نص التقرير للتصدير"""
        dp = state.dupont
        waterfall = self.analyzer.dupont_waterfall(
            dp.get('net_profit_margin', 0),
            dp.get('asset_turnover', 0),
            dp.get('equity_multiplier', 0)
        )
        industry = self.analyzer.dupont_industry_comparison(dp, self._sector_code) if self._sector_code else None
        recommendations = self.analyzer.dupont_recommendations(dp, sector_code=self._sector_code)

        reporter = ReportGenerator(state.company_name or t("de_company_default"), state.fiscal_year)
        return reporter.generate_dupont_report(dp, waterfall, industry, recommendations)

    def export_pdf(self):
        """تصدير تقرير DuPont إلى PDF"""
        if not self._has_data():
            QMessageBox.warning(self, t("analysis_title"), t("ana_export_empty"))
            return

        default_name = f"DuPont_Report_{state.company_name or 'Company'}_{state.fiscal_year}.pdf"
        filename, _ = QFileDialog.getSaveFileName(
            self, t("ana_export_pdf"), default_name, "PDF (*.pdf)"
        )
        if not filename:
            return

        from modules.reporting import ReportGenerator
        reporter = ReportGenerator(state.company_name or t("de_company_default"), state.fiscal_year)
        ok = reporter.export_to_pdf(self._build_report_text(), filename)

        if ok:
            QMessageBox.information(self, t("analysis_title"), t("ana_export_success"))
        else:
            QMessageBox.critical(self, t("analysis_title"), t("ana_export_error"))
