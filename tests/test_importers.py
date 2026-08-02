# Unit tests for modules/data_import.py and modules/csv_import.py.
# Covers Excel/CSV import paths, error branches, validation summaries,
# database export error handling, and the advanced CSV importer
# (delimiter/file-type detection, encodings, mapping, row processing).

import builtins
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_import import DataImporter
from modules.csv_import import CSVImporter
import modules.data_import as data_import_mod


class TestDataImporterUncovered(unittest.TestCase):
    """Tests for the Excel import, summary and export error paths."""

    def setUp(self):
        self.importer = DataImporter()

    def _set_data(self):
        self.importer.data = pd.DataFrame([{
            "total_assets": 500000,
            "total_liabilities": 200000,
            "equity": 300000,
            "revenue": 200000,
            "net_income": 15000,
        }])

    def test_import_from_excel_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "book.xlsx")
            pd.DataFrame({"name": ["a"], "value": [1.0]}).to_excel(path, index=False)
            result = self.importer.import_from_excel(path)
            self.assertTrue(result)
            self.assertEqual(len(self.importer.get_data()), 1)

    def test_import_from_excel_file_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.importer.import_from_excel(
                os.path.join(tmp, "missing.xlsx")
            )
            self.assertFalse(result)

    def test_import_from_excel_generic_error(self):
        with mock.patch.object(data_import_mod.pd, "read_excel",
                               side_effect=ValueError("corrupt file")):
            result = self.importer.import_from_excel("whatever.xlsx")
            self.assertFalse(result)

    def test_import_from_csv_generic_error(self):
        with mock.patch.object(data_import_mod.pd, "read_csv",
                               side_effect=ValueError("corrupt csv")):
            result = self.importer.import_from_csv("whatever.csv")
            self.assertFalse(result)

    def test_import_from_csv_file_not_found_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.importer.import_from_csv(os.path.join(tmp, "none.csv"))
            self.assertFalse(result)

    def test_get_columns_with_data(self):
        self._set_data()
        self.assertEqual(self.importer.get_columns(),
                         ["total_assets", "total_liabilities", "equity",
                          "revenue", "net_income"])

    def test_get_columns_no_data(self):
        self.assertIsNone(self.importer.get_columns())

    def test_get_summary_with_data(self):
        self._set_data()
        summary = self.importer.get_summary()
        self.assertIsNotNone(summary)
        self.assertIn("count", summary.index)

    def test_get_summary_no_data(self):
        self.assertIsNone(self.importer.get_summary())

    def test_export_invalid_table_name_starts_with_digit(self):
        self._set_data()
        result = self.importer.export_to_database(None, "123bad_table")
        self.assertFalse(result)

    def test_export_invalid_table_name_only_symbols(self):
        self._set_data()
        result = self.importer.export_to_database(None, "   !!!   ")
        self.assertFalse(result)

    def test_export_sanitizes_table_name(self):
        self._set_data()
        db = mock.MagicMock()
        db.connect.return_value = True
        db.cursor.execute.return_value = None
        result = self.importer.export_to_database(db, "good!table;name")
        self.assertTrue(result)
        insert_query = db.cursor.execute.call_args[0][0]
        self.assertIn("goodtablename", insert_query)
        db.connection.commit.assert_called_once()

    def test_export_connect_failure_returns_false(self):
        self._set_data()
        db = mock.MagicMock()
        db.connect.return_value = False
        result = self.importer.export_to_database(db, "test_table")
        self.assertFalse(result)

    def test_export_insert_error_rolls_back(self):
        self._set_data()
        db = mock.MagicMock()
        db.connect.return_value = True
        db.cursor.execute.side_effect = Exception("INSERT failed")
        result = self.importer.export_to_database(db, "test_table")
        self.assertFalse(result)
        db.connection.rollback.assert_called_once()
        db.disconnect.assert_called_once()

    def test_export_outer_error_returns_false(self):
        self._set_data()
        db = mock.MagicMock()
        db.connect.side_effect = Exception("connection boom")
        result = self.importer.export_to_database(db, "test_table")
        self.assertFalse(result)

    def test_filter_data_missing_column_returns_none(self):
        self._set_data()
        self.assertIsNone(self.importer.filter_data("no_such_column", "x"))

    def test_sort_data_no_data_returns_none(self):
        self.assertIsNone(self.importer.sort_data("col"))

    def test_sort_data_missing_column_returns_none(self):
        self._set_data()
        self.assertIsNone(self.importer.sort_data("no_such_column"))

    def test_import_from_csv_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data.csv")
            pd.DataFrame({"name": ["a", "b"]}).to_csv(path, index=False)
            result = self.importer.import_from_csv(path)
            self.assertTrue(result)
            self.assertEqual(self.importer.get_row_count(), 2)

    def test_get_row_count_with_data(self):
        self._set_data()
        self.assertEqual(self.importer.get_row_count(), 1)

    def test_get_row_count_no_data(self):
        self.assertEqual(self.importer.get_row_count(), 0)

    def test_validate_data_no_data(self):
        self.assertFalse(self.importer.validate_data())

    def test_export_to_database_no_data(self):
        result = self.importer.export_to_database(None, "test_table")
        self.assertFalse(result)

    def test_filter_data_no_data(self):
        self.assertIsNone(self.importer.filter_data("col", "val"))

    def test_filter_data_success(self):
        self._set_data()
        filtered = self.importer.filter_data("revenue", 200000)
        self.assertEqual(len(filtered), 1)

    def test_sort_data_success(self):
        self.importer.data = pd.DataFrame({"value": [30, 10, 20]})
        sorted_data = self.importer.sort_data("value", ascending=True)
        self.assertEqual(sorted_data.iloc[0]["value"], 10)

    def test_validate_data_valid(self):
        self._set_data()
        self.assertTrue(self.importer.validate_data())

    def test_validate_data_invalid_row(self):
        self.importer.data = pd.DataFrame([{
            "total_assets": 600000,
            "total_liabilities": 200000,
            "equity": 300000,
            "revenue": 200000,
            "net_income": 15000,
        }])
        self.assertFalse(self.importer.validate_data())


