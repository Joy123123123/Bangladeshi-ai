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
    # Bangla / Bengali
    "bangla": SubjectCode.BANGLA,
    "bengali": SubjectCode.BANGLA,
    "বাংলা": SubjectCode.BANGLA,

    # English
    "english": SubjectCode.ENGLISH,
    "ing": SubjectCode.ENGLISH,
    "ইংরেজি": SubjectCode.ENGLISH,

    # Math
    "math": SubjectCode.MATH,
    "maths": SubjectCode.MATH,
    "gonit": SubjectCode.MATH,
    "গণিত": SubjectCode.MATH,

    # Physics
    "physics": SubjectCode.PHYSICS,
    "fisics": SubjectCode.PHYSICS,
    "podartho": SubjectCode.PHYSICS,
    "পদার্থ": SubjectCode.PHYSICS,
    "পদার্থবিজ্ঞান": SubjectCode.PHYSICS,

    # Chemistry
    "chemistry": SubjectCode.CHEMISTRY,
    "chem": SubjectCode.CHEMISTRY,
    "rashayon": SubjectCode.CHEMISTRY,
    "রসায়ন": SubjectCode.CHEMISTRY,

    # Biology
    "biology": SubjectCode.BIOLOGY,
    "bio": SubjectCode.BIOLOGY,
    "jibbigyan": SubjectCode.BIOLOGY,
    "জীববিজ্ঞান": SubjectCode.BIOLOGY,

    # ICT
    "ict": SubjectCode.ICT,
    "computer": SubjectCode.ICT,
    "computing": SubjectCode.ICT,
    "তথ্য প্রযুক্তি": SubjectCode.ICT,

    # History
    "history": SubjectCode.HISTORY,
    "itihash": SubjectCode.HISTORY,
    "ইতিহাস": SubjectCode.HISTORY,

    # Geography
    "geography": SubjectCode.GEOGRAPHY,
    "geo": SubjectCode.GEOGRAPHY,
    "vugol": SubjectCode.GEOGRAPHY,
    "ভূগোল": SubjectCode.GEOGRAPHY,

    # Economics
    "economics": SubjectCode.ECONOMICS,
    "economy": SubjectCode.ECONOMICS,
    "orthoniti": SubjectCode.ECONOMICS,
    "অর্থনীতি": SubjectCode.ECONOMICS,

    # Higher Math
    "higher math": SubjectCode.HIGHER_MATH,
    "ucchatar gonit": SubjectCode.HIGHER_MATH,
    "উচ্চতর গণিত": SubjectCode.HIGHER_MATH,

    # General Science
    "science": SubjectCode.GENERAL_SCIENCE,
    "bigyan": SubjectCode.GENERAL_SCIENCE,
    "বিজ্ঞান": SubjectCode.GENERAL_SCIENCE,
}

# ---------------------------------------------------------------------------
# Banglish word → Bengali word mapping (common words)
# ---------------------------------------------------------------------------

BANGLISH_TO_BANGLA: dict[str, str] = {
    # Greetings & common phrases
    "ami": "আমি",
    "tumi": "তুমি",
    "apni": "আপনি",
    "ki": "কি",
    "kি": "কি",
    "keno": "কেন",
    "kivabe": "কিভাবে",
    "kothai": "কোথায়",
    "kon": "কোন",
    "koto": "কত",
    "boro": "বড়",
    "choto": "ছোট",
    "valo": "ভালো",
    "kharap": "খারাপ",
    "hya": "হ্যাঁ",
    "na": "না",
    "dhonnobad": "ধন্যবাদ",
    "please": "অনুগ্রহ করে",
    "help": "সাহায্য",

    # Educational terms
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
    "write": "লিখুন",
    "read": "পড়ুন",
    "study": "পড়াশোনা",
    "learn": "শেখা",
    "understand": "বোঝা",
    "remember": "মনে রাখা",
    "practice": "অনুশীলন",
    "shortcut": "শর্টকাট",
    "trick": "কৌশল",
    "tip": "টিপস",
    "important": "গুরুত্বপূর্ণ",
    "easy": "সহজ",
    "difficult": "কঠিন",
    "preparation": "প্রস্তুতি",
    "admission": "ভর্তি",
    "result": "ফলাফল",
}

# ---------------------------------------------------------------------------
# Intent detection patterns
# ---------------------------------------------------------------------------

INTENT_PATTERNS: dict[str, list[str]] = {
    "explanation": [
        r"\bki\b", r"\bkeno\b", r"\bkivabe\b", r"কী", r"কেন", r"কিভাবে",
        r"what is", r"why", r"how", r"explain", r"describe", r"define",
    ],
    "problem_solving": [
        r"\bsolve\b", r"\bcalculate\b", r"\bfind\b", r"সমাধান", r"হিসাব", r"নির্ণয়",
        r"=\?", r"=\s*\?", r"বের কর",
    ],
    "shortcut_request": [
        r"\bshortcut\b", r"\btrick\b", r"\btips?\b", r"\bfast\b", r"\bquick\b",
        r"শর্টকাট", r"কৌশল", r"টিপস", r"দ্রুত",
    ],
    "previous_year": [
        r"\bprev(ious)?\b", r"\blast year\b", r"\bold question\b",
        r"পূর্ববর্তী", r"গত বছর", r"পুরনো প্রশ্ন",
    ],
    "practice": [
        r"\bpractice\b", r"\bexercise\b", r"\bmcq\b",
        r"অনুশীলন", r"প্র্যাকটিস", r"MCQ",
    ],
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
    # Treat as Banglish when Latin chars dominate but some context suggests Bengali topic
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


def detect_intent(text: str) -> str:
    """Classify the user's intent (explanation, problem_solving, etc.)."""
    lower = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower, re.IGNORECASE):
                return intent
    return "general"


class BanglishParser:
    """Parse and normalise user input for the NCTB AI platform."""

    async def parse(self, text: str) -> str:
        """
        Normalise input text.

        - If the text is Banglish, convert known words to Bengali.
        - Pure Bengali and pure English text is returned as-is.
        """
        if not text or not text.strip():
            return text

        if _is_banglish(text):
            return _normalize_banglish(text)

        return text

    async def detect_subject(self, text: str) -> Optional[SubjectCode]:
        return detect_subject_from_text(text)

    async def detect_intent(self, text: str) -> str:
        return detect_intent(text)

    async def full_parse(self, text: str) -> dict:
        """Return a dict with normalised text, detected subject, and intent."""
        normalized = await self.parse(text)
        subject = await self.detect_subject(text)
        intent = await self.detect_intent(text)
        return {
            "original": text,
            "normalized": normalized,
            "detected_subject": subject,
            "intent": intent,
            "was_banglish": _is_banglish(text),
        }


banglish_parser = BanglishParser()
