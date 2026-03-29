"""
Admission Engine

Detects and classifies admission exam question patterns (BUET, DU, Medical, BCS)
and provides targeted preparation guidance.
"""

import re
from typing import Optional

from app.models.schemas import ExamType, SubjectCode


# ---------------------------------------------------------------------------
# Pattern definitions for each exam type
# ---------------------------------------------------------------------------

EXAM_PATTERNS: dict[str, dict] = {
    ExamType.BUET.value: {
        "subjects": [SubjectCode.PHYSICS, SubjectCode.CHEMISTRY, SubjectCode.MATH, SubjectCode.ENGLISH],
        "keywords": [
            "buet", "বুয়েট", "প্রকৌশল", "engineering",
            "mechanics", "thermodynamics", "calculus", "vector",
        ],
        "question_types": ["MCQ", "Short Answer", "Proof"],
        "time_per_question": 90,  # seconds
        "total_marks": 500,
        "negative_marking": True,
    },
    ExamType.DU.value: {
        "subjects": [SubjectCode.BANGLA, SubjectCode.ENGLISH, SubjectCode.MATH, SubjectCode.GENERAL_SCIENCE],
        "keywords": [
            "du", "dhaka university", "ঢাকা বিশ্ববিদ্যালয়", "ঢাবি",
            "unit a", "unit b", "unit c", "ইউনিট",
        ],
        "question_types": ["MCQ"],
        "time_per_question": 60,
        "total_marks": 120,
        "negative_marking": True,
    },
    ExamType.MEDICAL.value: {
        "subjects": [SubjectCode.BIOLOGY, SubjectCode.CHEMISTRY, SubjectCode.PHYSICS, SubjectCode.ENGLISH],
        "keywords": [
            "medical", "mbbs", "মেডিকেল", "চিকিৎসা",
            "anatomy", "physiology", "biochemistry",
        ],
        "question_types": ["MCQ"],
        "time_per_question": 60,
        "total_marks": 300,
        "negative_marking": True,
    },
    ExamType.BCS.value: {
        "subjects": [SubjectCode.BANGLA, SubjectCode.ENGLISH, SubjectCode.MATH, SubjectCode.HISTORY],
        "keywords": [
            "bcs", "বিসিএস", "civil service", "সিভিল সার্ভিস",
            "general knowledge", "সাধারণ জ্ঞান", "current affairs",
        ],
        "question_types": ["MCQ", "Written"],
        "time_per_question": 60,
        "total_marks": 200,
        "negative_marking": False,
    },
}

# ---------------------------------------------------------------------------
# Shortcut patterns for common question types
# ---------------------------------------------------------------------------

SHORTCUT_PATTERNS: dict[str, list[str]] = {
    "integration": [
        "দ্রুত পদ্ধতি: Substitution নিয়ম আগে চেষ্টা করুন",
        "By parts: ∫u dv = uv - ∫v du",
        "সময় বাঁচান: সরল ক্ষেত্রে সরাসরি সূত্র প্রয়োগ করুন",
    ],
    "derivative": [
        "Power rule: d/dx(xⁿ) = nxⁿ⁻¹",
        "Chain rule দিয়ে composite function সমাধান করুন",
        "Implicit differentiation: উভয় পক্ষকে x-এর সাপেক্ষে differentiate করুন",
    ],
    "equilibrium": [
        "বল বিশ্লেষণের জন্য Free Body Diagram আঁকুন",
        "ΣF = 0 এবং Στ = 0 প্রয়োগ করুন",
        "ঘর্ষণ বলের দিক সর্বদা গতির বিপরীত",
    ],
    "electricity": [
        "Ohm's law: V = IR সবসময় মনে রাখুন",
        "Series circuit: R_total = R₁ + R₂ + ...",
        "Parallel circuit: 1/R_total = 1/R₁ + 1/R₂ + ...",
    ],
    "organic_chemistry": [
        "Functional group চিহ্নিত করুন আগে",
        "IUPAC নামকরণ: সবচেয়ে লম্বা chain মূল ভিত্তি",
        "Reaction type: addition, substitution, elimination",
    ],
}


