# منصة الذكاء الاصطناعي المتكاملة — مركز القيادة
# ================================================
# Health Score • Risk Radar • Executive Summary • Recommendations

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame, QSizePolicy, QProgressBar, QScrollArea,
    QWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.ai_platform import platform_analysis


class AIPlatformView(BaseView):
    """مركز قيادة الذكاء الاصطناعي المتكامل"""

    def __init__(self):
        super().__init__()
        self._result = {}
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("ai_platform_title", "ai_platform_subtitle")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        self._inner_layout = QVBoxLayout()
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(8)

        # صف 1: Health Score
        score_row = QHBoxLayout()
        self._health_card = QFrame()
        self._health_card.setObjectName("card")
        hl = QVBoxLayout()
        hl.setContentsMargins(16, 12, 16, 12)
        self._health_title = QLabel(t("ai_platform_health"))
        self._health_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E293B;")
        hl.addWidget(self._health_title)
        self._health_value = QLabel("—")
        self._health_value.setStyleSheet("font-size: 48px; font-weight: bold;")
        self._health_value.setAlignment(Qt.AlignCenter)
        hl.addWidget(self._health_value)
        self._health_grade = QLabel("")
        self._health_grade.setAlignment(Qt.AlignCenter)
        self._health_grade.setStyleSheet("font-size: 16px; font-weight: bold;")
        hl.addWidget(self._health_grade)
        self._health_card.setLayout(hl)
        score_row.addWidget(self._health_card)

        # صف 2: المحاور الستة
        self._breakdown_layout = QVBoxLayout()
        bd_card = QFrame()
        bd_card.setObjectName("card")
        bl = QVBoxLayout()
        bl.setContentsMargins(16, 12, 16, 12)
        bl.addWidget(QLabel(t("ai_platform_breakdown")))
        self._breakdown_bars = {}
        for key in ("profitability", "liquidity", "leverage", "efficiency", "growth", "stability"):
            row_w = QWidget()
            rl = QHBoxLayout()
            rl.setContentsMargins(0, 2, 0, 2)
            lbl = QLabel(t(f"ai_platform_{key}"))
            lbl.setFixedWidth(120)
            rl.addWidget(lbl)
            bar = QProgressBar()
            bar.setMaximum(30 if key == "profitability" else
                           20 if key in ("liquidity",) else
                           15 if key in ("leverage", "efficiency") else 10)
            bar.setTextVisible(True)
            bar.setFormat("%v")
            bar.setFixedHeight(22)
            self._breakdown_bars[key] = bar
            rl.addWidget(bar)
            row_w.setLayout(rl)
            bl.addWidget(row_w)
        bd_card.setLayout(bl)
        self._breakdown_layout.addWidget(bd_card)

        score_row.addLayout(self._breakdown_layout)
        self._inner_layout.addLayout(score_row)

        # صف 3: Risk Radar
        radar_card = QFrame()
        radar_card.setObjectName("card")
        rl = QVBoxLayout()
        rl.setContentsMargins(16, 12, 16, 12)
        rl.addWidget(QLabel(t("ai_platform_risk_radar")))
        self._radar_bars = {}
        radar_row = QHBoxLayout()
        for key in ("liquidity_risk", "leverage_risk", "profitability_risk",
                     "efficiency_risk", "growth_risk", "solvency_risk"):
            col = QVBoxLayout()
            lbl = QLabel(t(f"ai_platform_{key}"))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 10px;")
            col.addWidget(lbl)
            bar = QProgressBar()
            bar.setOrientation(Qt.Vertical)
            bar.setFixedWidth(32)
            bar.setFixedHeight(100)
            bar.setMaximum(100)
            bar.setTextVisible(False)
            self._radar_bars[key] = bar
            col.addWidget(bar, 0, Qt.AlignCenter)
            val = QLabel("0")
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet("font-size: 10px; font-weight: bold;")
            self._radar_bars[key + "_val"] = val
            col.addWidget(val)
            radar_row.addLayout(col)
        rl.addLayout(radar_row)
        radar_card.setLayout(rl)
        self._inner_layout.addWidget(radar_card)

        # صف 4: Executive Summary
        summary_card = QFrame()
        summary_card.setObjectName("card")
        sl = QVBoxLayout()
        sl.setContentsMargins(16, 12, 16, 12)
        sl.addWidget(QLabel(t("ai_platform_summary")))
        self._summary_list = QVBoxLayout()
        sl.addLayout(self._summary_list)
        summary_card.setLayout(sl)
        self._inner_layout.addWidget(summary_card)

        # صف 5: Recommendations
        rec_card = QFrame()
        rec_card.setObjectName("card")
        recl = QVBoxLayout()
        recl.setContentsMargins(16, 12, 16, 12)
        recl.addWidget(QLabel(t("ai_platform_recommendations")))
        self._rec_layout = QVBoxLayout()
        recl.addLayout(self._rec_layout)
        rec_card.setLayout(recl)
        self._inner_layout.addWidget(rec_card)

        # صف 6: روابط سريعة
        links_card = QFrame()
        links_card.setObjectName("card")
        ll = QVBoxLayout()
        ll.setContentsMargins(16, 12, 16, 12)
        ll.addWidget(QLabel(t("ai_platform_quick_links")))
        links_row = QHBoxLayout()
        links = [("sidebar_ai_insights", 24), ("sidebar_forecast", 14),
                 ("sidebar_scenarios", 22), ("sidebar_benchmarks", 18),
                 ("sidebar_ias", 38)]
        for label_key, vid in links:
            btn = QPushButton(t(label_key))
            btn.clicked.connect(lambda checked, v=vid: self._go_via_main(v))
            links_row.addWidget(btn)
        links_row.addStretch()
        ll.addLayout(links_row)
        links_card.setLayout(ll)
        self._inner_layout.addWidget(links_card)

        self._inner_layout.addStretch()
        inner.setLayout(self._inner_layout)
        scroll.setWidget(inner)
        self._main_layout.addWidget(scroll)

    def _go_via_main(self, vid):
        w = self
        while w is not None:
            if hasattr(w, '_go_to_view'):
                w._go_to_view(vid)
                return
            w = w.parent()

    # ── Refresh ──────────────────────────────────────────────────────────────

    def refresh(self):
        self._result = platform_analysis()
        self._render_health()
        self._render_radar()
        self._render_summary()
        self._render_recommendations()

    def _render_health(self):
        hs = self._result.get("health_score", {})
        total = hs.get("total", 0)
        grade = hs.get("grade", ("?", "", "#888"))
        color = grade[2]
        self._health_value.setText(f"{total:.0f}")
        self._health_value.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {color};")
        from ui.resources.i18n import t as _t
        self._health_grade.setText(f"{grade[0]} — {_t(grade[1])}")
        self._health_grade.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")
        for k, v in hs.get("breakdown", {}).items():
            if k in self._breakdown_bars:
                self._breakdown_bars[k].setValue(int(v))

    def _render_radar(self):
        radar = self._result.get("risk_radar", {})
        for k, v in radar.items():
            if k in self._radar_bars:
                self._radar_bars[k].setValue(int(v))
                color = "#22C55E" if v < 30 else "#F59E0B" if v < 60 else "#EF4444"
                self._radar_bars[k].setStyleSheet(
                    f"QProgressBar::chunk {{ background: {color}; }} QProgressBar {{ background: #E5E7EB; border: none; border-radius: 4px; }}")
                if k + "_val" in self._radar_bars:
                    self._radar_bars[k + "_val"].setText(f"{int(v)}")

    def _render_summary(self):
        sl = self._summary_list
        while sl.count():
            item = sl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for point in self._result.get("executive_summary", []):
            lbl = QLabel(f"• {point}")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px; padding: 4px 8px;")
            sl.addWidget(lbl)

    def _render_recommendations(self):
        rl = self._rec_layout
        while rl.count():
            item = rl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for rec in self._result.get("recommendations", []):
            frame = QFrame()
            frame.setStyleSheet(
                "QFrame { background: #FEF3C7; border-left: 4px solid #F59E0B; "
                "border-radius: 6px; padding: 8px; margin: 2px 0; }"
                if rec["priority"] == "high" else
                "QFrame { background: #DBEAFE; border-left: 4px solid #3B82F6; "
                "border-radius: 6px; padding: 8px; margin: 2px 0; }"
                if rec["priority"] == "medium" else
                "QFrame { background: #D1FAE5; border-left: 4px solid #22C55E; "
                "border-radius: 6px; padding: 8px; margin: 2px 0; }"
            )
            fl = QVBoxLayout()
            fl.setContentsMargins(8, 6, 8, 6)
            act = QLabel(rec["action"])
            act.setWordWrap(True)
            act.setStyleSheet("font-weight: bold; font-size: 12px; border: none; background: transparent;")
            fl.addWidget(act)
            imp = QLabel(f"💡 {rec['impact']}")
            imp.setWordWrap(True)
            imp.setStyleSheet("font-size: 11px; color: #555; border: none; background: transparent;")
            fl.addWidget(imp)
            frame.setLayout(fl)
            rl.addWidget(frame)
