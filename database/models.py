from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Float, Text,
    DateTime, Date, ForeignKey, Index, text, func, UniqueConstraint,
)
from database.engine import get_engine

metadata = MetaData()

TABLE_NAMES = [
    "companies", "fiscal_years", "assets", "liabilities",
    "equity", "income_statement", "financial_ratios",
    "audit_log", "notes", "tax_data", "tax_obligations",
    "scenario_results", "reference_standards", "competitor_data",
    "dashboard_layouts",
    "ledger_entries", "partners", "partner_transactions",
    "invoices", "invoice_items",
    "inventory_items", "inventory_movements",
    "employees", "payroll_runs", "budget_items"
]

companies = Table(
    "companies", metadata,
    Column("company_id", Integer, primary_key=True, autoincrement=True),
    Column("company_name", String(255), nullable=False),
    Column("industry", String(100)),
    Column("registration_number", String(100)),
    Column("country", String(100)),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    Column("updated_date", DateTime, server_default=func.current_timestamp()),
)

fiscal_years = Table(
    "fiscal_years", metadata,
    Column("fiscal_year_id", Integer, primary_key=True, autoincrement=True),
    Column("company_id", Integer, ForeignKey("companies.company_id"), nullable=False),
    Column("year", Integer),
    Column("start_date", Date),
    Column("end_date", Date),
    UniqueConstraint("company_id", "year"),
)

