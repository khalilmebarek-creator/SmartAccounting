# محرك الحسابات المالية
# =====================

from typing import Dict, Optional, Any
from utils.app_logger import get_logger

logger = get_logger("calculations")


class CalculationEngine:
    """
    فئة لحساب جميع النسب المالية
    """

    def __init__(self, data=None):
        """تهيئة محرك الحسابات"""
        self.data = data

    @staticmethod
    def _safe_div(numerator: float, denominator: float, default: float = 0) -> float:
        if denominator == 0:
            return default
        return numerator / denominator

    @staticmethod
    def _round(value: float, places: int = 4) -> float:
        return round(value, places)
    
    # ===== نسب السيولة =====
    
    def current_ratio(self, current_assets: float, current_liabilities: float) -> float:
        return self._round(self._safe_div(current_assets, current_liabilities))
    
    def quick_ratio(self, current_assets: float, inventory: float, current_liabilities: float) -> float:
        return self._round(self._safe_div(current_assets - inventory, current_liabilities))
    
    def cash_ratio(self, cash: float, current_liabilities: float) -> float:
        return self._round(self._safe_div(cash, current_liabilities))
    
    # ===== نسب الربحية =====
    
    def gross_profit_margin(self, gross_profit: float, revenue: float) -> float:
        return self._round(self._safe_div(gross_profit, revenue) * 100)
    
    def operating_profit_margin(self, operating_income: float, revenue: float) -> float:
        return self._round(self._safe_div(operating_income, revenue) * 100)
    
    def net_profit_margin(self, net_income: float, revenue: float) -> float:
        return self._round(self._safe_div(net_income, revenue) * 100)
    
    def roa(self, net_income: float, total_assets: float) -> float:
        return self._round(self._safe_div(net_income, total_assets) * 100)
    
    def roe(self, net_income: float, equity: float) -> float:
        return self._round(self._safe_div(net_income, equity) * 100)
    
    # ===== نسب الكفاءة =====
    
    def asset_turnover(self, revenue: float, total_assets: float) -> float:
        return self._round(self._safe_div(revenue, total_assets))
    
    def receivables_turnover(self, revenue: float, average_receivables: float) -> float:
        return self._round(self._safe_div(revenue, average_receivables))
    
    def days_sales_outstanding(self, receivables_turnover: float) -> float:
        return self._round(self._safe_div(365, receivables_turnover), 0)
    
    def inventory_turnover(self, cost_of_goods_sold: float, average_inventory: float) -> float:
        return self._round(self._safe_div(cost_of_goods_sold, average_inventory))
    
    def days_inventory_outstanding(self, inventory_turnover: float) -> float:
        return self._round(self._safe_div(365, inventory_turnover), 0)
    
    def payables_turnover(self, cost_of_goods_sold: float, average_payables: float) -> float:
        return self._round(self._safe_div(cost_of_goods_sold, average_payables))
    
    def days_payable_outstanding(self, payables_turnover: float) -> float:
        return self._round(self._safe_div(365, payables_turnover), 0)
    
    def operating_cycle(self, days_inventory_outstanding: float, days_sales_outstanding: float) -> float:
        return self._round(days_inventory_outstanding + days_sales_outstanding, 0)
    
    def cash_conversion_cycle(self, days_inventory_outstanding: float, days_sales_outstanding: float,
                               days_payable_outstanding: float) -> float:
        return self._round(days_inventory_outstanding + days_sales_outstanding - days_payable_outstanding, 0)
    
    # ===== نسب الاستدانة =====
    
    def debt_to_equity(self, total_liabilities: float, equity: float) -> float:
        return self._round(self._safe_div(total_liabilities, equity))
    
    def debt_ratio(self, total_liabilities: float, total_assets: float) -> float:
        return self._round(self._safe_div(total_liabilities, total_assets))
    
    def equity_ratio(self, equity: float, total_assets: float) -> float:
        return self._round(self._safe_div(equity, total_assets))
    
    # ===== دالة شاملة لحساب جميع النسب =====
    
    def calculate_all_ratios(self, financial_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """
        حساب جميع النسب المالية دفعة واحدة
        
        المدخلات:
        {
            'current_assets': float,
            'inventory': float,
            'current_liabilities': float,
            'cash': float (اختياري),
            'gross_profit': float,
            'operating_expenses': float (اختياري),
            'net_income': float,
            'revenue': float,
            'total_assets': float,
            'equity': float,
            'cost_of_goods_sold': float,
            'average_receivables': float,
            'average_inventory': float,
            'average_payables': float (اختياري),
            'total_liabilities': float
        }
        """
        
        try:
            ratios = {}
            operating_income = financial_data.get('operating_income', 0) or 0
            if operating_income == 0 and 'gross_profit' in financial_data and 'operating_expenses' in financial_data:
                operating_income = max(0, (financial_data.get('gross_profit', 0) or 0) - (financial_data.get('operating_expenses', 0) or 0))

            ratio_calcs = [
                ('current_ratio', self.current_ratio, financial_data['current_assets'], financial_data['current_liabilities']),
                ('quick_ratio', self.quick_ratio, financial_data['current_assets'], financial_data['inventory'], financial_data['current_liabilities']),
                ('cash_ratio', self.cash_ratio, financial_data.get('cash', 0) or 0, financial_data['current_liabilities']),
                ('gross_profit_margin', self.gross_profit_margin, financial_data['gross_profit'], financial_data['revenue']),
                ('operating_profit_margin', self.operating_profit_margin, operating_income, financial_data['revenue']),
                ('net_profit_margin', self.net_profit_margin, financial_data['net_income'], financial_data['revenue']),
                ('roa', self.roa, financial_data['net_income'], financial_data['total_assets']),
                ('roe', self.roe, financial_data['net_income'], financial_data['equity']),
                ('asset_turnover', self.asset_turnover, financial_data['revenue'], financial_data['total_assets']),
                ('receivables_turnover', self.receivables_turnover, financial_data['revenue'], financial_data['average_receivables']),
                ('inventory_turnover', self.inventory_turnover, financial_data['cost_of_goods_sold'], financial_data['average_inventory']),
                ('payables_turnover', self.payables_turnover, financial_data.get('cost_of_goods_sold', 0) or 0, financial_data.get('average_payables', 0) or 0),
                ('debt_to_equity', self.debt_to_equity, financial_data['total_liabilities'], financial_data['equity']),
                ('debt_ratio', self.debt_ratio, financial_data['total_liabilities'], financial_data['total_assets']),
                ('equity_ratio', self.equity_ratio, financial_data['equity'], financial_data['total_assets']),
            ]

            for entry in ratio_calcs:
                name, func = entry[0], entry[1]
                args = entry[2:]
                try:
                    ratios[name] = func(*args)
                except Exception as e:
                    ratios[name] = 0
                    logger.warning(f"Ratio {name} failed: {e}")

            try:
                ratios['days_sales_outstanding'] = self.days_sales_outstanding(
                    ratios.get('receivables_turnover', 0)
                )
            except Exception as e:
                ratios['days_sales_outstanding'] = 0
                logger.warning(f"Ratio days_sales_outstanding failed: {e}")

            try:
                ratios['days_inventory_outstanding'] = self.days_inventory_outstanding(
                    ratios.get('inventory_turnover', 0)
                )
            except Exception as e:
                ratios['days_inventory_outstanding'] = 0
                logger.warning(f"Ratio days_inventory_outstanding failed: {e}")

            try:
                ratios['days_payable_outstanding'] = self.days_payable_outstanding(
                    ratios.get('payables_turnover', 0)
                )
            except Exception as e:
                ratios['days_payable_outstanding'] = 0
                logger.warning(f"Ratio days_payable_outstanding failed: {e}")

            try:
                ratios['operating_cycle'] = self.operating_cycle(
                    ratios.get('days_inventory_outstanding', 0),
                    ratios.get('days_sales_outstanding', 0)
                )
            except Exception as e:
                ratios['operating_cycle'] = 0
                logger.warning(f"Ratio operating_cycle failed: {e}")

            try:
                ratios['cash_conversion_cycle'] = self.cash_conversion_cycle(
                    ratios.get('days_inventory_outstanding', 0),
                    ratios.get('days_sales_outstanding', 0),
                    ratios.get('days_payable_outstanding', 0)
                )
            except Exception as e:
                ratios['cash_conversion_cycle'] = 0
                logger.warning(f"Ratio cash_conversion_cycle failed: {e}")

            logger.info(f"Ratios calculated: ROE={ratios.get('roe',0)}%, CR={ratios.get('current_ratio',0)}")
            return ratios

        except Exception as e:
            logger.error(f"Ratio calculation failed: {e}")
            return None
    
    # ===== Altman Z-Score =====
    
    def z_score(self, working_capital: float, retained_earnings: float, ebit: float,
                market_value_equity: float, book_value_debt: float, sales: float,
                total_assets: float) -> Dict[str, Any]:
        """
        Altman Z-Score: توقع إفلاس الشركة
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        X1 = رأس المال العامل / الأصول الكلية
        X2 = الأرباح المحتفظ بها / الأصول الكلية
        X3 = EBIT / الأصول الكلية
        X4 = القيمة السوقية / القيمة الدفترية للخصوم
        X5 = المبيعات / الأصول الكلية
        """
        if total_assets == 0:
            return {"z_score": 0, "status": "danger", "status_en": "Danger", "status_fr": "Danger", "components": {}}

        x1 = self._safe_div(working_capital, total_assets)
        x2 = self._safe_div(retained_earnings, total_assets)
        x3 = self._safe_div(ebit, total_assets)
        x4 = self._safe_div(market_value_equity, book_value_debt)
        x5 = self._safe_div(sales, total_assets)

        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

        if z > 2.99:
            status = "safe"
            status_en = "Safe"
            status_fr = "Sûr"
        elif z > 1.81:
            status = "grey"
            status_en = "Grey Zone"
            status_fr = "Zone Grise"
        else:
            status = "danger"
            status_en = "Danger"
            status_fr = "Danger"

        return {
            "z_score": round(z, 3),
            "status": status,
            "status_en": status_en,
            "status_fr": status_fr,
            "components": {
                "x1": round(x1, 4),
                "x2": round(x2, 4),
                "x3": round(x3, 4),
                "x4": round(x4, 4),
                "x5": round(x5, 4),
            }
        }

    def print_ratios(self, ratios: Optional[Dict[str, Any]]) -> None:
        """طباعة النسب المالية بشكل منسق"""
        if not ratios:
            logger.warning("No ratios to print")
            return
        
        logger.info("Ratios: CR=%.2f, QR=%.2f, CashR=%.2f, GPM=%.2f%%, OPM=%.2f%%, NPM=%.2f%%, ROA=%.2f%%, ROE=%.2f%%",
                     ratios.get('current_ratio', 0), ratios.get('quick_ratio', 0),
                     ratios.get('cash_ratio', 0),
                     ratios.get('gross_profit_margin', 0), ratios.get('operating_profit_margin', 0),
                     ratios.get('net_profit_margin', 0),
                     ratios.get('roa', 0), ratios.get('roe', 0))
        logger.info("Efficiency: AT=%.2f, RT=%.2f, DSO=%.0f, IT=%.2f, DIO=%.0f, PT=%.2f, DPO=%.0f, OC=%.0f, CCC=%.0f",
                     ratios.get('asset_turnover', 0), ratios.get('receivables_turnover', 0),
                     ratios.get('days_sales_outstanding', 0), ratios.get('inventory_turnover', 0),
                     ratios.get('days_inventory_outstanding', 0), ratios.get('payables_turnover', 0),
                     ratios.get('days_payable_outstanding', 0), ratios.get('operating_cycle', 0),
                     ratios.get('cash_conversion_cycle', 0))
        logger.info("Leverage: D/E=%.2f, DR=%.2f, ER=%.2f",
                     ratios.get('debt_to_equity', 0), ratios.get('debt_ratio', 0),
                     ratios.get('equity_ratio', 0))
        