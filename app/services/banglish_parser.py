"""
Banglish-to-Bangla intent parser.

Detects Romanised Bengali (Banglish) input and:
  1. Identifies the intended subject / intent.
  2. Normalises the text so the LLM receives consistent Bengali input.
"""

import re
from typing import Optional

from app.models.schemas import SubjectCode


# ---------------------------------------------------------------------------
# Banglish → Subject keyword mapping
# ---------------------------------------------------------------------------

SUBJECT_KEYWORDS: dict[str, SubjectCode] = {
    "bangla": SubjectCode.BANGLA,
    "bengali": SubjectCode.BANGLA,
    "বাংলা": SubjectCode.BANGLA,
    "english": SubjectCode.ENGLISH,
    "ইংরেজি": SubjectCode.ENGLISH,
    "math": SubjectCode.MATH,
    "maths": SubjectCode.MATH,
    "gonit": SubjectCode.MATH,
    "গণিত": SubjectCode.MATH,
    "physics": SubjectCode.PHYSICS,
    "podartho": SubjectCode.PHYSICS,
    "পদার্থ": SubjectCode.PHYSICS,
    "পদার্থবিজ্ঞান": SubjectCode.PHYSICS,
    "chemistry": SubjectCode.CHEMISTRY,
    "chem": SubjectCode.CHEMISTRY,
    "rashayon": SubjectCode.CHEMISTRY,
    "রসায়ন": SubjectCode.CHEMISTRY,
    "biology": SubjectCode.BIOLOGY,
    "bio": SubjectCode.BIOLOGY,
    "jibbigyan": SubjectCode.BIOLOGY,
    "জীববিজ্ঞান": SubjectCode.BIOLOGY,
    "ict": SubjectCode.ICT,
    "computer": SubjectCode.ICT,
    "তথ্য প্রযুক্তি": SubjectCode.ICT,
    "history": SubjectCode.HISTORY,
    "ইতিহাস": SubjectCode.HISTORY,
    "geography": SubjectCode.GEOGRAPHY,
    "geo": SubjectCode.GEOGRAPHY,
    "ভূগোল": SubjectCode.GEOGRAPHY,
    "economics": SubjectCode.ECONOMICS,
    "অর্থনীতি": SubjectCode.ECONOMICS,
    "higher math": SubjectCode.HIGHER_MATH,
    "উচ্চতর গণিত": SubjectCode.HIGHER_MATH,
    "science": SubjectCode.GENERAL_SCIENCE,
    "bigyan": SubjectCode.GENERAL_SCIENCE,
    "বিজ্ঞান": SubjectCode.GENERAL_SCIENCE,
}

# ---------------------------------------------------------------------------
# Banglish word → Bengali word mapping
# ---------------------------------------------------------------------------

BANGLISH_TO_BANGLA: dict[str, str] = {
    "ami": "আমি",
    "tumi": "তুমি",
    "apni": "আপনি",
    "ki": "কি",
    "keno": "কেন",
    "kivabe": "কিভাবে",
    "kothai": "কোথায়",
    "kon": "কোন",
    "koto": "কত",
    "valo": "ভালো",
    "hya": "হ্যাঁ",
    "na": "না",
    "dhonnobad": "ধন্যবাদ",
    "please": "অনুগ্রহ করে",
    "help": "সাহায্য",
    "math": "গণিত",
    "maths": "গণিত",
    "physics": "পদার্থবিজ্ঞান",
    "chemistry": "রসায়ন",
    "biology": "জীববিজ্ঞান",
    "english": "ইংরেজি",
    "bangla": "বাংলা",
    "history": "ইতিহাস",
    "geography": "ভূগোল",
    "science": "বিজ্ঞান",
    "exam": "পরীক্ষা",
    "question": "প্রশ্ন",
    "answer": "উত্তর",
    "problem": "সমস্যা",
    "solution": "সমাধান",
    "formula": "সূত্র",
    "class": "শ্রেণী",
    "teacher": "শিক্ষক",
    "student": "শিক্ষার্থী",
    "book": "বই",
    "chapter": "অধ্যায়",
    "definition": "সংজ্ঞা",
    "example": "উদাহরণ",
    "explain": "ব্যাখ্যা করুন",
    "calculate": "হিসাব করুন",
    "solve": "সমাধান করুন",
    "study": "পড়াশোনা",
    "learn": "শেখা",
    "shortcut": "শর্টকাট",
    "trick": "কৌশল",
    "tip": "টিপস",
    "important": "গুরুত্বপূর্ণ",
    "easy": "সহজ",
    "difficult": "কঠিন",
    "admission": "ভর্তি",
    "integration": "সংকলন",
    "derivative": "অন্তরক",
    "equilibrium": "ভারসাম্য",
    "velocity": "বেগ",
    "acceleration": "ত্বরণ",
}


# ---------------------------------------------------------------------------
# Core parsing functions
# ---------------------------------------------------------------------------

def _is_banglish(text: str) -> bool:
    """Return True if text contains significant Romanised Bengali content."""
    bangla_chars = len(re.findall(r"[\u0980-\u09FF]", text))
    latin_chars = len(re.findall(r"[a-zA-Z]", text))
    total = bangla_chars + latin_chars
    if total == 0:
        return False
    return latin_chars > bangla_chars and latin_chars > 3


def _normalize_banglish(text: str) -> str:
    """Replace known Banglish words with their Bengali equivalents."""
    words = text.split()
    normalized_words: list[str] = []
    for word in words:
        clean = re.sub(r"[^\w\u0980-\u09FF]", "", word.lower())
        normalized_words.append(BANGLISH_TO_BANGLA.get(clean, word))
    return " ".join(normalized_words)


def detect_subject_from_text(text: str) -> Optional[SubjectCode]:
    """Detect subject intent from text (supports both Bangla and Banglish)."""
    lower = text.lower()
    for keyword, subject in SUBJECT_KEYWORDS.items():
        if keyword in lower:
            return subject
    return None


class BanglishParser:
    """Parse and normalise user input for the NCTB AI platform."""

    async def parse(self, text: str) -> str:
        if not text or not text.strip():
            return text
        if _is_banglish(text):
            return _normalize_banglish(text)
        return text

    async def detect_subject(self, text: str) -> Optional[SubjectCode]:
        return detect_subject_from_text(text)

    async def full_parse(self, text: str) -> dict:
        """Return a dict with normalised text, detected subject, and intent."""
        normalized = await self.parse(text)
        subject = await self.detect_subject(text)
        return {
            "original": text,
            "normalized": normalized,
            "detected_subject": subject,
            "was_banglish": _is_banglish(text),
        }


banglish_parser = BanglishParser()
