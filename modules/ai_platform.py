# منصة الذكاء الاصطناعي المتكاملة
# =================================
# تجمع كل محركات التحليل الذكي في طبقة تنسيق موحّدة
# Health Score (0-100) • Risk Radar • Executive Summary • Recommendations

from typing import Dict, List, Any, Optional
from ui.app_state import state


def _f(key, default=0.0):
    v = (state.financial_data or {}).get(key) or (state.ratios or {}).get(key)
    return float(v) if v else default


def _r(key, default=0.0):
    return float((state.ratios or {}).get(key, default)) or default


# ── Health Score (0-100) ────────────────────────────────────────────────────


def compute_health_score() -> Dict[str, Any]:
    """درجة الصحة المالية من 0-100 مبنية على 6 محاور."""
    scores = {}

    # 1. الربحية (30 نقطة)
    roe = _r("roe")
    npm = _r("net_profit_margin")
    scores["profitability"] = min(30, max(0, (min(roe, 40) / 40) * 15 + (min(npm, 30) / 30) * 15))

    # 2. السيولة (20 نقطة)
    cr = _r("current_ratio")
    qr = _r("quick_ratio")
    scores["liquidity"] = min(20, max(0, (min(cr, 3) / 3) * 10 + (min(qr, 2) / 2) * 10))

    # 3. المديونية (15 نقطة)
    de = _r("debt_to_equity")
    dar = _r("debt_ratio")
    scores["leverage"] = min(15, max(0, 15 - (min(de, 3) / 3) * 8 - (min(dar, 1) / 1) * 7))

    # 4. الكفاءة (15 نقطة)
    inv_turn = _r("inventory_turnover")
    ar_turn = _r("receivables_turnover")
    scores["efficiency"] = min(15, max(0, (min(inv_turn, 12) / 12) * 7 + (min(ar_turn, 12) / 12) * 8))

    # 5. النمو (10 نقطة)
    gp = _f("gross_profit")
    rev = _f("revenue")
    ni = _f("net_income")
    gpm = (gp / rev * 100) if rev > 0 else 0
    nim = (ni / rev * 100) if rev > 0 else 0
    scores["growth"] = min(10, max(0, (min(gpm, 50) / 50) * 5 + (min(nim, 20) / 20) * 5))

    # 6. الاستقرار (10 نقطة) — Z-Score
    zs = _r("z_score")
    scores["stability"] = min(10, max(0, (max(0, min(zs, 4)) / 4) * 10))

    total = sum(scores.values())
    return {
        "total": round(total, 1),
        "grade": _grade(total),
        "breakdown": {k: round(v, 1) for k, v in scores.items()},
    }


def _grade(score):
    if score >= 80:
        return ("A", "ai_grade_excellent", "#22C55E")
    if score >= 60:
        return ("B", "ai_grade_good", "#3B82F6")
    if score >= 40:
        return ("C", "ai_grade_fair", "#F59E0B")
    if score >= 20:
        return ("D", "ai_grade_poor", "#EF4444")
    return ("E", "ai_grade_critical", "#DC2626")


# ── Risk Radar ──────────────────────────────────────────────────────────────


def compute_risk_radar() -> Dict[str, Any]:
    """رادار مخاطر 6 أبعاد بقيم 0-100."""
    return {
        "liquidity_risk": round(min(100, max(0, 100 - (_r("current_ratio") / 2) * 100)), 1),
        "leverage_risk": round(min(100, max(0, (_r("debt_to_equity") / 3) * 100)), 1),
        "profitability_risk": round(min(100, max(0, 100 - (_r("roe") / 30) * 100)), 1),
        "efficiency_risk": round(min(100, max(0, 100 - (_r("inventory_turnover") / 8) * 100)), 1),
        "growth_risk": round(min(100, max(0, 100 - (_r("net_profit_margin") / 20) * 100)), 1),
        "solvency_risk": round(min(100, max(0, (1 - min(_r("z_score"), 3) / 3) * 100)), 1),
    }


# ── Executive Summary ───────────────────────────────────────────────────────


