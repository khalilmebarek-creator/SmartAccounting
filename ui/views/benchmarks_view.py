from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QScrollArea, QListWidget,
    QDialog, QLineEdit, QDoubleSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import pyqtgraph as pg
from ui.charts import (PgChartWidget, PgPolarWidget,
    draw_radar, draw_bar,
    _text_color, _edge_color, _chart_bg, _hex_to_rgb, _mk_brush, _mk_pen, _mk_text_item)

from ui.views._base import BaseView
from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from ui.plotly_export import export_benchmarks_html
from modules.benchmarks import benchmark_analyzer, ALGERIAN_SECTORS
from database.db_operations import (
    get_competitors, save_competitor, delete_competitor, get_company_ratio_history
)


class AddCompetitorDialog(QDialog):
    """حوار إضافة منافس مع إدخال نسبه المالية"""

    def __init__(self, defaults, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("bench_comp_add"))
        self.setMinimumWidth(460)
        self._defaults = defaults or {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel(t("bench_comp_add"))
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        name_lbl = QLabel(t("bench_comp_name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("bench_comp_name"))
        layout.addWidget(name_lbl)
        layout.addWidget(self.name_input)

        self.ratio_inputs = {}
        ratio_labels = self._ratio_labels()
        form = QFormLayout()
        for key in self._defaults.keys():
            spin = QDoubleSpinBox()
            spin.setRange(-999999, 999999)
            spin.setDecimals(2)
            spin.setValue(float(self._defaults[key] or 0))
            spin.setMinimumWidth(180)
            self.ratio_inputs[key] = spin
            form.addRow(ratio_labels.get(key, key), spin)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton(t("btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.save_btn = QPushButton(t("bench_comp_save"))
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setTabOrder(self.name_input, self.save_btn)

    @staticmethod
    def _ratio_labels():
        return {
            "current_ratio": t("bench_r_current"),
            "quick_ratio": t("bench_r_quick"),
            "gross_profit_margin": t("bench_r_gross"),
            "net_profit_margin": t("bench_r_net"),
            "roa": t("bench_r_roa"),
            "roe": t("bench_r_roe"),
            "debt_to_equity": t("bench_r_de"),
            "asset_turnover": t("bench_r_asset"),
            "inventory_turnover": t("bench_r_inv"),
            "receivable_turnover": t("bench_r_rec"),
        }

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, t("warning"), t("bench_comp_name_required"))
            return
        self.accept()

    def get_data(self):
        ratios = {}
        for key, spin in self.ratio_inputs.items():
            ratios[key] = round(spin.value(), 4)
        return {
            "name": self.name_input.text().strip(),
            "ratios": ratios,
        }


class BenchmarkView(BaseView):

    def __init__(self):
        super().__init__()
        self.comparison_result = None
        self._labels = {}
        self.setup_ui()

    def setup_ui(self):
        title = self._make_header("bench_title", "bench_subtitle")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dashboardScroll")

        scroll_content = QWidget()
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setSpacing(15)
        self._build_controls()
        self._build_score()
        self._build_table_section()
        self._build_strengths_weaknesses()
        self._build_charts()
        self._build_suggestions()
        self._build_trend()
        self._build_competitors()

        self.content_layout.addStretch()

        scroll.setWidget(scroll_content)
        self._main_layout.addWidget(scroll, 1)

        self.refresh()
    def _build_controls(self):
        """شريط التحكم: القطاع + أزرار المقارنة"""

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.sector_label = QLabel(t("bench_sector_select"))
        controls.addWidget(self.sector_label)

        self.sector_combo = QComboBox()
        self.sector_combo.setMinimumWidth(220)
        self.sector_combo.setMinimumHeight(40)
        for s in benchmark_analyzer.get_sectors_list():
            self.sector_combo.addItem(s["name_ar"], s["code"])
        self.sector_combo.currentIndexChanged.connect(self._on_sector_changed)
        controls.addWidget(self.sector_combo)

        self.compare_btn = QPushButton(t("bench_compare"))
        self.compare_btn.setObjectName("primaryBtn")
        self.compare_btn.setMinimumWidth(180)
        self.compare_btn.setMinimumHeight(40)
        self.compare_btn.clicked.connect(self.run_comparison)
        controls.addWidget(self.compare_btn)

        controls.addStretch()

        self.print_btn = QPushButton(t("bench_print"))
        self.print_btn.setObjectName("secondaryBtn")
        self.print_btn.setMinimumHeight(40)
        self.print_btn.clicked.connect(self._print_report)
        controls.addWidget(self.print_btn)

        self.export_btn = QPushButton(t("bench_export"))
        self.export_btn.setObjectName("secondaryBtn")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self._export_excel)
        controls.addWidget(self.export_btn)

        self.html_btn = QPushButton(t("export_benchmarks_html"))
        self.html_btn.setObjectName("secondaryBtn")
        self.html_btn.setMinimumHeight(40)
        self.html_btn.clicked.connect(self._export_html)
        controls.addWidget(self.html_btn)

        self._main_layout.addLayout(controls)

        self.setTabOrder(self.sector_combo, self.compare_btn)
        self.setTabOrder(self.compare_btn, self.print_btn)
        self.setTabOrder(self.print_btn, self.export_btn)
        self.setTabOrder(self.export_btn, self.html_btn)

    def _build_score(self):
        """بطاقة النتيجة والتقييم"""

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separator")
        self._main_layout.addWidget(sep)

        self.score_frame = QFrame()
        self.score_frame.setObjectName("card")
        score_layout = QHBoxLayout(self.score_frame)
        score_layout.setContentsMargins(16, 12, 16, 12)

        self.score_title = QLabel(t("bench_score"))
        self.score_title.setObjectName("cardTitle")
        score_layout.addWidget(self.score_title)

        value_layout = QVBoxLayout()

        self.score_value = QLabel("--")
        self.score_value.setObjectName("statValue")
        score_font = QFont()
        score_font.setBold(True)
        score_font.setPointSize(22)
        self.score_value.setFont(score_font)
        self.score_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_layout.addWidget(self.score_value)

        self.rating_value = QLabel("")
        self.rating_value.setObjectName("cardSubtitle")
        rating_font = QFont()
        rating_font.setBold(True)
        rating_font.setPointSize(14)
        self.rating_value.setFont(rating_font)
        self.rating_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_layout.addWidget(self.rating_value)

        score_layout.addLayout(value_layout)

        self._main_layout.addWidget(self.score_frame)

    def _build_table_section(self):
        """جدول المعايير"""

        self.table_title = QLabel(t("bench_table_title"))
        self.table_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.table_title)

        self.empty_guide = QLabel(t("bench_empty_guide"))
        self.empty_guide.setObjectName("card")
        self.empty_guide.setWordWrap(True)
        self.empty_guide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_guide.setMinimumHeight(100)
        self.empty_guide.setStyleSheet("padding: 20px; font-size: 14px;")
        self.empty_guide.hide()
        self.content_layout.addWidget(self.empty_guide)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            t("bench_col_ratio"), t("bench_col_company"),
            t("bench_col_best"), t("bench_col_international"),
            t("bench_col_min"), t("bench_col_avg"), t("bench_col_max")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setMinimumHeight(300)
        self.content_layout.addWidget(self.table)

    def _build_strengths_weaknesses(self):
        """نقاط القوة والضعف"""

        self.sw_title = QLabel(t("bench_sw_title"))
        self.sw_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.sw_title)

        sw_layout = QHBoxLayout()
        sw_layout.setSpacing(15)
        self.strengths_list = QListWidget()
        self.strengths_list.setMinimumHeight(120)
        self.strengths_list.setMaximumHeight(180)
        self.weaknesses_list = QListWidget()
        self.weaknesses_list.setMinimumHeight(120)
        self.weaknesses_list.setMaximumHeight(180)
        sw_layout.addWidget(self.strengths_list, 1)
        sw_layout.addWidget(self.weaknesses_list, 1)
        self.content_layout.addLayout(sw_layout)

    def _build_charts(self):
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        self.radar_widget = PgPolarWidget(t("bench_radar_title"))
        self.radar_widget.setMinimumHeight(320)
        charts_layout.addWidget(self.radar_widget, 1)

        self.bar_widget = PgChartWidget(t("bench_bar_title"))
        self.bar_widget.setMinimumHeight(300)
        charts_layout.addWidget(self.bar_widget, 1)

        self.content_layout.addLayout(charts_layout)

    def _build_suggestions(self):
        """التوصيات"""

        self.suggestions_title = QLabel(t("bench_suggestions"))
        self.suggestions_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.suggestions_title)

        self.suggestions_list = QListWidget()
        self.suggestions_list.setMinimumHeight(120)
        self.suggestions_list.setMaximumHeight(200)
        self.content_layout.addWidget(self.suggestions_list)

    def _build_trend(self):
        self.trend_title = QLabel(t("bench_trend_title"))
        self.trend_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.trend_title)

        self.trend_widget = PgChartWidget(t("bench_trend_title"))
        self.trend_widget.setMinimumHeight(240)
        self.content_layout.addWidget(self.trend_widget)

    def _build_competitors(self):
        """مقارنة المنافسين"""

        self.comp_title = QLabel(t("bench_comp_title"))
        self.comp_title.setObjectName("sectionTitle")
        self.content_layout.addWidget(self.comp_title)

        comp_controls = QHBoxLayout()
        comp_controls.setSpacing(10)
        self.comp_add_btn = QPushButton(t("bench_comp_add"))
        self.comp_add_btn.setObjectName("primaryBtn")
        self.comp_add_btn.clicked.connect(self._on_add_competitor)
        comp_controls.addWidget(self.comp_add_btn)
        self.comp_delete_btn = QPushButton(t("bench_comp_delete"))
        self.comp_delete_btn.setObjectName("secondaryBtn")
        self.comp_delete_btn.clicked.connect(self._on_delete_competitor)
        comp_controls.addWidget(self.comp_delete_btn)
        comp_controls.addStretch()
        self.content_layout.addLayout(comp_controls)

        self.comp_table = QTableWidget()
        self.comp_table.setColumnCount(3)
        self.comp_table.setHorizontalHeaderLabels([
            t("bench_comp_position"), t("bench_comp_name"), t("bench_score")
        ])
        self.comp_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.comp_table.setAlternatingRowColors(True)
        self.comp_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.comp_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.comp_table.setMinimumHeight(120)
        self.comp_table.setMaximumHeight(200)
        self.content_layout.addWidget(self.comp_table)

        self.refresh()

    def _on_sector_changed(self, index):
        if not state.has_data():
            return
        company_ratios = self._get_company_ratios()
        if not company_ratios:
            return
        self.run_comparison()

    def run_comparison(self):
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("bench_no_data"))
            return

        sector_code = self.sector_combo.currentData()
        if not sector_code:
            QMessageBox.warning(self, t("warning"), t("bench_no_sector"))
            return

        try:
            company_ratios = self._get_company_ratios()
            if not company_ratios:
                QMessageBox.warning(self, t("warning"), t("bench_no_ratios"))
                return

            self.comparison_result = benchmark_analyzer.compare_with_sector(
                company_ratios, sector_code
            )

            if "error" in self.comparison_result:
                QMessageBox.critical(self, t("error"), self.comparison_result["error"])
                return

            self._update_score()
            self._populate_table()
            self._draw_radar(company_ratios, sector_code)
            self._draw_bar()
            self._fill_suggestions(company_ratios, sector_code)
            self._fill_strengths_weaknesses()
            self._draw_trend()
            self._refresh_competitor_ranking()

        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("benchmarks_view").error(f"Benchmark comparison failed: {e}")
            QMessageBox.critical(self, t("error"), str(e))

    def _get_company_ratios(self):
        ratios = state.ratios
        if not ratios:
            return {}
        return {k: v for k, v in ratios.items() if v is not None}

    def _update_score(self):
        result = self.comparison_result
        score = result.get("overall_score", 0)
        rating = result.get("rating", {})

        self.score_value.setText(f"{score}")
        color = rating.get("color", "#7F8C8D")
        self.score_value.setStyleSheet(f"color: {color};")
        self.rating_value.setText(rating.get("ar", ""))
        self.rating_value.setStyleSheet(f"color: {color};")

    def _populate_table(self):
        ratios = self.comparison_result.get("ratios", {})
        ratio_display = {
            "current_ratio": t("bench_r_current"),
            "quick_ratio": t("bench_r_quick"),
            "gross_profit_margin": t("bench_r_gross"),
            "net_profit_margin": t("bench_r_net"),
            "roa": t("bench_r_roa"),
            "roe": t("bench_r_roe"),
            "debt_to_equity": t("bench_r_de"),
            "asset_turnover": t("bench_r_asset"),
            "inventory_turnover": t("bench_r_inv"),
            "receivable_turnover": t("bench_r_rec"),
        }

        rows = []
        for key, display in ratio_display.items():
            if key in ratios:
                r = ratios[key]
                rows.append((display, r))

        self.table.setRowCount(len(rows))
        for i, (name, r) in enumerate(rows):
            name_item = QTableWidgetItem(name)
            self.table.setItem(i, 0, name_item)

            company_val = r.get("company_value", 0)
            min_val = r.get("sector_min", 0)
            avg_val = r.get("sector_avg", 0)
            max_val = r.get("sector_max", 0)
            best_val = r.get("best_practice", 0)
            inter_val = r.get("international", 0)
            status = r.get("status", "")

            company_item = QTableWidgetItem(f"{company_val:.4f}")
            if status in ("critical", "below"):
                company_item.setForeground(QColor("#E74C3C"))
            elif status in ("good", "excellent", "best"):
                company_item.setForeground(QColor("#27AE60"))
            else:
                company_item.setForeground(QColor("#F39C12"))
            self.table.setItem(i, 1, company_item)

            self.table.setItem(i, 2, QTableWidgetItem(f"{best_val:.4f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{inter_val:.4f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{min_val:.4f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{avg_val:.4f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{max_val:.4f}"))

    def _draw_radar(self, company_ratios, sector_code):
        self.radar_widget.clear_plot()

        radar_data = benchmark_analyzer.get_radar_data(company_ratios, sector_code)
        labels = radar_data.get("labels", [])
        if not labels:
            return

        company_vals = radar_data["company"]
        sector_avg = radar_data["sector_avg"]

        draw_radar(self.radar_widget, labels,
                   [company_vals, sector_avg],
                   colors_list=["#3498DB", "#E74C3C"])

    def _draw_bar(self):
        self.bar_widget.clear_plot()
        pi = self.bar_widget.plot_item

        if not self.comparison_result:
            return

        ratios = self.comparison_result.get("ratios", {})
        ratio_display = {
            "current_ratio": t("bench_r_current"),
            "quick_ratio": t("bench_r_quick"),
            "gross_profit_margin": t("bench_r_gross"),
            "net_profit_margin": t("bench_r_net"),
            "roa": t("bench_r_roa"),
            "roe": t("bench_r_roe"),
            "debt_to_equity": t("bench_r_de"),
            "asset_turnover": t("bench_r_asset"),
            "inventory_turnover": t("bench_r_inv"),
            "receivable_turnover": t("bench_r_rec"),
        }

        names = []
        scores = []
        bar_colors = []
        for key, display in ratio_display.items():
            if key in ratios:
                names.append(display)
                score = ratios[key].get("score", 0)
                scores.append(score)
                status = ratios[key].get("status", "")
                if status in ("critical", "below"):
                    bar_colors.append("#E74C3C")
                elif status in ("good", "excellent"):
                    bar_colors.append("#27AE60")
                else:
                    bar_colors.append("#F39C12")

        if not names:
            return

        import numpy as np
        n = len(names)
        y = np.arange(n)
        brushes = [_mk_brush(c) for c in bar_colors]
        bg = pg.BarGraphItem(y=y, x0=0, width=scores, height=0.6, brushes=brushes)
        pi.addItem(bg)

        for i, score in enumerate(scores):
            t_item = _mk_text_item(f"{score:.0f}", score + 2, y[i], bold=True, size=9)
            pi.addItem(t_item)

        tick_labels = [[(i, l) for i, l in enumerate(names)]]
        pi.getAxis("left").setTicks(tick_labels)
        pi.setXRange(0, 110)
        pi.setLabel("bottom", t("bench_bar_xlabel"))
        pi.showGrid(x=True, y=False, alpha=0.2)

    def _fill_suggestions(self, company_ratios, sector_code):
        self.suggestions_list.clear()
        suggestions = benchmark_analyzer.suggest_improvements(company_ratios, sector_code)

        if not suggestions:
            self.suggestions_list.addItem(t("bench_no_suggestions"))
            return

        severity_icons = {
            "critical": "\u2716",
            "warning": "\u26A0",
            "info": "\u2139",
        }
        severity_colors = {
            "critical": "#E74C3C",
            "warning": "#F39C12",
            "info": "#3498DB",
        }

        for s in suggestions:
            icon = severity_icons.get(s.get("severity", ""), "")
            msg = s.get("message_ar", s.get("message_en", ""))
            target = s.get("target_range", "")
            item_text = f"  {icon}  {msg}  [{t('bench_target')}: {target}]"
            self.suggestions_list.addItem(item_text)
            item_widget = self.suggestions_list.item(self.suggestions_list.count() - 1)
            if item_widget:
                color = severity_colors.get(s.get("severity", ""), "#7F8C8D")
                item_widget.setForeground(QColor(color))

    @staticmethod
    def _ratio_display():
        return {
            "current_ratio": t("bench_r_current"),
            "quick_ratio": t("bench_r_quick"),
            "gross_profit_margin": t("bench_r_gross"),
            "net_profit_margin": t("bench_r_net"),
            "roa": t("bench_r_roa"),
            "roe": t("bench_r_roe"),
            "debt_to_equity": t("bench_r_de"),
            "asset_turnover": t("bench_r_asset"),
            "inventory_turnover": t("bench_r_inv"),
            "receivable_turnover": t("bench_r_rec"),
        }

    def _fill_strengths_weaknesses(self):
        self.strengths_list.clear()
        self.weaknesses_list.clear()
        result = self.comparison_result or {}
        strengths = result.get("strengths", [])
        weaknesses = result.get("weaknesses", [])
        status_text = {
            "best": t("bench_status_best"),
            "excellent": t("bench_status_excellent"),
            "good": t("bench_status_good"),
            "above": t("bench_status_above"),
            "below": t("bench_status_below"),
            "critical": t("bench_status_critical"),
        }
        display = self._ratio_display()

        if not strengths:
            self.strengths_list.addItem(t("bench_no_strengths"))
        for s in strengths:
            label = display.get(s["ratio"], s["ratio"])
            st = status_text.get(s["status"], s["status"])
            self.strengths_list.addItem(f"  {label}  ·  {st}  ({s['score']}/100)")

        if not weaknesses:
            self.weaknesses_list.addItem(t("bench_no_weaknesses"))
        for w in weaknesses:
            label = display.get(w["ratio"], w["ratio"])
            st = status_text.get(w["status"], w["status"])
            self.weaknesses_list.addItem(f"  {label}  ·  {st}  ({w['score']}/100)")

    def _draw_trend(self):
        self.trend_widget.clear_plot()
        pi = self.trend_widget.plot_item

        company = state.company_name or ""
        sector_code = self.sector_combo.currentData()
        history = get_company_ratio_history(company) if company else []

        if not history or not sector_code:
            pi.hideAxis("left")
            pi.hideAxis("bottom")
            t_item = _mk_text_item(t("bench_trend_no_data"), 0, 0, size=10, anchor=(0.5, 0.5))
            pi.addItem(t_item)
            return

        trend = benchmark_analyzer.get_trend_data(history, sector_code)
        if "error" in trend:
            return

        years = trend.get("years", [])
        scores = trend.get("scores", [])
        if not years:
            return

        sector_avg_ratios = {
            rname: bm.get("avg", 0)
            for rname, bm in ALGERIAN_SECTORS.get(sector_code, {}).get("benchmarks", {}).items()
        }
        ref = benchmark_analyzer.compare_with_sector(sector_avg_ratios, sector_code)
        ref_score = ref.get("overall_score", 0)

        draw_line(pi, years, scores,
                  label=t("bench_legend_company"),
                  colors="#3498DB", fill=False)

        from pyqtgraph import InfiniteLine
        ref_line = InfiniteLine(pos=(0, ref_score), angle=0,
                                pen=_mk_pen('#E74C3C', 2))
        pi.addItem(ref_line)
        ref_lbl = _mk_text_item(
            f"{t('bench_trend_sector_avg')}: {ref_score:.0f}",
            years[-1] if years else 0, ref_score,
            color='#E74C3C', size=8, anchor=(1.0, 1.5))
        pi.addItem(ref_lbl)

        for x, y in zip(years, scores):
            ann = _mk_text_item(f"{y:.0f}", x, y, size=8, anchor=(0.5, 2.0))
            pi.addItem(ann)

        pi.showGrid(x=False, y=True, alpha=0.2)

    def _load_competitors(self):
        sector_code = self.sector_combo.currentData()
        self._competitors = get_competitors(sector_code) if sector_code else []

    def _refresh_competitor_ranking(self):
        self._load_competitors()
        self.comp_table.setRowCount(0)

        sector_code = self.sector_combo.currentData()
        company_ratios = self._get_company_ratios()
        if not sector_code or not company_ratios:
            return

        result = benchmark_analyzer.compare_with_competitors(
            company_ratios, sector_code, self._competitors
        )
        if "error" in result:
            return

        ranking = result.get("ranking", [])
        self.comp_table.setRowCount(len(ranking))
        for i, item in enumerate(ranking):
            name = t("bench_comp_company") if item.get("is_company") else item["name"]
            self.comp_table.setItem(i, 0, QTableWidgetItem(str(item.get("position", ""))))
            name_item = QTableWidgetItem(name)
            score_item = QTableWidgetItem(
                f"{item.get('overall_score', 0):.1f} · {item.get('rating_ar', '')}"
            )
            if item.get("is_company"):
                name_item.setForeground(QColor("#27AE60"))
                score_item.setForeground(QColor("#27AE60"))
            self.comp_table.setItem(i, 1, name_item)
            self.comp_table.setItem(i, 2, score_item)

    def _on_add_competitor(self):
        sector_code = self.sector_combo.currentData()
        if not sector_code:
            QMessageBox.warning(self, t("warning"), t("bench_no_sector"))
            return

        defaults = {
            rname: bm.get("avg", 0)
            for rname, bm in ALGERIAN_SECTORS.get(sector_code, {}).get("benchmarks", {}).items()
        }
        dlg = AddCompetitorDialog(defaults, self)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        if save_competitor(sector_code, data["name"], data["ratios"]):
            self._refresh_competitor_ranking()
        else:
            QMessageBox.critical(self, t("error"), t("bench_comp_name_required"))

    def _on_delete_competitor(self):
        row = self.comp_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("warning"), t("bench_no_results"))
            return
        name_item = self.comp_table.item(row, 1)
        if not name_item or name_item.text() == t("bench_comp_company"):
            return

        sector_code = self.sector_combo.currentData()
        if not sector_code:
            return
        confirm = QMessageBox.question(
            self, t("warning"), t("bench_comp_confirm_delete")
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        delete_competitor(sector_code, name_item.text())
        self._refresh_competitor_ranking()

    def _generate_html_report(self):
        if not self.comparison_result:
            return ""

        result = self.comparison_result
        score = result.get("overall_score", 0)
        rating = result.get("rating", {})
        sector = result.get("sector_ar", result.get("sector", ""))
        ratios = result.get("ratios", {})
        suggestions = benchmark_analyzer.suggest_improvements(
            self._get_company_ratios(), self.sector_combo.currentData()
        )

        html = f"""
<html><body dir="rtl" style="font-family: Arial; padding: 20px;">
<h1 style="color: #2C3E50;">{t('bench_report_title')}</h1>
<h2>{t('bench_report_sector')}: {sector}</h2>
<h3>{t('bench_score')}: {score} - {rating.get('ar', '')}</h3>
<table border="1" cellpadding="8" cellspacing="0" style="width:100%; border-collapse: collapse;">
<tr style="background: #2980B9; color: white;">
<th>{t('bench_col_ratio')}</th><th>{t('bench_col_company')}</th>
<th>{t('bench_col_min')}</th><th>{t('bench_col_avg')}</th><th>{t('bench_col_max')}</th>
</tr>
"""
        ratio_labels = {
            "current_ratio": t("bench_r_current"), "quick_ratio": t("bench_r_quick"),
            "gross_profit_margin": t("bench_r_gross"), "net_profit_margin": t("bench_r_net"),
            "roa": t("bench_r_roa"), "roe": t("bench_r_roe"),
            "debt_to_equity": t("bench_r_de"), "asset_turnover": t("bench_r_asset"),
            "inventory_turnover": t("bench_r_inv"), "receivable_turnover": t("bench_r_rec"),
        }

        for key, label in ratio_labels.items():
            if key in ratios:
                r = ratios[key]
                html += f"<tr><td>{label}</td><td>{r.get('company_value', 0):.4f}</td>"
                html += f"<td>{r.get('sector_min', 0):.4f}</td>"
                html += f"<td>{r.get('sector_avg', 0):.4f}</td>"
                html += f"<td>{r.get('sector_max', 0):.4f}</td></tr>"

        html += "</table><br>"
        html += f"<h3>{t('bench_suggestions')}</h3><ul>"
        for s in suggestions:
            html += f"<li>{s.get('message_ar', s.get('message_en', ''))}</li>"
        html += "</ul></body></html>"
        return html

    def _print_report(self):
        if not self.comparison_result:
            QMessageBox.warning(self, t("warning"), t("bench_no_results"))
            return

        try:
            from modules.print_manager import print_manager
            html = self._generate_html_report()
            if html:
                print_manager.print_html(html, title=t("bench_report_title"))
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("benchmarks_view").error(f"Print failed: {e}")
            QMessageBox.critical(self, t("error"), str(e))

    def _export_excel(self):
        if not self.comparison_result:
            QMessageBox.warning(self, t("warning"), t("bench_no_results"))
            return

        try:
            from modules.excel_export import excel_exporter
            result = self.comparison_result
            ratios = result.get("ratios", {})

            data = []
            ratio_labels = {
                "current_ratio": "Current Ratio", "quick_ratio": "Quick Ratio",
                "gross_profit_margin": "Gross Profit Margin",
                "net_profit_margin": "Net Profit Margin",
                "roa": "ROA", "roe": "ROE",
                "debt_to_equity": "Debt/Equity",
                "asset_turnover": "Asset Turnover",
                "inventory_turnover": "Inventory Turnover",
                "receivable_turnover": "Receivable Turnover",
            }

            for key, label in ratio_labels.items():
                if key in ratios:
                    r = ratios[key]
                    data.append({
                        "Ratio": label,
                        "Company Value": r.get("company_value", 0),
                        "Sector Min": r.get("sector_min", 0),
                        "Sector Avg": r.get("sector_avg", 0),
                        "Sector Max": r.get("sector_max", 0),
                        "Status": r.get("status", ""),
                        "Score": r.get("score", 0),
                    })

            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, t("bench_export_title"), "benchmarks.xlsx",
                "Excel Files (*.xlsx)"
            )
            if not file_path:
                return

            excel_exporter.export_comparison(data, file_path,
                                             title=t("bench_report_title"))
            QMessageBox.information(self, t("success"), t("bench_export_success"))
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("benchmarks_view").error(f"Export failed: {e}")
            QMessageBox.critical(self, t("error"), str(e))

    def _export_html(self):
        if not self.comparison_result:
            QMessageBox.warning(self, t("warning"), t("bench_no_results"))
            return

        try:
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, t("export_benchmarks_html"), "benchmarks.html",
                "HTML (*.html)"
            )
            if not file_path:
                return

            result = self.comparison_result
            ratios = result.get("ratios", {})
            ratio_display = self._ratio_display()

            radar_data = benchmark_analyzer.get_radar_data(
                self._get_company_ratios(), self.sector_combo.currentData()
            )
            labels = radar_data.get("labels", [])
            company_vals = radar_data.get("company", [])
            sector_avg = radar_data.get("sector_avg", [])

            charts_data = {}
            if labels:
                charts_data["radar"] = {
                    "labels": labels,
                    "series": [
                        {"name": t("bench_legend_company"), "values": company_vals, "color": "#3498DB"},
                        {"name": t("bench_legend_sector"), "values": sector_avg, "color": "#E74C3C"},
                    ],
                }

            bar_labels = []
            bar_values = []
            bar_colors = []
            for key, display in ratio_display.items():
                if key in ratios:
                    bar_labels.append(display)
                    bar_values.append(ratios[key].get("score", 0))
                    status = ratios[key].get("status", "")
                    if status in ("critical", "below"):
                        bar_colors.append("#E74C3C")
                    elif status in ("good", "excellent"):
                        bar_colors.append("#27AE60")
                    else:
                        bar_colors.append("#F39C12")
            if bar_labels:
                charts_data["bar"] = {
                    "labels": bar_labels, "values": bar_values, "colors": bar_colors,
                }

            company = state.company_name or ""
            history = get_company_ratio_history(company) if company else []
            sector_code = self.sector_combo.currentData()
            if history and sector_code:
                trend = benchmark_analyzer.get_trend_data(history, sector_code)
                years = trend.get("years", [])
                scores = trend.get("scores", [])
                if years and "error" not in trend:
                    charts_data["trend"] = {
                        "x": years,
                        "series": [
                            {"name": t("bench_legend_company"), "y": scores, "color": "#3498DB"},
                        ],
                    }

            export_benchmarks_html(file_path, charts_data)
            QMessageBox.information(self, t("success"), t("bench_export_success"))
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("benchmarks_view").error(f"HTML export failed: {e}")
            QMessageBox.critical(self, t("error"), str(e))

    def refresh(self):
        if not state.has_data():
            self.score_value.setText("--")
            self.rating_value.setText("")
            self.table.setRowCount(0)
            self.suggestions_list.clear()
            self.strengths_list.clear()
            self.weaknesses_list.clear()
            self.comp_table.setRowCount(0)
            self.empty_guide.show()
            self.table_title.hide()
            self.table.hide()
            self.score_frame.hide()
            self.suggestions_title.hide()
            self.suggestions_list.hide()
            self.radar_widget.hide()
            self.bar_widget.hide()
            self.sw_title.hide()
            self.strengths_list.hide()
            self.weaknesses_list.hide()
            self.trend_title.hide()
            self.trend_widget.hide()
            self.comp_title.hide()
            self.comp_add_btn.hide()
            self.comp_delete_btn.hide()
            self.comp_table.hide()
            return

        self.empty_guide.hide()
        self.table_title.show()
        self.table.show()
        self.score_frame.show()
        self.suggestions_title.show()
        self.suggestions_list.show()
        self.radar_widget.show()
        self.bar_widget.show()
        self.sw_title.show()
        self.strengths_list.show()
        self.weaknesses_list.show()
        self.trend_title.show()
        self.trend_widget.show()
        self.comp_title.show()
        self.comp_add_btn.show()
        self.comp_delete_btn.show()
        self.comp_table.show()

        self.sector_combo.blockSignals(True)
        self.sector_combo.clear()
        for s in benchmark_analyzer.get_sectors_list():
            self.sector_combo.addItem(s["name_ar"], s["code"])
        self.sector_combo.blockSignals(False)

    def retranslate(self):
        title = self.findChild(QLabel, "headerTitle")
        if title:
            title.setText(t("bench_title"))
        subtitle = self.findChild(QLabel, "headerSubtitle")
        if subtitle:
            subtitle.setText(t("bench_subtitle"))

        self.sector_label.setText(t("bench_sector_select"))
        self.compare_btn.setText(t("bench_compare"))
        self.print_btn.setText(t("bench_print"))
        self.export_btn.setText(t("bench_export"))
        self.html_btn.setText(t("export_benchmarks_html"))
        self.score_title.setText(t("bench_score"))
        self.table_title.setText(t("bench_table_title"))
        self.suggestions_title.setText(t("bench_suggestions"))
        self.sw_title.setText(t("bench_sw_title"))
        self.trend_title.setText(t("bench_trend_title"))
        self.comp_title.setText(t("bench_comp_title"))
        self.comp_add_btn.setText(t("bench_comp_add"))
        self.comp_delete_btn.setText(t("bench_comp_delete"))

        self.table.setHorizontalHeaderLabels([
            t("bench_col_ratio"), t("bench_col_company"),
            t("bench_col_best"), t("bench_col_international"),
            t("bench_col_min"), t("bench_col_avg"), t("bench_col_max")
        ])

        self.comp_table.setHorizontalHeaderLabels([
            t("bench_comp_position"), t("bench_comp_name"), t("bench_score")
        ])

        self.refresh()
        if self.comparison_result:
            self.run_comparison()
