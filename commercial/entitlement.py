"""Module 3: live tier enforcement at feature entry points.

Reads the activated license (via :class:`~commercial.licensing.activation.LicenseStore`)
and answers ``feature_allowed(...)`` — the same gates that Module 1 defined
in ``tier.feature_enabled``, now driven by the *current* license instead of a
caller-supplied tier. Without a license file the app runs as FREE tier.

Tests can inject a store with :func:`set_store`; :func:`reset` restores the
default (real) license location.
"""

from __future__ import annotations

from typing import Optional

from .licensing.activation import LicenseStore
from .licensing.errors import LicenseError
from .licensing.tier import FEATURES, Tier, feature_enabled

_store_override: Optional[LicenseStore] = None


def set_store(store: Optional[LicenseStore]) -> None:
    """Override the license store (used by tests and app startup wiring)."""
    global _store_override
    _store_override = store


def reset() -> None:
    """Restore the default license store (real ``license.dat`` location)."""
    global _store_override
    _store_override = None


def _current_store() -> LicenseStore:
    return _store_override if _store_override is not None else LicenseStore()


def current_tier() -> Tier:
    """Tier of the activated license, or FREE when absent/corrupt."""
    try:
        state = _current_store().load()
    except LicenseError:
        return Tier.FREE
    return state.tier if state is not None else Tier.FREE


def required_tier(feature: str) -> Optional[Tier]:
    """Tier that unlocks ``feature`` (None for unregistered features)."""
    return FEATURES.get(feature)


def feature_allowed(feature: str) -> bool:
    """True when the current license unlocks ``feature``.

    Unknown features stay enabled so future features never break FREE users.
    """
    return feature_enabled(feature, current_tier())
