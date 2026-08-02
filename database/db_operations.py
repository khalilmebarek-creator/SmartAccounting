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


def get_company_dupont_history(company_name):
    """
    استرجاع تاريخ مكونات DuPont لشركة معينة عبر السنوات

    المخرجات:
        قائمة dicts: {year, net_profit_margin, asset_turnover, equity_multiplier, roe}
        equity_multiplier مشتق: EM = ROE / (NPM × AT) عندما المقام != 0
    """
    if not db.connect():
        return []

    try:
        query = """
            SELECT fy.year, fr.net_profit_margin, fr.asset_turnover, fr.roe
            FROM companies c
            JOIN fiscal_years fy ON c.company_id = fy.company_id
            LEFT JOIN financial_ratios fr ON fy.fiscal_year_id = fr.fiscal_year_id
            WHERE c.company_name = ?
            ORDER BY fy.year ASC
        """
        db.cursor.execute(query, (company_name,))
        rows = db.cursor.fetchall()

        results = []
        for row in rows:
            year = row[0]
            npm = row[1] or 0
            at = row[2] or 0
            roe = row[3] or 0
            denominator = npm * at
            em = round(roe / denominator, 4) if denominator != 0 else 0
            results.append({
                'year': year,
                'net_profit_margin': round(npm, 4),
                'asset_turnover': round(at, 4),
                'equity_multiplier': em,
                'roe': round(roe, 4),
            })

        return results

    except Exception as e:
        log.error("خطأ في استرجاع تاريخ DuPont: %s", e)
        return []

    finally:
        db.disconnect()


def save_scenario_results(fiscal_year_id, scenarios):
    """حفظ نتائج السيناريوهات (مثالي/طبيعي/أسوأ) لسنة مالية"""
    if not db.connect():
        return False

    try:
        import json as _json
        db.cursor.execute(
            "DELETE FROM scenario_results WHERE fiscal_year_id = ?",
            (fiscal_year_id,)
        )
        for sc_type in ("best", "base", "worst"):
            sc = scenarios.get(sc_type)
            if not sc:
                continue
            assumptions = sc.get("assumptions", {})
            db.cursor.execute(
                """INSERT INTO scenario_results
                   (fiscal_year_id, scenario_type, revenue_change_pct,
                    cost_change_pct, efficiency_change_pct, projected_revenue,
                    projected_net_income, net_profit_margin, roe, result_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fiscal_year_id,
                    sc_type,
                    assumptions.get("revenue_change_pct", 0),
                    assumptions.get("cost_change_pct", 0),
                    assumptions.get("efficiency_change_pct", 0),
                    sc.get("revenue", 0),
                    sc.get("net_income", 0),
                    sc.get("net_profit_margin", 0),
                    sc.get("roe", 0),
                    _json.dumps(sc, ensure_ascii=False)
                )
            )
        db.connection.commit()
        log.info("Scenario results saved for fiscal year %s", fiscal_year_id)
        return True
    except Exception as e:
        db.connection.rollback()
        log.error("خطأ في حفظ نتائج السيناريوهات: %s", e)
        return False
    finally:
        db.disconnect()


def get_scenario_results(fiscal_year_id):
    """استرجاع آخر نتائج السيناريوهات لسنة مالية"""
    if not db.connect():
        return {}

    try:
        import json as _json
        db.cursor.execute(
            """SELECT scenario_type, result_json
               FROM scenario_results
               WHERE fiscal_year_id = ?
               ORDER BY scenario_id ASC""",
            (fiscal_year_id,)
        )
        rows = db.cursor.fetchall()
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
        db.cursor.execute(
            "DELETE FROM notes WHERE audit_log_id IN "
            "(SELECT log_id FROM audit_log WHERE fiscal_year_id = ?)", (fid,))
        for tbl in ["audit_log", "tax_data", "tax_obligations",
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


# ===== المعايير المرجعية (Reference Standards) =====

def save_reference_standards(sector_code=None):
    """بذر جدول المعايير المرجعية من محرك المعايير (قطاع واحد أو الكل)

    المخرجات: عدد الصفوف المحفوظة
    """
    from modules.benchmarks import ALGERIAN_SECTORS
    if not db.connect():
        return 0
    try:
        total = 0
        codes = [sector_code] if sector_code else list(ALGERIAN_SECTORS.keys())
        for code in codes:
            info = ALGERIAN_SECTORS.get(code)
            if not info:
                continue
            db.cursor.execute(
                "DELETE FROM reference_standards WHERE sector_code = ?", (code,)
            )
            rows = []
            for rname, bm in info["benchmarks"].items():
                ideal_min, ideal_max = bm["ideal"]
                rows.append(
                    (code, rname, bm["min"], bm["avg"], bm["max"],
                     ideal_min, ideal_max, bm["best_practice"], bm["international"])
                )
            db.cursor.executemany(
                """INSERT INTO reference_standards
                   (sector_code, ratio_name, min_val, avg_val, max_val,
                    ideal_min, ideal_max, best_practice, international)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows
            )
            total += len(rows)
        db.connection.commit()
        log.info("Reference standards seeded: %d rows", total)
        return total
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to save reference standards: %s", e)
        return 0
    finally:
        db.disconnect()


