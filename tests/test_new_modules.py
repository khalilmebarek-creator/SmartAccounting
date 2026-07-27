# اختبارات الوحدات الجديدة - Phase 4
# ====================================

import pytest
import os
import sys
import tempfile
import csv
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPrintManager:
    def test_init(self):
        from modules.print_manager import PrintManager
        pm = PrintManager()
        assert pm.temp_dir is not None
        assert os.path.exists(pm.temp_dir)

    def test_generate_report_html(self):
        from modules.print_manager import PrintManager
        pm = PrintManager()
        sections = [
            {"title": "Balance Sheet", "headers": ["Item", "Value"], "rows": [("Cash", 100000), ("Debt", 50000)]},
            {"title": "Income", "content": "Revenue: 500,000 DZD"},
        ]
        html = pm.generate_report_html("Financial Report", sections, "Test Company", "2025")
        assert "<html" in html
        assert "Financial Report" in html
        assert "Test Company" in html
        assert "100,000.00" in html

    def test_save_and_print_html(self):
        from modules.print_manager import PrintManager
        pm = PrintManager()
        html = "<html><body><h1>Test</h1></body></html>"
        path = pm.save_and_print_html(html, "Test Report")
        assert path is not None
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Test" in content
        pm.cleanup()

    def test_cleanup(self):
        from modules.print_manager import PrintManager
        pm = PrintManager()
        pm.cleanup()
        assert not os.path.exists(pm.temp_dir)


class TestExcelExporter:
    def test_init(self):
        from modules.excel_export import ExcelExporter
        ee = ExcelExporter()
        assert ee.TITLE_FONT is not None

    def test_full_report_export(self):
        from modules.excel_export import ExcelExporter
        ee = ExcelExporter()
        data = {
            "cash": 500000, "accounts_receivable": 200000, "inventory": 300000,
            "current_assets": 1000000, "fixed_assets": 2000000, "total_assets": 3000000,
            "accounts_payable": 150000, "current_liabilities": 300000,
            "total_liabilities": 600000, "equity": 2400000,
            "revenue": 5000000, "cost_of_goods_sold": 3000000, "gross_profit": 2000000,
            "operating_expenses": 1000000, "net_income": 1000000,
        }
        ratios = {"current_ratio": 3.33, "roa": 0.33, "roe": 0.42, "net_profit_margin": 20}
        tax_data = {"ibs": 190000, "tva": 950000, "cnas": 260000}
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            filepath = f.name
        try:
            result = ee.export_full_report(filepath, data, "Test Co", "2025", ratios=ratios, tax_data=tax_data)
            assert result is True
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0
        finally:
            os.unlink(filepath)


class TestTaxReminders:
    def test_get_upcoming(self):
        from modules.tax_reminders import TaxReminderManager
        tr = TaxReminderManager()
        upcoming = tr.get_upcoming_reminders(days_ahead=365)
        assert isinstance(upcoming, list)
        assert len(upcoming) > 0
        for r in upcoming:
            assert "name_ar" in r
            assert "due_date" in r
            assert "severity" in r

    def test_acknowledge(self):
        from modules.tax_reminders import TaxReminderManager
        tr = TaxReminderManager()
        upcoming = tr.get_upcoming_reminders(365)
        if upcoming:
            rid = upcoming[0]["id"]
            tr.acknowledge_reminder(rid)
            assert rid in tr.acknowledged

    def test_custom_reminder(self):
        from modules.tax_reminders import TaxReminderManager
        tr = TaxReminderManager()
        initial = len(tr.custom_reminders)
        result = tr.add_custom_reminder("Test Reminder", "2026-12-31", "Test desc", "Custom")
        assert result is True
        assert len(tr.custom_reminders) == initial + 1
        tr.remove_custom_reminder(len(tr.custom_reminders) - 1)

    def test_calendar_summary(self):
        from modules.tax_reminders import TaxReminderManager
        tr = TaxReminderManager()
        cal = tr.get_calendar_summary(2026)
        assert isinstance(cal, dict)
        assert len(cal) == 12