assets = Table(
    "assets", metadata,
    Column("asset_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("asset_name", String(255)),
    Column("current_assets", Float),
    Column("non_current_assets", Float),
    Column("total_assets", Float),
    UniqueConstraint("fiscal_year_id"),
)

liabilities = Table(
    "liabilities", metadata,
    Column("liability_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("current_liabilities", Float),
    Column("non_current_liabilities", Float),
    Column("total_liabilities", Float),
    UniqueConstraint("fiscal_year_id"),
)

equity = Table(
    "equity", metadata,
    Column("equity_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("share_capital", Float),
    Column("retained_earnings", Float),
    Column("total_equity", Float),
    UniqueConstraint("fiscal_year_id"),
)

income_statement = Table(
    "income_statement", metadata,
    Column("income_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("revenue", Float),
    Column("cost_of_goods_sold", Float),
    Column("gross_profit", Float),
    Column("operating_expenses", Float),
    Column("operating_income", Float),
    Column("interest_expense", Float),
    Column("tax_expense", Float),
    Column("net_income", Float),
    UniqueConstraint("fiscal_year_id"),
)

financial_ratios = Table(
    "financial_ratios", metadata,
    Column("ratio_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("current_ratio", Float),
    Column("quick_ratio", Float),
    Column("gross_profit_margin", Float),
    Column("net_profit_margin", Float),
    Column("roa", Float),
    Column("roe", Float),
    Column("asset_turnover", Float),
    Column("receivables_turnover", Float),
    Column("debt_to_equity", Float),
    Column("debt_ratio", Float),
    Column("days_sales_outstanding", Integer),
    Column("inventory_turnover", Float),
    UniqueConstraint("fiscal_year_id"),
)

audit_log = Table(
    "audit_log", metadata,
    Column("log_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("issue_type", String(100)),
    Column("issue_description", Text),
    Column("severity", String(20)),
    Column("detected_date", DateTime, server_default=func.current_timestamp()),
    Column("status", String(50)),
)

notes = Table(
    "notes", metadata,
    Column("note_id", Integer, primary_key=True, autoincrement=True),
    Column("audit_log_id", Integer, ForeignKey("audit_log.log_id"), nullable=False),
    Column("reviewer_name", String(255)),
    Column("note_text", Text),
    Column("note_date", DateTime, server_default=func.current_timestamp()),
)

tax_data = Table(
    "tax_data", metadata,
    Column("tax_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("activity_type", String(50), server_default=text("'other'")),
    Column("number_of_employees", Integer, server_default=text("0")),
    Column("avg_salary", Float, server_default=text("0")),
    Column("is_construction", Integer, server_default=text("0")),
    Column("ibs_amount", Float, server_default=text("0")),
    Column("ibs_rate", Float, server_default=text("0")),
    Column("tva_collected", Float, server_default=text("0")),
    Column("tva_paid", Float, server_default=text("0")),
    Column("tva_net", Float, server_default=text("0")),
    Column("irg_total", Float, server_default=text("0")),
    Column("cnas_employer", Float, server_default=text("0")),
    Column("cnas_employee", Float, server_default=text("0")),
    Column("cnas_total", Float, server_default=text("0")),
    Column("cnac_employer", Float, server_default=text("0")),
    Column("cnac_employee", Float, server_default=text("0")),
    Column("cnac_total", Float, server_default=text("0")),
    Column("vf_amount", Float, server_default=text("0")),
    Column("total_taxes", Float, server_default=text("0")),
    Column("tax_burden_pct", Float, server_default=text("0")),
    Column("simulation_json", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
)

tax_obligations = Table(
    "tax_obligations", metadata,
    Column("obligation_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("tax_type", String(50), nullable=False),
    Column("due_month", Integer, nullable=False),
    Column("due_day", Integer, server_default=text("20")),
    Column("amount", Float, server_default=text("0")),
    Column("status", String(20), server_default=text("'pending'")),
    Column("paid_date", Date),
    Column("notes", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
)

scenario_results = Table(
    "scenario_results", metadata,
    Column("scenario_id", Integer, primary_key=True, autoincrement=True),
    Column("fiscal_year_id", Integer, ForeignKey("fiscal_years.fiscal_year_id"), nullable=False),
    Column("scenario_type", String(20), nullable=False),
    Column("revenue_change_pct", Float, server_default=text("0")),
    Column("cost_change_pct", Float, server_default=text("0")),
    Column("efficiency_change_pct", Float, server_default=text("0")),
    Column("projected_revenue", Float, server_default=text("0")),
    Column("projected_net_income", Float, server_default=text("0")),
    Column("net_profit_margin", Float, server_default=text("0")),
    Column("roe", Float, server_default=text("0")),
    Column("result_json", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
)

reference_standards = Table(
    "reference_standards", metadata,
    Column("standard_id", Integer, primary_key=True, autoincrement=True),
    Column("sector_code", String(50), nullable=False),
    Column("ratio_name", String(50), nullable=False),
    Column("min_val", Float, server_default=text("0")),
    Column("avg_val", Float, server_default=text("0")),
    Column("max_val", Float, server_default=text("0")),
    Column("ideal_min", Float, server_default=text("0")),
    Column("ideal_max", Float, server_default=text("0")),
    Column("best_practice", Float, server_default=text("0")),
    Column("international", Float, server_default=text("0")),
    UniqueConstraint("sector_code", "ratio_name"),
)

competitor_data = Table(
    "competitor_data", metadata,
    Column("competitor_id", Integer, primary_key=True, autoincrement=True),
    Column("sector_code", String(50), nullable=False),
    Column("competitor_name", String(255), nullable=False),
    Column("ratio_name", String(50), nullable=False),
    Column("ratio_value", Float, server_default=text("0")),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    UniqueConstraint("sector_code", "competitor_name", "ratio_name"),
)

dashboard_layouts = Table(
    "dashboard_layouts", metadata,
    Column("layout_id", Integer, primary_key=True, autoincrement=True),
    Column("layout_name", String(255), nullable=False),
    Column("layout_json", Text, nullable=False),
    Column("updated_at", DateTime, server_default=func.current_timestamp()),
    UniqueConstraint("layout_name"),
)

ledger_entries = Table(
    "ledger_entries", metadata,
    Column("entry_id", Integer, primary_key=True, autoincrement=True),
    Column("entry_date", Date, nullable=False),
    Column("account_code", String(50), nullable=False),
    Column("account_name", String(255)),
    Column("description", Text),
    Column("debit", Float, server_default=text("0")),
    Column("credit", Float, server_default=text("0")),
    Column("reference", String(100)),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
)

partners = Table(
    "partners", metadata,
    Column("partner_id", Integer, primary_key=True, autoincrement=True),
    Column("partner_type", String(20), nullable=False),
    Column("partner_name", String(255), nullable=False),
    Column("phone", String(50)),
    Column("email", String(255)),
    Column("address", Text),
    Column("tax_id", String(100)),
    Column("notes", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    Column("updated_date", DateTime, server_default=func.current_timestamp()),
)

partner_transactions = Table(
    "partner_transactions", metadata,
    Column("transaction_id", Integer, primary_key=True, autoincrement=True),
    Column("partner_id", Integer, ForeignKey("partners.partner_id"), nullable=False),
    Column("transaction_date", Date, nullable=False),
    Column("transaction_type", String(20), nullable=False),
    Column("amount", Float, server_default=text("0")),
    Column("reference", String(100)),
    Column("notes", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
)

invoices = Table(
    "invoices", metadata,
    Column("invoice_id", Integer, primary_key=True, autoincrement=True),
    Column("invoice_number", String(50), nullable=False),
    Column("invoice_type", String(20), nullable=False),
    Column("partner_id", Integer, ForeignKey("partners.partner_id"), nullable=False),
    Column("invoice_date", Date, nullable=False),
    Column("due_date", Date),
    Column("subtotal", Float, server_default=text("0")),
    Column("tva_rate", Float, server_default=text("0")),
    Column("tva_amount", Float, server_default=text("0")),
    Column("total", Float, server_default=text("0")),
    Column("status", String(20), server_default=text("'draft'")),
    Column("notes", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    UniqueConstraint("invoice_number"),
)

invoice_items = Table(
    "invoice_items", metadata,
    Column("item_id", Integer, primary_key=True, autoincrement=True),
    Column("invoice_id", Integer, ForeignKey("invoices.invoice_id"), nullable=False),
    Column("description", String(255), nullable=False),
    Column("quantity", Float, server_default=text("1")),
    Column("unit_price", Float, server_default=text("0")),
    Column("amount", Float, server_default=text("0")),
)

inventory_items = Table(
    "inventory_items", metadata,
    Column("item_id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(100), unique=True),
    Column("item_name", String(255), nullable=False),
    Column("category", String(100)),
    Column("unit", String(50)),
    Column("quantity", Float, server_default=text("0")),
    Column("avg_cost", Float, server_default=text("0")),
    Column("sale_price", Float, server_default=text("0")),
    Column("min_quantity", Float, server_default=text("0")),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    Column("updated_date", DateTime, server_default=func.current_timestamp()),
)

inventory_movements = Table(
    "inventory_movements", metadata,
    Column("movement_id", Integer, primary_key=True, autoincrement=True),
    Column("item_id", Integer, ForeignKey("inventory_items.item_id"), nullable=False),
    Column("movement_date", Date, nullable=False),
    Column("movement_type", String(20), nullable=False),
    Column("quantity", Float, server_default=text("0")),
    Column("unit_cost", Float, server_default=text("0")),
    Column("reference", String(100)),
    Column("notes", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
)

employees = Table(
    "employees", metadata,
    Column("employee_id", Integer, primary_key=True, autoincrement=True),
    Column("employee_name", String(255), nullable=False),
    Column("position", String(255)),
    Column("department", String(100)),
    Column("base_salary", Float, server_default=text("0")),
    Column("hire_date", Date),
    Column("status", String(20), server_default=text("'active'")),
    Column("notes", Text),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    Column("updated_date", DateTime, server_default=func.current_timestamp()),
)

payroll_runs = Table(
    "payroll_runs", metadata,
    Column("run_id", Integer, primary_key=True, autoincrement=True),
    Column("employee_id", Integer, ForeignKey("employees.employee_id"), nullable=False),
    Column("pay_month", Integer, nullable=False),
    Column("pay_year", Integer, nullable=False),
    Column("base_salary", Float, server_default=text("0")),
    Column("cnas_employee", Float, server_default=text("0")),
    Column("unemployment_insurance", Float, server_default=text("0")),
    Column("taxable_salary", Float, server_default=text("0")),
    Column("irg", Float, server_default=text("0")),
    Column("net_salary", Float, server_default=text("0")),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    UniqueConstraint("employee_id", "pay_month", "pay_year"),
)

budget_items = Table(
    "budget_items", metadata,
    Column("budget_id", Integer, primary_key=True, autoincrement=True),
    Column("budget_year", Integer, nullable=False),
    Column("category", String(50), server_default=text("'expense'")),
    Column("item_name", String(255), nullable=False),
    Column("planned_amount", Float, server_default=text("0")),
    Column("created_date", DateTime, server_default=func.current_timestamp()),
    UniqueConstraint("budget_year", "item_name"),
)

Index("idx_fiscal_years_company", fiscal_years.c.company_id)
Index("idx_fiscal_years_year", fiscal_years.c.year)
Index("idx_assets_fy", assets.c.fiscal_year_id)
Index("idx_liabilities_fy", liabilities.c.fiscal_year_id)
Index("idx_equity_fy", equity.c.fiscal_year_id)
Index("idx_income_fy", income_statement.c.fiscal_year_id)
Index("idx_ratios_fy", financial_ratios.c.fiscal_year_id)
Index("idx_audit_fy", audit_log.c.fiscal_year_id)
Index("idx_notes_audit", notes.c.audit_log_id)
Index("idx_tax_data_fy", tax_data.c.fiscal_year_id)
Index("idx_tax_oblig_fy", tax_obligations.c.fiscal_year_id)
Index("idx_tax_oblig_month", tax_obligations.c.due_month)
Index("idx_scenario_fy", scenario_results.c.fiscal_year_id)
Index("idx_ref_std_sector", reference_standards.c.sector_code)
Index("idx_comp_sector", competitor_data.c.sector_code)
Index("idx_comp_name", competitor_data.c.competitor_name)
Index("idx_layout_name", dashboard_layouts.c.layout_name)
Index("idx_companies_name", companies.c.company_name)
Index("idx_ledger_date", ledger_entries.c.entry_date)
Index("idx_ledger_account", ledger_entries.c.account_code)
Index("idx_partners_type", partners.c.partner_type)
Index("idx_pt_partner", partner_transactions.c.partner_id)
Index("idx_invoices_partner", invoices.c.partner_id)
Index("idx_invoices_date", invoices.c.invoice_date)
Index("idx_ii_invoice", invoice_items.c.invoice_id)
Index("idx_inv_category", inventory_items.c.category)
Index("idx_inv_min", inventory_items.c.min_quantity)
Index("idx_im_item", inventory_movements.c.item_id)
Index("idx_emp_status", employees.c.status)
Index("idx_pr_emp", payroll_runs.c.employee_id)
Index("idx_pr_month", payroll_runs.c.pay_year)
Index("idx_budget_year", budget_items.c.budget_year)


def create_all():
    metadata.create_all(get_engine())
