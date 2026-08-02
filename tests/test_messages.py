"""Tests for the unified error-message helpers (ui/widgets/messages.py)."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.widgets.messages import build_error_text
from ui.resources.i18n import Translator


class TestBuildErrorText(unittest.TestCase):
    """Pure text builder used by the GUI message wrappers."""

    def setUp(self):
        Translator.set_language("en")

    def test_plain_message(self):
        text = build_error_text("Something failed")
        self.assertEqual(text, "Something failed")

    def test_message_with_exception(self):
        text = build_error_text("Could not export", exc=ValueError("bad file"))
        self.assertIn("Could not export", text)
        self.assertIn("bad file", text)

    def test_message_with_detail(self):
        text = build_error_text("Could not print", detail="Printer not connected")
        self.assertIn("Printer not connected", text)

    def test_message_with_hint_includes_translated_suggestion(self):
        text = build_error_text("Export failed", hint_key="hint_export_failed")
        self.assertIn("Suggested action", text)
        self.assertIn(Translator.t("hint_export_failed"), text)

    def test_hint_uses_current_language(self):
        Translator.set_language("ar")
        text = build_error_text("Export failed", hint_key="hint_export_failed")
        self.assertIn(Translator.t("err_suggestion"), text)

    def test_empty_hint_key_is_omitted(self):
        text = build_error_text("Failed", hint_key="")
        self.assertNotIn("Suggested action", text)
        self.assertEqual(text, "Failed")

    def test_all_components_combined(self):
        text = build_error_text(
            "Operation failed",
            hint_key="hint_print_failed",
            exc=OSError(2, "no such file"),
            detail="extra detail",
        )
        self.assertIn("Operation failed", text)
        self.assertIn("extra detail", text)
        self.assertIn("no such file", text)
        self.assertIn("Suggested action", text)
        self.assertIn(Translator.t("hint_print_failed"), text)

    def test_unknown_hint_key_returns_key_itself(self):
        text = build_error_text("Failed", hint_key="hint_missing_key_xyz")
        self.assertIn("hint_missing_key_xyz", text)


if __name__ == "__main__":
    unittest.main()
