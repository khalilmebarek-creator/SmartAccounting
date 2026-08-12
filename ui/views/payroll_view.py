# واجهة الرواتب الجزائرية
# ========================
# موظفون + تشغيل الرواتب (CNAS/IRG/البطالة) + كشوفات + تصدير CSV + حفظ قاعدة البيانات

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QMessageBox, QFileDialog,
    QHeaderView, QFrame,
)

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.payroll import PayrollEngine, payroll_engine


def _plain(text):
    return "".join(ch for ch in (text or "") if ord(ch) < 0xFFFF)


class PayrollView(BaseView):
    """واجهة الرواتب"""

    def __init__(self):
        super().__init__()
        self._engine = payroll_engine
        if not self._engine.load_db():
            self._engine = PayrollEngine()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("payroll_title", "payroll_subtitle")

        stats = QHBoxLayout()
        f1, self.stat_employees = self._make_stat(t("payroll_stat_employees"))
        f2, self.stat_gross = self._make_stat(t("payroll_stat_gross"))
        f3, self.stat_irg = self._make_stat(t("payroll_stat_irg"))
        f4, self.stat_net = self._make_stat(t("payroll_stat_net"))
        for w in (f1, f2, f3, f4):
            stats.addWidget(w)
        self._main_layout.addLayout(stats)

        # إضافة موظف
        add_card = self._make_card("payroll_add_employee")
        form = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(t("payroll_name"))
        self.position_edit = QLineEdit()
        self.position_edit.setPlaceholderText(t("payroll_position"))
        self.department_edit = QLineEdit()
        self.department_edit.setPlaceholderText(t("payroll_department"))
        self.salary_spin = QDoubleSpinBox()
        self.salary_spin.setRange(0, 1e12)
        self.salary_spin.setDecimals(2)
        add_btn = QPushButton(t("payroll_add_btn"))
        add_btn.clicked.connect(self._add_employee)
        for w in (self.name_edit, self.position_edit, self.department_edit,
                  self.salary_spin, add_btn):
            form.addWidget(w)
        add_card.layout().addLayout(form)
        self._main_layout.addWidget(add_card)

        # جدول الموظفين
        list_card = self._make_card("payroll_employees")
        actions = QHBoxLayout()
        self.only_active = QComboBox()
        self.only_active.addItems([t("payroll_all"), t("payroll_active_only")])
        self.only_active.currentIndexChanged.connect(self.refresh)
        actions.addWidget(self.only_active)
        delete_btn = QPushButton(t("payroll_delete_employee"))
        delete_btn.clicked.connect(self._delete_employee)
        actions.addWidget(delete_btn)
        actions.addStretch()
        list_card.layout().addLayout(actions)

        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(5)
        self.employees_table.setHorizontalHeaderLabels([
            t("payroll_col_id"), t("payroll_col_name"),
            t("payroll_col_position"), t("payroll_col_department"),
            t("payroll_col_salary"),
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.employees_table.setEditTriggers(QTableWidget.NoEditTriggers)
        list_card.layout().addWidget(self.employees_table)
        self._main_layout.addWidget(list_card)

        # تشغيل الرواتب
        run_card = self._make_card("payroll_run")
        run_form = QHBoxLayout()
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(8)
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(2026)
        run_btn = QPushButton(t("payroll_run_btn"))
        run_btn.clicked.connect(self._run_payroll)
        export_btn = QPushButton(t("payroll_export_csv"))
        export_btn.clicked.connect(self._export_csv)
        save_btn = QPushButton(t("payroll_save_db"))
        save_btn.clicked.connect(self._save_db)
        clear_btn = QPushButton(t("payroll_clear"))
        clear_btn.clicked.connect(self._clear_all)
        for w in (QLabel(t("payroll_month")), self.month_spin,
                  QLabel(t("payroll_year")), self.year_spin,
                  run_btn, export_btn, save_btn, clear_btn):
            run_form.addWidget(w)
        run_form.addStretch()
        run_card.layout().addLayout(run_form)

        self.payslips_table = QTableWidget()
        self.payslips_table.setColumnCount(6)
        self.payslips_table.setHorizontalHeaderLabels([
            t("payroll_col_name"), t("payroll_col_base"),
            t("payroll_col_cnas"), t("payroll_col_irg"),
            t("payroll_col_net"), t("payroll_col_status"),
        ])
        self.payslips_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.payslips_table.setEditTriggers(QTableWidget.NoEditTriggers)
        run_card.layout().addWidget(self.payslips_table)
        self._main_layout.addWidget(run_card)

        self._main_layout.addStretch()

    def _selected_employee_id(self):
        row = self.employees_table.currentRow()
        if row < 0:
            return None
        item = self.employees_table.item(row, 0)
        return int(item.text()) if item else None

    def _add_employee(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, t("payroll_title"), t("payroll_name_required"))
            return
        try:
            self._engine.add_employee(
                name, position=self.position_edit.text().strip(),
                department=self.department_edit.text().strip(),
                base_salary=self.salary_spin.value(),
            )
        except Exception as exc:
            QMessageBox.critical(self, t("payroll_title"), str(exc))
            return
        self.name_edit.clear()
        self.position_edit.clear()
        self.department_edit.clear()
        self.salary_spin.setValue(0.0)
        self.refresh()

    def _delete_employee(self):
        emp_id = self._selected_employee_id()
        if emp_id is None:
            QMessageBox.warning(self, t("payroll_title"), t("payroll_select_first"))
            return
        if QMessageBox.question(
                self, t("payroll_title"), t("payroll_delete_confirm")) != \
                QMessageBox.Yes:
            return
        self._engine.delete_employee(emp_id)
        self.refresh()

    def _run_payroll(self):
        try:
            slips = self._engine.run_payroll(self.month_spin.value(),
                                             self.year_spin.value())
        except Exception as exc:
            QMessageBox.critical(self, t("payroll_title"), str(exc))
            return
        if not slips:
            QMessageBox.warning(self, t("payroll_title"), t("payroll_no_employees"))
        self.refresh()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("payroll_export_csv"), "payroll.csv", "CSV Files (*.csv)")
        if not path:
            return
        if self._engine.export_payslips_csv(path, self.month_spin.value(),
                                            self.year_spin.value()):
            QMessageBox.information(self, t("payroll_title"), t("payroll_export_ok"))
        else:
            QMessageBox.warning(self, t("payroll_title"), t("payroll_export_fail"))

    def _save_db(self):
        if self._engine.save_db():
            QMessageBox.information(self, t("payroll_title"), t("payroll_saved"))
        else:
            QMessageBox.warning(self, t("payroll_title"), t("payroll_save_fail"))

    def _clear_all(self):
        if QMessageBox.question(
                self, t("payroll_title"), t("payroll_clear_confirm")) != \
                QMessageBox.Yes:
            return
        self._engine.clear()
        self.refresh()

    def refresh(self):
        active_only = hasattr(self, "only_active") and \
            self.only_active.currentIndex() == 1
        employees = self._engine.list_employees(
            status="active" if active_only else None)
        self.employees_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            self.employees_table.setItem(row, 0, QTableWidgetItem(str(emp["id"])))
            self.employees_table.setItem(row, 1, QTableWidgetItem(_plain(emp["name"])))
            self.employees_table.setItem(row, 2, QTableWidgetItem(emp.get("position") or ""))
            self.employees_table.setItem(row, 3, QTableWidgetItem(emp.get("department") or ""))
            self.employees_table.setItem(row, 4, QTableWidgetItem(f"{emp['base_salary']:,.2f}"))

        self.stat_employees.setText(str(len(self._engine.list_employees())))

        slips = self._engine.get_payroll(self.month_spin.value(),
                                         self.year_spin.value())
        self.payslips_table.setRowCount(len(slips))
        gross = irg = net = 0.0
        for row, slip in enumerate(slips):
            gross += slip["base_salary"]
            irg += slip["irg"]
            net += slip["net_salary"]
            self.payslips_table.setItem(row, 0, QTableWidgetItem(_plain(slip["employee_name"])))
            self.payslips_table.setItem(row, 1, QTableWidgetItem(f"{slip['base_salary']:,.2f}"))
            self.payslips_table.setItem(row, 2, QTableWidgetItem(f"{slip['cnas_employee']:,.2f}"))
            self.payslips_table.setItem(row, 3, QTableWidgetItem(f"{slip['irg']:,.2f}"))
            self.payslips_table.setItem(row, 4, QTableWidgetItem(f"{slip['net_salary']:,.2f}"))
            self.payslips_table.setItem(
                row, 5, QTableWidgetItem(
                    t("payroll_status_%s" % slip["status"])))

        self.stat_gross.setText(f"{gross:,.2f}")
        self.stat_irg.setText(f"{irg:,.2f}")
        self.stat_net.setText(f"{net:,.2f}")
