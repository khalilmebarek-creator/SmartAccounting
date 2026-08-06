# عرض النسب المالية
# ===================

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QFrame, QSizePolicy, QScrollArea,
)
from PyQt5.QtGui import QFont

from ui.app_state import state
from ui.resources.i18n import t


class RatioCard(QFrame):
    """كارت عرض نسبة مالية واحدة"""
    
    def __init__(self, title, value, suffix="", good_threshold=None, bad_threshold=None, 
                 higher_is_better=True, format_str="{:.2f}"):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumSize(220, 130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # العنوان
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        layout.addWidget(self.title_label)
        
        # القيمة
        self.value_label = QLabel("--")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.value_label.setFont(font)
        layout.addWidget(self.value_label)
        
        # الحالة
        self.status_label = QLabel("")
        self.status_label.setObjectName("cardTitle")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.suffix = suffix
        self.good_threshold = good_threshold
        self.bad_threshold = bad_threshold
        self.higher_is_better = higher_is_better
        self.format_str = format_str
        self.update_value(value)
    
    def retranslate(self, title, suffix=None):
        self.title_label.setText(title)
        if suffix is not None:
            self.suffix = suffix
    
    def update_value(self, value):
        """تحديث القيمة ولونها"""
        if value is None or value == 0:
            self.value_label.setText("--")
            self.value_label.setObjectName("cardValue")
            self.status_label.setText("")
            return
        
        self.value_label.setText(self.format_str.format(value) + self.suffix)
        
        # تحديد اللون
        color = self._get_color(value)
        self.value_label.setObjectName(color)
        self.status_label.setText(self._get_status_text(value))
        
        # إعادة تطبيق الستايل
        self.value_label.style().unpolish(self.value_label)
        self.value_label.style().polish(self.value_label)
    
    def _get_color(self, value):
        """تحديد لون الكارت"""
        if self.good_threshold is None:
            return "cardValue"
        
        if self.higher_is_better:
            if value >= self.good_threshold:
                return "cardValueGood"
            elif self.bad_threshold and value <= self.bad_threshold:
                return "cardValueBad"
            else:
                return "cardValueWarning"
        else:
            if value <= self.good_threshold:
                return "cardValueGood"
            elif self.bad_threshold and value >= self.bad_threshold:
                return "cardValueBad"
            else:
                return "cardValueWarning"
    
    def _get_status_text(self, value):
        """نص الحالة"""
        if self.good_threshold is None:
            return ""
        if self.higher_is_better:
            if value >= self.good_threshold:
                return t("rat_excellent")
            elif self.bad_threshold and value <= self.bad_threshold:
                return t("rat_weak")
            else:
                return t("rat_acceptable")
        else:
            if value <= self.good_threshold:
                return t("rat_excellent")
            elif self.bad_threshold and value >= self.bad_threshold:
                return t("rat_weak")
            else:
                return t("rat_acceptable")


class RatiosView(QWidget):
    """واجهة عرض النسب المالية"""
    
    def __init__(self):
        super().__init__()
        self.cards = {}
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # العنوان
        self.title = QLabel(t("ratios_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)
        
        self.subtitle = QLabel(t("ratios_subtitle_calc"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)
        
        # منطقة قابلة للتمرير للكروت
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dashboardScroll")
        
        scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(scroll_content)
        self.cards_layout.setSpacing(15)
        
        # ===== نسب السيولة =====
        self.liquidity_title = QLabel(t("rat_liquidity"))
        self.liquidity_title.setObjectName("sectionTitle")
        self.cards_layout.addWidget(self.liquidity_title)
        
        liquidity_grid = QGridLayout()
        liquidity_grid.setSpacing(10)
        self.cards['current_ratio'] = RatioCard(t("rat_current_ratio"), 0, higher_is_better=True, good_threshold=1.5, bad_threshold=1.0)
        self.cards['quick_ratio'] = RatioCard(t("rat_quick_ratio"), 0, higher_is_better=True, good_threshold=1.0, bad_threshold=0.5)
        self.cards['cash_ratio'] = RatioCard(t("rat_cash_ratio"), 0, higher_is_better=True, good_threshold=0.3, bad_threshold=0.1)
        liquidity_grid.addWidget(self.cards['current_ratio'], 0, 0)
        liquidity_grid.addWidget(self.cards['quick_ratio'], 0, 1)
        liquidity_grid.addWidget(self.cards['cash_ratio'], 0, 2)
        self.cards_layout.addLayout(liquidity_grid)
        
        # ===== نسب الربحية =====
        self.profitability_title = QLabel(t("rat_profitability"))
        self.profitability_title.setObjectName("sectionTitle")
        self.cards_layout.addWidget(self.profitability_title)
        
        profitability_grid = QGridLayout()
        profitability_grid.setSpacing(10)
        self.cards['gross_profit_margin'] = RatioCard(t("rat_gross_margin"), 0, "%", higher_is_better=True, good_threshold=30, bad_threshold=15)
        self.cards['operating_profit_margin'] = RatioCard(t("rat_operating_margin"), 0, "%", higher_is_better=True, good_threshold=15, bad_threshold=8)
        self.cards['net_profit_margin'] = RatioCard(t("rat_net_margin"), 0, "%", higher_is_better=True, good_threshold=10, bad_threshold=5)
        self.cards['roa'] = RatioCard(t("rat_roa"), 0, "%", higher_is_better=True, good_threshold=10, bad_threshold=5)
        self.cards['roe'] = RatioCard(t("rat_roe_label"), 0, "%", higher_is_better=True, good_threshold=15, bad_threshold=8)
        profitability_grid.addWidget(self.cards['gross_profit_margin'], 0, 0)
        profitability_grid.addWidget(self.cards['operating_profit_margin'], 0, 1)
        profitability_grid.addWidget(self.cards['net_profit_margin'], 0, 2)
        profitability_grid.addWidget(self.cards['roa'], 1, 0)
        profitability_grid.addWidget(self.cards['roe'], 1, 1)
        self.cards_layout.addLayout(profitability_grid)
        
        # ===== نسب الكفاءة =====
        self.efficiency_title = QLabel(t("rat_efficiency"))
        self.efficiency_title.setObjectName("sectionTitle")
        self.cards_layout.addWidget(self.efficiency_title)
        
        efficiency_grid = QGridLayout()
        efficiency_grid.setSpacing(10)
        self.cards['asset_turnover'] = RatioCard(t("rat_asset_turnover"), 0, higher_is_better=True, good_threshold=1.5, bad_threshold=0.5)
        self.cards['receivables_turnover'] = RatioCard(t("rat_receivables_turnover"), 0, higher_is_better=True, good_threshold=8, bad_threshold=4)
        self.cards['inventory_turnover'] = RatioCard(t("rat_inventory_turnover"), 0, higher_is_better=True, good_threshold=6, bad_threshold=2)
        self.cards['days_sales_outstanding'] = RatioCard(t("rat_days_sales"), 0, t("rat_days_unit"), higher_is_better=False, good_threshold=45, bad_threshold=90)
        self.cards['days_inventory_outstanding'] = RatioCard(t("rat_days_inventory"), 0, t("rat_days_unit"), higher_is_better=False, good_threshold=60, bad_threshold=120)
        self.cards['payables_turnover'] = RatioCard(t("rat_payables_turnover"), 0, higher_is_better=True, good_threshold=6, bad_threshold=2)
        self.cards['days_payable_outstanding'] = RatioCard(t("rat_days_payables"), 0, t("rat_days_unit"), higher_is_better=True, good_threshold=45, bad_threshold=90)
        self.cards['operating_cycle'] = RatioCard(t("rat_operating_cycle"), 0, t("rat_days_unit"), higher_is_better=False, good_threshold=120, bad_threshold=180)
        self.cards['cash_conversion_cycle'] = RatioCard(t("rat_ccc"), 0, t("rat_days_unit"), higher_is_better=False, good_threshold=90, bad_threshold=150)
        efficiency_grid.addWidget(self.cards['asset_turnover'], 0, 0)
        efficiency_grid.addWidget(self.cards['receivables_turnover'], 0, 1)
        efficiency_grid.addWidget(self.cards['inventory_turnover'], 0, 2)
        efficiency_grid.addWidget(self.cards['days_sales_outstanding'], 1, 0)
        efficiency_grid.addWidget(self.cards['days_inventory_outstanding'], 1, 1)
        efficiency_grid.addWidget(self.cards['payables_turnover'], 1, 2)
        efficiency_grid.addWidget(self.cards['days_payable_outstanding'], 2, 0)
        efficiency_grid.addWidget(self.cards['operating_cycle'], 2, 1)
        efficiency_grid.addWidget(self.cards['cash_conversion_cycle'], 2, 2)
        self.cards_layout.addLayout(efficiency_grid)
        
        # ===== نسب الاستدانة =====
        self.leverage_title = QLabel(t("rat_leverage"))
        self.leverage_title.setObjectName("sectionTitle")
        self.cards_layout.addWidget(self.leverage_title)
        
        leverage_grid = QGridLayout()
        leverage_grid.setSpacing(10)
        self.cards['debt_to_equity'] = RatioCard(t("rat_debt_equity"), 0, higher_is_better=False, good_threshold=1.0, bad_threshold=2.0)
        self.cards['debt_ratio'] = RatioCard(t("rat_debt_ratio"), 0, higher_is_better=False, good_threshold=0.5, bad_threshold=0.7)
        self.cards['equity_ratio'] = RatioCard(t("rat_equity_ratio"), 0, higher_is_better=True, good_threshold=0.5, bad_threshold=0.3)
        leverage_grid.addWidget(self.cards['debt_to_equity'], 0, 0)
        leverage_grid.addWidget(self.cards['debt_ratio'], 0, 1)
        leverage_grid.addWidget(self.cards['equity_ratio'], 0, 2)
        self.cards_layout.addLayout(leverage_grid)
        
        self.cards_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
    
    def refresh(self):
        """تحديث كل الكروت بالبيانات الحالية"""
        if state.has_data():
            self.subtitle.setText(f"{t('dash_company_label')} {state.company_name} | {t('dash_fiscal_label')} {state.fiscal_year}")
            for key, card in self.cards.items():
                value = state.ratios.get(key, 0)
                card.update_value(value)
        else:
            self.subtitle.setText(t("dashboard_no_data"))
            for card in self.cards.values():
                card.update_value(0)
    
    def retranslate(self):
        self.title.setText(t("ratios_title"))
        self.liquidity_title.setText(t("rat_liquidity"))
        self.profitability_title.setText(t("rat_profitability"))
        self.efficiency_title.setText(t("rat_efficiency"))
        self.leverage_title.setText(t("rat_leverage"))
        self.cards['current_ratio'].retranslate(t("rat_current_ratio"))
        self.cards['quick_ratio'].retranslate(t("rat_quick_ratio"))
        self.cards['cash_ratio'].retranslate(t("rat_cash_ratio"))
        self.cards['gross_profit_margin'].retranslate(t("rat_gross_margin"))
        self.cards['operating_profit_margin'].retranslate(t("rat_operating_margin"))
        self.cards['net_profit_margin'].retranslate(t("rat_net_margin"))
        self.cards['roa'].retranslate(t("rat_roa"))
        self.cards['roe'].retranslate(t("rat_roe_label"))
        self.cards['asset_turnover'].retranslate(t("rat_asset_turnover"))
        self.cards['receivables_turnover'].retranslate(t("rat_receivables_turnover"))
        self.cards['inventory_turnover'].retranslate(t("rat_inventory_turnover"))
        self.cards['days_sales_outstanding'].retranslate(t("rat_days_sales"), t("rat_days_unit"))
        self.cards['days_inventory_outstanding'].retranslate(t("rat_days_inventory"), t("rat_days_unit"))
        self.cards['payables_turnover'].retranslate(t("rat_payables_turnover"))
        self.cards['days_payable_outstanding'].retranslate(t("rat_days_payables"), t("rat_days_unit"))
        self.cards['operating_cycle'].retranslate(t("rat_operating_cycle"), t("rat_days_unit"))
        self.cards['cash_conversion_cycle'].retranslate(t("rat_ccc"), t("rat_days_unit"))
        self.cards['debt_to_equity'].retranslate(t("rat_debt_equity"))
        self.cards['debt_ratio'].retranslate(t("rat_debt_ratio"))
        self.cards['equity_ratio'].retranslate(t("rat_equity_ratio"))
        self.refresh()
