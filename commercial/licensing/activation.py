"""Offline activation: challenge-response + license file store.

The license file (``license.dat``) stores the activated license key, which is
self-contained (payload + RSA signature) — so activation needs no phone-home.

Flow:
    user -> app shows hardware fingerprint (challenge)
    vendor -> offline keygen signs a key for that hardware + tier + expiry
    user -> paste key into the dialog -> the key is verified locally and saved
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional

from .errors import (
    LicenseFileError,
    LicenseHardwareMismatchError,
    LicenseSignatureError,
)
from .expiry import is_read_only
from .hardware_id import fingerprint
from .license import decode_key, embedded_public_key
from .tier import Tier

LICENSE_FILE_NAME = "license.dat"


@dataclass
class LicenseState:
    """Decoded, verified license held in memory."""

    tier: Tier
    licensee: str
    expiry: Optional[date]
    issued: date
    hardware_id: str
    raw_payload: Dict = field(default_factory=dict)

    @property
    def is_perpetual(self) -> bool:
        """True for non-expiring licenses."""
        return self.expiry is None


class LicenseStore:
    """Loads/verifies/saves the local license file."""

    def __init__(
        self,
        path: Optional[str] = None,
        public_key=None,
        hardware_id: Optional[str] = None,
    ) -> None:
        self.path = path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            LICENSE_FILE_NAME,
        )
        self.public_key = public_key if public_key is not None else embedded_public_key()
        self.hardware_id = hardware_id if hardware_id is not None else fingerprint()

    def challenge(self) -> Dict:
        """Challenge payload the user sends to the vendor for activation."""
        return {"hardware_id": self.hardware_id, "date": date.today().isoformat()}

    def decode_and_check(self, key_text: str) -> LicenseState:
        """Verify the key signature + hardware binding; raise on any failure."""
        payload = decode_key(key_text, self.public_key)
        payload_hwid = payload.get("hwid", "")
        if payload_hwid != self.hardware_id:
            raise LicenseHardwareMismatchError(
                f"license issued for hardware {payload_hwid}, this machine is {self.hardware_id}"
            )
        expiry = payload.get("exp")
        try:
            from .expiry import parse_expiry

            parsed_expiry = parse_expiry(expiry) if expiry else None
        except (TypeError, ValueError) as exc:
            raise LicenseSignatureError(f"license expiry field is corrupt: {exc}") from exc
        issued = parse_expiry(payload.get("iss") or date.today().isoformat())
        return LicenseState(
            tier=Tier.parse(payload.get("tier", "")),
            licensee=str(payload.get("licensee", "")),
            expiry=parsed_expiry,
            issued=issued,
            hardware_id=payload_hwid,
            raw_payload=payload,
        )

    def save(self, key_text: str) -> LicenseState:
        """Validate a pasted key and atomically write it to disk."""
        state = self.decode_and_check(key_text)
        self._atomic_write(self.path, key_text.strip())
        return state

    def load(self) -> Optional[LicenseState]:
        """Read the license file; None if absent. Raises on tampering."""
        if not os.path.exists(self.path):
            return None
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                key_text = handle.read()
        except OSError as exc:
            raise LicenseFileError(f"cannot read license file: {exc}") from exc
        return self.decode_and_check(key_text)

    def is_read_only(self) -> bool:
        """True when the stored license is expired beyond the grace period."""
        try:
            state = self.load()
        except Exception:
            return False
        if state is None or state.expiry is None:
            return False
        return is_read_only(state.expiry)

    @staticmethod
    def _atomic_write(filepath: str, data: str) -> None:
        """Write via temp file + os.replace so a crash never corrupts the license."""
        directory = os.path.dirname(filepath)
        try:
            fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(data)
            os.replace(tmp_path, filepath)
        except OSError as exc:
            raise LicenseFileError(f"cannot write license file: {exc}") from exc
