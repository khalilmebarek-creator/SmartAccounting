# واجهة الرؤى الذكية (AI Insights)
# ================================
# تنبؤات + كشف شذوذ + أنماط + توصيات + تنبيهات ذكية

from ui.views._path import _  # noqa: F401

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_pdf import PdfPages

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, QListWidget,
    QMessageBox, QFileDialog, QHeaderView
)
from PyQt5.QtCore import Qt

from ui.views._base import BaseView
from ui.views.dashboard import ChartWidget, _chart_text_color
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from modules.ai_insights import ai_insights_engine
from modules.advanced_dashboard import _MONTHLY_WEIGHTS

_RISK_LABEL_KEYS = {
    "volatility": "ai_msg_risk_volatility",
    "max_drawdown": "ai_msg_risk_max_drawdown",
    "negative_months": "ai_msg_risk_negative_months",
}

_MONTH_KEYS = [
    "tax_month_jan", "tax_month_feb", "tax_month_mar", "tax_month_apr",
    "tax_month_may", "tax_month_jun", "tax_month_jul", "tax_month_aug",
    "tax_month_sep", "tax_month_oct", "tax_month_nov", "tax_month_dec",
]


def _plain_title(text):
    """إزالة الرموز التعبيرية من عناوين الرسوم (غير مدعومة في matplotlib)"""
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


def _build_monthly_series(financial_data):
    """بناء سلسلة شهرية (12 شهراً) من البيانات السنوية"""
    fd = financial_data or {}
    weights = _MONTHLY_WEIGHTS
    revenue = fd.get("revenue", 0) or 0
    opex = fd.get("operating_expenses", 0) or 0
    net = fd.get("net_income", 0) or 0
    return (
        [round(revenue * w) for w in weights],
        [round(opex * w) for w in weights],
        [round(net * w) for w in weights],
    )


