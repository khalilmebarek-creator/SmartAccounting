# اختبارات قوالب الإقرارات الجبائية والتقارير
# =============================================

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.tax import TaxEngine
from modules.tax_reports import tax_declaration_generator


def _company_header():
    return {
        "company_name": "شركة النور للتجارة",
        "nif": "099916000123456",
        "rc": "16/00-1234567B23",
        "ai": "16000991",
        "address": "الجزائر العاصمة، شارع ديدوش مراد 12",
        "dgi_center": "مديرية الضرائب — الجزائر",
    }


# ==================== TVA 6% ====================

def test_tva_intermediate_rate():
    """اختبار حساب TVA بنسبة 6%"""
    engine = TaxEngine()
    result = engine.calculate_tva(1000000, "intermediate")
    assert result["tva_amount"] == 60000
    assert result["total_with_tax"] == 1060000
    assert result["rate_used"] == 0.06
    print("✅ test_tva_intermediate_rate")
    return True


def test_tva_rates_include_six_percent():
    """اختبار أن نسب TVA تتضمن 6%"""
    engine = TaxEngine()
    rates = engine.get_tva_rates()
    assert rates.get("intermediate") == 0.06
    assert rates.get("standard") == 0.19
    assert rates.get("reduced") == 0.09
    print("✅ test_tva_rates_include_six_percent")
    return True


# ==================== IBS Acomptes ====================

def test_ibs_acomptes_count_and_schedule():
    """اختبار عدد ومواعيد الدفعات المقدمة IBS"""
    engine = TaxEngine()
    result = engine.calculate_ibs_acomptes(10000000, "production")
    acomptes = result["acomptes"]
    assert len(acomptes) == 3
    months = [a["month"] for a in acomptes]
    assert months == [3, 6, 11]
    print("✅ test_ibs_acomptes_count_and_schedule")
    return True


def test_ibs_acomptes_equal_tax_third():
    """اختبار أن كل دفعة = ثلث ضريبة IBS"""
    engine = TaxEngine()
    result = engine.calculate_ibs_acomptes(10000000, "production")
    annual_tax = 10000000 * 0.19
    expected = round(annual_tax / 3, 2)
    assert result["acompte_amount"] == expected
    assert all(a["amount"] == expected for a in result["acomptes"])
    assert abs(result["total_acomptes"] - annual_tax) < 0.05
    print("✅ test_ibs_acomptes_equal_tax_third")
    return True


def test_ibs_acomptes_minimum_tax():
    """اختبار الدفعات المقدمة مع الحد الأدنى للضريبة"""
    engine = TaxEngine()
    result = engine.calculate_ibs_acomptes(10000, "production")
    assert result["annual_tax"] == 10000
    assert result["acompte_amount"] == round(10000 / 3, 2)
    print("✅ test_ibs_acomptes_minimum_tax")
    return True


def test_ibs_balance_due():
    """اختبار تصفية IBS مع رصيد مستحق"""
    engine = TaxEngine()
    tax = 10000000 * 0.19
    paid = tax - 100000
    result = engine.calculate_ibs_balance(10000000, "production", acomptes_paid=paid)
    assert result["tax"] == tax
    assert result["acomptes_paid"] == paid
    assert result["balance_due"] == 100000
    assert result["refund_amount"] == 0
    print("✅ test_ibs_balance_due")
    return True


def test_ibs_balance_refund():
    """اختبار تصفية IBS مع فائض يسترجع"""
    engine = TaxEngine()
    tax = 10000000 * 0.19
    paid = tax + 50000
    result = engine.calculate_ibs_balance(10000000, "production", acomptes_paid=paid)
    assert result["balance_due"] == 0
    assert result["refund_amount"] == 50000
    print("✅ test_ibs_balance_refund")
    return True


# ==================== TVA Refund / Credit ====================

def test_tva_refund_payable_no_credit():
    """اختبار TVA واجبة الدفع بدون رصيد سابق"""
    engine = TaxEngine()
    result = engine.calculate_tva_refund(190000, 100000)
    assert result["net_payable"] == 90000
    assert result["remaining_credit"] == 0
    assert result["status"] == "payable"
    print("✅ test_tva_refund_payable_no_credit")
    return True


