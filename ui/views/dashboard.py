# لوحة التحكم - Dashboard
# ========================

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QSizePolicy, QScrollArea, QPushButton
)
from PyQt6.QtCore import (pyqtSignal)
from PyQt6.QtGui import QFont

from ui.charts import (PgChartWidget, PgPieWidget, PgPolarWidget,
    draw_bar, draw_horizontal_bar, draw_line, draw_area, draw_waterfall, draw_pie_widget, draw_radar, draw_gauge,
    _text_color, _edge_color, _chart_bg, _hex_to_rgb, _mk_brush, _mk_pen, _mk_text_item)

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from ui.plotly_export import export_dashboard_html


class ChartWidget(QFrame):
    """كارت يحتوي على رسم بياني"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.plot_widget = PgChartWidget(title)
        self.plot_item = self.plot_widget.plot_item
        self.plot_widget.setMinimumSize(300, 200)
        layout.addWidget(self.plot_widget)

        self.setLayout(layout)

    def set_title(self, title):
        self.title_label.setText(title)

    def clear_chart(self):
        self.plot_item.clear()


class PieChartWidget(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.pie_widget = PgPieWidget(title)
        layout.addWidget(self.pie_widget)

        self.setLayout(layout)

    def set_title(self, title):
        self.title_label.setText(title)

    def clear_chart(self):
        self.pie_widget.pie_canvas.set_pie_data([], [], [])


class RadarChartWidget(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(350, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        layout.addWidget(self.title_label)

        self.polar_widget = PgPolarWidget(title)
        layout.addWidget(self.polar_widget)

        self.setLayout(layout)

    def set_title(self, title):
        self.title_label.setText(title)

    def clear_chart(self):
        self.polar_widget.clear_plot()


class SummaryCard(QFrame):
    """كارت ملخص صغير"""

    def __init__(self, title, value, subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(200, 120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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

        self.html_btn = QPushButton(t("export_dashboard_html"))
        self.html_btn.setObjectName("secondaryBtn")
        self.html_btn.setMinimumWidth(280)
        self.html_btn.setMinimumHeight(40)
        self.html_btn.clicked.connect(self._export_html)
        btn_layout.addWidget(self.html_btn)

        self.content_layout.addLayout(btn_layout)

    def _build_charts(self):
        """بناء الرسوم البيانية"""
        self.charts_section = self._section_label(t("charts_title"))
        self.content_layout.addWidget(self.charts_section)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)

        self.chart_ratios = ChartWidget(t("chart_ratios"))
        charts_grid.addWidget(self.chart_ratios, 0, 0)

        self.chart_profitability = PieChartWidget(t("chart_profitability"))
        charts_grid.addWidget(self.chart_profitability, 0, 1)

        self.chart_dupont = ChartWidget(t("chart_dupont"))
        charts_grid.addWidget(self.chart_dupont, 1, 0)

        self.chart_balance = PieChartWidget(t("chart_balance"))
        charts_grid.addWidget(self.chart_balance, 1, 1)

        self.chart_expenses = PieChartWidget(t("chart_expenses"))
        charts_grid.addWidget(self.chart_expenses, 2, 0)

        self.chart_radar = RadarChartWidget(t("chart_radar"))
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

    def _export_html(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getSaveFileName(
            self, t("export_dashboard_html"), "dashboard.html", "HTML (*.html)"
        )
        if not path:
            return
        ratios = state.ratios
        fd = state.financial_data
        charts_data = {}

        labels_r = ['Current Ratio', 'Quick Ratio', 'ROA', 'ROE', 'Asset Turnover']
        keys_r = ['current_ratio', 'quick_ratio', 'roa', 'roe', 'asset_turnover']
        charts_data['ratios_bar'] = {
            'labels': labels_r,
            'values': [ratios.get(k, 0) for k in keys_r],
            'colors': ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6'],
        }

        pp_labels = ['Gross Margin', 'Net Margin', 'ROA', 'ROE']
        pp_keys = ['gross_profit_margin', 'net_profit_margin', 'roa', 'roe']
        charts_data['profitability_pie'] = {
            'labels': pp_labels,
            'values': [max(ratios.get(k, 0), 0) for k in pp_keys],
            'colors': ['#27AE60', '#3498DB', '#E74C3C', '#F39C12'],
        }

        if state.dupont:
            dp = state.dupont
            charts_data['dupont'] = {
                'labels': ['Net Profit Margin %', 'Asset Turnover', 'Equity Multiplier', 'ROE %'],
                'values': [dp.get('net_profit_margin', 0), dp.get('asset_turnover', 0),
                           dp.get('equity_multiplier', 0), dp.get('roe', 0)],
                'colors': ['#2ECC71', '#3498DB', '#E74C3C', '#F39C12'],
            }

        if fd:
            total_liab = fd.get('total_liabilities', 0)
            equity = fd.get('equity', 0)
            if total_liab or equity:
                charts_data['balance_pie'] = {
                    'labels': ['Liabilities', 'Equity'],
                    'values': [total_liab, equity],
                    'colors': ['#E74C3C', '#3498DB'],
                }
            cogs = fd.get('cost_of_goods_sold', 0)
            gross = fd.get('gross_profit', 0)
            net = fd.get('net_income', 0)
            opex = max(gross - net, 0) if gross > 0 else 0
            if cogs or opex:
                charts_data['expenses_pie'] = {
                    'labels': ['COGS', 'OpEx', 'Net Profit'],
                    'values': [cogs, opex, max(net, 0)],
                    'colors': ['#E74C3C', '#F39C12', '#2ECC71'],
                }
            ca = fd.get('current_assets', 0)
            inv = fd.get('inventory', 0)
            cl = fd.get('current_liabilities', 0)
            charts_data['liquidity'] = {
                'labels': ['Current Assets', 'Inventory', 'Quick Assets', 'Current Liabilities'],
                'values': [ca, inv, max(ca - inv, 0), cl],
                'colors': ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12'],
            }

        cat_r = ['ROE', 'ROA', 'NPM', 'Current Ratio', 'Quick Ratio', 'Asset Turnover']
        keys_rd = ['roe', 'roa', 'net_profit_margin', 'current_ratio', 'quick_ratio', 'asset_turnover']
        max_ref = [25, 15, 25, 3, 2.5, 2]
        raw = [max(ratios.get(k, 0), 0) for k in keys_rd]
        charts_data['radar'] = {
            'labels': cat_r,
            'values': [min(r / m * 100, 100) for r, m in zip(raw, max_ref)],
        }

        from modules.calculations import CalculationEngine
        engine = CalculationEngine()
        working_capital = (fd.get('current_assets', 0) or 0) - (fd.get('current_liabilities', 0) or 0) if fd else 0
        retained_earnings = (fd.get('net_income', 0) or 0) if fd else 0
        equity_val = (fd.get('equity', 0) or 0) if fd else 0
        total_assets = (fd.get('total_assets', 0) or 0) if fd else 0
        market_value = equity_val if equity_val > 0 else total_assets * 0.5
        book_debt = (fd.get('total_liabilities', 0) or 0) if fd else 0
        revenue = (fd.get('revenue', 0) or 0) if fd else 0
        result = engine.z_score(
            working_capital=working_capital, retained_earnings=retained_earnings,
            ebit=retained_earnings, market_value_equity=market_value,
            book_value_debt=book_debt, sales=revenue, total_assets=total_assets,
        )
        charts_data['zscore'] = {
            'value': result.get('z_score', 0),
            'zones': [('#E74C3C', 'Danger', 0, 1.8), ('#F39C12', 'Grey', 1.8, 3.0), ('#2ECC71', 'Safe', 3.0, 5.0)],
        }

        try:
            export_dashboard_html(path, charts_data)
            QMessageBox.information(self, t("export_dashboard_html"), t("dashboard_export_html_success"))
        except Exception as e:
            QMessageBox.warning(self, t("export_dashboard_html"), str(e))

    def retranslate(self):
        """ تحديث كل النصوص عند تغيير اللغة"""
        self.title_label.setText(t("dashboard_title"))
        self.subtitle.setText(t("dashboard_subtitle"))
        self.summary_section.setText(t("summary_title"))
        self.charts_section.setText(t("charts_title"))
        self.export_btn.setText(t("dashboard_export_pdf"))
        self.html_btn.setText(t("export_dashboard_html"))
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
        self.card_roe.value_label.setText("--")
        self.card_cr.value_label.setText("--")
        self.card_npm.value_label.setText("--")
        self.card_de.value_label.setText("--")
        for chart in [self.chart_ratios, self.chart_profitability, self.chart_dupont,
                      self.chart_balance, self.chart_expenses, self.chart_radar,
                      self.chart_zscore, self.chart_liquidity]:
            chart.clear_chart()

    def _draw_ratios_bar(self, ratios):
        """رسم بياني شريطي للنسب المالية"""
        labels = ['Current\nRatio', 'Quick\nRatio', 'ROA', 'ROE', 'Asset\nTurnover']
        keys = ['current_ratio', 'quick_ratio', 'roa', 'roe', 'asset_turnover']
        values = [ratios.get(k, 0) for k in keys]
        colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']
        draw_bar(self.chart_ratios.plot_item, labels, values, colors)

    def _draw_profitability_pie(self, ratios):
        """رسم بياني دائري لنسب الربحية"""
        labels = ['Gross Margin', 'Net Margin', 'ROA', 'ROE']
        keys = ['gross_profit_margin', 'net_profit_margin', 'roa', 'roe']
        values = [max(ratios.get(k, 0), 0) for k in keys]
        colors = ['#27AE60', '#3498DB', '#E74C3C', '#F39C12']
        if sum(values) == 0:
            self.chart_profitability.clear_chart()
        else:
            draw_pie_widget(self.chart_profitability.pie_widget, labels, values, colors)

    def _draw_dupont_waterfall(self, ratios):
        """رسم بياني شريطي لتحليل DuPont"""
        if not state.dupont:
            self.chart_dupont.plot_item.clear()
            t_item = _mk_text_item(t("dash_no_data_dupont"), 0.5, 0.5, size=12)
            self.chart_dupont.plot_item.addItem(t_item)
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
            draw_bar(self.chart_dupont.plot_item, labels, values, colors)

    def _draw_balance_pie(self, data):
        """رسم بياني دائري لهيكل الميزانية"""
        if not data:
            self.chart_balance.clear_chart()
            return

        total_liab = data.get('total_liabilities', 0)
        equity = data.get('equity', 0)

        if total_liab == 0 and equity == 0:
            self.chart_balance.clear_chart()
        else:
            labels = [t("dash_liabilities"), t("dash_equity")]
            values = [total_liab, equity]
            colors = ['#E74C3C', '#3498DB']
            draw_pie_widget(self.chart_balance.pie_widget, labels, values, colors)

    def _draw_expenses_pie(self, data):
        """رسم بياني دائري لتوزيع المصروفات"""
        if not data:
            self.chart_expenses.clear_chart()
            return

        cogs = data.get('cost_of_goods_sold', 0)
        gross = data.get('gross_profit', 0)
        net = data.get('net_income', 0)
        opex = max(gross - net, 0) if gross > 0 else 0

        if cogs == 0 and opex == 0:
            self.chart_expenses.clear_chart()
        else:
            labels = [t("dash_cogs"), t("dash_opex"), t("dash_net_profit")]
            values = [cogs, opex, max(net, 0)]
            colors = ['#E74C3C', '#F39C12', '#2ECC70']
            filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
            if filtered:
                f_labels, f_values, f_colors = zip(*filtered)
                draw_pie_widget(self.chart_expenses.pie_widget, list(f_labels), list(f_values), list(f_colors))
            else:
                self.chart_expenses.clear_chart()

    def _draw_radar(self, ratios):
        categories = ['ROE', 'ROA', 'NPM', 'Current\nRatio', 'Quick\nRatio', 'Asset\nTurnover']
        keys = ['roe', 'roa', 'net_profit_margin', 'current_ratio', 'quick_ratio', 'asset_turnover']
        raw_values = [max(ratios.get(k, 0), 0) for k in keys]
        max_ref = [25, 15, 25, 3, 2.5, 2]
        values = [min(r / m * 100, 100) for r, m in zip(raw_values, max_ref)]
        draw_radar(self.chart_radar.polar_widget, categories, [values], colors_list=["#3498DB"])

    def _draw_zscore_gauge(self):
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

        zones = [('#E74C3C', 'Danger'), ('#F39C12', 'Grey'), ('#2ECC71', 'Safe')]
        shifted_z = z + 3
        draw_gauge(self.chart_zscore.plot_item, shifted_z, zones, max_val=8)
        t_val = _mk_text_item(f"Z-Score = {z:.2f}", 4, 0.3, color=color, bold=True, size=11)
        self.chart_zscore.plot_item.addItem(t_val)
        t_cls = _mk_text_item(classification.upper(), 4, -0.3, color=color, bold=False, size=10)
        self.chart_zscore.plot_item.addItem(t_cls)

    def _draw_liquidity_chart(self, data):
        if not data:
            self.chart_liquidity.plot_item.clear()
            t_item = _mk_text_item(t("dash_no_data_chart"), 0.5, 0.5, size=12)
            self.chart_liquidity.plot_item.addItem(t_item)
            return

        ca = data.get('current_assets', 0)
        inv = data.get('inventory', 0)
        cl = data.get('current_liabilities', 0)
        qa = max(ca - inv, 0)

        labels = [t("dash_current_assets"), t("dash_inventory"), t("dash_quick_assets"), t("dash_current_liab")]
        values = [ca, inv, qa, cl]
        colors = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12']
        draw_horizontal_bar(self.chart_liquidity.plot_item, labels, values, colors)
