"""Tests for fraud detection, email notifier, and activity log modules."""

import os
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from collections import deque

from modules.fraud_detection import FraudDetector, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW
from modules.activity_log import ActivityLog
from modules.email_notifier import EmailNotifier


class TestFraudDetector(unittest.TestCase):
    """Tests for FraudDetector rule engine."""

    def setUp(self):
        self.detector = FraudDetector()
        self.detector.clear_alerts()

    # --- Rule 1: Large change ---
    def test_large_change_triggers_medium(self):
        alerts = self.detector.check_data_change("revenue", 100, 200)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], SEVERITY_MEDIUM)
        self.assertEqual(alerts[0]["rule"], "large_change")

    def test_small_change_no_alert(self):
        alerts = self.detector.check_data_change("revenue", 100, 105)
        self.assertEqual(len(alerts), 0)

    def test_exact_20_percent_no_alert(self):
        alerts = self.detector.check_data_change("revenue", 100, 120)
        self.assertEqual(len(alerts), 0)

    def test_over_20_percent_triggers(self):
        alerts = self.detector.check_data_change("revenue", 100, 121)
        self.assertEqual(len(alerts), 1)

    def test_zero_old_value_no_large_change(self):
        alerts = self.detector.check_data_change("revenue", 0, 500)
        self.assertEqual(len(alerts), 0)

    # --- Rule 2: Negative revenue ---
    def test_negative_revenue_triggers_high(self):
        alerts = self.detector.check_data_change("revenue", 100, -50)
        high = [a for a in alerts if a["severity"] == SEVERITY_HIGH]
        self.assertGreater(len(high), 0)
        self.assertEqual(high[0]["rule"], "negative_revenue")

    def test_positive_revenue_no_alert(self):
        alerts = self.detector.check_data_change("revenue", 100, 200)
        for a in alerts:
            self.assertNotEqual(a["rule"], "negative_revenue")

    def test_negative_non_revenue_field_no_alert(self):
        alerts = self.detector.check_data_change("total_assets", 100, -50)
        revenue_alerts = [a for a in alerts if a["rule"] == "negative_revenue"]
        self.assertEqual(len(revenue_alerts), 0)

    # --- Balance check (new proper version) ---
    def test_balanced_sheet_no_alert(self):
        data = {"total_assets": 500000, "total_liabilities": 200000, "equity": 300000}
        alerts = self.detector.check_balance_sheet(data)
        self.assertEqual(len(alerts), 0)

    def test_unbalanced_sheet_triggers_medium(self):
        data = {"total_assets": 500000, "total_liabilities": 200000, "equity": 200000}
        alerts = self.detector.check_balance_sheet(data)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], SEVERITY_MEDIUM)
        self.assertEqual(alerts[0]["rule"], "balance_check")

    def test_all_zero_no_alert(self):
        data = {"total_assets": 0, "total_liabilities": 0, "equity": 0}
        alerts = self.detector.check_balance_sheet(data)
        self.assertEqual(len(alerts), 0)

    def test_missing_data_treated_as_zero(self):
        data = {}
        alerts = self.detector.check_balance_sheet(data)
        self.assertEqual(len(alerts), 0)

    # --- Rapid edits ---
    def test_rapid_edits_no_alert_under_limit(self):
        for _ in range(5):
            self.detector.check_rapid_edits()
        count = self.detector.get_alert_count()
        self.assertEqual(count["high"], 0)

    def test_rapid_edits_triggers_over_limit(self):
        for _ in range(6):
            self.detector.check_rapid_edits()
        count = self.detector.get_alert_count()
        self.assertGreater(count["high"], 0)

    # --- Post-audit change ---
    def test_post_audit_change_when_not_approved(self):
        alerts = self.detector.check_after_audit("revenue", 100)
        self.assertEqual(len(alerts), 0)

    def test_post_audit_change_when_approved(self):
        self.detector.mark_audit_approved()
        alerts = self.detector.check_after_audit("revenue", 100)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["severity"], SEVERITY_HIGH)
        self.assertEqual(alerts[0]["rule"], "post_audit_change")

    def test_mark_audit_reset(self):
        self.detector.mark_audit_approved()
        self.detector.mark_audit_reset()
        alerts = self.detector.check_after_audit("revenue", 100)
        self.assertEqual(len(alerts), 0)

    # --- Tax consistency ---
    def test_tax_consistency_profit_no_tax(self):
        financial = {"net_income": 50000}
        tax = {"total_taxes": 0}
        alerts = self.detector.check_tax_consistency(financial, tax)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["rule"], "no_taxes_with_profit")

    def test_tax_consistency_loss_with_tax(self):
        financial = {"net_income": -10000}
        tax = {"total_taxes": 5000}
        alerts = self.detector.check_tax_consistency(financial, tax)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["rule"], "taxes_with_loss")

    def test_tax_consistency_profit_with_tax_ok(self):
        financial = {"net_income": 50000}
        tax = {"total_taxes": 10000}
        alerts = self.detector.check_tax_consistency(financial, tax)
        self.assertEqual(len(alerts), 0)

    def test_tax_consistency_empty_data(self):
        alerts = self.detector.check_tax_consistency({}, {})
        self.assertEqual(len(alerts), 0)

    def test_tax_consistency_none_data(self):
        alerts = self.detector.check_tax_consistency(None, None)
        self.assertEqual(len(alerts), 0)

    # --- get_alerts / get_alert_count / clear ---
    def test_get_alerts_returns_limited(self):
        for i in range(20):
            self.detector.check_data_change(f"field_{i}", 0, 100 + i * 30)
        alerts = self.detector.get_alerts(limit=5)
        self.assertLessEqual(len(alerts), 5)

    def test_get_alerts_filter_severity(self):
        self.detector.check_data_change("revenue", 100, -50)  # HIGH + MEDIUM
        self.detector.check_data_change("revenue", 0, 5000)   # no alert (old=0)
        high = self.detector.get_alerts(severity_filter=SEVERITY_HIGH)
        medium = self.detector.get_alerts(severity_filter=SEVERITY_MEDIUM)
        self.assertGreaterEqual(len(high), 1)
        self.assertGreaterEqual(len(medium), 1)

    def test_clear_alerts(self):
        self.detector.check_data_change("revenue", 100, -50)
        self.detector.clear_alerts()
        self.assertEqual(self.detector.get_alert_count()["total"], 0)


