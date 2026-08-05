"""Custom exception hierarchy for the licensing system.

Every license error derives from :class:`LicenseError`, so callers may
catch the root type or a specific subtype.
"""

from __future__ import annotations


class LicenseError(Exception):
    """Base class for all licensing errors."""


class LicenseInvalidError(LicenseError):
    """The license key is malformed or unparseable."""


class LicenseSignatureError(LicenseError):
    """The license key failed RSA signature verification (tampered)."""


class LicenseHardwareMismatchError(LicenseError):
    """The license key was issued for a different machine."""


class LicenseExpiredError(LicenseError):
    """The license is past its expiry date."""


class LicenseFileError(LicenseError):
    """The license file on disk is missing or unreadable."""
