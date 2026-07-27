from typing import Optional, Dict, Any


class CashFlowStatement:

    def calculate(self, financial_data: Dict[str, Any], prev_financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if prev_financial_data is None:
            return self._simplified_estimate(financial_data)
        return self._full_calculation(financial_data, prev_financial_data)

    def _full_calculation(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        net_income = current.get("net_income", 0)
        depreciation = current.get("depreciation", 0)

        delta_ca = current.get("current_assets", 0) - previous.get("current_assets", 0)
        delta_cl = current.get("current_liabilities", 0) - previous.get("current_liabilities", 0)
        delta_inventory = current.get("inventory", 0) - previous.get("inventory", 0)

        operating = net_income + depreciation - delta_ca + delta_cl - delta_inventory

        delta_assets = current.get("total_assets", 0) - previous.get("total_assets", 0)
        investing = -delta_assets

        delta_liabilities = current.get("total_liabilities", 0) - previous.get("total_liabilities", 0)
        delta_equity = current.get("equity", 0) - previous.get("equity", 0)
        financing = delta_liabilities + delta_equity

        net_change = operating + investing + financing
        beginning_cash = previous.get("total_assets", 0) * 0.05
        ending_cash = beginning_cash + net_change

        return {
            "operating": operating,
            "investing": investing,
            "financing": financing,
            "net_change": net_change,
            "beginning_cash": beginning_cash,
            "ending_cash": ending_cash,
        }

    def _simplified_estimate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        net_income = data.get("net_income", 0)
        depreciation = data.get("depreciation", 0)
        revenue = data.get("revenue", 0)

        operating = net_income + depreciation
        investing = -(data.get("total_assets", 0) * 0.08)
        financing = -(data.get("total_liabilities", 0) * 0.02) + (data.get("equity", 0) * 0.01)

        net_change = operating + investing + financing
        beginning_cash = revenue * 0.05
        ending_cash = beginning_cash + net_change

        return {
            "operating": operating,
            "investing": investing,
            "financing": financing,
            "net_change": net_change,
            "beginning_cash": beginning_cash,
            "ending_cash": ending_cash,
        }

    def generate_report(self, results: Optional[Dict[str, Any]] = None) -> str:
        if results is None:
            results = self._last_results if hasattr(self, "_last_results") else None
        if results is None:
            return "No cash flow data available. Run calculate() first."

        self._last_results = results

        lines = [
            "=" * 50,
            "       STATEMENT OF CASH FLOWS",
            "=" * 50,
            "",
            "Cash Flows from Operating Activities",
            "-" * 50,
            f"  Net Cash from Operations:      ${results['operating']:>12,.2f}",
            "",
            "Cash Flows from Investing Activities",
            "-" * 50,
            f"  Net Cash from Investing:       ${results['investing']:>12,.2f}",
            "",
            "Cash Flows from Financing Activities",
            "-" * 50,
            f"  Net Cash from Financing:       ${results['financing']:>12,.2f}",
            "",
            "=" * 50,
            f"  Net Change in Cash:            ${results['net_change']:>12,.2f}",
            f"  Beginning Cash:                ${results['beginning_cash']:>12,.2f}",
            f"  Ending Cash:                   ${results['ending_cash']:>12,.2f}",
            "=" * 50,
        ]

        return "\n".join(lines)
