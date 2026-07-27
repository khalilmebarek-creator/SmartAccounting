# عمليات قاعدة البيانات - حفظ التحليلات
# ====================================

import logging
from database.db_connection import db
from utils.app_logger import get_logger

log = get_logger("db_operations")

_ALLOWED_TABLES = frozenset({"income_statement", "equity", "liabilities", "assets", "financial_ratios", "tax_data", "tax_obligations", "fiscal_years", "companies", "notes", "audit_log"})


class ValidationError(Exception):
    """بيانات غير صالحة للإدخال"""
    pass


def _validate_positive(value, field_name):
    """التحقق من أن القيمة موجبة"""
    if value is not None and value < 0:
        raise ValidationError(f"{field_name} must be non-negative (got {value})")


def _validate_required(value, field_name):
    """التحقق من وجود القيمة المطلوبة"""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} is required")


def _validate_financial_data(data):
    """التحقق من صحة البيانات المالية قبل الحفظ"""
    if not isinstance(data, dict):
        raise ValidationError("financial_data must be a dict")
    for key in ['revenue', 'total_assets', 'total_liabilities', 'equity']:
        val = data.get(key)
        if val is not None:
            _validate_positive(val, key)


def _validate_ratios(ratios):
    """التحقق من النسب المالية قبل الحفظ"""
    if not isinstance(ratios, dict):
        raise ValidationError("ratios must be a dict")


