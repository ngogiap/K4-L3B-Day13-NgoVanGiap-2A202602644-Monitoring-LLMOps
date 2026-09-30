from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # TODO: Add more patterns (e.g., Passport, Vietnamese address keywords)
    "passport": r"\b[A-Z]{1,2}\d{7,8}\b",
    "vn_address": (
        r"(?:"
        # "số X, đường/phố Y, phường/xã Z, quận/huyện W"
        r"(?:số\s*\d+[\w\s,]*)?(?:(?:đường|phố|ngõ|hẻm|ngách)[^\S\r\n]+[\w\d]+(?:[\s,]+[\w\d]+){0,4})"
        r"[\s,]*(?:(?:phường|xã|thôn|ấp|thị\s*trấn)[^\S\r\n]+[\w\d]+(?:[\s,]+[\w\d]+){0,3})?"
        r"[\s,]*(?:(?:quận|huyện|thị\s*xã)[^\S\r\n]+[\w\d]+(?:[\s,]+[\w\d]+){0,3})?"
        r"[\s,]*(?:(?:tỉnh|thành\s*phố|tp\.?)[^\S\r\n]+[\w\d]+(?:[\s,]+[\w\d]+){0,3})?"
        r"|"
        # standalone city/province keywords with value
        r"(?:tỉnh|thành\s*phố|tp\.?)\s+[\w\d]+(?:[\s,]+[\w\d]+){0,3}"
        r")"
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
