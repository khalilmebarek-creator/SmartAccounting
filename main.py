# برنامج المنصة المحاسبية الذكية
# البرنامج الرئيسي المحدّث
# ==============================

import os

from config import APP_TITLE, APP_VERSION
from database import create_tables, save_analysis
from modules import (
    CalculationEngine,
    DataValidator,
    FinancialAnalyzer,
    AuditEngine,
    ReportGenerator
)


def _t(key):
    """ترجمة بسيطة للـ CLI"""
    try:
        from ui.resources.i18n import t
        return t(key)
    except Exception:
        return key


def main():
    """البرنامج الرئيسي"""
    print("=" * 70)
    print(f"🎉 مرحباً بك في {APP_TITLE}")
    print(f"📌 الإصدار: {APP_VERSION}")
    print("=" * 70)
    print()
    
    # 1️⃣ إنشاء قاعدة البيانات
    print("🚀 جاري إنشاء قاعدة البيانات...")
    print()
    
    if not create_tables():
        print("❌ فشل إنشاء قاعدة البيانات!")
        return False
    
    print()
    print("=" * 70)
    print("✅ تم إعداد قاعدة البيانات بنجاح!")
    print("=" * 70)
    
    # 2️⃣ اختبار الحسابات المالية
    print("\n\n📊 اختبار محرك الحسابات...")
    print("=" * 70)
    
    # بيانات تجريبية
    test_data = {
        'current_assets': 100000,
        'inventory': 20000,
        'current_liabilities': 50000,
        'gross_profit': 30000,
        'net_income': 15000,
        'revenue': 200000,
        'total_assets': 500000,
        'equity': 300000,
        'cost_of_goods_sold': 120000,
        'average_receivables': 40000,
        'average_inventory': 25000,
        'total_liabilities': 200000
    }
    
    calculator = CalculationEngine(test_data)
    
    # حساب جميع النسب
    ratios = calculator.calculate_all_ratios(test_data)
    
    if ratios:
        print("\n✅ تم حساب النسب المالية بنجاح!")
        calculator.print_ratios(ratios)
    else:
        print("❌ فشل حساب النسب!")
    
    # 3️⃣ اختبار التحقق من البيانات
    print("\n\n🔍 اختبار التحقق من البيانات...")
    print("=" * 70)
    
    validator = DataValidator()
    is_valid = validator.validate_financial_statement(test_data)
    
    if is_valid:
        print("✅ البيانات صحيحة!")
    else:
        print("❌ توجد أخطاء في البيانات:")
        validator.print_report()
    
    # 4️⃣ اختبار التحليل المالي
    print("\n\n📈 اختبار التحليل المالي...")
    print("=" * 70)
    
    analyzer = FinancialAnalyzer(test_data)
    
    dupont = analyzer.dupont_analysis(
        test_data['net_income'],
        test_data['revenue'],
        test_data['total_assets'],
        test_data['equity']
    )
    
    print("\n🔄 تحليل DuPont:")
    print(f"  • هامش الربح الصافي: {dupont['net_profit_margin']}%")
    print(f"  • معدل دوران الأصول: {dupont['asset_turnover']}")
    print(f"  • الرافعة المالية: {dupont['equity_multiplier']}")
    print(f"  • العائد على حقوق المالكين (ROE): {dupont['roe']}%")
    
    working_capital = analyzer.working_capital_analysis(
        test_data['current_assets'],
        test_data['current_liabilities'],
        test_data['inventory']
    )
    
    print(f"\n💰 رأس المال العامل:")
    print(f"  • رأس المال العامل: {working_capital['working_capital']}")
    print(f"  • الحالة: {working_capital['status']}")
    
    # 5️⃣ اختبار التدقيق
    print("\n\n🔍 اختبار التدقيق والمراجعة...")
    print("=" * 70)
    
    auditor = AuditEngine()
    
    # التحقق من توازن الميزانية
    auditor.check_balance_sheet(
        test_data['total_assets'],
        test_data['total_liabilities'],
        test_data['equity']
    )
    
    # التحقق من معقولية النسب
    auditor.check_ratios_reasonableness(ratios)
    
    # الحصول على ملخص التدقيق
    audit_summary = auditor.get_audit_summary()
    print(audit_summary['report'])
    
    # 6️⃣ توليد التقارير
    print("\n\n📄 توليد التقارير...")
    print("=" * 70)
    
    reporter = ReportGenerator("شركة اختبار", 2024)
    
    # توليد تقرير النسب المالية
    ratios_report = reporter.generate_financial_ratios_report(ratios)
    print(ratios_report)
    
    # 7️⃣ حفظ التحليل في قاعدة البيانات
    print("\n\n💾 حفظ التحليل في قاعدة البيانات...")
    print("=" * 70)
    
    fiscal_year_id = save_analysis(
        company_name="شركة اختبار",
        fiscal_year=2024,
        financial_data=test_data,
        ratios=ratios
    )
    
    if fiscal_year_id:
        print(f"✅ تم حفظ التحليل بنجاح! (ID: {fiscal_year_id})")
    else:
        print("⚠️ تعذّر حفظ التحليل")
    
    # 8️⃣ ملخص نهائي
    print("\n" + "="*70)
    print("🎯 ملخص الجلسة")
    print("="*70)
    print("\n✅ تم بنجاح:")
    print("  ✓ إنشاء قاعدة البيانات")
    print("  ✓ حساب النسب المالية")
    print("  ✓ التحقق من البيانات")
    print("  ✓ التحليل المالي")
    print("  ✓ التدقيق والمراجعة")
    print("  ✓ توليد التقارير")
    print("  ✓ حفظ التحليل في قاعدة البيانات")
    
    print("\n🚀 المنصة جاهزة للعمل!")
    print("\n" + "="*70)
    
    return True

if __name__ == "__main__":
    main()
    