def save_analysis(company_name, fiscal_year, financial_data, ratios):
    """
    حفظ تحليل مالي كامل في قاعدة البيانات
    
    المدخلات:
        company_name: اسم الشركة
        fiscal_year: السنة المالية
        financial_data: dict يحتوي على بيانات الميزانية وقائمة الدخل
        ratios: dict يحتوي على النسب المالية المحسوبة
    
    المخرجات:
        fiscal_year_id إذا نجح، None إذا فشل
    """
    if not db.connect():
        log.error("فشل الاتصال بقاعدة البيانات")
        return None
    
    try:
        _validate_required(company_name, "company_name")
        _validate_financial_data(financial_data)
        # 1️⃣ إضافة الشركة (أو استرجاع ID لو موجودة)
        db.cursor.execute(
            "SELECT company_id FROM companies WHERE company_name = ?",
            (company_name,)
        )
        result = db.cursor.fetchone()
        
        if result:
            company_id = result[0]
        else:
            db.cursor.execute(
                "INSERT INTO companies (company_name) VALUES (?)",
                (company_name,)
            )
            company_id = db.cursor.lastrowid
            log.info("New company added: %s (ID: %d)", company_name, company_id)
        
        # 2️⃣ إضافة السنة المالية (أو استرجاع ID لو موجودة)
        db.cursor.execute(
            "SELECT fiscal_year_id FROM fiscal_years WHERE company_id = ? AND year = ?",
            (company_id, fiscal_year)
        )
        result = db.cursor.fetchone()
        
        if result:
            fiscal_year_id = result[0]
            log.info("Fiscal year %d already exists (ID: %d)", fiscal_year, fiscal_year_id)
        else:
            db.cursor.execute(
                """INSERT INTO fiscal_years (company_id, year, start_date, end_date)
                   VALUES (?, ?, ?, ?)""",
                (
                    company_id,
                    fiscal_year,
                    f"{fiscal_year}-01-01",
                    f"{fiscal_year}-12-31"
                )
            )
            fiscal_year_id = db.cursor.lastrowid
            log.info("Fiscal year %d added (ID: %d)", fiscal_year, fiscal_year_id)
        
        # 3️⃣ حذف البيانات القديمة إن وجدت (لتجنب التكرار)
        for tbl in ["income_statement", "equity", "liabilities", "assets", "financial_ratios"]:
            if tbl not in _ALLOWED_TABLES:
                raise ValidationError(f"Invalid table name: {tbl}")
            db.cursor.execute(f"DELETE FROM {tbl} WHERE fiscal_year_id = ?", (fiscal_year_id,))
        
        # 4️⃣ إضافة الأصول
        current_assets = financial_data.get('current_assets', 0) or 0
        total_assets = financial_data.get('total_assets', 0) or 0
        non_current_assets = total_assets - current_assets
        
        db.cursor.execute(
            """INSERT INTO assets
               (fiscal_year_id, current_assets, non_current_assets, total_assets)
               VALUES (?, ?, ?, ?)""",
            (fiscal_year_id, current_assets, non_current_assets, total_assets)
        )
        
        # 5️⃣ إضافة الالتزامات
        current_liabilities = financial_data.get('current_liabilities', 0) or 0
        total_liabilities = financial_data.get('total_liabilities', 0) or 0
        non_current_liabilities = total_liabilities - current_liabilities
        
        db.cursor.execute(
            """INSERT INTO liabilities
               (fiscal_year_id, current_liabilities, non_current_liabilities, total_liabilities)
               VALUES (?, ?, ?, ?)""",
            (fiscal_year_id, current_liabilities, non_current_liabilities, total_liabilities)
        )
        
        # 6️⃣ إضافة حقوق المالكين
        equity = financial_data.get('equity', 0) or 0
        retained_earnings = financial_data.get('retained_earnings', equity)
        
        db.cursor.execute(
            """INSERT INTO equity
               (fiscal_year_id, retained_earnings, total_equity)
               VALUES (?, ?, ?)""",
            (fiscal_year_id, retained_earnings, equity)
        )
        
        # 7️⃣ إضافة قائمة الدخل
        db.cursor.execute(
            """INSERT INTO income_statement
               (fiscal_year_id, revenue, cost_of_goods_sold, gross_profit,
                net_income)
               VALUES (?, ?, ?, ?, ?)""",
            (
                fiscal_year_id,
                financial_data.get('revenue', 0) or 0,
                financial_data.get('cost_of_goods_sold', 0) or 0,
                financial_data.get('gross_profit', 0) or 0,
                financial_data.get('net_income', 0) or 0
            )
        )
        
        # 8️⃣ إضافة النسب المالية
        db.cursor.execute(
            """INSERT INTO financial_ratios
               (fiscal_year_id, current_ratio, quick_ratio, gross_profit_margin,
                net_profit_margin, roa, roe, asset_turnover,
                receivables_turnover, debt_to_equity, debt_ratio,
                days_sales_outstanding, inventory_turnover)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                fiscal_year_id,
                ratios.get('current_ratio', 0) or 0,
                ratios.get('quick_ratio', 0) or 0,
                ratios.get('gross_profit_margin', 0) or 0,
                ratios.get('net_profit_margin', 0) or 0,
                ratios.get('roa', 0) or 0,
                ratios.get('roe', 0) or 0,
                ratios.get('asset_turnover', 0) or 0,
                ratios.get('receivables_turnover', 0) or 0,
                ratios.get('debt_to_equity', 0) or 0,
                ratios.get('debt_ratio', 0) or 0,
                ratios.get('days_sales_outstanding', 0) or 0,
                ratios.get('inventory_turnover', 0) or 0
            )
        )
        
        db.connection.commit()
        log.info("Analysis saved: company=%s, year=%d, fiscal_year_id=%d", company_name, fiscal_year, fiscal_year_id)
        return fiscal_year_id
        
    except ValidationError as e:
        db.connection.rollback()
        log.warning("Validation error in save_analysis: %s", e)
        return None
    except Exception as e:
        db.connection.rollback()
        log.error("خطأ في حفظ التحليل: %s", e)
        return None
        
    finally:
        db.disconnect()


def get_company_analyses(company_name):
    """
    استرجاع كل التحليلات لشركة معينة
    
    المخرجات:
        list of dicts تحتوي على التحليلات
    """
    if not db.connect():
        return []
    
    try:
        query = """
            SELECT 
                c.company_name,
                fy.year,
                fy.fiscal_year_id,
                fr.current_ratio,
                fr.net_profit_margin,
                fr.roe,
                fr.debt_to_equity,
                a.total_assets,
                l.total_liabilities,
                e.total_equity
            FROM companies c
            JOIN fiscal_years fy ON c.company_id = fy.company_id
            LEFT JOIN financial_ratios fr ON fy.fiscal_year_id = fr.fiscal_year_id
            LEFT JOIN assets a ON fy.fiscal_year_id = a.fiscal_year_id
            LEFT JOIN liabilities l ON fy.fiscal_year_id = l.fiscal_year_id
            LEFT JOIN equity e ON fy.fiscal_year_id = e.fiscal_year_id
            WHERE c.company_name = ?
            ORDER BY fy.year DESC
        """
        db.cursor.execute(query, (company_name,))
        rows = db.cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'company_name': row[0],
                'year': row[1],
                'fiscal_year_id': row[2],
                'current_ratio': row[3],
                'net_profit_margin': row[4],
                'roe': row[5],
                'debt_to_equity': row[6],
                'total_assets': row[7],
                'total_liabilities': row[8],
                'total_equity': row[9]
            })
        
        return results
        
    except Exception as e:
        log.error("خطأ في استرجاع التحليلات: %s", e)
        return []
        
    finally:
        db.disconnect()


def save_tax_data(fiscal_year_id, tax_data):
    """حفظ بيانات الضرائب لسنة مالية"""
    if not db.connect():
        return False
    
    try:
        import json as _json
        _validate_positive(tax_data.get("ibs_amount", 0), "ibs_amount")
        _validate_positive(tax_data.get("tva_collected", 0), "tva_collected")
        _validate_positive(tax_data.get("total_taxes", 0), "total_taxes")
        db.cursor.execute("DELETE FROM tax_data WHERE fiscal_year_id = ?", (fiscal_year_id,))
        db.cursor.execute(
            """INSERT INTO tax_data
               (fiscal_year_id, activity_type, number_of_employees, avg_salary,
                is_construction, ibs_amount, ibs_rate, tva_collected, tva_paid,
                tva_net, irg_total, cnas_employer, cnas_employee, cnas_total,
                cnac_employer, cnac_employee, cnac_total, vf_amount,
                total_taxes, tax_burden_pct, simulation_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                fiscal_year_id,
                tax_data.get("activity_type", "other"),
                tax_data.get("number_of_employees", 0),
                tax_data.get("avg_salary", 0),
                1 if tax_data.get("is_construction", False) else 0,
                tax_data.get("ibs_amount", 0),
                tax_data.get("ibs_rate", 0),
                tax_data.get("tva_collected", 0),
                tax_data.get("tva_paid", 0),
                tax_data.get("tva_net", 0),
                tax_data.get("irg_total", 0),
                tax_data.get("cnas_employer", 0),
                tax_data.get("cnas_employee", 0),
                tax_data.get("cnas_total", 0),
                tax_data.get("cnac_employer", 0),
                tax_data.get("cnac_employee", 0),
                tax_data.get("cnac_total", 0),
                tax_data.get("vf_amount", 0),
                tax_data.get("total_taxes", 0),
                tax_data.get("tax_burden_pct", 0),
                _json.dumps(tax_data.get("simulation", {}), ensure_ascii=False)
            )
        )
        db.connection.commit()
        return True
    except (ValidationError, Exception) as e:
        db.connection.rollback()
        log.error("خطأ في حفظ بيانات الضرائب: %s", e)
        return False
    finally:
        db.disconnect()


