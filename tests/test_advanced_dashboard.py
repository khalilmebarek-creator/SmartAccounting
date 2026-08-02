# اختبارات لوحة التحكم المتقدمة
# ===============================

import unittest
import sys
import os
import sqlite3
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.advanced_dashboard import (
    AdvancedDashboardEngine, DEFAULT_KPIS, ALL_WIDGETS
)


FD = {
    "current_assets": 200000,
    "inventory": 50000,
    "current_liabilities": 100000,
    "cash": 30000,
    "total_assets": 500000,
    "total_liabilities": 200000,
    "equity": 300000,
    "revenue": 600000,
    "cost_of_goods_sold": 300000,
    "gross_profit": 300000,
    "operating_expenses": 100000,
    "net_income": 200000,
    "average_receivables": 40000,
    "average_inventory": 25000,
    "average_payables": 18000,
}


def make_ratios():
    from modules.calculations import CalculationEngine
    return CalculationEngine(FD).calculate_all_ratios(FD)


class TestKpis(unittest.TestCase):
    """اختبارات مؤشرات الأداء الرئيسية"""

    def setUp(self):
        self.engine = AdvancedDashboardEngine()

    def test_compute_kpis_returns_six(self):
        kpis = self.engine.compute_kpis(FD, make_ratios())
        self.assertEqual(len(kpis), 6)
        keys = [k["key"] for k in kpis]
        self.assertEqual(keys, DEFAULT_KPIS)

    def test_kpi_fields(self):
        kpi = self.engine.compute_kpis(FD, make_ratios())[0]
        self.assertIn("key", kpi)
        self.assertIn("value", kpi)
        self.assertIn("unit", kpi)
        self.assertIn("status", kpi)
        self.assertIn(kpi["status"], ("green", "yellow", "red"))

    def test_kpi_values(self):
        kpis = {k["key"]: k for k in self.engine.compute_kpis(FD, make_ratios())}
        self.assertAlmostEqual(kpis["revenue"]["value"], 600000)
        self.assertAlmostEqual(kpis["roe"]["value"], 200000 / 300000 * 100, places=2)
        self.assertAlmostEqual(kpis["liquidity"]["value"], 2.0)

    def test_status_higher_better(self):
        self.assertEqual(self.engine.status_for_value("current_ratio", 2.0), "green")
        self.assertEqual(self.engine.status_for_value("current_ratio", 1.2), "yellow")
        self.assertEqual(self.engine.status_for_value("current_ratio", 0.5), "red")

    def test_status_lower_better(self):
        self.assertEqual(self.engine.status_for_value("debt_ratio", 0.4), "green")
        self.assertEqual(self.engine.status_for_value("debt_ratio", 0.6), "yellow")
        self.assertEqual(self.engine.status_for_value("debt_ratio", 0.9), "red")

    def test_status_unknown_key(self):
        self.assertEqual(self.engine.status_for_value("unknown_metric", 5), "green")


class TestCharts(unittest.TestCase):
    """اختبارات البيانات للرسوم البيانية"""

    def setUp(self):
        self.engine = AdvancedDashboardEngine()

    def test_revenue_trend_monthly(self):
        trend = self.engine.revenue_trend(FD, period="monthly")
        self.assertEqual(len(trend["labels"]), 12)
        self.assertEqual(len(trend["values"]), 12)
        self.assertAlmostEqual(sum(trend["values"]), 600000, delta=1)

    def test_revenue_trend_quarterly(self):
        trend = self.engine.revenue_trend(FD, period="quarterly")
        self.assertEqual(len(trend["labels"]), 4)
        self.assertAlmostEqual(sum(trend["values"]), 600000, delta=1)

    def test_revenue_trend_no_data(self):
        trend = self.engine.revenue_trend({}, period="monthly")
        self.assertEqual(trend["values"], [0] * 12)

    def test_expense_breakdown(self):
        e = self.engine.expense_breakdown(FD)
        self.assertEqual(e["labels"], ["cogs", "opex", "net_profit"])
        self.assertAlmostEqual(sum(e["values"]), 600000)
        self.assertAlmostEqual(e["values"][1], 100000)

    def test_profitability_trend(self):
        history = [
            {"year": 2022, "ratios": {"roe": 5, "net_profit_margin": 2}},
            {"year": 2023, "ratios": {"roe": 8, "net_profit_margin": 4}},
        ]
        trend = self.engine.profitability_trend(history)
        self.assertEqual(trend["years"], [2022, 2023])
        self.assertEqual(trend["series"]["roe"], [5, 8])

    def test_profitability_trend_unsorted(self):
        history = [
            {"year": 2023, "ratios": {"roe": 8}},
            {"year": 2022, "ratios": {"roe": 5}},
        ]
        trend = self.engine.profitability_trend(history)
        self.assertEqual(trend["years"], [2022, 2023])

    def test_profitability_trend_empty(self):
        trend = self.engine.profitability_trend([])
        self.assertEqual(trend["years"], [])

    def test_ratios_radar(self):
        data = self.engine.ratios_radar(make_ratios(), "commercial")
        self.assertIn("labels", data)
        self.assertEqual(len(data["labels"]), len(data["company"]))


