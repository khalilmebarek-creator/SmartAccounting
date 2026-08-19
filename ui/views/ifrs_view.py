# واجهة التقارير المعيارية IFRS/IAS
# =================================
# قوائم مالية معيارية + تصدير PDF/Excel + معاينة

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QMessageBox, QFileDialog, QFrame
)

from ui.views._base import BaseView
from ui.resources.i18n import t
from modules.ifrs_reporting import IFRSReporter, ifrs_reporter
from ui.app_state import state


class IFRSView(BaseView):

    def __init__(self):
        super().__init__()
        self._reporter = IFRSReporter(
            state.company_name or "",
            state.fiscal_year or "",
        )
        self.setup_ui()

    def setup_ui(self):
        self._make_header("ifrs_title", "ifrs_subtitle")

        info_card = self._make_card("ifrs_info")
        info = QHBoxLayout()
        info.addWidget(QLabel(f"{t('ifrs_company')} {state.company_name or '-'}"))
        info.addWidget(QLabel(f"{t('ifrs_year')} {state.fiscal_year or '-'}"))
        info.addStretch()
        info_card.layout().addLayout(info)
        self._main_layout.addWidget(info_card)

        actions_card = self._make_card("ifrs_actions")
        actions = QHBoxLayout()
        for label, slot in [
            ("ifrs_generate", self.generate),
            ("ifrs_export_pdf", self._export_pdf),
            ("ifrs_export_excel", self._export_excel),
        ]:
            btn = QPushButton(t(label))
            btn.clicked.connect(slot)
            actions.addWidget(btn)
        actions.addStretch()
        actions_card.layout().addLayout(actions)
        self._main_layout.addWidget(actions_card)

        self._report_view = QTextEdit()
        self._report_view.setReadOnly(True)
        self._report_view.setPlaceholderText(t("ifrs_placeholder"))
        self._main_layout.addWidget(self._report_view, 1)

        self._main_layout.addStretch()

    def generate(self):
        if not state.has_data():
            QMessageBox.warning(self, t("ifrs_title"), t("ifrs_no_data"))
            return
        self._reporter = IFRSReporter(state.company_name, state.fiscal_year)
        report = self._reporter.full_report(state.financial_data, state.ratios)
        text = self._reporter._format_text(report)
        self._report_view.setPlainText(text)

    def _export_pdf(self):
        if not state.has_data():
            QMessageBox.warning(self, t("ifrs_title"), t("ifrs_no_data"))
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("ifrs_export_pdf"), "ifrs_report.pdf",
            "PDF Files (*.pdf)")
        if not path:
            return
        self._reporter = IFRSReporter(state.company_name, state.fiscal_year)
        if self._reporter.export_pdf(state.financial_data, path, state.ratios):
            QMessageBox.information(self, t("ifrs_title"), t("ifrs_export_ok"))
        else:
            QMessageBox.warning(self, t("ifrs_title"), t("ifrs_export_fail"))

    def _export_excel(self):
        if not state.has_data():
            QMessageBox.warning(self, t("ifrs_title"), t("ifrs_no_data"))
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("ifrs_export_excel"), "ifrs_report.xlsx",
            "Excel Files (*.xlsx)")
        if not path:
            return
        self._reporter = IFRSReporter(state.company_name, state.fiscal_year)
        if self._reporter.export_excel(state.financial_data, path, state.ratios):
            QMessageBox.information(self, t("ifrs_title"), t("ifrs_export_ok"))
        else:
            QMessageBox.warning(self, t("ifrs_title"), t("ifrs_export_fail"))
