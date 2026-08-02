# اختبارات المعايير المرجعية المتقدمة (Best Practice / الدولية / المنافسين / الاتجاه)
# =====================================================================================

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.benchmarks import BenchmarkAnalyzer, ALGERIAN_SECTORS

SAMPLE_RATIOS = {
    "current_ratio": 2.0,
    "quick_ratio": 1.1,
    "gross_profit_margin": 20.0,
    "net_profit_margin": 8.0,
    "roa": 7.0,
    "roe": 16.0,
    "debt_to_equity": 0.9,
    "asset_turnover": 1.2,
    "inventory_turnover": 6.0,
    "receivable_turnover": 8.0,
}


class TestStandardsDerivation(unittest.TestCase):
    """اشتقاق best_practice + international لكل نسبة في كل قطاع"""

    def test_all_ratios_have_best_practice_and_international(self):
        for code, info in ALGERIAN_SECTORS.items():
            for rname, bm in info["benchmarks"].items():
                self.assertIn("best_practice", bm, f"{code}/{rname}")
                self.assertIn("international", bm, f"{code}/{rname}")
                self.assertGreater(bm["best_practice"], 0, f"{code}/{rname}")
                self.assertGreater(bm["international"], 0, f"{code}/{rname}")

    def test_best_practice_between_avg_and_max(self):
        bm = ALGERIAN_SECTORS["commercial"]["benchmarks"]["current_ratio"]
        self.assertGreater(bm["best_practice"], bm["avg"])
        self.assertLess(bm["best_practice"], bm["max"])

    def test_international_above_max_for_margins(self):
        bm = ALGERIAN_SECTORS["industrial"]["benchmarks"]["net_profit_margin"]
        self.assertGreater(bm["international"], bm["max"])

    def test_debt_to_equity_best_practice_below_avg(self):
        bm = ALGERIAN_SECTORS["commercial"]["benchmarks"]["debt_to_equity"]
        self.assertLess(bm["best_practice"], bm["avg"])
        self.assertLess(bm["international"], bm["min"])


class TestComparisonExtensions(unittest.TestCase):
    def setUp(self):
        self.ba = BenchmarkAnalyzer()

    def test_compare_returns_new_fields(self):
        r = self.ba.compare_with_sector(SAMPLE_RATIOS, "commercial")
        self.assertNotIn("error", r)
        row = r["ratios"]["net_profit_margin"]
        self.assertIn("best_practice", row)
        self.assertIn("international", row)
        self.assertIn("best_practice_gap", row)
        self.assertIn("international_gap", row)

    def test_compare_returns_strengths_and_weaknesses(self):
        weak = dict(SAMPLE_RATIOS)
        weak["current_ratio"] = 0.5
        weak["net_profit_margin"] = 0.5
        r = self.ba.compare_with_sector(weak, "commercial")
        self.assertIn("strengths", r)
        self.assertIn("weaknesses", r)
        self.assertGreater(len(r["weaknesses"]), 0)
        self.assertGreater(len(r["strengths"]), 0)

    def test_top_performer_gets_best_status(self):
        top = dict(SAMPLE_RATIOS)
        top["net_profit_margin"] = 30.0
        r = self.ba.compare_with_sector(top, "commercial")
        self.assertEqual(r["ratios"]["net_profit_margin"]["status"], "best")

    def test_get_strengths_weaknesses_helper(self):
        weak = dict(SAMPLE_RATIOS)
        weak["current_ratio"] = 0.5
        sw = self.ba.get_strengths_weaknesses(weak, "commercial")
        self.assertIn("strengths", sw)
        self.assertIn("weaknesses", sw)
        self.assertGreater(len(sw["weaknesses"]), 0)


