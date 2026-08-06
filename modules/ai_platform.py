# منصة الذكاء الاصطناعي المتكاملة
# ================================
# محرك توصيات موحّد + تحليل متعدد الأبعاد + تقارير ذكية + تنبيهات استباقية

from datetime import date, datetime
from utils.app_logger import get_logger

log = get_logger("ai_platform")


class AIPlatform:
    """المنصة الموحدة للذكاء الاصطناعي المالي."""

    def __init__(self):
        self._context = {}
        self._alerts = []
        self._insights = []

    def analyze(self, financial_data, ratios=None, history=None):
        """تحليل شامل متعدد الأبعاد. Returns: dict with all insights."""
        ratios = ratios or {}
        history = history or []
        self._insights = []

        self._analyze_profitability(financial_data, ratios)
        self._analyze_liquidity(financial_data, ratios)
        self._analyze_leverage(financial_data, ratios)
        self._analyze_efficiency(financial_data, ratios)
        if history:
            self._analyze_trends(history)
        self._analyze_tax_burden(financial_data, ratios)

        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "summary": self._summary(),
            "insights": self._insights,
            "alerts": self._alerts,
            "recommendations": self._recommendations(),
            "health_score": self._health_score(),
        }

    def _analyze_profitability(self, fd, ratios):
        revenue = float(fd.get("revenue") or 0)
        net = float(fd.get("net_income") or 0)
        roe = float(ratios.get("roe") or 0)
        npm = float(ratios.get("net_profit_margin") or 0)

        if revenue > 0 and net > 0:
            if npm > 15:
                self._insights.append({
                    "area": "profitability",
                    "level": "excellent",
                    "message": "ربحية ممتازة — هامش صافي أعلى من 15%",
                })
            elif npm > 5:
                self._insights.append({
                    "area": "profitability",
                    "level": "good",
                    "message": "ربحية جيدة — هامش صافي بين 5-15%",
                })
            else:
                self._insights.append({
                    "area": "profitability",
                    "level": "warning",
                    "message": "هامش ربح منخفض — أقل من 5%. راجع هيكل التكاليف.",
                })
                self._alerts.append({
                    "area": "profitability",
                    "severity": "warning",
                    "message": "انخفاض هامش الربح",
                })
        if net < 0:
            self._alerts.append({
                "area": "profitability",
                "severity": "danger",
                "message": "خسارة صافية! تدخل فوري مطلوب.",
            })

    def _analyze_liquidity(self, fd, ratios):
        cr = float(ratios.get("current_ratio") or 0)
        qr = float(ratios.get("quick_ratio") or 0)
        cash = float(fd.get("cash") or 0)
        cl = float(fd.get("current_liabilities") or 0)

        if cr > 0:
            if cr > 2:
                self._insights.append({
                    "area": "liquidity",
                    "level": "good",
                    "message": f"سيولة قوية — نسبة التداول {cr:.1f}",
                })
            elif cr > 1:
                self._insights.append({
                    "area": "liquidity",
                    "level": "ok",
                    "message": f"سيولة مقبولة — نسبة التداول {cr:.1f}",
                })
            elif cr > 0.5:
                self._alerts.append({
                    "area": "liquidity",
                    "severity": "warning",
                    "message": f"سيولة ضعيفة — نسبة التداول {cr:.1f}",
                })
            else:
                self._alerts.append({
                    "area": "liquidity",
                    "severity": "danger",
                    "message": f"خطر سيولة — نسبة التداول {cr:.1f}",
                })
        if cash > 0 and cl > 0 and cash < cl * 0.3:
            self._alerts.append({
                "area": "liquidity",
                "severity": "warning",
                "message": "نقدية منخفضة مقارنة بالالتزامات الجارية",
            })

    def _analyze_leverage(self, fd, ratios):
        de = float(ratios.get("debt_to_equity") or 0)
        dr = float(ratios.get("debt_ratio") or 0)
        if de > 0:
            if de > 2:
                self._insights.append({
                    "area": "leverage",
                    "level": "warning",
                    "message": f"مديونية مرتفعة — الديون/حقوق الملكية {de:.1f}",
                })
            elif de < 1:
                self._insights.append({
                    "area": "leverage",
                    "level": "good",
                    "message": "هيكل تمويل متوازن",
                })

    def _analyze_efficiency(self, fd, ratios):
        at = float(ratios.get("asset_turnover") or 0)
        it = float(ratios.get("inventory_turnover") or 0)
        if at > 0:
            if at < 1:
                self._insights.append({
                    "area": "efficiency",
                    "level": "warning",
                    "message": "دوران أصول منخفض — أصول غير مستغلة",
                })

    def _analyze_trends(self, history):
        if len(history) < 3:
            return
        revenues = [float(h.get("revenue") or 0) for h in history[-6:]]
        if len(revenues) >= 3:
            growth = sum(1 for i in range(1, len(revenues)) if revenues[i] > revenues[i-1])
            trend = growth / (len(revenues) - 1) if len(revenues) > 1 else 0
            if trend > 0.7:
                self._insights.append({
                    "area": "growth",
                    "level": "good",
                    "message": "اتجاه نمو تصاعدي في الإيرادات",
                })
            elif trend < 0.3:
                self._alerts.append({
                    "area": "growth",
                    "severity": "warning",
                    "message": "انخفاض متكرر في الإيرادات",
                })

    def _analyze_tax_burden(self, fd, ratios):
        revenue = float(fd.get("revenue") or 0)
        net = float(fd.get("net_income") or 0)
        if revenue > 0 and net > 0:
            burden = round((revenue - net) / revenue * 100, 1)
            if burden > 40:
                self._insights.append({
                    "area": "tax",
                    "level": "info",
                    "message": f"العبء الإجمالي (ضرائب + تكاليف) مرتفع: {burden}%",
                })

    def _summary(self):
        warnings = len(self._alerts)
        insights = len(self._insights)
        if warnings == 0:
            return "الوضع المالي مستقر. لا توجد تحذيرات."
        elif warnings <= 2:
            return f"توجد {warnings} تحذيرات تستدعي الانتباه."
        else:
            return f"توجد {warnings} تحذيرات. يوصى بمراجعة فورية."

    def _recommendations(self):
        recs = []
        for a in self._alerts:
            area = a.get("area", "")
            sev = a.get("severity", "")
            tips = {
                ("profitability", "danger"): "خفض المصاريف التشغيلية فوراً ومراجعة الأسعار",
                ("profitability", "warning"): "تحليل هيكل التكاليف وتحسين الهوامش",
                ("liquidity", "danger"): "تأمين تمويل قصير الأجل فوراً",
                ("liquidity", "warning"): "تحسين إدارة الذمم المدينة والنقدية",
                ("growth", "warning"): "تنويع المنتجات وفتح أسواق جديدة",
            }
            tip = tips.get((area, sev))
            if tip and tip not in recs:
                recs.append(tip)
        if not recs:
            recs.append("مواصلة الاستراتيجية الحالية مع المراقبة الدورية")
        return recs

    def _health_score(self):
        """صحة مالية 0-100."""
        score = 100
        for a in self._alerts:
            sev = a.get("severity")
            if sev == "danger":
                score -= 25
            elif sev == "warning":
                score -= 10
        return max(score, 0)

    def generate_alert_report(self):
        """تقرير تنبيهات نصي."""
        if not self._alerts:
            return "لا توجد تنبيهات حالية."
        lines = ["=" * 60, "  تقرير التنبيهات الذكية", "=" * 60, ""]
        for a in self._alerts:
            sev_icon = {"danger": "🔴", "warning": "🟡", "info": "🔵"}.get(
                a.get("severity"), "⚪")
            lines.append(f"  {sev_icon} {a['message']}")
        lines.append("")
        lines.append(f"  درجة الصحة المالية: {self._health_score()}/100")
        return "\n".join(lines)

    def generate_insight_report(self):
        """تقرير الرؤى الذكية نصي."""
        if not self._insights:
            return "لا توجد رؤى جديدة."
        lines = ["=" * 60, "  تقرير الرؤى الذكية", "=" * 60, ""]
        for ins in self._insights:
            level_icon = {"excellent": "⭐", "good": "✅", "ok": "✔️",
                          "info": "ℹ️", "warning": "⚠️"}.get(
                ins.get("level"), "•")
            lines.append(f"  {level_icon} [{ins['area']}] {ins['message']}")
        return "\n".join(lines)


ai_platform = AIPlatform()
