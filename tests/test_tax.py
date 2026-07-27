# اختبارات النظام الجبائي الجزائري
# =================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.tax import TaxEngine


def test_tax_engine_init():
    """اختبار تهيئة محرك الضرائب"""
    engine = TaxEngine()
    assert engine is not None
    assert engine.get_config_year() == 2025
    print("✅ test_tax_engine_init")
    return True


def test_ibs_calculation_production():
    """اختبار حساب IBS للنشاط الإنتاجي"""
    engine = TaxEngine()
    result = engine.calculate_ibs(10000000, "production")
    assert result["tax_amount"] == 10000000 * 0.19
    assert result["rate_used"] == 0.19
    assert result["minimum_applied"] is False
    print("✅ test_ibs_calculation_production")
    return True


def test_ibs_calculation_construction():
    """اختبار حساب IBS للبناء"""
    engine = TaxEngine()
    result = engine.calculate_ibs(10000000, "construction")
    assert result["tax_amount"] == 10000000 * 0.23
    assert result["rate_used"] == 0.23
    print("✅ test_ibs_calculation_construction")
    return True


def test_ibs_calculation_other():
    """اختبار حساب IBS لأنشطة أخرى"""
    engine = TaxEngine()
    result = engine.calculate_ibs(10000000, "other")
    assert result["tax_amount"] == 10000000 * 0.26
    assert result["rate_used"] == 0.26
    print("✅ test_ibs_calculation_other")
    return True


def test_ibs_minimum_tax():
    """اختبار الحد الأدنى لـ IBS"""
    engine = TaxEngine()
    result = engine.calculate_ibs(10000, "production")
    assert result["tax_amount"] == 10000
    assert result["minimum_applied"] is True
    print("✅ test_ibs_minimum_tax")
    return True


def test_ibs_negative_income():
    """اختبار IBS للدخل السلبي"""
    engine = TaxEngine()
    result = engine.calculate_ibs(-1000000, "production")
    assert result["tax_amount"] == 10000
    assert result["minimum_applied"] is True
    print("✅ test_ibs_negative_income")
    return True


def test_tva_standard_rate():
    """اختبار TVA النسبة العادية"""
    engine = TaxEngine()
    result = engine.calculate_tva(1000000, "standard")
    assert result["tva_amount"] == 190000
    assert result["total_with_tax"] == 1190000
    assert result["rate_used"] == 0.19
    print("✅ test_tva_standard_rate")
    return True


def test_tva_reduced_rate():
    """اختبار TVA النسبة المخفضة"""
    engine = TaxEngine()
    result = engine.calculate_tva(1000000, "reduced")
    assert result["tva_amount"] == 90000
    assert result["total_with_tax"] == 1090000
    assert result["rate_used"] == 0.09
    print("✅ test_tva_reduced_rate")
    return True


def test_tva_zero_rate():
    """اختبار TVA النسبة صفر"""
    engine = TaxEngine()
    result = engine.calculate_tva(1000000, "zero")
    assert result["tva_amount"] == 0
    assert result["total_with_tax"] == 1000000
    assert result["rate_used"] == 0.0
    print("✅ test_tva_zero_rate")
    return True


def test_irg_low_salary():
    """اختبار IRG للراتب المنخفض (معفي)"""
    engine = TaxEngine()
    result = engine.calculate_irg(100000)
    assert result["irg_amount"] == 0
    assert result["effective_rate"] == 0
    print("✅ test_irg_low_salary")
    return True


def test_irg_medium_salary():
    """اختبار IRG للراتب المتوسط"""
    engine = TaxEngine()
    result = engine.calculate_irg(300000)
    assert result["irg_amount"] > 0
    assert result["marginal_rate"] == 0.20
    print("✅ test_irg_medium_salary")
    return True


def test_irg_high_salary():
    """اختبار IRG للراتب العالي"""
    engine = TaxEngine()
    result = engine.calculate_irg(2000000)
    assert result["irg_amount"] > 0
    assert result["marginal_rate"] == 0.35
    print("✅ test_irg_high_salary")
    return True


