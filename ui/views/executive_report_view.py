# واجهة التقرير التنفيذي الشامل (Executive Report)
# =================================================
# زر واحد يجمّع كل التحليلات: صحة مالية + ملخص + نسب + قوائم + جباية + توصيات
# معاينة HTML + تصدير PDF/Excel.

from ui.views._path import _  # noqa: F401

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser, QMessageBox,
)
from PyQt6.QtCore import Qt

from ui.views._base import BaseView
from ui.resources.i18n import t
from ui.app_state import ThemeColors
from ui import exporters
from modules import executive_report


def _theme_colors():
    """لوحة ألوان متوافقة مع الثيم الحالي (للمعاينة داخل التطبيق)."""
    return {
        "primary": ThemeColors.get("primary"),
        "info": ThemeColors.get("info"),
        "warning": ThemeColors.get("warning"),
        "error": ThemeColors.get("error"),
        "success": ThemeColors.get("success"),
        "text": ThemeColors.get("text"),
        "secondary": ThemeColors.get("text_secondary"),
        "border": ThemeColors.get("text_muted"),
        "muted": ThemeColors.get("text_muted"),
    }


class ExecutiveReportView(BaseView):
    """التقرير التنفيذي الشامل"""

    def __init__(self):
        super().__init__()
        self._report = {}
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self._make_header("er_title", "er_subtitle")

        btns = QHBoxLayout()
        self.generate_btn = QPushButton(t("er_generate"))
        self.generate_btn.clicked.connect(self.refresh)
        btns.addWidget(self.generate_btn)
        self.pdf_btn = QPushButton(t("er_export_pdf"))
        self.pdf_btn.clicked.connect(self._export_pdf)
        btns.addWidget(self.pdf_btn)
        self.excel_btn = QPushButton(t("er_export_excel"))
        self.excel_btn.clicked.connect(self._export_excel)
        btns.addWidget(self.excel_btn)
        btns.addStretch()
        self._main_layout.addLayout(btns)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self._main_layout.addWidget(self.browser)

    def refresh(self):
        self._report = executive_report.build_report()
        self.browser.setHtml(executive_report.render_html(self._report, _theme_colors()))

    # ── Export PDF ───────────────────────────────────────────────────────────

    def _export_pdf(self):
        path = exporters.ask_save_path(
            self, t("er_export_pdf"), "executive_report.pdf", "PDF Files (*.pdf)"
        )
        if not path:
            return
        try:
            from PyQt6.QtPrintSupport import QPrinter
            from PyQt6.QtGui import QTextDocument

            html = self._build_print_html()
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print_(printer)
            QMessageBox.information(self, t("success"), f"✅ {path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))

    def _build_print_html(self):
        body = executive_report.render_html(self._report)
        return (
            '<html lang="ar" dir="rtl"><head><meta charset="UTF-8">'
            "<style>body{font-family:'Amiri','Segoe UI',sans-serif;direction:rtl;"
            "color:#222;} table{width:100%;}</style></head>"
            f"<body>{body}</body></html>"
        )

    # ── Export Excel ─────────────────────────────────────────────────────────

    def _export_excel(self):
        path = exporters.ask_save_path(
            self, t("er_export_excel"), "executive_report.xlsx", "Excel Files (*.xlsx)"
        )
        if not path:
            return
        try:
            wb = exporters.new_workbook()

            # النسب الرئيسية
            ratio_rows = []
            for key, value in self._report.get("key_ratios", []):
                if value is not None:
                    ratio_rows.append((
                        t(executive_report.KEY_RATIOS_KEY.get(key, key)),
                        round(float(value), 2),
                    ))
            exporters.add_excel_sheet(
                wb, t("er_key_ratios")[:31], [t("er_ratio"), t("er_value")],
                ratio_rows, header_fill="7C4DFF"
            )

            # القوائم المالية (ملخص)
            bs = self._report.get("balance_sheet", {})
            inc = self._report.get("income_statement", {})
            cf = self._report.get("cash_flow", {})
            eq = self._report.get("equity_statement", {})
            stmt_rows = [
                (t("er_total_assets"), bs.get("total_assets", 0)),
                (t("er_total_equity"), bs.get("equity_liabilities", {}).get("total_equity", 0)),
                (t("er_gross_profit"), inc.get("gross_profit", 0)),
                (t("er_net_income"), inc.get("net_income", 0)),
                (t("er_operating_cashflow"), cf.get("operating_total", 0)),
                (t("er_ending_cash"), cf.get("cash_ending", 0)),
                (t("er_closing_equity"), eq.get("closing_balance", 0)),
            ]
            exporters.add_excel_sheet(
                wb, t("er_financial_statements")[:31],
                [t("er_statement"), t("er_value")], stmt_rows, header_fill="3B82F6"
            )

            # الملخص الجبائي
            if self._report.get("tax_rows"):
                tax_rows = [(t(k), round(float(v), 2))
                            for k, v in self._report.get("tax_rows", [])]
                exporters.add_excel_sheet(
                    wb, t("er_tax_summary")[:31], [t("er_tax"), t("er_value")],
                    tax_rows, header_fill="F59E0B"
                )

            # التوصيات
            rec_rows = [(
                t("er_priority_" + rec.get("priority", "low")),
                rec.get("action", ""),
                rec.get("impact", ""),
            ) for rec in self._report.get("recommendations", [])]
            exporters.add_excel_sheet(
                wb, t("er_recommendations")[:31],
                [t("er_priority"), t("er_action"), t("er_impact")],
                rec_rows, header_fill="22C55E"
            )

            wb.save(path)
            QMessageBox.information(self, t("success"), f"✅ {path}")
        except Exception as e:
            QMessageBox.critical(self, t("error"), str(e))
