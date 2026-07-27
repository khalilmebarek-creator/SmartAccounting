# تذكيرات المواعيد الضريبية - Algeria Tax Calendar
# ===================================================

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from utils.app_logger import get_logger

logger = get_logger("tax_reminders")

REMINDERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "tax_reminders.json"
)

ALGERIAN_TAX_CALENDAR = {
    "tva_monthly": {
        "name_ar": "إقرار TVA الشهري",
        "name_en": "Monthly VAT Declaration",
        "name_fr": "Déclaration TVA mensuelle",
        "frequency": "monthly",
        "due_day": 20,
        "description_ar": "تقديم إقرار ضريبة القيمة المضافة الشهري",
        "description_en": "Submit monthly Value Added Tax declaration",
        "tax_type": "TVA",
        "form_number": "DAI/01",
    },
    "ibs_quarterly": {
        "name_ar": "تقديم IBS quarterly",
        "name_en": "Quarterly IBS Payment",
        "name_fr": "Acompte IBS trimestriel",
        "frequency": "quarterly",
        "due_months": [3, 6, 9, 12],
        "due_day": 20,
        "description_ar": "تقديم دفعة مقدمة من ضريبة الدخل للمؤسسات",
        "description_en": "Submit advance installment of Corporate Income Tax",
        "tax_type": "IBS",
        "form_number": "TS/01",
    },
    "ibs_annual": {
        "name_ar": "الإقرار السنوي IBS",
        "name_en": "Annual IBS Declaration",
        "name_fr": "Déclaration annuelle IBS",
        "frequency": "annual",
        "due_month": 4,
        "due_day": 30,
        "description_ar": "تقديم الإقرار السنوي لضريبة الدخل للمؤسسات",
        "description_en": "Submit annual Corporate Income Tax declaration",
        "tax_type": "IBS",
        "form_number": "TS/02",
    },
    "irg_annual": {
        "name_ar": "الإقرار السنوي IRG",
        "name_en": "Annual IRG Declaration",
        "name_fr": "Déclaration annuelle IRG",
        "frequency": "annual",
        "due_month": 2,
        "due_day": 28,
        "description_ar": "تقديم الإقرار السنوي لضريبة الدخل الفردي",
        "description_en": "Submit annual Personal Income Tax declaration",
        "tax_type": "IRG",
        "form_number": "DAI/03",
    },
    "cnas_monthly": {
        "name_ar": "تصريح CNAS الشهري",
        "name_en": "Monthly CNAS Declaration",
        "name_fr": "Déclaration CNAS mensuelle",
        "frequency": "monthly",
        "due_day": 30,
        "description_ar": "تقديم تصريح الضمان الاجتماعي الشهري",
        "description_en": "Submit monthly social security declaration",
        "tax_type": "CNAS",
        "form_number": "DAS/01",
    },
    "cnac_quarterly": {
        "name_ar": "تصريح CNAC ربع سنوي",
        "name_en": "Quarterly CNAC Declaration",
        "name_fr": "Déclaration CNAC trimestrielle",
        "frequency": "quarterly",
        "due_months": [3, 6, 9, 12],
        "due_day": 30,
        "description_ar": "تقديم تصريح التأمينات الاجتماعية الإجبارية",
        "description_en": "Submit mandatory social insurance declaration",
        "tax_type": "CNAC",
    },
    "accounting_close": {
        "name_ar": "إقفال الحسابات السنوي",
        "name_en": "Annual Account Closing",
        "name_fr": "Clôture annuelle des comptes",
        "frequency": "annual",
        "due_month": 6,
        "due_day": 30,
        "description_ar": "إقفال الحسابات وتحضير الميزانية العمومية",
        "description_en": "Close accounts and prepare balance sheet",
        "tax_type": "Accounting",
    },
    "audit_declaration": {
        "name_ar": "تصريح المراجعة الحسابية",
        "name_en": "Audit Declaration",
        "name_fr": "Déclaration d'audit",
        "frequency": "annual",
        "due_month": 9,
        "due_day": 30,
        "description_ar": "تقديم التصريح الخاص بالمراجعة الحسابية",
        "description_en": "Submit the accounting audit declaration",
        "tax_type": "Audit",
    },
}


