# التحليل المالي المتقدم
# ======================

class FinancialAnalyzer:
    """فئة لإجراء تحليل مالي متقدم"""
    
    def __init__(self, financial_data):
        """تهيئة المحلل المالي"""
        self.data = financial_data
        self.analysis_results = {}
    
    def trend_analysis(self, data_series):
        """
        تحليل الاتجاهات
        
        يحسب التغير النسبي والمطلق
        """
        if len(data_series) < 2:
            return None
        
        trends = []
        for i in range(1, len(data_series)):
            prev_value = data_series[i-1]
            curr_value = data_series[i]
            
            if prev_value == 0:
                percentage_change = 0
            else:
                percentage_change = ((curr_value - prev_value) / prev_value) * 100
            
            trends.append({
                'period': i,
                'value': curr_value,
                'change': curr_value - prev_value,
                'percentage_change': round(percentage_change, 2)
            })
        
        return trends
    
    _LOWER_IS_BETTER = frozenset({
        'debt_to_equity', 'debt_ratio', 'days_sales_outstanding',
    })

    def comparative_analysis(self, company_ratios, industry_average):
        """
        تحليل مقارن بين الشركة والمتوسط الصناعي
        
        المدخلات:
            company_ratios: نسب الشركة
            industry_average: المتوسط الصناعي
        """
        comparison = {}
        
        for ratio_name, company_value in company_ratios.items():
            industry_value = industry_average.get(ratio_name, 0)
            
            if industry_value == 0:
                difference = 0
                percentage_diff = 0
            else:
                difference = company_value - industry_value
                percentage_diff = (difference / industry_value) * 100
            
            if ratio_name in self._LOWER_IS_BETTER:
                is_better = company_value < industry_value
            else:
                is_better = company_value > industry_value
            
            comparison[ratio_name] = {
                'company_value': company_value,
                'industry_average': industry_value,
                'difference': round(difference, 4),
                'percentage_difference': round(percentage_diff, 2),
                'status': '✅ أفضل' if is_better else '❌ أقل'
            }
        
        return comparison
    
    def dupont_analysis(self, net_income, revenue, total_assets, equity):
        """
        تحليل DuPont (تحليل العائد على حقوق المالكين)
        
        ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
        """
        
        # حساب المكونات
        net_profit_margin = (net_income / revenue) * 100 if revenue != 0 else 0
        asset_turnover = revenue / total_assets if total_assets != 0 else 0
        equity_multiplier = total_assets / equity if equity != 0 else 0
        
        # حساب ROE
        roe = (net_profit_margin / 100) * asset_turnover * equity_multiplier * 100
        
        # ✅ تخزين النتيجة في analysis_results للـ report
        self.analysis_results['dupont'] = {
            'net_profit_margin': round(net_profit_margin, 2),
            'asset_turnover': round(asset_turnover, 4),
            'equity_multiplier': round(equity_multiplier, 4),
            'roe': round(roe, 2)
        }
        
        return {
            'net_profit_margin': round(net_profit_margin, 2),
            'asset_turnover': round(asset_turnover, 4),
            'equity_multiplier': round(equity_multiplier, 4),
            'roe': round(roe, 2),
            'analysis': self._interpret_dupont(net_profit_margin, asset_turnover, equity_multiplier)
        }
    
    def _interpret_dupont(self, npm, at, em):
        """تفسير نتائج تحليل DuPont"""
        interpretation = []
        
        if npm > 10:
            interpretation.append("✅ هامش ربح عالي جداً")
        elif npm > 5:
            interpretation.append("✅ هامش ربح جيد")
        else:
            interpretation.append("❌ هامش ربح منخفض")
        
        if at > 1.5:
            interpretation.append("✅ معدل دوران أصول عالي")
        elif at > 1:
            interpretation.append("✅ معدل دوران أصول جيد")
        else:
            interpretation.append("❌ معدل دوران أصول منخفض")
        
        if em > 3:
            interpretation.append("⚠️ رافعة مالية عالية (مخاطرة أعلى)")
        elif em > 2:
            interpretation.append("✅ رافعة مالية متوازنة")
        else:
            interpretation.append("✅ رافعة مالية منخفضة")
        
        return interpretation
    
    def working_capital_analysis(self, current_assets, current_liabilities, inventory):
        """
        تحليل رأس المال العامل
        
        رأس المال العامل = الأصول المتداولة - الالتزامات المتداولة
        """
        working_capital = current_assets - current_liabilities
        net_working_capital = current_assets - inventory - current_liabilities
        
        return {
            'working_capital': round(working_capital, 2),
            'operating_cycle': round(net_working_capital, 2),
            'status': '✅ موجب' if working_capital > 0 else ('⚠️ صفر' if working_capital == 0 else '❌ سالب')
        }
    
    def cash_flow_analysis(self, operating_cash_flow, investing_cash_flow, financing_cash_flow):
        """تحليل التدفقات النقدية"""
        
        total_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        analysis = {
            'operating_cash_flow': operating_cash_flow,
            'investing_cash_flow': investing_cash_flow,
            'financing_cash_flow': financing_cash_flow,
            'total_cash_flow': total_cash_flow,
            'analysis': self._interpret_cash_flow(operating_cash_flow, investing_cash_flow, financing_cash_flow)
        }
        
        return analysis
    
    def _interpret_cash_flow(self, ocf, icf, fcf):
        """تفسير التدفقات النقدية"""
        interpretation = []
        
        if ocf > 0:
            interpretation.append("✅ التدفق النقدي التشغيلي موجب - عملياتنا مربحة")
        else:
            interpretation.append("❌ التدفق النقدي التشغيلي سالب - قلق")
        
        if icf < 0:
            interpretation.append("ℹ️ التدفق الاستثماري سالب - استثمار في النمو")
        else:
            interpretation.append("ℹ️ التدفق الاستثماري موجب - تصفية الاستثمارات")
        
        return interpretation
    
    def generate_report(self):
        """توليد تقرير التحليل الشامل"""
        report = "\n" + "="*60
        report += "\n📊 تقرير التحليل المالي الشامل"
        report += "\n" + "="*60
        
        report += "\n\n📈 الاتجاهات:"
        if 'trends' in self.analysis_results:
            for trend in self.analysis_results['trends']:
                report += f"\n  الفترة {trend['period']}: {trend['value']} (التغير: {trend['percentage_change']}%)"
        
        report += "\n\n🔄 تحليل DuPont:"
        if 'dupont' in self.analysis_results:
            dupont = self.analysis_results['dupont']
            report += f"\n  • هامش الربح الصافي: {dupont['net_profit_margin']}%"
            report += f"\n  • معدل دوران الأصول: {dupont['asset_turnover']}"
            report += f"\n  • الرافعة المالية: {dupont['equity_multiplier']}"
            report += f"\n  • العائد على حقوق المالكين (ROE): {dupont['roe']}%"
        
        report += "\n\n💰 رأس المال العامل:"
        if 'working_capital' in self.analysis_results:
            wc = self.analysis_results['working_capital']
            report += f"\n  • رأس المال العامل: {wc['working_capital']}"
            report += f"\n  • دورة التشغيل: {wc['operating_cycle']}"
        
        report += "\n\n" + "="*60
        
        return report
    
    def get_summary(self):
        """الحصول على ملخص التحليل"""
        return {
            'analysis_results': self.analysis_results,
            'report': self.generate_report()
        }
    