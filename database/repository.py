# عمليات قاعدة البيانات - SQLAlchemy Core CRUD
# ==============================================

import json as _json
import logging
from sqlalchemy import text, insert, update, delete
from database.engine import get_engine
from utils.app_logger import get_logger

log = get_logger("repository")

_ALLOWED_TABLES = frozenset({"income_statement", "equity", "liabilities", "assets", "financial_ratios", "tax_data", "tax_obligations", "fiscal_years", "companies", "notes", "audit_log"})
_VALID_STATUSES = {"pending", "paid", "overdue", "cancelled"}


class ValidationError(Exception):
    pass


def _validate_positive(value, field_name):
    if value is not None and value < 0:
        raise ValidationError(f"{field_name} must be non-negative (got {value})")


def _validate_required(value, field_name):
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} is required")


def _validate_financial_data(data):
    if not isinstance(data, dict):
        raise ValidationError("financial_data must be a dict")
    for key in ['revenue', 'total_assets', 'total_liabilities', 'equity']:
        val = data.get(key)
        if val is not None:
            _validate_positive(val, key)


def _validate_ratios(ratios):
    if not isinstance(ratios, dict):
        raise ValidationError("ratios must be a dict")


def _row_to_dict(row):
    if row is None:
        return None
    if hasattr(row, "_mapping"):
        return dict(row._mapping)
    if hasattr(row, "keys"):
        return dict(row)
    return row


def _rows_to_dicts(rows):
    return [_row_to_dict(r) for r in rows]