class TaxReminderManager:
    """مدير تذكيرات المواعيد الضريبية"""

    def __init__(self):
        self.reminders = self._load_reminders()
        self.custom_reminders = self.reminders.get("custom", [])
        self.acknowledged = self.reminders.get("acknowledged", [])

    def _load_reminders(self) -> Dict:
        if os.path.exists(REMINDERS_FILE):
            try:
                with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"custom": [], "acknowledged": []}

    def _save_reminders(self):
        try:
            with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "custom": self.custom_reminders,
                    "acknowledged": self.acknowledged
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save reminders: {e}")

    def get_upcoming_reminders(self, days_ahead: int = 30) -> List[Dict]:
        """الحصول على التذكيرات القادمة خلال عدد أيام محدد"""
        today = datetime.now()
        upcoming = []

        for key, tax in ALGERIAN_TAX_CALENDAR.items():
            due_date = self._calculate_next_due(tax, today)
            if due_date and due_date <= today + timedelta(days=days_ahead):
                days_until = (due_date - today).days
                reminder_id = f"{key}_{due_date.strftime('%Y%m')}"
                upcoming.append({
                    "id": reminder_id,
                    "key": key,
                    "name_ar": tax["name_ar"],
                    "name_en": tax["name_en"],
                    "name_fr": tax.get("name_fr", tax["name_en"]),
                    "description_ar": tax["description_ar"],
                    "description_en": tax["description_en"],
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "days_until": days_until,
                    "tax_type": tax.get("tax_type", ""),
                    "form_number": tax.get("form_number", ""),
                    "severity": "urgent" if days_until <= 3 else "warning" if days_until <= 7 else "info",
                    "acknowledged": reminder_id in self.acknowledged,
                })

        upcoming.sort(key=lambda x: x["due_date"])
        return upcoming

    def _calculate_next_due(self, tax: Dict, from_date: datetime) -> Optional[datetime]:
        """حساب تاريخ الاستحقاق التالي"""
        freq = tax.get("frequency")
        due_day = tax.get("due_day", 15)

        if freq == "monthly":
            next_month = from_date.month + 1 if from_date.day > due_day else from_date.month
            next_year = from_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            try:
                return datetime(next_year, next_month, due_day)
            except ValueError:
                return datetime(next_year, next_month, 28)

        elif freq == "quarterly":
            due_months = tax.get("due_months", [3, 6, 9, 12])
            for m in sorted(due_months):
                try:
                    due = datetime(from_date.year, m, due_day)
                    if due >= from_date:
                        return due
                except ValueError:
                    continue
            for m in sorted(due_months):
                try:
                    return datetime(from_date.year + 1, m, due_day)
                except ValueError:
                    continue

        elif freq == "annual":
            due_month = tax.get("due_month", 4)
            try:
                due = datetime(from_date.year, due_month, due_day)
                if due >= from_date:
                    return due
                return datetime(from_date.year + 1, due_month, due_day)
            except ValueError:
                return datetime(from_date.year + 1, due_month, 28)

        return None

    def acknowledge_reminder(self, reminder_id: str):
        """تأكيد استلام التذكير"""
        if reminder_id not in self.acknowledged:
            self.acknowledged.append(reminder_id)
            self._save_reminders()

    def add_custom_reminder(self, name: str, due_date: str, description: str = "",
                            tax_type: str = "Custom") -> bool:
        """إضافة تذكير مخصص"""
        try:
            reminder = {
                "name": name,
                "due_date": due_date,
                "description": description,
                "tax_type": tax_type,
                "created": datetime.now().strftime("%Y-%m-%d"),
            }
            self.custom_reminders.append(reminder)
            self._save_reminders()
            logger.info(f"Custom reminder added: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom reminder: {e}")
            return False

    def remove_custom_reminder(self, index: int) -> bool:
        """حذف تذكير مخصص"""
        if 0 <= index < len(self.custom_reminders):
            self.custom_reminders.pop(index)
            self._save_reminders()
            return True
        return False

    def get_calendar_summary(self, year: int = None) -> Dict[str, List]:
        """ملخص التقويم الضريبي للسنة"""
        if year is None:
            year = datetime.now().year

        monthly = {}
        for month in range(1, 13):
            monthly[month] = []

        for key, tax in ALGERIAN_TAX_CALENDAR.items():
            freq = tax.get("frequency")
            due_day = tax.get("due_day", 15)

            if freq == "monthly":
                for m in range(1, 13):
                    try:
                        due = datetime(year, m, due_day)
                        monthly[m].append({
                            "name_ar": tax["name_ar"],
                            "name_en": tax["name_en"],
                            "tax_type": tax.get("tax_type", ""),
                            "form_number": tax.get("form_number", ""),
                        })
                    except ValueError:
                        pass

            elif freq == "quarterly":
                for m in tax.get("due_months", []):
                    try:
                        due = datetime(year, m, due_day)
                        monthly[m].append({
                            "name_ar": tax["name_ar"],
                            "name_en": tax["name_en"],
                            "tax_type": tax.get("tax_type", ""),
                        })
                    except ValueError:
                        pass

            elif freq == "annual":
                m = tax.get("due_month", 4)
                try:
                    monthly[m].append({
                        "name_ar": tax["name_ar"],
                        "name_en": tax["name_en"],
                        "tax_type": tax.get("tax_type", ""),
                    })
                except ValueError:
                    pass

        return monthly


tax_reminders = TaxReminderManager()
