"""Demo/sample data for the Smart Accounting Platform."""

import copy

from utils.app_logger import get_logger

log = get_logger("demo_data")


DEMO_DATA = {
    "company_name": "شركة النور للمقاولات",
    "fiscal_year": 2024,
    "financial_data": {
        "revenue": 85000000,
        "cost_of_goods_sold": 52000000,
        "gross_profit": 33000000,
        "operating_expenses": 18000000,
        "operating_income": 15000000,
        "other_income": 2000000,
        "other_expenses": 1500000,
        "net_income": 15500000,
        "total_assets": 120000000,
        "current_assets": 45000000,
        "cash": 8000000,
        "accounts_receivable": 15000000,
        "inventory": 22000000,
        "non_current_assets": 75000000,
        "total_liabilities": 55000000,
        "current_liabilities": 30000000,
        "accounts_payable": 18000000,
        "average_payables": 18000000,
        "short_term_debt": 12000000,
        "non_current_liabilities": 25000000,
        "long_term_debt": 25000000,
        "equity": 65000000,
        "share_capital": 40000000,
        "retained_earnings": 25000000,
        "average_receivables": 15000000,
        "average_inventory": 22000000,
    },
    "tax_summary": {
        "revenue": 85000000,
        "gross_profit": 33000000,
        "operating_income": 15000000,
        "taxable_income": 15500000,
        "ibs": {"tax_amount": 4030000, "effective_rate": 0.26, "rate_used": 0.26},
        "cnas_annual": 1443750,
        "cnac_annual": 127500,
        "irg_annual": 2400000,
        "vf_annual": 1700000,
        "total_taxes": 9701250,
        "tax_burden_pct": 11.41,
        "net_income_after_taxes": 5798750,
        "config_year": "2025",
    },
}


# ---- شركات تجريبية متعددة القطاعات (تجارية / خدمات / إنتاج / استيراد-تصدير) ----