def create_tables():
    engine = get_engine()
    _DDL = [
        """CREATE TABLE IF NOT EXISTS companies (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name VARCHAR(255) NOT NULL,
            industry VARCHAR(100),
            registration_number VARCHAR(100),
            country VARCHAR(100),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS fiscal_years (
            fiscal_year_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            year INTEGER,
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (company_id) REFERENCES companies(company_id),
            UNIQUE(company_id, year)
        )""",
        """CREATE TABLE IF NOT EXISTS assets (
            asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            asset_name VARCHAR(255),
            current_assets DECIMAL(15,2),
            non_current_assets DECIMAL(15,2),
            total_assets DECIMAL(15,2),
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
            UNIQUE(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS liabilities (
            liability_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            current_liabilities DECIMAL(15,2),
            non_current_liabilities DECIMAL(15,2),
            total_liabilities DECIMAL(15,2),
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
            UNIQUE(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS equity (
            equity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            share_capital DECIMAL(15,2),
            retained_earnings DECIMAL(15,2),
            total_equity DECIMAL(15,2),
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
            UNIQUE(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS income_statement (
            income_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            revenue DECIMAL(15,2),
            cost_of_goods_sold DECIMAL(15,2),
            gross_profit DECIMAL(15,2),
            operating_expenses DECIMAL(15,2),
            operating_income DECIMAL(15,2),
            interest_expense DECIMAL(15,2),
            tax_expense DECIMAL(15,2),
            net_income DECIMAL(15,2),
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
            UNIQUE(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS financial_ratios (
            ratio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            current_ratio DECIMAL(10,4),
            quick_ratio DECIMAL(10,4),
            gross_profit_margin DECIMAL(10,4),
            net_profit_margin DECIMAL(10,4),
            roa DECIMAL(10,4),
            roe DECIMAL(10,4),
            asset_turnover DECIMAL(10,4),
            receivables_turnover DECIMAL(10,4),
            debt_to_equity DECIMAL(10,4),
            debt_ratio DECIMAL(10,4),
            days_sales_outstanding INTEGER,
            inventory_turnover DECIMAL(10,4),
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
            UNIQUE(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            issue_type VARCHAR(100),
            issue_description TEXT,
            severity VARCHAR(20),
            detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50),
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS notes (
            note_id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_log_id INTEGER NOT NULL,
            reviewer_name VARCHAR(255),
            note_text TEXT,
            note_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (audit_log_id) REFERENCES audit_log(log_id)
        )""",
        """CREATE TABLE IF NOT EXISTS tax_data (
            tax_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            activity_type VARCHAR(50) DEFAULT 'other',
            number_of_employees INTEGER DEFAULT 0,
            avg_salary DECIMAL(15,2) DEFAULT 0,
            is_construction INTEGER DEFAULT 0,
            ibs_amount DECIMAL(15,2) DEFAULT 0,
            ibs_rate DECIMAL(5,4) DEFAULT 0,
            tva_collected DECIMAL(15,2) DEFAULT 0,
            tva_paid DECIMAL(15,2) DEFAULT 0,
            tva_net DECIMAL(15,2) DEFAULT 0,
            irg_total DECIMAL(15,2) DEFAULT 0,
            cnas_employer DECIMAL(15,2) DEFAULT 0,
            cnas_employee DECIMAL(15,2) DEFAULT 0,
            cnas_total DECIMAL(15,2) DEFAULT 0,
            cnac_employer DECIMAL(15,2) DEFAULT 0,
            cnac_employee DECIMAL(15,2) DEFAULT 0,
            cnac_total DECIMAL(15,2) DEFAULT 0,
            vf_amount DECIMAL(15,2) DEFAULT 0,
            total_taxes DECIMAL(15,2) DEFAULT 0,
            tax_burden_pct DECIMAL(10,4) DEFAULT 0,
            simulation_json TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS tax_obligations (
            obligation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            tax_type VARCHAR(50) NOT NULL,
            due_month INTEGER NOT NULL,
            due_day INTEGER DEFAULT 20,
            amount DECIMAL(15,2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'pending',
            paid_date DATE,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS scenario_results (
            scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year_id INTEGER NOT NULL,
            scenario_type VARCHAR(20) NOT NULL,
            revenue_change_pct DECIMAL(10,4) DEFAULT 0,
            cost_change_pct DECIMAL(10,4) DEFAULT 0,
            efficiency_change_pct DECIMAL(10,4) DEFAULT 0,
            projected_revenue DECIMAL(15,2) DEFAULT 0,
            projected_net_income DECIMAL(15,2) DEFAULT 0,
            net_profit_margin DECIMAL(10,4) DEFAULT 0,
            roe DECIMAL(10,4) DEFAULT 0,
            result_json TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id)
        )""",
        """CREATE TABLE IF NOT EXISTS reference_standards (
            standard_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector_code VARCHAR(50) NOT NULL,
            ratio_name VARCHAR(50) NOT NULL,
            min_val DECIMAL(12,4) DEFAULT 0,
            avg_val DECIMAL(12,4) DEFAULT 0,
            max_val DECIMAL(12,4) DEFAULT 0,
            ideal_min DECIMAL(12,4) DEFAULT 0,
            ideal_max DECIMAL(12,4) DEFAULT 0,
            best_practice DECIMAL(12,4) DEFAULT 0,
            international DECIMAL(12,4) DEFAULT 0,
            UNIQUE(sector_code, ratio_name)
        )""",
        """CREATE TABLE IF NOT EXISTS competitor_data (
            competitor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector_code VARCHAR(50) NOT NULL,
            competitor_name VARCHAR(255) NOT NULL,
            ratio_name VARCHAR(50) NOT NULL,
            ratio_value DECIMAL(12,4) DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sector_code, competitor_name, ratio_name)
        )""",
        """CREATE TABLE IF NOT EXISTS dashboard_layouts (
            layout_id INTEGER PRIMARY KEY AUTOINCREMENT,
            layout_name VARCHAR(255) NOT NULL,
            layout_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(layout_name)
        )""",
        """CREATE TABLE IF NOT EXISTS ledger_entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date DATE NOT NULL,
            account_code VARCHAR(50) NOT NULL,
            account_name VARCHAR(255),
            description TEXT,
            debit DECIMAL(15,2) DEFAULT 0,
            credit DECIMAL(15,2) DEFAULT 0,
            reference VARCHAR(100),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS partners (
            partner_id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_type VARCHAR(20) NOT NULL,
            partner_name VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            email VARCHAR(255),
            address TEXT,
            tax_id VARCHAR(100),
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS partner_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,
            transaction_date DATE NOT NULL,
            transaction_type VARCHAR(20) NOT NULL,
            amount DECIMAL(15,2) DEFAULT 0,
            reference VARCHAR(100),
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES partners(partner_id)
        )""",
        """CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number VARCHAR(50) NOT NULL,
            invoice_type VARCHAR(20) NOT NULL,
            partner_id INTEGER NOT NULL,
            invoice_date DATE NOT NULL,
            due_date DATE,
            subtotal DECIMAL(15,2) DEFAULT 0,
            tva_rate DECIMAL(5,4) DEFAULT 0,
            tva_amount DECIMAL(15,2) DEFAULT 0,
            total DECIMAL(15,2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'draft',
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(invoice_number)
        )""",
        """CREATE TABLE IF NOT EXISTS invoice_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            description VARCHAR(255) NOT NULL,
            quantity DECIMAL(15,2) DEFAULT 1,
            unit_price DECIMAL(15,2) DEFAULT 0,
            amount DECIMAL(15,2) DEFAULT 0,
            FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
        )""",
        """CREATE TABLE IF NOT EXISTS inventory_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku VARCHAR(100) UNIQUE,
            item_name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            unit VARCHAR(50),
            quantity DECIMAL(15,3) DEFAULT 0,
            avg_cost DECIMAL(15,2) DEFAULT 0,
            sale_price DECIMAL(15,2) DEFAULT 0,
            min_quantity DECIMAL(15,3) DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS inventory_movements (
            movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            movement_date DATE NOT NULL,
            movement_type VARCHAR(20) NOT NULL,
            quantity DECIMAL(15,3) DEFAULT 0,
            unit_cost DECIMAL(15,2) DEFAULT 0,
            reference VARCHAR(100),
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES inventory_items(item_id)
        )""",
        """CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name VARCHAR(255) NOT NULL,
            position VARCHAR(255),
            department VARCHAR(100),
            base_salary DECIMAL(15,2) DEFAULT 0,
            hire_date DATE,
            status VARCHAR(20) DEFAULT 'active',
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE IF NOT EXISTS payroll_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            pay_month INTEGER NOT NULL,
            pay_year INTEGER NOT NULL,
            base_salary DECIMAL(15,2) DEFAULT 0,
            cnas_employee DECIMAL(15,2) DEFAULT 0,
            unemployment_insurance DECIMAL(15,2) DEFAULT 0,
            taxable_salary DECIMAL(15,2) DEFAULT 0,
            irg DECIMAL(15,2) DEFAULT 0,
            net_salary DECIMAL(15,2) DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(employee_id, pay_month, pay_year),
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )""",
        """CREATE TABLE IF NOT EXISTS budget_items (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_year INTEGER NOT NULL,
            category VARCHAR(50) DEFAULT 'expense',
            item_name VARCHAR(255) NOT NULL,
            planned_amount DECIMAL(15,2) DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(budget_year, item_name)
        )""",
    ]
    _INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_fiscal_years_company ON fiscal_years(company_id)",
        "CREATE INDEX IF NOT EXISTS idx_fiscal_years_year ON fiscal_years(year)",
        "CREATE INDEX IF NOT EXISTS idx_assets_fy ON assets(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_liabilities_fy ON liabilities(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_equity_fy ON equity(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_income_fy ON income_statement(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_ratios_fy ON financial_ratios(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_fy ON audit_log(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_notes_audit ON notes(audit_log_id)",
        "CREATE INDEX IF NOT EXISTS idx_tax_data_fy ON tax_data(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_tax_oblig_fy ON tax_obligations(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_tax_oblig_month ON tax_obligations(due_month)",
        "CREATE INDEX IF NOT EXISTS idx_scenario_fy ON scenario_results(fiscal_year_id)",
        "CREATE INDEX IF NOT EXISTS idx_ref_std_sector ON reference_standards(sector_code)",
        "CREATE INDEX IF NOT EXISTS idx_comp_sector ON competitor_data(sector_code)",
        "CREATE INDEX IF NOT EXISTS idx_comp_name ON competitor_data(competitor_name)",
        "CREATE INDEX IF NOT EXISTS idx_layout_name ON dashboard_layouts(layout_name)",
        "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(company_name)",
        "CREATE INDEX IF NOT EXISTS idx_ledger_date ON ledger_entries(entry_date)",
        "CREATE INDEX IF NOT EXISTS idx_ledger_account ON ledger_entries(account_code)",
        "CREATE INDEX IF NOT EXISTS idx_partners_type ON partners(partner_type)",
        "CREATE INDEX IF NOT EXISTS idx_pt_partner ON partner_transactions(partner_id)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_partner ON invoices(partner_id)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date)",
        "CREATE INDEX IF NOT EXISTS idx_ii_invoice ON invoice_items(invoice_id)",
        "CREATE INDEX IF NOT EXISTS idx_inv_category ON inventory_items(category)",
        "CREATE INDEX IF NOT EXISTS idx_inv_min ON inventory_items(min_quantity)",
        "CREATE INDEX IF NOT EXISTS idx_im_item ON inventory_movements(item_id)",
        "CREATE INDEX IF NOT EXISTS idx_emp_status ON employees(status)",
        "CREATE INDEX IF NOT EXISTS idx_pr_emp ON payroll_runs(employee_id)",
        "CREATE INDEX IF NOT EXISTS idx_pr_month ON payroll_runs(pay_year)",
        "CREATE INDEX IF NOT EXISTS idx_budget_year ON budget_items(budget_year)",
    ]
    try:
        engine = get_engine()
        with engine.connect() as conn:
            for ddl in _DDL + _INDEXES:
                conn.execute(text(ddl))
            conn.commit()
        log.info("All tables/indexes created via SQLAlchemy Core")
        return True
    except Exception as e:
        log.error("Table creation failed: %s", e)
        return False