def test_tva_refund_credit_carry():
    """اختبار ترحيل رصيد TVA عند زيادة الخصم"""
    engine = TaxEngine()
    result = engine.calculate_tva_refund(100000, 190000)
    assert result["net_payable"] == 0
    assert result["remaining_credit"] == 90000
    assert result["status"] == "credit"
    print("✅ test_tva_refund_credit_carry")
    return True


def test_tva_refund_credit_applied():
    """اختبار تطبيق الرصيد السابق على المبلغ المستحق"""
    engine = TaxEngine()
    result = engine.calculate_tva_refund(190000, 100000, previous_credit=60000)
    assert result["net_payable"] == 30000
    assert result["remaining_credit"] == 0
    print("✅ test_tva_refund_credit_applied")
    return True


def test_tva_refund_credit_partial():
    """اختبار رصيد سابق يفوق المستحق"""
    engine = TaxEngine()
    result = engine.calculate_tva_refund(190000, 100000, previous_credit=150000)
    assert result["net_payable"] == 0
    assert result["remaining_credit"] == 60000
    print("✅ test_tva_refund_credit_partial")
    return True


# ==================== DAS ====================

def test_build_das_data():
    """اختبار بيانات الإقرار السنوي للأجور"""
    engine = TaxEngine()
    result = engine.build_das_data(monthly_payroll=100000, number_of_employees=1)
    assert result["number_of_employees"] == 1
    assert result["annual_payroll"] == 1200000
    assert result["cnas_employer_annual"] > 0
    assert result["cnas_employee_annual"] > 0
    assert result["cnac_employer_annual"] == 1500 * 12
    assert result["irg_withheld_annual"] >= 0
    assert result["net_payroll_annual"] > 0
    print("✅ test_build_das_data")
    return True


# ==================== Declaration Generator ====================

def test_declaration_types_available():
    """اختبار توفر أنواع الإقرارات"""
    types = tax_declaration_generator.get_declaration_types()
    assert "g50" in types
    assert "g57" in types
    assert "das" in types
    print("✅ test_declaration_types_available")
    return True


def test_generate_g50_structure():
    """اختبار بنية إقرار G50"""
    decl = tax_declaration_generator.generate("g50", {
        "header": _company_header(),
        "month": 3,
        "year": 2025,
        "monthly_turnover": 10000000,
        "tva_collected": 1900000,
        "tva_deductible": 1200000,
    })
    assert decl["type"] == "g50"
    assert decl["header"]["company_name"] == "شركة النور للتجارة"
    assert decl["period"]["month"] == 3
    assert decl["period"]["year"] == 2025
    assert decl["turnover"] == 10000000
    assert decl["net_tva"]["net_payable"] == 700000
    print("✅ test_generate_g50_structure")
    return True


def test_generate_g57_structure():
    """اختبار بنية إقرار G57"""
    decl = tax_declaration_generator.generate("g57", {
        "header": _company_header(),
        "taxable_income": 10000000,
        "acomptes_paid": 1000000,
        "activity_type": "production",
    })
    assert decl["type"] == "g57"
    assert decl["ibs"]["tax_amount"] == 1900000
    assert len(decl["acomptes"]["acomptes"]) == 3
    assert decl["balance"]["balance_due"] == 900000
    print("✅ test_generate_g57_structure")
    return True


def test_generate_das_structure():
    """اختبار بنية إقرار DAS"""
    decl = tax_declaration_generator.generate("das", {
        "header": _company_header(),
        "monthly_payroll": 100000,
        "number_of_employees": 1,
    })
    assert decl["type"] == "das"
    assert decl["data"]["annual_payroll"] == 1200000
    assert decl["data"]["number_of_employees"] == 1
    print("✅ test_generate_das_structure")
    return True


def test_generate_invalid_type_raises():
    """اختبار رفض نوع إقرار غير معروف"""
    try:
        tax_declaration_generator.generate("xyz", {"header": _company_header()})
        assert False, "Expected ValueError"
    except ValueError:
        pass
    print("✅ test_generate_invalid_type_raises")
    return True