DEMO_COMPANIES = {
    "retail": {
        "company_name": "شركة الأمل للتجارة العامة",
        "company_name_fr": "Société El Amel de Commerce Général",
        "industry": "retail",
        "fiscal_year": 2024,
        "financial_data": {
            "revenue": 120000000,
            "cost_of_goods_sold": 88000000,
            "gross_profit": 32000000,
            "operating_expenses": 21000000,
            "operating_income": 11000000,
            "other_income": 1000000,
            "other_expenses": 500000,
            "net_income": 11500000,
            "total_assets": 100000000,
            "current_assets": 55000000,
            "cash": 9000000,
            "accounts_receivable": 14000000,
            "inventory": 32000000,
            "non_current_assets": 45000000,
            "total_liabilities": 60000000,
            "current_liabilities": 38000000,
            "accounts_payable": 26000000,
            "average_payables": 26000000,
            "short_term_debt": 12000000,
            "non_current_liabilities": 22000000,
            "long_term_debt": 22000000,
            "equity": 40000000,
            "share_capital": 25000000,
            "retained_earnings": 15000000,
            "average_receivables": 14000000,
            "average_inventory": 32000000,
        },
        "tax_summary": {
            "revenue": 120000000,
            "gross_profit": 32000000,
            "operating_income": 11000000,
            "taxable_income": 11500000,
            "ibs": {"tax_amount": 2990000, "effective_rate": 0.26, "rate_used": 0.26},
            "cnas_annual": 960000,
            "cnac_annual": 84000,
            "irg_annual": 1500000,
            "vf_annual": 1200000,
            "total_taxes": 6734000,
            "tax_burden_pct": 5.61,
            "net_income_after_taxes": 8510000,
            "config_year": "2025",
        },
    },
    "services": {
        "company_name": "شركة المستقبل للخدمات التقنية",
        "company_name_fr": "Société El Moustakbal des Services Techniques",
        "industry": "services",
        "fiscal_year": 2024,
        "financial_data": {
            "revenue": 60000000,
            "cost_of_goods_sold": 25000000,
            "gross_profit": 35000000,
            "operating_expenses": 18000000,
            "operating_income": 17000000,
            "other_income": 500000,
            "other_expenses": 200000,
            "net_income": 17300000,
            "total_assets": 65000000,
            "current_assets": 35000000,
            "cash": 12000000,
            "accounts_receivable": 18000000,
            "inventory": 5000000,
            "non_current_assets": 30000000,
            "total_liabilities": 35000000,
            "current_liabilities": 22000000,
            "accounts_payable": 14000000,
            "average_payables": 14000000,
            "short_term_debt": 8000000,
            "non_current_liabilities": 13000000,
            "long_term_debt": 13000000,
            "equity": 30000000,
            "share_capital": 20000000,
            "retained_earnings": 10000000,
            "average_receivables": 18000000,
            "average_inventory": 5000000,
        },
        "tax_summary": {
            "revenue": 60000000,
            "gross_profit": 35000000,
            "operating_income": 17000000,
            "taxable_income": 17300000,
            "ibs": {"tax_amount": 4498000, "effective_rate": 0.26, "rate_used": 0.26},
            "cnas_annual": 1100000,
            "cnac_annual": 90000,
            "irg_annual": 1800000,
            "vf_annual": 900000,
            "total_taxes": 8388000,
            "tax_burden_pct": 13.98,
            "net_income_after_taxes": 12802000,
            "config_year": "2025",
        },
    },
    "manufacturing": {
        "company_name": "مصنع الجزائر للصناعات الغذائية",
        "company_name_fr": "Usine d'Algérie des Industries Alimentaires",
        "industry": "manufacturing",
        "fiscal_year": 2024,
        "financial_data": {
            "revenue": 200000000,
            "cost_of_goods_sold": 130000000,
            "gross_profit": 70000000,
            "operating_expenses": 35000000,
            "operating_income": 35000000,
            "other_income": 2000000,
            "other_expenses": 1000000,
            "net_income": 36000000,
            "total_assets": 250000000,
            "current_assets": 90000000,
            "cash": 12000000,
            "accounts_receivable": 28000000,
            "inventory": 50000000,
            "non_current_assets": 160000000,
            "total_liabilities": 130000000,
            "current_liabilities": 70000000,
            "accounts_payable": 40000000,
            "average_payables": 40000000,
            "short_term_debt": 30000000,
            "non_current_liabilities": 60000000,
            "long_term_debt": 60000000,
            "equity": 120000000,
            "share_capital": 70000000,
            "retained_earnings": 50000000,
            "average_receivables": 28000000,
            "average_inventory": 50000000,
        },
        "tax_summary": {
            "revenue": 200000000,
            "gross_profit": 70000000,
            "operating_income": 35000000,
            "taxable_income": 36000000,
            "ibs": {"tax_amount": 9360000, "effective_rate": 0.26, "rate_used": 0.26},
            "cnas_annual": 2400000,
            "cnac_annual": 150000,
            "irg_annual": 4200000,
            "vf_annual": 2800000,
            "total_taxes": 18910000,
            "tax_burden_pct": 9.46,
            "net_income_after_taxes": 26640000,
            "config_year": "2025",
        },
    },
    "import_export": {
        "company_name": "شركة البحر المتوسط للاستيراد والتصدير",
        "company_name_fr": "Société Méditerranée Import-Export",
        "industry": "import_export",
        "fiscal_year": 2024,
        "financial_data": {
            "revenue": 150000000,
            "cost_of_goods_sold": 115000000,
            "gross_profit": 35000000,
            "operating_expenses": 15000000,
            "operating_income": 20000000,
            "other_income": 1500000,
            "other_expenses": 1000000,
            "net_income": 20500000,
            "total_assets": 125000000,
            "current_assets": 70000000,
            "cash": 8000000,
            "accounts_receivable": 22000000,
            "inventory": 40000000,
            "non_current_assets": 55000000,
            "total_liabilities": 75000000,
            "current_liabilities": 55000000,
            "accounts_payable": 35000000,
            "average_payables": 35000000,
            "short_term_debt": 20000000,
            "non_current_liabilities": 20000000,
            "long_term_debt": 20000000,
            "equity": 50000000,
            "share_capital": 30000000,
            "retained_earnings": 20000000,
            "average_receivables": 22000000,
            "average_inventory": 40000000,
        },
        "tax_summary": {
            "revenue": 150000000,
            "gross_profit": 35000000,
            "operating_income": 20000000,
            "taxable_income": 20500000,
            "ibs": {"tax_amount": 5330000, "effective_rate": 0.26, "rate_used": 0.26},
            "cnas_annual": 1300000,
            "cnac_annual": 100000,
            "irg_annual": 2100000,
            "vf_annual": 1900000,
            "total_taxes": 10730000,
            "tax_burden_pct": 7.15,
            "net_income_after_taxes": 15170000,
            "config_year": "2025",
        },
    },
}