def save_analysis(company_name, fiscal_year, financial_data, ratios):
    engine = get_engine()
    try:
        _validate_required(company_name, "company_name")
        _validate_financial_data(financial_data)
        with engine.connect() as conn:
            with conn.begin():
                row = conn.execute(
                    text("SELECT company_id FROM companies WHERE company_name = :cn"),
                    {"cn": company_name},
                ).fetchone()
                if row:
                    company_id = row[0]
                else:
                    result = conn.execute(
                        insert(text("companies")).values(company_name=company_name).prefix_with("OR IGNORE"),
                        {"company_name": company_name},
                    )
                    company_id = conn.execute(
                        text("SELECT company_id FROM companies WHERE company_name = :cn"),
                        {"cn": company_name},
                    ).fetchone()[0]
                    log.info("New company added: %s (ID: %d)", company_name, company_id)

                row = conn.execute(
                    text("SELECT fiscal_year_id FROM fiscal_years WHERE company_id = :cid AND year = :yr"),
                    {"cid": company_id, "yr": fiscal_year},
                ).fetchone()
                if row:
                    fiscal_year_id = row[0]
                    log.info("Fiscal year %d already exists (ID: %d)", fiscal_year, fiscal_year_id)
                else:
                    conn.execute(
                        text("INSERT INTO fiscal_years (company_id, year, start_date, end_date) VALUES (:cid, :yr, :sd, :ed)"),
                        {"cid": company_id, "yr": fiscal_year, "sd": f"{fiscal_year}-01-01", "ed": f"{fiscal_year}-12-31"},
                    )
                    fiscal_year_id = conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
                    log.info("Fiscal year %d added (ID: %d)", fiscal_year, fiscal_year_id)

                for tbl in ["income_statement", "equity", "liabilities", "assets", "financial_ratios"]:
                    if tbl not in _ALLOWED_TABLES:
                        raise ValidationError(f"Invalid table name: {tbl}")
                    conn.execute(text(f"DELETE FROM {tbl} WHERE fiscal_year_id = :fid"), {"fid": fiscal_year_id})

                current_assets = financial_data.get('current_assets', 0) or 0
                total_assets = financial_data.get('total_assets', 0) or 0
                non_current_assets = total_assets - current_assets
                conn.execute(
                    text("INSERT INTO assets (fiscal_year_id, current_assets, non_current_assets, total_assets) VALUES (:fid, :ca, :nca, :ta)"),
                    {"fid": fiscal_year_id, "ca": current_assets, "nca": non_current_assets, "ta": total_assets},
                )

                current_liabilities = financial_data.get('current_liabilities', 0) or 0
                total_liabilities = financial_data.get('total_liabilities', 0) or 0
                non_current_liabilities = total_liabilities - current_liabilities
                conn.execute(
                    text("INSERT INTO liabilities (fiscal_year_id, current_liabilities, non_current_liabilities, total_liabilities) VALUES (:fid, :cl, :ncl, :tl)"),
                    {"fid": fiscal_year_id, "cl": current_liabilities, "ncl": non_current_liabilities, "tl": total_liabilities},
                )

                equity_val = financial_data.get('equity', 0) or 0
                retained_earnings = financial_data.get('retained_earnings', equity_val)
                conn.execute(
                    text("INSERT INTO equity (fiscal_year_id, retained_earnings, total_equity) VALUES (:fid, :re, :te)"),
                    {"fid": fiscal_year_id, "re": retained_earnings, "te": equity_val},
                )

                conn.execute(
                    text("INSERT INTO income_statement (fiscal_year_id, revenue, cost_of_goods_sold, gross_profit, net_income) VALUES (:fid, :rev, :cogs, :gp, :ni)"),
                    {
                        "fid": fiscal_year_id,
                        "rev": financial_data.get('revenue', 0) or 0,
                        "cogs": financial_data.get('cost_of_goods_sold', 0) or 0,
                        "gp": financial_data.get('gross_profit', 0) or 0,
                        "ni": financial_data.get('net_income', 0) or 0,
                    },
                )

                conn.execute(
                    text(
                        "INSERT INTO financial_ratios (fiscal_year_id, current_ratio, quick_ratio, gross_profit_margin, "
                        "net_profit_margin, roa, roe, asset_turnover, receivables_turnover, debt_to_equity, debt_ratio, "
                        "days_sales_outstanding, inventory_turnover) VALUES (:fid, :cr, :qr, :gpm, :npm, :roa, :roe, :at, :rt, :dte, :dr, :dso, :it)"
                    ),
                    {
                        "fid": fiscal_year_id,
                        "cr": ratios.get('current_ratio', 0) or 0,
                        "qr": ratios.get('quick_ratio', 0) or 0,
                        "gpm": ratios.get('gross_profit_margin', 0) or 0,
                        "npm": ratios.get('net_profit_margin', 0) or 0,
                        "roa": ratios.get('roa', 0) or 0,
                        "roe": ratios.get('roe', 0) or 0,
                        "at": ratios.get('asset_turnover', 0) or 0,
                        "rt": ratios.get('receivables_turnover', 0) or 0,
                        "dte": ratios.get('debt_to_equity', 0) or 0,
                        "dr": ratios.get('debt_ratio', 0) or 0,
                        "dso": ratios.get('days_sales_outstanding', 0) or 0,
                        "it": ratios.get('inventory_turnover', 0) or 0,
                    },
                )
        log.info("Analysis saved: company=%s, year=%d, fiscal_year_id=%d", company_name, fiscal_year, fiscal_year_id)
        return fiscal_year_id
    except ValidationError as e:
        log.warning("Validation error in save_analysis: %s", e)
        return None
    except Exception as e:
        log.error("خطأ في حفظ التحليل: %s", e)
        return None


