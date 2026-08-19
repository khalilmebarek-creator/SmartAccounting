from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser,
    QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont

from ui.app_state import state
from ui.resources.i18n import t
from modules.cashflow import CashFlowStatement


class CashFlowView(QWidget):

    def __init__(self):
        super().__init__()
        self.cashflow_engine = CashFlowStatement()
        self._last_results = None
        self._last_report = ""
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(t("cf_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("cf_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.calc_btn = QPushButton(t("cf_calculate"))
        self.calc_btn.setObjectName("primaryBtn")
        self.calc_btn.setMinimumHeight(40)
        self.calc_btn.clicked.connect(self._calculate_cash_flow)
        btn_layout.addWidget(self.calc_btn)

        self.export_btn = QPushButton(t("cf_export"))
        self.export_btn.setObjectName("secondaryBtn")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self._export)
        self.export_btn.setEnabled(False)
        btn_layout.addWidget(self.export_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.report_browser = QTextBrowser()
        self.report_browser.setPlaceholderText(t("cf_placeholder"))
        self.report_browser.setFont(QFont("Consolas", 10))
        main_layout.addWidget(self.report_browser, 1)

        self.setLayout(main_layout)

    def refresh(self):
        if not state.has_data():
            self.subtitle.setText(t("dashboard_no_data"))
            return
        self.subtitle.setText(
            f"{t('dash_company_label')} {state.company_name} | "
            f"{t('dash_fiscal_label')} {state.fiscal_year}"
        )

    def retranslate(self):
        self.title.setText(t("cf_title"))
        self.subtitle.setText(t("cf_subtitle"))
        self.calc_btn.setText(t("cf_calculate"))
        self.export_btn.setText(t("cf_export"))
        self.report_browser.setPlaceholderText(t("cf_placeholder"))
        self.refresh()

    def _calculate_cash_flow(self):
        if not state.has_data():
            QMessageBox.warning(self, t("warning"), t("cf_no_data"))
            return

        fd = state.financial_data
        if not fd:
            QMessageBox.warning(self, t("warning"), t("cf_no_data"))
            return

        results = self.cashflow_engine.calculate(fd)
        self._last_results = results
        report = self.cashflow_engine.generate_report(results)
        self._last_report = report

        import html as _html
        html = (
            '<pre style="font-family: Consolas, monospace; font-size: 11pt; '
            'direction: ltr; text-align: left;">'
            f'{_html.escape(report)}'
            '</pre>'
        )
        self.report_browser.setHtml(html)
        self.export_btn.setEnabled(True)

    def _export(self):
        if not self._last_report:
            QMessageBox.warning(self, t("warning"), t("cf_no_report"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, t("cf_save_title"), "cashflow.txt",
            "Text Files (*.txt);;HTML Files (*.html)"
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(".html"):
                from ui.views._html_export import render_html_report
                content = render_html_report(self._last_report, "Cash Flow Statement")
            else:
                content = self._last_report

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            QMessageBox.information(self, t("success"), f"{t('reports_success')}\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), f"{t('reports_fail')} {e}")
