"""QA tests for unified UI spacing & layout standards (ui.constants)."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)


class TestUIConstants(unittest.TestCase):
    """Standards in ui.constants must exist and stay consistent."""

    def _c(self):
        from ui import constants as C
        return C

    def test_spacing_tiers_exist_and_ordered(self):
        C = self._c()
        self.assertLess(C.SPACING_TIGHT, C.SPACING_NORMAL)
        self.assertless_tuple = (
            C.SPACING_TIGHT < C.SPACING_NORMAL < C.SPACING_MEDIUM
            < C.SPACING_LARGE < C.SPACING_XLARGE
        )
        self.assertTrue(self.assertless_tuple)

    def test_margins_tiers_exist(self):
        C = self._c()
        self.assertTrue(all(v >= 5 for v in
                            (C.MARGIN_SMALL, C.MARGIN_NORMAL,
                             C.MARGIN_LARGE, C.MARGIN_XLARGE)))

    def test_min_heights_standard(self):
        C = self._c()
        self.assertEqual(C.MIN_HEIGHT_FIELD, 40)
        self.assertEqual(C.MIN_HEIGHT_BUTTON, 40)

    def test_page_standard_positive(self):
        C = self._c()
        self.assertEqual(C.PAGE_MARGINS, (20, 20, 20, 20))
        self.assertEqual(C.PAGE_SPACING, 15)

    def test_card_and_stat_standards(self):
        C = self._c()
        self.assertEqual(C.CARD_SPACING, 10)
        self.assertEqual(C.STAT_SPACING, 8)
        self.assertEqual(C.STAT_MARGINS, (16, 12, 16, 12))


class TestApplyStandardLayout(unittest.TestCase):
    """apply_standard_layout must set margins + spacing per level."""

    def _apply(self, level):
        from ui.constants import apply_standard_layout
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        apply_standard_layout(layout, level)
        return layout

    def test_page(self):
        from ui.constants import PAGE_MARGINS, PAGE_SPACING
        layout = self._apply("page")
        self.assertEqual(layout.spacing(), PAGE_SPACING)
        self.assertEqual(layout.getContentsMargins()[0:4], PAGE_MARGINS)

    def test_card(self):
        from ui.constants import CARD_MARGINS, CARD_SPACING
        layout = self._apply("card")
        self.assertEqual(layout.spacing(), CARD_SPACING)
        self.assertEqual(layout.getContentsMargins()[0:4], CARD_MARGINS)

    def test_stat(self):
        from ui.constants import STAT_MARGINS, STAT_SPACING
        layout = self._apply("stat")
        self.assertEqual(layout.spacing(), STAT_SPACING)
        self.assertEqual(layout.getContentsMargins()[0:4], STAT_MARGINS)

    def test_form(self):
        from ui.constants import FORM_MARGINS, FORM_SPACING
        layout = self._apply("form")
        self.assertEqual(layout.spacing(), FORM_SPACING)
        self.assertEqual(layout.getContentsMargins()[0:4], FORM_MARGINS)

    def test_unknown_level_falls_back_to_page(self):
        from ui.constants import PAGE_SPACING
        layout = self._apply("bogus")
        self.assertEqual(layout.spacing(), PAGE_SPACING)


class TestBaseViewStandard(unittest.TestCase):
    """BaseView must expose the unified page standard."""

    def test_main_layout_uses_page_standard(self):
        from ui.views._base import BaseView
        from ui.constants import PAGE_MARGINS, PAGE_SPACING
        view = BaseView()
        lyt = view.layout()
        self.assertEqual(lyt.spacing(), PAGE_SPACING)
        self.assertEqual(lyt.getContentsMargins()[0:4], PAGE_MARGINS)

    def test_make_stat_card_uses_stat_standard(self):
        from ui.views._base import BaseView
        from ui.constants import STAT_MARGINS, STAT_SPACING
        view = BaseView()
        card = view._make_stat_card("T", "1")
        lyt = card.layout()
        self.assertEqual(lyt.spacing(), STAT_SPACING)
        self.assertEqual(lyt.getContentsMargins()[0:4], STAT_MARGINS)


class TestViewSpacingMinimums(unittest.TestCase):
    """No view may use cramped spacing (< 5) outside scroll wrappers.

    Scroll-container wrappers use 0 spacing deliberately; those layouts are
    the direct children of the view widget and contain a QScrollArea.
    """

    def test_no_cramped_spacing_outside_scroll_wrappers(self):
        import ast
        import glob
        view_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "ui", "views")
        offenders = []
        for path in sorted(glob.glob(os.path.join(view_dir, "*_view.py"))) \
                + [os.path.join(view_dir, "data_entry.py"),
                   os.path.join(view_dir, "dashboard.py"),
                   os.path.join(view_dir, "login_view.py")]:
            name = os.path.basename(path)
            src = open(path, encoding="utf-8").read()
            tree = ast.parse(src)
            # لكل دالة: هل فيها QScrollArea؟ (نعم = غلاف تمرير مقصود)
            func_has_scroll = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_has_scroll[node.lineno] = any(
                        isinstance(c, ast.Attribute) and c.attr == "QScrollArea"
                        for c in ast.walk(node)
                    ) or any(
                        isinstance(c, ast.Name) and c.id == "QScrollArea"
                        for c in ast.walk(node)
                    )
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                if isinstance(fn, ast.Attribute) and fn.attr == "setSpacing" \
                        and node.args:
                    val = node.args[0]
                    if isinstance(val, ast.Constant) \
                            and isinstance(val.value, int):
                        v = val.value
                        if v < 5:
                            # هل الدالة المحيطة هي غلاف تمرير؟
                            enclosing = next(
                                (k for k in reversed(sorted(func_has_scroll))
                                 if k <= node.lineno), None)
                            if enclosing and func_has_scroll[enclosing]:
                                continue
                            offenders.append((name, v, node.lineno))
        self.assertEqual(offenders, [])


class TestBaseViewHeader(unittest.TestCase):
    """Header helpers must still build after _base refactor."""

    def setUp(self):
        from ui.views._base import BaseView
        self.view = BaseView()

    def test_make_header_title_added(self):
        self.view._make_header("data_entry_title")
        self.assertGreaterEqual(self.view._main_layout.count(), 1)

    def test_make_header_with_subtitle(self):
        self.view._make_header("data_entry_title", "data_entry_subtitle")
        self.assertGreaterEqual(self.view._main_layout.count(), 2)


if __name__ == "__main__":
    unittest.main()