class TestActivityLog(unittest.TestCase):
    """Tests for ActivityLog."""

    def setUp(self):
        self.log = ActivityLog()
        self.log.clear()

    def test_log_creates_entry(self):
        self.log.log("test_action", "test details")
        entries = self.log.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "test_action")
        self.assertEqual(entries[0]["details"], "test details")

    def test_log_stores_timestamp(self):
        self.log.log("action")
        entries = self.log.get_entries()
        self.assertIn("time", entries[0])

    def test_multiple_entries(self):
        for i in range(10):
            self.log.log(f"action_{i}")
        entries = self.log.get_entries()
        self.assertEqual(len(entries), 10)

    def test_get_entries_limit(self):
        for i in range(20):
            self.log.log(f"action_{i}")
        entries = self.log.get_entries(limit=5)
        self.assertEqual(len(entries), 5)
        self.assertEqual(entries[-1]["action"], "action_19")

    def test_clear(self):
        self.log.log("action")
        self.log.clear()
        entries = self.log.get_entries()
        self.assertEqual(len(entries), 0)

    def test_empty_log(self):
        entries = self.log.get_entries()
        self.assertEqual(len(entries), 0)


class TestEmailNotifier(unittest.TestCase):
    """Tests for EmailNotifier configuration logic."""

    def setUp(self):
        self.notifier = EmailNotifier()

    def test_not_configured_by_default(self):
        self.assertFalse(self.notifier.is_configured())

    def test_configure_enables(self):
        self.notifier.configure("smtp.gmail.com", 587, "test@gmail.com", "pass", "manager@gmail.com")
        self.assertTrue(self.notifier.is_configured())

    def test_configure_missing_fields_not_enabled(self):
        self.notifier.configure("smtp.gmail.com", 587, "", "pass", "manager@gmail.com")
        self.assertFalse(self.notifier.is_configured())

    def test_send_alert_returns_false_when_not_configured(self):
        result, msg = self.notifier.send_alert({"severity": "high", "rule": "test"})
        self.assertFalse(result)
        self.assertIn("not configured", msg.lower())

    def test_send_summary_returns_false_when_not_configured(self):
        result, msg = self.notifier.send_summary({}, [])
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