class TestCompetitorComparison(unittest.TestCase):
    def setUp(self):
        self.ba = BenchmarkAnalyzer()

    def test_ranking_sorted(self):
        competitors = [
            {"name": "CompA", "ratios": dict(SAMPLE_RATIOS)},
            {"name": "CompB", "ratios": {**SAMPLE_RATIOS, "net_profit_margin": 3.0}},
        ]
        r = self.ba.compare_with_competitors(SAMPLE_RATIOS, "commercial", competitors)
        self.assertNotIn("error", r)
        self.assertEqual(len(r["ranking"]), 3)
        scores = [p["overall_score"] for p in r["ranking"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertGreaterEqual(r["ranking"][0]["overall_score"], r["ranking"][-1]["overall_score"])

    def test_company_flag_in_ranking(self):
        r = self.ba.compare_with_competitors(SAMPLE_RATIOS, "commercial", [])
        self.assertEqual(len(r["ranking"]), 1)
        self.assertTrue(r["ranking"][0]["is_company"])

    def test_competitor_invalid_sector(self):
        r = self.ba.compare_with_competitors(SAMPLE_RATIOS, "bad", [])
        self.assertIn("error", r)


class TestTrendAnalysis(unittest.TestCase):
    def setUp(self):
        self.ba = BenchmarkAnalyzer()

    def test_trend_data_structure(self):
        history = [
            {"year": 2022, "ratios": {"current_ratio": 1.2, "net_profit_margin": 5.0, "roe": 10.0}},
            {"year": 2023, "ratios": {"current_ratio": 1.5, "net_profit_margin": 6.0, "roe": 12.0}},
            {"year": 2024, "ratios": {"current_ratio": 1.8, "net_profit_margin": 8.0, "roe": 15.0}},
        ]
        trend = self.ba.get_trend_data(history, "commercial")
        self.assertEqual(trend["years"], [2022, 2023, 2024])
        self.assertEqual(len(trend["scores"]), 3)
        self.assertIn("net_profit_margin", trend["ratios"])
        self.assertEqual(len(trend["ratios"]["net_profit_margin"]["values"]), 3)

    def test_trend_improving_scores(self):
        history = [
            {"year": 2022, "ratios": {"current_ratio": 0.5, "net_profit_margin": 1.0}},
            {"year": 2023, "ratios": {"current_ratio": 1.2, "net_profit_margin": 5.0}},
            {"year": 2024, "ratios": {"current_ratio": 2.0, "net_profit_margin": 10.0}},
        ]
        trend = self.ba.get_trend_data(history, "commercial")
        self.assertGreater(trend["scores"][-1], trend["scores"][0])

    def test_trend_unsorted_history_sorted(self):
        history = [
            {"year": 2024, "ratios": {"current_ratio": 2.0}},
            {"year": 2022, "ratios": {"current_ratio": 1.2}},
            {"year": 2023, "ratios": {"current_ratio": 1.5}},
        ]
        trend = self.ba.get_trend_data(history, "commercial")
        self.assertEqual(trend["years"], [2022, 2023, 2024])

    def test_trend_invalid_sector(self):
        r = self.ba.get_trend_data([{"year": 2024, "ratios": {}}], "bad")
        self.assertIn("error", r)

    def test_trend_empty_history(self):
        trend = self.ba.get_trend_data([], "commercial")
        self.assertEqual(trend["years"], [])
        self.assertEqual(trend["ratios"], {})
        self.assertEqual(trend["scores"], [])


class TestReferenceStandardsDB(unittest.TestCase):
    """اختبارات جدول reference_standards (قاعدة بيانات مؤقتة)"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp_db.close()
        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name
        from database import db_connection as db_conn_module
        from database import db_operations
        from database import db_schema
        from database.db_connection import DatabaseConnection
        new_db = DatabaseConnection()
        db_conn_module.db = new_db
        db_operations.db = new_db
        db_schema.db = new_db

    @classmethod
    def tearDownClass(cls):
        import config
        config.DATABASE_PATH = cls.original_path
        from database import db_connection as db_conn_module
        db_conn_module.close_pool()
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)

    def setUp(self):
        import sqlite3
        if os.path.exists(self.tmp_db.name):
            conn = sqlite3.connect(self.tmp_db.name)
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                for (t,) in cur.fetchall():
                    cur.execute(f"DROP TABLE IF EXISTS {t}")
                conn.commit()
            finally:
                conn.close()
        from database.db_schema import create_tables
        self.assertTrue(create_tables())

    def test_save_and_get_reference_standards(self):
        from database.db_operations import save_reference_standards, get_reference_standards
        count = save_reference_standards("commercial")
        self.assertGreaterEqual(count, 10)
        rows = get_reference_standards("commercial")
        self.assertGreaterEqual(len(rows), 10)
        row = next(r for r in rows if r["ratio_name"] == "current_ratio")
        self.assertIn("best_practice", row)
        self.assertIn("international", row)
        self.assertGreater(row["best_practice"], 0)

    def test_seed_all_sectors(self):
        from database.db_operations import save_reference_standards
        count = save_reference_standards()
        self.assertGreaterEqual(count, 70)

    def test_get_reference_standards_unknown_sector(self):
        from database.db_operations import get_reference_standards
        self.assertEqual(get_reference_standards("nonexistent_sector"), [])

    def test_get_reference_standards_auto_seeds(self):
        from database.db_operations import get_reference_standards
        rows = get_reference_standards("services")
        self.assertGreaterEqual(len(rows), 10)


class TestCompetitorDB(unittest.TestCase):
    """اختبارات جدول competitor_data"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp_db.close()
        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name
        from database import db_connection as db_conn_module
        from database import db_operations
        from database import db_schema
        from database.db_connection import DatabaseConnection
        new_db = DatabaseConnection()
        db_conn_module.db = new_db
        db_operations.db = new_db
        db_schema.db = new_db

    @classmethod
    def tearDownClass(cls):
        import config
        config.DATABASE_PATH = cls.original_path
        from database import db_connection as db_conn_module
        db_conn_module.close_pool()
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)

    def setUp(self):
        import sqlite3
        if os.path.exists(self.tmp_db.name):
            conn = sqlite3.connect(self.tmp_db.name)
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                for (t,) in cur.fetchall():
                    cur.execute(f"DROP TABLE IF EXISTS {t}")
                conn.commit()
            finally:
                conn.close()
        from database.db_schema import create_tables
        self.assertTrue(create_tables())

    def test_save_get_delete_competitor(self):
        from database.db_operations import (
            save_competitor, get_competitors, delete_competitor,
        )
        name = "__test_comp__"
        ratios = {"current_ratio": 2.5, "net_profit_margin": 12.0}
        self.assertTrue(save_competitor("commercial", name, ratios))
        comps = get_competitors("commercial")
        found = [c for c in comps if c["name"] == name]
        self.assertEqual(len(found), 1)
        self.assertAlmostEqual(found[0]["ratios"]["net_profit_margin"], 12.0)
        self.assertTrue(delete_competitor("commercial", name))
        comps = get_competitors("commercial")
        self.assertFalse(any(c["name"] == name for c in comps))

    def test_competitors_sector_scoped(self):
        from database.db_operations import save_competitor, get_competitors, delete_competitor
        save_competitor("commercial", "__scoped__", {"current_ratio": 1.0})
        try:
            comps = get_competitors("services")
            self.assertFalse(any(c["name"] == "__scoped__" for c in comps))
        finally:
            delete_competitor("commercial", "__scoped__")

    def test_save_competitor_overwrites(self):
        from database.db_operations import save_competitor, get_competitors
        save_competitor("commercial", "__ow__", {"current_ratio": 1.0})
        save_competitor("commercial", "__ow__", {"current_ratio": 3.0, "roe": 20.0})
        comps = get_competitors("commercial")
        found = [c for c in comps if c["name"] == "__ow__"][0]
        self.assertAlmostEqual(found["ratios"]["current_ratio"], 3.0)
        self.assertNotIn("net_profit_margin", found["ratios"])
        from database.db_operations import delete_competitor
        delete_competitor("commercial", "__ow__")


class TestCompanyRatioHistory(unittest.TestCase):
    """اختبارات سجل النسب عبر السنوات"""

    @classmethod
    def setUpClass(cls):
        cls.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp_db.close()
        import config
        cls.original_path = config.DATABASE_PATH
        config.DATABASE_PATH = cls.tmp_db.name
        from database import db_connection as db_conn_module
        from database import db_operations
        from database import db_schema
        from database.db_connection import DatabaseConnection
        new_db = DatabaseConnection()
        db_conn_module.db = new_db
        db_operations.db = new_db
        db_schema.db = new_db

    @classmethod
    def tearDownClass(cls):
        import config
        config.DATABASE_PATH = cls.original_path
        from database import db_connection as db_conn_module
        db_conn_module.close_pool()
        if os.path.exists(cls.tmp_db.name):
            os.unlink(cls.tmp_db.name)

    def setUp(self):
        import sqlite3
        if os.path.exists(self.tmp_db.name):
            conn = sqlite3.connect(self.tmp_db.name)
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                for (t,) in cur.fetchall():
                    cur.execute(f"DROP TABLE IF EXISTS {t}")
                conn.commit()
            finally:
                conn.close()
        from database.db_schema import create_tables
        self.assertTrue(create_tables())

    def test_history_empty_for_unknown(self):
        from database.db_operations import get_company_ratio_history
        self.assertEqual(get_company_ratio_history("__no_such_company__"), [])

    def test_history_after_saving_two_years(self):
        from database.db_operations import save_analysis, get_company_ratio_history
        fy1 = save_analysis("TrendCo", 2023, {
            "current_assets": 100, "total_assets": 200,
            "current_liabilities": 50, "total_liabilities": 100,
            "equity": 100, "retained_earnings": 40,
            "revenue": 300, "cost_of_goods_sold": 200, "gross_profit": 100,
            "net_income": 30,
        }, {"current_ratio": 2.0, "net_profit_margin": 10.0, "roe": 30.0})
        fy2 = save_analysis("TrendCo", 2024, {
            "current_assets": 150, "total_assets": 260,
            "current_liabilities": 60, "total_liabilities": 120,
            "equity": 140, "retained_earnings": 50,
            "revenue": 400, "cost_of_goods_sold": 260, "gross_profit": 140,
            "net_income": 50,
        }, {"current_ratio": 2.5, "net_profit_margin": 12.5, "roe": 35.7})
        self.assertIsNotNone(fy1)
        self.assertIsNotNone(fy2)
        history = get_company_ratio_history("TrendCo")
        self.assertEqual(len(history), 2)
        self.assertEqual([h["year"] for h in history], [2023, 2024])
        self.assertIn("current_ratio", history[0]["ratios"])
        self.assertAlmostEqual(history[1]["ratios"]["net_profit_margin"], 12.5)


if __name__ == "__main__":
    unittest.main()
