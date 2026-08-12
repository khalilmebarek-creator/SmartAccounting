"""Tests for IAS/IFRS financial reports engine."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest import mock

from ui.app_state import state


class TestIASReports(unittest.TestCase):

    def setUp(self):
        state.clear()
        state.financial_data = {
            "current_assets": 150000,
            "inventory": 25000,
            "cash": 12000,
            "total_assets": 600000,
            "current_liabilities": 60000,
            "total_liabilities": 220000,
            "equity": 380000,
            "revenue": 250000,
            "cogs": 140000,
            "gross_profit": 50000,
            "operating_expenses": 25000,
            "net_income": 20000,
            "avg_receivables": 45000,
            "avg_inventory": 25000,
            "avg_payables": 20000,
            "fiscal_year": 2024,
        }
        state.tax_summary = {"ibs": 5000}
        state.company_name = "TEST Co"
        state.company_name_fr = "TEST Co"

    def tearDown(self):
        state.clear()

    def test_generate_balance_sheet(self):
        from modules.ias_reports import generate_balance_sheet
        bs = generate_balance_sheet()
        self.assertIsNotNone(bs)
        self.assertIn("assets", bs)
        self.assertIn("equity_liabilities", bs)
        self.assertAlmostEqual(bs["total_assets"], 600000, delta=1)
        nca = 600000 - 150000
        self.assertAlmostEqual(bs["assets"]["total_non_current"], nca, delta=1)
        self.assertAlmostEqual(bs["assets"]["total_current"], 150000, delta=1)

    def test_generate_income_statement(self):
        from modules.ias_reports import generate_income_statement
        inc = generate_income_statement()
        self.assertIsNotNone(inc)
        self.assertAlmostEqual(inc["gross_profit"], 50000, delta=1)
        self.assertAlmostEqual(inc["operating_profit"], 25000, delta=1)
        self.assertGreater(inc["net_income"], 10000)

    def test_generate_cash_flow(self):
        from modules.ias_reports import generate_cash_flow
        cf = generate_cash_flow()
        self.assertIsNotNone(cf)
        self.assertIn("operating", cf)
        self.assertIn("operating_total", cf)
        self.assertIn("net_change", cf)

    def test_generate_equity_statement(self):
        from modules.ias_reports import generate_equity_statement
        eq = generate_equity_statement()
        self.assertIsNotNone(eq)
        self.assertIn("opening_balance", eq)
        self.assertAlmostEqual(eq["closing_balance"], 380000, delta=1)

    def test_generate_all(self):
        from modules.ias_reports import generate_all
        rpt = generate_all()
        self.assertIn("balance_sheet", rpt)
        self.assertIn("income_statement", rpt)
        self.assertIn("cash_flow", rpt)
        self.assertIn("equity_statement", rpt)

    def test_empty_data_does_not_crash(self):
        state.financial_data = {}
        state.tax_summary = {}
        from modules.ias_reports import generate_all
        rpt = generate_all()
        self.assertIsNotNone(rpt)
        self.assertIsNotNone(rpt["balance_sheet"])
        self.assertIsNotNone(rpt["income_statement"])
