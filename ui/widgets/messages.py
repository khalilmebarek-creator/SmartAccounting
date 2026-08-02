# Unified message helpers
# ========================
# رسائل خطأ/تحذير/نجاح موحّدة: عنوان واضح + إجراء مقترح (تلميح) + نص مترجم.

from PyQt5.QtWidgets import QMessageBox

from ui.resources.i18n import t


def build_error_text(message, hint_key=None, exc=None, detail=None):
    """Build a readable multi-line error text.

    - message:  core translated message
    - hint_key: i18n key of the suggested action line (shown as "💡 ...")
    - exc:      optional exception to append its text
    - detail:   optional extra detail line
    """
    parts = [message]
    if detail:
        parts.append(detail)
    if exc is not None:
        parts.append(str(exc))
    if hint_key:
        parts.append(f"💡 {t('err_suggestion')}: {t(hint_key)}")
    return "\n\n".join(p for p in parts if p)


def show_error(parent, message, hint_key=None, exc=None, title_key="error"):
    """Show a critical error dialog with a suggested action line."""
    QMessageBox.critical(
        parent, t(title_key),
        build_error_text(message, hint_key=hint_key, exc=exc)
    )


def show_warning(parent, message, hint_key=None, title_key="warning"):
    """Show a warning dialog with a suggested action line."""
    QMessageBox.warning(
        parent, t(title_key),
        build_error_text(message, hint_key=hint_key)
    )


def show_info(parent, message, title_key="success"):
    """Show an informational success dialog."""
    QMessageBox.information(parent, t(title_key), message)
