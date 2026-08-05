"""Offline vendor CLI: key pair generation + license issuing.

Run the private key generator once and keep the key offline — never commit
it. This tool is for the vendor (license seller), not shipped to customers.

Examples:
    # generate the key pair (private key stored under commercial/keys/)
    python -m commercial.licensing.keygen --new-keypair

    # issue a 1-year PRO license for a customer's hardware id
    python -m commercial.licensing.keygen --hwid <hex> --tier pro --days 365 --licensee "Acme SARL"

    # emit 5 demo keys bound to a fake test hardware id
    python -m commercial.licensing.keygen --sample
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date

from .activation import LicenseStore
from .expiry import expiry_from_today
from .hardware_id import fingerprint
from .license import (
    encode_key,
    generate_keypair,
    load_private_key,
    new_license_payload,
)
from .tier import Tier

KEYS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "keys")
PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pub_key.pem")
SAMPLE_HARDWARE_ID = "0" * 64


def _load_or_create_private_key() -> bytes:
    """Load the vendor private key, generating it on first run."""
    os.makedirs(KEYS_DIR, exist_ok=True)
    if os.path.exists(PRIVATE_KEY_FILE):
        with open(PRIVATE_KEY_FILE, "rb") as handle:
            return handle.read()
    private_pem, public_pem = generate_keypair()
    with open(PRIVATE_KEY_FILE, "wb") as handle:
        handle.write(private_pem)
    with open(PUBLIC_KEY_FILE, "wb") as handle:
        handle.write(public_pem)
    print(f"[keygen] key pair created: private -> {PRIVATE_KEY_FILE}")
    return private_pem


def issue_key(
    hardware_id: str,
    tier: Tier,
    days: int,
    licensee: str,
    private_pem: bytes,
    issued: str | date | None = None,
) -> str:
    """Issue one license key; prints and returns it."""
    key = encode_key(
        new_license_payload(
            tier=tier,
            hardware_id=hardware_id,
            licensee=licensee,
            expiry=expiry_from_today(days),
            issued=issued,
        ),
        load_private_key(private_pem),
    )
    return key


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Smart Accounting license keygen (offline vendor tool)")
    parser.add_argument("--new-keypair", action="store_true", help="generate a fresh RSA-2048 key pair")
    parser.add_argument("--hwid", help="target hardware id (omit to use this machine)")
    parser.add_argument("--tier", default="pro", choices=["free", "pro", "enterprise"], help="license tier")
    parser.add_argument("--days", type=int, default=365, help="validity period in days")
    parser.add_argument("--licensee", default="Customer", help="licensee name")
    parser.add_argument("--sample", action="store_true", help="emit 5 demo keys for a fake test machine")
    args = parser.parse_args(argv)

    if args.new_keypair:
        os.makedirs(KEYS_DIR, exist_ok=True)
        private_pem, public_pem = generate_keypair()
        with open(PRIVATE_KEY_FILE, "wb") as handle:
            handle.write(private_pem)
        with open(PUBLIC_KEY_FILE, "wb") as handle:
            handle.write(public_pem)
        print(f"[keygen] key pair written: {PRIVATE_KEY_FILE} + {PUBLIC_KEY_FILE}")
        return 0

    private_pem = _load_or_create_private_key()

    if args.sample:
        print(f"[keygen] 5 demo keys bound to test hardware {SAMPLE_HARDWARE_ID[:8]}...")
        for index in range(1, 6):
            key = issue_key(
                SAMPLE_HARDWARE_ID,
                Tier.PRO if index % 2 else Tier.ENTERPRISE,
                days=90 * index,
                licensee=f"Demo Customer {index}",
                private_pem=private_pem,
            )
            print(f"  [{index}] {key}")
        return 0

    hardware_id = args.hwid or fingerprint()
    print(f"[keygen] target hardware: {hardware_id}")
    key = issue_key(
        hardware_id,
        Tier.parse(args.tier),
        args.days,
        args.licensee,
        private_pem,
    )
    print(key)
    return 0


if __name__ == "__main__":
    sys.exit(main())
