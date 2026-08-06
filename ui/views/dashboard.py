# لوحة التحكم - Dashboard
# ========================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QSizePolicy, QScrollArea, QPushButton
)
from PyQt5.QtCore import (pyqtSignal)
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t


def _chart_text_color():
    return ThemeColors.get("chart_text")


def _chart_edge_color():
    return ThemeColors.get("chart_edge")


class ChartWidget(QFrame):
    """كارت يحتوي على رسم بياني"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

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
        import matplotlib.pyplot as plt
        plt.close(self.figure)
        self.canvas.draw()


class SummaryCard(QFrame):
    """كارت ملخص صغير"""

    def __init__(self, title, value, subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(200, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        layout.addWidget(self.title_label)

        self.value_label = QLabel(value)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setObjectName("cardValue")
        layout.addWidget(self.value_label)

        self.sub_label = None
        if subtitle:
            self.sub_label = QLabel(subtitle)
            self.sub_label.setObjectName("cardSubtitle")
            layout.addWidget(self.sub_label)

        layout.addStretch()
        self.setLayout(layout)

    def set_texts(self, title, subtitle=""):
        self.title_label.setText(title)
        if self.sub_label:
            self.sub_label.setText(subtitle)


class DashboardView(QWidget):
    """لوحة التحكم الرئيسية مع الرسوم البيانية"""

    export_pdf_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._dash_fingerprint = None
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title_label = QLabel(t("dashboard_title"))
        self.title_label.setObjectName("headerTitle")
        main_layout.addWidget(self.title_label)

        self.subtitle = QLabel(t("dashboard_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dashboardScroll")

        scroll_content = QWidget()
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setSpacing(15)

        self._build_summary_cards()
        self._build_export_button()
        self._build_charts()

        self.content_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    def _build_summary_cards(self):
        """بناء كروت الملخص"""
        self.summary_section = self._section_label(t("summary_title"))
        self.content_layout.addWidget(self.summary_section)

        summary_grid = QGridLayout()
        summary_grid.setSpacing(10)

        self.card_roe = SummaryCard(t("card_roe_title"), "--", t("card_roe_sub"))
        self.card_cr = SummaryCard(t("card_cr_title"), "--", t("card_cr_sub"))
        self.card_npm = SummaryCard(t("card_npm_title"), "--", t("card_npm_sub"))
        self.card_de = SummaryCard(t("card_de_title"), "--", t("card_de_sub"))

        summary_grid.addWidget(self.card_roe, 0, 0)
        summary_grid.addWidget(self.card_cr, 0, 1)
        summary_grid.addWidget(self.card_npm, 0, 2)
        summary_grid.addWidget(self.card_de, 0, 3)

        self.content_layout.addLayout(summary_grid)

    def _build_export_button(self):
        """بناء زر تصدير Dashboard"""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.export_btn = QPushButton(t("dashboard_export_pdf"))
        self.export_btn.setObjectName("primaryBtn")
        self.export_btn.setMinimumWidth(280)
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self.export_pdf_clicked.emit)
        btn_layout.addWidget(self.export_btn)

        self.content_layout.addLayout(btn_layout)

    def _build_charts(self):
        """بناء الرسوم البيانية"""
        self.charts_section = self._section_label(t("charts_title"))
        self.content_layout.addWidget(self.charts_section)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)

        self.chart_ratios = ChartWidget(t("chart_ratios"))
        charts_grid.addWidget(self.chart_ratios, 0, 0)

        self.chart_profitability = ChartWidget(t("chart_profitability"))
        charts_grid.addWidget(self.chart_profitability, 0, 1)

        self.chart_dupont = ChartWidget(t("chart_dupont"))
        charts_grid.addWidget(self.chart_dupont, 1, 0)

        self.chart_balance = ChartWidget(t("chart_balance"))
        charts_grid.addWidget(self.chart_balance, 1, 1)

        self.chart_expenses = ChartWidget(t("chart_expenses"))
        charts_grid.addWidget(self.chart_expenses, 2, 0)

        self.chart_radar = ChartWidget(t("chart_radar"))
        charts_grid.addWidget(self.chart_radar, 2, 1)

        self.chart_zscore = ChartWidget(t("chart_zscore"))
        charts_grid.addWidget(self.chart_zscore, 3, 0)

        self.chart_liquidity = ChartWidget(t("chart_liquidity"))
        charts_grid.addWidget(self.chart_liquidity, 3, 1)

        self.content_layout.addLayout(charts_grid)

    def _section_label(self, text):
        """إنشاء عنوان قسم"""
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def retranslate(self):
        """ تحديث كل النصوص عند تغيير اللغة"""
        self.title_label.setText(t("dashboard_title"))
        self.subtitle.setText(t("dashboard_subtitle"))
        self.summary_section.setText(t("summary_title"))
        self.charts_section.setText(t("charts_title"))
        self.export_btn.setText(t("dashboard_export_pdf"))
        self.card_roe.set_texts(t("card_roe_title"), t("card_roe_sub"))
        self.card_cr.set_texts(t("card_cr_title"), t("card_cr_sub"))
        self.card_npm.set_texts(t("card_npm_title"), t("card_npm_sub"))
        self.card_de.set_texts(t("card_de_title"), t("card_de_sub"))
        self.chart_ratios.set_title(t("chart_ratios"))
        self.chart_profitability.set_title(t("chart_profitability"))
        self.chart_dupont.set_title(t("chart_dupont"))
        self.chart_balance.set_title(t("chart_balance"))
        self.chart_expenses.set_title(t("chart_expenses"))
        self.chart_radar.set_title(t("chart_radar"))
        self.chart_zscore.set_title(t("chart_zscore"))
        self.chart_liquidity.set_title(t("chart_liquidity"))
        self.refresh()

    def refresh(self):
        """ تحديث كل البيانات والرسوم"""
        if not state.has_data():
            fingerprint = repr(state.__dict__)
            if fingerprint == self._dash_fingerprint:
                return
            self._dash_fingerprint = fingerprint
            self.subtitle.setText(t("dashboard_no_data"))
            self._clear_all()
            return

        fingerprint = repr(state.__dict__)
        if fingerprint == self._dash_fingerprint:
            return
        self._dash_fingerprint = fingerprint

        self.subtitle.setText(
            f"{t('dash_company_label')} {state.company_name} | {t('dash_fiscal_label')} {state.fiscal_year}"
        )

        ratios = state.ratios

        self.card_roe.value_label.setText(f"{ratios.get('roe', 0):.2f}%")
        self.card_cr.value_label.setText(f"{ratios.get('current_ratio', 0):.2f}")
        self.card_npm.value_label.setText(f"{ratios.get('net_profit_margin', 0):.2f}%")
        self.card_de.value_label.setText(f"{ratios.get('debt_to_equity', 0):.2f}")

        self._draw_ratios_bar(ratios)
        self._draw_profitability_pie(ratios)
        self._draw_dupont_waterfall(ratios)
        self._draw_balance_pie(state.financial_data)
        self._draw_expenses_pie(state.financial_data)
        self._draw_radar(ratios)
        self._draw_zscore_gauge()
        self._draw_liquidity_chart(state.financial_data)

    def _clear_all(self):
        """مسح كل الرسوم"""
        import matplotlib.pyplot as plt
        self.card_roe.value_label.setText("--")
        self.card_cr.value_label.setText("--")
        self.card_npm.value_label.setText("--")
        self.card_de.value_label.setText("--")
        for chart in [self.chart_ratios, self.chart_profitability, self.chart_dupont,
                      self.chart_balance, self.chart_expenses, self.chart_radar,
                      self.chart_zscore, self.chart_liquidity]:
            chart.figure.clear()
            plt.close(chart.figure)
            chart.canvas.draw()

    def _draw_ratios_bar(self, ratios):
        """رسم بياني شريطي للنسب المالية"""
        self.chart_ratios.figure.clear()
        ax = self.chart_ratios.figure.add_subplot(111)

        labels = ['Current\nRatio', 'Quick\nRatio', 'ROA', 'ROE', 'Asset\nTurnover']
        keys = ['current_ratio', 'quick_ratio', 'roa', 'roe', 'asset_turnover']
        values = [ratios.get(k, 0) for k in keys]
        colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']

        bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor=_chart_edge_color(), linewidth=0.5)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.02,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_title(t("dash_main_indicators"), fontsize=11, fontweight='bold', pad=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, max(values) * 1.3 if max(values) > 0 else 1)

        self.chart_ratios.figure.tight_layout()
        self.chart_ratios.canvas.draw()

    def _draw_profitability_pie(self, ratios):
        """رسم بياني دائري لنسب الربحية"""
        self.chart_profitability.figure.clear()
        ax = self.chart_profitability.figure.add_subplot(111)

        labels = ['Gross Margin', 'Net Margin', 'ROA', 'ROE']
        keys = ['gross_profit_margin', 'net_profit_margin', 'roa', 'roe']
        values = [max(ratios.get(k, 0), 0) for k in keys]
        colors = ['#27AE60', '#3498DB', '#E74C3C', '#F39C12']

        if sum(values) == 0:
            ax.text(0.5, 0.5, t("dash_no_data_chart"), ha='center', va='center',
                    fontsize=12, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
        else:
            wedges, texts, autotexts = ax.pie(
                values, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, pctdistance=0.75
            )
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_fontweight('bold')

        ax.set_title(t("dash_profitability_structure"), fontsize=11, fontweight='bold', pad=10)
        self.chart_profitability.figure.tight_layout()
        self.chart_profitability.canvas.draw()

    def _draw_dupont_waterfall(self, ratios):
        """رسم بياني شريطي لتحليل DuPont"""
        self.chart_dupont.figure.clear()
        ax = self.chart_dupont.figure.add_subplot(111)

        if not state.dupont:
            ax.text(0.5, 0.5, t("dash_no_data_dupont"), ha='center', va='center',
                    fontsize=12, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
        else:
            dp = state.dupont
            labels = ['Net Profit\nMargin %', 'Asset\nTurnover', 'Equity\nMultiplier', 'ROE %']
            values = [
                dp.get('net_profit_margin', 0),
                dp.get('asset_turnover', 0),
                dp.get('equity_multiplier', 0),
                dp.get('roe', 0)
            ]
            colors = ['#2ECC71', '#3498DB', '#E74C3C', '#F39C12']

            bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor=_chart_edge_color(), linewidth=0.5)

            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.02,
                        f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

            ax.set_title(t("chart_dupont"), fontsize=11, fontweight='bold', pad=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_ylim(0, max(values) * 1.3 if max(values) > 0 else 1)

        self.chart_dupont.figure.tight_layout()
        self.chart_dupont.canvas.draw()

    def _draw_balance_pie(self, data):
        """رسم بياني دائري لهيكل الميزانية"""
        self.chart_balance.figure.clear()
        ax = self.chart_balance.figure.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, t("dash_no_data_chart"), ha='center', va='center',
                    fontsize=12, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
            self.chart_balance.canvas.draw()
            return

        total_liab = data.get('total_liabilities', 0)
        equity = data.get('equity', 0)

        if total_liab == 0 and equity == 0:
            ax.text(0.5, 0.5, t("dash_no_data_chart"), ha='center', va='center',
                    fontsize=12, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
        else:
            labels = [t("dash_liabilities"), t("dash_equity")]
            values = [total_liab, equity]
            colors = ['#E74C3C', '#3498DB']
            explode = (0.03, 0.03)

            wedges, texts, autotexts = ax.pie(
                values, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, explode=explode, pctdistance=0.75
            )
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')

        ax.set_title(t("dash_finance_structure"), fontsize=11, fontweight='bold', pad=10)
        self.chart_balance.figure.tight_layout()
        self.chart_balance.canvas.draw()

    def _draw_expenses_pie(self, data):
        """رسم بياني دائري لتوزيع المصروفات"""
        self.chart_expenses.figure.clear()
        ax = self.chart_expenses.figure.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, t("dash_no_data_chart"), ha='center', va='center',
                    fontsize=12, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
            self.chart_expenses.canvas.draw()
            return

        cogs = data.get('cost_of_goods_sold', 0)
        gross = data.get('gross_profit', 0)
        net = data.get('net_income', 0)
        opex = max(gross - net, 0) if gross > 0 else 0

        if cogs == 0 and opex == 0:
            ax.text(0.5, 0.5, t("dash_no_data_chart"), ha='center', va='center',
                    fontsize=12, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
        else:
            labels = [t("dash_cogs"), t("dash_opex"), t("dash_net_profit")]
            values = [cogs, opex, max(net, 0)]
            colors = ['#E74C3C', '#F39C12', '#2ECC70']

            wedges, texts, autotexts = ax.pie(
                [v for v in values if v > 0],
                labels=[l for l, v in zip(labels, values) if v > 0],
                colors=[c for c, v in zip(colors, values) if v > 0],
                autopct='%1.1f%%',
                startangle=90, pctdistance=0.75
            )
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_fontweight('bold')

        ax.set_title(t("dash_expenses_structure"), fontsize=11, fontweight='bold', pad=10)
        self.chart_expenses.figure.tight_layout()
        self.chart_expenses.canvas.draw()

    def _draw_radar(self, ratios):
        self.chart_radar.figure.clear()
        ax = self.chart_radar.figure.add_subplot(111, polar=True)

        categories = ['ROE', 'ROA', 'NPM', 'Current\nRatio', 'Quick\nRatio', 'Asset\nTurnover']
        keys = ['roe', 'roa', 'net_profit_margin', 'current_ratio', 'quick_ratio', 'asset_turnover']
        raw_values = [max(ratios.get(k, 0), 0) for k in keys]
        max_ref = [25, 15, 25, 3, 2.5, 2]
        values = [min(r / m * 100, 100) for r, m in zip(raw_values, max_ref)]

        N = len(categories)
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += angles[:1]
        values_plot = values + values[:1]

        ax.plot(angles, values_plot, 'o-', linewidth=2, color='#3498DB')
        ax.fill(angles, values_plot, alpha=0.2, color='#3498DB')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_title(t("chart_radar"), fontsize=11, fontweight='bold', pad=20)
        ax.set_facecolor(ThemeColors.get("chart_bg"))
        self.chart_radar.figure.tight_layout()
        self.chart_radar.canvas.draw()

    def _draw_zscore_gauge(self):
        self.chart_zscore.figure.clear()
        ax = self.chart_zscore.figure.add_subplot(111)

        fd = state.financial_data
        from modules.calculations import CalculationEngine
        engine = CalculationEngine()
        working_capital = (fd.get('current_assets', 0) or 0) - (fd.get('current_liabilities', 0) or 0)
        retained_earnings = fd.get('net_income', 0) or 0
        ebit = retained_earnings
        equity = fd.get('equity', 0) or 0
        total_assets = fd.get('total_assets', 0) or 0
        market_value = equity if equity > 0 else total_assets * 0.5
        book_debt = (fd.get('total_liabilities', 0) or 0)
        revenue = fd.get('revenue', 0) or 0

        result = engine.z_score(
            working_capital=working_capital,
            retained_earnings=retained_earnings,
            ebit=ebit,
            market_value_equity=market_value,
            book_value_debt=book_debt,
            sales=revenue,
            total_assets=total_assets,
        )
        z = result.get("z_score", 0)
        classification = result.get("status", "safe")

        colors_gauge = {'safe': '#2ECC71', 'grey': '#F39C12', 'danger': '#E74C3C'}
        color = colors_gauge.get(classification, '#95A5A6')

        bar_x = [0.5]
        bar_h = min(max(z, -3) / 5, 1.2) if z != 0 else 0
        ax.barh(0, bar_h, height=0.5, color=color, edgecolor='none')
        ax.barh(0, 1.2, height=0.5, color=ThemeColors.get("chart_grid"), edgecolor='none', zorder=0)

        zones = [(-3, -1, '#E74C3C', 'Danger'), (-1, 1.81, '#F39C12', 'Grey'), (1.81, 5, '#2ECC71', 'Safe')]
        for x0, x1, c, label in zones:
            ax.axvline(x=(x0 + 3) / 8, color=c, linewidth=2, alpha=0.5, linestyle='--')

        ax.set_xlim(0, 1.2)
        ax.set_ylim(-0.5, 0.5)
        ax.text(0.5, 0.4, f"Z-Score = {z:.2f}", ha='center', va='center',
                fontsize=16, fontweight='bold', color=color)
        ax.text(0.5, 0.15, classification.upper(), ha='center', va='center',
                fontsize=12, color=color, style='italic')
        ax.axis('off')
        self.chart_zscore.figure.tight_layout()
        self.chart_zscore.canvas.draw()

    def _draw_liquidity_chart(self, data):
        self.chart_liquidity.figure.clear()
        ax = self.chart_liquidity.figure.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, t("dash_no_data_chart"), ha='center', va='center',
                    fontsize=12, color=_chart_text_color(), transform=ax.transAxes)
            ax.axis('off')
            self.chart_liquidity.canvas.draw()
            return

        ca = data.get('current_assets', 0)
        inv = data.get('inventory', 0)
        cl = data.get('current_liabilities', 0)
        qa = max(ca - inv, 0)

        labels = [t("dash_current_assets"), t("dash_inventory"), t("dash_quick_assets"), t("dash_current_liab")]
        values = [ca, inv, qa, cl]
        colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12']

        bars = ax.barh(labels, values, color=colors, height=0.5, edgecolor=_chart_edge_color(), linewidth=0.5)
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height() / 2.,
                    f'{val:,.0f}', ha='left', va='center', fontsize=9, fontweight='bold')

        cr = qa / cl if cl > 0 else 0
        ax.set_title(f"{t('chart_liquidity')} (Quick Ratio: {cr:.2f})", fontsize=11, fontweight='bold', pad=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlim(0, max(values) * 1.2 if max(values) > 0 else 1)
        self.chart_liquidity.figure.tight_layout()
        self.chart_liquidity.canvas.draw()
