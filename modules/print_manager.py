# إدارة الطباعة المباشرة
# =======================

import os
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any
from utils.app_logger import get_logger

logger = get_logger("print_manager")


class PrintManager:
    """فئة لإدارة الطباعة المباشرة من التطبيق"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sap_print_")

    def print_html(self, html_content: str, title: str = "Smart Accounting Platform",
                   landscape: bool = False) -> bool:
        """طباعة محتوى HTML مباشرة"""
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt5.QtWebEngineWidgets import QWebEnginePage
            from PyQt5.QtGui import QPageLayout
            from PyQt5.QtCore import QEventLoop

            if not QApplication.instance():
                return False

            printer = QPrinter(QPrinter.HighResolution)
            if landscape:
                printer.setPageOrientation(QPageLayout.Landscape)

            dialog = QPrintDialog(printer)
            if dialog.exec_() != QPrintDialog.Accepted:
                return False

            page = QWebEnginePage()
            loop = QEventLoop()
            page.loadFinished.connect(loop.quit)
            page.setHtml(html_content)
            loop.exec_()

            def on_printed(ok):
                if ok:
                    logger.info("Document printed successfully")
                else:
                    logger.error("Print failed")

            page.print(printer, on_printed)
            return True

        except ImportError:
            logger.warning("QtWebEngine not available, falling back to file print")
            return self._print_via_temp_file(html_content, title)
        except Exception as e:
            logger.error(f"Print error: {e}")
            return False

    def _print_via_temp_file(self, html_content: str, title: str) -> bool:
        """طباعة عبر ملف مؤقت"""
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt5.QtGui import QTextDocument

            if not QApplication.instance():
                return False

            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer)
            if dialog.exec_() != QPrintDialog.Accepted:
                return False

            doc = QTextDocument()
            doc.setHtml(html_content)
            doc.print_(printer)
            logger.info("Printed via QTextDocument fallback")
            return True

        except Exception as e:
            logger.error(f"Fallback print error: {e}")
            return False

    def generate_report_html(self, title: str, sections: list,
                             company_name: str = "", fiscal_year: str = "") -> str:
        """توليد تقرير HTML جاهز للطباعة"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  body {{ font-family: 'Amiri', Arial, sans-serif; margin: 40px; color: #333; direction: rtl; }}
  .header {{ text-align: center; border-bottom: 3px solid #2980B9; padding-bottom: 15px; margin-bottom: 25px; }}
  .header h1 {{ color: #2980B9; margin: 0; font-size: 24px; }}
  .header .meta {{ color: #666; font-size: 12px; margin-top: 8px; }}
  .section {{ margin-bottom: 20px; page-break-inside: avoid; }}
  .section h2 {{ color: #2C3E50; border-right: 4px solid #2980B9; padding-right: 12px; font-size: 18px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
  th {{ background: #2980B9; color: white; padding: 10px 12px; text-align: right; font-size: 13px; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #ddd; text-align: right; }}
  tr:nth-child(even) {{ background: #f8f9fa; }}
  .total {{ font-weight: bold; background: #ecf0f1 !important; }}
  .positive {{ color: #27AE60; }}
  .negative {{ color: #E74C3C; }}
  .footer {{ text-align: center; margin-top: 30px; padding-top: 15px; border-top: 2px solid #ddd; color: #999; font-size: 11px; }}
  @media print {{
    body {{ margin: 20px; }}
    .no-print {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  {"<div class='meta'>الشركة: " + company_name + "</div>" if company_name else ""}
  {"<div class='meta'>السنة المالية: " + fiscal_year + "</div>" if fiscal_year else ""}
  <div class="meta">تاريخ الطباعة: {now}</div>
</div>
"""

        for section in sections:
            html += f'<div class="section">\n<h2>{section.get("title", "")}</h2>\n'
            rows = section.get("rows", [])
            if rows:
                headers = section.get("headers", [])
                if headers:
                    html += "<table><thead><tr>"
                    for h in headers:
                        html += f"<th>{h}</th>"
                    html += "</tr></thead><tbody>\n"
                for row in rows:
                    html += "<tr>"
                    for cell in row:
                        css_class = ""
                        if isinstance(cell, (int, float)):
                            if cell > 0:
                                css_class = ' class="positive"'
                            elif cell < 0:
                                css_class = ' class="negative"'
                            cell = f"{cell:,.2f}"
                        html += f"<td{css_class}>{cell}</td>"
                    html += "</tr>\n"
                if headers:
                    html += "</tbody></table>\n"
            content = section.get("content", "")
            if content:
                html += f"<p>{content}</p>\n"
            html += "</div>\n"

        html += f"""
<div class="footer">
  <p>Smart Accounting Platform - {now}</p>
  <p>هذه الوثيقة تم توليدها تلقائياً</p>
</div>
</body></html>"""
        return html

    def print_financial_report(self, company_name: str, fiscal_year: str,
                                data: Dict[str, Any]) -> bool:
        """طباعة التقرير المالي"""
        sections = []

        if "income" in data:
            inc = data["income"]
            sections.append({
                "title": "قائمة الدخل",
                "headers": ["البيان", "المبلغ (دج)"],
                "rows": [
                    ("الإيرادات", inc.get("revenue", 0)),
                    ("تكلفة المبيعات", inc.get("cogs", 0)),
                    ("إجمالي الربح", inc.get("gross_profit", 0)),
                    ("المصاريف التشغيلية", inc.get("operating_expenses", 0)),
                    ("صافي الدخل", inc.get("net_income", 0)),
                ]
            })

        if "balance" in data:
            bal = data["balance"]
            sections.append({
                "title": "الميزانية العمومية",
                "headers": ["البيان", "المبلغ (دج)"],
                "rows": [
                    ("الأصول المتداولة", bal.get("current_assets", 0)),
                    ("الأصول الثابتة", bal.get("fixed_assets", 0)),
                    ("إجمالي الأصول", bal.get("total_assets", 0)),
                    ("الخصوم المتداولة", bal.get("current_liabilities", 0)),
                    ("الخصوم طويلة الأجل", bal.get("long_term_liabilities", 0)),
                    ("حقوق الملكية", bal.get("equity", 0)),
                ]
            })

        if "ratios" in data:
            rat = data["ratios"]
            rows = []
            ratio_names = {
                "current_ratio": "نسبة التداول",
                "quick_ratio": "نسبة السرعة",
                "debt_to_equity": "نسبة الدين لحقوق الملكية",
                "net_profit_margin": "هامش صافي الربح (%)",
                "roa": "العائد على الأصول (%)",
                "roe": "العائد على حقوق الملكية (%)",
            }
            for key, label in ratio_names.items():
                if key in rat:
                    rows.append((label, f"{rat[key]:.2f}"))
            if rows:
                sections.append({"title": "النسب المالية", "headers": ["النسبة", "القيمة"], "rows": rows})

        html = self.generate_report_html("التقرير المالي", sections, company_name, fiscal_year)
        return self.print_html(html, f"Financial Report - {company_name}")

    def save_and_print_html(self, html_content: str, title: str = "Report") -> Optional[str]:
        """حفظ ملف HTML مؤقت وإرجاع المسار"""
        safe_title = "".join(c if c.isalnum() else "_" for c in title)
        filepath = os.path.join(self.temp_dir, f"{safe_title}_{datetime.now():%Y%m%d_%H%M%S}.html")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save HTML: {e}")
            return None

    def cleanup(self):
        """تنظيف الملفات المؤقتة"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass


print_manager = PrintManager()