class TestCSVImporterUncovered(unittest.TestCase):
    """Tests for the advanced CSV/Excel importer paths."""

    def setUp(self):
        self.importer = CSVImporter()

    def test_detect_file_type_excel(self):
        self.assertEqual(self.importer.detect_file_type("a.XLSX"), "excel")
        self.assertEqual(self.importer.detect_file_type("a.xls"), "excel")

    def test_detect_file_type_tsv(self):
        self.assertEqual(self.importer.detect_file_type("a.tsv"), "tsv")

    def test_detect_file_type_unknown(self):
        self.assertEqual(self.importer.detect_file_type("a.txt"), "unknown")

    def test_read_csv_unicode_fallback_to_latin1(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "latin.csv")
            with open(path, "wb") as f:
                f.write("date,description,amount\n2025-01-01,Dépôt,100\n".encode("latin-1"))
            headers, rows = self.importer.read_csv(path)
            self.assertEqual(headers, ["date", "description", "amount"])
            self.assertEqual(len(rows), 1)
            self.assertIn("Dépôt", rows[0][1])

    def test_read_csv_generic_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.importer.read_csv(tmp)  # a directory
            self.assertEqual(result, ([], []))
            self.assertTrue(self.importer.errors)

    def test_read_csv_has_header_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "plain.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("a,b\n1,2\n")
            headers, rows = self.importer.read_csv(path, has_header=False)
            self.assertEqual(headers, [])
            self.assertEqual(len(rows), 2)

    def test_read_excel_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "book.xlsx")
            pd.DataFrame({"name": ["x"], "amount": [100]}).to_excel(path, index=False)
            headers, rows = self.importer.read_excel(path)
            self.assertIn("name", headers)
            self.assertEqual(len(rows), 1)

    def test_read_excel_import_error(self):
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "pandas":
                raise ImportError("pandas not installed")
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "book.xlsx")
            pd.DataFrame({"a": [1]}).to_excel(path, index=False)
            with mock.patch("builtins.__import__", side_effect=fake_import):
                headers, rows = self.importer.read_excel(path)
            self.assertEqual((headers, rows), ([], []))
            self.assertIn("pandas", self.importer.errors[0])

    def test_read_excel_generic_error(self):
        with mock.patch("pandas.read_excel",
                        side_effect=ValueError("not an excel")):
            headers, rows = self.importer.read_excel("bad.xlsx")
            self.assertEqual((headers, rows), ([], []))
            self.assertTrue(self.importer.errors)

    def test_import_data_excel_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "book.xlsx")
            pd.DataFrame([{"date": "2025-01-01", "description": "Sale", "amount": 100}]).to_excel(path, index=False)
            result = self.importer.import_data(path, lang="en")
            self.assertEqual(result["stats"]["imported"], 1)
            self.assertEqual(result["data"][0]["description"], "Sale")

    def test_import_data_unsupported_file_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("x")
            result = self.importer.import_data(path)
            self.assertEqual(result["stats"]["imported"], 0)
            self.assertIn("Unsupported file type", result["errors"][0])

    def test_import_data_tsv_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data.tsv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("date\tdescription\tamount\n2025-01-01\tTest\t100\n")
            result = self.importer.import_data(path, lang="en")
            self.assertEqual(result["stats"]["imported"], 1)
            self.assertEqual(result["data"][0]["amount"], 100.0)

    def test_import_data_skips_row_without_amount_or_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "skip.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("date,description,amount\n")
                f.write("2025-01-01,Sale,500\n")
                f.write("2025-01-02,,\n")
            result = self.importer.import_data(path, lang="en")
            self.assertEqual(result["stats"]["total"], 2)
            self.assertEqual(result["stats"]["imported"], 1)
            self.assertEqual(result["stats"]["skipped"], 1)

    def test_import_data_non_numeric_amount_becomes_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "badnum.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("date,description,amount\n2025-01-01,Sale,abc\n")
            result = self.importer.import_data(path, lang="en")
            self.assertEqual(result["stats"]["imported"], 1)
            self.assertEqual(result["data"][0]["amount"], 0.0)

    def test_import_data_on_row_callback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cb.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("date,description,amount\n2025-01-01,Sale,500\n")
            seen = []
            result = self.importer.import_data(path, lang="en",
                                               on_row=lambda i, rec: seen.append((i, rec["amount"])))
            self.assertEqual(result["stats"]["imported"], 1)
            self.assertEqual(seen, [(0, 500.0)])

    def test_import_data_on_row_error_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cb.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("date,description,amount\n2025-01-01,Sale,500\n")

            def bad_callback(index, record):
                raise RuntimeError("boom")

            result = self.importer.import_data(path, lang="en", on_row=bad_callback)
            self.assertEqual(result["stats"]["errors"], 1)
            self.assertIn("Row 1", result["errors"][0])

    def test_import_data_no_data_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "only_header.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("date,description,amount\n")
            result = self.importer.import_data(path, lang="en")
            self.assertEqual(result["stats"]["imported"], 0)
            self.assertIn("No data found", result["errors"][0])

    def test_import_data_french_lang_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fr.csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("date,description,montant\n2025-01-01,Vente,250\n")
            result = self.importer.import_data(path, lang="fr")
            self.assertEqual(result["stats"]["imported"], 1)
            self.assertEqual(result["data"][0]["amount"], 250.0)

    def test_get_preview(self):
        headers = ["a", "b", "c"]
        rows = [["1", "2", "3"], ["4", "5"], ["6", "7", "8", "9"]]
        preview = self.importer.get_preview(rows, headers, max_rows=2)
        self.assertEqual(len(preview), 2)
        self.assertEqual(preview[0], {"a": "1", "b": "2", "c": "3"})
        self.assertEqual(preview[1], {"a": "4", "b": "5"})

    def test_get_preview_default_max_rows(self):
        rows = [["r%d" % i] for i in range(7)]
        preview = self.importer.get_preview(rows, ["col"])
        self.assertEqual(len(preview), 5)

    def test_get_preview_empty(self):
        self.assertEqual(self.importer.get_preview([], ["a"]), [])

    def test_auto_map_columns_unknown_lang_falls_back_to_en(self):
        mapping = self.importer.auto_map_columns(
            ["date", "description", "amount"], lang="xx"
        )
        self.assertIn("date", mapping)
        self.assertIn("amount", mapping)


if __name__ == "__main__":
    unittest.main()
