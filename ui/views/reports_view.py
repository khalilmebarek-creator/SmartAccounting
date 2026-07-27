# عرض التحليلات المحفوظة والتقارير
# ==================================

from ui.views._path import _  # noqa: F401

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextBrowser, QListWidget,
    QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.app_state import state
from ui.resources.i18n import t


class ReportsView(QWidget):
    """واجهة التقارير والتحليلات المحفوظة"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """إنشاء الواجهة"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel(t("reports_title"))
        self.title.setObjectName("headerTitle")
        main_layout.addWidget(self.title)

        self.subtitle = QLabel(t("reports_subtitle"))
        self.subtitle.setObjectName("headerSubtitle")
        main_layout.addWidget(self.subtitle)

        search_layout = QHBoxLayout()
        self.search_label = QLabel(t("rep_company_label"))
        search_layout.addWidget(self.search_label)

        self.search_input = QPushButton(t("reports_search"))
        self.search_input.setObjectName("primaryBtn")
        self.search_input.clicked.connect(self.refresh_analyses)
        search_layout.addWidget(self.search_input)

        self.search_layout_stretch = search_layout
        main_layout.addLayout(search_layout)

        content_layout = QHBoxLayout()

        self.analyses_list = QListWidget()
        self.analyses_list.itemClicked.connect(self.show_analysis)
        self.analyses_list.setMaximumWidth(350)
        content_layout.addWidget(self.analyses_list)

        self.report_view = QTextBrowser()
        self.report_view.setPlaceholderText(t("rep_placeholder"))
        content_layout.addWidget(self.report_view, 1)

        main_layout.addLayout(content_layout, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.export_txt_btn = QPushButton(t("reports_export_txt"))
        self.export_txt_btn.setObjectName("secondaryBtn")
        self.export_txt_btn.clicked.connect(lambda: self.export_report("txt"))
        buttons_layout.addWidget(self.export_txt_btn)

        self.export_html_btn = QPushButton(t("reports_export_html"))
        self.export_html_btn.setObjectName("secondaryBtn")
        self.export_html_btn.clicked.connect(lambda: self.export_report("html"))
        buttons_layout.addWidget(self.export_html_btn)

        self.export_pdf_btn = QPushButton(t("reports_export_pdf"))
        self.export_pdf_btn.setObjectName("pdfBtn")
        self.export_pdf_btn.clicked.connect(lambda: self.export_report("pdf"))
        buttons_layout.addWidget(self.export_pdf_btn)

        self.export_xlsx_btn = QPushButton(t("reports_export_xlsx"))
        self.export_xlsx_btn.setObjectName("secondaryBtn")
        self.export_xlsx_btn.clicked.connect(lambda: self.export_report("xlsx"))
        buttons_layout.addWidget(self.export_xlsx_btn)

        self.delete_btn = QPushButton(t("reports_delete"))
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self.clear_current)
        buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def retranslate(self):
        self.title.setText(t("reports_title"))
        self.subtitle.setText(t("reports_subtitle"))
        self.search_label.setText(t("rep_company_label"))
        self.search_input.setText(t("reports_search"))
        self.report_view.setPlaceholderText(t("rep_placeholder"))
        self.export_txt_btn.setText(t("reports_export_txt"))
        self.export_html_btn.setText(t("reports_export_html"))
        self.export_pdf_btn.setText(t("reports_export_pdf"))
        self.export_xlsx_btn.setText(t("reports_export_xlsx"))
        self.delete_btn.setText(t("reports_delete"))

    def refresh_analyses(self):
        """تحديث قائمة التحليلات"""
        company, ok = QInputDialog.getText(
            self, t("rep_query"),
            t("rep_query_prompt"),
            text=""
        )
        if not ok:
            return

        self.analyses_list.clear()
        if not company.strip():
            company = t("rep_company_default")

        try:
            from database import get_company_analyses
            results = get_company_analyses(company)

            if not results:
                QMessageBox.information(self, t("info"), t("reports_no_data"))
                return

            for r in results:
                display = f"📊 {r['company_name']} - {r['year']}\n"
                display += f"   ROE: {r['roe']}% | Current: {r['current_ratio']}"
                self.analyses_list.addItem(display)

            self._current_results = results
            self._current_company = company

        except Exception as e:
            QMessageBox.critical(self, t("error"), f"{t('rep_query_error')} {e}")

    def show_analysis(self, item):
        """عرض تفاصيل التحليل المحدد"""
        try:
            index = self.analyses_list.currentRow()
            if index < 0 or not hasattr(self, '_current_results'):
                return

            r = self._current_results[index]

            report = f"""
╔══════════════════════════════════════════════════════════════╗
║           📊 {t('rep_report_title')}                            ║
╚══════════════════════════════════════════════════════════════╝

🏢 {t('rep_company')} {r['company_name']}
📅 {t('rep_year')} {r['year']}
🔢 {t('rep_fiscal_id')} {r['fiscal_year_id']}

{'='*64}
📈 {t('rep_ratios_main')}
{'='*64}

💧 {t('rep_liquidity')}
   • {t('rep_current_ratio')} {r['current_ratio']}

💰 {t('rep_profitability')}
   • {t('rep_net_margin')} {r['net_profit_margin']}%
   • {t('rep_roe')} {r['roe']}%

📊 {t('rep_leverage')}
   • {t('rep_de_ratio')} {r['debt_to_equity']}

{'='*64}
💼 {t('rep_balance_data')}
{'='*64}

   • {t('rep_total_assets')} {r['total_assets']:,.2f}
   • {t('rep_total_liabilities')} {r['total_liabilities']:,.2f}
   • {t('rep_total_equity')} {r['total_equity']:,.2f}

{'='*64}
"""
            self.report_view.setPlainText(report)
        except Exception as e:
            QMessageBox.critical(self, t("error"), t("error_display_analysis").format(e=e))

    def export_report(self, format_type):
        """تصدير التقرير الحالي"""
        current_text = self.report_view.toPlainText()
        if not current_text:
            QMessageBox.warning(self, t("warning"), t("reports_no_report"))
            return

        format_config = {
            "txt": ("Text Files (*.txt)", "txt"),
            "html": ("HTML Files (*.html)", "html"),
            "pdf": ("PDF Files (*.pdf)", "pdf"),
            "xlsx": ("Excel Files (*.xlsx)", "xlsx"),
        }

        file_filter, ext = format_config.get(format_type, ("All Files (*)", "txt"))

        file_path, _ = QFileDialog.getSaveFileName(
            self, t("rep_save_title"), f"report.{ext}", file_filter
        )
        if not file_path:
            return

        try:
            if format_type == "html":
                from ui.views._html_export import render_html_report
                html_content = render_html_report(current_text, t('rep_html_title'))
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            elif format_type == "xlsx":
                from modules.reporting import ReportGenerator
                reporter = ReportGenerator(state.company_name, state.fiscal_year)
                success = reporter.export_to_excel(
                    file_path,
                    financial_data=state.financial_data if state.has_data() else None,
                    ratios=state.ratios if state.ratios else None,
                )
                if not success:
                    QMessageBox.critical(self, t("error"), t("reports_fail"))
                    return
            elif format_type == "pdf":
                from modules.reporting import ReportGenerator
                reporter = ReportGenerator(state.company_name, state.fiscal_year)
                success = reporter.export_to_pdf(current_text, file_path)
                if not success:
                    QMessageBox.critical(self, t("error"), t("rep_pdf_fail"))
                    return
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_text)

            QMessageBox.information(self, t("success"), f"{t('reports_success')}\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), f"{t('reports_fail')} {e}")

    def clear_current(self):
        """حذف التحليل المحدد من قاعدة البيانات"""
        index = self.analyses_list.currentRow()
        if index < 0 or not hasattr(self, '_current_results'):
            return
        r = self._current_results[index]
        reply = QMessageBox.question(
            self, t("confirm_delete_title"),
            f"{t('reports_delete_confirm')}\n{r['company_name']} - {r['year']}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            from database import delete_analysis
            ok = delete_analysis(r['company_name'], r['year'])
            if ok:
                self.analyses_list.takeItem(index)
                self.report_view.clear()
                self._current_results.pop(index)
                from ui.widgets.toast import toast_success
                toast_success(self, t("reports_delete_success"))
            else:
                from ui.widgets.toast import toast_error
                toast_error(self, t("reports_delete_fail"))
        except Exception as e:
            from ui.widgets.toast import toast_error
            toast_error(self, f"{e}")
