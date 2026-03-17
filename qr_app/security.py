from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
from typing import Tuple


PASSWORD_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return f"{PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        iterations_str, salt_hex, digest_hex = stored_value.split("$", 2)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations_str),
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)


def check_password_strength(password: str) -> Tuple[int, Tuple[str, str]]:
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    strength_map = {
        0: (25, ("Very Weak", "#ef4444")),
        1: (25, ("Very Weak", "#ef4444")),
        2: (50, ("Weak", "#f97316")),
        3: (75, ("Medium", "#f59e0b")),
        4: (100, ("Strong", "#22c55e")),
    }
    return strength_map.get(score, (0, ("Very Weak", "#ef4444")))


def generate_session_token() -> str:
    return secrets.token_hex(32)
