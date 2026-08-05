"""RSA-2048 license keys.

A license key is a URL-safe base64 blob, split into 5-char groups:

    [canonical JSON payload]---[RSA signature]

The payload carries tier, licensee, expiry, hardware id and issue date.
The signature is made with the vendor's private key; every client verifies
it with the embedded public key, so keys cannot be forged offline.

Note: the human format shown in the prompt (``XXXX-XXXX-XXXX-XXXX-XXXX``)
cannot carry an RSA-2048 signature (256 bytes); the real key is longer but
kept in the same grouped style for readability and copy-paste safety.
"""

from __future__ import annotations

import base64
import json
import os
import re
import secrets
from datetime import date
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from .errors import LicenseInvalidError, LicenseSignatureError
from .tier import Tier

KEY_GROUP_SIZE = 5
PAYLOAD_SIG_SEP = "---"
VERSION = "1"
KEY_PATTERN = re.compile(r"^[A-Za-z0-9+/=]+(?:-[A-Za-z0-9+/=]+)*(?:---[A-Za-z0-9+/=]+(?:-[A-Za-z0-9+/=]+)*)?$")

PUBLIC_KEY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pub_key.pem")


def generate_keypair() -> Tuple[bytes, bytes]:
    """Generate a new RSA-2048 key pair: ``(private_pem, public_pem)``."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def load_private_key(private_pem: bytes) -> RSAPrivateKey:
    """Load an RSA private key from PEM bytes."""
    return serialization.load_pem_private_key(private_pem, password=None)


def load_public_key(public_pem: bytes) -> RSAPublicKey:
    """Load an RSA public key from PEM bytes."""
    return serialization.load_pem_public_key(public_pem)


def embedded_public_key() -> RSAPublicKey:
    """Load the public key shipped inside this package."""
    with open(PUBLIC_KEY_PATH, "rb") as handle:
        return load_public_key(handle.read())


def payload_serialize(payload: Dict) -> bytes:
    """Canonical JSON bytes for a payload (stable across Python runs)."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sign_payload(payload: Dict, private_key: RSAPrivateKey) -> bytes:
    """RSA PKCS#1 v1.5 SHA-256 signature over the canonical payload."""
    return private_key.sign(payload_serialize(payload), PKCS1v15(), hashes.SHA256())


def verify_signature(payload: Dict, signature: bytes, public_key: RSAPublicKey) -> bool:
    """Verify a signature; False on any verification failure."""
    try:
        public_key.verify(signature, payload_serialize(payload), PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        return False


def new_license_payload(
    tier: Tier,
    hardware_id: str,
    licensee: str,
    expiry: str | date,
    issued: Optional[str | date] = None,
    uid: Optional[str] = None,
) -> Dict:
    """Build a signed payload dict for a new license."""
    if isinstance(expiry, date):
        expiry = expiry.isoformat()
    if isinstance(issued, date):
        issued = issued.isoformat()
    if issued is None:
        issued = date.today().isoformat()
    return {
        "v": VERSION,
        "tier": tier.value,
        "licensee": licensee,
        "hwid": hardware_id,
        "exp": str(expiry),
        "iss": str(issued),
        "uid": uid or secrets.token_hex(6),
    }


def _group(base64_text: str) -> str:
    """Split base64 text into 5-char groups joined by dashes."""
    if len(base64_text) <= KEY_GROUP_SIZE:
        return base64_text
    groups = [
        base64_text[i : i + KEY_GROUP_SIZE]
        for i in range(0, len(base64_text), KEY_GROUP_SIZE)
    ]
    return "-".join(groups)


def _ungroup(key_text: str) -> str:
    """Remove group separators, returning the raw base64 text."""
    return key_text.replace("-", "")


def encode_key(payload: Dict, private_key: RSAPrivateKey) -> str:
    """Encode a payload + signature as a grouped license key string."""
    signature = sign_payload(payload, private_key)
    payload_b64 = base64.b64encode(payload_serialize(payload)).decode("ascii")
    signature_b64 = base64.b64encode(signature).decode("ascii")
    return _group(payload_b64) + PAYLOAD_SIG_SEP + _group(signature_b64)


def decode_key(key_text: str, public_key: RSAPublicKey) -> Dict:
    """Decode and verify a license key.

    Whitespace is tolerated so pasted keys (email/WhatsApp line wraps) work.

    Raises:
        LicenseInvalidError: key is malformed or does not match the format.
        LicenseSignatureError: the RSA signature does not verify (tampered).
    """
    if not isinstance(key_text, str) or not key_text.strip():
        raise LicenseInvalidError("empty license key")
    key_text = "".join(key_text.split())
    if not KEY_PATTERN.match(key_text):
        raise LicenseInvalidError("license key format is invalid")
    if PAYLOAD_SIG_SEP not in key_text:
        raise LicenseInvalidError("license key is missing its signature separator")
    payload_part, signature_part = key_text.split(PAYLOAD_SIG_SEP, 1)
    raw_payload = _ungroup(payload_part)
    raw_signature = _ungroup(signature_part)
    if len(raw_payload) < 8 or len(raw_signature) < 40:
        raise LicenseInvalidError("license key is too short")
    try:
        payload_bytes = base64.b64decode(raw_payload.encode("ascii"))
        signature = base64.b64decode(raw_signature.encode("ascii"))
    except Exception as exc:
        raise LicenseInvalidError(f"license key is not valid base64: {exc}") from exc
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise LicenseInvalidError(f"license payload is corrupt: {exc}") from exc
    if not verify_signature(payload, signature, public_key):
        raise LicenseSignatureError("license signature verification failed")
    return payload
