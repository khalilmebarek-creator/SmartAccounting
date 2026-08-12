# تقارير مالية معيارية IAS/IFRS
# =================================
# IAS 1: عرض القوائم المالية (المركز المالي، الدخل، التغيرات في حقوق الملكية)
# IAS 7: قائمة التدفقات النقدية (الطريقة غير المباشرة)

from typing import Dict, List, Any
from ui.app_state import state


def _safe(v, default=0.0):
    return float(v) if v is not None else default


def _fmt(amount):
    return f"{amount:,.2f}" if amount is not None else "—"


# ── جداول المعادلة المحاسبية ─────────────────────────────────────────────────


def _non_current_assets(data):
    ca = _safe(data.get("current_assets"))
    ta = _safe(data.get("total_assets"))
    return max(0, ta - ca)


def _non_current_liabilities(data):
    cl = _safe(data.get("current_liabilities"))
    tl = _safe(data.get("total_liabilities"))
    return max(0, tl - cl)


# ── IAS 1: Statement of Financial Position (Balance Sheet) ───────────────────


def generate_balance_sheet() -> Dict[str, Any]:
    """قائمة المركز المالي وفق IAS 1."""
    d = state.financial_data or {}
    nca = _non_current_assets(d)
    ca = _safe(d.get("current_assets"))
    inv = _safe(d.get("inventory"))
    cash_val = _safe(d.get("cash"))
    recv = _safe(d.get("avg_receivables"))
    ta = _safe(d.get("total_assets"))

    ncl = _non_current_liabilities(d)
    cl = _safe(d.get("current_liabilities"))
    tl = _safe(d.get("total_liabilities"))
    pay = _safe(d.get("avg_payables"))
    eq = _safe(d.get("equity"))
    re_val = _safe(d.get("retained_earnings")) or _safe(d.get("net_income"))
    other_eq = max(0, eq - re_val)

    return {
        "report_title": "Statement of Financial Position",
        "ia_as_at": state.financial_data.get("fiscal_year", 2024),
        "assets": {
            "non_current": [
                ("ias_ppe", nca if nca > 0 else 0),
            ],
            "total_non_current": nca if nca > 0 else 0,
            "current": [
                ("ias_inventory", inv),
                ("ias_receivables", recv),
                ("ias_cash", cash_val),
            ],
            "total_current": ca if ca > 0 else inv + recv + cash_val,
        },
        "total_assets": ta if ta > 0 else (nca + ca if ca > 0 else inv + recv + cash_val),
        "equity_liabilities": {
            "equity": [
                ("ias_share_capital", other_eq),
                ("ias_retained_earnings", re_val),
            ],
            "total_equity": eq if eq > 0 else other_eq + re_val,
            "non_current_liabilities": [
                ("ias_long_term_debt", ncl if ncl > 0 else 0),
            ],
            "total_non_current_liabilities": ncl if ncl > 0 else 0,
            "current_liabilities": [
                ("ias_payables", pay),
                ("ias_short_term_debt", max(0, cl - pay) if cl > 0 else 0),
            ],
            "total_current_liabilities": cl if cl > 0 else pay,
        },
        "total_equity_liabilities": tl if tl > 0 else (eq + cl if cl > 0 else eq),
    }


# ── IAS 1: Statement of Comprehensive Income ────────────────────────────────


