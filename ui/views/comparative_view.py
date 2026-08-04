from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.app_state import state
from ui.resources.i18n import t


class ComparativeView(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.years_data = {}
        self.comparison_result = None
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(t("comparative_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("comparative_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.year_label = QLabel(t("comparative_select_year"))
        controls_layout.addWidget(self.year_label)

        self.year_combo = QComboBox()
        self.year_combo.setMinimumWidth(120)
        controls_layout.addWidget(self.year_combo)

        self.add_year_btn = QPushButton(t("comparative_add_year"))
        self.add_year_btn.setObjectName("primaryBtn")
        self.add_year_btn.clicked.connect(self._add_year)
        controls_layout.addWidget(self.add_year_btn)

        self.compare_btn = QPushButton(t("comparative_compare"))
        self.compare_btn.setObjectName("primaryBtn")
        self.compare_btn.clicked.connect(self._run_comparison)
        controls_layout.addWidget(self.compare_btn)

        self.clear_btn = QPushButton(t("comparative_clear"))
        self.clear_btn.setObjectName("secondaryBtn")
        self.clear_btn.clicked.connect(self._clear_data)
        controls_layout.addWidget(self.clear_btn)

        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        self.years_display = QLabel("")
        self.years_display.setObjectName("cardSubtitle")
        main_layout.addWidget(self.years_display)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("dashboardScroll")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            t("comparative_item"), t("comparative_year1"),
            t("comparative_year2"), t("comparative_change"),
            t("comparative_change_pct")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(400)
        scroll_layout.addWidget(self.table)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        summary_title = QLabel(t("comparative_summary"))
        summary_title.setObjectName("sectionTitle")
        main_layout.addWidget(summary_title)

        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("card")
        summary_layout = QVBoxLayout(self.summary_frame)

        self.summary_label = QLabel(t("comparative_no_data"))
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("font-size: 11pt; padding: 10px;")
        summary_layout.addWidget(self.summary_label)

        main_layout.addWidget(self.summary_frame)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def _populate_years(self):
        self.year_combo.clear()
        if state.has_data():
            company = state.company_name
            try:
                from database.db_operations import get_company_analyses
                results = get_company_analyses(company)
                years = sorted(set(r['year'] for r in results if r['year']))
                for y in years:
                    self.year_combo.addItem(str(y), y)
            except Exception:
                pass

    def _add_year(self):
        year = self.year_combo.currentData()
        if year is None:
            QMessageBox.warning(self, t("warning"), t("comparative_no_year"))
            return

        if year in self.years_data:
            QMessageBox.information(self, t("info"), t("comparative_year_exists"))
            return

        try:
            from database.db_operations import get_company_analyses
            company = state.company_name
            results = get_company_analyses(company)
            year_data = None
            for r in results:
                if r['year'] == year:
                    year_data = r
                    break

            if not year_data:
                QMessageBox.warning(self, t("warning"), t("comparative_no_data_for_year"))
                return

            self.years_data[year] = {
                'revenue': year_data.get('revenue', 0) or 0,
                'gross_profit': year_data.get('gross_profit', 0) or 0,
                'net_income': year_data.get('net_income', 0) or 0,
                'total_assets': year_data.get('total_assets', 0) or 0,
                'total_liabilities': year_data.get('total_liabilities', 0) or 0,
                'equity': year_data.get('total_equity', 0) or 0,
                'current_ratio': year_data.get('current_ratio', 0) or 0,
                'net_profit_margin': year_data.get('net_profit_margin', 0) or 0,
                'roe': year_data.get('roe', 0) or 0,
                'debt_to_equity': year_data.get('debt_to_equity', 0) or 0
            }

            self._update_years_display()
            QMessageBox.information(self, t("success"), t("comparative_year_added").format(year=year))

        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _clear_data(self):
        self.years_data.clear()
        self.comparison_result = None
        self.table.setRowCount(0)
        self.summary_label.setText(t("comparative_no_data"))
        self._update_years_display()

    def _update_years_display(self):
        if not self.years_data:
            self.years_display.setText("")
            return
        years = sorted(self.years_data.keys())
        self.years_display.setText(
            t("comparative_years_loaded").format(
                count=len(years),
                years=", ".join(str(y) for y in years)
            )
        )

    def _run_comparison(self):
        if len(self.years_data) < 2:
            QMessageBox.warning(self, t("warning"), t("comparative_need_two_years"))
            return

        try:
            from modules.comparative import ComparativeAnalyzer
            analyzer = ComparativeAnalyzer(self.years_data)
            self.comparison_result = analyzer.generate_report()
            comparison = analyzer.get_comparison()
            self._populate_table(comparison)
            self._update_summary(comparison)
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _populate_table(self, comparison):
        years = comparison['years']
        if len(years) < 2:
            return

        year_a = years[-2]
        year_b = years[-1]

        self.table.setHorizontalHeaderLabels([
            t("comparative_item"),
            str(year_a),
            str(year_b),
            t("comparative_change"),
            t("comparative_change_pct")
        ])

        items = []
        key_items = comparison.get('item_changes', {})
        for item_name, periods in key_items.items():
            for period, data in periods.items():
                change = data['change']
                items.append({
                    'name': item_name,
                    'prev': data['previous'],
                    'current': data['current'],
                    'abs_change': change['absolute'],
                    'pct_change': change['percentage']
                })

        ratio_items = comparison.get('ratio_changes', {})
        for ratio_name, periods in ratio_items.items():
            for period, data in periods.items():
                change = data['change']
                items.append({
                    'name': ratio_name,
                    'prev': data['previous'],
                    'current': data['current'],
                    'abs_change': change['absolute'],
                    'pct_change': change['percentage']
                })

        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.table.setItem(row, 1, QTableWidgetItem(f"{item['prev']:,.4f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['current']:,.4f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['abs_change']:+,.4f}"))
            pct_item = QTableWidgetItem(f"{item['pct_change']:+.2f}%")
            if item['pct_change'] > 0:
                pct_item.setForeground(Qt.darkGreen)
            elif item['pct_change'] < 0:
                pct_item.setForeground(Qt.red)
            self.table.setItem(row, 4, pct_item)

    def _update_summary(self, comparison):
        years = comparison['years']
        year_a = years[-2]
        year_b = years[-1]

        lines = []
        lines.append(t("comparative_summary_header").format(year_a=year_a, year_b=year_b))

        key_items = comparison.get('item_changes', {})
        for item_name, periods in key_items.items():
            for period, data in periods.items():
                change = data['change']
                direction = t("comparative_increase") if change['absolute'] > 0 else t("comparative_decrease")
                lines.append(
                    f"  {item_name}: {data['previous']:,.2f} -> {data['current']:,.2f} "
                    f"({direction} {abs(change['percentage']):.2f}%)"
                )

        self.summary_label.setText("\n".join(lines))

    def refresh(self):
        self._populate_years()
        if not state.has_data():
            self.subtitle.setText(t("dashboard_no_data"))
        else:
            self.subtitle.setText(
                t("comparative_subtitle_active").format(
                    company=state.company_name
                )
            )

    def retranslate(self):
        self.title.setText(t("comparative_title"))
        self.subtitle.setText(t("comparative_subtitle"))
        self.year_label.setText(t("comparative_select_year"))
        self.add_year_btn.setText(t("comparative_add_year"))
        self.compare_btn.setText(t("comparative_compare"))
        self.clear_btn.setText(t("comparative_clear"))
        self.summary_label.setText(t("comparative_no_data"))
        self.table.setHorizontalHeaderLabels([
            t("comparative_item"), t("comparative_year1"),
            t("comparative_year2"), t("comparative_change"),
            t("comparative_change_pct")
        ])
        self.refresh()