class TestAlerts(unittest.TestCase):
    """اختبارات نظام التنبيهات"""

    def setUp(self):
        self.engine = AdvancedDashboardEngine()

    def test_no_anomalies_balanced(self):
        alerts = self.engine.alerts(FD, make_ratios())
        anomalies = [a for a in alerts if a["category"] == "anomaly"]
        self.assertEqual(anomalies, [])

    def test_balance_anomaly_detected(self):
        bad = dict(FD)
        bad["total_assets"] = 600000
        alerts = self.engine.alerts(bad, make_ratios())
        anomalies = [a for a in alerts if a["category"] == "anomaly"]
        self.assertTrue(any(a["severity"] == "critical" for a in anomalies))

    def test_income_mismatch_anomaly(self):
        bad = dict(FD)
        bad["net_income"] = 50000
        alerts = self.engine.alerts(bad, make_ratios())
        anomalies = [a for a in alerts if a["category"] == "anomaly"]
        self.assertTrue(any(a["key"] == "income_statement" for a in anomalies))

    def test_negative_values_anomaly(self):
        bad = dict(FD)
        bad["equity"] = -1000
        alerts = self.engine.alerts(bad, make_ratios())
        anomalies = [a for a in alerts if a["category"] == "anomaly"]
        self.assertTrue(anomalies)

    def test_performance_warning_low_liquidity(self):
        ratios = make_ratios()
        ratios["current_ratio"] = 0.5
        alerts = self.engine.alerts(FD, ratios)
        perf = [a for a in alerts
                if a["category"] == "performance" and a["key"] == "current_ratio"]
        self.assertTrue(any(a["severity"] == "warning" for a in perf))

    def test_ratio_alert_below_sector(self):
        ratios = make_ratios()
        ratios["current_ratio"] = 0.3
        alerts = self.engine.alerts(FD, ratios, sector_code="commercial")
        ratio_alerts = [a for a in alerts if a["category"] == "ratio"]
        self.assertTrue(ratio_alerts)

    def test_action_items(self):
        ratios = make_ratios()
        ratios["current_ratio"] = 0.3
        alerts = self.engine.alerts(FD, ratios, sector_code="commercial")
        actions = [a for a in alerts if a["category"] == "action"]
        self.assertTrue(actions)

    def test_alert_fields(self):
        alerts = self.engine.alerts(FD, make_ratios())
        if alerts:
            a = alerts[0]
            for field in ("category", "severity", "key", "message_ar", "message_en"):
                self.assertIn(field, a)
            self.assertIn(a["severity"], ("critical", "warning", "info"))

    def test_unknown_sector_ignored(self):
        alerts = self.engine.alerts(FD, make_ratios(), sector_code="__nope__")
        for a in alerts:
            self.assertNotEqual(a["category"], "ratio")


class TestLayouts(unittest.TestCase):
    """اختبارات نظام تخطيط الويدجتات"""

    def setUp(self):
        self.engine = AdvancedDashboardEngine()

    def test_default_layout(self):
        layout = self.engine.default_layout()
        self.assertEqual(layout["widgets"], ALL_WIDGETS)
        self.assertEqual(layout["kpis"], DEFAULT_KPIS)

    def test_build_layout(self):
        layout = self.engine.build_layout(
            ["kpi_cards", "alerts"], ["roe", "roa"], color="#123456", name="compact"
        )
        self.assertEqual(layout["name"], "compact")
        self.assertEqual(layout["widgets"], ["kpi_cards", "alerts"])
        self.assertEqual(layout["kpis"], ["roe", "roa"])
        self.assertEqual(layout["color"], "#123456")


class TestExportData(unittest.TestCase):
    """اختبارات تصدير بيانات اللوحة"""

    def test_export_data_structure(self):
        engine = AdvancedDashboardEngine()
        data = engine.export_data(FD, make_ratios(), sector_code="commercial")
        self.assertIn("kpis", data)
        self.assertIn("expenses", data)
        self.assertIn("revenue_trend", data)
        self.assertIn("alerts", data)
        self.assertEqual(len(data["kpis"]), 6)


class TestDashboardLayoutsDB(unittest.TestCase):
    """اختبارات حفظ/تحميل التخطيطات في قاعدة البيانات"""

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
        if os.path.exists(self.tmp_db.name):
            conn = sqlite3.connect(self.tmp_db.name)
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%'"
                )
                for (t,) in cur.fetchall():
                    cur.execute(f"DROP TABLE IF EXISTS {t}")
                conn.commit()
            finally:
                conn.close()
        from database.db_schema import create_tables
        self.assertTrue(create_tables())

    def test_save_and_get_layout(self):
        from database.db_operations import save_dashboard_layout, get_dashboard_layouts
        layout = {"widgets": ["kpi_cards"], "kpis": ["roe"], "color": "#123"}
        self.assertTrue(save_dashboard_layout("compact", layout))
        layouts = get_dashboard_layouts()
        self.assertTrue(any(
            l["name"] == "compact" and l["layout"]["kpis"] == ["roe"]
            for l in layouts
        ))

    def test_save_overwrites(self):
        from database.db_operations import save_dashboard_layout, get_dashboard_layouts
        save_dashboard_layout("compact", {"widgets": ["kpi_cards"], "kpis": ["roe"], "color": "#123"})
        save_dashboard_layout("compact", {"widgets": ["alerts"], "kpis": [], "color": "#999"})
        layouts = get_dashboard_layouts()
        matches = [l for l in layouts if l["name"] == "compact"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["layout"]["widgets"], ["alerts"])

    def test_delete_layout(self):
        from database.db_operations import (
            save_dashboard_layout, delete_dashboard_layout, get_dashboard_layouts
        )
        save_dashboard_layout("temp_layout", {"widgets": [], "kpis": [], "color": ""})
        self.assertTrue(delete_dashboard_layout("temp_layout"))
        self.assertFalse(any(l["name"] == "temp_layout" for l in get_dashboard_layouts()))

    def test_get_layouts_empty(self):
        from database.db_operations import get_dashboard_layouts
        self.assertEqual(get_dashboard_layouts(), [])


if __name__ == "__main__":
    unittest.main()
