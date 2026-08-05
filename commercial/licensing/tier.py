"""Feature tiers: FREE | PRO | ENTERPRISE.

The tier is part of the signed license payload, so a tier cannot be
elevated by editing local files.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict


class Tier(str, Enum):
    """License tiers, ordered by rank."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    @classmethod
    def parse(cls, value: str) -> "Tier":
        """Parse a tier name, defaulting to FREE on unknown input."""
        try:
            return cls(str(value).lower())
        except ValueError:
            return cls.FREE

    @property
    def rank(self) -> int:
        """Numeric rank used for comparisons."""
        return {"free": 0, "pro": 1, "enterprise": 2}[self.value]

    def at_least(self, other: "Tier") -> bool:
        """True if this tier is at least as privileged as ``other``."""
        return self.rank >= other.rank


FEATURES: Dict[str, Tier] = {
    "cloud_sync": Tier.PRO,
    "multi_device": Tier.PRO,
    "ai_unlimited": Tier.ENTERPRISE,
    "api_access": Tier.ENTERPRISE,
    "audit_trail": Tier.ENTERPRISE,
}


def feature_enabled(feature: str, tier: Tier) -> bool:
    """Feature gate: returns True if ``tier`` unlocks ``feature``.

    Unknown features default to enabled (Free keeps working).
    """
    required = FEATURES.get(feature)
    if required is None:
        return True
    return tier.at_least(required)