def get_company_analyses(company_name):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT c.company_name, fy.year, fy.fiscal_year_id, fr.current_ratio, fr.net_profit_margin, "
                    "fr.roe, fr.debt_to_equity, a.total_assets, l.total_liabilities, e.total_equity "
                    "FROM companies c "
                    "JOIN fiscal_years fy ON c.company_id = fy.company_id "
                    "LEFT JOIN financial_ratios fr ON fy.fiscal_year_id = fr.fiscal_year_id "
                    "LEFT JOIN assets a ON fy.fiscal_year_id = a.fiscal_year_id "
                    "LEFT JOIN liabilities l ON fy.fiscal_year_id = l.fiscal_year_id "
                    "LEFT JOIN equity e ON fy.fiscal_year_id = e.fiscal_year_id "
                    "WHERE c.company_name = :cn ORDER BY fy.year DESC"
                ),
                {"cn": company_name},
            ).fetchall()
        return [
            {
                "company_name": r[0], "year": r[1], "fiscal_year_id": r[2],
                "current_ratio": r[3], "net_profit_margin": r[4], "roe": r[5],
                "debt_to_equity": r[6], "total_assets": r[7], "total_liabilities": r[8],
                "total_equity": r[9],
            }
            for r in rows
        ]
    except Exception as e:
        log.error("خطأ في استرجاع التحليلات: %s", e)
        return []


