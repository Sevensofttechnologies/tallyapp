#!/usr/bin/env python3
"""
scripts/check_env.py
====================
Verify that TallyBridge and TallyInsight are configured with the SAME
shared JWT secret, without ever printing the secret itself.

Usage (run from the repo root):
    python scripts/check_env.py \
        --bridge TallyInsightPlus-master/TallyBridge/.env \
        --insight TallyInsightPlus-master/TallyInsight/.env

Exit codes:
    0  — keys match (or both are absent — treated as a config error)
    1  — keys differ, or one/both are missing / weak
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

# Known placeholder values that must never be used
_BANNED_KEYS = {
    "your-secret-key-change-in-production",
    "your-super-secret-key-change-this-in-production",
    "tallybots-super-secret-key-change-in-production-2026",
    "REPLACE_WITH_OUTPUT_OF_secrets_token_urlsafe_48",
    "change-me",
    "secret",
    "password",
}

_MIN_KEY_LENGTH = 32


def _sha256_prefix(value: str) -> str:
    """Return first 12 hex chars of SHA-256(value) for comparison without revealing the key."""
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def _parse_dotenv(path: Path) -> dict:
    """Parse a .env file into a dict. Ignores comments and blank lines."""
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def _extract_secret(env: dict, path: Path) -> str | None:
    """
    Extract the JWT secret from a parsed env dict.
    TallyBridge uses SECRET_KEY; TallyInsight uses JWT_SECRET_KEY (with SECRET_KEY as alias).
    """
    return (
        env.get("JWT_SECRET_KEY")
        or env.get("SECRET_KEY")
    )


def _validate(key: str | None, label: str) -> str:
    """Validate a key value; return it or exit with an error message."""
    if not key:
        print(f"[ERROR] {label}: JWT secret not found (JWT_SECRET_KEY / SECRET_KEY not set).")
        sys.exit(1)
    if key in _BANNED_KEYS:
        print(f"[ERROR] {label}: JWT secret is a known placeholder. Set a real key.")
        sys.exit(1)
    if len(key) < _MIN_KEY_LENGTH:
        print(
            f"[ERROR] {label}: JWT secret is too short "
            f"({len(key)} chars, minimum {_MIN_KEY_LENGTH})."
        )
        sys.exit(1)
    return key


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check that TallyBridge and TallyInsight share the same JWT secret."
    )
    parser.add_argument(
        "--bridge",
        default="TallyInsightPlus-master/TallyBridge/.env",
        help="Path to TallyBridge .env file",
    )
    parser.add_argument(
        "--insight",
        default="TallyInsightPlus-master/TallyInsight/.env",
        help="Path to TallyInsight .env file",
    )
    args = parser.parse_args()

    bridge_path = Path(args.bridge)
    insight_path = Path(args.insight)

    # Parse both files
    bridge_env = _parse_dotenv(bridge_path)
    insight_env = _parse_dotenv(insight_path)

    if not bridge_path.exists():
        print(f"[ERROR] TallyBridge .env not found at: {bridge_path}")
        sys.exit(1)
    if not insight_path.exists():
        print(f"[ERROR] TallyInsight .env not found at: {insight_path}")
        sys.exit(1)

    # Extract and validate each key
    bridge_key = _validate(_extract_secret(bridge_env, bridge_path), "TallyBridge")
    insight_key = _validate(_extract_secret(insight_env, insight_path), "TallyInsight")

    # Compare by SHA-256 hash — never print the raw key
    bridge_hash = _sha256_prefix(bridge_key)
    insight_hash = _sha256_prefix(insight_key)

    print(f"TallyBridge  SECRET_KEY  SHA-256[:12] = {bridge_hash}")
    print(f"TallyInsight JWT_SECRET_KEY SHA-256[:12] = {insight_hash}")

    if bridge_hash == insight_hash:
        print("\n[OK] Both services share the same JWT secret.")
        sys.exit(0)
    else:
        print(
            "\n[ERROR] JWT secrets DO NOT match!\n"
            "Both services must use the same key.\n"
            "Copy the value from TallyBridge SECRET_KEY into TallyInsight JWT_SECRET_KEY."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()