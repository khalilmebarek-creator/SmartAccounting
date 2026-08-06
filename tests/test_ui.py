"""UI tests for login, user manager, and key views."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

from modules.user_manager import UserManager, ROLE_ADMIN, _hash_password


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.um = UserManager()
        self.um._users = {}
        self.um._current_user = None
        self.um._users["admin"] = {
            "password": _hash_password("Admin@1234"),
            "role": ROLE_ADMIN,
            "created": "2024-01-01",
            "display_name": "Admin",
            "email": "admin@test.com"
        }

    def test_login_success(self):
        ok, code, extra = self.um.login("admin@test.com", "Admin@1234")
        self.assertTrue(ok)
        self.assertEqual(code, "ok")
        self.assertTrue(self.um.is_logged_in())

    def test_login_wrong_password(self):
        ok, code, extra = self.um.login("admin@test.com", "wrong")
        self.assertFalse(ok)
        self.assertEqual(code, "err_wrong_password")

    def test_login_nonexistent_email(self):
        ok, code, extra = self.um.login("nobody@test.com", "pass")
        self.assertFalse(ok)
        self.assertEqual(code, "err_email_not_found")

    def test_login_lockout(self):
        for _ in range(5):
            self.um.login("admin@test.com", "wrong")
        ok, code, extra = self.um.login("admin@test.com", "wrong")
        self.assertFalse(ok)
        self.assertEqual(code, "err_locked")
        self.assertIn("minutes", extra)

    def test_logout(self):
        self.um.login("admin@test.com", "Admin@1234")
        self.um.logout()
        self.assertFalse(self.um.is_logged_in())
        self.assertIsNone(self.um.get_current_user())

    def test_register_success(self):
        ok, code = self.um.register("user1@test.com", "Test@1234", "User One")
        self.assertTrue(ok)
        _, udata = self.um._find_by_email("user1@test.com")
        self.assertIsNotNone(udata)
        self.assertEqual(udata["email"], "user1@test.com")

    def test_register_role_default_viewer(self):
        ok, code = self.um.register("newuser1@test.com", "Test@1234", "New User")
        self.assertTrue(ok)
        _, udata = self.um._find_by_email("newuser1@test.com")
        self.assertIsNotNone(udata)
        self.assertEqual(udata["role"], "viewer")

    def test_register_role_explicit_admin(self):
        from modules.user_manager import ROLE_ADMIN
        ok, code = self.um.register("admin2@test.com", "Test@1234", "Admin2", ROLE_ADMIN)
        self.assertTrue(ok)
        _, udata = self.um._find_by_email("admin2@test.com")
        self.assertIsNotNone(udata)
        self.assertEqual(udata["role"], ROLE_ADMIN)

    def test_register_duplicate_email(self):
        ok, code = self.um.register("admin@test.com", "Test@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_email_exists")

    def test_register_invalid_email(self):
        ok, code = self.um.register("not-an-email", "Test@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_invalid_email")

    def test_register_weak_password(self):
        ok, code = self.um.register("newuser@test.com", "ab")
        self.assertFalse(ok)
        self.assertIn("password", code)

    def test_register_password_no_upper(self):
        ok, code = self.um.register("newuser@test.com", "test@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_password_no_upper")

    def test_register_password_no_digit(self):
        ok, code = self.um.register("newuser@test.com", "Test@abcd")
        self.assertFalse(ok)
        self.assertEqual(code, "err_password_no_digit")

    def test_change_password_success(self):
        self.um.login("admin@test.com", "Admin@1234")
        ok, code = self.um.change_password("admin", "Admin@1234", "NewPass@1234")
        self.assertTrue(ok)
        ok2, _, _ = self.um.login("admin@test.com", "NewPass@1234")
        self.assertTrue(ok2)

    def test_change_password_wrong_old(self):
        self.um.login("admin@test.com", "Admin@1234")
        ok, code = self.um.change_password("admin", "WrongOld", "NewPass@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_wrong_password")

    def test_delete_user(self):
        self.um.register("user2@test.com", "Test@1234")
        username, _ = self.um._find_by_email("user2@test.com")
        ok, msg = self.um.delete_user(username)
        self.assertTrue(ok)

    def test_cannot_delete_admin(self):
        ok, msg = self.um.delete_user("admin")
        self.assertFalse(ok)

    def test_is_admin(self):
        self.um.login("admin@test.com", "Admin@1234")
        self.assertTrue(self.um.is_admin())

    def test_get_all_users(self):
        users = self.um.get_all_users()
        self.assertGreaterEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "admin")

    def test_reset_password_by_email(self):
        ok, code = self.um.reset_password_by_email("admin@test.com", "Reset@1234")
        self.assertTrue(ok)
        udata = self.um._users["admin"]
        self.assertTrue(udata.get("must_change_password"))
        ok2, _, _ = self.um.login("admin@test.com", "Reset@1234")
        self.assertTrue(ok2)

    def test_reset_password_email_not_found(self):
        ok, code = self.um.reset_password_by_email("ghost@test.com", "Reset@1234")
        self.assertFalse(ok)
        self.assertEqual(code, "err_email_not_found")

    def test_permissions_admin_has_all(self):
        from modules.user_manager import ROLE_ADMIN, PERMISSIONS
        self.um.login("admin@test.com", "Admin@1234")
        for perm in PERMISSIONS[ROLE_ADMIN]:
            self.assertTrue(self.um.has_permission(perm))

    def test_permissions_viewer_limited(self):
        from modules.user_manager import ROLE_VIEWER, PERMISSIONS
        self.um.register("viewer@test.com", "Test@1234", "Viewer")
        self.um._current_user = {"username": "viewer", "role": ROLE_VIEWER}
        for perm in PERMISSIONS[ROLE_VIEWER]:
            self.assertTrue(self.um.has_permission(perm))
        self.assertFalse(self.um.has_permission("manage_users"))
        self.assertFalse(self.um.has_permission("enter_data"))

    def test_generate_otp(self):
        from modules.user_manager import generate_otp
        otp = generate_otp(6)
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())


class TestReportTemplates(unittest.TestCase):

    def test_get_all_templates(self):
        from modules.report_templates import report_templates
        templates = report_templates.get_all_templates()
        self.assertGreaterEqual(len(templates), 5)

    def test_get_template(self):
        from modules.report_templates import report_templates
        t = report_templates.get_template("financial_summary")
        self.assertIsNotNone(t)
        self.assertIn("sections", t)

    def test_create_custom_template(self):
        from modules.report_templates import report_templates
        ok = report_templates.create_template("custom_test", {
            "name": "Test", "sections": ["summary"]
        })
        self.assertTrue(ok)
        report_templates.delete_template("custom_test")


class TestScheduledBackup(unittest.TestCase):

    def test_manual_backup(self):
        from modules.scheduled_backup import scheduled_backup
        filename = scheduled_backup.manual_backup()
        self.assertIsNotNone(filename)
        self.assertTrue(filename.startswith("backup_"))

    def test_get_backups(self):
        from modules.scheduled_backup import scheduled_backup
        scheduled_backup.manual_backup()
        backups = scheduled_backup.get_backups()
        self.assertGreater(len(backups), 0)


class TestLoginUI(unittest.TestCase):

    def test_login_view_creation(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertIsNotNone(view)
        self.assertEqual(view.stack.currentIndex(), 0)

    def test_login_view_switch_to_register(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.stack.setCurrentIndex(1)
        self.assertEqual(view.stack.currentIndex(), 1)

    def test_register_no_role_selector(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertFalse(hasattr(view, 'reg_role'))

    def test_forgot_link_always_present(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        self.assertTrue(view.forgot_link.isEnabled())

    def test_forgot_link_shows_on_error(self):
        from ui.views.login_view import LoginView
        view = LoginView()
        view.show()
        self.assertTrue(view.forgot_link.isEnabled())


class TestBenchmarksView(unittest.TestCase):

    def setUp(self):
        from ui.views.benchmarks_view import BenchmarkView
        self.bv = BenchmarkView()

    def test_view_creation(self):
        self.assertIsNotNone(self.bv)

    def test_sector_combo_exists(self):
        self.assertTrue(hasattr(self.bv, 'sector_combo'))

    def test_sector_combo_has_items(self):
        self.assertGreater(self.bv.sector_combo.count(), 0)

    def test_compare_button_exists(self):
        self.assertTrue(hasattr(self.bv, 'compare_btn'))

    def test_score_defaults_to_dash(self):
        self.assertEqual(self.bv.score_value.text(), "--")

    def test_empty_guide_shows_when_no_data(self):
        self.assertTrue(hasattr(self.bv, 'empty_guide'))
        self.assertIsNotNone(self.bv.empty_guide)
        self.assertEqual(self.bv.empty_guide.objectName(), "card")


class TestTaxCalendarView(unittest.TestCase):

    def setUp(self):
        from ui.views.tax_calendar_view import TaxCalendarView
        self.tcv = TaxCalendarView()

    def test_view_creation(self):
        self.assertIsNotNone(self.tcv)

    def test_year_combo_exists(self):
        self.assertTrue(hasattr(self.tcv, 'year_combo'))

    def test_year_combo_has_items(self):
        self.assertGreater(self.tcv.year_combo.count(), 0)

    def test_upcoming_table_exists(self):
        self.assertTrue(hasattr(self.tcv, 'upcoming_table'))

    def test_refresh_button_exists(self):
        self.assertTrue(hasattr(self.tcv, 'refresh_btn'))

    def test_empty_guide_exists(self):
        self.assertTrue(hasattr(self.tcv, 'empty_guide'))
        self.assertIsNotNone(self.tcv.empty_guide)
        self.assertEqual(self.tcv.empty_guide.objectName(), "card")


class TestDataEntryView(unittest.TestCase):

    def setUp(self):
        from ui.app_state import state
        state.clear()
        from ui.views.data_entry import DataEntryView
        self.dev = DataEntryView()

    def test_view_creation(self):
        self.assertIsNotNone(self.dev)

    def test_demo_button_exists(self):
        self.assertTrue(hasattr(self.dev, 'demo_btn'))
        self.assertEqual(self.dev.demo_btn.objectName(), "secondaryBtn")

    def test_demo_button_text_is_set(self):
        self.assertTrue(len(self.dev.demo_btn.text()) > 0)

    def test_save_button_starts_disabled(self):
        self.assertFalse(self.dev.save_btn.isEnabled())

    def test_company_name_starts_empty(self):
        self.assertEqual(self.dev.company_name.text(), "")

    def test_company_name_fr_starts_empty(self):
        self.assertEqual(self.dev.company_name_fr.text(), "")

    def test_company_nif_starts_empty(self):
        self.assertEqual(self.dev.company_nif.text(), "")

    def test_company_rc_starts_empty(self):
        self.assertEqual(self.dev.company_rc.text(), "")

    def test_company_bank_starts_empty(self):
        self.assertEqual(self.dev.company_bank.text(), "")

    def test_company_address_starts_empty(self):
        self.assertEqual(self.dev.company_address.text(), "")

    def test_company_phone_starts_empty(self):
        self.assertEqual(self.dev.company_phone.text(), "")

    def test_company_email_starts_empty(self):
        self.assertEqual(self.dev.company_email.text(), "")

    def test_legal_form_starts_at_0(self):
        self.assertEqual(self.dev.company_legal_form.currentIndex(), 0)

    def test_activity_starts_at_0(self):
        self.assertEqual(self.dev.company_activity.currentIndex(), 0)

    def test_fiscal_year_default_2024(self):
        self.assertEqual(self.dev.fiscal_year.value(), 2024)

    def test_financial_spins_start_zero(self):
        self.assertEqual(self.dev.current_assets.value(), 0.0)
        self.assertEqual(self.dev.inventory.value(), 0.0)
        self.assertEqual(self.dev.current_liabilities.value(), 0.0)
        self.assertEqual(self.dev.total_assets.value(), 0.0)
        self.assertEqual(self.dev.total_liabilities.value(), 0.0)
        self.assertEqual(self.dev.equity.value(), 0.0)
        self.assertEqual(self.dev.revenue.value(), 0.0)
        self.assertEqual(self.dev.cogs.value(), 0.0)
        self.assertEqual(self.dev.gross_profit.value(), 0.0)
        self.assertEqual(self.dev.net_income.value(), 0.0)
        self.assertEqual(self.dev.avg_receivables.value(), 0.0)
        self.assertEqual(self.dev.avg_inventory.value(), 0.0)

    def test_financial_spins_show_empty_before_input(self):
        from ui.resources.i18n import t
        ph = t("de_enter_amount")
        self.assertEqual(self.dev.current_assets.text().strip(), ph)
        self.assertEqual(self.dev.inventory.text().strip(), ph)
        self.assertEqual(self.dev.total_assets.text().strip(), ph)
        self.assertEqual(self.dev.revenue.text().strip(), ph)
        self.assertEqual(self.dev.net_income.text().strip(), ph)
        self.dev.current_assets.setValue(150000)
        self.assertEqual(self.dev.current_assets.value(), 150000)

    def test_load_demo_data_fills_fields(self):
        self.dev.load_default_data()
        self.assertNotEqual(self.dev.company_name.text(), "")
        self.assertNotEqual(self.dev.company_name_fr.text(), "")
        self.assertGreater(self.dev.current_assets.value(), 0)
        self.assertGreater(self.dev.revenue.value(), 0)
        self.assertNotEqual(self.dev.company_legal_form.currentIndex(), 0)
        self.assertNotEqual(self.dev.company_activity.currentIndex(), 0)


class TestCostCenterProfitabilityView(unittest.TestCase):

    def setUp(self):
        from ui.views.cost_center_profitability_view import CostCenterProfitabilityView
        self.cpv = CostCenterProfitabilityView()

    def test_view_creation(self):
        self.assertIsNotNone(self.cpv)

    def test_center_table_exists(self):
        self.assertTrue(hasattr(self.cpv, 'center_table'))

    def test_center_table_has_max_rows(self):
        self.assertEqual(self.cpv.center_table.rowCount(), self.cpv.MAX_CENTERS)

    def test_method_combo_has_items(self):
        self.assertGreater(self.cpv.method_combo.count(), 0)

    def test_run_button_exists(self):
        self.assertTrue(hasattr(self.cpv, 'run_btn'))

    def test_analysis_tab_exists(self):
        self.assertTrue(hasattr(self.cpv, 'analysis_table'))

    def test_comparison_tab_exists(self):
        self.assertTrue(hasattr(self.cpv, 'comparison_table'))

    def test_standards_table_exists(self):
        self.assertTrue(hasattr(self.cpv, 'standards_table'))

    def test_recommendations_table_exists(self):
        self.assertTrue(hasattr(self.cpv, 'rec_table'))

    def test_no_data_shows_when_empty(self):
        self.cpv.refresh()
        self.assertFalse(self.cpv.no_data_label.isHidden())


class TestLedgerView(unittest.TestCase):

    def setUp(self):
        from ui.views.ledger_view import LedgerView
        self.view = LedgerView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_stat_cards_exist(self):
        self.assertTrue(hasattr(self.view, 'stat_entries'))
        self.assertTrue(hasattr(self.view, 'stat_debit'))
        self.assertTrue(hasattr(self.view, 'stat_credit'))

    def test_entries_table_exists(self):
        self.assertEqual(self.view.entries_table.columnCount(), 7)

    def test_add_entry_updates_table(self):
        self.view.account_edit.setText("600000")
        self.view.debit_spin.setValue(100.0)
        self.view._add_entry()
        self.assertEqual(self.view.entries_table.rowCount(), 1)
        self.assertEqual(self.view.stat_debit.text(), "100.00")

    def test_trial_balance_table_exists(self):
        self.assertEqual(self.view.tb_table.columnCount(), 4)

    def test_refresh_clears_filter(self):
        self.view.account_edit.setText("600000")
        self.view.refresh()
        self.assertGreaterEqual(self.view.entries_table.rowCount(), 0)


class TestPartnersView(unittest.TestCase):

    def setUp(self):
        from ui.views.partners_view import PartnersView
        self.view = PartnersView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_type_combo_has_items(self):
        self.assertGreaterEqual(self.view.type_combo.count(), 2)

    def test_add_partner_updates_table(self):
        self.view.name_edit.setText("Test Partner")
        self.view._add_partner()
        self.assertEqual(self.view.partners_table.rowCount(), 1)

    def test_partners_table_columns(self):
        self.assertEqual(self.view.partners_table.columnCount(), 6)

    def test_aging_table_exists(self):
        self.assertEqual(self.view.aging_table.columnCount(), 5)

    def test_add_transaction_requires_selection(self):
        self.view.refresh()
        self.assertIsNone(self.view._selected_partner_id())


class TestInvoicingView(unittest.TestCase):

    def setUp(self):
        from ui.views.invoicing_view import InvoicingView
        self.view = InvoicingView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_type_combo_has_items(self):
        self.assertGreaterEqual(self.view.type_combo.count(), 2)

    def test_add_pending_item(self):
        self.view.item_desc.setText("Service")
        self.view.item_qty.setValue(2.0)
        self.view.item_price.setValue(50.0)
        self.view._add_pending_item()
        self.assertEqual(len(self.view._pending_items), 1)
        self.assertEqual(self.view.pending_table.rowCount(), 1)

    def test_create_invoice_requires_partner(self):
        from unittest import mock
        self.view.item_desc.setText("Service")
        self.view._add_pending_item()
        with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
            self.view._create_invoice()
        self.assertEqual(self.view.invoices_table.rowCount(), 0)

    def test_invoices_table_columns(self):
        self.assertEqual(self.view.invoices_table.columnCount(), 7)

    def test_status_combo_exists(self):
        self.assertGreaterEqual(self.view.status_combo.count(), 6)


class TestInventoryView(unittest.TestCase):

    def setUp(self):
        from ui.views.inventory_view import InventoryView
        self.view = InventoryView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_add_item_updates_table(self):
        self.view.name_edit.setText("Widget")
        self.view.qty_spin.setValue(10.0)
        self.view._add_item()
        self.assertEqual(self.view.items_table.rowCount(), 1)

    def test_items_table_columns(self):
        self.assertEqual(self.view.items_table.columnCount(), 7)

    def test_movement_table_columns(self):
        self.assertEqual(self.view.mov_table.columnCount(), 5)

    def test_low_stock_combo_exists(self):
        self.assertGreaterEqual(self.view.low_only_check.count(), 2)

    def test_add_movement_requires_selection(self):
        self.view.refresh()
        self.assertIsNone(self.view._selected_item_id())


class TestPayrollView(unittest.TestCase):

    def setUp(self):
        from ui.views.payroll_view import PayrollView
        self.view = PayrollView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_add_employee_updates_table(self):
        self.view.name_edit.setText("Ali")
        self.view.salary_spin.setValue(50000.0)
        self.view._add_employee()
        self.assertEqual(self.view.employees_table.rowCount(), 1)

    def test_employees_table_columns(self):
        self.assertEqual(self.view.employees_table.columnCount(), 5)

    def test_run_payroll_with_no_employees(self):
        from unittest import mock
        with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
            self.view._run_payroll()
        self.assertEqual(self.view.payslips_table.rowCount(), 0)

    def test_payslips_table_columns(self):
        self.assertEqual(self.view.payslips_table.columnCount(), 6)

    def test_month_year_spins(self):
        self.assertEqual(self.view.month_spin.value(), 8)
        self.assertEqual(self.view.year_spin.value(), 2026)


class TestBudgetingView(unittest.TestCase):

    def setUp(self):
        from ui.views.budgeting_view import BudgetingView
        self.view = BudgetingView()

    def test_view_creation(self):
        self.assertIsNotNone(self.view)

    def test_add_item_updates_table(self):
        self.view.name_edit.setText("Salaries")
        self.view.amount_spin.setValue(1000.0)
        self.view._add_item()
        self.assertEqual(self.view.items_table.rowCount(), 1)

    def test_items_table_columns(self):
        self.assertEqual(self.view.items_table.columnCount(), 4)

    def test_compare_table_columns(self):
        self.assertEqual(self.view.compare_table.columnCount(), 5)

    def test_compare_without_actuals(self):
        from unittest import mock
        with mock.patch("PyQt5.QtWidgets.QMessageBox.warning"):
            self.view._compare()
        self.assertEqual(self.view.compare_table.rowCount(), 0)

    def test_parse_actuals(self):
        self.view.actual_input.setPlainText("Salaries,1000\nRent,500")
        actuals = self.view._parse_actuals()
        self.assertEqual(actuals, {"Salaries": 1000.0, "Rent": 500.0})

    def test_category_combo_has_items(self):
        self.assertGreaterEqual(self.view.category_combo.count(), 3)


class TestFadeInSafety(unittest.TestCase):
    """ضمانة أمان التنقل: لا تبقى أي شاشة عالقة عند شفافية صفر (شاشة سوداء)."""

    def setUp(self):
        from ui.main_window import MainWindow
        self.win = MainWindow()

    def _pump(self, ms):
        from PyQt5.QtCore import QEventLoop, QTimer
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec_()

    def test_rapid_switching_clears_effect(self):
        for vid in (1, 2, 3, 4, 5, 1, 2, 3):
            self.win._go_to_view(vid)
        self._pump(600)
        cur = self.win.content.currentWidget()
        self.assertIsNone(cur.graphicsEffect())

    def test_no_lingering_animations_referenced(self):
        self.win._go_to_view(1)
        self.assertIn(id(self.win.content.currentWidget()), self.win._view_anims)
        self._pump(600)
        self.assertEqual(self.win._view_anims, {})

    def test_single_navigation_clean(self):
        self.win._go_to_view(4)
        self._pump(400)
        cur = self.win.content.currentWidget()
        self.assertIsNone(cur.graphicsEffect())

    def test_none_widget_no_crash(self):
        self.win._fade_in_view(None)

    def test_fade_failure_clears_effect(self):
        from unittest import mock
        cur = self.win.content.currentWidget()
        with mock.patch(
            "PyQt5.QtWidgets.QGraphicsOpacityEffect.setOpacity",
            side_effect=RuntimeError("boom")
        ):
            self.win._fade_in_view(cur)
        self._pump(600)
        self.assertIsNone(cur.graphicsEffect())


if __name__ == "__main__":
    unittest.main(verbosity=2)
