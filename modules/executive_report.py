# التقرير التنفيذي الشامل (Executive Report)
# ==========================================
# يجمع كل التحليلات في تقرير واحد موحّد:
#   درجة الصحة المالية • الملخص التنفيذي • النسب الرئيسية • القوائم المالية
#   الملخص الجبائي • التوصيات الاستراتيجية
# إخراج: نص عادي + HTML (للمعاينة والتصدير).

from datetime import datetime
from typing import Dict, List, Any

from ui.app_state import state


# نسبة المفتاح → مفتاح التسمية في i18n
KEY_RATIOS: List[tuple] = [
    ("current_ratio", "rat_current_ratio"),
    ("quick_ratio", "rat_quick_ratio"),
    ("gross_profit_margin", "rat_gross_margin"),
    ("net_profit_margin", "rat_net_margin"),
    ("operating_margin", "rat_operating_margin"),
    ("roe", "rat_roe_label"),
    ("return_on_assets", "rat_roa"),
    ("debt_to_equity", "rat_debt_equity"),
    ("debt_ratio", "rat_debt_ratio"),
    ("interest_coverage", "er_interest_coverage"),
    ("asset_turnover", "rat_asset_turnover"),
    ("inventory_turnover", "rat_inventory_turnover"),
    ("receivables_turnover", "rat_receivables_turnover"),
    ("z_score", "er_z_score"),
]


def _safe(v, default=0.0):
    return float(v) if v is not None else default


def _tax_rows(ts):
    """تحويل ملخص الضرائب إلى صفوف (مفتاح تسمية، قيمة)."""
    if not ts:
        return []
    ibs = ts.get("ibs") or {}
    return [
        ("er_tax_ibs", _safe(ibs.get("tax_amount"))),
        ("er_tax_cnas", _safe(ts.get("cnas_annual"))),
        ("er_tax_cnac", _safe(ts.get("cnac_annual"))),
        ("er_tax_irg", _safe(ts.get("irg_annual"))),
        ("er_tax_vf", _safe(ts.get("vf_annual"))),
        ("er_tax_total", _safe(ts.get("total_taxes"))),
        ("er_tax_burden_pct", _safe(ts.get("tax_burden_pct"))),
    ]


def build_report() -> Dict[str, Any]:
    """تجميع كل التحليلات في هيكل تقرير واحد."""
    from modules.ai_platform import platform_analysis
    from modules.ias_reports import generate_all as ias_all

    analysis = platform_analysis()
    statements = ias_all()
    ratios = state.ratios or {}
    data = state.financial_data or {}

    return {
        "company_name": state.company_name or state.company_name_fr or "",
        "fiscal_year": data.get("fiscal_year", state.fiscal_year or 2024),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "health_score": analysis.get("health_score", {}),
        "executive_summary": analysis.get("executive_summary", []),
        "recommendations": analysis.get("recommendations", []),
        "key_ratios": [(key, ratios.get(key)) for key, _ in KEY_RATIOS],
        "balance_sheet": statements.get("balance_sheet", {}),
        "income_statement": statements.get("income_statement", {}),
        "cash_flow": statements.get("cash_flow", {}),
        "equity_statement": statements.get("equity_statement", {}),
        "tax_rows": _tax_rows(state.tax_summary),
    }


# ── نص عادي ─────────────────────────────────────────────────────────────────


def render_text(report: Dict[str, Any]) -> str:
    """تقرير نصي بسيط (يُستخدم للتصدير البسيط)."""
    from ui.resources.i18n import t

    lines = []
    lines.append("=" * 60)
    lines.append(t("er_title"))
    lines.append("=" * 60)
    lines.append(f"{t('er_company')}: {report.get('company_name') or '-'}")
    lines.append(f"{t('er_year')}: {report.get('fiscal_year')}")
    lines.append(f"{t('er_generated_at')}: {report.get('generated_at')}")
    lines.append("")

    hs = report.get("health_score", {})
    lines.append(f"{t('er_health_score')}: {hs.get('total', 0)}/100")
    lines.append("")

    lines.append(t("er_summary") + ":")
    for point in report.get("executive_summary", []):
        lines.append(f"  • {point}")
    lines.append("")

    lines.append(t("er_key_ratios") + ":")
    for (key, value) in report.get("key_ratios", []):
        if value is not None:
            lines.append(f"  - {t(KEY_RATIOS_KEY[key])}: {value:,.2f}")
    lines.append("")

    if report.get("tax_rows"):
        lines.append(t("er_tax_summary") + ":")
        for label_key, value in report.get("tax_rows", []):
            lines.append(f"  - {t(label_key)}: {value:,.2f}")
        lines.append("")

    lines.append(t("er_recommendations") + ":")
    for rec in report.get("recommendations", []):
        lines.append(f"  [{t('er_priority_' + rec.get('priority', 'low'))}] {rec.get('action', '')}")
    lines.append("")

    return "\n".join(lines)


# خريطة مساعدة: مفتاح النسبة → مفتاح التسمية
KEY_RATIOS_KEY = dict(KEY_RATIOS)


# ── HTML ────────────────────────────────────────────────────────────────────


# لوحة ألوان افتراضية (وثيقة فاتحة — تُستخدم للتصدير PDF)
_DEFAULT_COLORS = {
    "primary": "#7C4DFF",
    "info": "#3B82F6",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "success": "#22C55E",
    "text": "#222222",
    "secondary": "#555555",
    "border": "#dddddd",
    "muted": "#888888",
}


