# تقويم المواعيد الضريبية والتذكيرات
# ====================================

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QFrame,
    QMessageBox, QDialog, QLineEdit, QTextEdit, QDateEdit,
    QComboBox, QHeaderView, QGridLayout, QScrollArea
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QTextDocument

from ui.app_state import state, ThemeColors
from ui.resources.i18n import t
from ui.views._base import BaseView
from modules.tax_reminders import tax_reminders
from datetime import datetime


class AddReminderDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("taxcal_add_reminder"))
        self.setMinimumWidth(420)
        self.setMinimumHeight(340)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl = QLabel(t("taxcal_add_reminder"))
        lbl.setObjectName("headerTitle")
        layout.addWidget(lbl)

        name_lbl = QLabel(t("taxcal_reminder_name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("taxcal_reminder_name_ph"))
        layout.addWidget(name_lbl)
        layout.addWidget(self.name_input)

        date_lbl = QLabel(t("taxcal_due_date"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate().addDays(7))
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(date_lbl)
        layout.addWidget(self.date_input)

        desc_lbl = QLabel(t("taxcal_description"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setPlaceholderText(t("taxcal_description_ph"))
        layout.addWidget(desc_lbl)
        layout.addWidget(self.desc_input)

        type_lbl = QLabel(t("taxcal_tax_type"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "TVA", "IBS", "IRG", "CNAS", "CNAC",
            "Accounting", "Audit", t("taxcal_custom")
        ])
        layout.addWidget(type_lbl)
        layout.addWidget(self.type_combo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cancel_btn = QPushButton(t("btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.save_btn = QPushButton(t("taxcal_save_reminder"))
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setTabOrder(self.name_input, self.date_input)
        self.setTabOrder(self.date_input, self.desc_input)
        self.setTabOrder(self.desc_input, self.type_combo)

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, t("warning"), t("taxcal_name_required"))
            return
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        desc = self.desc_input.toPlainText().strip()
        tax_type = self.type_combo.currentText()
        tax_reminders.add_custom_reminder(name, date_str, desc, tax_type)
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "description": self.desc_input.toPlainText().strip(),
            "tax_type": self.type_combo.currentText(),
        }


class TaxCalendarView(BaseView):

    def __init__(self):
        super().__init__()
        self._labels = {}
        self._stat_labels = {}
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("taxcal_title", "taxcal_subtitle")

        stats_layout = QHBoxLayout()
        self.stat_next = self._make_stat_card(t("taxcal_next_deadline"), "--", ThemeColors.get('error'))
        self.stat_overdue = self._make_stat_card(t("taxcal_overdue_count"), "0", ThemeColors.get('warning'))
        self.stat_month = self._make_stat_card(t("taxcal_this_month"), "0", ThemeColors.get('info'))
        self._stat_labels["next"] = self.stat_next.findChild(QLabel, "statValue")
        self._stat_labels["overdue"] = self.stat_overdue.findChild(QLabel, "statValue")
        self._stat_labels["month"] = self.stat_month.findChild(QLabel, "statValue")
        stats_layout.addWidget(self.stat_next)
        stats_layout.addWidget(self.stat_overdue)
        stats_layout.addWidget(self.stat_month)
        self._main_layout.addLayout(stats_layout)

        toolbar = QHBoxLayout()

        year_lbl = QLabel(t("taxcal_year"))
        toolbar.addWidget(year_lbl)
        self.year_combo = QComboBox()
        self.year_combo.setMinimumWidth(100)
        self.year_combo.setMinimumHeight(36)
        current_year = datetime.now().year
        for y in range(current_year + 1, current_year - 4, -1):
            self.year_combo.addItem(str(y), y)
        idx = self.year_combo.findData(state.fiscal_year)
        if idx >= 0:
            self.year_combo.setCurrentIndex(idx)
        self.year_combo.currentIndexChanged.connect(self._on_year_changed)
        toolbar.addWidget(self.year_combo)

        self.refresh_btn = QPushButton(t("taxcal_refresh"))
        self.refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self.refresh_btn)
        self.add_btn = QPushButton(t("taxcal_add_reminder"))
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.clicked.connect(self._add_reminder)
        toolbar.addWidget(self.add_btn)
        self.print_btn = QPushButton(t("taxcal_print"))
        self.print_btn.clicked.connect(self._print_calendar)
        toolbar.addWidget(self.print_btn)
        toolbar.addStretch()
        self._main_layout.addLayout(toolbar)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        self._main_layout.addWidget(sep)

        self.empty_guide = QLabel(t("taxcal_empty_guide"))
        self.empty_guide.setObjectName("card")
        self.empty_guide.setWordWrap(True)
        self.empty_guide.setAlignment(Qt.AlignCenter)
        self.empty_guide.setMinimumHeight(80)
        self.empty_guide.setStyleSheet("padding: 20px; font-size: 14px;")
        self.empty_guide.hide()
        self._main_layout.addWidget(self.empty_guide)

        self.upcoming_group = QGroupBox(t("taxcal_upcoming"))
        upcoming_layout = QVBoxLayout()
        self.upcoming_table = QTableWidget()
        self.upcoming_table.setColumnCount(7)
        self.upcoming_table.setHorizontalHeaderLabels([
            t("taxcal_col_type"), t("taxcal_col_name"),
            t("taxcal_col_due"), t("taxcal_col_days"),
            t("taxcal_col_form"), t("taxcal_col_severity"),
            t("taxcal_col_action"),
        ])
        self.upcoming_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.upcoming_table.setAlternatingRowColors(True)
        self.upcoming_table.verticalHeader().setVisible(False)
        self.upcoming_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.upcoming_table.setMinimumHeight(250)
        upcoming_layout.addWidget(self.upcoming_table)
        self.upcoming_group.setLayout(upcoming_layout)
        self._main_layout.addWidget(self.upcoming_group, 1)

        cal_sep = QFrame()
        cal_sep.setFrameShape(QFrame.HLine)
        cal_sep.setObjectName("separator")
        self._main_layout.addWidget(cal_sep)

        cal_group = QGroupBox(t("taxcal_yearly_overview"))
        cal_scroll = QScrollArea()
        cal_scroll.setWidgetResizable(True)
        cal_scroll.setMaximumHeight(320)
        self.calendar_widget = QWidget()
        self.calendar_layout = QGridLayout(self.calendar_widget)
        self.calendar_layout.setSpacing(8)
        self.calendar_layout.setContentsMargins(10, 10, 10, 10)
        cal_scroll.setWidget(self.calendar_widget)
        cal_group_layout = QVBoxLayout()
        cal_group_layout.addWidget(cal_scroll)
        cal_group.setLayout(cal_group_layout)
        self._main_layout.addWidget(cal_group)

        year = self.year_combo.currentData()
        self._build_calendar_overview(year)

    def _on_year_changed(self, index):
        year = self.year_combo.currentData()
        if year:
            self._build_calendar_overview(year)

    def _build_calendar_overview(self, year=None):
        for i in range(self.calendar_layout.count()):
            item = self.calendar_layout.itemAt(i)
            if item is None:
                continue
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if year is None:
            try:
                year = state.fiscal_year
            except Exception:
                year = datetime.now().year

        cal_summary = tax_reminders.get_calendar_summary(year)
        month_keys = [
            "tax_month_jan", "tax_month_feb", "tax_month_mar",
            "tax_month_apr", "tax_month_may", "tax_month_jun",
            "tax_month_jul", "tax_month_aug", "tax_month_sep",
            "tax_month_oct", "tax_month_nov", "tax_month_dec",
        ]

        for col in range(12):
            month = col + 1
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(8, 8, 8, 8)
            card_layout.setSpacing(8)

            month_lbl = QLabel(t(month_keys[col]))
            month_lbl.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            font.setPointSize(11)
            month_lbl.setFont(font)
            card_layout.addWidget(month_lbl)

            obligations = cal_summary.get(month, [])
            if obligations:
                for ob in obligations:
                    name = ob.get("name_en", ob.get("name_ar", ""))
                    tax_type = ob.get("tax_type", "")
                    ob_lbl = QLabel(f"• {name[:22]}")
                    ob_lbl.setStyleSheet(f"font-size: 9px; color: {ThemeColors.get('text_secondary')};")
                    ob_lbl.setWordWrap(True)
                    card_layout.addWidget(ob_lbl)
                count_lbl = QLabel(f"{len(obligations)} {t('taxcal_items')}")
                count_lbl.setStyleSheet(f"font-size: 10px; color: {ThemeColors.get('info')}; font-weight: bold;")
                count_lbl.setAlignment(Qt.AlignCenter)
                card_layout.addWidget(count_lbl)
            else:
                empty_lbl = QLabel(t("taxcal_no_items"))
                empty_lbl.setStyleSheet(f"font-size: 10px; color: {ThemeColors.get('text_muted')};")
                empty_lbl.setAlignment(Qt.AlignCenter)
                card_layout.addWidget(empty_lbl)

            card.setLayout(card_layout)
            self.calendar_layout.addWidget(card, 0, col)

    def refresh(self):
        try:
            reminders = tax_reminders.get_upcoming_reminders(days_ahead=90)
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("tax_calendar_view").error(f"Failed to load reminders: {e}")
            reminders = []

        overdue = [r for r in reminders if r["days_until"] < 0]
        this_month = datetime.now().month
        this_year = datetime.now().year
        month_items = [
            r for r in reminders
            if datetime.strptime(r["due_date"], "%Y-%m-%d").month == this_month
            and datetime.strptime(r["due_date"], "%Y-%m-%d").year == this_year
        ]

        next_deadline = "--"
        if reminders:
            nearest = reminders[0]
            next_deadline = f"{nearest['days_until']}d"

        if self._stat_labels.get("next"):
            self._stat_labels["next"].setText(next_deadline)
            if overdue:
                self._stat_labels["next"].setStyleSheet(
                    f"color: {ThemeColors.get('error')}; font-size: 18px; font-weight: bold;"
                )
        if self._stat_labels.get("overdue"):
            self._stat_labels["overdue"].setText(str(len(overdue)))
        if self._stat_labels.get("month"):
            self._stat_labels["month"].setText(str(len(month_items)))

        self._fill_table(reminders)
        year = self.year_combo.currentData() if hasattr(self, 'year_combo') else None
        self._build_calendar_overview(year)

        has_reminders = len(reminders) > 0
        self.empty_guide.setVisible(not has_reminders)
        self.upcoming_group.setVisible(has_reminders)

    def _fill_table(self, reminders):
        self.upcoming_table.setRowCount(len(reminders))
        for i, rem in enumerate(reminders):
            days = rem["days_until"]
            severity = rem["severity"]

            if severity == "urgent":
                row_color = QColor(ThemeColors.get('error')).lighter(160)
            elif severity == "warning":
                row_color = QColor(ThemeColors.get('warning')).lighter(160)
            else:
                row_color = QColor(ThemeColors.get('info')).lighter(160)

            type_item = QTableWidgetItem(rem.get("tax_type", ""))
            type_item.setTextAlignment(Qt.AlignCenter)

            name = rem.get("name_en", rem.get("name_ar", ""))
            name_item = QTableWidgetItem(name)

            due_item = QTableWidgetItem(rem.get("due_date", ""))
            due_item.setTextAlignment(Qt.AlignCenter)

            days_text = f"{days}" if days >= 0 else str(days)
            days_item = QTableWidgetItem(days_text)
            days_item.setTextAlignment(Qt.AlignCenter)
            if days <= 3:
                days_item.setForeground(QColor(ThemeColors.get('error')))
            elif days <= 7:
                days_item.setForeground(QColor(ThemeColors.get('warning')))
            else:
                days_item.setForeground(QColor(ThemeColors.get('info')))
            font = days_item.font()
            font.setBold(True)
            font.setPointSize(12)
            days_item.setFont(font)

            form_item = QTableWidgetItem(rem.get("form_number", ""))
            form_item.setTextAlignment(Qt.AlignCenter)

            sev_text = f"🔴 {t('taxcal_urgent')}" if severity == "urgent" else (
                f"🟠 {t('taxcal_warning')}" if severity == "warning" else f"🔵 {t('taxcal_info')}"
            )
            sev_item = QTableWidgetItem(sev_text)
            sev_item.setTextAlignment(Qt.AlignCenter)

            ack_btn = QPushButton(t("taxcal_acknowledge"))
            ack_btn.setMinimumHeight(30)
            if rem.get("acknowledged"):
                ack_btn.setText(t("taxcal_acknowledged"))
                ack_btn.setEnabled(False)
            ack_btn.setProperty("reminder_id", rem.get("id", ""))
            ack_btn.clicked.connect(self._acknowledge)
            self.upcoming_table.setCellWidget(i, 6, ack_btn)

            for col_idx, item in enumerate([type_item, name_item, due_item, days_item, form_item, sev_item]):
                item.setBackground(row_color)
                self.upcoming_table.setItem(i, col_idx, item)

    def _acknowledge(self):
        btn = self.sender()
        if not btn:
            return
        reminder_id = btn.property("reminder_id")
        if reminder_id:
            tax_reminders.acknowledge_reminder(reminder_id)
            btn.setText(t("taxcal_acknowledged"))
            btn.setEnabled(False)
            self.refresh()

    def _add_reminder(self):
        dialog = AddReminderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh()

    def _print_calendar(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrinter.Accepted:
                reminders = tax_reminders.get_upcoming_reminders(days_ahead=90)
                doc = QTextDocument()
                html = self._build_print_html(reminders)
                doc.setHtml(html)
                doc.print_(printer)
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("tax_calendar_view").error(f"Print failed: {e}")

    def _build_print_html(self, reminders):
        title = t("taxcal_title")
        html = f"<h2>{title}</h2>"
        html += f"<p>{t('taxcal_subtitle')}</p>"
        html += f"<p>{t('taxcal_print_date')}: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"
        html += "<hr>"
        html += f"<h3>{t('taxcal_upcoming')}</h3>"
        html += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
        html += "<tr>"
        for header in [t("taxcal_col_type"), t("taxcal_col_name"), t("taxcal_col_due"),
                        t("taxcal_col_days"), t("taxcal_col_form")]:
            html += f"<th style='background:#f0f0f0; text-align:center;'>{header}</th>"
        html += "</tr>"
        for rem in reminders:
            html += "<tr>"
            html += f"<td style='text-align:center;'>{rem.get('tax_type', '')}</td>"
            html += f"<td>{rem.get('name_en', rem.get('name_ar', ''))}</td>"
            html += f"<td style='text-align:center;'>{rem.get('due_date', '')}</td>"
            days = rem['days_until']
            color = "#e74c3c" if days <= 3 else ("#f39c12" if days <= 7 else "#3498db")
            html += f"<td style='text-align:center; color:{color}; font-weight:bold;'>{days}</td>"
            html += f"<td style='text-align:center;'>{rem.get('form_number', '')}</td>"
            html += "</tr>"
        html += "</table>"
        html += "<br>"
        try:
            year = state.fiscal_year
        except Exception:
            year = datetime.now().year
        cal_summary = tax_reminders.get_calendar_summary(year)
        month_keys = [
            "tax_month_jan", "tax_month_feb", "tax_month_mar",
            "tax_month_apr", "tax_month_may", "tax_month_jun",
            "tax_month_jul", "tax_month_aug", "tax_month_sep",
            "tax_month_oct", "tax_month_nov", "tax_month_dec",
        ]
        html += f"<h3>{t('taxcal_yearly_overview')} — {year}</h3>"
        html += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
        for month_num in range(1, 13):
            obligations = cal_summary.get(month_num, [])
            month_name = t(month_keys[month_num - 1])
            items = ", ".join([ob.get("name_en", ob.get("name_ar", "")) for ob in obligations]) if obligations else t("taxcal_no_items")
            html += f"<tr><td style='font-weight:bold; width:120px;'>{month_name}</td><td>{items}</td></tr>"
        html += "</table>"
        return html

    def retranslate(self):
        title = self.findChild(QLabel, "headerTitle")
        if title:
            title.setText(t("taxcal_title"))
        subtitle = self.findChild(QLabel, "headerSubtitle")
        if subtitle:
            subtitle.setText(t("taxcal_subtitle"))
        self.refresh_btn.setText(t("taxcal_refresh"))
        self.add_btn.setText(t("taxcal_add_reminder"))
        self.print_btn.setText(t("taxcal_print"))
        self.upcoming_table.setHorizontalHeaderLabels([
            t("taxcal_col_type"), t("taxcal_col_name"),
            t("taxcal_col_due"), t("taxcal_col_days"),
            t("taxcal_col_form"), t("taxcal_col_severity"),
            t("taxcal_col_action"),
        ])
        if self._stat_labels.get("next"):
            pass
        year = self.year_combo.currentData() if hasattr(self, 'year_combo') else None
        self._build_calendar_overview(year)