# أوزان موسمية شهرية (يناير..ديسمبر) لكل قطاع — مجموعها = 1
_MONTHLY_WEIGHTS = {
    "retail": [0.06, 0.05, 0.06, 0.07, 0.08, 0.11, 0.09, 0.08, 0.07, 0.08, 0.10, 0.15],
    "services": [0.07, 0.07, 0.08, 0.08, 0.09, 0.09, 0.08, 0.08, 0.09, 0.09, 0.09, 0.09],
    "manufacturing": [0.09, 0.08, 0.07, 0.07, 0.08, 0.09, 0.08, 0.08, 0.08, 0.09, 0.09, 0.10],
    "import_export": [0.06, 0.05, 0.07, 0.10, 0.12, 0.11, 0.08, 0.07, 0.06, 0.07, 0.09, 0.12],
}


def _generate_monthly_transactions(company_id):
    """توليد معاملات شهرية (12 شهراً) متسقة مع البيانات السنوية."""
    cfg = DEMO_COMPANIES.get(company_id)
    if not cfg:
        return []
    fd = cfg["financial_data"]
    weights = _MONTHLY_WEIGHTS[company_id]
    revenue = fd.get("revenue", 0)
    cogs = fd.get("cost_of_goods_sold", 0)
    opex = fd.get("operating_expenses", 0)
    cash = fd.get("cash", 0)
    receivables = fd.get("accounts_receivable", fd.get("average_receivables", 0))
    inventory = fd.get("inventory", fd.get("average_inventory", 0))
    payables = fd.get("accounts_payable", fd.get("average_payables", 0))
    rows = []
    for i, w in enumerate(weights, start=1):
        rows.append({
            "month": i,
            "revenue": round(revenue * w, 2),
            "cost_of_goods_sold": round(cogs * w, 2),
            "operating_expenses": round(opex * w, 2),
            "net_income": round((revenue - cogs - opex) * w, 2),
            "cash": round(cash * w, 2),
            "accounts_receivable": round(receivables * w, 2),
            "inventory": round(inventory * w, 2),
            "accounts_payable": round(payables * w, 2),
        })
    return rows


class DemoData:
    @staticmethod
    def get_data():
        return copy.deepcopy(DEMO_DATA)

    @staticmethod
    def get_financial_data():
        return copy.deepcopy(DEMO_DATA["financial_data"])

    @staticmethod
    def get_company_name():
        return DEMO_DATA["company_name"]

    # ===== واجهة الشركات التجريبية المتعددة =====

    @staticmethod
    def list_companies():
        """قائمة ملخصات الشركات التجريبية المتاحة."""
        return [
            {
                "id": cid,
                "company_name": c["company_name"],
                "company_name_fr": c["company_name_fr"],
                "industry": c["industry"],
                "fiscal_year": c["fiscal_year"],
            }
            for cid, c in DEMO_COMPANIES.items()
        ]

    @staticmethod
    def get_company(company_id):
        """إرجاع نسخة من بيانات شركة تجريبية كاملة (أو None)."""
        company = DEMO_COMPANIES.get(company_id)
        if not company:
            return None
        result = copy.deepcopy(company)
        result["id"] = company_id
        return result

    @staticmethod
    def get_monthly_transactions(company_id):
        """إرجاع المعاملات الشهرية النموذجية لشركة (12 شهراً)."""
        if company_id not in DEMO_COMPANIES:
            return []
        return copy.deepcopy(_generate_monthly_transactions(company_id))

    @staticmethod
    def load_company(state, company_id):
        """تحميل شركة تجريبية إلى حالة التطبيق وحفظها."""
        company = DemoData.get_company(company_id)
        if not company:
            log.warning("Demo company not found: %s", company_id)
            return False
        state.company_name = company["company_name"]
        state.company_name_fr = company["company_name_fr"]
        state.fiscal_year = company["fiscal_year"]
        state.financial_data = company["financial_data"]
        state.tax_summary = company["tax_summary"]
        from modules.calculations import CalculationEngine
        from modules.analysis import FinancialAnalyzer
        engine = CalculationEngine()
        state.ratios = engine.calculate_all_ratios(state.financial_data)
        analyzer = FinancialAnalyzer(state.financial_data)
        fd = state.financial_data
        analyzer.dupont_analysis(
            net_income=fd.get('net_income', 0),
            revenue=fd.get('revenue', 0),
            total_assets=fd.get('total_assets', 0),
            equity=fd.get('equity', 0),
        )
        state.dupont = analyzer.analysis_results.get('dupont', {})
        analyzer.working_capital_analysis(
            current_assets=fd.get('current_assets', 0),
            current_liabilities=fd.get('current_liabilities', 0),
            inventory=fd.get('inventory', 0),
        )
        state.working_capital = analyzer.analysis_results.get('working_capital', {})
        state.save_data()
        log.info("Loaded demo company: %s", company["company_name"])
        return True