class AIInsightsView(BaseView):
    """الرؤى الذكية المدعومة بالتعلم الآلي"""

    def __init__(self):
        super().__init__()
        self._result = None
        self._revenue_series = []
        self._expense_series = []
        self._profit_series = []
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        """بناء الواجهة"""
        self.title_label = self._make_header("ai_title", "ai_subtitle")

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.method_label = QLabel(t("ai_method"))
        controls.addWidget(self.method_label)

        self.method_combo = QComboBox()
        self.method_combo.setMinimumWidth(160)
        self.method_combo.addItems([
            t("ai_method_linear"),
            t("ai_method_moving_average"),
            t("ai_method_exp_smoothing"),
        ])
        controls.addWidget(self.method_combo)

        self.months_label = QLabel(t("ai_months"))
        controls.addWidget(self.months_label)

        self.months_combo = QComboBox()
        self.months_combo.addItems(["3", "6"])
        self.months_combo.setCurrentText("6")
        controls.addWidget(self.months_combo)

        self.analyze_btn = QPushButton(t("ai_analyze_btn"))
        self.analyze_btn.setObjectName("primaryBtn")
        self.analyze_btn.setMinimumHeight(36)
        self.analyze_btn.clicked.connect(self.refresh)
        controls.addWidget(self.analyze_btn)

        controls.addStretch()

        self.export_pdf_btn = QPushButton(t("ai_export_pdf"))
        self.export_pdf_btn.setObjectName("secondaryBtn")
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        controls.addWidget(self.export_pdf_btn)

        self.export_excel_btn = QPushButton(t("ai_export_excel"))
        self.export_excel_btn.setObjectName("secondaryBtn")
        self.export_excel_btn.clicked.connect(self._export_excel)
        controls.addWidget(self.export_excel_btn)

        self._main_layout.addLayout(controls)

        self.no_data_label = QLabel(t("ai_no_data"))
        self.no_data_label.setObjectName("card")
        self.no_data_label.setWordWrap(True)
        self.no_data_label.setAlignment(Qt.AlignCenter)
        self.no_data_label.setMinimumHeight(100)
        self.no_data_label.setStyleSheet("padding: 20px; font-size: 14px;")
        self.no_data_label.hide()
        self._main_layout.addWidget(self.no_data_label)

        self.tabs = QTabWidget()
        self._build_forecast_tab()
        self._build_anomaly_tab()
        self._build_patterns_tab()
        self._build_recommendations_tab()
        self._build_alerts_tab()
        self._main_layout.addWidget(self.tabs, 1)
        self._set_headers()

    def _set_headers(self):
        self.fc_table.setHorizontalHeaderLabels([
            t("ai_fc_period"), t("ai_fc_value"), t("ai_fc_lower"), t("ai_fc_upper"),
        ])
        self.an_series_table.setHorizontalHeaderLabels([
            t("ai_an_index"), t("ai_an_amount"), t("ai_an_expected"),
            t("ai_an_zscore"), t("ai_an_severity"),
        ])
        self.an_tx_table.setHorizontalHeaderLabels([
            t("ai_an_amount"), t("ai_an_description"), t("ai_an_score"),
            t("ai_an_severity"),
        ])
        self.pat_risk_table.setHorizontalHeaderLabels([
            t("ai_pat_risk"), t("ai_pat_h_value"), t("ai_pat_h_level"),
        ])
        self.rec_table.setHorizontalHeaderLabels([
            t("ai_rec_category"), t("ai_rec_h_title"), t("ai_rec_priority"),
        ])

    # ===== Forecasting tab =====

    def _build_forecast_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        self.fc_chart_revenue = ChartWidget("")
        self.fc_chart_expenses = ChartWidget("")
        self.fc_chart_profit = ChartWidget("")
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.addWidget(self.fc_chart_revenue, 0, 0)
        grid.addWidget(self.fc_chart_expenses, 0, 1)
        grid.addWidget(self.fc_chart_profit, 1, 0)
        layout.addLayout(grid)

        growth_row = QHBoxLayout()
        growth_row.setSpacing(10)
        self.fc_growth_revenue = QLabel("--")
        self.fc_growth_revenue.setObjectName("cardValue")
        self.fc_growth_expenses = QLabel("--")
        self.fc_growth_expenses.setObjectName("cardValue")
        self.fc_growth_profit = QLabel("--")
        self.fc_growth_profit.setObjectName("cardValue")
        growth_row.addWidget(self._growth_box(t("ai_fc_sales"), self.fc_growth_revenue))
        growth_row.addWidget(self._growth_box(t("ai_fc_expenses"), self.fc_growth_expenses))
        growth_row.addWidget(self._growth_box(t("ai_fc_profit"), self.fc_growth_profit))
        layout.addLayout(growth_row)

        self.fc_table = QTableWidget(0, 4)
        self.fc_table.setObjectName("dataTable")
        self.fc_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.fc_table)

        self.tabs.addTab(tab, t("ai_fc_tab"))

    def _growth_box(self, title, value_label):
        from PyQt5.QtWidgets import QFrame
        frame = QFrame()
        frame.setObjectName("card")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 10, 16, 10)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 11px; color: #888;")
        v.addWidget(lbl)
        v.addWidget(value_label)
        return frame

    # ===== Anomaly tab =====

    def _build_anomaly_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        self.an_series_title = QLabel(t("ai_an_series"))
        self.an_series_title.setObjectName("sectionTitle")
        layout.addWidget(self.an_series_title)

        self.an_series_table = QTableWidget(0, 5)
        self.an_series_table.setObjectName("dataTable")
        self.an_series_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.an_series_table)

        self.an_tx_title = QLabel(t("ai_an_transactions"))
        self.an_tx_title.setObjectName("sectionTitle")
        layout.addWidget(self.an_tx_title)

        self.an_tx_table = QTableWidget(0, 4)
        self.an_tx_table.setObjectName("dataTable")
        self.an_tx_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.an_tx_table)

        layout.addStretch()
        self.tabs.addTab(tab, t("ai_an_tab"))

    # ===== Patterns tab =====

    def _build_patterns_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        info_row = QHBoxLayout()
        info_row.setSpacing(10)
        self.pat_trend = QLabel("--")
        self.pat_trend.setObjectName("cardValue")
        self.pat_season = QLabel("--")
        self.pat_season.setObjectName("cardValue")
        self.pat_cycle = QLabel("--")
        self.pat_cycle.setObjectName("cardValue")
        info_row.addWidget(self._growth_box(t("ai_pat_trend"), self.pat_trend))
        info_row.addWidget(self._growth_box(t("ai_pat_seasonality"), self.pat_season))
        info_row.addWidget(self._growth_box(t("ai_pat_cyclical"), self.pat_cycle))
        layout.addLayout(info_row)

        self.chart_seasonality = ChartWidget("")
        self.chart_seasonality.title_label.hide()
        layout.addWidget(self.chart_seasonality)

        self.pat_risk_title = QLabel(t("ai_pat_risk"))
        self.pat_risk_title.setObjectName("sectionTitle")
        layout.addWidget(self.pat_risk_title)

        self.pat_risk_table = QTableWidget(0, 3)
        self.pat_risk_table.setObjectName("dataTable")
        self.pat_risk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.pat_risk_table)

        self.tabs.addTab(tab, t("ai_pat_tab"))

    # ===== Recommendations tab =====

    def _build_recommendations_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        self.rec_table = QTableWidget(0, 3)
        self.rec_table.setObjectName("dataTable")
        self.rec_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.rec_table)

        layout.addStretch()
        self.tabs.addTab(tab, t("ai_rec_tab"))

    # ===== Alerts tab =====

    def _build_alerts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        self.alerts_list = QListWidget()
        self.alerts_list.setObjectName("dataTable")
        layout.addWidget(self.alerts_list)

        layout.addStretch()
        self.tabs.addTab(tab, t("ai_alert_tab"))

    # ===== Analysis =====

    def _method(self):
        idx = self.method_combo.currentIndex()
        return ["linear", "moving_average", "exp_smoothing"][idx if 0 <= idx < 3 else 0]

    def _months(self):
        return int(self.months_combo.currentText())

    def refresh(self):
        """إعادة التحليل الذكي"""
        if not state.has_data():
            self._result = None
            self._clear_tables()
            self.no_data_label.show()
            self.tabs.hide()
            return

        self.no_data_label.hide()
        self.tabs.show()

        self._revenue_series, self._expense_series, self._profit_series = _build_monthly_series(
            state.financial_data
        )
        ratios = state.ratios or {}
        result = ai_insights_engine.generate_insights(
            revenue_history=self._revenue_series,
            expense_history=self._expense_series,
            profit_history=self._profit_series,
            transactions=None,
            ratios=ratios,
            months=self._months(),
            method=self._method(),
        )
        self._result = result
        self._draw_forecasts(result["forecasts"])
        self._fill_anomalies(result["anomalies"])
        self._fill_patterns(result["patterns"])
        self._fill_recommendations(result["recommendations"])
        self._fill_alerts(result["alerts"])

    def _clear_tables(self):
        for table in (self.fc_table, self.an_series_table, self.an_tx_table,
                      self.pat_risk_table, self.rec_table):
            table.setRowCount(0)
        self.alerts_list.clear()
        self.fc_growth_revenue.setText("--")
        self.fc_growth_expenses.setText("--")
        self.fc_growth_profit.setText("--")
        self.pat_trend.setText("--")
        self.pat_season.setText("--")
        self.pat_cycle.setText("--")
        self._clear_chart(self.fc_chart_revenue)
        self._clear_chart(self.fc_chart_expenses)
        self._clear_chart(self.fc_chart_profit)
        self._clear_chart(self.chart_seasonality)

    def _clear_chart(self, chart):
        chart.clear_chart()

    def _draw_forecasts(self, forecasts):
        self._draw_forecast_chart(self.fc_chart_revenue, t("ai_fc_sales"),
                                  self._revenue_series, forecasts.get("revenue", {}))
        self._draw_forecast_chart(self.fc_chart_expenses, t("ai_fc_expenses"),
                                  self._expense_series, forecasts.get("expenses", {}))
        self._draw_forecast_chart(self.fc_chart_profit, t("ai_fc_profit"),
                                  self._profit_series, forecasts.get("profit", {}))

        self.fc_growth_revenue.setText(f"{forecasts.get('revenue', {}).get('growth_rate_pct', 0):+.2f}%")
        self.fc_growth_expenses.setText(f"{forecasts.get('expenses', {}).get('growth_rate_pct', 0):+.2f}%")
        self.fc_growth_profit.setText(f"{forecasts.get('profit', {}).get('growth_rate_pct', 0):+.2f}%")

        periods = forecasts.get("revenue", {}).get("forecast", [])
        self.fc_table.setRowCount(len(periods))
        for row, p in enumerate(periods):
            self.fc_table.setItem(row, 0, QTableWidgetItem(str(p.get("period", ""))))
            self._set_money(self.fc_table, row, 1, p.get("value", 0))
            conf = forecasts.get("revenue", {}).get("confidence", [])
            if row < len(conf):
                self._set_money(self.fc_table, row, 2, conf[row].get("lower", 0))
                self._set_money(self.fc_table, row, 3, conf[row].get("upper", 0))

    def _draw_forecast_chart(self, chart, title, history, fc):
        if not history:
            chart.set_title(title)
            self._clear_chart(chart)
            return
        fig = chart.figure
        fig.clear()
        ax = fig.add_subplot(111)
        text_color = _chart_text_color()
        bg = ThemeColors.get("chart_bg")
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
        ax.tick_params(colors=text_color)
        for spine in ax.spines.values():
            spine.set_color(text_color)

        x_hist = list(range(1, len(history) + 1))
        n = len(history)
        forecast = fc.get("forecast", [])
        conf = fc.get("confidence", [])
        x_fc = [n + i + 1 for i in range(len(forecast))]

        ax.plot(x_hist, history, color="#2196F3", marker="o", linewidth=1.5)
        if x_fc and forecast:
            ax.plot(x_fc, [p["value"] for p in forecast], color="#E74C3C",
                    marker="s", linestyle="--", linewidth=1.5, label=_plain_title(title))
            lower = [c["lower"] for c in conf]
            upper = [c["upper"] for c in conf]
            ax.fill_between(x_fc, lower, upper, color="#E74C3C", alpha=0.15,
                            label=_plain_title(t("ai_fc_confidence")))
        ax.set_title(_plain_title(title), color=text_color)
        ax.legend(loc="upper left", fontsize=8, labelcolor=text_color)
        ax.grid(True, alpha=0.3)
        chart.canvas.draw()
        chart.set_title(title)

    def _fill_anomalies(self, anomalies):
        series = anomalies.get("profit", [])
        self.an_series_table.setRowCount(len(series))
        for row, a in enumerate(series):
            self.an_series_table.setItem(row, 0, QTableWidgetItem(str(a.get("index", ""))))
            self._set_money(self.an_series_table, row, 1, a.get("value", 0))
            self._set_money(self.an_series_table, row, 2, a.get("expected", 0))
            self.an_series_table.setItem(row, 3, QTableWidgetItem(str(a.get("z_score", ""))))
            self.an_series_table.setItem(row, 4, QTableWidgetItem(a.get("severity", "")))

        tx = anomalies.get("transactions", [])
        self.an_tx_table.setRowCount(len(tx))
        for row, a in enumerate(tx):
            self._set_money(self.an_tx_table, row, 0, a.get("amount", 0))
            self.an_tx_table.setItem(row, 1, QTableWidgetItem(a.get("description", "")))
            self.an_tx_table.setItem(row, 2, QTableWidgetItem(str(a.get("score", ""))))
            self.an_tx_table.setItem(row, 3, QTableWidgetItem(a.get("severity", "")))

    def _fill_patterns(self, patterns):
        trend = patterns.get("trend", {})
        direction = trend.get("direction", "flat")
        direction_text = t(f"ai_pat_{direction}")
        self.pat_trend.setText(f"{direction_text} — {trend.get('growth_rate_pct', 0):+.2f}%")

        season = patterns.get("seasonality", {})
        peak = season.get("peak_month")
        trough = season.get("trough_month")
        season_text = t("ai_pat_flat")
        if peak and trough:
            peak_text = t(_MONTH_KEYS[peak - 1]) if 1 <= peak <= 12 else str(peak)
            trough_text = t(_MONTH_KEYS[trough - 1]) if 1 <= trough <= 12 else str(trough)
            season_text = f"{t('ai_pat_peak_month')}: {peak_text} / {t('ai_pat_trough_month')}: {trough_text}"
        self.pat_season.setText(season_text)

        cycle = patterns.get("cyclical", {})
        self.pat_cycle.setText(f"{t('ai_pat_cycle_length')}: {cycle.get('cycle_length', '—')}")

        indexes = season.get("indexes", [])
        self._draw_seasonality(indexes, t("ai_pat_seasonality"))

        risks = patterns.get("risk_indicators", [])
        self.pat_risk_table.setRowCount(len(risks))
        for row, r in enumerate(risks):
            key = _RISK_LABEL_KEYS.get(r.get("name", ""), "ai_pat_risk")
            self.pat_risk_table.setItem(row, 0, QTableWidgetItem(t(key)))
            self.pat_risk_table.setItem(row, 1, QTableWidgetItem(str(r.get("value", ""))))
            self.pat_risk_table.setItem(row, 2, QTableWidgetItem(r.get("level", "")))

    def _draw_seasonality(self, indexes, title):
        if not indexes:
            self._clear_chart(self.chart_seasonality)
            return
        fig = self.chart_seasonality.figure
        fig.clear()
        ax = fig.add_subplot(111)
        text_color = _chart_text_color()
        bg = ThemeColors.get("chart_bg")
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
        ax.tick_params(colors=text_color)
        for spine in ax.spines.values():
            spine.set_color(text_color)
        labels = [t(k) for k in _MONTH_KEYS[:len(indexes)]]
        bars = ax.bar(range(1, len(indexes) + 1), indexes, color="#8E44AD", alpha=0.8)
        ax.axhline(1.0, color=text_color, linestyle="--", alpha=0.5)
        ax.set_title(_plain_title(title), color=text_color)
        ax.set_xticks(range(1, len(indexes) + 1))
        ax.set_xticklabels([_plain_title(l) for l in labels], rotation=45, fontsize=7, color=text_color)
        ax.grid(True, alpha=0.3)
        self.chart_seasonality.canvas.draw()

    def _fill_recommendations(self, recs):
        self.rec_table.setRowCount(len(recs))
        for row, r in enumerate(recs):
            cat_key = f"ai_cat_{r.get('category', '')}"
            self.rec_table.setItem(row, 0, QTableWidgetItem(t(cat_key) if cat_key in _KEYS else r.get("category", "")))
            title = r.get("title", "")
            msg_key = f"ai_msg_{title}"
            self.rec_table.setItem(row, 1, QTableWidgetItem(t(msg_key) if msg_key in _KEYS else title))
            self.rec_table.setItem(row, 2, QTableWidgetItem(t(f"ai_priority_{r.get('priority', 'medium')}")))

    def _fill_alerts(self, alerts):
        self.alerts_list.clear()
        for a in alerts:
            type_key = f"ai_type_{a.get('type', '')}"
            msg_key = f"ai_msg_{a.get('message', '')}"
            type_text = t(type_key) if type_key in _KEYS else a.get("type", "")
            msg_text = t(msg_key) if msg_key in _KEYS else a.get("message", "")
            sev = a.get("severity", "low")
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev, "⚪")
            self.alerts_list.addItem(f"{icon} [{type_text}] {msg_text}")

    # ===== helpers =====

    def _set_money(self, table, row, col, value):
        item = QTableWidgetItem(f"{value:,.2f}")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(row, col, item)

    # ===== export =====

    def _export_pdf(self):
        if self._result is None:
            QMessageBox.warning(self, t("warning"), t("ai_no_data"))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t("ai_export_pdf"), "ai_insights.pdf", "PDF Files (*.pdf)"
        )
        if not file_path:
            return
        try:
            charts = [self.fc_chart_revenue, self.fc_chart_expenses,
                      self.fc_chart_profit, self.chart_seasonality]
            with PdfPages(file_path) as pdf:
                for chart in charts:
                    if chart.isVisible():
                        pdf.savefig(chart.figure, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, t("success"), f"✅ {t('ai_export_success')}\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _export_excel(self):
        if self._result is None:
            QMessageBox.warning(self, t("warning"), t("ai_no_data"))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, t("ai_export_excel"), "ai_insights.xlsx", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return
        try:
            self._write_excel(file_path)
            QMessageBox.information(self, t("success"), f"✅ {t('ai_export_success')}\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _write_excel(self, file_path):
        from ui.exporters import add_excel_sheet, new_workbook

        wb = new_workbook()

        forecast_rows = []
        for metric, key in (("Revenue", "revenue"), ("Expenses", "expenses"), ("Profit", "profit")):
            fc = self._result["forecasts"].get(key, {})
            for row, p in enumerate(fc.get("forecast", [])):
                conf = fc.get("confidence", [])
                forecast_rows.append(
                    [metric, p.get("period", ""), p.get("value", 0),
                     conf[row].get("lower", 0) if row < len(conf) else 0,
                     conf[row].get("upper", 0) if row < len(conf) else 0,
                     fc.get("growth_rate_pct", 0)])
        add_excel_sheet(wb, "Forecasts",
                        ["Metric", "Period", "Forecast", "Lower", "Upper", "Growth%"],
                        forecast_rows)

        anomaly_rows = []
        for a in self._result["anomalies"].get("profit", []):
            anomaly_rows.append(["profit", a.get("value", ""), a.get("expected", ""),
                                 a.get("z_score", ""), a.get("severity", "")])
        for a in self._result["anomalies"].get("transactions", []):
            anomaly_rows.append(["transaction", a.get("amount", ""), "", a.get("score", ""),
                                 a.get("severity", "")])
        add_excel_sheet(wb, "Anomalies",
                        ["Kind", "Value", "Expected", "Score", "Severity"],
                        anomaly_rows)

        add_excel_sheet(
            wb, "Recommendations",
            ["Category", "Title", "Priority"],
            [[r.get("category", ""), r.get("title", ""), r.get("priority", "")]
             for r in self._result["recommendations"]],
        )

        add_excel_sheet(
            wb, "Alerts",
            ["Type", "Severity", "Message"],
            [[a.get("type", ""), a.get("severity", ""), a.get("message", "")]
             for a in self._result["alerts"]],
        )

        wb.save(file_path)

    # ===== language =====

    def retranslate(self):
        """تحديث النصوص عند تغيير اللغة"""
        self.title_label.setText(t("ai_title"))
        self.method_label.setText(t("ai_method"))
        current_method = self.method_combo.currentIndex()
        self.method_combo.clear()
        self.method_combo.addItems([
            t("ai_method_linear"),
            t("ai_method_moving_average"),
            t("ai_method_exp_smoothing"),
        ])
        self.method_combo.setCurrentIndex(current_method)
        self.months_label.setText(t("ai_months"))
        self.analyze_btn.setText(t("ai_analyze_btn"))
        self.export_pdf_btn.setText(t("ai_export_pdf"))
        self.export_excel_btn.setText(t("ai_export_excel"))

        self.fc_chart_revenue.set_title(t("ai_fc_sales"))
        self.fc_chart_expenses.set_title(t("ai_fc_expenses"))
        self.fc_chart_profit.set_title(t("ai_fc_profit"))
        self.an_series_title.setText(t("ai_an_series"))
        self.an_tx_title.setText(t("ai_an_transactions"))
        self.pat_risk_title.setText(t("ai_pat_risk"))

        current_tab = self.tabs.currentIndex()
        self.tabs.setTabText(0, t("ai_fc_tab"))
        self.tabs.setTabText(1, t("ai_an_tab"))
        self.tabs.setTabText(2, t("ai_pat_tab"))
        self.tabs.setTabText(3, t("ai_rec_tab"))
        self.tabs.setTabText(4, t("ai_alert_tab"))
        self.tabs.setCurrentIndex(current_tab)
        self._set_headers()

        self.refresh()


from ui.resources.i18n import LANGUAGES as _KEYS_DICT
_KEYS = set(_KEYS_DICT["en"]) | set(_KEYS_DICT["ar"]) | set(_KEYS_DICT["fr"])
