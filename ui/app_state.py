# حالة التطبيق المشتركة بين الواجهات
# ===================================

import json
import os
import tempfile
from utils.app_logger import get_logger
from utils.vault import encrypt, decrypt

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

        self.scenarios = {}

        self.language = "ar"
        self.theme = "light"
        self.api_key = ""
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"

        self.base_currency = "DZD"
        self.exchange_rates = {}

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
            self.base_currency = data.get("base_currency", "DZD")
            self.exchange_rates = data.get("exchange_rates", {})
            try:
                from modules.currency import currency_engine
                currency_engine.load_from_dict({
                    "base_currency": self.base_currency,
                    "rates": self.exchange_rates,
                })
            except Exception:
                pass

    def save_settings(self):
        try:
            from modules.currency import currency_engine
            self.base_currency = currency_engine.base_currency
            self.exchange_rates = dict(currency_engine.rates)
        except Exception:
            pass
        data = {
            "language": self.language,
            "theme": self.theme,
            "api_key": encrypt(self.api_key),
            "api_url": self.api_url,
            "model": self.model,
            "base_currency": self.base_currency,
            "exchange_rates": self.exchange_rates,
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
            "scenarios": self.scenarios,
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
            self.scenarios = data.get("scenarios", {})

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
        self.scenarios = {}
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
    """ثوابت الألوان Material Design 3 — ثلاث ثيمات"""

    _MODERN = {
        "bg": "#0F0F23",
        "card_bg": "#1A1A35",
        "text": "#E8EAF6",
        "text_secondary": "#B0BEC5",
        "text_muted": "#78909C",
        "border": "rgba(255,255,255,0.08)",
        "chart_text": "#B0BEC5",
        "chart_edge": "rgba(255,255,255,0.10)",
        "error": "#FF5252",
        "success": "#69F0AE",
        "warning": "#FFD740",
        "info": "#40C4FF",
        "chart_bg": "#1A1A35",
        "chart_grid": "rgba(255,255,255,0.06)",
        "primary": "#7C4DFF",
        "surface": "#1A1A35",
        "on_surface": "#E8EAF6",
        "outline": "rgba(255,255,255,0.12)",
    }

    _DARK = {
        "bg": "#121212",
        "card_bg": "#1E1E1E",
        "text": "#E0E0E0",
        "text_secondary": "#9E9E9E",
        "text_muted": "#757575",
        "border": "rgba(255,255,255,0.08)",
        "chart_text": "#9E9E9E",
        "chart_edge": "rgba(255,255,255,0.10)",
        "error": "#CF6679",
        "success": "#4CAF50",
        "warning": "#FFB74D",
        "info": "#64B5F6",
        "chart_bg": "#1E1E1E",
        "chart_grid": "rgba(255,255,255,0.06)",
        "primary": "#90CAF9",
        "surface": "#1E1E1E",
        "on_surface": "#E0E0E0",
        "outline": "rgba(255,255,255,0.15)",
    }

    _LIGHT = {
        "bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "text": "#1E293B",
        "text_secondary": "#64748B",
        "text_muted": "#94A3B8",
        "border": "#E2E8F0",
        "chart_text": "#64748B",
        "chart_edge": "#F1F5F9",
        "error": "#EF4444",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "info": "#3B82F6",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#F1F5F9",
        "primary": "#3B82F6",
        "surface": "#FFFFFF",
        "on_surface": "#1E293B",
        "outline": "#CBD5E1",
    }

    _PALETTES = {"light": _LIGHT, "dark": _DARK, "modern": _MODERN}

    @classmethod
    def get(cls, key):
        palette = cls._PALETTES.get(state.theme, cls._LIGHT)
        value = palette.get(key, "#888888")
        # matplotlib لا يفهم صيغة CSS rgba(..) — حوّلها إلى hex
        if isinstance(value, str) and value.startswith("rgba("):
            parts = value[value.index("(") + 1: value.index(")")].split(",")
            try:
                r, g, b = (int(p.strip()) for p in parts[:3])
                return "#%02X%02X%02X" % (r, g, b)
            except (ValueError, IndexError):
                return "#888888"
        return value

    @classmethod
    def chart_palette(cls):
        return ["#3B82F6", "#22C55E", "#EF4444", "#F59E0B", "#8B5CF6", "#06B6D4"]
