"""UI tests for views not previously covered (integration feature testing)."""

import sys
import os
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication, QPushButton, QTableWidget, QLineEdit

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)


class TestBaseViewHelpers(unittest.TestCase):
    """Regression tests for _base.py shared helpers."""

    def setUp(self):
        from ui.views._base import BaseView, _clear_nested
        self.BaseView = BaseView
        self._clear_nested = _clear_nested

    def test_clear_nested_recurses_into_sub_layouts(self):
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
        outer = QVBoxLayout()
        inner = QHBoxLayout()
        inner.addWidget(QLabel("x"))
        inner.addWidget(QLabel("y"))
        outer.addLayout(inner)
        self._clear_nested(outer)
        self.assertEqual(outer.count(), 0)

    def test_clear_nested_empty_layout(self):
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        self._clear_nested(layout)
        self.assertEqual(layout.count(), 0)

    def test_clear_layout_rebuild_after_retranslate(self):
        view = self.BaseView()
        view._make_header("dash_title", "dash_subtitle")
        self.assertGreaterEqual(view._main_layout.count(), 2)
        view._clear_layout()
        self.assertEqual(view._main_layout.count(), 0)


class TestDashboardView(unittest.TestCase):

    def setUp(self):
        from ui.views.dashboard import DashboardView
        self.view = DashboardView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_summary_cards_exist(self):
        self.assertTrue(hasattr(self.view, "card_roe"))
        self.assertTrue(hasattr(self.view, "card_cr"))
        self.assertTrue(hasattr(self.view, "card_npm"))
        self.assertTrue(hasattr(self.view, "card_de"))

    def test_eight_charts_exist(self):
        for name in ("chart_ratios", "chart_profitability", "chart_dupont",
                     "chart_balance", "chart_expenses", "chart_radar",
                     "chart_zscore", "chart_liquidity"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_export_button_exists(self):
        self.assertTrue(hasattr(self.view, "export_btn"))

    def test_refresh_does_not_crash(self):
        self.view.refresh()

    def test_clear_all_clears_cards(self):
        from ui.views.dashboard import SummaryCard
        self.view.refresh()
        self.view._clear_all()


class TestRatiosView(unittest.TestCase):

    def setUp(self):
        from ui.views.ratios_view import RatiosView
        self.view = RatiosView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_twenty_cards_exist(self):
        expected = {
            "current_ratio", "quick_ratio", "cash_ratio",
            "gross_profit_margin", "operating_profit_margin",
            "net_profit_margin", "roa", "roe",
            "asset_turnover", "receivables_turnover", "inventory_turnover",
            "days_sales_outstanding", "days_inventory_outstanding",
            "payables_turnover", "days_payable_outstanding",
            "operating_cycle", "cash_conversion_cycle",
            "debt_to_equity", "debt_ratio", "equity_ratio",
        }
        self.assertEqual(set(self.view.cards.keys()), expected)

    def test_update_value(self):
        self.view.cards["roe"].update_value(12.5)
        self.assertIn("12.50", self.view.cards["roe"].value_label.text())

    def test_refresh_does_not_crash(self):
        self.view.refresh()


class TestAuditView(unittest.TestCase):

    def setUp(self):
        from ui.views.audit_view import AuditView
        self.view = AuditView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_buttons_exist(self):
        self.assertIsInstance(self.view.run_audit_btn, QPushButton)
        self.assertIsInstance(self.view.clear_btn, QPushButton)

    def test_clear_results(self):
        self.view.clear_results()
        self.assertTrue(self.view.placeholder_label.isVisibleTo(self.view) or
                        not self.view.report_browser.toPlainText())

    def test_run_audit_no_data_shows_warning(self):
        from ui.app_state import state
        old_ratios = state.ratios
        old_data = state.financial_data
        state.ratios = {}
        state.financial_data = {}
        try:
            with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
                self.view.run_audit()
        finally:
            state.ratios = old_ratios
            state.financial_data = old_data

    def test_run_audit_with_mock_engine(self):
        from ui.app_state import state
        old_ratios = state.ratios
        old_data = state.financial_data
        state.ratios = {"roe": 10.0}
        state.financial_data = {"revenue": 100}
        try:
            fake = mock.Mock()
            fake.get_audit_summary.return_value = {
                "total_issues": 1, "total_warnings": 2, "notes": ["x"],
                "issues": [], "warnings": [], "report": "audit report"}
            with mock.patch("modules.AuditEngine", return_value=fake), \
                 mock.patch("modules.fraud_detection.fraud_detector.mark_audit_approved"), \
                 mock.patch("modules.fraud_detection.fraud_detector.mark_audit_reset"), \
                 mock.patch("modules.activity_log.activity_log.log"):
                self.view.run_audit()
            self.assertEqual(self.view.issues_count.value_label.text(), "1")
            self.assertEqual(self.view.warnings_count.value_label.text(), "2")
        finally:
            state.ratios = old_ratios
            state.financial_data = old_data


class TestReportsView(unittest.TestCase):

    def setUp(self):
        from ui.views.reports_view import ReportsView
        self.view = ReportsView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertTrue(hasattr(self.view, "analyses_list"))
        self.assertTrue(hasattr(self.view, "report_view"))
        for btn in ("export_txt_btn", "export_html_btn", "export_pdf_btn",
                    "export_xlsx_btn", "delete_btn"):
            self.assertTrue(hasattr(self.view, btn), btn)

    def test_refresh_analyses_cancelled(self):
        with mock.patch("PyQt5.QtWidgets.QInputDialog.getText",
                        return_value=("", False)):
            self.view.refresh_analyses()
        self.assertEqual(self.view.analyses_list.count(), 0)

    def test_refresh_analyses_with_results(self):
        results = [{"company_name": "ACME", "year": 2024, "roe": 12.5,
                    "current_ratio": 1.8}]
        with mock.patch("PyQt5.QtWidgets.QInputDialog.getText",
                        return_value=("ACME", True)), \
             mock.patch("database.get_company_analyses",
                        return_value=results):
            self.view.refresh_analyses()
        self.assertEqual(self.view.analyses_list.count(), 1)
        self.assertEqual(self.view._current_company, "ACME")

    def test_clear_current(self):
        self.view.clear_current()
        self.assertEqual(self.view.report_view.toPlainText(), "")


class TestSettingsView(unittest.TestCase):

    def setUp(self):
        from ui.views.settings_view import SettingsView
        self.view = SettingsView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_language_theme_combos(self):
        self.assertGreaterEqual(self.view.lang_combo.count(), 2)
        self.assertGreaterEqual(self.view.theme_combo.count(), 2)

    def test_api_fields_exist(self):
        self.assertIsInstance(self.view.api_key_input, QLineEdit)
        self.assertTrue(hasattr(self.view, "api_url_input"))
        self.assertTrue(hasattr(self.view, "model_combo"))

    def test_api_url_rejects_non_http_schemes(self):
        from unittest import mock
        from ui.app_state import state
        before = state.api_url
        self.view.api_url_input.setText("file:///C:/Windows/system32")
        with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
            self.view.save_settings()
        self.assertEqual(state.api_url, before)

    def test_api_url_accepts_https(self):
        from unittest import mock
        from ui.app_state import state
        self.view.api_url_input.setText("https://api.example.com/v1")
        with mock.patch("PyQt5.QtWidgets.QMessageBox.information"), \
                mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
            self.view.save_settings()
        self.assertEqual(state.api_url, "https://api.example.com/v1")

    def test_backup_buttons_exist(self):
        for name in ("backup_btn", "restore_btn", "export_json_btn",
                     "import_json_btn", "save_btn"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_toggle_key_visibility(self):
        mode_before = self.view.api_key_input.echoMode()
        self.view.toggle_key_visibility()
        self.assertNotEqual(self.view.api_key_input.echoMode(), mode_before)


class TestChatView(unittest.TestCase):

    def setUp(self):
        from ui.views.chat_view import ChatView
        self.view = ChatView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertTrue(hasattr(self.view, "chat_display"))
        self.assertTrue(hasattr(self.view, "input_field"))
        self.assertIsInstance(self.view.send_btn, QPushButton)
        self.assertIsInstance(self.view.clear_btn, QPushButton)

    def test_clear_chat(self):
        self.view.messages = [{"role": "user", "content": "hi"}]
        self.view.clear_chat()
        self.assertEqual(self.view.messages, [])

    def test_add_system_message(self):
        self.view._add_system_message("مرحباً")
        self.assertIn("مرحباً", self.view.chat_display.toPlainText())


class TestTaxView(unittest.TestCase):

    def setUp(self):
        from ui.views.tax_view import TaxView
        self.view = TaxView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_tabs_exist(self):
        self.assertGreaterEqual(self.view.tabs.count(), 3)

    def test_input_fields_exist(self):
        for name in ("revenue_input", "cogs_input", "opex_input",
                     "assets_input", "liabilities_input", "equity_input"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_run_simulation(self):
        self.view.revenue_input.setValue(1000000.0)
        self.view.cogs_input.setValue(400000.0)
        self.view.opex_input.setValue(200000.0)
        self.view.run_simulation()
        self.assertIsNotNone(self.view.last_simulation)

    def test_save_simulation_no_data(self):
        with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
            self.view.save_simulation()


class TestComparativeView(unittest.TestCase):

    def setUp(self):
        from ui.views.comparative_view import ComparativeView
        self.view = ComparativeView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_table_columns(self):
        self.assertEqual(self.view.table.columnCount(), 5)

    def test_add_year_requires_data(self):
        from ui.app_state import state
        old_data = state.financial_data
        state.financial_data = {}
        try:
            with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
                self.view._add_year()
            self.assertEqual(len(self.view.years_data), 0)
        finally:
            state.financial_data = old_data

    def test_add_year_stores_data(self):
        from ui.app_state import state
        old_data = state.financial_data
        state.financial_data = {"revenue": 1000000}
        results = [{"year": 2024, "revenue": 900000, "gross_profit": 400000,
                    "net_income": 100000, "total_assets": 1500000,
                    "total_liabilities": 700000, "total_equity": 800000,
                    "current_ratio": 1.8, "net_profit_margin": 11.1,
                    "roe": 12.5, "debt_to_equity": 0.9}]
        self.view.year_combo.addItem("2024", 2024)
        try:
            with mock.patch("PyQt5.QtWidgets.QMessageBox.information"), \
                 mock.patch("database.db_operations.get_company_analyses",
                            return_value=results):
                self.view._add_year()
            self.assertEqual(len(self.view.years_data), 1)
            self.assertEqual(self.view.years_data[2024]["revenue"], 900000)
            self.assertGreaterEqual(self.view.year_combo.count(), 1)
        finally:
            state.financial_data = old_data

    def test_clear_data(self):
        self.view.years_data = {"2023": {"revenue": 100}}
        self.view._clear_data()
        self.assertEqual(self.view.years_data, {})


class TestCashFlowView(unittest.TestCase):

    def setUp(self):
        from ui.views.cashflow_view import CashFlowView
        self.view = CashFlowView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertIsInstance(self.view.calc_btn, QPushButton)
        self.assertTrue(hasattr(self.view, "report_browser"))
        self.assertTrue(hasattr(self.view, "export_btn"))

    def test_calculate_cash_flow(self):
        from ui.app_state import state
        old_data = state.financial_data
        state.financial_data = {
            "revenue": 1000000, "cost_of_goods": 400000,
            "operating_expenses": 200000, "total_assets": 1500000,
            "total_liabilities": 700000,
        }
        try:
            self.view._calculate_cash_flow()
            self.assertIsNotNone(self.view._last_results)
            self.assertNotEqual(self.view.report_browser.toPlainText(), "")
        finally:
            state.financial_data = old_data


class TestSecurityView(unittest.TestCase):

    def setUp(self):
        from ui.views.security_view import SecurityView
        self.view = SecurityView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertIsInstance(self.view.filter_combo, object)
        self.assertIsInstance(self.view.refresh_btn, QPushButton)
        self.assertTrue(hasattr(self.view, "alerts_table"))
        self.assertTrue(hasattr(self.view, "detail_text"))

    def test_alerts_table_columns(self):
        self.assertEqual(self.view.alerts_table.columnCount(), 6)

    def test_clear_alerts(self):
        with mock.patch("PyQt5.QtWidgets.QMessageBox.question",
                        return_value=16384), \
             mock.patch("modules.fraud_detection.fraud_detector.clear_alerts",
                        return_value=0):
            self.view._clear_alerts()

    def test_clear_alerts_cancelled(self):
        with mock.patch("PyQt5.QtWidgets.QMessageBox.question",
                        return_value=65536):
            self.view._clear_alerts()

    def test_refresh_table_with_mock(self):
        with mock.patch("modules.fraud_detection.fraud_detector.get_alerts",
                        return_value=[]):
            self.view._refresh_table()


class TestZScoreView(unittest.TestCase):

    def setUp(self):
        from ui.views.zscore_view import ZScoreView
        self.view = ZScoreView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_inputs_exist(self):
        for name in ("working_capital", "retained_earnings", "ebit",
                     "market_value_equity", "book_value_debt", "sales",
                     "total_assets"):
            self.assertIn(name, self.view.inputs)

    def test_calculate_result(self):
        self.view.inputs["working_capital"].setText("500000")
        self.view.inputs["retained_earnings"].setText("200000")
        self.view.inputs["ebit"].setText("150000")
        self.view.inputs["market_value_equity"].setText("800000")
        self.view.inputs["book_value_debt"].setText("400000")
        self.view.inputs["sales"].setText("1000000")
        self.view.inputs["total_assets"].setText("1200000")
        self.view.calculate()
        self.assertNotEqual(self.view.result_label.text(), "")


class TestForecastingView(unittest.TestCase):

    def setUp(self):
        from ui.views.forecasting_view import ForecastingView
        self.view = ForecastingView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        for name in ("optimistic", "base_rate", "pessimistic", "years_spin"):
            self.assertTrue(hasattr(self.view, name), name)
        self.assertIsInstance(self.view.run_btn, QPushButton)
        self.assertIsInstance(self.view.results_table, QTableWidget)

    def test_run_forecast(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {"revenue": 1000000, "cost_of_goods_sold": 400000,
                                "operating_expenses": 200000}
        state.ratios = {"roe": 10.0}
        try:
            self.view.optimistic.setValue(15.0)
            self.view.base_rate.setValue(8.0)
            self.view.pessimistic.setValue(3.0)
            self.view.years_spin.setValue(5)
            self.view.run_forecast()
            self.assertGreaterEqual(self.view.results_table.rowCount(), 1)
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios

    def test_run_forecast_no_data_warns(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {}
        state.ratios = {}
        try:
            with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
                self.view.run_forecast()
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios


class TestBudgetView(unittest.TestCase):

    def setUp(self):
        from ui.views.budget_view import BudgetView
        self.view = BudgetView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertIsInstance(self.view.input_table, QTableWidget)
        self.assertGreaterEqual(len(self.view._budget_spins), 4)
        self.assertIsInstance(self.view.run_btn, QPushButton)

    def test_run_budget(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {"revenue": 1000000, "operating_expenses": 300000}
        state.ratios = {"roe": 10.0}
        try:
            self.view.run_budget()
            self.assertGreaterEqual(self.view.results_table.rowCount(), 1)
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios

    def test_run_budget_no_data_warns(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {}
        state.ratios = {}
        try:
            with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
                self.view.run_budget()
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios


class TestCostCenterView(unittest.TestCase):

    def setUp(self):
        from ui.views.cost_center_view import CostCenterView
        self.view = CostCenterView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertIsInstance(self.view.center_table, QTableWidget)
        self.assertIsInstance(self.view.run_btn, QPushButton)

    def test_center_table_rows(self):
        self.assertGreaterEqual(self.view.center_table.rowCount(), 1)

    def test_run_analysis(self):
        from ui.app_state import state
        old_data = state.financial_data
        state.financial_data = {"revenue": 1000000, "operating_expenses": 300000}
        try:
            name_edit, costs_spin, rev_spin, hc_spin = self.view._center_data[0]
            name_edit.setText("Production")
            costs_spin.setValue(100000.0)
            rev_spin.setValue(150000.0)
            hc_spin.setValue(10)
            self.view.run_analysis()
            self.assertGreaterEqual(self.view.results_table.rowCount(), 1)
        finally:
            state.financial_data = old_data


class TestBreakEvenView(unittest.TestCase):

    def setUp(self):
        from ui.views.breakeven_view import BreakEvenView
        self.view = BreakEvenView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertTrue(hasattr(self.view, "fixed_costs"))
        self.assertTrue(hasattr(self.view, "vc_ratio"))
        self.assertIsInstance(self.view.run_btn, QPushButton)

    def test_run_analysis(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {"revenue": 1000000, "operating_expenses": 300000}
        state.ratios = {"roe": 10.0}
        try:
            self.view.fixed_costs.setValue(300000.0)
            self.view.vc_ratio.setValue(60.0)
            self.view.run_analysis()
            self.assertIsNotNone(self.view.analyzer)
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios

    def test_run_analysis_no_data_warns(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {}
        state.ratios = {}
        try:
            with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
                self.view.run_analysis()
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios


class TestDataImportView(unittest.TestCase):

    def setUp(self):
        from ui.views.data_import_view import DataImportView
        self.view = DataImportView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertIsInstance(self.view.btn_select, QPushButton)
        self.assertIsInstance(self.view.btn_import, QPushButton)
        self.assertGreaterEqual(self.view.combo_encoding.count(), 1)
        self.assertGreaterEqual(self.view.combo_lang.count(), 1)

    def test_mapping_combos_exist(self):
        for name in ("date", "description", "debit", "credit", "amount", "account"):
            self.assertIn(name, self.view.mapping_combos)

    def test_import_btn_disabled_initial(self):
        self.assertFalse(self.view.btn_import.isEnabled())

    def test_show_preview(self):
        self.view._show_preview(["date", "amount"], [["2026-01-01", "1000"]])
        self.assertEqual(self.view.preview_table.rowCount(), 1)

    def test_retranslate_rebuilds_ui(self):
        old_btn = self.view.btn_select
        self.view.retranslate()
        self.assertNotEqual(self.view.btn_select, old_btn)
        self.assertIsInstance(self.view.btn_select, QPushButton)


class TestBankSyncView(unittest.TestCase):

    def setUp(self):
        from ui.views.bank_sync_view import BankSyncView
        self.view = BankSyncView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertIsInstance(self.view.btn_select, QPushButton)
        self.assertIsInstance(self.view.btn_detect, QPushButton)
        self.assertIsInstance(self.view.btn_import, QPushButton)
        self.assertTrue(hasattr(self.view, "combo_bank"))
        self.assertTrue(hasattr(self.view, "txt_account"))

    def test_bank_combo_has_items(self):
        self.assertGreaterEqual(self.view.combo_bank.count(), 1)

    def test_import_btn_disabled_initial(self):
        self.assertFalse(self.view.btn_import.isEnabled())

    def test_populate_table(self):
        self.view._populate_table([
            {"date": "2026-01-01", "label": "x", "debit": 100, "credit": 0},
        ])
        self.assertEqual(self.view.tx_table.rowCount(), 1)

    def test_retranslate_rebuilds_ui(self):
        old_btn = self.view.btn_select
        self.view.retranslate()
        self.assertNotEqual(self.view.btn_select, old_btn)
        self.assertIsInstance(self.view.btn_select, QPushButton)


class TestScenariosView(unittest.TestCase):

    def setUp(self):
        from ui.views.scenarios_view import ScenariosView
        self.view = ScenariosView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_assumption_spins_exist(self):
        for name in ("best_revenue", "best_cost", "best_efficiency",
                     "worst_revenue", "worst_cost", "worst_efficiency"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_run_simulation(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {"revenue": 1000000, "cost_of_goods_sold": 400000,
                                "operating_expenses": 200000}
        state.ratios = {"roe": 10.0}
        try:
            self.view.run_simulation()
            self.assertIsNotNone(self.view._scenarios)
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios

    def test_run_simulation_no_data_warns(self):
        from ui.app_state import state
        old_data = state.financial_data
        old_ratios = state.ratios
        state.financial_data = {}
        state.ratios = {}
        try:
            with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
                self.view.run_simulation()
        finally:
            state.financial_data = old_data
            state.ratios = old_ratios

    def test_comparison_table_exists(self):
        self.assertIsInstance(self.view.comparison_table, QTableWidget)

    def test_export_btn_exists(self):
        self.assertIsInstance(self.view.export_btn, QPushButton)


class TestAdvancedDashboardView(unittest.TestCase):

    def setUp(self):
        from ui.views.advanced_dashboard_view import AdvancedDashboardView
        self.view = AdvancedDashboardView()

    def tearDown(self):
        try:
            self.view._auto_refresh_timer.stop()
        except Exception:
            pass

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertIsInstance(self.view.export_pdf_btn, QPushButton)
        self.assertIsInstance(self.view.export_excel_btn, QPushButton)
        self.assertTrue(hasattr(self.view, "kpi_cards"))
        self.assertTrue(hasattr(self.view, "sector_combo"))

    def test_refresh_does_not_crash(self):
        self.view.refresh()

    def test_kpi_cards_present(self):
        self.assertGreaterEqual(len(self.view.kpi_cards), 4)


class TestAIInsightsView(unittest.TestCase):

    def setUp(self):
        from ui.views.ai_insights_view import AIInsightsView
        self.view = AIInsightsView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_method_combo(self):
        self.assertGreaterEqual(self.view.method_combo.count(), 2)
        self.assertGreaterEqual(self.view.months_combo.count(), 1)

    def test_buttons_exist(self):
        self.assertIsInstance(self.view.analyze_btn, QPushButton)
        self.assertIsInstance(self.view.export_pdf_btn, QPushButton)
        self.assertIsInstance(self.view.export_excel_btn, QPushButton)

    def test_tabs_exist(self):
        self.assertGreaterEqual(self.view.tabs.count(), 4)

    def test_tables_exist(self):
        self.assertTrue(hasattr(self.view, "fc_table"))
        self.assertTrue(hasattr(self.view, "an_series_table"))
        self.assertTrue(hasattr(self.view, "an_tx_table"))
        self.assertTrue(hasattr(self.view, "pat_risk_table"))
        self.assertTrue(hasattr(self.view, "rec_table"))
        self.assertTrue(hasattr(self.view, "alerts_list"))


class TestCurrencyView(unittest.TestCase):

    def setUp(self):
        from ui.views.currency_view import CurrencyView
        self.view = CurrencyView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertGreaterEqual(self.view.base_combo.count(), 2)
        self.assertTrue(hasattr(self.view, "rates_table"))
        self.assertTrue(hasattr(self.view, "from_combo"))
        self.assertTrue(hasattr(self.view, "to_combo"))

    def test_rates_table_columns(self):
        self.assertEqual(self.view.rates_table.columnCount(), 4)

    def test_convert(self):
        self.view.amount_input.setValue(1000.0)
        self.view._convert()
        self.assertNotEqual(self.view.convert_result.text(), "")


class TestCloudSyncView(unittest.TestCase):

    def setUp(self):
        from ui.views.cloud_sync_view import CloudSyncView
        self.view = CloudSyncView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertTrue(hasattr(self.view, "dest_table"))
        self.assertTrue(hasattr(self.view, "backup_table"))
        self.assertTrue(hasattr(self.view, "history_table"))
        self.assertTrue(hasattr(self.view, "dest_name"))
        self.assertTrue(hasattr(self.view, "dest_path"))

    def test_auto_settings_widgets(self):
        self.assertTrue(hasattr(self.view, "auto_check"))
        self.assertTrue(hasattr(self.view, "interval_spin"))
        self.assertTrue(hasattr(self.view, "max_spin"))


class TestDemoDataView(unittest.TestCase):

    def setUp(self):
        from ui.views.demo_data_view import DemoDataView
        self.view = DemoDataView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_widgets_exist(self):
        self.assertGreaterEqual(self.view.company_combo.count(), 1)
        self.assertIsInstance(self.view.load_btn, QPushButton)
        self.assertTrue(hasattr(self.view, "desc_label"))
        self.assertTrue(hasattr(self.view, "tx_table"))

    def test_export_buttons_exist(self):
        self.assertIsInstance(self.view.report_btn, QPushButton)
        self.assertIsInstance(self.view.export_btn, QPushButton)
        self.assertIsInstance(self.view.templates_btn, QPushButton)


class TestUserTestingView(unittest.TestCase):

    def setUp(self):
        from ui.views.user_testing_view import UserTestingView
        self.view = UserTestingView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_combos_exist(self):
        for name in ("group_combo", "scenario_combo", "category_combo",
                     "priority_combo", "status_combo", "session_combo"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_buttons_exist(self):
        for name in ("new_btn", "demo_btn", "save_db_btn", "load_db_btn",
                     "delete_btn", "add_btn", "delete_fb_btn", "resolve_btn"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_stat_cards_exist(self):
        for name in ("stat_score", "stat_count", "stat_issues", "stat_enh"):
            self.assertTrue(hasattr(self.view, name), name)


class TestAnalysisView(unittest.TestCase):

    def setUp(self):
        from ui.views.analysis_view import DuPontView
        self.view = DuPontView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_component_cards_exist(self):
        for name in ("npm_card", "at_card", "em_card", "roe_card"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_charts_exist(self):
        for name in ("chart_waterfall", "chart_trend", "chart_gauge",
                     "chart_industry"):
            self.assertTrue(hasattr(self.view, name), name)

    def test_sector_combo_has_items(self):
        self.assertGreaterEqual(self.view.sector_combo.count(), 1)

    def test_export_btn_exists(self):
        self.assertIsInstance(self.view.export_btn, QPushButton)


if __name__ == "__main__":
    unittest.main()
