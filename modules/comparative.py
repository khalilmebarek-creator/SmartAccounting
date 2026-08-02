from modules.calculations import CalculationEngine


class ComparativeAnalyzer:
    def __init__(self, financial_data_by_year):
        self.financial_data_by_year = dict(sorted(financial_data_by_year.items()))
        self.engine = CalculationEngine()
        self.key_items = [
            'revenue', 'gross_profit', 'net_income',
            'total_assets', 'total_liabilities', 'equity'
        ]
        self.ratio_keys = [
            'current_ratio', 'quick_ratio', 'gross_profit_margin',
            'net_profit_margin', 'roa', 'roe', 'asset_turnover',
            'receivables_turnover', 'days_sales_outstanding',
            'inventory_turnover', 'debt_to_equity', 'debt_ratio'
        ]

    def _compute_ratios_for_year(self, data):
        return self.engine.calculate_all_ratios(data)

    def _yoy_change(self, current, previous):
        if previous == 0:
            return {'absolute': 0, 'percentage': 0}
        absolute = round(current - previous, 4)
        percentage = round(((current - previous) / abs(previous)) * 100, 4)
        return {'absolute': absolute, 'percentage': percentage}

    def _compute_item_changes(self, all_ratios_by_year):
        years = sorted(all_ratios_by_year.keys())
        item_changes = {}
        for item in self.key_items:
            item_changes[item] = {}
            for i in range(1, len(years)):
                prev_year, curr_year = years[i - 1], years[i]
                prev_val = self.financial_data_by_year.get(prev_year, {}).get(item, 0) or 0
                curr_val = self.financial_data_by_year.get(curr_year, {}).get(item, 0) or 0
                item_changes[item][f'{prev_year}-{curr_year}'] = {
                    'previous': prev_val,
                    'current': curr_val,
                    'change': self._yoy_change(curr_val, prev_val)
                }
        return item_changes

    def _compute_ratio_changes(self, all_ratios_by_year):
        years = sorted(all_ratios_by_year.keys())
        ratio_changes = {}
        for ratio in self.ratio_keys:
            ratio_changes[ratio] = {}
            for i in range(1, len(years)):
                prev_year, curr_year = years[i - 1], years[i]
                prev_val = all_ratios_by_year.get(prev_year, {}).get(ratio, 0) or 0
                curr_val = all_ratios_by_year.get(curr_year, {}).get(ratio, 0) or 0
                ratio_changes[ratio][f'{prev_year}-{curr_year}'] = {
                    'previous': prev_val,
                    'current': curr_val,
                    'change': self._yoy_change(curr_val, prev_val)
                }
        return ratio_changes

    def get_comparison(self):
        years = sorted(self.financial_data_by_year.keys())
        all_ratios = {}
        for year in years:
            ratios = self._compute_ratios_for_year(
                self.financial_data_by_year[year]
            )
            all_ratios[year] = ratios if ratios else {}

        item_changes = self._compute_item_changes(all_ratios)
        ratio_changes = self._compute_ratio_changes(all_ratios)

        return {
            'years': years,
            'financial_data': self.financial_data_by_year,
            'ratios_by_year': all_ratios,
            'item_changes': item_changes,
            'ratio_changes': ratio_changes
        }

    def generate_report(self):
        comparison = self.get_comparison()
        years = comparison['years']
        lines = []

        lines.append('=' * 60)
        lines.append('COMPARATIVE FINANCIAL ANALYSIS REPORT')
        lines.append(f'Years: {", ".join(str(y) for y in years)}')
        lines.append('=' * 60)

        lines.append('')
        lines.append('-' * 60)
        lines.append('SECTION 1: KEY FINANCIAL ITEMS BY YEAR')
        lines.append('-' * 60)
        header = f'{"Item":<25}' + ''.join(f'{y:>12}' for y in years)
        lines.append(header)
        lines.append('-' * 60)
        for item in self.key_items:
            row = f'{item:<25}'
            for year in years:
                val = comparison['financial_data'].get(year, {}).get(item, 0)
                row += f'{val:>12,.2f}'
            lines.append(row)
        lines.append('')

        lines.append('-' * 60)
        lines.append('SECTION 2: KEY ITEMS - YEAR-OVER-YEAR CHANGES')
        lines.append('-' * 60)
        for item in self.key_items:
            lines.append(f'  {item}:')
            for period, data in comparison['item_changes'][item].items():
                change = data['change']
                lines.append(
                    f'    {period}: {data["previous"]:>12,.2f} -> '
                    f'{data["current"]:>12,.2f}  |  '
                    f'Change: {change["absolute"]:>+12,.2f}  '
                    f'({change["percentage"]:>+8.2f}%)'
                )
            lines.append('')

        lines.append('-' * 60)
        lines.append('SECTION 3: RATIOS BY YEAR')
        lines.append('-' * 60)
        header = f'{"Ratio":<25}' + ''.join(f'{y:>12}' for y in years)
        lines.append(header)
        lines.append('-' * 60)
        for ratio in self.ratio_keys:
            row = f'{ratio:<25}'
            for year in years:
                val = comparison['ratios_by_year'].get(year, {}).get(ratio, 0)
                row += f'{val:>12.4f}'
            lines.append(row)
        lines.append('')

        lines.append('-' * 60)
        lines.append('SECTION 4: RATIOS - YEAR-OVER-YEAR CHANGES')
        lines.append('-' * 60)
        for ratio in self.ratio_keys:
            lines.append(f'  {ratio}:')
            for period, data in comparison['ratio_changes'][ratio].items():
                change = data['change']
                lines.append(
                    f'    {period}: {data["previous"]:>12.4f} -> '
                    f'{data["current"]:>12.4f}  |  '
                    f'Change: {change["absolute"]:>+12.4f}  '
                    f'({change["percentage"]:>+8.2f}%)'
                )
            lines.append('')

        lines.append('=' * 60)
        lines.append('END OF REPORT')
        lines.append('=' * 60)

        return '\n'.join(lines)
