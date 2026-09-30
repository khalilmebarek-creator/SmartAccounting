# القوائم المالية المرئية (Visual Financial Statements)
# =====================================================
# عرض مركّز بالألوان للقوائم الثلاث (المركز المالي + الدخل + التدفقات)
# بطاقات KPI + أشرطة مقارنة + صفوف ملوّنة. البيانات من modules.ias_reports.
# كل الألوان من ThemeColors (متوافقة مع الثيمات الثلاثة).

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QPushButton,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush

from ui.views._base import BaseView
from ui.resources.i18n import t
from ui.app_state import ThemeColors
from modules.ias_reports import generate_all


class _CompareBar(QWidget):
    """شريطا مقارنة أفقيان (أصول مقابل خصوم+حقوق) بمقياس موحّد."""

    def __init__(self, label_a="", value_a=0, color_a=None,
                 label_b="", value_b=0, color_b=None):
        super().__init__()
        self.label_a = label_a
        self.value_a = max(0.0, float(value_a or 0))
        self.color_a = color_a or ThemeColors.get("info")
        self.label_b = label_b
        self.value_b = max(0.0, float(value_b or 0))
        self.color_b = color_b or ThemeColors.get("error")
        self.setMinimumHeight(84)

    def update_values(self, label_a, value_a, color_a, label_b, value_b, color_b):
        self.label_a = label_a
        self.value_a = max(0.0, float(value_a or 0))
        self.color_a = color_a
        self.label_b = label_b
        self.value_b = max(0.0, float(value_b or 0))
        self.color_b = color_b
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        row_h = 34
        max_v = max(self.value_a, self.value_b, 1.0)
        text_color = QColor(ThemeColors.get("text"))

        def draw_row(y, label, value, color):
            p.setPen(text_color)
            p.drawText(QRectF(0, y, w * 0.38, row_h),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       f"{label}")
            bar_x = w * 0.40
            bar_w = w * 0.40
            ratio = value / max_v
            grad = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            grad.setColorAt(0.0, QColor(color))
            grad.setColorAt(1.0, QColor(color).darker(130))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(QRectF(bar_x, y + 8, bar_w * ratio, row_h - 16), 6, 6)
            p.setPen(text_color)
            p.drawText(QRectF(bar_x + bar_w + 8, y, w - bar_x - bar_w - 8, row_h),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                       f"{value:,.0f}")

        draw_row(0, self.label_a, self.value_a, self.color_a)
        draw_row(row_h + 10, self.label_b, self.value_b, self.color_b)


def _money_row(label, value, color=None, bold=False):
    """صف (تسمية + قيمة ملوّنة) داخل بطاقة."""
    row = QFrame()
    lay = QHBoxLayout()
    lay.setContentsMargins(0, 2, 0, 2)
    lbl = QLabel(label)
    lbl.setStyleSheet(f"color: {ThemeColors.get('text_secondary')};")
    val = QLabel(f"{value:,.2f}" if isinstance(value, (int, float)) else str(value))
    val.setStyleSheet(f"color: {color or ThemeColors.get('text')}; "
                      f"font-weight: {'bold' if bold else 'normal'};")
    val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    lay.addWidget(lbl, 1)
    lay.addWidget(val)
    row.setLayout(lay)
    return row


class FinancialStatementsView(BaseView):
    """عرض مرئي للقوائم المالية"""

    def __init__(self):
        super().__init__()
        self._data = {}
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("fs_title", "fs_subtitle")

        btns = QHBoxLayout()
        self.refresh_btn = QPushButton(t("ias_refresh"))
        self.refresh_btn.clicked.connect(self.refresh)
        btns.addWidget(self.refresh_btn)
        btns.addStretch()
        self._main_layout.addLayout(btns)

        # بطاقات KPI
        stats = QHBoxLayout()
        self._stat_assets, self._val_assets = self._make_stat(t("ias_total_assets"))
        self._stat_equity, self._val_equity = self._make_stat(t("ias_total_equity"))
        self._stat_income, self._val_income = self._make_stat(t("ias_net_income"))
        self._stat_cash, self._val_cash = self._make_stat(t("er_ending_cash"))
        for s in (self._stat_assets, self._stat_equity, self._stat_income, self._stat_cash):
            stats.addWidget(s, 1)
        self._main_layout.addLayout(stats)

        # المركز المالي
        bs_card = self._make_card("fs_balance_sheet")
        self._compare_bar = _CompareBar()
        bs_card.layout().addWidget(self._compare_bar)
        self._main_layout.addWidget(bs_card)

        # قائمة الدخل
        inc_card = self._make_card("fs_income_statement")
        self._inc_layout = QVBoxLayout()
        inc_card.layout().addLayout(self._inc_layout)
        self._main_layout.addWidget(inc_card)

        # التدفقات النقدية
        cf_card = self._make_card("fs_cash_flow")
        self._cf_layout = QVBoxLayout()
        cf_card.layout().addLayout(self._cf_layout)
        self._main_layout.addWidget(cf_card)

        self._main_layout.addStretch()

    def refresh(self):
        self._data = generate_all()

        bs = self._data.get("balance_sheet", {})
        eqliab = bs.get("equity_liabilities", {})
        total_assets = bs.get("total_assets", 0)
        total_eqliab = bs.get("total_equity_liabilities", 0)
        total_equity = eqliab.get("total_equity", 0)

        self._val_assets.setText(f"{total_assets:,.0f}")
        self._val_equity.setText(f"{total_equity:,.0f}")
        self._val_income.setText(f"{self._data.get('income_statement', {}).get('net_income', 0):,.0f}")
        self._val_cash.setText(f"{self._data.get('cash_flow', {}).get('cash_ending', 0):,.0f}")

        # تحديث شريط المقارنة
        self._compare_bar.update_values(
            t("fs_assets"), total_assets, ThemeColors.get("info"),
            t("fs_liabilities_equity"), total_eqliab, ThemeColors.get("error"),
        )

        self._render_income()
        self._render_cashflow()

    def _render_income(self):
        inc = self._data.get("income_statement", {})
        while self._inc_layout.count():
            item = self._inc_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        rows = [
            (t("ias_revenue"), inc.get("revenue", 0), ThemeColors.get("success"), False),
            (t("ias_cogs"), abs(inc.get("cogs", inc.get("cost_of_goods_sold", 0))),
             ThemeColors.get("error"), False),
            (t("ias_gross_profit"), inc.get("gross_profit", 0), ThemeColors.get("info"), True),
            (t("ias_operating_expenses"), abs(inc.get("operating_expenses", 0)),
             ThemeColors.get("error"), False),
            (t("ias_net_income"), inc.get("net_income", 0), ThemeColors.get("success"), True),
        ]
        for label, value, color, bold in rows:
            self._inc_layout.addWidget(_money_row(label, value, color, bold))

    def _render_cashflow(self):
        cf = self._data.get("cash_flow", {})
        while self._cf_layout.count():
            item = self._cf_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        rows = [
            (t("ias_operating_activities"), cf.get("operating_total", 0),
             ThemeColors.get("success"), False),
            (t("ias_investing_activities"), cf.get("investing_total", 0),
             ThemeColors.get("info"), False),
            (t("ias_financing_activities"), cf.get("financing_total", 0),
             ThemeColors.get("warning"), False),
            (t("er_ending_cash"), cf.get("cash_ending", 0), ThemeColors.get("success"), True),
        ]
        for label, value, color, bold in rows:
            self._cf_layout.addWidget(_money_row(label, value, color, bold))