class AdmissionEngine:
    """Detect exam patterns and provide targeted preparation guidance."""

    def detect_exam_type(self, text: str) -> Optional[str]:
        """Detect which admission exam the question relates to."""
        lower = text.lower()
        for exam_type, pattern_data in EXAM_PATTERNS.items():
            for keyword in pattern_data["keywords"]:
                if keyword in lower:
                    return exam_type
        return None

    def get_exam_strategy(self, exam_type: str) -> str:
        """Return exam-specific strategy tips in Bengali."""
        strategies = {
            ExamType.BUET.value: """
**BUET পরীক্ষার কৌশল:**
• পদার্থবিজ্ঞান, রসায়ন, গণিতে সমান মনোযোগ দিন
• প্রতিটি প্রশ্নে সর্বোচ্চ ৯০ সেকেন্ড ব্যয় করুন
• নেগেটিভ মার্কিং আছে – অনিশ্চিত প্রশ্ন এড়িয়ে যান
• পূর্ববর্তী ১০ বছরের প্রশ্ন সমাধান করুন
• গণিতের সূত্র মুখস্থ না করে বুঝে প্রয়োগ করুন
""",
            ExamType.DU.value: """
**ঢাকা বিশ্ববিদ্যালয় ভর্তি কৌশল:**
• বাংলা ও ইংরেজি ব্যাকরণে দক্ষতা অর্জন করুন
• সাধারণ জ্ঞান আপডেট রাখুন
• প্রতিটি ইউনিটের বিশেষ বিষয়ে ফোকাস করুন
• MCQ তে প্রতি প্রশ্নে ১ মিনিটের বেশি সময় দেবেন না
• নিয়মিত মক টেস্ট দিন
""",
            ExamType.MEDICAL.value: """
**মেডিকেল ভর্তি কৌশল:**
• জীববিজ্ঞানে সর্বোচ্চ প্রাধান্য দিন (সর্বোচ্চ নম্বর)
• রসায়ন ও পদার্থবিজ্ঞানের সূত্র দ্রুত প্রয়োগের অভ্যাস করুন
• Anatomy এবং Physiology গভীরভাবে পড়ুন
• নেগেটিভ মার্কিং থেকে সাবধান থাকুন
• প্রতিদিন ১০০+ MCQ অনুশীলন করুন
""",
            ExamType.BCS.value: """
**BCS পরীক্ষার কৌশল:**
• বাংলাদেশ ও আন্তর্জাতিক বিষয়াবলি নিয়মিত পড়ুন
• গণিত ও মানসিক দক্ষতায় শর্টকাট পদ্ধতি শিখুন
• বাংলা সাহিত্য ও ব্যাকরণে দক্ষতা তৈরি করুন
• ইংরেজি vocabulary এবং grammar শক্তিশালী করুন
• সময় ব্যবস্থাপনা: প্রতি প্রশ্নে ৬০ সেকেন্ড
""",
        }
        return strategies.get(exam_type, "সাধারণ পরীক্ষার কৌশল: নিয়মিত অনুশীলন করুন।")

    def get_shortcuts_for_topic(self, topic: str) -> list[str]:
        """Return relevant shortcuts for a given topic."""
        lower = topic.lower()
        results: list[str] = []
        for keyword, shortcuts in SHORTCUT_PATTERNS.items():
            if keyword in lower:
                results.extend(shortcuts)
        return results

    def classify_question_type(self, question: str) -> str:
        """Classify the question type (MCQ, problem-solving, theory)."""
        lower = question.lower()

        if any(kw in lower for kw in ["which", "what is", "কোনটি", "কোনটা"]):
            return "MCQ"

        if any(kw in lower for kw in ["prove", "show that", "প্রমাণ করুন", "দেখাও"]):
            return "proof"

        if any(kw in lower for kw in ["calculate", "find", "solve", "নির্ণয়", "সমাধান", "বের করো"]):
            return "problem_solving"

        if any(kw in lower for kw in ["explain", "describe", "what", "why", "ব্যাখ্যা", "বর্ণনা"]):
            return "theory"

        return "general"

    def get_marks_breakdown(self, exam_type: str) -> dict:
        """Return marks breakdown for an exam type."""
        breakdowns = {
            ExamType.BUET.value: {
                "পদার্থবিজ্ঞান": 200,
                "রসায়ন": 100,
                "গণিত": 100,
                "ইংরেজি": 100,
            },
            ExamType.MEDICAL.value: {
                "জীববিজ্ঞান": 100,
                "রসায়ন": 100,
                "পদার্থবিজ্ঞান": 50,
                "ইংরেজি": 50,
            },
            ExamType.DU.value: {
                "বাংলা": 30,
                "ইংরেজি": 30,
                "সাধারণ জ্ঞান": 30,
                "বিষয়ভিত্তিক": 30,
            },
            ExamType.BCS.value: {
                "বাংলাদেশ বিষয়াবলি": 50,
                "আন্তর্জাতিক বিষয়াবলি": 20,
                "বাংলা ভাষা ও সাহিত্য": 35,
                "ইংরেজি ভাষা ও সাহিত্য": 35,
                "গণিত ও মানসিক দক্ষতা": 30,
                "বিজ্ঞান ও প্রযুক্তি": 15,
                "ভূগোল, পরিবেশ ও দুর্যোগ": 10,
                "নৈতিকতা ও সুশাসন": 10,
            },
        }
        return breakdowns.get(exam_type, {})


admission_engine = AdmissionEngine()