def get_company_dupont_history(company_name):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT fy.year, fr.net_profit_margin, fr.asset_turnover, fr.roe "
                    "FROM companies c "
                    "JOIN fiscal_years fy ON c.company_id = fy.company_id "
                    "LEFT JOIN financial_ratios fr ON fy.fiscal_year_id = fr.fiscal_year_id "
                    "WHERE c.company_name = :cn ORDER BY fy.year ASC"
                ),
                {"cn": company_name},
            ).fetchall()
        results = []
        for row in rows:
            year = row[0]
            npm = row[1] or 0
            at = row[2] or 0
            roe = row[3] or 0
            denominator = npm * at
            em = round(roe / denominator, 4) if denominator != 0 else 0
            results.append({
                "year": year,
                "net_profit_margin": round(npm, 4),
                "asset_turnover": round(at, 4),
                "equity_multiplier": em,
                "roe": round(roe, 4),
            })
        return results
    except Exception as e:
        log.error("خطأ في استرجاع تاريخ DuPont: %s", e)
        return []


def save_scenario_results(fiscal_year_id, scenarios):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text("DELETE FROM scenario_results WHERE fiscal_year_id = :fid"), {"fid": fiscal_year_id})
                for sc_type in ("best", "base", "worst"):
                    sc = scenarios.get(sc_type)
                    if not sc:
                        continue
                    assumptions = sc.get("assumptions", {})
                    conn.execute(
                        text(
                            "INSERT INTO scenario_results "
                            "(fiscal_year_id, scenario_type, revenue_change_pct, cost_change_pct, "
                            "efficiency_change_pct, projected_revenue, projected_net_income, "
                            "net_profit_margin, roe, result_json) "
                            "VALUES (:fid, :st, :rcp, :ccp, :ecp, :pr, :pni, :npm, :roe, :rj)"
                        ),
                        {
                            "fid": fiscal_year_id,
                            "st": sc_type,
                            "rcp": assumptions.get("revenue_change_pct", 0),
                            "ccp": assumptions.get("cost_change_pct", 0),
                            "ecp": assumptions.get("efficiency_change_pct", 0),
                            "pr": sc.get("revenue", 0),
                            "pni": sc.get("net_income", 0),
                            "npm": sc.get("net_profit_margin", 0),
                            "roe": sc.get("roe", 0),
                            "rj": _json.dumps(sc, ensure_ascii=False),
                        },
                    )
        log.info("Scenario results saved for fiscal year %s", fiscal_year_id)
        return True
    except Exception as e:
        log.error("خطأ في حفظ نتائج السيناريوهات: %s", e)
        return False


def get_scenario_results(fiscal_year_id):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT scenario_type, result_json FROM scenario_results WHERE fiscal_year_id = :fid ORDER BY scenario_id ASC"),
                {"fid": fiscal_year_id},
            ).fetchall()
        results = {}
        for row in rows:
            try:
                results[row[0]] = _json.loads(row[1])
            except Exception:
                continue
        return results
    except Exception as e:
        log.error("خطأ في استرجاع نتائج السيناريوهات: %s", e)
        return {}


