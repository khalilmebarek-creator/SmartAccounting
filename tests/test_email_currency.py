# Unit tests for modules/email_notifier.py and modules/currency.py.
# Covers the send_alert/send_summary/_send HTML+SMTP paths of EmailNotifier
# and the edge branches of the CurrencyEngine (base change, add/set rate,
# conversions, naming and formatting).

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modules.email_notifier as email_notifier_mod
from modules.email_notifier import EmailNotifier, MAX_RETRIES, RETRY_DELAY
from modules.currency import CurrencyEngine


class TestEmailNotifierSend(unittest.TestCase):
    """Tests for the HTML-building and SMTP sending paths."""

    def _configured(self):
        notifier = EmailNotifier()
        notifier.smtp_server = "smtp.test.com"
        notifier.smtp_port = 587
        notifier.sender_email = "from@test.com"
        notifier.sender_password = "ENC:secret"
        notifier.manager_email = "to@test.com"
        notifier.enabled = True
        return notifier

    def test_send_alert_builds_html_and_calls_send(self):
        notifier = self._configured()
        alert = {
            "severity": "high",
            "time": "2026-08-01 10:00",
            "rule": "big_jump",
            "field": "revenue",
            "detail": "Revenue jumped 400%",
            "old_value": 100,
            "new_value": 500,
            "user": "admin",
        }
        with mock.patch.object(notifier, "_send",
                               return_value=(True, "Email sent successfully")) as send_mock:
            result, msg = notifier.send_alert(alert)
        self.assertTrue(result)
        self.assertEqual(msg, "Email sent successfully")
        subject, html = send_mock.call_args[0]
        self.assertIn("HIGH", subject)
        self.assertIn("big_jump", html)
        self.assertIn("Revenue jumped 400%", html)
        self.assertIn("admin", html)

    def test_send_alert_default_low_severity_and_unknown_keys(self):
        notifier = self._configured()
        with mock.patch.object(notifier, "_send",
                               return_value=(True, "ok")) as send_mock:
            result, _ = notifier.send_alert({})
        self.assertTrue(result)
        subject, html = send_mock.call_args[0]
        self.assertIn("LOW", subject)
        self.assertIn("N/A", html)

    def test_send_alert_medium_severity_label(self):
        notifier = self._configured()
        with mock.patch.object(notifier, "_send",
                               return_value=(True, "ok")) as send_mock:
            notifier.send_alert({"severity": "medium"})
        subject, _ = send_mock.call_args[0]
        self.assertIn("MEDIUM", subject)

    def test_send_alert_unknown_severity_info(self):
        notifier = self._configured()
        with mock.patch.object(notifier, "_send",
                               return_value=(True, "ok")) as send_mock:
            notifier.send_alert({"severity": "info"})
        subject, _ = send_mock.call_args[0]
        self.assertIn("INFO", subject)

    def test_send_summary_with_high_alerts(self):
        notifier = self._configured()
        alerts = [
            {"time": f"t{i}", "rule": f"r{i}", "field": f"f{i}", "detail": f"d{i}"}
            for i in range(12)
        ]
        with mock.patch.object(notifier, "_send",
                               return_value=(True, "ok")) as send_mock:
            result, _ = notifier.send_summary(
                {"total": 12, "high": 3, "medium": 4, "low": 5}, alerts
            )
        self.assertTrue(result)
        subject, html = send_mock.call_args[0]
        self.assertIn("Security Summary", subject)
        # only the last 10 high-severity alerts make it into the table
        self.assertIn("r2", html)
        self.assertNotIn("r0", html)

    def test_send_summary_without_high_alerts(self):
        notifier = self._configured()
        with mock.patch.object(notifier, "_send",
                               return_value=(True, "ok")) as send_mock:
            result, _ = notifier.send_summary({}, [])
        self.assertTrue(result)
        _, html = send_mock.call_args[0]
        self.assertIn("No high-severity alerts", html)

    def test_send_success_path(self):
        notifier = self._configured()
        server = mock.MagicMock()
        server.__enter__.return_value = server
        with mock.patch.object(email_notifier_mod, "decrypt",
                               return_value="plain-pass"), \
             mock.patch.object(email_notifier_mod.smtplib, "SMTP",
                               return_value=server) as smtp_cls:
            result, msg = notifier._send("Subject", "<html></html>")
        self.assertTrue(result)
        self.assertEqual(msg, "Email sent successfully")
        smtp_cls.assert_called_once_with("smtp.test.com", 587, timeout=15)
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("from@test.com", "plain-pass")
        server.sendmail.assert_called_once()

    def test_send_retries_then_fails(self):
        notifier = self._configured()
        with mock.patch.object(email_notifier_mod, "decrypt",
                               return_value="plain-pass"), \
             mock.patch.object(email_notifier_mod.smtplib, "SMTP",
                               side_effect=Exception("connection refused")), \
             mock.patch.object(email_notifier_mod.time, "sleep") as sleep_mock:
            result, msg = notifier._send("Subject", "<html></html>")
        self.assertFalse(result)
        self.assertIn("Failed after", msg)
        self.assertIn(str(MAX_RETRIES), msg)
        self.assertEqual(sleep_mock.call_count, MAX_RETRIES - 1)
        self.assertEqual(sleep_mock.call_args_list[0], mock.call(RETRY_DELAY * 1))
        self.assertEqual(sleep_mock.call_args_list[1], mock.call(RETRY_DELAY * 2))

    def test_send_alert_not_configured(self):
        notifier = EmailNotifier()
        result, msg = notifier.send_alert({"severity": "high"})
        self.assertFalse(result)
        self.assertIn("not configured", msg.lower())

    def test_send_summary_not_configured(self):
        notifier = EmailNotifier()
        result, msg = notifier.send_summary({}, [])
        self.assertFalse(result)
        self.assertIn("not configured", msg.lower())

    def test_configure_encrypts_password(self):
        notifier = EmailNotifier()
        with mock.patch.object(email_notifier_mod, "encrypt",
                               return_value="ENC:secret") as enc_mock:
            notifier.configure("smtp.gmail.com", "587", "a@b.c", "pw", "m@b.c")
        enc_mock.assert_called_once_with("pw")
        self.assertTrue(notifier.is_configured())
        self.assertEqual(notifier.smtp_port, 587)


