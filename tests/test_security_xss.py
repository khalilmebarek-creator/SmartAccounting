"""Security regression tests: HTML output must neutralize XSS payloads."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from modules.print_manager import PrintManager


class TestPrintManagerXSS(unittest.TestCase):

    def setUp(self):
        self.manager = PrintManager()

    def test_company_name_escaped(self):
        html = self.manager.generate_report_html(
            "Report",
            sections=[{"title": "S1", "rows": [["a", "b"]]}],
            company_name='<script>alert(1)</script>',
            fiscal_year="2024",
        )
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_title_escaped(self):
        html = self.manager.generate_report_html(
            '<img src=x onerror=alert(1)>',
            sections=[{"title": "S1", "rows": [["a", "b"]]}],
        )
        self.assertNotIn('<img src=x onerror=alert(1)>', html)
        self.assertIn('&lt;img', html)

    def test_section_title_and_cells_escaped(self):
        html = self.manager.generate_report_html(
            "R",
            sections=[{
                "title": '<b onmouseover=alert(2)>T</b>',
                "rows": [["<iframe src=evil>", 5]],
            }],
        )
        self.assertNotIn('<iframe src=evil>', html)
        self.assertNotIn('<b onmouseover=alert(2)>', html)
        self.assertIn('&lt;iframe', html)

    def test_section_content_escaped(self):
        html = self.manager.generate_report_html(
            "R",
            sections=[{"title": "S", "content": "<script>steal()</script>"}],
        )
        self.assertNotIn('<script>steal()</script>', html)
        self.assertIn('&lt;script&gt;', html)


if __name__ == "__main__":
    unittest.main()