def save_tax_data(fiscal_year_id, tax_data):
    engine = get_engine()
    try:
        _validate_positive(tax_data.get("ibs_amount", 0), "ibs_amount")
        _validate_positive(tax_data.get("tva_collected", 0), "tva_collected")
        _validate_positive(tax_data.get("total_taxes", 0), "total_taxes")
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text("DELETE FROM tax_data WHERE fiscal_year_id = :fid"), {"fid": fiscal_year_id})
                conn.execute(
                    text(
                        "INSERT INTO tax_data "
                        "(fiscal_year_id, activity_type, number_of_employees, avg_salary, is_construction, "
                        "ibs_amount, ibs_rate, tva_collected, tva_paid, tva_net, irg_total, "
                        "cnas_employer, cnas_employee, cnas_total, cnac_employer, cnac_employee, cnac_total, "
                        "vf_amount, total_taxes, tax_burden_pct, simulation_json) "
                        "VALUES (:fid, :at, :noe, :as, :ic, :ia, :ir, :tc, :tp, :tn, :it, "
                        ":ce, :ce2, :ct, :cae, :cae2, :cat, :vf, :tt, :tbp, :sj)"
                    ),
                    {
                        "fid": fiscal_year_id,
                        "at": tax_data.get("activity_type", "other"),
                        "noe": tax_data.get("number_of_employees", 0),
                        "as": tax_data.get("avg_salary", 0),
                        "ic": 1 if tax_data.get("is_construction", False) else 0,
                        "ia": tax_data.get("ibs_amount", 0),
                        "ir": tax_data.get("ibs_rate", 0),
                        "tc": tax_data.get("tva_collected", 0),
                        "tp": tax_data.get("tva_paid", 0),
                        "tn": tax_data.get("tva_net", 0),
                        "it": tax_data.get("irg_total", 0),
                        "ce": tax_data.get("cnas_employer", 0),
                        "ce2": tax_data.get("cnas_employee", 0),
                        "ct": tax_data.get("cnas_total", 0),
                        "cae": tax_data.get("cnac_employer", 0),
                        "cae2": tax_data.get("cnac_employee", 0),
                        "cat": tax_data.get("cnac_total", 0),
                        "vf": tax_data.get("vf_amount", 0),
                        "tt": tax_data.get("total_taxes", 0),
                        "tbp": tax_data.get("tax_burden_pct", 0),
                        "sj": _json.dumps(tax_data.get("simulation", {}), ensure_ascii=False),
                    },
                )
        return True
    except (ValidationError, Exception) as e:
        log.error("خطأ في حفظ بيانات الضرائب: %s", e)
        return False


def get_tax_data(fiscal_year_id):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM tax_data WHERE fiscal_year_id = :fid ORDER BY created_date DESC LIMIT 1"),
                {"fid": fiscal_year_id},
            ).fetchone()
        if row:
            return {
                "tax_id": row[0], "fiscal_year_id": row[1],
                "activity_type": row[2], "number_of_employees": row[3],
                "avg_salary": row[4], "is_construction": bool(row[5]),
                "ibs_amount": row[6], "ibs_rate": row[7],
                "tva_collected": row[8], "tva_paid": row[9], "tva_net": row[10],
                "irg_total": row[11],
                "cnas_employer": row[12], "cnas_employee": row[13], "cnas_total": row[14],
                "cnac_employer": row[15], "cnac_employee": row[16], "cnac_total": row[17],
                "vf_amount": row[18], "total_taxes": row[19], "tax_burden_pct": row[20],
                "simulation": _json.loads(row[21]) if row[21] else {},
            }
        return None
    except Exception as e:
        log.error("خطأ في استرجاع بيانات الضرائب: %s", e)
        return None


def save_tax_obligation(fiscal_year_id, obligation):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text(
                        "INSERT INTO tax_obligations (fiscal_year_id, tax_type, due_month, due_day, amount, status, notes) "
                        "VALUES (:fid, :tt, :dm, :dd, :amt, :st, :nt)"
                    ),
                    {
                        "fid": fiscal_year_id,
                        "tt": obligation.get("tax_type", ""),
                        "dm": obligation.get("month", 1),
                        "dd": obligation.get("due_day", 20),
                        "amt": obligation.get("amount", 0),
                        "st": obligation.get("status", "pending"),
                        "nt": obligation.get("notes", ""),
                    },
                )
        return True
    except Exception as e:
        log.error("Failed to save tax obligation: %s", e)
        return False


def get_tax_obligations(fiscal_year_id, month=None):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            if month:
                rows = conn.execute(
                    text("SELECT * FROM tax_obligations WHERE fiscal_year_id = :fid AND due_month = :dm ORDER BY due_day"),
                    {"fid": fiscal_year_id, "dm": month},
                ).fetchall()
            else:
                rows = conn.execute(
                    text("SELECT * FROM tax_obligations WHERE fiscal_year_id = :fid ORDER BY due_month, due_day"),
                    {"fid": fiscal_year_id},
                ).fetchall()
        return [
            {
                "obligation_id": r[0], "fiscal_year_id": r[1], "tax_type": r[2],
                "due_month": r[3], "due_day": r[4], "amount": r[5],
                "status": r[6], "paid_date": r[7], "notes": r[8],
            }
            for r in rows
        ]
    except Exception as e:
        log.error("Failed to get tax obligations: %s", e)
        return []


