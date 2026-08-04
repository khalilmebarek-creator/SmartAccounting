from ui.views._path import _  # noqa: F401

import math

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QComboBox, QMessageBox, QScrollArea, QSizePolicy, QCheckBox,
    QLineEdit, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ui.views._base import BaseView
from ui.views.dashboard import ChartWidget, _chart_text_color
from ui.app_state import state, ThemeColors
from ui import exporters
from ui.resources.i18n import t
from modules.advanced_dashboard import (
    advanced_dashboard_engine, DEFAULT_KPIS, ALL_WIDGETS
)
from modules.benchmarks import benchmark_analyzer
from database.db_operations import (
    get_dashboard_layouts, save_dashboard_layout, delete_dashboard_layout,
    get_company_ratio_history
)

_STATUS_COLORS = {
    "green": "#27AE60",
    "yellow": "#F39C12",
    "red": "#E74C3C",
}

_STATUS_TEXT_KEYS = {
    "green": "advd_status_green",
    "yellow": "advd_status_yellow",
    "red": "advd_status_red",
}

_ACTIVITY_SECTOR_MAP = ["commercial", "industrial", "construction", "services"]

_THEME_COLORS = ["#2196F3", "#27AE60", "#8E44AD", "#E67E22", "#E74C3C", "#16A085"]
_THEME_COLOR_KEYS = {
    "#2196F3": "color_blue",
    "#27AE60": "color_green",
    "#8E44AD": "color_purple",
    "#E67E22": "color_orange",
    "#E74C3C": "color_red",
    "#16A085": "color_teal",
}

_KPI_LABEL_KEYS = {
    "revenue": "advd_kpi_revenue",
    "net_profit": "advd_kpi_net_profit",
    "roe": "advd_kpi_roe",
    "roa": "advd_kpi_roa",
    "liquidity": "advd_kpi_liquidity",
    "debt_ratio": "advd_kpi_debt_ratio",
}

_WIDGET_LABEL_KEYS = {
    "kpi_cards": "advd_widget_kpi_cards",
    "revenue_trend": "advd_widget_revenue_trend",
    "expense_breakdown": "advd_widget_expense_breakdown",
    "profitability_trend": "advd_widget_profitability_trend",
    "ratios_radar": "advd_widget_ratios_radar",
    "alerts": "advd_widget_alerts",
}


