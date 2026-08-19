# عرض تحليل DuPont
# ==================

from ui.views._path import _  # noqa: F401 — ensures project root on sys.path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QPushButton,
    QComboBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import pyqtgraph as pg
from ui.charts import (PgChartWidget,
    draw_waterfall, draw_line, draw_bar, draw_grouped_bar, draw_gauge,
    _text_color, _edge_color, _chart_bg, _hex_to_rgb, _mk_brush, _mk_pen, _mk_text_item)

from ui.app_state import state
from ui.resources.i18n import t
from ui.plotly_export import export_analysis_html
from modules import FinancialAnalyzer, ReportGenerator
from modules.benchmarks import benchmark_analyzer
from database.db_operations import get_company_dupont_history


class ChartWidget(PgChartWidget):

    def set_title(self, title):
        self.title_label.setText(title)

    def clear_chart(self):
        self.plot_item.clear()


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

        self._build_header(content_layout)
        self._build_equation(content_layout)
        self._build_components(content_layout)
        self._build_charts(content_layout)
        self._build_interpretation(content_layout)
        self._build_industry(content_layout)
        self._build_recommendations(content_layout)
        self._build_working_capital(content_layout)
        self._build_export(content_layout)

        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        self._fill_sector_combo()
    def _build_header(self, content_layout):
        """العنوان"""

        # العنوان
        self.title = QLabel(t("analysis_title"))
        self.title.setObjectName("headerTitle")
        content_layout.addWidget(self.title)

        self.subtitle = QLabel(t("analysis_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        content_layout.addWidget(self.subtitle)

    def _build_equation(self, content_layout):
        """معادلة DuPont"""

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
        self.equation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.equation_label.setStyleSheet("padding: 15px;")
        self.equation_label.setObjectName("equationLabel")
        equation_layout.addWidget(self.equation_label)

        content_layout.addWidget(equation_frame)

    def _build_components(self, content_layout):
        """مكونات DuPont"""

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

    def _build_charts(self, content_layout):
        """الرسوم البيانية"""

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

    def _build_interpretation(self, content_layout):
        """التفسير"""

        # ===== التفسير =====
        self.interpretation_title = QLabel(t("ana_interpretation"))
        self.interpretation_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.interpretation_title)

        self.interpretation_frame = QFrame()
        self.interpretation_frame.setObjectName("card")
        interp_layout = QVBoxLayout(self.interpretation_frame)

        self.interp_label = QLabel("--")
        self.interp_label.setWordWrap(True)
        self.interp_label.setTextFormat(Qt.TextFormat.RichText)
        self.interp_label.setStyleSheet("font-size: 11pt;")
        interp_layout.addWidget(self.interp_label)

        content_layout.addWidget(self.interpretation_frame)

    def _build_industry(self, content_layout):
        """مقارنة القطاع"""

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

    def _build_recommendations(self, content_layout):
        """التوصيات"""

        # ===== التوصيات =====
        self.rec_title = QLabel(t("ana_recommendations"))
        self.rec_title.setObjectName("sectionTitle")
        content_layout.addWidget(self.rec_title)

        self.rec_frame = QFrame()
        self.rec_frame.setObjectName("card")
        self.rec_layout = QVBoxLayout(self.rec_frame)
        self.rec_layout.setSpacing(8)
        content_layout.addWidget(self.rec_frame)

    def _build_working_capital(self, content_layout):
        """رأس المال العامل"""

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

    def _build_export(self, content_layout):
        """زر التصدير"""

        # ===== زر التصدير =====
        export_row = QHBoxLayout()
        export_row.addStretch()
        self.export_btn = QPushButton(t("ana_export_pdf"))
        self.export_btn.setObjectName("pdfBtn")
        self.export_btn.setMinimumWidth(220)
        self.export_btn.clicked.connect(self.export_pdf)
        export_row.addWidget(self.export_btn)
        self.html_btn = QPushButton(t("export_analysis_html"))
        self.html_btn.setObjectName("secondaryBtn")
        self.html_btn.setMinimumWidth(220)
        self.html_btn.clicked.connect(self._export_html)
        export_row.addWidget(self.html_btn)
        content_layout.addLayout(export_row)

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
        layout.setSpacing(8)
        layout.setContentsMargins(16, 12, 16, 12)

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
        self.html_btn.setText(t("export_analysis_html"))
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
            chart.plot_item.clear()

    def _draw_waterfall(self):
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

        draw_waterfall(self.chart_waterfall.plot_item, labels, values)

    def _draw_trend(self):
        history = []
        if state.company_name:
            try:
                history = get_company_dupont_history(state.company_name)
            except Exception:
                history = []

        if not history:
            self.chart_trend.plot_item.clear()
            txt = _mk_text_item(t("ana_no_history"), 0, 0, size=10, anchor=(0.5, 0.5))
            self.chart_trend.plot_item.addItem(txt)
            return

        years = [h['year'] for h in history]
        roe = [h['roe'] for h in history]
        npm = [h['net_profit_margin'] for h in history]
        at = [h['asset_turnover'] for h in history]
        em = [h['equity_multiplier'] for h in history]

        draw_line(self.chart_trend.plot_item, years,
                  [roe, npm, at, em],
                  labels=[t("ana_waterfall_total"), t("ana_industry_npm"),
                          t("ana_industry_at"), t("ana_industry_em")],
                  colors=['#F39C12', '#3498DB', '#2ECC71', '#9B59B6'])

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
        roe = state.dupont.get('roe', 0)
        sector_avg = self._sector_roe_average()

        top = max(roe, sector_avg if sector_avg else 0, 20) * 1.25
        if top <= 0:
            top = 25

        zones = [
            ('#E74C3C', ''),
            ('#F39C12', ''),
            ('#2ECC71', ''),
        ]
        draw_gauge(self.chart_gauge.plot_item, roe, zones, max_val=top)

        if sector_avg is not None:
            indicator = pg.InfiniteLine(pos=(sector_avg, 0), angle=90,
                                        pen=_mk_pen('#8E44AD', width=3))
            self.chart_gauge.plot_item.addItem(indicator)
            lbl = _mk_text_item(
                f"{t('ana_gauge_sector')}: {sector_avg:.1f}%",
                sector_avg, 0.7, color='#8E44AD', size=8, anchor=(0.5, 1.0))
            self.chart_gauge.plot_item.addItem(lbl)

    def _draw_industry(self):
        if not self._has_data():
            self.chart_industry.plot_item.clear()
            self.industry_summary.setText(t("ana_industry_no_sector"))
            return

        if not self._sector_code:
            self.chart_industry.plot_item.clear()
            txt = _mk_text_item(t("ana_industry_no_sector"), 0, 0, size=11, anchor=(0.5, 0.5))
            self.chart_industry.plot_item.addItem(txt)
            self.industry_summary.setText("")
            return

        industry = self.analyzer.dupont_industry_comparison(state.dupont, self._sector_code)

        components = ['roe', 'net_profit_margin', 'asset_turnover', 'equity_multiplier']
        label_map = {
            'roe': t('ana_industry_roe'),
            'net_profit_margin': t('ana_industry_npm'),
            'asset_turnover': t('ana_industry_at'),
            'equity_multiplier': t('ana_industry_em'),
        }

        status_text = {'above': t('ana_status_above'), 'below': t('ana_status_below'),
                       'aligned': t('ana_status_aligned'), 'n/a': '—'}

        company_vals = []
        sector_vals = []
        groups = []
        summary_lines = []
        for component in components:
            cmp_data = industry.get(component, {})
            company_val = cmp_data.get('company_value', 0)
            sector_val = cmp_data.get('sector_average', 0)
            status = cmp_data.get('status', 'n/a')

            company_vals.append(company_val)
            sector_vals.append(sector_val)
            groups.append(label_map[component])

            summary_lines.append(
                f"{label_map[component]}: {company_val:.2f} vs {sector_val:.2f} — {status_text.get(status, '—')}"
            )

        series_data = [
            {'label': t('ana_industry_company'), 'values': company_vals, 'color': '#95A5A6'},
            {'label': t('ana_industry_avg'), 'values': sector_vals, 'color': '#3498DB'},
        ]
        draw_grouped_bar(self.chart_industry.plot_item, groups, series_data)
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

    def _export_html(self):
        if not self._has_data():
            QMessageBox.warning(self, t("analysis_title"), t("ana_export_empty"))
            return
        default_name = f"analysis_{state.company_name or 'Company'}_{state.fiscal_year}.html"
        filename, _ = QFileDialog.getSaveFileName(
            self, t("export_analysis_html"), default_name, "HTML (*.html)"
        )
        if not filename:
            return
        dp = state.dupont
        waterfall = self.analyzer.dupont_waterfall(
            dp.get('net_profit_margin', 0),
            dp.get('asset_turnover', 0),
            dp.get('equity_multiplier', 0)
        )
        charts_data = {
            'waterfall': {
                'labels': [
                    t("ana_waterfall_base"), t("ana_waterfall_at"),
                    t("ana_waterfall_em"), t("ana_waterfall_total"),
                ],
                'values': [
                    waterfall['base'], waterfall['turnover_effect'],
                    waterfall['leverage_effect'], waterfall['total'],
                ],
            },
            'gauge': {
                'value': dp.get('roe', 0),
                'zones': [],
            },
            'industry': {
                'groups': [],
                'series': [],
            },
        }
        history = []
        if state.company_name:
            try:
                history = get_company_dupont_history(state.company_name)
            except Exception:
                history = []
        if history:
            charts_data['trend'] = {
                'x': [h['year'] for h in history],
                'series': [
                    {'name': t("ana_waterfall_total"), 'y': [h['roe'] for h in history], 'color': '#F39C12'},
                    {'name': t("ana_industry_npm"), 'y': [h['net_profit_margin'] for h in history], 'color': '#3498DB'},
                    {'name': t("ana_industry_at"), 'y': [h['asset_turnover'] for h in history], 'color': '#2ECC71'},
                    {'name': t("ana_industry_em"), 'y': [h['equity_multiplier'] for h in history], 'color': '#9B59B6'},
                ],
            }
        if self._sector_code:
            industry = self.analyzer.dupont_industry_comparison(dp, self._sector_code)
            components = ['roe', 'net_profit_margin', 'asset_turnover', 'equity_multiplier']
            label_map = {
                'roe': t('ana_industry_roe'),
                'net_profit_margin': t('ana_industry_npm'),
                'asset_turnover': t('ana_industry_at'),
                'equity_multiplier': t('ana_industry_em'),
            }
            groups = [label_map[c] for c in components]
            charts_data['industry'] = {
                'groups': groups,
                'series': [
                    {
                        'name': t('ana_industry_company'),
                        'values': [industry.get(c, {}).get('company_value', 0) for c in components],
                        'color': '#95A5A6',
                    },
                    {
                        'name': t('ana_industry_avg'),
                        'values': [industry.get(c, {}).get('sector_average', 0) for c in components],
                        'color': '#3498DB',
                    },
                ],
            }
        try:
            export_analysis_html(filename, charts_data)
            QMessageBox.information(self, t("analysis_title"), t("ana_export_success"))
        except Exception:
            QMessageBox.critical(self, t("analysis_title"), t("ana_export_error"))