def update_obligation_status(obligation_id, status, paid_date=None):
    if status not in _VALID_STATUSES:
        log.warning("Invalid obligation status: %s", status)
        return False
    engine = get_engine()
    try:
        with engine.connect() as conn:
            with conn.begin():
                if paid_date:
                    conn.execute(
                        text("UPDATE tax_obligations SET status = :st, paid_date = :pd WHERE obligation_id = :oid"),
                        {"st": status, "pd": paid_date, "oid": obligation_id},
                    )
                else:
                    conn.execute(
                        text("UPDATE tax_obligations SET status = :st WHERE obligation_id = :oid"),
                        {"st": status, "oid": obligation_id},
                    )
        return True
    except Exception as e:
        log.error("Failed to update obligation status: %s", e)
        return False


def delete_analysis(company_name, year):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            with conn.begin():
                row = conn.execute(
                    text(
                        "SELECT fiscal_year_id FROM fiscal_years WHERE company_id = "
                        "(SELECT company_id FROM companies WHERE company_name = :cn) AND year = :yr"
                    ),
                    {"cn": company_name, "yr": year},
                ).fetchone()
                if not row:
                    return False
                fid = row[0]
                conn.execute(
                    text("DELETE FROM notes WHERE audit_log_id IN (SELECT log_id FROM audit_log WHERE fiscal_year_id = :fid)"),
                    {"fid": fid},
                )
                for tbl in ["audit_log", "tax_data", "tax_obligations",
                            "income_statement", "equity", "liabilities", "assets", "financial_ratios"]:
                    if tbl not in _ALLOWED_TABLES:
                        raise ValidationError(f"Invalid table name: {tbl}")
                    conn.execute(text(f"DELETE FROM {tbl} WHERE fiscal_year_id = :fid"), {"fid": fid})
                conn.execute(text("DELETE FROM fiscal_years WHERE fiscal_year_id = :fid"), {"fid": fid})
        return True
    except Exception as e:
        log.error("Failed to delete analysis: %s", e)
        return False


def save_reference_standards(sector_code=None):
    from modules.benchmarks import ALGERIAN_SECTORS
    engine = get_engine()
    try:
        total = 0
        codes = [sector_code] if sector_code else list(ALGERIAN_SECTORS.keys())
        with engine.connect() as conn:
            with conn.begin():
                for code in codes:
                    info = ALGERIAN_SECTORS.get(code)
                    if not info:
                        continue
                    conn.execute(text("DELETE FROM reference_standards WHERE sector_code = :sc"), {"sc": code})
                    rows = []
                    for rname, bm in info["benchmarks"].items():
                        ideal_min, ideal_max = bm["ideal"]
                        rows.append({
                            "sector_code": code, "ratio_name": rname,
                            "min_val": bm["min"], "avg_val": bm["avg"], "max_val": bm["max"],
                            "ideal_min": ideal_min, "ideal_max": ideal_max,
                            "best_practice": bm["best_practice"], "international": bm["international"],
                        })
                    if rows:
                        conn.execute(
                            insert(text("reference_standards")),
                            rows,
                        )
                        total += len(rows)
        log.info("Reference standards seeded: %d rows", total)
        return total
    except Exception as e:
        log.error("Failed to save reference standards: %s", e)
        return 0


def get_reference_standards(sector_code=None):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            if sector_code:
                rows = conn.execute(
                    text(
                        "SELECT sector_code, ratio_name, min_val, avg_val, max_val, "
                        "ideal_min, ideal_max, best_practice, international "
                        "FROM reference_standards WHERE sector_code = :sc ORDER BY ratio_name"
                    ),
                    {"sc": sector_code},
                ).fetchall()
            else:
                rows = conn.execute(
                    text(
                        "SELECT sector_code, ratio_name, min_val, avg_val, max_val, "
                        "ideal_min, ideal_max, best_practice, international "
                        "FROM reference_standards ORDER BY sector_code, ratio_name"
                    ),
                ).fetchall()
            if not rows and sector_code:
                from modules.benchmarks import ALGERIAN_SECTORS
                if sector_code in ALGERIAN_SECTORS:
                    save_reference_standards(sector_code)
                    return get_reference_standards(sector_code)
        return [
            {
                "sector_code": r[0], "ratio_name": r[1],
                "min_val": r[2], "avg_val": r[3], "max_val": r[4],
                "ideal_min": r[5], "ideal_max": r[6],
                "best_practice": r[7], "international": r[8],
            }
            for r in rows
        ]
    except Exception as e:
        log.error("Failed to load reference standards: %s", e)
        return []


