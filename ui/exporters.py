# -*- coding: utf-8 -*-
"""طبقة التصدير الموحدة — أدوات مشتركة لتصدير PDF/Excel عبر الشاشات

تجمّع الأنماط المتكررة في كل الشاشات:
  - مربع الحفظ الموحد (QFileDialog)
  - تنسيق رأس أوراق Excel (openpyxl)
  - حفظ أشكال matplotlib في PDF واحد (PdfPages)
"""
from PyQt5.QtWidgets import QFileDialog
from openpyxl.styles import Font, PatternFill

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2980B9", end_color="2980B9",
                          fill_type="solid")


def ask_save_path(parent, caption, default_name, file_filter):
    """مربع حفظ موحد — يعيد المسار المختار أو None عند الإلغاء."""
    path, _ = QFileDialog.getSaveFileName(parent, caption, default_name,
                                          file_filter)
    return path or None


def style_header_row(ws, row=1):
    """تنسيق موحد لصف الرأس (خط أبيض عريض على خلفية زرقاء)."""
    for cell in ws[row]:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL


def write_charts_pdf(path, figures):
    """حفظ عدة أشكال matplotlib في ملف PDF واحد (150dpi، بلا هوامش)."""
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(path) as pdf:
        for fig in figures:
            pdf.savefig(fig, dpi=150, bbox_inches="tight")
