"""
NCTB Context Service

Injects NCTB curriculum context into system prompts based on the user's
selected class, subject, exam type, and education board.
"""

from typing import Optional

from app.core.config import settings
from app.core.prompts_bn import (
    BASE_SYSTEM_PROMPT,
    CLASS_LEVEL_PROMPTS,
    SUBJECT_PROMPTS,
    ADMISSION_PROMPTS,
    DATA_SAVER_PROMPT,
)
from app.models.schemas import ClassLevel, SubjectCode, ExamType, BoardType


# ---------------------------------------------------------------------------
# NCTB Syllabus Topic Mappings (abbreviated – extend as needed)
# ---------------------------------------------------------------------------

SYLLABUS_TOPICS: dict[str, dict[int, list[str]]] = {
    SubjectCode.PHYSICS: {
        9: ["ভৌত রাশি ও পরিমাপ", "গতি", "বল", "কাজ শক্তি ও ক্ষমতা", "পদার্থের অবস্থা ও চাপ"],
        10: ["তরঙ্গ ও শব্দ", "আলোর প্রতিফলন", "স্থির বিদ্যুৎ", "চল বিদ্যুৎ", "আধুনিক পদার্থবিজ্ঞান ও ইলেকট্রনিক্স"],
        11: ["ভেক্টর", "নিউটনের গতিসূত্র", "মহাকর্ষ ও অভিকর্ষ", "পদার্থের বৈশিষ্ট্য", "তাপগতিবিদ্যা"],
        12: ["তড়িৎচুম্বকত্ব", "পরমাণু মডেল", "নিউক্লিয়ার পদার্থবিজ্ঞান", "সেমিকন্ডাক্টর", "জ্যোতির্বিজ্ঞান"],
    },
    SubjectCode.CHEMISTRY: {
        9: ["পদার্থের গঠন", "পর্যায় সারণি", "রাসায়নিক বন্ধন", "মোলের ধারণা", "রাসায়নিক বিক্রিয়া"],
        10: ["তড়িৎ রসায়ন", "এসিড ক্ষার লবণ", "জৈব রসায়ন", "পরিমাণগত রসায়ন", "বাস্তব জীবনে রসায়ন"],
        11: ["পারমাণবিক গঠন", "রাসায়নিক পরিমিতি", "গ্যাসের ধর্ম", "তাপ রসায়ন", "দ্রবণ রসায়ন"],
        12: ["জৈব যৌগের শ্রেণিবিভাগ", "হ্যালোজেন যৌগ", "অ্যামিন", "কার্বোহাইড্রেট", "বিশ্লেষণী রসায়ন"],
    },
    SubjectCode.MATH: {
        9: ["বাস্তব সংখ্যা", "সেট ও ফাংশন", "বীজগাণিতিক রাশি", "সরল সমীকরণ", "জ্যামিতি"],
        10: ["দ্বিঘাত সমীকরণ", "ত্রিকোণমিতি", "পরিমিতি", "পরিসংখ্যান", "সম্ভাবনা"],
        11: ["সংযোগ রেখা", "ম্যাট্রিক্স", "নির্ণায়ক", "জটিল সংখ্যা", "বিন্যাস সমাবেশ"],
        12: ["ক্যালকুলাস", "অন্তরীকরণ", "যোগজীকরণ", "কনিক সেকশন", "ভেক্টর"],
    },
    SubjectCode.BIOLOGY: {
        9: ["কোষ ও এর গঠন", "কোষ বিভাজন", "উদ্ভিদ শারীরতত্ত্ব", "প্রাণীর শারীরিক গঠন", "বাস্তুতন্ত্র"],
        10: ["জীনতত্ত্ব", "বিবর্তন", "মানব শারীরতত্ত্ব", "রোগ ও স্বাস্থ্য", "জৈবপ্রযুক্তি"],
        11: ["কোষ রসায়ন", "উদ্ভিদ টিস্যু", "উদ্ভিদ শ্বসন", "উদ্ভিদ পুষ্টি", "প্রজনন"],
        12: ["প্রাণী টিস্যু", "রক্ত সংবহন", "শ্বসনতন্ত্র", "রেচনতন্ত্র", "স্নায়ুতন্ত্র"],
    },
}


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------

class NCTBContextService:
    """Build context-enriched system prompts based on NCTB parameters."""

    def get_subject_prompt(self, subject: Optional[SubjectCode]) -> str:
        if subject is None:
            return BASE_SYSTEM_PROMPT
        return SUBJECT_PROMPTS.get(subject.value, BASE_SYSTEM_PROMPT)

    def get_class_context(self, class_level: Optional[ClassLevel]) -> str:
        if class_level is None:
            return ""
        return CLASS_LEVEL_PROMPTS.get(class_level.value, "")

    def get_exam_prompt(self, exam_type: Optional[ExamType]) -> str:
        if exam_type is None or exam_type == ExamType.GENERAL:
            return ""
        return ADMISSION_PROMPTS.get(exam_type.value, "")

    def get_board_context(self, board: Optional[BoardType]) -> str:
        if board is None:
            return ""
        return f"শিক্ষার্থী {board.value} শিক্ষা বোর্ডের অধীনে পড়াশোনা করছে।"

    def get_syllabus_topics(
        self,
        subject: Optional[SubjectCode],
        class_level: Optional[ClassLevel],
    ) -> list[str]:
        """Return relevant syllabus topics for the given subject and class."""
        if subject is None or class_level is None:
            return []
        subject_map = SYLLABUS_TOPICS.get(subject, {})
        return subject_map.get(class_level.value, [])

    async def get_context_prompt(
        self,
        class_level: Optional[ClassLevel] = None,
        subject: Optional[SubjectCode] = None,
        exam_type: Optional[ExamType] = None,
        board: Optional[BoardType] = None,
        data_saver_mode: bool = False,
    ) -> str:
        """
        Build a complete system prompt by combining subject, class, exam,
        and board context segments.
        """
        parts: list[str] = []

        # 1. Subject-specific base prompt
        parts.append(self.get_subject_prompt(subject))

        # 2. Class-level context
        class_ctx = self.get_class_context(class_level)
        if class_ctx:
            parts.append(class_ctx)

        # 3. Board context
        board_ctx = self.get_board_context(board)
        if board_ctx:
            parts.append(board_ctx)

        # 4. Exam / admission context (overrides if non-general)
        exam_ctx = self.get_exam_prompt(exam_type)
        if exam_ctx:
            parts.append(exam_ctx)

        # 5. Relevant syllabus topics
        topics = self.get_syllabus_topics(subject, class_level)
        if topics:
            topic_list = "、".join(topics)
            parts.append(f"এই শ্রেণীতে প্রাসঙ্গিক বিষয়সমূহ: {topic_list}")

        # 6. Data-saver modifier
        if data_saver_mode:
            parts.append(DATA_SAVER_PROMPT)

        return "\n\n".join(parts)

    def validate_class_subject(
        self,
        class_level: Optional[ClassLevel],
        subject: Optional[SubjectCode],
    ) -> bool:
        """Basic validation: some subjects are only available in certain classes."""
        if class_level is None or subject is None:
            return True
        # Higher Math is only for classes 11 and 12
        if subject == SubjectCode.HIGHER_MATH and class_level.value < 11:
            return False
        return True


nctb_service = NCTBContextService()
