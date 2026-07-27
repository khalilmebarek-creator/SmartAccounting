# عرض تحليل DuPont
# ==================

from ui.views._path import _  # noqa: F401 — ensures project root on sys.path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.app_state import state
from ui.resources.i18n import t


class DuPontView(QWidget):
    """واجهة تحليل DuPont"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # العنوان
        self.title = QLabel(t("analysis_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("analysis_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        # ===== المعادلة =====
        equation_frame = QFrame()
        equation_frame.setObjectName("card")
        equation_layout = QVBoxLayout(equation_frame)

        eq_title = QLabel(t("ana_equation"))
        eq_title.setObjectName("sectionTitle")
        equation_layout.addWidget(eq_title)

        equation = QLabel(t("ana_equation_formula"))
        eq_font = QFont()
        eq_font.setPointSize(14)
        eq_font.setBold(True)
        equation.setFont(eq_font)
        equation.setAlignment(Qt.AlignCenter)
        equation.setStyleSheet("padding: 15px;")
        equation.setObjectName("equationLabel")
        equation_layout.addWidget(equation)

        main_layout.addWidget(equation_frame)

        # ===== المكونات =====
        components_title = QLabel(t("ana_components"))
        components_title.setObjectName("sectionTitle")
        main_layout.addWidget(components_title)

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

        main_layout.addLayout(components_grid)

        # ===== التفسير =====
        interpretation_title = QLabel(t("ana_interpretation"))
        interpretation_title.setObjectName("sectionTitle")
        main_layout.addWidget(interpretation_title)

        self.interpretation_frame = QFrame()
        self.interpretation_frame.setObjectName("card")
        interp_layout = QVBoxLayout(self.interpretation_frame)

        self.interp_label = QLabel("--")
        self.interp_label.setWordWrap(True)
        self.interp_label.setTextFormat(Qt.RichText)
        self.interp_label.setStyleSheet("font-size: 11pt;")
        interp_layout.addWidget(self.interp_label)

        main_layout.addWidget(self.interpretation_frame)

        # ===== رأس المال العامل =====
        wc_title = QLabel(t("ana_wc_title"))
        wc_title.setObjectName("sectionTitle")
        main_layout.addWidget(wc_title)

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

        main_layout.addLayout(wc_grid)

        main_layout.addStretch()
        self.setLayout(main_layout)

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

    def retranslate(self):
        """تحديث النصوص عند تغيير اللغة"""
        self.title.setText(t("analysis_title"))
        self.subtitle.setText(t("analysis_subtitle"))
        self.npm_card.title_label.setText(t("ana_npm"))
        self.npm_card.desc_label.setText(t("ana_npm_formula"))
        self.at_card.title_label.setText(t("ana_asset_turnover"))
        self.at_card.desc_label.setText(t("ana_asset_turnover_formula"))
        self.em_card.title_label.setText(t("ana_equity_multiplier"))
        self.em_card.desc_label.setText(t("ana_equity_multiplier_formula"))
        self.roe_card.title_label.setText(t("ana_roe_label"))
        self.roe_card.sub_label.setText(t("ana_roe_result"))
        self.wc_value.title_label.setText(t("ana_wc"))
        self.wc_value.desc_label.setText(t("ana_wc_formula"))
        self.wc_status.title_label.setText(t("ana_wc_status"))
        self.wc_status.desc_label.setText(t("ana_wc_question"))
        self.wc_cycle.title_label.setText(t("ana_working_cycle"))
        self.wc_cycle.desc_label.setText(t("ana_wc_cycle_formula"))
        self.refresh()

    def refresh(self):
        """تحديث البيانات"""
        if not state.has_data() or not state.dupont:
            self.subtitle.setText(t("dashboard_no_data"))
            return

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

        # رأس المال العامل
        if state.working_capital:
            wc = state.working_capital.get('working_capital', 0)
            self.wc_value.value_label.setText(self.wc_value.format_str.format(wc))

            status = state.working_capital.get('status', '')
            self.wc_status.value_label.setText(status)

            cycle = state.working_capital.get('operating_cycle', 0)
            self.wc_cycle.value_label.setText(self.wc_cycle.format_str.format(cycle))
