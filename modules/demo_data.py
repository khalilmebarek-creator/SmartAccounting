"""Demo/sample data for the Smart Accounting Platform."""

import copy


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