def save_competitor(sector_code, competitor_name, ratios):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("DELETE FROM competitor_data WHERE sector_code = :sc AND competitor_name = :cn"),
                    {"sc": sector_code, "cn": competitor_name},
                )
                rows = []
                for rname, value in (ratios or {}).items():
                    if value is None:
                        continue
                    rows.append({
                        "sector_code": sector_code,
                        "competitor_name": competitor_name,
                        "ratio_name": rname,
                        "ratio_value": float(value),
                    })
                if rows:
                    conn.execute(insert(text("competitor_data")), rows)
        log.info("Competitor saved: %s (%s) - %d ratios", competitor_name, sector_code, len(ratios or {}))
        return True
    except Exception as e:
        log.error("Failed to save competitor: %s", e)
        return False


def get_competitors(sector_code):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT competitor_name, ratio_name, ratio_value "
                    "FROM competitor_data WHERE sector_code = :sc "
                    "ORDER BY competitor_name, ratio_name"
                ),
                {"sc": sector_code},
            ).fetchall()
        grouped = {}
        for name, rname, value in rows:
            grouped.setdefault(name, {})[rname] = float(value)
        return [{"name": name, "ratios": ratios} for name, ratios in grouped.items()]
    except Exception as e:
        log.error("Failed to load competitors: %s", e)
        return []


def delete_competitor(sector_code, competitor_name):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            with conn.begin():
                result = conn.execute(
                    text("DELETE FROM competitor_data WHERE sector_code = :sc AND competitor_name = :cn"),
                    {"sc": sector_code, "cn": competitor_name},
                )
                deleted = result.rowcount
        log.info("Competitor deleted: %s (%s) - rows=%d", competitor_name, sector_code, deleted)
        return deleted > 0
    except Exception as e:
        log.error("Failed to delete competitor: %s", e)
        return False


def get_company_ratio_history(company_name):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT fy.year, fr.current_ratio, fr.quick_ratio, fr.gross_profit_margin, "
                    "fr.net_profit_margin, fr.roa, fr.roe, fr.asset_turnover, fr.debt_to_equity, "
                    "fr.inventory_turnover "
                    "FROM companies c "
                    "JOIN fiscal_years fy ON c.company_id = fy.company_id "
                    "LEFT JOIN financial_ratios fr ON fy.fiscal_year_id = fr.fiscal_year_id "
                    "WHERE c.company_name = :cn ORDER BY fy.year ASC"
                ),
                {"cn": company_name},
            ).fetchall()
        keys = (
            "current_ratio", "quick_ratio", "gross_profit_margin",
            "net_profit_margin", "roa", "roe", "asset_turnover",
            "debt_to_equity", "inventory_turnover",
        )
        results = []
        for row in rows:
            ratios = {}
            for key, val in zip(keys, row[1:]):
                if val is not None:
                    ratios[key] = round(float(val), 4)
            results.append({"year": row[0], "ratios": ratios})
        return results
    except Exception as e:
        log.error("Failed to load ratio history: %s", e)
        return []


def save_dashboard_layout(layout_name, layout_dict):
    if not layout_name or not isinstance(layout_dict, dict):
        log.error("Invalid dashboard layout: name=%s", layout_name)
        return False
    engine = get_engine()
    try:
        payload = _json.dumps(layout_dict, ensure_ascii=False)
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text(
                        "INSERT INTO dashboard_layouts (layout_name, layout_json) VALUES (:ln, :lj) "
                        "ON CONFLICT(layout_name) DO UPDATE SET "
                        "layout_json = excluded.layout_json, updated_at = CURRENT_TIMESTAMP"
                    ),
                    {"ln": layout_name, "lj": payload},
                )
        log.info("Dashboard layout saved: %s", layout_name)
        return True
    except Exception as e:
        log.error("Failed to save dashboard layout: %s", e)
        return False


def get_dashboard_layouts():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT layout_name, layout_json, updated_at FROM dashboard_layouts ORDER BY layout_name ASC"),
            ).fetchall()
        results = []
        for name, payload, updated_at in rows:
            try:
                layout = _json.loads(payload) if payload else {}
            except (ValueError, TypeError):
                layout = {}
            results.append({
                "name": name,
                "layout": layout,
                "updated_at": updated_at,
            })
        return results
    except Exception as e:
        log.error("Failed to load dashboard layouts: %s", e)
        return []


def delete_dashboard_layout(layout_name):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            with conn.begin():
                result = conn.execute(
                    text("DELETE FROM dashboard_layouts WHERE layout_name = :ln"),
                    {"ln": layout_name},
                )
                deleted = result.rowcount
        log.info("Dashboard layout deleted: %s - rows=%d", layout_name, deleted)
        return deleted > 0
    except Exception as e:
        log.error("Failed to delete dashboard layout: %s", e)
        return False
