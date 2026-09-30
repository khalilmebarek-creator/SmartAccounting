# اختبار القوائم المالية المرئية
# ================================
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from ui.app_state import state


class TestFinancialStatementsView(unittest.TestCase):
    """شاشة القوائم المالية المرئية: بنية سليمة + قيم معبّأة من البيانات."""

    def setUp(self):
        state.clear()
        state.financial_data = {
            "revenue": 200000, "cogs": 120000, "gross_profit": 80000,
            "operating_expenses": 40000, "net_income": 30000,
            "total_assets": 500000, "current_assets": 100000,
            "total_liabilities": 200000, "current_liabilities": 80000,
            "equity": 300000, "cash": 50000, "inventory": 20000,
            "avg_receivables": 40000, "avg_payables": 18000,
            "fiscal_year": 2026,
        }
        from ui.views.financial_statements_view import FinancialStatementsView
        self.view = FinancialStatementsView()

    def tearDown(self):
        self.view.close()
        self.view.deleteLater()
        state.clear()
        QApplication.processEvents()

    def test_stat_cards_populated(self):
        self.assertEqual(self.view._val_assets.text(), "500,000")
        self.assertEqual(self.view._val_equity.text(), "300,000")

    def test_compare_bar_values(self):
        bar = self.view._compare_bar
        self.assertGreater(bar.value_a, 0)
        self.assertGreater(bar.value_b, 0)

    def test_income_rows_rendered(self):
        self.assertGreater(self.view._inc_layout.count(), 0)

    def test_cashflow_rows_rendered(self):
        self.assertGreater(self.view._cf_layout.count(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
