# التدقيق والمراجعة
# =================

class AuditEngine:
    """فئة للتدقيق والمراجعة المحاسبية"""
    
    def __init__(self):
        """تهيئة محرك التدقيق"""
        self.issues = []
        self.warnings = []
        self.notes = []
    
    def check_balance_sheet(self, assets, liabilities, equity):
        """
        التحقق من توازن الميزانية
        الأصول = الالتزامات + حقوق المالكين
        """
        difference = abs(assets - (liabilities + equity))
        
        if difference > 0.01:
            self.issues.append({
                'type': 'خطأ حرج',
                'description': 'عدم توازن الميزانية',
                'difference': round(difference, 2),
                'severity': 'حرج'
            })
            return False
        
        self.notes.append("✅ الميزانية متوازنة")
        return True
    
    def check_income_statement(self, revenue, cogs, operating_expenses, net_income):
        """
        التحقق من صحة قائمة الدخل
        الإيرادات - تكلفة البضاعة - المصاريف = الربح
        """
        calculated_income = revenue - cogs - operating_expenses
        difference = abs(calculated_income - net_income)
        
        if difference > 0.01:
            self.issues.append({
                'type': 'خطأ في الحسابات',
                'description': f'عدم تطابق صافي الربح: المحسوب {calculated_income} ≠ المسجل {net_income}',
                'difference': round(difference, 2),
                'severity': 'حرج'
            })
            return False
        
        self.notes.append("✅ قائمة الدخل صحيحة")
        return True
    
    def check_negative_values(self, financial_data):
        """
        التحقق من وجود قيم سالبة غير متوقعة
        """
        negative_fields = ['revenue', 'total_assets', 'equity']
        found_any = False
        
        for field in negative_fields:
            if field in financial_data and financial_data[field] < 0:
                self.issues.append({
                    'type': 'قيمة غير منطقية',
                    'description': f'{field} لا يمكن أن تكون سالبة: {financial_data[field]}',
                    'field': field,
                    'severity': 'حرج'
                })
                found_any = True
        
        return not found_any
    
    def check_ratios_reasonableness(self, ratios):
        """
        التحقق من معقولية النسب المالية
        """
        # التحقق من نسبة السيولة الحالية (يجب تكون بين 1 و 3)
        if 'current_ratio' in ratios:
            cr = ratios['current_ratio']
            if cr < 0.5:
                self.warnings.append({
                    'type': 'تحذير',
                    'description': 'نسبة السيولة الحالية منخفضة جداً',
                    'value': cr,
                    'recommended': '> 1.0'
                })
            elif cr > 5:
                self.warnings.append({
                    'type': 'تحذير',
                    'description': 'نسبة السيولة الحالية عالية جداً',
                    'value': cr,
                    'note': 'قد يشير إلى استثمارات منخفضة'
                })
        
        # التحقق من نسبة الدين إلى حقوق المالكين
        if 'debt_to_equity' in ratios:
            dte = ratios['debt_to_equity']
            if dte > 2:
                self.warnings.append({
                    'type': 'تحذير',
                    'description': 'نسبة الدين إلى حقوق المالكين عالية',
                    'value': dte,
                    'note': 'مخاطرة مالية عالية'
                })
        
        # التحقق من هامش الربح الصافي
        if 'net_profit_margin' in ratios:
            npm = ratios['net_profit_margin']
            if npm < 0:
                # ✅ الشركة الخاسرة ده تحذير، مش issue (البيانات صحيحة، بس الشركة خاسرة)
                self.warnings.append({
                    'type': 'تحذير',
                    'description': f'الشركة تحقق خسائر: {npm}%',
                    'value': npm,
                    'note': 'وضع يحتاج انتباه الإدارة'
                })
        
        return True
    
    def check_cash_flow_consistency(self, operating_cf, net_income):
        """
        التحقق من اتساق التدفق النقدي التشغيلي مع صافي الربح
        """
        if net_income > 0 and operating_cf < net_income * 0.5:
            self.warnings.append({
                'type': 'تحذير',
                'description': 'التدفق النقدي التشغيلي أقل بكثير من صافي الربح',
                'operating_cf': operating_cf,
                'net_income': net_income,
                'note': 'قد يشير إلى مشاكل في تحصيل الفلوس'
            })
        
        return True
    
    def check_inventory_sanity(self, inventory, cogs):
        """
        التحقق من معقولية مستويات المخزون
        """
        if inventory == 0 and cogs > 0:
            self.warnings.append({
                'type': 'تحذير',
                'description': 'المخزون = صفر بينما تكلفة البضاعة > 0',
                'note': 'قد يكون خطأ في البيانات'
            })
        
        return True
    
    def generate_audit_report(self):
        """توليد تقرير التدقيق الشامل"""
        report = "\n" + "="*70
        report += "\n🔍 تقرير التدقيق والمراجعة"
        report += "\n" + "="*70
        
        # الأخطاء
        if self.issues:
            report += "\n\n❌ الأخطاء المكتشفة:"
            for idx, issue in enumerate(self.issues, 1):
                report += f"\n  {idx}. {issue['description']}"
                report += f"\n     المستوى: {issue['severity']}"
        else:
            report += "\n\n✅ لا توجد أخطاء حرجة"
        
        # التحذيرات
        if self.warnings:
            report += "\n\n⚠️ التحذيرات:"
            for idx, warning in enumerate(self.warnings, 1):
                report += f"\n  {idx}. {warning['description']}"
                if 'note' in warning:
                    report += f"\n     ملاحظة: {warning['note']}"
        else:
            report += "\n\n✅ لا توجد تحذيرات"
        
        # الملاحظات الإيجابية
        if self.notes:
            report += "\n\n✅ الملاحظات الإيجابية:"
            for note in self.notes:
                report += f"\n  • {note}"
        
        report += "\n\n" + "="*70
        report += "\n📊 الخلاصة:"
        
        if not self.issues:
            report += "\n✅ المراجعة الداخلية: نجح"
            report += "\n🎯 حالة البيانات: موثوقة"
        else:
            report += f"\n❌ المراجعة الداخلية: فشل ({len(self.issues)} أخطاء)"
            report += "\n🎯 حالة البيانات: تحتاج إلى تصحيح"
        
        report += "\n" + "="*70 + "\n"
        
        return report
    
    def get_audit_summary(self):
        """الحصول على ملخص التدقيق"""
        return {
            'total_issues': len(self.issues),
            'total_warnings': len(self.warnings),
            'issues': self.issues,
            'warnings': self.warnings,
            'notes': self.notes,
            'report': self.generate_audit_report()
        }
    
    def clear_audit(self):
        """مسح نتائج التدقيق السابقة"""
        self.issues = []
        self.warnings = []
        self.notes = []
        