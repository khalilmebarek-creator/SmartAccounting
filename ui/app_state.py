# حالة التطبيق المشتركة بين الواجهات
# ===================================

import json
import os
import tempfile
from utils.app_logger import get_logger
from utils.vault import encrypt, decrypt, is_encrypted

logger = get_logger("app_state")

SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "settings.json"
)

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "accounting_data.json"
)

CHAT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "chat_history.json"
)


def _atomic_write(filepath, data):
    dir_name = os.path.dirname(filepath)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, filepath)
    except Exception as e:
        logger.error(f"Failed to write {filepath}: {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise


def _safe_read(filepath, default=None):
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Corrupted JSON in {filepath}: {e}")
        backup = filepath + ".corrupt"
        try:
            os.replace(filepath, backup)
            logger.info(f"Backed up corrupted file to {backup}")
        except OSError:
            pass
        return default if default is not None else {}
    except Exception as e:
        logger.error(f"Failed to read {filepath}: {e}")
        return default if default is not None else {}


class AppState:
    """
    يحمل البيانات المشتركة بين كل الواجهات
    (البيانات المالية، النسب، التحليلات، الإعدادات)
    """
    def __init__(self):
        self.company_name = ""
        self.company_name_fr = ""
        self.fiscal_year = 2024
        self.company_rc = ""
        self.company_nif = ""
        self.company_address = ""
        self.company_phone = ""
        self.company_email = ""
        self.company_legal_form = ""
        self.company_activity_type = ""
        self.company_bank_account = ""
        self.financial_data = {}
        self.ratios = {}
        self.dupont = {}
        self.working_capital = {}
        self.audit_result = None

        self.tax_data = {}
        self.tax_summary = None
        self.tax_obligations = []

        self.language = "ar"
        self.theme = "light"
        self.api_key = ""
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"

        self._load_settings()
        self.load_data()

    def _load_settings(self):
        data = _safe_read(SETTINGS_FILE)
        if data:
            self.language = data.get("language", "ar")
            self.theme = data.get("theme", "light")
            self.api_key = decrypt(data.get("api_key", ""))
            self.api_url = data.get("api_url", "https://api.openai.com/v1/chat/completions")
            self.model = data.get("model", "gpt-3.5-turbo")

    def save_settings(self):
        data = {
            "language": self.language,
            "theme": self.theme,
            "api_key": encrypt(self.api_key),
            "api_url": self.api_url,
            "model": self.model,
        }
        try:
            _atomic_write(SETTINGS_FILE, data)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def save_data(self):
        data = {
            "company_name": self.company_name,
            "company_name_fr": self.company_name_fr,
            "fiscal_year": self.fiscal_year,
            "company_rc": self.company_rc,
            "company_nif": self.company_nif,
            "company_address": self.company_address,
            "company_phone": self.company_phone,
            "company_email": self.company_email,
            "company_legal_form": self.company_legal_form,
            "company_activity_type": self.company_activity_type,
            "company_bank_account": self.company_bank_account,
            "financial_data": self.financial_data,
            "ratios": self.ratios,
            "dupont": self.dupont,
            "working_capital": self.working_capital,
            "audit_result": self.audit_result,
            "tax_data": self.tax_data,
            "tax_summary": self.tax_summary,
            "tax_obligations": self.tax_obligations,
        }
        try:
            _atomic_write(DATA_FILE, data)
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

    def load_data(self):
        data = _safe_read(DATA_FILE)
        if data:
            self.company_name = data.get("company_name", "")
            self.company_name_fr = data.get("company_name_fr", "")
            self.fiscal_year = data.get("fiscal_year", 2024)
            self.company_rc = data.get("company_rc", "")
            self.company_nif = data.get("company_nif", "")
            self.company_address = data.get("company_address", "")
            self.company_phone = data.get("company_phone", "")
            self.company_email = data.get("company_email", "")
            self.company_legal_form = data.get("company_legal_form", "")
            self.company_activity_type = data.get("company_activity_type", "")
            self.company_bank_account = data.get("company_bank_account", "")
            self.financial_data = data.get("financial_data", {})
            self.ratios = data.get("ratios", {})
            self.dupont = data.get("dupont", {})
            self.working_capital = data.get("working_capital", {})
            self.audit_result = data.get("audit_result", None)
            self.tax_data = data.get("tax_data", {})
            self.tax_summary = data.get("tax_summary", None)
            self.tax_obligations = data.get("tax_obligations", [])

    def clear(self):
        self.company_name = ""
        self.company_name_fr = ""
        self.fiscal_year = 2024
        self.company_rc = ""
        self.company_nif = ""
        self.company_address = ""
        self.company_phone = ""
        self.company_email = ""
        self.company_legal_form = ""
        self.company_activity_type = ""
        self.company_bank_account = ""
        self.financial_data = {}
        self.ratios = {}
        self.dupont = {}
        self.working_capital = {}
        self.audit_result = None
        self.tax_data = {}
        self.tax_summary = None
        self.tax_obligations = []
        if os.path.exists(DATA_FILE):
            backup = DATA_FILE + ".bak"
            try:
                os.replace(DATA_FILE, backup)
                logger.info(f"Data file backed up to {backup}")
            except OSError as e:
                logger.error(f"Failed to backup data file: {e}")

    def has_data(self):
        return bool(self.ratios) or bool(self.financial_data)

    def summary(self):
        from ui.resources.i18n import t
        if not self.ratios:
            return t("summary_no_data")
        tax_info = ""
        if self.tax_summary:
            tax_info = f" | {t('summary_taxes')}: {self.tax_summary.get('total_taxes', 0):,.0f} DZD"
        return (
            f"{t('summary_company')}: {self.company_name} | "
            f"{t('summary_year')}: {self.fiscal_year} | "
            f"ROE: {self.ratios.get('roe', 0):.2f}% | "
            f"Current Ratio: {self.ratios.get('current_ratio', 0):.2f}"
            f"{tax_info}"
        )

    def save_chat_history(self, messages):
        try:
            _atomic_write(CHAT_FILE, messages)
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")

    def load_chat_history(self):
        return _safe_read(CHAT_FILE, [])


state = AppState()


class ThemeColors:
    """ثوابت الألوان حسب الثيم — يستخدمها كل الواجهات"""

    _DARK = {
        "bg": "#1A1A2E",
        "card_bg": "#2A2A3C",
        "text": "#E0E0E0",
        "text_secondary": "#AAAAAA",
        "text_muted": "#888888",
        "border": "#444444",
        "chart_text": "#CCCCCC",
        "chart_edge": "#555555",
        "error": "#E74C3C",
        "success": "#2ECC71",
        "warning": "#F39C12",
        "info": "#3498DB",
        "chart_bg": "#2A2A3C",
        "chart_grid": "#444444",
    }

    _LIGHT = {
        "bg": "#F5F6FA",
        "card_bg": "#FFFFFF",
        "text": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "text_muted": "#999999",
        "border": "#E0E0E0",
        "chart_text": "#7F8C8D",
        "chart_edge": "#FFFFFF",
        "error": "#E74C3C",
        "success": "#2ECC71",
        "warning": "#F39C12",
        "info": "#3498DB",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#EAECEE",
    }

    @classmethod
    def get(cls, key):
        palette = cls._DARK if state.theme == "dark" else cls._LIGHT
        return palette.get(key, "#888888")

    @classmethod
    def chart_palette(cls):
        return ["#3498DB", "#2ECC71", "#E74C3C", "#F39C12", "#9B59B6", "#1ABC9C"]