def _plain_title(text):
    """إزالة الرموز التعبيرية من عناوين الرسوم (غير مدعومة في matplotlib)"""
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class AdvancedDashboardView(BaseView):
    """لوحة التحكم المتقدمة التفاعلية"""

    def __init__(self):
        super().__init__()
        self._period = "monthly"
        self._accent_color = _THEME_COLORS[0]
        self._widget_frames = {}
        self.setup_ui()
        self._reload_saved_layouts()
        self._auto_refresh_timer = QTimer(self)
        self._auto_refresh_timer.timeout.connect(self.refresh)
        self._auto_refresh_timer.start(30000)
        self.refresh()

    def setup_ui(self):
        """إنشاء الواجهة"""
        self.title_label = self._make_header("advd_title")
        self.subtitle = QLabel(t("advd_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        self._main_layout.addWidget(self.subtitle)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.sector_label = QLabel(t("bench_sector_select"))
        controls.addWidget(self.sector_label)

        self.sector_combo = QComboBox()
        self.sector_combo.setMinimumWidth(200)
        self.sector_combo.setMinimumHeight(36)
        for s in benchmark_analyzer.get_sectors_list():
            self.sector_combo.addItem(s["name_ar"], s["code"])
        self.sector_combo.currentIndexChanged.connect(self._on_sector_changed)
        controls.addWidget(self.sector_combo)

        controls.addStretch()

        self.export_pdf_btn = QPushButton(t("advd_export_pdf"))
        self.export_pdf_btn.setObjectName("secondaryBtn")
        self.export_pdf_btn.setMinimumHeight(36)
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        controls.addWidget(self.export_pdf_btn)

        self.export_excel_btn = QPushButton(t("advd_export_excel"))
        self.export_excel_btn.setObjectName("secondaryBtn")
        self.export_excel_btn.setMinimumHeight(36)
        self.export_excel_btn.clicked.connect(self._export_excel)
        controls.addWidget(self.export_excel_btn)

        self._main_layout.addLayout(controls)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("dashboardScroll")

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(15)

        self._build_health_card()
        self._build_kpi_cards()
        self._build_charts()
        self._build_alerts()
        self._build_customization()

        self.content_layout.addStretch()
        self.scroll.setWidget(content)
        self._main_layout.addWidget(self.scroll, 1)

    def _build_health_card(self):
        """بطاقة درجة الصحة العامة"""
        self.health_frame = QFrame()
        self.health_frame.setObjectName("card")
        hl = QHBoxLayout(self.health_frame)
        hl.setContentsMargins(20, 15, 20, 15)

        self.health_title = QLabel(t("advd_health_score"))
        self.health_title.setObjectName("cardTitle")
        hl.addWidget(self.health_title)
        hl.addStretch()

        self.health_rating = QLabel("")
        self.health_rating.setObjectName("cardSubtitle")
        hl.addWidget(self.health_rating)

        self.health_value = QLabel("--")
        self.health_value.setObjectName("statValue")
        f = QFont()
        f.setBold(True)
        f.setPointSize(20)
        self.health_value.setFont(f)
        hl.addWidget(self.health_value)

        self.content_layout.addWidget(self.health_frame)

    def _build_kpi_cards(self):
        """بطاقات مؤشرات الأداء الرئيسية"""
        self.kpi_container = QWidget()
        kc = QVBoxLayout(self.kpi_container)
        kc.setSpacing(10)

        self.kpi_section = QLabel(t("advd_widget_kpi_cards"))
        self.kpi_section.setObjectName("sectionTitle")
        kc.addWidget(self.kpi_section)

        self.kpi_grid = QGridLayout()
        self.kpi_grid.setSpacing(10)
        self.kpi_cards = {}
        for i, key in enumerate(DEFAULT_KPIS):
            card = self._make_kpi_card(key)
            self.kpi_cards[key] = card
            self.kpi_grid.addWidget(card, i // 3, i % 3)
        kc.addLayout(self.kpi_grid)

        self.content_layout.addWidget(self.kpi_container)
        self._widget_frames["kpi_cards"] = self.kpi_container

    def _make_kpi_card(self, key):
        """كارت مؤشر أداء واحد"""
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        frame.title_label = QLabel(t(_KPI_LABEL_KEYS.get(key, key)))
        frame.title_label.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(frame.title_label)

        frame.value_label = QLabel("--")
        frame.value_label.setObjectName("statValue")
        f = QFont()
        f.setBold(True)
        f.setPointSize(16)
        frame.value_label.setFont(f)
        layout.addWidget(frame.value_label)

        frame.status_label = QLabel("")
        frame.status_label.setObjectName("cardSubtitle")
        layout.addWidget(frame.status_label)

        layout.addStretch()
        return frame

    def _build_charts(self):
        """الرسوم البيانية التفاعلية"""
        self.revenue_box = QFrame()
        self.revenue_box.setObjectName("card")
        rl = QVBoxLayout(self.revenue_box)
        rl.setContentsMargins(15, 15, 15, 15)

        title_row = QHBoxLayout()
        self.chart_revenue_title = QLabel(t("advd_chart_revenue"))
        self.chart_revenue_title.setObjectName("sectionTitle")
        title_row.addWidget(self.chart_revenue_title)
        title_row.addStretch()

        self.period_btn_monthly = QPushButton(t("advd_period_monthly"))
        self.period_btn_monthly.setCheckable(True)
        self.period_btn_monthly.setChecked(True)
        self.period_btn_monthly.clicked.connect(lambda: self._set_period("monthly"))
        title_row.addWidget(self.period_btn_monthly)

        self.period_btn_quarterly = QPushButton(t("advd_period_quarterly"))
        self.period_btn_quarterly.setCheckable(True)
        self.period_btn_quarterly.clicked.connect(lambda: self._set_period("quarterly"))
        title_row.addWidget(self.period_btn_quarterly)

        rl.addLayout(title_row)

        self.chart_revenue = ChartWidget("")
        self.chart_revenue.title_label.hide()
        rl.addWidget(self.chart_revenue)

        self.chart_expense = ChartWidget(t("advd_chart_expense"))
        self.chart_profitability = ChartWidget(t("advd_chart_profitability"))
        self.chart_radar = ChartWidget(t("advd_chart_radar"))

        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)
        charts_grid.addWidget(self.revenue_box, 0, 0)
        charts_grid.addWidget(self.chart_expense, 0, 1)
        charts_grid.addWidget(self.chart_profitability, 1, 0)
        charts_grid.addWidget(self.chart_radar, 1, 1)
        self.content_layout.addLayout(charts_grid)

        self._widget_frames["revenue_trend"] = self.revenue_box
        self._widget_frames["expense_breakdown"] = self.chart_expense
        self._widget_frames["profitability_trend"] = self.chart_profitability
        self._widget_frames["ratios_radar"] = self.chart_radar

    def _build_alerts(self):
        """لوحة التنبيهات والإجراءات"""
        self.alerts_frame = QFrame()
        self.alerts_frame.setObjectName("card")
        al = QVBoxLayout(self.alerts_frame)
        al.setContentsMargins(16, 16, 16, 16)

        self.alerts_title = QLabel(t("advd_alerts_title"))
        self.alerts_title.setObjectName("cardTitle")
        al.addWidget(self.alerts_title)

        self.alerts_list = QListWidget()
        self.alerts_list.setMinimumHeight(140)
        al.addWidget(self.alerts_list)

        self.content_layout.addWidget(self.alerts_frame)
        self._widget_frames["alerts"] = self.alerts_frame

    def _build_customization(self):
        """لوحة التخصيص وحفظ التخطيطات"""
        self.custom_frame = QFrame()
        self.custom_frame.setObjectName("card")
        cl = QVBoxLayout(self.custom_frame)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(10)

        self.custom_title = QLabel(t("advd_custom_title"))
        self.custom_title.setObjectName("cardTitle")
        cl.addWidget(self.custom_title)

        kpis_row = QHBoxLayout()
        kpis_lbl = QLabel(t("advd_custom_kpis"))
        kpis_row.addWidget(kpis_lbl)
        self.kpi_checkboxes = {}
        for key in DEFAULT_KPIS:
            cb = QCheckBox(t(_KPI_LABEL_KEYS.get(key, key)))
            cb.setChecked(True)
            cb.toggled.connect(self._on_customization_changed)
            self.kpi_checkboxes[key] = cb
            kpis_row.addWidget(cb)
        kpis_row.addStretch()
        cl.addLayout(kpis_row)

        widgets_row = QHBoxLayout()
        widgets_lbl = QLabel(t("advd_custom_widgets"))
        widgets_row.addWidget(widgets_lbl)
        self.widget_checkboxes = {}
        for wkey in ALL_WIDGETS:
            cb = QCheckBox(t(_WIDGET_LABEL_KEYS.get(wkey, wkey)))
            cb.setChecked(True)
            cb.toggled.connect(self._on_customization_changed)
            self.widget_checkboxes[wkey] = cb
            widgets_row.addWidget(cb)
        widgets_row.addStretch()
        cl.addLayout(widgets_row)

        theme_row = QHBoxLayout()
        theme_lbl = QLabel(t("advd_custom_theme"))
        theme_row.addWidget(theme_lbl)
        self.color_combo = QComboBox()
        self.color_combo.setMinimumWidth(140)
        for c in _THEME_COLORS:
            self.color_combo.addItem(t(_THEME_COLOR_KEYS.get(c, c)), c)
        self.color_combo.currentIndexChanged.connect(self._on_color_changed)
        theme_row.addWidget(self.color_combo)
        theme_row.addStretch()
        cl.addLayout(theme_row)

        layout_row = QHBoxLayout()
        layout_lbl = QLabel(t("advd_layout_name"))
        layout_row.addWidget(layout_lbl)
        self.layout_name_input = QLineEdit()
        self.layout_name_input.setPlaceholderText(t("advd_layout_name"))
        self.layout_name_input.setMaximumWidth(180)
        layout_row.addWidget(self.layout_name_input)

        self.save_layout_btn = QPushButton(t("advd_layout_save"))
        self.save_layout_btn.clicked.connect(self._save_layout)
        layout_row.addWidget(self.save_layout_btn)

        self.saved_layouts_combo = QComboBox()
        self.saved_layouts_combo.setMinimumWidth(160)
        layout_row.addWidget(self.saved_layouts_combo)

        self.load_layout_btn = QPushButton(t("advd_layout_load"))
        self.load_layout_btn.clicked.connect(self._load_layout)
        layout_row.addWidget(self.load_layout_btn)

        self.delete_layout_btn = QPushButton(t("advd_layout_delete"))
        self.delete_layout_btn.clicked.connect(self._delete_layout)
        layout_row.addWidget(self.delete_layout_btn)

        layout_row.addStretch()
        cl.addLayout(layout_row)

        self.content_layout.addWidget(self.custom_frame)

    # ===== التحديث والرسم =====

    def refresh(self):
        """تحديث كل البيانات والرسوم"""
        if not hasattr(self, "_sector_auto_set"):
            self._sector_auto_set = True
            self.sector_combo.blockSignals(True)
            self._auto_select_sector()
            self.sector_combo.blockSignals(False)

        if not state.has_data():
            self._clear_all()
            return

        fd = state.financial_data or {}
        ratios = state.ratios or {}
        self._update_kpi_cards(fd, ratios)
        self._update_health(fd, ratios)
        self._draw_revenue_trend(fd)
        self._draw_expense_breakdown(fd)
        self._draw_profitability_trend()
        self._draw_radar(ratios)
        self._update_alerts(fd, ratios)

    def _clear_all(self):
        """مسح كل البيانات عند غيابها"""
        self.health_value.setText("--")
        self.health_rating.setText("")
        for key, card in self.kpi_cards.items():
            card.value_label.setText("--")
            card.status_label.setText("")
            card.value_label.setStyleSheet("color: #888;")
        self.alerts_list.clear()
        for chart in (self.chart_revenue, self.chart_expense,
                      self.chart_profitability, self.chart_radar):
            chart.figure.clear()
            plt.close(chart.figure)
            chart.canvas.draw()

    def _update_kpi_cards(self, fd, ratios):
        kpis = {k["key"]: k for k in advanced_dashboard_engine.compute_kpis(fd, ratios)}
        for key, card in self.kpi_cards.items():
            kpi = kpis.get(key)
            if kpi is None:
                card.value_label.setText("--")
                card.status_label.setText("")
                continue
            if kpi["unit"] == "DZD":
                card.value_label.setText(f"{kpi['value']:,.0f} {kpi['unit']}")
            elif kpi["unit"] == "%":
                card.value_label.setText(f"{kpi['value']:.2f}%")
            else:
                card.value_label.setText(f"{kpi['value']:.2f}")
            color = _STATUS_COLORS.get(kpi["status"], "#888")
            card.value_label.setStyleSheet(f"color: {color};")
            card.status_label.setText(t(_STATUS_TEXT_KEYS.get(kpi["status"], "")))

    def _update_health(self, fd, ratios):
        kpis = advanced_dashboard_engine.compute_kpis(fd, ratios)
        health = advanced_dashboard_engine.health_score(kpis)
        self.health_value.setText(f"{health['score']:.0f} / 100")
        self.health_value.setStyleSheet(f"color: {health['color']};")
        self.health_rating.setText(
            health["rating_ar"] if state.language == "ar" else health["rating_en"]
        )

    def _draw_revenue_trend(self, fd):
        fig = self.chart_revenue.figure
        fig.clear()
        ax = fig.add_subplot(111)
        trend = advanced_dashboard_engine.revenue_trend(fd, period=self._period)
        ax.plot(trend["labels"], trend["values"], marker="o", linewidth=2,
                color=self._accent_color)
        ax.fill_between(range(len(trend["values"])), trend["values"],
                        alpha=0.15, color=self._accent_color)
        ax.set_title(_plain_title(t("advd_chart_revenue")), fontsize=11, fontweight="bold", pad=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=8)
        if self._period == "monthly":
            ax.set_xticks(range(len(trend["labels"])))
            ax.set_xticklabels(trend["labels"], rotation=45, ha="right", fontsize=8)
        fig.tight_layout()
        self.chart_revenue.canvas.draw()

    def _draw_expense_breakdown(self, fd):
        fig = self.chart_expense.figure
        fig.clear()
        ax = fig.add_subplot(111)
        e = advanced_dashboard_engine.expense_breakdown(fd)
        labels = [t("advd_expense_cogs"), t("advd_expense_opex"), t("advd_expense_net")]
        values = [max(v, 0) for v in e["values"]]
        colors = ["#E74C3C", "#F39C12", "#2ECC71"]
        if sum(values) == 0:
            ax.text(0.5, 0.5, t("dash_no_data_chart"), ha="center", va="center",
                    color=_chart_text_color(), transform=ax.transAxes)
            ax.axis("off")
        else:
            wedges, texts, autotexts = ax.pie(
                [v for v in values if v > 0],
                labels=[l for l, v in zip(labels, values) if v > 0],
                colors=[c for c, v in zip(colors, values) if v > 0],
                autopct="%1.1f%%", startangle=90, pctdistance=0.75
            )
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_fontweight("bold")
        ax.set_title(_plain_title(t("advd_chart_expense")), fontsize=11, fontweight="bold", pad=10)
        fig.tight_layout()
        self.chart_expense.canvas.draw()

    def _draw_profitability_trend(self):
        fig = self.chart_profitability.figure
        fig.clear()
        ax = fig.add_subplot(111)
        history = get_company_ratio_history(state.company_name)
        trend = advanced_dashboard_engine.profitability_trend(history)
        if not trend["years"]:
            ax.text(0.5, 0.5, t("bench_trend_no_data"), ha="center", va="center",
                    color=_chart_text_color(), transform=ax.transAxes, fontsize=11)
            ax.axis("off")
        else:
            ax.plot(trend["years"], trend["series"]["roe"], marker="o",
                    linewidth=2, label="ROE %", color="#3498DB")
            ax.plot(trend["years"], trend["series"]["net_profit_margin"],
                    marker="s", linewidth=2, label="NPM %", color="#F39C12")
            ax.legend(fontsize=9, loc="best")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        ax.set_title(_plain_title(t("advd_chart_profitability")), fontsize=11, fontweight="bold", pad=10)
        fig.tight_layout()
        self.chart_profitability.canvas.draw()

    def _draw_radar(self, ratios):
        fig = self.chart_radar.figure
        fig.clear()
        ax = fig.add_subplot(111, polar=True)
        sector = self.sector_combo.currentData()
        data = advanced_dashboard_engine.ratios_radar(ratios, sector)
        if not data["labels"]:
            ax.text(0.5, 0.5, t("bench_no_sector"), ha="center", va="center",
                    color=_chart_text_color(), transform=ax.transAxes)
            ax.axis("off")
        else:
            N = len(data["labels"])
            angles = [n / float(N) * 2 * math.pi for n in range(N)]
            angles += angles[:1]
            company = data["company"] + data["company"][:1]
            sector_avg = data["sector_avg"] + data["sector_avg"][:1]
            ax.plot(angles, company, "o-", linewidth=2, color=self._accent_color,
                    label=t("bench_legend_company"))
            ax.fill(angles, company, alpha=0.2, color=self._accent_color)
            ax.plot(angles, sector_avg, "s--", linewidth=1.5, color="#95A5A6",
                    label=t("bench_trend_sector_avg"))
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(data["labels"], fontsize=8)
            ax.set_ylim(0, 100)
            ax.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.25, 1.1))
            ax.set_facecolor(ThemeColors.get("chart_bg"))
        ax.set_title(_plain_title(t("advd_chart_radar")), fontsize=11, fontweight="bold", pad=20)
        fig.tight_layout()
        self.chart_radar.canvas.draw()

    def _update_alerts(self, fd, ratios):
        self.alerts_list.clear()
        sector = self.sector_combo.currentData()
        alerts = advanced_dashboard_engine.alerts(fd, ratios, sector)
        if not alerts:
            item = QListWidgetItem(t("advd_alerts_no_alerts"))
            item.setForeground(QColor("#27AE60"))
            self.alerts_list.addItem(item)
            return
        cat_keys = {
            "anomaly": "advd_alerts_cat_anomaly",
            "performance": "advd_alerts_cat_performance",
            "ratio": "advd_alerts_cat_ratio",
            "action": "advd_alerts_cat_action",
        }
        sev_colors = {"critical": "#E74C3C", "warning": "#F39C12", "info": "#3498DB"}
        sev_icons = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
        for a in alerts:
            cat = t(cat_keys.get(a["category"], a["category"]))
            msg = a.get("message_ar") if state.language == "ar" else a.get(
                "message_en", a.get("message_ar", "")
            )
            icon = sev_icons.get(a["severity"], "•")
            item = QListWidgetItem(f"{icon} [{cat}] {msg}")
            item.setForeground(QColor(sev_colors.get(a["severity"], "#555555")))
            self.alerts_list.addItem(item)

    # ===== التخصيص والتخطيط =====

    def _on_customization_changed(self):
        self._apply_widget_visibility()
        self._apply_kpi_visibility()

    def _apply_widget_visibility(self):
        for wkey, widget in self._widget_frames.items():
            cb = self.widget_checkboxes.get(wkey)
            widget.setVisible(cb.isChecked() if cb else True)

    def _apply_kpi_visibility(self):
        for key, card in self.kpi_cards.items():
            cb = self.kpi_checkboxes.get(key)
            card.setVisible(cb.isChecked() if cb else True)

    def _on_color_changed(self, index):
        self._apply_accent_color()

    def _apply_accent_color(self):
        self._accent_color = self.color_combo.currentData() or _THEME_COLORS[0]
        if state.has_data():
            self._draw_revenue_trend(state.financial_data or {})
            self._draw_radar(state.ratios or {})

    def _set_period(self, period):
        self._period = period
        self.period_btn_monthly.setChecked(period == "monthly")
        self.period_btn_quarterly.setChecked(period == "quarterly")
        if state.has_data():
            self._draw_revenue_trend(state.financial_data or {})

    def _on_sector_changed(self, index):
        if state.has_data():
            self.refresh()

    def _auto_select_sector(self):
        act = getattr(state, "company_activity_type", 0) or 0
        code = _ACTIVITY_SECTOR_MAP[act] if 0 <= act < len(_ACTIVITY_SECTOR_MAP) else "commercial"
        idx = self.sector_combo.findData(code)
        if idx >= 0:
            self.sector_combo.setCurrentIndex(idx)

    def _current_preferences(self):
        return {
            "widgets": [k for k, cb in self.widget_checkboxes.items() if cb.isChecked()],
            "kpis": [k for k, cb in self.kpi_checkboxes.items() if cb.isChecked()],
            "color": self.color_combo.currentData() or _THEME_COLORS[0],
        }

    def _save_layout(self):
        name = self.layout_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, t("warning"), t("advd_layout_name_required"))
            return
        prefs = self._current_preferences()
        prefs["name"] = name
        if save_dashboard_layout(name, prefs):
            QMessageBox.information(self, t("success"), t("advd_layout_saved"))
            self._reload_saved_layouts()
        else:
            QMessageBox.critical(self, t("error"), t("failed"))

    def _reload_saved_layouts(self):
        self.saved_layouts_combo.clear()
        for l in get_dashboard_layouts():
            self.saved_layouts_combo.addItem(l["name"])

    def _load_layout(self):
        name = self.saved_layouts_combo.currentText()
        if not name:
            QMessageBox.information(self, t("info"), t("advd_no_saved_layouts"))
            return
        found = next((l for l in get_dashboard_layouts() if l["name"] == name), None)
        if not found:
            QMessageBox.warning(self, t("warning"), t("advd_no_saved_layouts"))
            return
        self._apply_preferences(found["layout"])
        QMessageBox.information(self, t("success"), t("advd_layout_loaded"))

    def _apply_preferences(self, prefs):
        widgets = prefs.get("widgets", list(ALL_WIDGETS))
        kpis = prefs.get("kpis", list(DEFAULT_KPIS))
        color = prefs.get("color", _THEME_COLORS[0])
        for key, cb in self.widget_checkboxes.items():
            cb.setChecked(key in widgets)
        for key, cb in self.kpi_checkboxes.items():
            cb.setChecked(key in kpis)
        idx = self.color_combo.findData(color)
        if idx >= 0:
            self.color_combo.setCurrentIndex(idx)
        self._apply_widget_visibility()
        self._apply_kpi_visibility()
        self._apply_accent_color()

    def _delete_layout(self):
        name = self.saved_layouts_combo.currentText()
        if not name:
            QMessageBox.information(self, t("info"), t("advd_no_saved_layouts"))
            return
        if delete_dashboard_layout(name):
            QMessageBox.information(self, t("success"), t("advd_layout_deleted"))
            self._reload_saved_layouts()
        else:
            QMessageBox.critical(self, t("error"), t("failed"))

    # ===== التصدير =====

    def _export_pdf(self):
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("advd_no_data"))
            return
        file_path = exporters.ask_save_path(
            self, t("advd_export"), "advanced_dashboard.pdf", "PDF Files (*.pdf)"
        )
        if not file_path:
            return
        try:
            figures = [c.figure for c in
                       (self.chart_revenue, self.chart_expense,
                        self.chart_profitability, self.chart_radar)
                       if c.isVisible()]
            exporters.write_charts_pdf(file_path, figures)
            QMessageBox.information(
                self, t("success"), f"✅ {t('advd_export_success')}\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _export_excel(self):
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("advd_no_data"))
            return
        file_path = exporters.ask_save_path(
            self, t("advd_export"), "advanced_dashboard.xlsx", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return
        try:
            self._write_excel(file_path)
            QMessageBox.information(
                self, t("success"), f"✅ {t('advd_export_success')}\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _write_excel(self, file_path):
        from ui.exporters import add_excel_sheet, new_workbook
        data = advanced_dashboard_engine.export_data(
            state.financial_data or {}, state.ratios or {},
            self.sector_combo.currentData()
        )
        wb = new_workbook()

        add_excel_sheet(
            wb, "KPIs",
            ["KPI", "Value", "Unit", "Status"],
            [[k["key"], k["value"], k["unit"], k["status"]] for k in data["kpis"]],
        )
        add_excel_sheet(
            wb, "Revenue Trend",
            ["Period", "Revenue"],
            [[label, val] for label, val in
             zip(data["revenue_trend"]["labels"], data["revenue_trend"]["values"])],
        )
        add_excel_sheet(
            wb, "Expenses",
            ["Category", "Amount"],
            [[label, val] for label, val in
             zip(data["expenses"]["labels"], data["expenses"]["values"])],
        )
        add_excel_sheet(
            wb, "Alerts",
            ["Category", "Severity", "Message"],
            [[a["category"], a["severity"], a.get("message_en", "")] for a in data["alerts"]],
        )

        wb.save(file_path)

    # ===== اللغة =====

    def retranslate(self):
        """تحديث كل النصوص عند تغيير اللغة"""
        self.title_label.setText(t("advd_title"))
        self.subtitle.setText(t("advd_subtitle"))
        self.sector_label.setText(t("bench_sector_select"))
        self.export_pdf_btn.setText(t("advd_export_pdf"))
        self.export_excel_btn.setText(t("advd_export_excel"))
        self.health_title.setText(t("advd_health_score"))
        self.kpi_section.setText(t("advd_widget_kpi_cards"))
        self.alerts_title.setText(t("advd_alerts_title"))
        self.custom_title.setText(t("advd_custom_title"))
        self.chart_revenue_title.setText(t("advd_chart_revenue"))
        self.period_btn_monthly.setText(t("advd_period_monthly"))
        self.period_btn_quarterly.setText(t("advd_period_quarterly"))
        self.chart_expense.set_title(t("advd_chart_expense"))
        self.chart_profitability.set_title(t("advd_chart_profitability"))
        self.chart_radar.set_title(t("advd_chart_radar"))
        self.layout_name_input.setPlaceholderText(t("advd_layout_name"))
        self.save_layout_btn.setText(t("advd_layout_save"))
        self.load_layout_btn.setText(t("advd_layout_load"))
        self.delete_layout_btn.setText(t("advd_layout_delete"))
        for key, card in self.kpi_cards.items():
            card.title_label.setText(t(_KPI_LABEL_KEYS.get(key, key)))
        for key, cb in self.kpi_checkboxes.items():
            cb.setText(t(_KPI_LABEL_KEYS.get(key, key)))
        for wkey, cb in self.widget_checkboxes.items():
            cb.setText(t(_WIDGET_LABEL_KEYS.get(wkey, wkey)))
        self.refresh()