def test_render_text_g50():
    """اختبار عرض نص إقرار G50"""
    decl = tax_declaration_generator.generate("g50", {
        "header": _company_header(),
        "month": 3,
        "year": 2025,
        "monthly_turnover": 10000000,
        "tva_collected": 1900000,
        "tva_deductible": 1200000,
    })
    text = tax_declaration_generator.render_text(decl)
    assert "شركة النور للتجارة" in text
    assert "G N°50" in text
    assert "700,000.00" in text
    print("✅ test_render_text_g50")
    return True


def test_render_text_contains_header():
    """اختبار أن نص الإقرار يحتوي بيانات الشركة"""
    decl = tax_declaration_generator.generate("g57", {
        "header": _company_header(),
        "taxable_income": 10000000,
        "acomptes_paid": 1000000,
        "activity_type": "production",
    })
    text = tax_declaration_generator.render_text(decl)
    assert "099916000123456" in text
    assert "G N°57" in text
    print("✅ test_render_text_contains_header")
    return True


def test_export_excel_g50():
    """اختبار تصدير إقرار G50 إلى Excel"""
    decl = tax_declaration_generator.generate("g50", {
        "header": _company_header(),
        "month": 3,
        "year": 2025,
        "monthly_turnover": 10000000,
        "tva_collected": 1900000,
        "tva_deductible": 1200000,
    })
    path = os.path.join(tempfile.gettempdir(), "test_g50_decl.xlsx")
    if os.path.exists(path):
        os.remove(path)
    result = tax_declaration_generator.export_excel(decl, path)
    assert result is True
    assert os.path.exists(path)
    os.remove(path)
    print("✅ test_export_excel_g50")
    return True


def test_export_excel_das():
    """اختبار تصدير إقرار DAS إلى Excel"""
    decl = tax_declaration_generator.generate("das", {
        "header": _company_header(),
        "monthly_payroll": 100000,
        "number_of_employees": 1,
    })
    path = os.path.join(tempfile.gettempdir(), "test_das_decl.xlsx")
    if os.path.exists(path):
        os.remove(path)
    result = tax_declaration_generator.export_excel(decl, path)
    assert result is True
    assert os.path.exists(path)
    os.remove(path)
    print("✅ test_export_excel_das")
    return True


def test_export_pdf_g57():
    """اختبار تصدير إقرار G57 إلى PDF"""
    decl = tax_declaration_generator.generate("g57", {
        "header": _company_header(),
        "taxable_income": 10000000,
        "acomptes_paid": 1000000,
        "activity_type": "production",
    })
    path = os.path.join(tempfile.gettempdir(), "test_g57_decl.pdf")
    if os.path.exists(path):
        os.remove(path)
    result = tax_declaration_generator.export_pdf(decl, path)
    assert result is True
    assert os.path.exists(path)
    os.remove(path)
    print("✅ test_export_pdf_g57")
    return True


if __name__ == "__main__":
    print("🧪 بدء اختبارات قوالب الإقرارات الجبائية...")
    print("=" * 50)

    tests = [
        test_tva_intermediate_rate,
        test_tva_rates_include_six_percent,
        test_ibs_acomptes_count_and_schedule,
        test_ibs_acomptes_equal_tax_third,
        test_ibs_acomptes_minimum_tax,
        test_ibs_balance_due,
        test_ibs_balance_refund,
        test_tva_refund_payable_no_credit,
        test_tva_refund_credit_carry,
        test_tva_refund_credit_applied,
        test_tva_refund_credit_partial,
        test_build_das_data,
        test_declaration_types_available,
        test_generate_g50_structure,
        test_generate_g57_structure,
        test_generate_das_structure,
        test_generate_invalid_type_raises,
        test_render_text_g50,
        test_render_text_contains_header,
        test_export_excel_g50,
        test_export_excel_das,
        test_export_pdf_g57,
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
        print("🎉 كل اختبارات الإقرارات الجبائية نجحت!")
    else:
        print("⚠️ بعض الاختبارات فشلت")