def get_reference_standards(sector_code=None):
    """استرجاع المعايير المرجعية (يُبذر تلقائياً لقطاع معروف عند الفراغ)"""
    if not db.connect():
        return []
    try:
        if sector_code:
            db.cursor.execute(
                """SELECT sector_code, ratio_name, min_val, avg_val, max_val,
                          ideal_min, ideal_max, best_practice, international
                   FROM reference_standards
                   WHERE sector_code = ?
                   ORDER BY ratio_name""",
                (sector_code,)
            )
        else:
            db.cursor.execute(
                """SELECT sector_code, ratio_name, min_val, avg_val, max_val,
                          ideal_min, ideal_max, best_practice, international
                   FROM reference_standards
                   ORDER BY sector_code, ratio_name"""
            )
        rows = db.cursor.fetchall()
        if not rows and sector_code:
            from modules.benchmarks import ALGERIAN_SECTORS
            if sector_code in ALGERIAN_SECTORS:
                db.disconnect()
                save_reference_standards(sector_code)
                return get_reference_standards(sector_code)
        results = []
        for r in rows:
            results.append({
                "sector_code": r[0], "ratio_name": r[1],
                "min_val": r[2], "avg_val": r[3], "max_val": r[4],
                "ideal_min": r[5], "ideal_max": r[6],
                "best_practice": r[7], "international": r[8],
            })
        return results
    except Exception as e:
        log.error("Failed to load reference standards: %s", e)
        return []
    finally:
        db.disconnect()


# ===== بيانات المنافسين (Competitor Data) =====

def save_competitor(sector_code, competitor_name, ratios):
    """حفظ بيانات منافس (يستبدل بيانات المنافس الحالي كلياً)"""
    if not db.connect():
        return False
    try:
        db.cursor.execute(
            "DELETE FROM competitor_data WHERE sector_code = ? AND competitor_name = ?",
            (sector_code, competitor_name)
        )
        rows = []
        for rname, value in (ratios or {}).items():
            if value is None:
                continue
            rows.append((sector_code, competitor_name, rname, float(value)))
        db.cursor.executemany(
            """INSERT INTO competitor_data (sector_code, competitor_name, ratio_name, ratio_value)
               VALUES (?, ?, ?, ?)""",
            rows
        )
        db.connection.commit()
        log.info("Competitor saved: %s (%s) - %d ratios", competitor_name, sector_code, len(ratios or {}))
        return True
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to save competitor: %s", e)
        return False
    finally:
        db.disconnect()


def get_competitors(sector_code):
    """استرجاع كل المنافسين لقطاع (name + ratios)"""
    if not db.connect():
        return []
    try:
        db.cursor.execute(
            """SELECT competitor_name, ratio_name, ratio_value
               FROM competitor_data
               WHERE sector_code = ?
               ORDER BY competitor_name, ratio_name""",
            (sector_code,)
        )
        rows = db.cursor.fetchall()
        grouped = {}
        for name, rname, value in rows:
            grouped.setdefault(name, {})[rname] = float(value)
        return [
            {"name": name, "ratios": ratios}
            for name, ratios in grouped.items()
        ]
    except Exception as e:
        log.error("Failed to load competitors: %s", e)
        return []
    finally:
        db.disconnect()


