# اختبارات إصدارات النظام الجبائي السنوية (2025/2026) + النظم الجديدة
# ==================================================================
# TDD: اختبارات جديدة لميزة "تحديث النظام الجبائي السنوي"

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import tax_years
from modules.tax import TaxEngine


class TestYearListing(unittest.TestCase):

    def test_list_years_contains_2025_2026(self):
        years = tax_years.list_years()
        self.assertIn(2025, years)
        self.assertIn(2026, years)
        self.assertEqual(years, sorted(years))

    def test_year_filename_and_path(self):
        self.assertEqual(tax_years.year_filename(2026), "tax_config_2026.json")
        self.assertTrue(tax_years.year_path(2026).endswith(
            os.path.join("config_years", "tax_config_2026.json")))

    def test_load_year_2026(self):
        data = tax_years.load_year(2026)
        self.assertIsNotNone(data)
        self.assertEqual(data["year"], 2026)

    def test_load_year_missing_returns_none(self):
        self.assertIsNone(tax_years.load_year(1999))

    def test_load_year_sets_year_field(self):
        data = tax_years.load_year(2025)
        self.assertEqual(data["year"], 2025)


class TestYearCrud(unittest.TestCase):

    def setUp(self):
        self._orig_dir = tax_years.YEARS_DIR
        # نسخ سنة مرجعية قبل تبديل المجلد
        data = tax_years.load_year(2026)
        self.tmp = tempfile.mkdtemp()
        tax_years.YEARS_DIR = self.tmp
        if data is not None:
            with open(os.path.join(self.tmp, "tax_config_2026.json"),
                      "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    def tearDown(self):
        tax_years.YEARS_DIR = self._orig_dir
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_save_and_load_roundtrip(self):
        cfg = {"country": "Algeria", "ibs": {"rates": {"production": 0.19}},
               "irg": {"brackets": []}}
        self.assertTrue(tax_years.save_year(2030, cfg))
        loaded = tax_years.load_year(2030)
        self.assertEqual(loaded["year"], 2030)
        self.assertEqual(loaded["ibs"]["rates"]["production"], 0.19)

    def test_copy_year(self):
        self.assertTrue(tax_years.copy_year(2026, 2027))
        copied = tax_years.load_year(2027)
        self.assertIsNotNone(copied)
        self.assertEqual(copied["year"], 2027)
        self.assertEqual(copied["ibs"]["rates"]["production"], 0.19)

    def test_copy_year_from_missing_src_fails(self):
        self.assertFalse(tax_years.copy_year(1999, 2027))

    def test_delete_year(self):
        tax_years.save_year(2031, {"country": "Algeria"})
        self.assertTrue(tax_years.delete_year(2031))
        self.assertFalse(tax_years.delete_year(2031))
        self.assertIsNone(tax_years.load_year(2031))

    def test_save_invalid_year_returns_false(self):
        self.assertFalse(tax_years.save_year("abc", {"country": "Algeria"}))


class TestYearValidation(unittest.TestCase):

    def test_valid_2026_passes(self):
        data = tax_years.load_year(2026)
        self.assertEqual(tax_years.validate_year_config(data), [])

    def test_missing_keys(self):
        errors = tax_years.validate_year_config({"country": "Algeria"})
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(any("missing key" in e for e in errors))

    def test_invalid_irg_rate(self):
        data = tax_years.load_year(2026)
        data["irg"]["brackets"][0]["rate"] = 1.9
        errors = tax_years.validate_year_config(data)
        self.assertTrue(any("irg rate" in e for e in errors))

    def test_irg_brackets_not_increasing(self):
        data = tax_years.load_year(2026)
        data["irg"]["brackets"] = [
            {"min": 100000, "max": 200000, "rate": 0.3},
            {"min": 50000, "max": 100000, "rate": 0.2},
        ]
        errors = tax_years.validate_year_config(data)
        self.assertTrue(any("increasing" in e for e in errors))

    def test_invalid_tva_rate(self):
        data = tax_years.load_year(2025)
        data["tva"]["rates"]["standard"] = 2.0
        errors = tax_years.validate_year_config(data)
        self.assertTrue(any("tva.rates.standard" in e for e in errors))


class TestYearJsonImportExport(unittest.TestCase):

    def setUp(self):
        self._orig_dir = tax_years.YEARS_DIR
        data = tax_years.load_year(2026)
        self.tmp = tempfile.mkdtemp()
        tax_years.YEARS_DIR = self.tmp
        if data is not None:
            with open(os.path.join(self.tmp, "tax_config_2026.json"),
                      "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    def tearDown(self):
        tax_years.YEARS_DIR = self._orig_dir
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_export_2026(self):
        text = tax_years.export_year_to_json(2026)
        self.assertIsNotNone(text)
        data = json.loads(text)
        self.assertEqual(data["year"], 2026)

    def test_export_missing_returns_none(self):
        self.assertIsNone(tax_years.export_year_to_json(1999))

    def test_import_valid_json(self):
        text = tax_years.export_year_to_json(2026)
        data, errors = tax_years.import_year_from_json(text, year=2027)
        self.assertEqual(errors, [])
        self.assertEqual(data["year"], 2027)

    def test_import_invalid_json(self):
        data, errors = tax_years.import_year_from_json("{not json")
        self.assertIsNone(data)
        self.assertTrue(any("invalid JSON" in e for e in errors))

    def test_import_invalid_schema(self):
        data, errors = tax_years.import_year_from_json("{\"year\": 2027}")
        self.assertIsNone(data)
        self.assertTrue(any("missing" in e for e in errors))

    def test_import_valid_then_save(self):
        text = tax_years.export_year_to_json(2026)
        data, errors = tax_years.import_year_from_json(text, year=2028)
        self.assertEqual(errors, [])
        self.assertTrue(tax_years.save_year(2028, data))
        self.assertIsNotNone(tax_years.load_year(2028))


class TestTaxEngineYearSelection(unittest.TestCase):

    def test_init_with_year_2026(self):
        engine = TaxEngine(year=2026)
        self.assertEqual(engine.get_config_year(), 2026)
        # الشرائح الجديدة من نشرة 2026
        brackets = engine.config["irg"]["brackets"]
        self.assertEqual(brackets[0]["max"], 240000)
        self.assertEqual(brackets[1]["rate"], 0.23)
        self.assertEqual(brackets[-1]["rate"], 0.35)

    def test_init_with_missing_year_falls_back(self):
        engine = TaxEngine(year=1999)
        self.assertEqual(engine.get_config_year(), 2025)

    def test_set_year(self):
        engine = TaxEngine()
        self.assertTrue(engine.set_year(2026))
        self.assertEqual(engine.get_config_year(), 2026)

    def test_set_year_missing_returns_false(self):
        engine = TaxEngine()
        self.assertFalse(engine.set_year(1999))

    def test_list_years_from_engine(self):
        engine = TaxEngine()
        self.assertIn(2025, engine.list_years())
        self.assertIn(2026, engine.list_years())


class TestIRG2026Brackets(unittest.TestCase):

    def setUp(self):
        self.engine = TaxEngine(year=2026)

    def test_below_threshold_exempt(self):
        result = self.engine.calculate_irg(200000)
        self.assertEqual(result["irg_amount"], 0)
        self.assertEqual(result["marginal_rate"], 0.0)

    def test_second_bracket_23(self):
        result = self.engine.calculate_irg(400000)
        self.assertGreater(result["irg_amount"], 0)
        self.assertEqual(result["marginal_rate"], 0.23)

    def test_high_bracket_35(self):
        result = self.engine.calculate_irg(5000000)
        self.assertEqual(result["marginal_rate"], 0.35)


class TestIFU(unittest.TestCase):

    def setUp(self):
        self.engine = TaxEngine(year=2026)

    def test_auto_regime_rate(self):
        result = self.engine.calculate_ifu(1000000, "auto")
        # 1,000,000 * 0.5% = 5,000 < 10,000 الحد الأدنى
        self.assertEqual(result["rate"], 0.005)
        self.assertEqual(result["tax_amount"], 10000)
        self.assertTrue(result["minimum_applied"])

    def test_production_rate(self):
        result = self.engine.calculate_ifu(1000000, "production")
        self.assertEqual(result["rate"], 0.05)
        self.assertEqual(result["tax_amount"], 50000)

    def test_other_rate(self):
        result = self.engine.calculate_ifu(1000000, "other")
        self.assertEqual(result["rate"], 0.12)
        self.assertEqual(result["tax_amount"], 120000)

    def test_default_other(self):
        result = self.engine.calculate_ifu(1000000)
        self.assertEqual(result["regime"], "other")

    def test_zero_turnover_minimum(self):
        result = self.engine.calculate_ifu(0, "production")
        self.assertEqual(result["tax_amount"], 30000)
        self.assertTrue(result["minimum_applied"])

    def test_negative_turnover_minimum(self):
        result = self.engine.calculate_ifu(-5, "other")
        self.assertEqual(result["tax_amount"], 30000)


class TestFormationTax(unittest.TestCase):

    def setUp(self):
        self.engine = TaxEngine(year=2026)

    def test_default_no_credit(self):
        result = self.engine.calculate_formation_tax(1000000)
        # 1% لكل رسم = 10,000 + 10,000
        self.assertEqual(result["formation_amount"], 10000)
        self.assertEqual(result["apprenticeship_amount"], 10000)
        self.assertEqual(result["total"], 20000)
        self.assertEqual(result["rate"], 0.01)

    def test_credit_reduces(self):
        result = self.engine.calculate_formation_tax(1000000, 4000, 6000)
        self.assertEqual(result["formation_amount"], 6000)
        self.assertEqual(result["apprenticeship_amount"], 4000)

    def test_over_budget_returns_zero(self):
        result = self.engine.calculate_formation_tax(10000, 5000, 5000)
        # 10000 * 1% = 100، الميزانية تفوق المستحق
        self.assertEqual(result["formation_amount"], 0)
        self.assertEqual(result["apprenticeship_amount"], 0)


class TestRentalWithholding(unittest.TestCase):

    def setUp(self):
        self.engine = TaxEngine(year=2026)

    def test_residential(self):
        result = self.engine.calculate_rental_withholding(100000, "residential")
        self.assertEqual(result["withholding_amount"], 7000)
        self.assertEqual(result["rate"], 0.07)
        self.assertFalse(result["provisional"])

    def test_commercial(self):
        result = self.engine.calculate_rental_withholding(100000, "commercial")
        self.assertEqual(result["withholding_amount"], 15000)
        self.assertEqual(result["rate"], 0.15)

    def test_above_threshold_provisional(self):
        result = self.engine.calculate_rental_withholding(2000000, "commercial")
        self.assertTrue(result["provisional"])
        self.assertEqual(result["rate"], 0.07)

    def test_default_residential(self):
        result = self.engine.calculate_rental_withholding(100000)
        self.assertEqual(result["rate"], 0.07)


class TestEngineBackwardsCompatible(unittest.TestCase):

    def test_default_year_still_2025(self):
        engine = TaxEngine()
        self.assertEqual(engine.get_config_year(), 2025)
        # الشرائح القديمة لا تزال تعمل (لا كسر للتطبيق الحالي)
        result = engine.calculate_irg(100000)
        self.assertEqual(result["irg_amount"], 0)

    def test_ibes_rate_preserved(self):
        engine = TaxEngine()
        result = engine.calculate_ibs(10000000, "production")
        self.assertEqual(result["rate_used"], 0.19)

    def test_tva_standard_preserved(self):
        engine = TaxEngine()
        result = engine.calculate_tva(1000000, "standard")
        self.assertEqual(result["tva_amount"], 190000)

    def test_legacy_config_missing_new_sections_gets_defaults(self):
        """ملف سنة قديم بلا أقسام جديدة: تُدمج الأقسام من الافتراضية"""
        with tempfile.TemporaryDirectory() as tmp:
            old = {
                "year": 2019,
                "ibs": {"rates": {"production": 0.19}, "minimum_tax": 10000},
                "tva": {"rates": {"standard": 0.19, "reduced": 0.09, "zero": 0.0}},
                "irg": {"brackets": [
                    {"min": 0, "max": None, "rate": 0.20}
                ]},
                "cnas": {"employer": {"total": 0.245}, "employee": {"total": 0.09}},
                "cnac": {"employer_rate": 0.015, "employee_rate": 0.005},
                "versement_forfaitaire": {"standard_rate": 0.02, "construction_rate": 0.01},
                "activity_types": ["commerce"],
            }
            path = os.path.join(tmp, "tax_config_old.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(old, f, ensure_ascii=False)
            engine = TaxEngine(config_path=path)
            # الأقسام الجديدة مهيأة بالافتراضية رغم غيابها من الملف القديم
            self.assertIn("ifu", engine.config)
            self.assertEqual(engine.config["ifu"]["rates"]["auto"], 0.005)
            self.assertIn("formation_tax", engine.config)
            self.assertIn("rental_withholding", engine.config)
            self.assertEqual(engine.config["rental_withholding"]["rates"]["commercial"], 0.15)
            # والقيم الموجودة في الملف القديم محفوظة (override)
            self.assertEqual(engine.get_config_year(), 2019)
            self.assertEqual(engine.calculate_irg(100000)["irg_amount"], 20000.2)
            # الحاسبة الجديدة تعمل مباشرة
            ifu = engine.calculate_ifu(1000000, "auto")
            self.assertEqual(ifu["rate"], 0.005)


if __name__ == "__main__":
    unittest.main()