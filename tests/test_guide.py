"""Tests for the interactive user guide (Help menu feature)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from ui.resources.i18n import t, Translator
from ui.views.guide_view import GuideDialog


class TestGuideDialog(unittest.TestCase):

    def setUp(self):
        Translator.set_language("ar")

    def test_dialog_builds_with_7_tabs(self):
        dlg = GuideDialog()
        self.assertEqual(dlg.tabs.count(), 7)
        dlg.close()

    def test_tabs_have_titles_in_all_languages(self):
        for lang in ("ar", "en", "fr"):
            Translator.set_language(lang)
            dlg = GuideDialog()
            for i in range(dlg.tabs.count()):
                self.assertTrue(
                    dlg.tabs.tabText(i).strip(),
                    f"tab {i} empty in {lang}")
            dlg.close()

    def test_content_has_no_source_code_or_architecture(self):
        """مطلب المستخدم: الدليل لا يعرض الكود ولا بنية المشروع."""
        forbidden = (
            ".py", "def ", "class ", "import ", "lib/", "modules/",
            "ui/views", "Nuitka", "QWidget", "PyQt",
        )
        dlg = GuideDialog()
        for i in range(dlg.tabs.count()):
            page = dlg.tabs.widget(i)
            text = page.toPlainText().lower()
            for word in forbidden:
                self.assertNotIn(word.lower(), text,
                                 f"tab {i} leaks {word}")
        dlg.close()

    def test_content_mentions_user_facing_features(self):
        dlg = GuideDialog()
        page1 = dlg.tabs.widget(0).toPlainText()
        self.assertIn("المنصة", page1)
        page4 = dlg.tabs.widget(3).toPlainText()
        self.assertIn("IBS", page4)
        dlg.close()

    def test_navigation_buttons(self):
        dlg = GuideDialog()
        dlg.show()
        self.assertFalse(dlg.prev_btn.isEnabled())
        self.assertTrue(dlg.next_btn.isEnabled())
        dlg._go_next()
        self.assertEqual(dlg.tabs.currentIndex(), 1)
        self.assertTrue(dlg.prev_btn.isEnabled())
        dlg._go_prev()
        self.assertEqual(dlg.tabs.currentIndex(), 0)
        dlg.close()

    def test_last_tab_disables_next(self):
        dlg = GuideDialog()
        dlg.tabs.setCurrentIndex(6)
        dlg._update_nav()
        self.assertFalse(dlg.next_btn.isEnabled())
        self.assertTrue(dlg.prev_btn.isEnabled())
        dlg.close()


if __name__ == "__main__":
    unittest.main()
