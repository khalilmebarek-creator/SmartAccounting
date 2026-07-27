"""Report templates system for generating professional reports."""

import json
import os
from datetime import datetime
from utils.app_logger import get_logger

logger = get_logger("report_templates")

TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates"
)

DEFAULT_TEMPLATES = {
    "financial_summary": {
        "name": "التقرير المالي الشامل",
        "name_en": "Financial Summary",
        "description": "تقرير شامل يتضمن الميزانية العمومية وقائمة الدخل",
        "sections": ["balance_sheet", "income_statement", "ratios", "charts"],
        "language": "ar",
        "format": "pdf",
        "company_logo": True,
        "charts_included": True,
    },
    "monthly_report": {
        "name": "التقرير الشهري",
        "name_en": "Monthly Report",
        "description": "تقرير شامل لأداء الشهر",
        "sections": ["summary", "revenue", "expenses", "variance"],
        "language": "ar",
        "format": "pdf",
        "company_logo": True,
        "charts_included": True,
    },
    "tax_report": {
        "name": "التقرير الجبائي",
        "name_en": "Tax Report",
        "description": "تقرير بالالتزامات الجبائية",
        "sections": ["tva", "cnas", "cnac", "is", "patente"],
        "language": "ar",
        "format": "pdf",
        "company_logo": True,
        "charts_included": False,
    },
    "cashflow_report": {
        "name": "تقرير التدفق النقدي",
        "name_en": "Cash Flow Report",
        "description": "تحليل التدفقات النقدية",
        "sections": ["operating", "investing", "financing", "net_flow"],
        "language": "ar",
        "format": "pdf",
        "company_logo": True,
        "charts_included": True,
    },
    "audit_report": {
        "name": "تقرير التدقيق والمراجعة",
        "name_en": "Audit Report",
        "description": "تقرير التدقيق الداخلي ونتائج المراجعة",
        "sections": ["checks", "anomalies", "fraud", "recommendations"],
        "language": "ar",
        "format": "pdf",
        "company_logo": True,
        "charts_included": False,
    },
    "budget_vs_actual": {
        "name": "تقرير الموازنة مقابل الفعلي",
        "name_en": "Budget vs Actual",
        "description": "مقارنة الموازنة المخططة بالإنفاق الفعلي",
        "sections": ["budget_summary", "variance_analysis", "alerts"],
        "language": "ar",
        "format": "pdf",
        "company_logo": True,
        "charts_included": True,
    },
    "executive_summary": {
        "name": "ملخص تنفيذي",
        "name_en": "Executive Summary",
        "description": "ملخص مختصر للمسؤولين/executives",
        "sections": ["kpi_highlights", "key_metrics", "recommendations"],
        "language": "ar",
        "format": "pdf",
        "company_logo": True,
        "charts_included": True,
    },
}


class ReportTemplates:
    """Manages report templates for professional output."""

    def __init__(self):
        self._templates = {}
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        self._load()

    def _load(self):
        custom_file = os.path.join(TEMPLATES_DIR, "custom_templates.json")
        if os.path.exists(custom_file):
            try:
                with open(custom_file, "r", encoding="utf-8") as f:
                    self._templates = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load templates: {e}")
        self._templates.update(DEFAULT_TEMPLATES)

    def _save(self):
        custom = {k: v for k, v in self._templates.items() if k not in DEFAULT_TEMPLATES}
        custom_file = os.path.join(TEMPLATES_DIR, "custom_templates.json")
        try:
            with open(custom_file, "w", encoding="utf-8") as f:
                json.dump(custom, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")

    def get_template(self, template_id: str) -> dict:
        return self._templates.get(template_id, None)

    def get_all_templates(self) -> dict:
        return dict(self._templates)

    def create_template(self, template_id: str, template_data: dict) -> bool:
        if template_id in DEFAULT_TEMPLATES:
            return False
        self._templates[template_id] = template_data
        self._save()
        return True

    def update_template(self, template_id: str, updates: dict) -> bool:
        if template_id not in self._templates:
            return False
        self._templates[template_id].update(updates)
        self._save()
        return True

    def delete_template(self, template_id: str) -> bool:
        if template_id in DEFAULT_TEMPLATES:
            return False
        if template_id in self._templates:
            del self._templates[template_id]
            self._save()
            return True
        return False

    def get_sections_for_template(self, template_id: str) -> list:
        tmpl = self._templates.get(template_id, {})
        return tmpl.get("sections", [])

    def generate_report_header(self, template_id: str, company_name: str = "") -> str:
        tmpl = self._templates.get(template_id, {})
        title = tmpl.get("name", "تقرير")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="utf-8"><style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #333; }}
h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
.header {{ text-align: center; margin-bottom: 30px; }}
.meta {{ color: #666; font-size: 14px; }}
</style></head>
<body>
<div class="header">
<h1>{title}</h1>
<p class="meta">{company_name} | {now}</p>
</div>
"""
        return header

    def generate_report_footer(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"""
<div style="margin-top: 40px; padding-top: 10px; border-top: 1px solid #ddd;
            text-align: center; color: #999; font-size: 12px;">
Smart Accounting Platform v2.5.0 | Generated: {now}
</div>
</body></html>
"""


report_templates = ReportTemplates()
