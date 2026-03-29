"""
Bengali NLP utilities.

Provides helper functions for Bengali language detection, translation,
summarisation, and text preprocessing.
"""

import re
from typing import Optional


# Unicode range for Bengali script: U+0980–U+09FF
_BENGALI_PATTERN = re.compile(r"[\u0980-\u09ff]")


def detect_language(text: str) -> str:
    """
    Detect whether the text is primarily Bengali or English.

    Returns:
        "bn" for Bengali, "en" for English/other.
    """
    total_chars = len(text.replace(" ", ""))
    if total_chars == 0:
        return "en"
    bengali_chars = len(_BENGALI_PATTERN.findall(text))
    ratio = bengali_chars / total_chars
    return "bn" if ratio > 0.2 else "en"


def preprocess_bengali_text(text: str) -> str:
    """
    Clean and normalise Bengali text before sending to an AI model.

    - Removes excess whitespace
    - Normalises Bengali punctuation (danda)
    """
    # Normalise multiple spaces/newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalise Bengali danda (।) spacing
    text = re.sub(r"\s*।\s*", "। ", text)
    return text.strip()


def build_language_instruction(language: str, detected: Optional[str] = None) -> str:
    """
    Build a language instruction to append to system prompts.

    Args:
        language: User preference — "auto", "bn", or "en".
        detected: Auto-detected language of the input, "bn" or "en".

    Returns:
        A short instruction string.
    """
    if language == "bn" or (language == "auto" and detected == "bn"):
        return "\n\nPlease respond in Bengali (বাংলা) language."
    if language == "en":
        return "\n\nPlease respond in English."
    # Auto + English → no extra instruction, model decides
    return ""
