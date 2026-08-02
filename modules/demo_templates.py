# قوالب استيراد/تصدير الشركات التجريبية والتقارير المعدة مسبقاً
# ==============================================================

import csv
import os

from utils.app_logger import get_logger
from modules.demo_data import DemoData

log = get_logger("demo_templates")

# أعمدة متوافقة مع DataImporter/DataValidator للاستيراد
FINANCIAL_COLUMNS = [
    "company_name", "fiscal_year",
    "revenue", "cost_of_goods_sold", "gross_profit",
    "operating_expenses", "operating_income", "net_income",
    "total_assets", "current_assets", "non_current_assets",
    "total_liabilities", "current_liabilities", "non_current_liabilities",
    "equity", "share_capital", "retained_earnings",
]

TRANSACTION_COLUMNS = [
    "company_name", "month",
    "revenue", "cost_of_goods_sold", "operating_expenses",
    "net_income", "cash", "accounts_receivable", "inventory",
    "accounts_payable",
]


def _write_csv(path, columns, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(row)
    log.info("Wrote CSV: %s (%d rows)", path, len(rows))


def write_financial_template(path):
    """كتابة قالب فارغ للبيانات المالية (رؤوس فقط)."""
    _write_csv(path, FINANCIAL_COLUMNS, [])
    return path


def write_transactions_template(path):
    """كتابة قالب فارغ للمعاملات الشهرية (رؤوس فقط)."""
    _write_csv(path, TRANSACTION_COLUMNS, [])
    return path


def write_templates(directory):
    """كتابة قوالب الاستيراد في مجلد معيّن. تعيد قائمة المسارات."""
    financial = os.path.join(directory, "template_financial.csv")
    transactions = os.path.join(directory, "template_transactions.csv")
    return [
        write_financial_template(financial),
        write_transactions_template(transactions),
    ]


def export_company_csv(directory, company_id):
    """تصدير بيانات شركة تجريبية (سنوية + شهرية) إلى CSV. تعيد قائمة المسارات."""
    company = DemoData.get_company(company_id)
    if not company:
        return []
    name = company["company_name"]
    fd = company["financial_data"]

    financial_rows = [[
        name, company["fiscal_year"],
        fd.get("revenue", ""), fd.get("cost_of_goods_sold", ""),
        fd.get("gross_profit", ""), fd.get("operating_expenses", ""),
        fd.get("operating_income", ""), fd.get("net_income", ""),
        fd.get("total_assets", ""), fd.get("current_assets", ""),
        fd.get("non_current_assets", ""), fd.get("total_liabilities", ""),
        fd.get("current_liabilities", ""), fd.get("non_current_liabilities", ""),
        fd.get("equity", ""), fd.get("share_capital", ""),
        fd.get("retained_earnings", ""),
    ]]

    tx_rows = []
    for m in DemoData.get_monthly_transactions(company_id):
        tx_rows.append([
            name, m["month"],
            m["revenue"], m["cost_of_goods_sold"], m["operating_expenses"],
            m["net_income"], m["cash"], m["accounts_receivable"],
            m["inventory"], m["accounts_payable"],
        ])

    financial_path = os.path.join(directory, f"{company_id}_financial.csv")
    transactions_path = os.path.join(directory, f"{company_id}_transactions.csv")
    _write_csv(financial_path, FINANCIAL_COLUMNS, financial_rows)
    _write_csv(transactions_path, TRANSACTION_COLUMNS, tx_rows)
    return [financial_path, transactions_path]


def generate_demo_reports(company_id):
    """توليد تقارير مُعدّة مسبقاً لشركة تجريبية. تعيد قاموس {اسم: نص}."""
    company = DemoData.get_company(company_id)
    if not company:
        return {}
    fd = company["financial_data"]
    from modules.reporting import ReportGenerator
    from modules.calculations import CalculationEngine

    rg = ReportGenerator(company["company_name"], company["fiscal_year"])
    engine = CalculationEngine()
    ratios = engine.calculate_all_ratios(fd)

    return {
        "balance_sheet": rg.generate_balance_sheet_report(
            fd.get("total_assets", 0),
            fd.get("total_liabilities", 0),
            fd.get("equity", 0),
        ),
        "income_statement": rg.generate_income_statement_report(
            fd.get("revenue", 0),
            fd.get("cost_of_goods_sold", 0),
            fd.get("operating_expenses", 0),
            fd.get("net_income", 0),
        ),
        "ratios": rg.generate_financial_ratios_report(ratios),
    }
