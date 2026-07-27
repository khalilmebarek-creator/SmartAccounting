# إنشاء جداول قاعدة البيانات
# ==========================

from database.db_connection import db
from utils.app_logger import get_logger

log = get_logger("db_schema")

TABLE_NAMES = [
    "companies", "fiscal_years", "assets", "liabilities",
    "equity", "income_statement", "financial_ratios",
    "audit_log", "notes", "tax_data", "tax_obligations"
]

def create_tables():
    """إنشاء جميع جداول قاعدة البيانات"""
    
    if not db.connect():
        log.error("Database connection failed")
        return False
    
    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name VARCHAR(255) NOT NULL,
                industry VARCHAR(100),
                registration_number VARCHAR(100),
                country VARCHAR(100),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS fiscal_years (
                fiscal_year_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER,
                start_date DATE,
                end_date DATE,
                FOREIGN KEY (company_id) REFERENCES companies(company_id),
                UNIQUE(company_id, year)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fiscal_year_id INTEGER NOT NULL,
                asset_name VARCHAR(255),
                current_assets DECIMAL(15,2),
                non_current_assets DECIMAL(15,2),
                total_assets DECIMAL(15,2),
                FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
                UNIQUE(fiscal_year_id)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS liabilities (
                liability_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fiscal_year_id INTEGER NOT NULL,
                current_liabilities DECIMAL(15,2),
                non_current_liabilities DECIMAL(15,2),
                total_liabilities DECIMAL(15,2),
                FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
                UNIQUE(fiscal_year_id)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS equity (
                equity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fiscal_year_id INTEGER NOT NULL,
                share_capital DECIMAL(15,2),
                retained_earnings DECIMAL(15,2),
                total_equity DECIMAL(15,2),
                FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id),
                UNIQUE(fiscal_year_id)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS income_statement (
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
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS financial_ratios (
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
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fiscal_year_id INTEGER NOT NULL,
                issue_type VARCHAR(100),
                issue_description TEXT,
                severity VARCHAR(20),
                detected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50),
                FOREIGN KEY (fiscal_year_id) REFERENCES fiscal_years(fiscal_year_id)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_log_id INTEGER NOT NULL,
                reviewer_name VARCHAR(255),
                note_text TEXT,
                note_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (audit_log_id) REFERENCES audit_log(log_id)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS tax_data (
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
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS tax_obligations (
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
            )
        """)
        
        _create_indexes(db)
        
        log.info("All %d tables created successfully", len(TABLE_NAMES))
        return True
        
    except Exception as e:
        log.error("Table creation failed: %s", e)
        return False
    
    finally:
        db.disconnect()


def _create_indexes(db):
    indexes = [
        ("idx_fiscal_years_company", "fiscal_years", "company_id"),
        ("idx_fiscal_years_year", "fiscal_years", "year"),
        ("idx_assets_fy", "assets", "fiscal_year_id"),
        ("idx_liabilities_fy", "liabilities", "fiscal_year_id"),
        ("idx_equity_fy", "equity", "fiscal_year_id"),
        ("idx_income_fy", "income_statement", "fiscal_year_id"),
        ("idx_ratios_fy", "financial_ratios", "fiscal_year_id"),
        ("idx_audit_fy", "audit_log", "fiscal_year_id"),
        ("idx_notes_audit", "notes", "audit_log_id"),
        ("idx_tax_data_fy", "tax_data", "fiscal_year_id"),
        ("idx_tax_oblig_fy", "tax_obligations", "fiscal_year_id"),
        ("idx_tax_oblig_month", "tax_obligations", "due_month"),
        ("idx_companies_name", "companies", "company_name"),
    ]
    for idx_name, table, col in indexes:
        db.execute(
            f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({col})"
        )
    log.info("Created %d indexes", len(indexes))

if __name__ == "__main__":
    log.info("Starting database creation...")
    create_tables()