class TestCSVImporter:
    def test_detect_csv_delimiter(self):
        from modules.csv_import import CSVImporter
        ci = CSVImporter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("date,description,amount\n2025-01-01,Test,1000\n")
            filepath = f.name
        try:
            delim = ci.detect_delimiter(filepath)
            assert delim == ","
        finally:
            os.unlink(filepath)

    def test_auto_map_columns_ar(self):
        from modules.csv_import import CSVImporter
        ci = CSVImporter()
        headers = ["التاريخ", "الوصف", "مدين", "دائن", "المبلغ"]
        mapping = ci.auto_map_columns(headers, "ar")
        assert "date" in mapping
        assert "description" in mapping
        assert "debit" in mapping
        assert "credit" in mapping

    def test_import_csv(self):
        from modules.csv_import import CSVImporter
        ci = CSVImporter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("date,description,debit,credit\n")
            f.write("2025-01-01,Payment received,0,50000\n")
            f.write("2025-01-02,Office rent,15000,0\n")
            filepath = f.name
        try:
            result = ci.import_data(filepath, lang="en")
            assert result["stats"]["total"] == 2
            assert result["stats"]["imported"] == 2
        finally:
            os.unlink(filepath)

    def test_empty_file(self):
        from modules.csv_import import CSVImporter
        ci = CSVImporter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("")
            filepath = f.name
        try:
            result = ci.import_data(filepath)
            assert result["stats"]["imported"] == 0
        finally:
            os.unlink(filepath)


class TestBankSync:
    def test_get_banks(self):
        from modules.bank_sync import BankSyncManager
        bs = BankSyncManager()
        banks = bs.get_bank_list()
        assert len(banks) >= 5
        for b in banks:
            assert "code" in b
            assert "name_en" in b

    def test_detect_bank(self):
        from modules.bank_sync import BankSyncManager
        bs = BankSyncManager()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("Date;Description;Debit;Credit;Balance\n")
            f.write("01/01/2025;Payment;0;5000;5000\n")
            filepath = f.name
        try:
            detected = bs.detect_bank(filepath)
            assert detected is None or isinstance(detected, str)
        finally:
            os.unlink(filepath)

    def test_parse_amount(self):
        from modules.bank_sync import BankSyncManager
        bs = BankSyncManager()
        assert bs._parse_amount("5000") == 5000.0
        assert bs._parse_amount("5,000.50") == 5000.50
        assert bs._parse_amount("") == 0.0
        assert bs._parse_amount("abc") == 0.0

    def test_parse_date(self):
        from modules.bank_sync import BankSyncManager
        bs = BankSyncManager()
        assert bs._parse_date("01/01/2025", "%d/%m/%Y") == "2025-01-01"
        assert bs._parse_date("2025-01-01", "%Y-%m-%d") == "2025-01-01"

    def test_reconcile(self):
        from modules.bank_sync import BankSyncManager
        bs = BankSyncManager()
        bank_tx = [
            {"date": "2025-01-01", "amount": 5000},
            {"date": "2025-01-02", "amount": -3000},
        ]
        book_tx = [
            {"date": "2025-01-01", "amount": 5000},
            {"date": "2025-01-03", "amount": -1000},
        ]
        result = bs.reconcile(bank_tx, book_tx)
        assert result["matched_count"] == 1
        assert result["unmatched_bank_count"] == 1
        assert result["unmatched_book_count"] == 1


class TestBenchmarks:
    def test_get_sectors(self):
        from modules.benchmarks import BenchmarkAnalyzer
        ba = BenchmarkAnalyzer()
        sectors = ba.get_sectors_list()
        assert len(sectors) >= 5
        for s in sectors:
            assert "code" in s
            assert "name_ar" in s

    def test_compare_with_sector(self):
        from modules.benchmarks import BenchmarkAnalyzer
        ba = BenchmarkAnalyzer()
        ratios = {
            "current_ratio": 2.0,
            "net_profit_margin": 8.0,
            "roa": 6.0,
            "roe": 15.0,
            "debt_to_equity": 1.0,
        }
        result = ba.compare_with_sector(ratios, "commercial")
        assert "ratios" in result
        assert "overall_score" in result
        assert "rating" in result
        assert result["overall_score"] > 0

    def test_radar_data(self):
        from modules.benchmarks import BenchmarkAnalyzer
        ba = BenchmarkAnalyzer()
        ratios = {"current_ratio": 2.0, "net_profit_margin": 8.0, "roa": 6.0, "roe": 15.0}
        radar = ba.get_radar_data(ratios, "services")
        assert "labels" in radar
        assert "company" in radar
        assert len(radar["labels"]) > 0

    def test_suggest_improvements(self):
        from modules.benchmarks import BenchmarkAnalyzer
        ba = BenchmarkAnalyzer()
        ratios = {"current_ratio": 0.5, "net_profit_margin": 1.0, "debt_to_equity": 4.0}
        suggestions = ba.suggest_improvements(ratios, "commercial")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        for s in suggestions:
            assert "ratio" in s
            assert "message_ar" in s

    def test_invalid_sector(self):
        from modules.benchmarks import BenchmarkAnalyzer
        ba = BenchmarkAnalyzer()
        result = ba.compare_with_sector({"current_ratio": 2.0}, "nonexistent")
        assert "error" in result
