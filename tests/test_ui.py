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


if __name__ == "__main__":
    unittest.main(verbosity=2)
