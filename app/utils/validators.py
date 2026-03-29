"""
Input Validators

Shared validation helpers for user inputs.
"""

import re
from typing import Optional


# Maximum lengths
MAX_MESSAGE_LENGTH = 4000
MAX_TOPIC_LENGTH = 500
MIN_MESSAGE_LENGTH = 1

# Dangerous patterns (prompt injection attempts)
_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+instructions?",
    r"you\s+are\s+now\s+(a|an)",
    r"act\s+as\s+(a|an)\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"disregard\s+(your|all)",
    r"system\s*:\s*",
    r"<\|.*?\|>",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)


def validate_message(text: str) -> tuple[bool, Optional[str]]:
    """
    Validate a user chat message.

    Returns (is_valid, error_message).
    """
    if not text or not text.strip():
        return False, "বার্তা খালি রাখা যাবে না।"

    if len(text) < MIN_MESSAGE_LENGTH:
        return False, f"বার্তা অন্তত {MIN_MESSAGE_LENGTH} অক্ষর হতে হবে।"

    if len(text) > MAX_MESSAGE_LENGTH:
        return False, f"বার্তা সর্বোচ্চ {MAX_MESSAGE_LENGTH} অক্ষর হতে পারবে।"

    if _INJECTION_RE.search(text):
        return False, "অনুগ্রহ করে একটি বৈধ শিক্ষামূলক প্রশ্ন করুন।"

    return True, None


def validate_topic(text: str) -> tuple[bool, Optional[str]]:
    """Validate a study topic string."""
    if not text or not text.strip():
        return False, "বিষয় খালি রাখা যাবে না।"

    if len(text) > MAX_TOPIC_LENGTH:
        return False, f"বিষয় সর্বোচ্চ {MAX_TOPIC_LENGTH} অক্ষর হতে পারবে।"

    return True, None


def sanitize_text(text: str) -> str:
    """Remove null bytes and excessive whitespace from text."""
    text = text.replace("\x00", "").strip()
    text = re.sub(r"\s{3,}", "  ", text)
    return text


def is_bengali(text: str) -> bool:
    """Return True if the text contains Bengali script characters."""
    return bool(re.search(r"[\u0980-\u09FF]", text))


def is_latin_only(text: str) -> bool:
    """Return True if the text contains only Latin characters and punctuation."""
    return not bool(re.search(r"[^\x00-\x7F]", text))