class TestCurrencyEngineUncovered(unittest.TestCase):
    """Tests for edge branches of the CurrencyEngine."""

    def setUp(self):
        self.engine = CurrencyEngine(base_currency="DZD")
        self.engine.set_rate("USD", 134.0)

    def test_set_base_unknown_currency_returns_false(self):
        self.assertFalse(self.engine.set_base_currency("ZZZ"))

    def test_set_base_same_currency_returns_true(self):
        self.assertTrue(self.engine.set_base_currency("DZD"))

    def test_set_base_currency_with_non_positive_rate_returns_false(self):
        self.engine.rates["USD"] = -1.0
        self.assertFalse(self.engine.set_base_currency("USD"))

    def test_add_currency_empty_code_returns_false(self):
        self.assertFalse(self.engine.add_currency(""))
        self.assertFalse(self.engine.add_currency(None))

    def test_add_currency_without_rate_sets_default_one(self):
        self.assertTrue(self.engine.add_currency("GBP", "جنيه إسترليني", "£"))
        self.assertEqual(self.engine.get_rate("GBP"), 1.0)

    def test_add_currency_keeps_existing_meta_when_partial(self):
        self.assertTrue(self.engine.add_currency("USD", None, None, 150.0))
        self.assertEqual(self.engine.get_rate("USD"), 150.0)
        self.assertEqual(self.engine.currencies["USD"]["name_en"], "US Dollar")

    def test_set_rate_unknown_currency_returns_false(self):
        self.assertFalse(self.engine.set_rate("XYZ", 5.0))

    def test_set_rate_non_numeric_returns_false(self):
        self.assertFalse(self.engine.set_rate("USD", "abc"))
        self.assertEqual(self.engine.get_rate("USD"), 134.0)

    def test_convert_to_base_non_numeric_amount_returns_zero(self):
        self.assertEqual(self.engine.convert_to_base("abc", "USD"), 0.0)
        self.assertEqual(self.engine.convert_to_base(None, "USD"), 0.0)

    def test_convert_from_base_zero_rate_returns_zero(self):
        self.assertEqual(self.engine.convert_from_base(100, "XYZ"), 0.0)

    def test_convert_from_base_non_numeric_amount_returns_zero(self):
        self.assertEqual(self.engine.convert_from_base("abc", "USD"), 0.0)

    def test_name_default_language_ar(self):
        self.assertEqual(self.engine.name(), "دينار جزائري")

    def test_name_english_language(self):
        self.assertEqual(self.engine.name("USD", "en"), "US Dollar")

    def test_name_non_ar_lang_falls_back_to_en(self):
        self.assertEqual(self.engine.name("USD", "fr"), "US Dollar")

    def test_name_unknown_currency_returns_code(self):
        self.assertEqual(self.engine.name("ZZZ"), "ZZZ")

    def test_name_lowercase_code_normalized(self):
        self.assertEqual(self.engine.name("usd"), "دولار أمريكي")

    def test_format_invalid_amount_returns_zero_string(self):
        self.assertEqual(self.engine.format("abc", "USD"), "0.00 $")

    def test_format_none_amount_returns_zero_string(self):
        self.assertEqual(self.engine.format(None, "DZD"), "0.00 دج")

    def test_format_unknown_code_uses_code_as_symbol(self):
        self.assertEqual(self.engine.format(100, "ZZZ"), "100.00 ZZZ")

    def test_format_decimals_option(self):
        self.assertEqual(self.engine.format(1234.6, "DZD", decimals=0), "1,235 دج")

    def test_remove_currency_unknown_returns_false(self):
        self.assertFalse(self.engine.remove_currency("XYZ"))

    def test_remove_currency_success(self):
        self.engine.add_currency("GBP", "جنيه إسترليني", "£", 180.0)
        self.assertTrue(self.engine.remove_currency("GBP"))
        self.assertNotIn("GBP", self.engine.supported_currencies())

    def test_set_rate_non_positive_returns_false(self):
        self.assertFalse(self.engine.set_rate("USD", 0))
        self.assertFalse(self.engine.set_rate("USD", -3))

    def test_set_base_currency_normalizes_rates(self):
        engine = CurrencyEngine(base_currency="DZD")
        engine.set_rate("USD", 134.0)
        engine.set_rate("EUR", 156.0)
        self.assertTrue(engine.set_base_currency("USD"))
        self.assertEqual(engine.base_currency, "USD")
        self.assertEqual(engine.get_rate("USD"), 1.0)
        self.assertAlmostEqual(engine.get_rate("DZD"), 1.0 / 134.0)
        self.assertAlmostEqual(engine.get_rate("EUR"), 156.0 / 134.0)

    def test_convert_to_base_zero_rate_returns_zero(self):
        self.assertEqual(self.engine.convert_to_base(100, "XYZ"), 0.0)

    def test_convert_same_code(self):
        self.assertEqual(self.engine.convert(50, "USD", "USD"), 50.0)
        self.assertEqual(self.engine.convert(None, "USD", "USD"), 0.0)

    def test_convert_cross_currency(self):
        self.engine.set_rate("EUR", 156.0)
        self.assertAlmostEqual(
            self.engine.convert(100, "USD", "EUR"), 100 * 134.0 / 156.0
        )

    def test_to_dict(self):
        data = self.engine.to_dict()
        self.assertEqual(data["base_currency"], "DZD")
        self.assertIn("USD", data["rates"])
        self.assertIn("USD", data["currencies"])

    def test_load_from_dict_full(self):
        data = {
            "base_currency": "USD",
            "currencies": {"USD": {"name_ar": "دولار", "name_en": "US Dollar", "symbol": "$"}},
            "rates": {"USD": 1.0, "DZD": 1.0 / 134.0},
        }
        engine = CurrencyEngine()
        self.assertTrue(engine.load_from_dict(data))
        self.assertEqual(engine.base_currency, "USD")
        self.assertEqual(engine.get_rate("DZD"), 1.0 / 134.0)

    def test_load_from_dict_empty(self):
        engine = CurrencyEngine()
        self.assertTrue(engine.load_from_dict(None))
        self.assertEqual(engine.base_currency, "DZD")
        self.assertEqual(engine.get_rate("DZD"), 1.0)

    def test_supported_currencies(self):
        codes = self.engine.supported_currencies()
        self.assertIn("DZD", codes)
        self.assertIn("USD", codes)

    def test_report_default_target_is_base(self):
        rows = self.engine.report({"revenue": 1000})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["currency"], "DZD")
        self.assertEqual(rows[0]["converted"], 1000.0)

    def test_report_with_target_and_none_item(self):
        financial = {"revenue": 1000, "cost_of_goods_sold": 0, "net_income": None}
        rows = self.engine.report(financial, target_currency="USD")
        by_item = {r["item"]: r for r in rows}
        self.assertAlmostEqual(by_item["revenue"]["converted"], 1000 / 134.0)
        self.assertEqual(by_item["cost_of_goods_sold"]["converted"], 0.0)
        self.assertEqual(by_item["net_income"]["converted"], 0.0)


if __name__ == "__main__":
    unittest.main()