def generate_income_statement() -> Dict[str, Any]:
    """قائمة الدخل وفق IAS 1."""
    d = state.financial_data or {}
    rev = _safe(d.get("revenue"))
    cogs_val = _safe(d.get("cogs")) or _safe(d.get("cost_of_goods_sold"))
    gp = _safe(d.get("gross_profit"))
    oe = _safe(d.get("operating_expenses"))
    ni = _safe(d.get("net_income"))
    op = max(0, gp - oe) if gp > 0 else 0

    tax = 0.0
    ts = state.tax_summary or {}
    for k in ("ibs", "tva_amount", "total_taxes"):
        tax += _safe(ts.get(k))

    pbt = ni + tax if ni > 0 else 0

    return {
        "report_title": "Statement of Comprehensive Income",
        "for_year": d.get("fiscal_year", 2024),
        "items": [
            ("ias_revenue", rev),
            ("ias_cogs", (-cogs_val if cogs_val else 0) if cogs_val > 0 else 0),
        ],
        "gross_profit": gp if gp > 0 else rev - cogs_val,
        "operating_items": [
            ("ias_operating_expenses", (-oe if oe else 0) if oe > 0 else 0),
        ],
        "operating_profit": op if op > 0 else (gp if gp > 0 else rev - cogs_val) - oe,
        "profit_before_tax": pbt if pbt > 0 else ni + tax,
        "tax_expense": -tax if tax > 0 else 0,
        "net_income": ni if ni > 0 else pbt - tax,
    }


# ── IAS 7: Statement of Cash Flows (Indirect Method) ───────────────────────


def generate_cash_flow() -> Dict[str, Any]:
    """قائمة التدفقات النقدية — الطريقة غير المباشرة وفق IAS 7."""
    d = state.financial_data or {}
    ni = _safe(d.get("net_income"))
    dep = _safe(d.get("depreciation")) or (_safe(d.get("total_assets")) * 0.05)
    inv = _safe(d.get("inventory"))
    recv = _safe(d.get("avg_receivables"))
    pay = _safe(d.get("avg_payables"))
    gp = _safe(d.get("gross_profit"))
    cash_val = _safe(d.get("cash"))

    wc_changes = (-(recv) + pay - (inv * 0.3) if recv or pay or inv else 0)
    oper = ni + dep + wc_changes

    capex = -((_safe(d.get("total_assets")) - _safe(d.get("current_assets"))) * 0.08)
    invest = capex

    debt_change = _safe(d.get("total_liabilities")) * 0.05
    finance = debt_change

    net_change = oper + invest + finance
    end_cash = cash_val + net_change if cash_val else net_change

    return {
        "report_title": "Statement of Cash Flows",
        "for_year": d.get("fiscal_year", 2024),
        "method": "Indirect (IAS 7)",
        "operating": [
            ("ias_net_income", ni),
            ("ias_depreciation", dep),
            ("ias_wc_changes", wc_changes),
        ],
        "operating_total": oper,
        "investing": [
            ("ias_capex", capex),
        ],
        "investing_total": invest,
        "financing": [
            ("ias_debt_change", debt_change),
        ],
        "financing_total": finance,
        "net_change": net_change,
        "cash_beginning": cash_val if cash_val else 0,
        "cash_ending": end_cash,
    }


# ── IAS 1: Statement of Changes in Equity ───────────────────────────────────


def generate_equity_statement() -> Dict[str, Any]:
    """قائمة التغيرات في حقوق الملكية وفق IAS 1."""
    d = state.financial_data or {}
    eq = _safe(d.get("equity"))
    ni = _safe(d.get("net_income"))
    re_val = _safe(d.get("retained_earnings")) or ni
    share = max(0, eq - re_val) if eq > 0 else 0

    return {
        "report_title": "Statement of Changes in Equity",
        "for_year": d.get("fiscal_year", 2024),
        "opening_balance": share + re_val - ni if eq > 0 and ni > 0 else eq,
        "changes": [
            ("ias_net_income", ni),
        ],
        "closing_balance": eq if eq > 0 else share + re_val,
    }


# ── Aggregate ────────────────────────────────────────────────────────────────


def generate_all() -> Dict[str, Any]:
    return {
        "balance_sheet": generate_balance_sheet(),
        "income_statement": generate_income_statement(),
        "cash_flow": generate_cash_flow(),
        "equity_statement": generate_equity_statement(),
        "company_name": state.company_name or "",
        "company_name_fr": state.company_name_fr or "",
        "fiscal_year": (state.financial_data or {}).get("fiscal_year", 2024),
    }
