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
from app.core.constants import NCTB_CHAPTERS
from app.models.schemas import ClassLevel, SubjectCode, ExamType, BoardType


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
        subject_map = NCTB_CHAPTERS.get(subject.value, {})
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

        parts.append(self.get_subject_prompt(subject))

        class_ctx = self.get_class_context(class_level)
        if class_ctx:
            parts.append(class_ctx)

        board_ctx = self.get_board_context(board)
        if board_ctx:
            parts.append(board_ctx)

        exam_ctx = self.get_exam_prompt(exam_type)
        if exam_ctx:
            parts.append(exam_ctx)

        topics = self.get_syllabus_topics(subject, class_level)
        if topics:
            topic_list = ", ".join(topics)
            parts.append(f"এই শ্রেণীতে প্রাসঙ্গিক বিষয়সমূহ: {topic_list}")

        if data_saver_mode:
            parts.append(DATA_SAVER_PROMPT)

        return "\n\n".join(parts)

    def validate_class_subject(
        self,
        class_level: Optional[ClassLevel],
        subject: Optional[SubjectCode],
    ) -> bool:
        if class_level is None or subject is None:
            return True
        if subject == SubjectCode.HIGHER_MATH and class_level.value < 11:
            return False
        return True


nctb_service = NCTBContextService()