def test_cnas_calculation():
    """اختبار حساب CNAS"""
    engine = TaxEngine()
    result = engine.calculate_cnas(100000)
    assert result["employer_amount"] > 0
    assert result["employee_amount"] > 0
    assert result["total"] == result["employer_amount"] + result["employee_amount"]
    assert result["gross_salary"] == 100000
    print("✅ test_cnas_calculation")
    return True


def test_cnac_calculation():
    """اختبار حساب CNAC"""
    engine = TaxEngine()
    result = engine.calculate_cnac(100000)
    assert result["employer_amount"] == 1500
    assert result["employee_amount"] == 500
    assert result["total"] == 2000
    print("✅ test_cnac_calculation")
    return True


def test_versement_forfaitaire():
    """اختبار الدفعات المقدمة"""
    engine = TaxEngine()
    result = engine.calculate_versement_forfaitaire(1000000, False)
    assert result["amount"] == 20000
    assert result["rate"] == 0.02
    result2 = engine.calculate_versement_forfaitaire(1000000, True)
    assert result2["amount"] == 10000
    assert result2["rate"] == 0.01
    print("✅ test_versement_forfaitaire")
    return True


def test_payroll_calculation():
    """اختبار حساب الرواتب الشامل"""
    engine = TaxEngine()
    result = engine.calculate_payroll(100000)
    assert result["gross_salary"] == 100000
    assert result["net_salary"] > 0
    assert result["net_salary"] < 100000
    assert result["total_cost_employer"] > 100000
    print("✅ test_payroll_calculation")
    return True


def test_full_simulation():
    """اختبار المحاكاة الشاملة"""
    engine = TaxEngine()
    result = engine.simulate(
        revenue=50000000, cogs=30000000, operating_expenses=10000000,
        total_assets=100000000, total_liabilities=40000000,
        equity=60000000, number_of_employees=50,
        avg_salary=80000, activity_type="production",
        is_construction=False
    )
    assert result["revenue"] == 50000000
    assert result["taxable_income"] == 10000000
    assert result["ibs"]["tax_amount"] == 1900000
    assert result["total_taxes"] > 0
    assert result["tax_burden_pct"] > 0
    print("✅ test_full_simulation")
    return True


def test_obligations():
    """اختبار الالتزامات الجبائية"""
    engine = TaxEngine()
    obligations = engine.get_obligations(3, "other", 5000000, 50000000)
    assert len(obligations) > 0
    types = [o["tax_type"] for o in obligations]
    assert "TVA" in types
    assert "IRG" in types
    assert "CNAS" in types
    assert "CNAC" in types
    assert "VF" in types
    print("✅ test_obligations")
    return True


def test_helpers():
    """اختبار الدوال المساعدة"""
    engine = TaxEngine()
    label = engine.get_ibs_rate_label("production")
    assert label != ""
    items = engine.get_tva_items()
    assert len(items) > 0
    exemptions = engine.get_tva_exemptions()
    assert len(exemptions) > 0
    formatted = engine.format_currency(1234567.89)
    assert "DZD" in formatted
    print("✅ test_helpers")
    return True


if __name__ == "__main__":
    print("🧪 بدء اختبارات النظام الجبائي الجزائري...")
    print("=" * 50)
    
    tests = [
        test_tax_engine_init,
        test_ibs_calculation_production,
        test_ibs_calculation_construction,
        test_ibs_calculation_other,
        test_ibs_minimum_tax,
        test_ibs_negative_income,
        test_tva_standard_rate,
        test_tva_reduced_rate,
        test_tva_zero_rate,
        test_irg_low_salary,
        test_irg_medium_salary,
        test_irg_high_salary,
        test_cnas_calculation,
        test_cnac_calculation,
        test_versement_forfaitaire,
        test_payroll_calculation,
        test_full_simulation,
        test_obligations,
        test_helpers,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"النتائج: {passed} نجح / {failed} فشل / {passed + failed} إجمالي")
    
    if failed == 0:
        print("🎉 كل اختبارات النظام الجبائي نجحت!")
    else:
        print("⚠️ بعض الاختبارات فشلت")