def delete_competitor(sector_code, competitor_name):
    """حذف منافس من قطاع معين"""
    if not db.connect():
        return False
    try:
        db.cursor.execute(
            "DELETE FROM competitor_data WHERE sector_code = ? AND competitor_name = ?",
            (sector_code, competitor_name)
        )
        db.connection.commit()
        deleted = db.cursor.rowcount
        log.info("Competitor deleted: %s (%s) - rows=%d", competitor_name, sector_code, deleted)
        return deleted > 0
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to delete competitor: %s", e)
        return False
    finally:
        db.disconnect()


# ===== سجل النسب عبر السنوات (Trend) =====

def get_company_ratio_history(company_name):
    """استرجاع تاريخ النسب المالية للشركة عبر السنوات (لتحليل الاتجاه)

    المخرجات: قائمة {year, ratios} بترتيب تصاعدي
    """
    if not db.connect():
        return []
    try:
        db.cursor.execute(
            """SELECT fy.year, fr.current_ratio, fr.quick_ratio,
                      fr.gross_profit_margin, fr.net_profit_margin, fr.roa,
                      fr.roe, fr.asset_turnover, fr.debt_to_equity,
                      fr.inventory_turnover
               FROM companies c
               JOIN fiscal_years fy ON c.company_id = fy.company_id
               LEFT JOIN financial_ratios fr ON fy.fiscal_year_id = fr.fiscal_year_id
               WHERE c.company_name = ?
               ORDER BY fy.year ASC""",
            (company_name,)
        )
        rows = db.cursor.fetchall()
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
    finally:
        db.disconnect()


# ===== تخطيطات لوحة التحكم (Dashboard Layouts) =====

def save_dashboard_layout(layout_name, layout_dict):
    """حفظ/استبدال تخطيط لوحة التحكم المخصص"""
    import json
    if not layout_name or not isinstance(layout_dict, dict):
        log.error("Invalid dashboard layout: name=%s", layout_name)
        return False
    if not db.connect():
        return False
    try:
        payload = json.dumps(layout_dict, ensure_ascii=False)
        db.cursor.execute(
            """INSERT INTO dashboard_layouts (layout_name, layout_json)
               VALUES (?, ?)
               ON CONFLICT(layout_name) DO UPDATE SET
                   layout_json = excluded.layout_json,
                   updated_at = CURRENT_TIMESTAMP""",
            (layout_name, payload)
        )
        db.connection.commit()
        log.info("Dashboard layout saved: %s", layout_name)
        return True
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to save dashboard layout: %s", e)
        return False
    finally:
        db.disconnect()


def get_dashboard_layouts():
    """استرجاع كل تخطيطات لوحة التحكم المحفوظة"""
    import json
    if not db.connect():
        return []
    try:
        db.cursor.execute(
            """SELECT layout_name, layout_json, updated_at
               FROM dashboard_layouts
               ORDER BY layout_name ASC"""
        )
        rows = db.cursor.fetchall()
        results = []
        for name, payload, updated_at in rows:
            try:
                layout = json.loads(payload) if payload else {}
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
    finally:
        db.disconnect()


def delete_dashboard_layout(layout_name):
    """حذف تخطيط لوحة تحكم محفوظ"""
    if not db.connect():
        return False
    try:
        db.cursor.execute(
            "DELETE FROM dashboard_layouts WHERE layout_name = ?",
            (layout_name,)
        )
        db.connection.commit()
        deleted = db.cursor.rowcount
        log.info("Dashboard layout deleted: %s - rows=%d", layout_name, deleted)
        return deleted > 0
    except Exception as e:
        db.connection.rollback()
        log.error("Failed to delete dashboard layout: %s", e)
        return False
    finally:
        db.disconnect()
