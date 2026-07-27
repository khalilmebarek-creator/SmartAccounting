# اختبارات Utils - Validators
# ============================

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import InputValidator


class TestInputValidator(unittest.TestCase):
    """اختبارات التحقق من صحة المدخلات"""

    def test_validate_number_valid(self):
        valid, msg = InputValidator.validate_number(50)
        self.assertTrue(valid)

    def test_validate_number_with_min(self):
        valid, _ = InputValidator.validate_number(5, min_val=10)
        self.assertFalse(valid)

    def test_validate_number_with_max(self):
        valid, _ = InputValidator.validate_number(100, max_val=50)
        self.assertFalse(valid)

    def test_validate_number_in_range(self):
        valid, _ = InputValidator.validate_number(25, min_val=10, max_val=50)
        self.assertTrue(valid)

    def test_validate_number_non_numeric(self):
        valid, msg = InputValidator.validate_number("abc")
        self.assertFalse(valid)
        self.assertIn("رقمية", msg)

    def test_validate_number_none(self):
        valid, _ = InputValidator.validate_number(None)
        self.assertFalse(valid)

    def test_validate_non_negative_positive(self):
        valid, _ = InputValidator.validate_non_negative(100)
        self.assertTrue(valid)

    def test_validate_non_negative_zero(self):
        valid, _ = InputValidator.validate_non_negative(0)
        self.assertTrue(valid)

    def test_validate_non_negative_negative(self):
        valid, msg = InputValidator.validate_non_negative(-5)
        self.assertFalse(valid)
        self.assertIn("سالبة", msg)

    def test_validate_positive_positive(self):
        valid, _ = InputValidator.validate_positive(100)
        self.assertTrue(valid)

    def test_validate_positive_zero(self):
        valid, _ = InputValidator.validate_positive(0)
        self.assertFalse(valid)

    def test_validate_positive_negative(self):
        valid, _ = InputValidator.validate_positive(-1)
        self.assertFalse(valid)

    def test_validate_text_valid(self):
        valid, _ = InputValidator.validate_text("مرحبا")
        self.assertTrue(valid)

    def test_validate_text_empty(self):
        valid, _ = InputValidator.validate_text("")
        self.assertFalse(valid)

    def test_validate_text_too_long(self):
        valid, _ = InputValidator.validate_text("a" * 201, max_length=200)
        self.assertFalse(valid)

    def test_validate_text_not_string(self):
        valid, _ = InputValidator.validate_text(123)
        self.assertFalse(valid)

    def test_validate_year_valid(self):
        valid, _ = InputValidator.validate_year(2024)
        self.assertTrue(valid)

    def test_validate_year_too_old(self):
        valid, _ = InputValidator.validate_year(1999)
        self.assertFalse(valid)

    def test_validate_year_too_future(self):
        valid, _ = InputValidator.validate_year(2101)
        self.assertFalse(valid)

    def test_validate_year_non_numeric(self):
        valid, _ = InputValidator.validate_year("abc")
        self.assertFalse(valid)

    def test_validate_balance_sheet_balanced(self):
        valid, _ = InputValidator.validate_balance_sheet(500000, 200000, 300000)
        self.assertTrue(valid)

    def test_validate_balance_sheet_unbalanced(self):
        valid, msg = InputValidator.validate_balance_sheet(500000, 200000, 200000)
        self.assertFalse(valid)
        self.assertIn("غير متوازنة", msg)

    def test_validate_balance_sheet_non_numeric(self):
        valid, _ = InputValidator.validate_balance_sheet("abc", 0, 0)
        self.assertFalse(valid)


if __name__ == '__main__':
    unittest.main()