def executive_summary() -> List[str]:
    """ملخص تنفيذي بالعربية من 5-8 نقاط."""
    hs = compute_health_score()
    points = []

    roe = _r("roe")
    npm = _r("net_profit_margin")
    cr = _r("current_ratio")
    de = _r("debt_to_equity")
    zs = _r("z_score")
    rev = _f("revenue")
    ni = _f("net_income")
    oe = _f("operating_expenses")

    points.append(f"درجة الصحة المالية: {hs['total']}/100 — تقييم {hs['grade'][0]}")

    if roe > 20:
        points.append(f"عائد قوي على حقوق الملكية ({roe:.1f}%) يفوق المعايير القطاعية.")
    elif roe > 10:
        points.append(f"عائد مقبول على حقوق الملكية ({roe:.1f}%) — مجال للتحسين في التحكم بالتكاليف.")
    else:
        points.append(f"عائد ضعيف على حقوق الملكية ({roe:.1f}%) — ينصح بمراجعة هيكل التكاليف والإيرادات.")

    if cr >= 2:
        points.append(f"سيولة مريحة ({cr:.1f}x) — الأصول المتداولة تغطي الخصوم المتداولة بأمان.")
    elif cr >= 1:
        points.append(f"سيولة حرجة ({cr:.1f}x) — ينصح بتحسين دورة التحصيل وتقليل الذمم المدينة.")
    else:
        points.append(f"⚠️ خطر سيولة ({cr:.1f}x) — الأصول المتداولة لا تغطي الخصوم المتداولة.")

    if de <= 1:
        points.append(f"هيكل تمويل متوازن (الدين/حقوق الملكية = {de:.2f}).")
    elif de <= 2:
        points.append(f"مديونية معتدلة ({de:.2f}) — تراقب عن كثب.")
    else:
        points.append(f"⚠️ مديونية مرتفعة ({de:.2f}) — خطر مالي يستوجب خفض الديون.")

    if zs >= 3:
        points.append(f"Z-Score آمن ({zs:.2f}) — الشركة في المنطقة الآمنة وبعيدة عن خطر الإفلاس.")
    elif zs >= 1.8:
        points.append(f"Z-Score في المنطقة الرمادية ({zs:.2f}) — ينصح بتحليل أعمق.")
    else:
        points.append(f"⚠️ Z-Score حرج ({zs:.2f}) — مؤشرات إنذار مبكر للإفلاس.")

    if ni > 0 and oe > 0:
        margin = (ni / rev * 100) if rev > 0 else 0
        points.append(f"هامش صافي الربح {margin:.1f}% — {'فوق' if margin > 10 else 'دون'} المتوسط.")

    return points


# ── Recommendations ─────────────────────────────────────────────────────────


def strategic_recommendations() -> List[Dict[str, Any]]:
    """توصيات استراتيجية مصنفة حسب الأولوية."""
    recs = []
    cr = _r("current_ratio")
    de = _r("debt_to_equity")
    roe = _r("roe")
    zs = _r("z_score")
    inv_turn = _r("inventory_turnover")

    if cr < 1.5:
        recs.append({"priority": "high", "action": "تحسين السيولة عبر تسريع تحصيل الذمم المدينة وتمديد آجال الدفع للموردين.",
                      "impact": "يخفض مخاطر العجز النقدي بنسبة تصل إلى 40%."})
    if de > 2:
        recs.append({"priority": "high", "action": "تخفيض المديونية عبر إعادة هيكلة القروض أو زيادة رأس المال.",
                      "impact": "يخفّض مصاريف الفوائد ويحسن التصنيف الائتماني."})
    if zs < 2.5:
        recs.append({"priority": "high", "action": "مراجعة شاملة للهيكل المالي — الشركة قريبة من المنطقة الحرجة.",
                      "impact": "يمنح فرصة للتدخل المبكر قبل تفاقم الأزمة."})
    if roe < 10:
        recs.append({"priority": "medium", "action": "تحسين الربحية عبر خفض التكاليف التشغيلية أو رفع الأسعار الانتقائي.",
                      "impact": "يرفع العائد على حقوق الملكية ويحسن التدفقات النقدية."})
    if inv_turn < 4:
        recs.append({"priority": "medium", "action": "تحسين إدارة المخزون — تصفية الأصناف بطيئة الحركة وتطبيق نظام JIT.",
                      "impact": "يحرر سيولة ويخفض تكاليف التخزين."})
    if not recs:
        recs.append({"priority": "low", "action": "الوضع المالي مستقر — استمر في مراقبة المؤشرات شهرياً.",
                      "impact": "يحافظ على الصحة المالية ويكتشف التغيرات مبكراً."})
    return recs


# ── Aggregate ───────────────────────────────────────────────────────────────


def platform_analysis() -> Dict[str, Any]:
    """التحليل الشامل للمنصة — جميع المؤشرات في مخرج واحد."""
    return {
        "health_score": compute_health_score(),
        "risk_radar": compute_risk_radar(),
        "executive_summary": executive_summary(),
        "recommendations": strategic_recommendations(),
        "company_name": state.company_name or "",
    }