def get_tax_data(fiscal_year_id):
    """استرجاع بيانات الضرائب لسنة مالية"""
    if not db.connect():
        return None
    
    try:
        db.cursor.execute(
            "SELECT * FROM tax_data WHERE fiscal_year_id = ? ORDER BY created_date DESC LIMIT 1",
            (fiscal_year_id,)
        )
        row = db.cursor.fetchone()
        if row:
            import json as _json
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
                "simulation": _json.loads(row[21]) if row[21] else {}
            }
        return None
    except Exception as e:
        log.error("خطأ في استرجاع بيانات الضرائب: %s", e)
        return None
    finally:
        db.disconnect()


def save_tax_obligation(fiscal_year_id, obligation):
    """حفظ التزام جبائي شهري"""
    if not db.connect():
        return False
    
    try:
        db.cursor.execute(
            """INSERT INTO tax_obligations
               (fiscal_year_id, tax_type, due_month, due_day, amount, status, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (fiscal_year_id, obligation.get("tax_type", ""), obligation.get("month", 1),
             obligation.get("due_day", 20), obligation.get("amount", 0),
             obligation.get("status", "pending"), obligation.get("notes", ""))
        )
        db.connection.commit()
        return True
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to save tax obligation: %s", e)
        return False
    finally:
        db.disconnect()


def get_tax_obligations(fiscal_year_id, month=None):
    """استرجاع الالتزامات الجبائية"""
    if not db.connect():
        return []
    
    try:
        if month:
            db.cursor.execute(
                "SELECT * FROM tax_obligations WHERE fiscal_year_id = ? AND due_month = ? ORDER BY due_day",
                (fiscal_year_id, month))
        else:
            db.cursor.execute(
                "SELECT * FROM tax_obligations WHERE fiscal_year_id = ? ORDER BY due_month, due_day",
                (fiscal_year_id,))
        rows = db.cursor.fetchall()
        return [{"obligation_id": r[0], "fiscal_year_id": r[1], "tax_type": r[2],
                 "due_month": r[3], "due_day": r[4], "amount": r[5],
                 "status": r[6], "paid_date": r[7], "notes": r[8]} for r in rows]
    except Exception as e:
        log.error("Failed to get tax obligations: %s", e)
        return []
    finally:
        db.disconnect()


_VALID_STATUSES = {"pending", "paid", "overdue", "cancelled"}


def update_obligation_status(obligation_id, status, paid_date=None):
    """تحديث حالة التزام جبائي"""
    if status not in _VALID_STATUSES:
        log.warning("Invalid obligation status: %s", status)
        return False
    if not db.connect():
        return False
    
    try:
        if paid_date:
            db.cursor.execute(
                "UPDATE tax_obligations SET status = ?, paid_date = ? WHERE obligation_id = ?",
                (status, paid_date, obligation_id))
        else:
            db.cursor.execute(
                "UPDATE tax_obligations SET status = ? WHERE obligation_id = ?",
                (status, obligation_id))
        db.connection.commit()
        return True
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to update obligation status: %s", e)
        return False
    finally:
        db.disconnect()


def delete_analysis(company_name, year):
    """حذف تحليل من قاعدة البيانات حسب اسم الشركة والسنة"""
    if not db.connect():
        return False
    try:
        db.cursor.execute(
            "SELECT fiscal_year_id FROM fiscal_years WHERE company_id = "
            "(SELECT company_id FROM companies WHERE company_name = ?) AND year = ?",
            (company_name, year))
        row = db.cursor.fetchone()
        if not row:
            return False
        fid = row[0]
        for tbl in ["notes", "audit_log", "tax_data", "tax_obligations",
                     "income_statement", "equity", "liabilities", "assets", "financial_ratios"]:
            if tbl not in _ALLOWED_TABLES:
                raise ValidationError(f"Invalid table name: {tbl}")
            db.cursor.execute(f"DELETE FROM {tbl} WHERE fiscal_year_id = ?", (fid,))
        db.cursor.execute("DELETE FROM fiscal_years WHERE fiscal_year_id = ?", (fid,))
        db.connection.commit()
        return True
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to delete analysis: %s", e)
        return False
    finally:
        db.disconnect()
