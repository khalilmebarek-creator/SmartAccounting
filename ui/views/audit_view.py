# واجهة التدقيق والمراجعة
# =========================

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QTextBrowser, QPushButton,
    QScrollArea, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.app_state import state
from ui.resources.i18n import t
from modules.fraud_detection import fraud_detector
from modules.activity_log import activity_log


class AuditItemCard(QFrame):
    """كارت عنصر تدقيق واحد"""

    SEVERITY_KEYS = {
        'aud_critical': ('#E74C3C', '❌'),
        'aud_warning': ('#F39C12', '⚠️'),
        'aud_note': ('#27AE60', '✅'),
    }

    def __init__(self, severity_key, description, detail="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(70)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._severity_key = severity_key
        color, icon = self.SEVERITY_KEYS.get(severity_key, ('#7F8C8D', '•'))
        label = t(severity_key)

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)

        self.icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(16)
        self.icon_label.setFont(icon_font)
        self.icon_label.setFixedWidth(35)
        layout.addWidget(self.icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        self.type_label = QLabel(label)
        self.type_label.setObjectName("issueTypeLabel")
        text_layout.addWidget(self.type_label)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("issueDescLabel")
        text_layout.addWidget(desc_label)

        if detail:
            detail_label = QLabel(detail)
            detail_label.setWordWrap(True)
            detail_label.setObjectName("issueDetailLabel")
            text_layout.addWidget(detail_label)

        layout.addLayout(text_layout, 1)
        self.setLayout(layout)

        self.setProperty("severityColor", color)
        self.setStyleSheet(f"""
            QFrame#card {{
                border-right: 4px solid {color};
                border-radius: 4px;
            }}
        """)

    def retranslate(self):
        color, icon = self.SEVERITY_KEYS.get(self._severity_key, ('#7F8C8D', '•'))
        label = t(self._severity_key)
        self.icon_label.setText(icon)
        self.type_label.setText(label)
        self.setProperty("severityColor", color)
        self.setStyleSheet(f"""
            QFrame#card {{
                border-right: 4px solid {color};
                border-radius: 4px;
            }}
        """)


class AuditView(QWidget):
    """واجهة التدقيق والمراجعة"""

    def __init__(self):
        super().__init__()
        self._init_labels()
        self.setup_ui()

    def _init_labels(self):
        self._lbl_title = t("audit_title")
        self._lbl_subtitle = t("audit_subtitle")
        self._lbl_run = t("aud_run")
        self._lbl_clear = t("aud_clear")
        self._lbl_errors = t("aud_errors")
        self._lbl_warnings = t("aud_warnings")
        self._lbl_notes = t("aud_notes")
        self._lbl_status = t("aud_status")
        self._lbl_status_not_run = t("aud_status_not_run")
        self._lbl_placeholder = t("aud_placeholder")
        self._lbl_report_placeholder = t("aud_report_placeholder")
        self._lbl_no_data_title = t("aud_no_data_title")
        self._lbl_no_data_msg = t("aud_no_data_msg")
        self._lbl_status_pass = t("aud_status_pass")
        self._lbl_status_fix = t("aud_status_fix")
        self._lbl_result = t("aud_result")
        self._lbl_critical = t("aud_critical")
        self._lbl_warning = t("aud_warning")
        self._lbl_note = t("aud_note")
        self._lbl_value = t("aud_value")
        self._lbl_diff = t("aud_diff")
        self._lbl_no_issues = t("aud_no_issues")
        self._lbl_error = t("error")
        self._lbl_warning_level = t("warning")
        self._lbl_success = t("success")

    def setup_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(self._lbl_title)
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(self._lbl_subtitle)
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.run_audit_btn = QPushButton(self._lbl_run)
        self.run_audit_btn.setObjectName("primaryBtn")
        self.run_audit_btn.clicked.connect(self.run_audit)
        buttons_layout.addWidget(self.run_audit_btn)

        self.clear_btn = QPushButton(self._lbl_clear)
        self.clear_btn.setObjectName("dangerBtn")
        self.clear_btn.clicked.connect(self.clear_results)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("card")
        summary_layout = QGridLayout(self.summary_frame)
        summary_layout.setSpacing(15)

        self.issues_count = self._make_stat_card(self._lbl_errors, "0", "#E74C3C")
        self.warnings_count = self._make_stat_card(self._lbl_warnings, "0", "#F39C12")
        self.notes_count = self._make_stat_card(self._lbl_notes, "0", "#27AE60")
        self.status_card = self._make_stat_card(self._lbl_status, self._lbl_status_not_run, "#7F8C8D")

        summary_layout.addWidget(self.issues_count, 0, 0)
        summary_layout.addWidget(self.warnings_count, 0, 1)
        summary_layout.addWidget(self.notes_count, 0, 2)
        summary_layout.addWidget(self.status_card, 0, 3)

        main_layout.addWidget(self.summary_frame)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("auditScroll")

        scroll_content = QWidget()
        self.results_layout = QVBoxLayout(scroll_content)
        self.results_layout.setSpacing(8)

        self.placeholder_label = QLabel(self._lbl_placeholder)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setObjectName("placeholderLabel")
        self.results_layout.addWidget(self.placeholder_label)

        self.results_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.scroll_area = scroll
        self.scroll_content = scroll_content

        main_layout.addWidget(scroll)

        self.report_browser = QTextBrowser()
        self.report_browser.setMaximumHeight(200)
        self.report_browser.setPlaceholderText(self._lbl_report_placeholder)
        main_layout.addWidget(self.report_browser)

        self.setLayout(main_layout)

    def _make_stat_card(self, title, value, color):
        """إنشاء كارت إحصائي"""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumSize(150, 80)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        card.title_label = QLabel(title)
        card.title_label.setObjectName("cardTitle")
        layout.addWidget(card.title_label)

        value_label = QLabel(value)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        value_label.setFont(font)
        value_label.setObjectName("statValue")
        layout.addWidget(value_label)

        layout.addStretch()
        card.setLayout(layout)

        card.value_label = value_label
        return card

    def run_audit(self):
        """تشغيل التدقيق"""
        if not state.has_data():
            QMessageBox.warning(
                self, self._lbl_no_data_title,
                self._lbl_no_data_msg
            )
            return

        try:
            from modules import AuditEngine

            auditor = AuditEngine()
            data = state.financial_data
            ratios = state.ratios

            auditor.check_balance_sheet(
                data.get('total_assets', 0),
                data.get('total_liabilities', 0),
                data.get('equity', 0)
            )

            auditor.check_negative_values(data)

            auditor.check_ratios_reasonableness(ratios)

            if 'inventory' in data and 'cost_of_goods_sold' in data:
                auditor.check_inventory_sanity(
                    data.get('inventory', 0),
                    data.get('cost_of_goods_sold', 0)
                )

            auditor.check_income_statement(
                data.get('revenue', 0),
                data.get('cost_of_goods_sold', 0),
                data.get('operating_expenses', 0),
                data.get('net_income', 0)
            )

            summary = auditor.get_audit_summary()

            self.issues_count.value_label.setText(str(summary['total_issues']))
            self.warnings_count.value_label.setText(str(summary['total_warnings']))
            self.notes_count.value_label.setText(str(len(summary['notes'])))

            if summary['total_issues'] == 0:
                self.status_card.value_label.setText(self._lbl_status_pass)
                self.status_card.value_label.setProperty("statusColor", "success")
                self.status_card.value_label.style().unpolish(self.status_card.value_label)
                self.status_card.value_label.style().polish(self.status_card.value_label)
            else:
                self.status_card.value_label.setText(self._lbl_status_fix)
                self.status_card.value_label.setProperty("statusColor", "error")
                self.status_card.value_label.style().unpolish(self.status_card.value_label)
                self.status_card.value_label.style().polish(self.status_card.value_label)

            self._display_results(summary)
            self.report_browser.setPlainText(summary['report'])

            if summary['total_issues'] == 0 and summary['total_warnings'] == 0:
                fraud_detector.mark_audit_approved()
                activity_log.log("audit_approved", f"issues=0, warnings=0")
            else:
                fraud_detector.mark_audit_reset()
                activity_log.log("audit_issues_found", f"issues={summary['total_issues']}, warnings={summary['total_warnings']}")

            self.subtitle.setText(
                f"{self._lbl_result} | "
                f"{self._lbl_error}: {summary['total_issues']} | "
                f"{self._lbl_warning_level}: {summary['total_warnings']} | "
                f"{self._lbl_success}: {len(summary['notes'])}"
            )
        except Exception as e:
            from utils.app_logger import get_logger
            get_logger("audit_view").error(f"Audit failed: {e}")
            QMessageBox.critical(self, "Error", str(e))

    def _display_results(self, summary):
        """عرض نتائج التدقيق"""
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        for note in summary.get('notes', []):
            self.results_layout.addWidget(
                AuditItemCard('aud_note', note)
            )

        for warning in summary.get('warnings', []):
            detail = warning.get('note', '')
            if 'value' in warning:
                detail += f" | {t('aud_value')} {warning['value']}"
            self.results_layout.addWidget(
                AuditItemCard('aud_warning', warning['description'], detail)
            )

        for issue in summary.get('issues', []):
            detail = issue.get('description', '')
            if 'difference' in issue:
                detail += f" | {t('aud_diff')} {issue['difference']}"
            self.results_layout.addWidget(
                AuditItemCard('aud_critical', issue['type'], detail)
            )

        if not summary.get('issues') and not summary.get('warnings') and not summary.get('notes'):
            self.results_layout.addWidget(
                AuditItemCard('aud_note', t('aud_no_issues'))
            )

        self.results_layout.addStretch()

    def clear_results(self):
        """مسح النتائج"""
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        self.placeholder_label = QLabel(self._lbl_placeholder)
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setObjectName("placeholderLabel")
        self.results_layout.addWidget(self.placeholder_label)
        self.results_layout.addStretch()

        self.issues_count.value_label.setText("0")
        self.warnings_count.value_label.setText("0")
        self.notes_count.value_label.setText("0")
        self.status_card.value_label.setText(self._lbl_status_not_run)
        self.status_card.value_label.setProperty("statusColor", "neutral")
        self.status_card.value_label.style().unpolish(self.status_card.value_label)
        self.status_card.value_label.style().polish(self.status_card.value_label)

        self.report_browser.clear()
        self.subtitle.setText(self._lbl_subtitle)

    def retranslate(self):
        """تحديث النصوص عند تغيير اللغة"""
        self._init_labels()

        self.title.setText(self._lbl_title)
        self.subtitle.setText(self._lbl_subtitle)
        self.run_audit_btn.setText(self._lbl_run)
        self.clear_btn.setText(self._lbl_clear)

        self.placeholder_label.setText(self._lbl_placeholder)
        self.report_browser.setPlaceholderText(self._lbl_report_placeholder)

        self.issues_count.title_label.setText(self._lbl_errors)
        self.warnings_count.title_label.setText(self._lbl_warnings)
        self.notes_count.title_label.setText(self._lbl_notes)
        self.status_card.title_label.setText(self._lbl_status)
        self.status_card.value_label.setText(self._lbl_status_not_run)
        self.status_card.value_label.setProperty("statusColor", "neutral")
        self.status_card.value_label.style().unpolish(self.status_card.value_label)
        self.status_card.value_label.style().polish(self.status_card.value_label)