def render_html(report: Dict[str, Any], colors: Dict[str, str] = None) -> str:
    """تقرير HTML ملوّن (للمعاينة داخل التطبيق أو التصدير).

    ``colors`` اختياري — لوحة ألوان متوافقة مع الثيم (المفاتيح: primary/info/
    warning/error/success/text/secondary/border/muted). عند غيابها تُستخدم
    لوحة وثيقة فاتحة مناسبة للطباعة.
    """
    from ui.resources.i18n import t
    import html as _html

    esc = _html.escape
    c = colors or _DEFAULT_COLORS

    parts = []
    parts.append(f'<div style="font-family:Segoe UI, Tahoma, sans-serif;color:{c["text"]};">')

    # الترويسة
    comp = esc(str(report.get("company_name") or "-"))
    fy = esc(str(report.get("fiscal_year") or "-"))
    gen = esc(str(report.get("generated_at") or "-"))
    parts.append(f'<h1 style="color:{c["primary"]};">{t("er_title")}</h1>')
    parts.append(f'<p style="color:{c["secondary"]};"><b>{t("er_company")}:</b> {comp} &nbsp;|&nbsp; '
                 f'<b>{t("er_year")}:</b> {fy} &nbsp;|&nbsp; <b>{t("er_generated_at")}:</b> {gen}</p>')

    # درجة الصحة
    hs = report.get("health_score", {})
    total = hs.get("total", 0)
    grade = hs.get("grade", ("-", "", "#888"))[0]
    color = hs.get("grade", ("-", "", "#888"))[2]
    parts.append(f'<h2>{t("er_health_score")}</h2>')
    parts.append(f'<div style="background:{color};color:#fff;display:inline-block;'
                 f'padding:10px 22px;border-radius:8px;font-size:26px;font-weight:bold;">'
                 f'{total} / 100 &nbsp; ({grade})</div>')

    # الملخص التنفيذي
    parts.append(f'<h2>{t("er_summary")}</h2><ul>')
    for point in report.get("executive_summary", []):
        parts.append(f"<li>{esc(str(point))}</li>")
    parts.append("</ul>")

    # النسب الرئيسية
    parts.append(f'<h2>{t("er_key_ratios")}</h2>')
    parts.append('<table border="1" cellspacing="0" cellpadding="6" '
                 f'style="border-collapse:collapse;border-color:{c["border"]};width:100%;">')
    parts.append(f'<tr style="background:{c["primary"]};color:#fff;">'
                 f'<th style="text-align:left;">{t("er_ratio")}</th>'
                 f'<th style="text-align:right;">{t("er_value")}</th></tr>')
    for key, value in report.get("key_ratios", []):
        if value is None:
            continue
        label = t(KEY_RATIOS_KEY.get(key, key))
        parts.append(f'<tr><td>{esc(label)}</td>'
                     f'<td style="text-align:right;">{_safe(value):,.2f}</td></tr>')
    parts.append("</table>")

    # القوائم المالية (ملخص)
    parts.append(f'<h2>{t("er_financial_statements")}</h2>')
    parts.append('<table border="1" cellspacing="0" cellpadding="6" '
                 f'style="border-collapse:collapse;border-color:{c["border"]};width:100%;">')
    parts.append(f'<tr style="background:{c["info"]};color:#fff;">'
                 f'<th style="text-align:left;">{t("er_statement")}</th>'
                 f'<th style="text-align:right;">{t("er_value")}</th></tr>')
    bs = report.get("balance_sheet", {})
    inc = report.get("income_statement", {})
    cf = report.get("cash_flow", {})
    eq = report.get("equity_statement", {})
    summary_rows = [
        ("er_total_assets", bs.get("total_assets", 0)),
        ("er_total_equity", bs.get("equity_liabilities", {}).get("total_equity", 0)),
        ("er_net_income", inc.get("net_income", 0)),
        ("er_gross_profit", inc.get("gross_profit", 0)),
        ("er_operating_cashflow", cf.get("operating_total", 0)),
        ("er_ending_cash", cf.get("cash_ending", 0)),
        ("er_closing_equity", eq.get("closing_balance", 0)),
    ]
    for label_key, value in summary_rows:
        parts.append(f'<tr><td>{esc(t(label_key))}</td>'
                     f'<td style="text-align:right;">{_safe(value):,.2f}</td></tr>')
    parts.append("</table>")

    # الملخص الجبائي
    if report.get("tax_rows"):
        parts.append(f'<h2>{t("er_tax_summary")}</h2>')
        parts.append('<table border="1" cellspacing="0" cellpadding="6" '
                     f'style="border-collapse:collapse;border-color:{c["border"]};width:100%;">')
        parts.append(f'<tr style="background:{c["warning"]};color:#fff;">'
                     f'<th style="text-align:left;">{t("er_tax")}</th>'
                     f'<th style="text-align:right;">{t("er_value")}</th></tr>')
        for label_key, value in report.get("tax_rows", []):
            parts.append(f'<tr><td>{esc(t(label_key))}</td>'
                         f'<td style="text-align:right;">{_safe(value):,.2f}</td></tr>')
        parts.append("</table>")

    # التوصيات
    parts.append(f'<h2>{t("er_recommendations")}</h2><ul>')
    prio_colors = {"high": c["error"], "medium": c["warning"], "low": c["success"]}
    for rec in report.get("recommendations", []):
        pr = rec.get("priority", "low")
        color = prio_colors.get(pr, c["muted"])
        action = esc(str(rec.get("action", "")))
        impact = esc(str(rec.get("impact", "")))
        parts.append(f'<li><span style="color:{color};font-weight:bold;">'
                     f'[{t("er_priority_" + pr)}]</span> {action} '
                     f'<span style="color:{c["muted"]};">({impact})</span></li>')
    parts.append("</ul>")

    parts.append("</div>")
    return "".join(parts)
