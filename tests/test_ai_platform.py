"""Tests for AI Platform — integrated financial health analysis."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from ui.app_state import state


class TestAIPlatform(unittest.TestCase):

    def setUp(self):
        state.clear()
        state.financial_data = {
            "current_assets": 150000, "inventory": 25000, "cash": 12000,
            "total_assets": 600000, "current_liabilities": 60000,
            "total_liabilities": 220000, "equity": 380000,
            "revenue": 250000, "cogs": 140000, "gross_profit": 50000,
            "operating_expenses": 25000, "net_income": 20000,
            "avg_receivables": 45000, "avg_inventory": 25000,
            "avg_payables": 20000, "fiscal_year": 2024,
        }
        state.ratios = {
            "roe": 25.0, "net_profit_margin": 12.0, "current_ratio": 2.5,
            "quick_ratio": 1.5, "debt_to_equity": 0.8, "debt_ratio": 0.35,
            "inventory_turnover": 8.0, "receivables_turnover": 6.5,
            "z_score": 3.5,
        }
        state.company_name = "TEST Platform"

    def tearDown(self):
        state.clear()

    def test_health_score_total(self):
        from modules.ai_platform import compute_health_score
        hs = compute_health_score()
        self.assertIn("total", hs)
        self.assertGreater(hs["total"], 50)
        self.assertLessEqual(hs["total"], 100)

    def test_health_score_breakdown(self):
        from modules.ai_platform import compute_health_score
        hs = compute_health_score()
        for key in ("profitability", "liquidity", "leverage", "efficiency", "growth", "stability"):
            self.assertIn(key, hs["breakdown"])

    def test_health_score_grade(self):
        from modules.ai_platform import compute_health_score
        hs = compute_health_score()
        self.assertIn("grade", hs)
        self.assertIsInstance(hs["grade"], tuple)
        self.assertEqual(len(hs["grade"]), 3)

    def test_risk_radar(self):
        from modules.ai_platform import compute_risk_radar
        rr = compute_risk_radar()
        for key in ("liquidity_risk", "leverage_risk", "profitability_risk",
                     "efficiency_risk", "growth_risk", "solvency_risk"):
            self.assertIn(key, rr)
            self.assertGreaterEqual(rr[key], 0)
            self.assertLessEqual(rr[key], 100)

    def test_executive_summary(self):
        from modules.ai_platform import executive_summary
        es = executive_summary()
        self.assertIsInstance(es, list)
        self.assertGreater(len(es), 2)

    def test_recommendations(self):
        from modules.ai_platform import strategic_recommendations
        recs = strategic_recommendations()
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)

    def test_platform_analysis_aggregate(self):
        from modules.ai_platform import platform_analysis
        pa = platform_analysis()
        self.assertIn("health_score", pa)
        self.assertIn("risk_radar", pa)
        self.assertIn("executive_summary", pa)
        self.assertIn("recommendations", pa)

    def test_empty_data_does_not_crash(self):
        state.financial_data = {}
        state.ratios = {}
        from modules.ai_platform import compute_health_score, compute_risk_radar
        hs = compute_health_score()
        self.assertIsNotNone(hs)
        rr = compute_risk_radar()
        self.assertIsNotNone(rr)
