# Extra unit tests for modules/tax_reminders.py (TaxReminderManager).
# Covers: file I/O branches, date-based due-date logic with fixed dates,
# acknowledge/custom-reminder error paths, and calendar summary exceptions.
# Uses a private data file; never touches the real project tax_reminders.json.

import contextlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modules.tax_reminders as tax_reminders_mod
from modules.tax_reminders import (
    TaxReminderManager,
    ALGERIAN_TAX_CALENDAR,
)


@contextlib.contextmanager
def _isolated_manager(content=None):
    """Patch REMINDERS_FILE to a temp path and build a fresh manager."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "reminders.json")
        if content is not None:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False)
        with mock.patch.object(tax_reminders_mod, "REMINDERS_FILE", path):
            yield TaxReminderManager(), path


@contextlib.contextmanager
def _patched_now(year, month, day, hour=0):
    """Freeze datetime.now() while keeping datetime(...) constructors real."""
    real_dt = datetime
    fake = mock.Mock()
    fake.now.return_value = real_dt(year, month, day, hour, 0, 0)
    fake.side_effect = lambda *a, **k: real_dt(*a, **k)
    fake.timedelta = timedelta
    with mock.patch.object(tax_reminders_mod, "datetime", fake):
        yield


class TestLoadReminders(unittest.TestCase):

    def test_load_no_file_returns_defaults(self):
        with _isolated_manager() as (manager, path):
            self.assertEqual(manager.reminders, {"custom": [], "acknowledged": []})
            self.assertEqual(manager.custom_reminders, [])
            self.assertEqual(manager.acknowledged, [])

    def test_load_valid_file(self):
        content = {"custom": [{"name": "x"}], "acknowledged": ["a1"]}
        with _isolated_manager(content) as (manager, path):
            self.assertEqual(manager.custom_reminders, [{"name": "x"}])
            self.assertEqual(manager.acknowledged, ["a1"])

    def test_load_corrupt_file_falls_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "reminders.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{this is not valid json")
            with mock.patch.object(tax_reminders_mod, "REMINDERS_FILE", path):
                manager = TaxReminderManager()
            self.assertEqual(manager.reminders, {"custom": [], "acknowledged": []})

    def test_save_failure_logged_no_crash(self):
        with _isolated_manager() as (manager, path):
            with mock.patch.object(
                tax_reminders_mod.json, "dump",
                side_effect=OSError("disk full"),
            ):
                manager.acknowledge_reminder("r1")
            self.assertIn("r1", manager.acknowledged)


class TestUpcomingReminders(unittest.TestCase):

    def test_upcoming_within_window(self):
        with _patched_now(2026, 1, 15), _isolated_manager() as (manager, _):
            upcoming = manager.get_upcoming_reminders(days_ahead=30)
        keys = [r["key"] for r in upcoming]
        self.assertIn("tva_monthly", keys)
        self.assertIn("cnas_monthly", keys)
        self.assertNotIn("ibs_quarterly", keys)
        for r in upcoming:
            self.assertIn("name_ar", r)
            self.assertIn("due_date", r)
            self.assertIn("form_number", r)

    def test_upcoming_severity_warning(self):
        with _patched_now(2026, 1, 15), _isolated_manager() as (manager, _):
            upcoming = manager.get_upcoming_reminders(30)
        tva = next(r for r in upcoming if r["key"] == "tva_monthly")
        self.assertEqual(tva["severity"], "warning")
        self.assertEqual(tva["days_until"], 5)

    def test_upcoming_severity_urgent(self):
        with _patched_now(2026, 1, 18), _isolated_manager() as (manager, _):
            upcoming = manager.get_upcoming_reminders(30)
        tva = next(r for r in upcoming if r["key"] == "tva_monthly")
        self.assertEqual(tva["severity"], "urgent")
        self.assertEqual(tva["days_until"], 2)

    def test_upcoming_severity_info(self):
        with _patched_now(2026, 1, 5), _isolated_manager() as (manager, _):
            upcoming = manager.get_upcoming_reminders(30)
        cnas = next(r for r in upcoming if r["key"] == "cnas_monthly")
        self.assertEqual(cnas["severity"], "info")
        self.assertEqual(cnas["days_until"], 25)

    def test_upcoming_acknowledged_flag(self):
        with _patched_now(2026, 1, 15), _isolated_manager() as (manager, _):
            manager.acknowledged = ["tva_monthly_202601"]
            upcoming = manager.get_upcoming_reminders(30)
        tva = next(r for r in upcoming if r["key"] == "tva_monthly")
        self.assertTrue(tva["acknowledged"])

    def test_upcoming_sorted_by_due_date(self):
        with _patched_now(2026, 1, 5), _isolated_manager() as (manager, _):
            upcoming = manager.get_upcoming_reminders(365)
        dates = [r["due_date"] for r in upcoming]
        self.assertEqual(dates, sorted(dates))


class TestCalculateNextDue(unittest.TestCase):

    def test_monthly_same_month(self):
        tax = ALGERIAN_TAX_CALENDAR["tva_monthly"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 10))
        self.assertEqual(result, datetime(2026, 1, 20))

    def test_monthly_next_month(self):
        tax = ALGERIAN_TAX_CALENDAR["tva_monthly"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 25))
        self.assertEqual(result, datetime(2026, 2, 20))

    def test_monthly_year_boundary(self):
        tax = ALGERIAN_TAX_CALENDAR["tva_monthly"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 12, 25))
        self.assertEqual(result, datetime(2027, 1, 20))

    def test_monthly_invalid_day_clamped_to_28(self):
        tax = ALGERIAN_TAX_CALENDAR["cnas_monthly"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 31))
        self.assertEqual(result, datetime(2026, 2, 28))

    def test_quarterly_first_upcoming(self):
        tax = ALGERIAN_TAX_CALENDAR["ibs_quarterly"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 1))
        self.assertEqual(result, datetime(2026, 3, 20))

    def test_quarterly_same_period(self):
        tax = ALGERIAN_TAX_CALENDAR["ibs_quarterly"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 3, 1))
        self.assertEqual(result, datetime(2026, 3, 20))

    def test_quarterly_rolls_to_next_year(self):
        tax = ALGERIAN_TAX_CALENDAR["ibs_quarterly"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 12, 31))
        self.assertEqual(result, datetime(2027, 3, 20))

    def test_quarterly_invalid_month_skipped(self):
        tax = {"frequency": "quarterly", "due_months": [2, 6], "due_day": 30}
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 1))
        self.assertEqual(result, datetime(2026, 6, 30))

    def test_quarterly_invalid_all_years_returns_none(self):
        tax = {"frequency": "quarterly", "due_months": [2], "due_day": 30}
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 3, 1))
        self.assertIsNone(result)

    def test_annual_current_year(self):
        tax = ALGERIAN_TAX_CALENDAR["irg_annual"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 1))
        self.assertEqual(result, datetime(2026, 2, 28))

    def test_annual_next_year(self):
        tax = ALGERIAN_TAX_CALENDAR["irg_annual"]
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 6, 1))
        self.assertEqual(result, datetime(2027, 2, 28))

    def test_annual_invalid_day_clamped_to_28(self):
        tax = {"frequency": "annual", "due_month": 2, "due_day": 31}
        result = TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 1))
        self.assertEqual(result, datetime(2027, 2, 28))

    def test_unknown_frequency_returns_none(self):
        tax = {"frequency": "weekly"}
        self.assertIsNone(TaxReminderManager()._calculate_next_due(tax, datetime(2026, 1, 1)))


class TestAcknowledgeAndCustomReminders(unittest.TestCase):

    def test_acknowledge_appends_and_saves(self):
        with _isolated_manager() as (manager, path):
            manager.acknowledge_reminder("tva_monthly_202601")
            self.assertEqual(manager.acknowledged, ["tva_monthly_202601"])
            self.assertTrue(os.path.exists(path))
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self.assertIn("tva_monthly_202601", saved["acknowledged"])

    def test_acknowledge_duplicate_ignored(self):
        with _isolated_manager() as (manager, path):
            manager.acknowledge_reminder("r1")
            manager.acknowledge_reminder("r1")
            self.assertEqual(manager.acknowledged, ["r1"])

    def test_add_custom_reminder_success(self):
        with _isolated_manager() as (manager, path):
            result = manager.add_custom_reminder(
                "Audit meeting", "2026-12-31", "desc", "Audit"
            )
            self.assertTrue(result)
            self.assertEqual(len(manager.custom_reminders), 1)
            self.assertEqual(manager.custom_reminders[0]["name"], "Audit meeting")
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(saved["custom"][0]["name"], "Audit meeting")

    def test_add_custom_reminder_save_failure_returns_false(self):
        with _isolated_manager() as (manager, path):
            with mock.patch.object(
                manager, "_save_reminders", side_effect=Exception("boom")
            ):
                result = manager.add_custom_reminder("X", "2026-12-31")
            self.assertFalse(result)

    def test_remove_custom_reminder_valid(self):
        with _isolated_manager() as (manager, path):
            manager.add_custom_reminder("A", "2026-12-31")
            manager.add_custom_reminder("B", "2026-12-31")
            self.assertTrue(manager.remove_custom_reminder(0))
            self.assertEqual(len(manager.custom_reminders), 1)
            self.assertEqual(manager.custom_reminders[0]["name"], "B")

    def test_remove_custom_reminder_invalid(self):
        with _isolated_manager() as (manager, path):
            self.assertFalse(manager.remove_custom_reminder(0))
            self.assertFalse(manager.remove_custom_reminder(-1))
            self.assertFalse(manager.remove_custom_reminder(99))


class TestCalendarSummary(unittest.TestCase):

    def test_summary_with_default_year(self):
        with _patched_now(2026, 6, 15), _isolated_manager() as (manager, _):
            cal = manager.get_calendar_summary()
        self.assertEqual(sorted(cal.keys()), list(range(1, 13)))
        self.assertTrue(cal[1])
        self.assertTrue(cal[3])
        self.assertTrue(cal[4])

    def test_summary_known_year_structure(self):
        with _isolated_manager() as (manager, _):
            cal = manager.get_calendar_summary(2026)
        self.assertEqual(len(cal), 12)
        self.assertTrue(cal[1])
        self.assertTrue(cal[3])
        self.assertTrue(cal[4])

    def test_summary_skips_invalid_days(self):
        # Note: the annual branch of get_calendar_summary never constructs a
        # datetime() inside its try block, so its except path is unreachable.
        fake_calendar = {
            "q_bad": {
                "name_ar": "q", "name_en": "Q", "frequency": "quarterly",
                "due_months": [6], "due_day": 31,
            },
        }
        with mock.patch.object(tax_reminders_mod, "ALGERIAN_TAX_CALENDAR", fake_calendar):
            with _isolated_manager() as (manager, _):
                cal = manager.get_calendar_summary(2026)
        self.assertEqual(cal[6], [])


if __name__ == "__main__":
    unittest.main()
