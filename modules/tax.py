# محرك الضرائب — النظام الجبائي الجزائري
# ==========================================

import json
import os
from datetime import datetime, date


class TaxEngine:
    """محرك حساب الضرائب — يدعم النظام الجبائي الجزائري"""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "tax_config.json"
            )
        self.config = self._load_config(config_path)
        self._cache = {}

    def _load_config(self, path):
        """تحميل ملف الإعدادات"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._default_config()

    def _default_config(self):
        """الإعدادات الافتراضية"""
        return {
            "country": "Algeria",
            "year": 2025,
            "ibs": {"rates": {"production": 0.19, "construction": 0.23, "other": 0.26}, "minimum_tax": 10000},
            "tva": {"rates": {"standard": 0.19, "reduced": 0.09, "intermediate": 0.06, "zero": 0.0}},
            "irg": {"brackets": [
                {"min": 0, "max": 120000, "rate": 0.0},
                {"min": 120001, "max": 360000, "rate": 0.20},
                {"min": 360001, "max": 1440000, "rate": 0.30},
                {"min": 1440001, "max": None, "rate": 0.35}
            ]},
            "cnas": {"employer": {"total": 0.245}, "employee": {"total": 0.09}},
            "cnac": {"employer_rate": 0.015, "employee_rate": 0.005},
            "versement_forfaitaire": {"standard_rate": 0.02, "construction_rate": 0.01}
        }

    def reload_config(self, config_path=None):
        """إعادة تحميل الإعدادات (للتحديث السنوي)"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "tax_config.json"
            )
        self.config = self._load_config(config_path)
        self._cache.clear()

    def get_config_year(self):
        """الحصول على سنة الإعدادات"""
        return self.config.get("year", 2025)

    def get_activity_types(self):
        """قائمة أنواع النشاط"""
        return self.config.get("activity_types", [])

    # ==================== IBS ====================

    def calculate_ibs(self, taxable_income, activity_type="other"):
        """
        حساب ضريبة أرباح الشركات (IBS)
        
        Args:
            taxable_income: صافي الدخل الخاضع للضريبة
            activity_type: نوع النشاط (production, construction, other)
        
        Returns:
            dict: {tax_amount, effective_rate, tax_before_minimum, minimum_applied}
        """
        ibs_config = self.config.get("ibs", {})
        rates = ibs_config.get("rates", {})
        minimum = ibs_config.get("minimum_tax", 10000)

        rate = rates.get(activity_type, rates.get("other", 0.26))

        if taxable_income <= 0:
            return {
                "tax_amount": minimum,
                "effective_rate": 0,
                "tax_before_minimum": 0,
                "minimum_applied": True,
                "rate_used": rate,
                "activity_type": activity_type,
                "taxable_income": taxable_income
            }

        tax_before_minimum = taxable_income * rate
        minimum_applied = tax_before_minimum < minimum
        tax_amount = max(tax_before_minimum, minimum)

        return {
            "tax_amount": round(tax_amount, 2),
            "effective_rate": round((tax_amount / taxable_income * 100), 2) if taxable_income > 0 else 0,
            "tax_before_minimum": round(tax_before_minimum, 2),
            "minimum_applied": minimum_applied,
            "rate_used": rate,
            "activity_type": activity_type,
            "taxable_income": taxable_income
        }

    def calculate_ibs_acomptes(self, taxable_income, activity_type="other"):
        """
        حساب الدفعات المقدمة IBS (3 دفعات سنوية)
        
        Args:
            taxable_income: صافي الدخل الخاضع للضريبة
            activity_type: نوع النشاط (production, construction, other)
        
        Returns:
            dict: {annual_tax, acompte_amount, acomptes, total_acomptes}
        """
        ibs = self.calculate_ibs(taxable_income, activity_type)
        annual_tax = ibs["tax_amount"]
        acompte_amount = round(annual_tax / 3, 2)

        schedule = self.config.get("ibs", {}).get("acomptes", [])
        acomptes = []
        for item in schedule:
            acomptes.append({
                "month": item.get("month"),
                "day": item.get("day", 20),
                "amount": acompte_amount,
                "label": item.get("label", "دفعة مقدمة"),
                "label_en": item.get("label_en", "instalment")
            })

        return {
            "annual_tax": round(annual_tax, 2),
            "acompte_amount": acompte_amount,
            "acomptes": acomptes,
            "total_acomptes": round(sum(a["amount"] for a in acomptes), 2)
        }

    def calculate_ibs_balance(self, taxable_income, activity_type="other", acomptes_paid=0):
        """
        حساب تصفية IBS السنوية (الباقي بعد الدفعات المقدمة)
        
        Args:
            taxable_income: صافي الدخل الخاضع للضريبة
            activity_type: نوع النشاط
            acomptes_paid: إجمالي الدفعات المقدمة المدفوعة
        
        Returns:
            dict: {tax, acomptes_paid, balance_due, refund_amount, rate_used}
        """
        ibs = self.calculate_ibs(taxable_income, activity_type)
        tax = ibs["tax_amount"]
        balance = tax - acomptes_paid

        return {
            "tax": round(tax, 2),
            "acomptes_paid": round(acomptes_paid, 2),
            "balance_due": round(max(0, balance), 2),
            "refund_amount": round(max(0, -balance), 2),
            "rate_used": ibs["rate_used"]
        }

    # ==================== TVA ====================

    def get_tva_rates(self):
        """الحصول على جدول نسب TVA"""
        return self.config.get("tva", {}).get("rates", {})

    def calculate_tva(self, amount_excl_tax, rate_type="standard"):
        """
        حساب ضريبة القيمة المضافة (TVA)
        
        Args:
            amount_excl_tax: المبلغ قبل الضريبة
            rate_type: نوع النسبة (standard, reduced, zero)
        
        Returns:
            dict: {tva_amount, total_with_tax, rate_used, amount_excl_tax}
        """
        tva_config = self.config.get("tva", {})
        rates = tva_config.get("rates", {})

        rate = rates.get(rate_type, rates.get("standard", 0.19))

        tva_amount = amount_excl_tax * rate
        total_with_tax = amount_excl_tax + tva_amount

        return {
            "tva_amount": round(tva_amount, 2),
            "total_with_tax": round(total_with_tax, 2),
            "rate_used": rate,
            "rate_type": rate_type,
            "amount_excl_tax": amount_excl_tax
        }

    def calculate_tva_collection(self, tva_collected, tva_paid):
        """
        حساب صافي TVA (الم collecting - المدفوع)
        
        Args:
            tva_collected: TVA المحصلة من المبيعات
            tva_paid: TVA المدفوعة للموردين
        
        Returns:
            dict: {net_tva, status, amount}
        """
        net = tva_collected - tva_paid
        return {
            "net_tva": round(net, 2),
            "tva_collected": round(tva_collected, 2),
            "tva_paid": round(tva_paid, 2),
            "status": "to_pay" if net > 0 else "to_receive",
            "amount": round(abs(net), 2)
        }

    def calculate_tva_refund(self, tva_collected, tva_paid, previous_credit=0):
        """
        حساب رصيد TVA الشهري: دفع أو ترحيل/استرجاع (G N°50)
        
        Args:
            tva_collected: TVA المحصلة من المبيعات
            tva_paid: TVA القابلة للخصم (المدفوعة للموردين)
            previous_credit: رصيد TVA المرحّل من الشهر السابق
        
        Returns:
            dict: {gross_difference, previous_credit, net_payable,
                   remaining_credit, status}
        """
        gross = tva_collected - tva_paid

        if gross > 0:
            net_payable = max(0, gross - previous_credit)
            remaining_credit = max(0, previous_credit - gross)
            status = "payable"
        else:
            net_payable = 0
            remaining_credit = previous_credit + abs(gross)
            status = "credit"

        return {
            "tva_collected": round(tva_collected, 2),
            "tva_paid": round(tva_paid, 2),
            "gross_difference": round(gross, 2),
            "previous_credit": round(previous_credit, 2),
            "net_payable": round(net_payable, 2),
            "remaining_credit": round(remaining_credit, 2),
            "status": status
        }

    # ==================== IRG ====================

    def calculate_irg(self, annual_taxable_salary):
        """
        حساب ضريبة الدخل على الرواتب (IRG)
        
        Args:
            annual_taxable_salary: الراتب السنوي الخاضع للضريبة
        
        Returns:
            dict: {irg_amount, effective_rate, marginal_rate, net_salary}
        """
        irg_config = self.config.get("irg", {})
        brackets = irg_config.get("brackets", [])

        if annual_taxable_salary <= 0:
            return {
                "irg_amount": 0,
                "effective_rate": 0,
                "marginal_rate": 0,
                "monthly_irg": 0,
                "annual_taxable": 0,
                "net_annual": 0,
                "net_monthly": 0
            }

        total_irg = 0
        marginal_rate = 0

        for bracket in brackets:
            b_min = bracket.get("min", 0)
            b_max = bracket.get("max")
            b_rate = bracket.get("rate", 0)

            if annual_taxable_salary < b_min:
                break

            taxable_in_bracket = (b_max if b_max else annual_taxable_salary) - b_min + 1
            taxable_in_bracket = min(taxable_in_bracket, annual_taxable_salary - b_min + 1)

            if taxable_in_bracket > 0:
                total_irg += taxable_in_bracket * b_rate
                marginal_rate = b_rate

        total_irg = max(0, total_irg)
        effective_rate = (total_irg / annual_taxable_salary * 100) if annual_taxable_salary > 0 else 0

        return {
            "irg_amount": round(total_irg, 2),
            "effective_rate": round(effective_rate, 2),
            "marginal_rate": marginal_rate,
            "monthly_irg": round(total_irg / 12, 2),
            "annual_taxable": annual_taxable_salary,
            "net_annual": round(annual_taxable_salary - total_irg, 2),
            "net_monthly": round((annual_taxable_salary - total_irg) / 12, 2)
        }

    # ==================== CNAS ====================

    def calculate_cnas(self, gross_salary):
        """
        حساب اشتراكات الصندوق الوطني للتأمينات الاجتماعية (CNAS)
        
        Args:
            gross_salary: الراتب الإجمالي
        
        Returns:
            dict: {employer_amount, employee_amount, total, details}
        """
        cnas_config = self.config.get("cnas", {})
        employer_config = cnas_config.get("employer", {})
        employee_config = cnas_config.get("employee", {})

        employer_amount = gross_salary * employer_config.get("total", 0.245)
        employee_amount = gross_salary * employee_config.get("total", 0.09)

        return {
            "employer_amount": round(employer_amount, 2),
            "employee_amount": round(employee_amount, 2),
            "total": round(employer_amount + employee_amount, 2),
            "employer_rate": employer_config.get("total", 0.245),
            "employee_rate": employee_config.get("total", 0.09),
            "gross_salary": gross_salary,
            "net_salary_before_irg": round(gross_salary - employee_amount, 2),
            "details": {
                "employer": {
                    "assurance_sociale": round(gross_salary * employer_config.get("assurance_sociale", 0.125), 2),
                    "accidents_travail": round(gross_salary * employer_config.get("accidents_travail", 0.0125), 2),
                    "retraite": round(gross_salary * employer_config.get("retraite", 0.105), 2),
                    "retraite_anticipee": round(gross_salary * employer_config.get("retraite_anticipee", 0.0025), 2)
                },
                "employee": {
                    "assurance_sociale": round(gross_salary * employee_config.get("assurance_sociale", 0.015), 2),
                    "retraite": round(gross_salary * employee_config.get("retraite", 0.0675), 2),
                    "chomage": round(gross_salary * employee_config.get("chomage", 0.0075), 2)
                }
            }
        }

    # ==================== CNAC ====================

    def calculate_cnac(self, gross_salary):
        """
        حساب اشتراكات تأمين البطالة (CNAC)
        
        Args:
            gross_salary: الراتب الإجمالي
        
        Returns:
            dict: {employer_amount, employee_amount, total}
        """
        cnac_config = self.config.get("cnac", {})
        employer_amount = gross_salary * cnac_config.get("employer_rate", 0.015)
        employee_amount = gross_salary * cnac_config.get("employee_rate", 0.005)

        return {
            "employer_amount": round(employer_amount, 2),
            "employee_amount": round(employee_amount, 2),
            "total": round(employer_amount + employee_amount, 2),
            "employer_rate": cnac_config.get("employer_rate", 0.015),
            "employee_rate": cnac_config.get("employee_rate", 0.005),
            "gross_salary": gross_salary
        }

    # ==================== VERSEMENT FORFAITAIRE ====================

    def calculate_versement_forfaitaire(self, monthly_payroll, is_construction=False):
        """
        حساب الدفعات المقدمة (Versement Forfaitaire)
        
        Args:
            monthly_payroll: كتلة الرواتب الشهرية
            is_construction: هل النشاط بناء؟
        
        Returns:
            dict: {amount, rate, monthly_payroll}
        """
        vf_config = self.config.get("versement_forfaitaire", {})
        rate = vf_config.get("construction_rate", 0.01) if is_construction else vf_config.get("standard_rate", 0.02)

        return {
            "amount": round(monthly_payroll * rate, 2),
            "rate": rate,
            "monthly_payroll": monthly_payroll,
            "is_construction": is_construction
        }

    # ==================== PAYROLL SUMMARY ====================

    def calculate_payroll(self, gross_salary, is_construction=False):
        """
        حساب كشوف الرواتب الشامل
        
        Args:
            gross_salary: الراتب الإجمالي
            is_construction: هل النشاط بناء؟
        
        Returns:
            dict: ملخص شامل للرواتب
        """
        cnas = self.calculate_cnas(gross_salary)
        cnac = self.calculate_cnac(gross_salary)
        vf = self.calculate_versement_forfaitaire(gross_salary, is_construction)

        total_deductions_employee = cnas["employee_amount"] + cnac["employee_amount"]
        net_before_irg = gross_salary - total_deductions_employee
        annual_net_before_irg = net_before_irg * 12

        irg = self.calculate_irg(annual_net_before_irg)

        total_deductions = total_deductions_employee + irg["monthly_irg"]
        net_salary = gross_salary - total_deductions

        total_cost_employer = gross_salary + cnas["employer_amount"] + cnac["employer_amount"] + vf["amount"]

        return {
            "gross_salary": gross_salary,
            "cnas": cnas,
            "cnac": cnac,
            "irg": irg,
            "vf": vf,
            "total_deductions_employee": round(total_deductions_employee, 2),
            "total_deductions": round(total_deductions, 2),
            "net_salary": round(net_salary, 2),
            "net_annual": round(net_salary * 12, 2),
            "total_cost_employer": round(total_cost_employer, 2),
            "monthly_cost_employer": round(total_cost_employer, 2)
        }

    # ==================== DAS (الإقرار السنوي للأجور) ====================

    def build_das_data(self, monthly_payroll=0, number_of_employees=0, avg_salary=0):
        """
        بناء بيانات الإقرار السنوي للأجور (DAS)
        
        Args:
            monthly_payroll: كتلة الأجور الشهرية
            number_of_employees: عدد الموظفين
            avg_salary: متوسط الراتب الشهري (اختياري)
        
        Returns:
            dict: تفاصيل الإقرار السنوي للأجور
        """
        annual_payroll = monthly_payroll * 12

        if avg_salary <= 0 and number_of_employees > 0:
            avg_salary = (monthly_payroll / number_of_employees) if monthly_payroll > 0 else 0

        if avg_salary > 0:
            cnas = self.calculate_cnas(avg_salary)
            cnac = self.calculate_cnac(avg_salary)
            irg = self.calculate_irg(
                (avg_salary - cnas["employee_amount"] - cnac["employee_amount"]) * 12
            )
            cnas_emp_annual = cnas["employee_amount"] * 12
            cnac_emp_annual = cnac["employee_amount"] * 12
            irg_annual = irg["irg_amount"]
        else:
            cnas_emp_annual = 0
            cnac_emp_annual = 0
            irg_annual = 0

        net_payroll = annual_payroll - cnas_emp_annual - cnac_emp_annual - irg_annual

        return {
            "number_of_employees": int(number_of_employees),
            "monthly_payroll": round(monthly_payroll, 2),
            "annual_payroll": round(annual_payroll, 2),
            "cnas_employer_annual": round(cnas["employer_amount"] * 12, 2) if avg_salary > 0 else 0,
            "cnas_employee_annual": round(cnas_emp_annual, 2),
            "cnac_employer_annual": round(cnac["employer_amount"] * 12, 2) if avg_salary > 0 else 0,
            "cnac_employee_annual": round(cnac_emp_annual, 2),
            "irg_withheld_annual": round(irg_annual, 2),
            "net_payroll_annual": round(net_payroll, 2)
        }

    # ==================== TAX OBLIGATIONS ====================

    def get_obligations(self, month=None, activity_type="other", monthly_payroll=0, annual_turnover=0):
        """
        الحصول على الالتزامات الجبائية لشهر محدد
        
        Args:
            month: الشهر (1-12)
            activity_type: نوع النشاط
            monthly_payroll: كتلة الرواتب الشهرية
            annual_turnover: الدوران السنوي
        
        Returns:
            list: قائمة الالتزامات
        """
        if month is None:
            month = datetime.now().month

        obligations = []
        cal = self.config.get("tax_calendar", {})
        monthly = cal.get("monthly", [])

        for item in monthly:
            taxes = item.get("taxes", [])

            for tax in taxes:
                obligation = {
                    "tax_type": tax,
                    "due_day": item.get("day", 20),
                    "month": month,
                    "status": "pending",
                    "amount": 0
                }

                if tax == "TVA" and annual_turnover > 0:
                    monthly_tva = annual_turnover / 12 * self.config.get("tva", {}).get("rates", {}).get("standard", 0.19)
                    obligation["amount"] = round(monthly_tva, 2)
                elif tax == "IRG" and monthly_payroll > 0:
                    cnas_result = self.calculate_cnas(monthly_payroll)
                    net_before_irg = monthly_payroll - cnas_result["employee_amount"]
                    irg_result = self.calculate_irg(net_before_irg * 12)
                    obligation["amount"] = irg_result["monthly_irg"]
                elif tax == "CNAS" and monthly_payroll > 0:
                    cnas_result = self.calculate_cnas(monthly_payroll)
                    obligation["amount"] = cnas_result["total"]
                elif tax == "CNAC" and monthly_payroll > 0:
                    cnac_result = self.calculate_cnac(monthly_payroll)
                    obligation["amount"] = cnac_result["total"]
                elif tax == "VF" and monthly_payroll > 0:
                    is_construction = activity_type == "construction"
                    vf_result = self.calculate_versement_forfaitaire(monthly_payroll, is_construction)
                    obligation["amount"] = vf_result["amount"]

                obligations.append(obligation)

        return obligations

    # ==================== FULL SIMULATION ====================

    def simulate(self, revenue, cogs, operating_expenses, total_assets,
                 total_liabilities, equity, number_of_employees=0,
                 avg_salary=0, activity_type="other", is_construction=False):
        """
        محاكاة شاملة لجميع الضرائب
        
        Args:
            revenue: الإيرادات
            cogs: تكلفة البضاعة المباعة
            operating_expenses: المصاريف التشغيلية
            total_assets: إجمالي الأصول
            total_liabilities: إجمالي الالتزامات
            equity: حقوق الملكية
            number_of_employees: عدد الموظفين
            avg_salary: متوسط الراتب
            activity_type: نوع النشاط
            is_construction: هل نشاط بناء
        
        Returns:
            dict: ملخص شامل لجميع الضرائب
        """
        gross_profit = revenue - cogs
        operating_income = gross_profit - operating_expenses
        taxable_income = max(0, operating_income)

        ibs = self.calculate_ibs(taxable_income, activity_type)

        monthly_payroll = number_of_employees * avg_salary if number_of_employees > 0 else 0
        annual_payroll = monthly_payroll * 12

        cnas_total = 0
        cnac_total = 0
        irg_total = 0
        vf_total = 0
        employee_details = []

        if number_of_employees > 0 and avg_salary > 0:
            cnas = self.calculate_cnas(avg_salary)
            cnac = self.calculate_cnac(avg_salary)
            irg_annual = self.calculate_irg(
                (avg_salary - cnas["employee_amount"] - cnac["employee_amount"]) * 12
            )
            vf = self.calculate_versement_forfaitaire(monthly_payroll, is_construction)

            cnas_total = cnas["total"] * 12 * number_of_employees
            cnac_total = cnac["total"] * 12 * number_of_employees
            irg_total = irg_annual["irg_amount"] * number_of_employees
            vf_total = vf["amount"] * 12

            employee_details = {
                "count": number_of_employees,
                "avg_salary": avg_salary,
                "cnas_per_employee": cnas,
                "cnac_per_employee": cnac,
                "irg_per_employee": irg_annual,
                "net_salary_per_employee": irg_annual.get("net_monthly", 0)
            }

        total_taxes = ibs["tax_amount"] + cnas_total + cnac_total + irg_total + vf_total
        tax_burden = (total_taxes / revenue * 100) if revenue > 0 else 0

        return {
            "revenue": revenue,
            "gross_profit": gross_profit,
            "operating_income": operating_income,
            "taxable_income": taxable_income,
            "ibs": ibs,
            "cnas_annual": round(cnas_total, 2),
            "cnac_annual": round(cnac_total, 2),
            "irg_annual": round(irg_total, 2),
            "vf_annual": round(vf_total, 2),
            "total_taxes": round(total_taxes, 2),
            "tax_burden_pct": round(tax_burden, 2),
            "net_income_after_taxes": round(taxable_income - total_taxes, 2),
            "employees": employee_details,
            "activity_type": activity_type,
            "config_year": self.get_config_year()
        }

    # ==================== HELPERS ====================

    def get_ibs_rate_label(self, activity_type):
        """الحصول على وصف نسبة IBS"""
        types = self.config.get("activity_types", [])
        for t in types:
            if t["key"] == activity_type:
                return t.get("label_ar", activity_type)
        return activity_type

    def get_tva_items(self):
        """الحصول على قائمة المنتجات الخاضعة لنسبة TVA المخفضة"""
        return self.config.get("tva", {}).get("reduced_rate_items", [])

    def get_tva_exemptions(self):
        """الحصول على قائمة المنتجات المعفاة من TVA"""
        return self.config.get("tva", {}).get("exemptions", [])

    def format_currency(self, amount):
        """تنسيق المبلغ بالدينار الجزائري"""
        return f"{amount:,.2f} DZD"
