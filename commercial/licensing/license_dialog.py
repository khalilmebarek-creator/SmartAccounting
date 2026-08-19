"""License activation dialog: paste key -> activate -> restart.

Follows the app UI conventions (ui.constants sizes + unified messages +
translated strings). All logic lives in the pure module functions
:func:`describe_license` and :func:`try_activate` so it is fully testable;
the QDialog widget itself is UI glue (Qt dialogs cannot be constructed
under pytest on this Windows environment, hence the pragma).
"""

from __future__ import annotations

from typing import Optional, Tuple

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from ui.constants import MARGIN_LARGE, MIN_HEIGHT_BUTTON, SPACING_LARGE, SPACING_NORMAL
from ui.resources.i18n import t
from ui.widgets.messages import show_error, show_info, show_warning

from .activation import LicenseState, LicenseStore
from .errors import LicenseError
from .tier import Tier

TIER_KEYS = {
    Tier.FREE: "license_tier_free",
    Tier.PRO: "license_tier_pro",
    Tier.ENTERPRISE: "license_tier_enterprise",
}


def tier_label(tier: Tier) -> str:
    """Translated display name for a tier."""
    return t(TIER_KEYS.get(tier, "license_tier_free"))


def describe_license(store: LicenseStore) -> Tuple[str, str, str, str]:
    """Return ``(tier_text, licensee_text, expiry_text, hardware_id)`` for the dialog.

    Never raises: a corrupt license file is reported as the ``tier_text``
    placeholder (the caller shows the error via the return contract? No —
    corrupt files surface through :func:`try_activate` on the next save).
    """
    try:
        state = store.load()
    except LicenseError:
        state = None
    if state is None:
        return (
            t("license_status_no"),
            "—",
            t("license_status_trial"),
            store.challenge()["hardware_id"],
        )
    expiry_text = state.expiry.isoformat() if state.expiry else t("license_perpetual")
    return (
        tier_label(state.tier),
        state.licensee or "—",
        expiry_text,
        store.challenge()["hardware_id"],
    )


def try_activate(store: LicenseStore, key_text: str) -> Tuple[bool, Optional[LicenseState], Optional[LicenseError]]:
    """Validate + persist a pasted key.

    Returns ``(ok, state, error)`` — error is None when ok is True.
    """
    if not key_text.strip():
        return False, None, LicenseError(t("license_key_empty"))
    try:
        state = store.save(key_text)
    except LicenseError as exc:
        return False, None, exc
    return True, state, None


class LicenseDialog(QDialog):  # pragma: no cover - QDialog cannot be constructed under pytest (Qt5.15 + Python 3.13 on Windows)
    """Modal dialog showing license status and accepting a license key."""

    def __init__(self, parent=None, store: Optional[LicenseStore] = None) -> None:
        super().__init__(parent)
        self.store = store if store is not None else LicenseStore()
        self.setWindowTitle(t("license_title"))
        self.setModal(True)
        self.setMinimumWidth(560)
        self._build_ui()
        self._refresh_status()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        root.setSpacing(SPACING_LARGE)

        self.status_title = QLabel(t("license_status_title"))
        self.status_title.setObjectName("sectionTitle")
        root.addWidget(self.status_title)

        form = QFormLayout()
        form.setSpacing(SPACING_NORMAL)
        self.tier_label = QLabel()
        self.licensee_label = QLabel()
        self.expiry_label = QLabel()
        self.hwid_label = QLabel()
        self.hwid_label.setWordWrap(True)
        form.addRow(t("license_tier_label"), self.tier_label)
        form.addRow(t("license_licensee_label"), self.licensee_label)
        form.addRow(t("license_expiry_label"), self.expiry_label)
        form.addRow(t("license_hwid"), self.hwid_label)
        root.addLayout(form)

        self.key_input = QPlainTextEdit()
        self.key_input.setPlaceholderText(t("license_key_hint"))
        self.key_input.setMaximumHeight(120)
        self.key_input.setMinimumHeight(80)
        root.addWidget(self.key_input)

        buttons = QHBoxLayout()
        buttons.setSpacing(SPACING_NORMAL)
        self.activate_btn = QPushButton(t("license_activate"))
        self.activate_btn.setMinimumHeight(MIN_HEIGHT_BUTTON)
        self.activate_btn.setObjectName("primaryBtn")
        self.activate_btn.clicked.connect(self._on_activate)
        self.close_btn = QPushButton(t("btn_cancel"))
        self.close_btn.setMinimumHeight(MIN_HEIGHT_BUTTON)
        self.close_btn.clicked.connect(self.reject)
        buttons.addWidget(self.activate_btn)
        buttons.addWidget(self.close_btn)
        root.addLayout(buttons)

    def _refresh_status(self) -> None:
        tier_text, licensee_text, expiry_text, hwid_text = describe_license(self.store)
        self.tier_label.setText(tier_text)
        self.licensee_label.setText(licensee_text)
        self.expiry_label.setText(expiry_text)
        self.hwid_label.setText(hwid_text)

    def _on_activate(self) -> None:
        ok, _state, error = try_activate(self.store, self.key_input.toPlainText())
        if not ok:
            show_error(
                self,
                t("license_invalid"),
                hint_key="license_hint",
                exc=error if isinstance(error, LicenseError) and str(error) else None,
            )
            return
        show_info(
            self,
            f"{t('license_success')}\n\n{t('license_restart_note')}",
            title_key="success",
        )
        self.accept()
