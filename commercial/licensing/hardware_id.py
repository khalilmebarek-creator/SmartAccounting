"""Stable machine fingerprint (CPUID + MAC + disk serial, SHA-256).

The fingerprint is used to bind a license to one machine. Components are
collected defensively: if a source is unavailable (e.g. no PowerShell on
non-Windows), the remaining sources still produce a stable value.
"""

from __future__ import annotations

import hashlib
import platform
import re
import subprocess
import uuid
from functools import lru_cache


def _mac() -> str:
    """Primary MAC address as 12 hex digits (uses the hostname-independent uuid)."""
    try:
        return format(uuid.getnode(), "012x")
    except Exception:
        return "000000000000"


def _processor() -> str:
    """CPU description string."""
    try:
        return platform.processor() or platform.machine()
    except Exception:
        return "unknown"


def _disk_serial() -> str:
    """First physical disk serial number (Windows: CIM/PowerShell)."""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_DiskDrive | Select-Object -First 1 -ExpandProperty SerialNumber",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=0x08000000,
        )
        serial = (result.stdout or "").strip()
        return serial or ""
    except Exception:
        return ""


def fingerprint_from_components(mac: str, processor: str, disk_serial: str) -> str:
    """Deterministic SHA-256 fingerprint from the raw hardware components."""
    clean_mac = re.sub(r"[^0-9a-f]", "", mac.strip().lower())
    raw = "|".join([clean_mac, processor.strip(), disk_serial.strip()]).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def fingerprint() -> str:
    """Full machine fingerprint (cached — subprocess calls are expensive)."""
    return fingerprint_from_components(_mac(), _processor(), _disk_serial())
