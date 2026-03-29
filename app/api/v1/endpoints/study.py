"""
Study Helpers Endpoint

Provides AI-powered study tools: summaries, flashcards, quizzes, and mind maps
based on NCTB curriculum content.
"""

import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import StudyRequest, SubjectCode
from app.services.banglish_parser import banglish_parser
from app.services.nctb_context_service import nctb_service
from app.services.ai_router import ai_router
from app.core.config import settings
from app.utils.validators import validate_topic, sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Study prompt templates
# ---------------------------------------------------------------------------

STUDY_PROMPTS = {
    "summary": "নিচের বিষয়টির একটি সংক্ষিপ্ত সারসংক্ষেপ বাংলায় লিখুন। মূল বিষয়গুলো বুলেট পয়েন্টে দিন:",
    "flashcards": """নিচের বিষয়টির জন্য ১০টি ফ্ল্যাশকার্ড তৈরি করুন। প্রতিটি ফ্ল্যাশকার্ড এই ফরম্যাটে হবে:
প্রশ্ন: [প্রশ্ন]
উত্তর: [উত্তর]
---""",
    "quiz": """নিচের বিষয়টির উপর ৫টি MCQ প্রশ্ন তৈরি করুন বাংলায়। প্রতিটি প্রশ্নের ৪টি অপশন এবং সঠিক উত্তর দিন:
ফরম্যাট:
প্রশ্ন: [প্রশ্ন]
(ক) [অপশন ১]
(খ) [অপশন ২]
(গ) [অপশন ৩]
(ঘ) [অপশন ৪]
উত্তর: [সঠিক অপশন]
---""",
    "mindmap": """নিচের বিষয়টির জন্য একটি মাইন্ড ম্যাপ তৈরি করুন টেক্সট ফরম্যাটে:
কেন্দ্রীয় বিষয় → শাখা ১ → উপশাখা
                  → শাখা ২ → উপশাখা
                  ইত্যাদি""",
    "notes": "নিচের বিষয়টির জন্য পরীক্ষার নোট তৈরি করুন। গুরুত্বপূর্ণ সূত্র ও তথ্য অন্তর্ভুক্ত করুন:",
}


async def _study_stream(
    request: StudyRequest,
    session_id: str,
) -> AsyncGenerator[bytes, None]:
    """Generate study content as an SSE stream."""
    try:
        sanitized = sanitize_text(request.topic)
        parse_result = await banglish_parser.full_parse(sanitized)
        normalized_topic = parse_result["normalized"]

        subject = request.subject
        if (subject is None or subject == SubjectCode.GENERAL) and parse_result.get("detected_subject"):
            subject = parse_result["detected_subject"]

        system_prompt = await nctb_service.get_context_prompt(
            class_level=request.class_level,
            subject=subject,
            data_saver_mode=request.data_saver_mode,
        )

        request_type = request.request_type.lower()
        instruction = STUDY_PROMPTS.get(request_type, STUDY_PROMPTS["summary"])
        full_message = f"{instruction}\n\n{normalized_topic}"

        chunk_size = settings.CHUNK_SIZE // 2 if request.data_saver_mode else settings.CHUNK_SIZE
        chunk_buffer = ""

        async for text_chunk in ai_router.route(
            message=full_message,
            system_prompt=system_prompt,
            preferred_model=request.preferred_model,
        ):
            chunk_buffer += text_chunk
            while len(chunk_buffer) >= chunk_size:
                emit, chunk_buffer = chunk_buffer[:chunk_size], chunk_buffer[chunk_size:]
                payload = json.dumps({"content": emit, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n".encode("utf-8")

        if chunk_buffer:
            payload = json.dumps({"content": chunk_buffer, "done": False}, ensure_ascii=False)
            yield f"data: {payload}\n\n".encode("utf-8")

        yield b"data: [DONE]\n\n"

    except Exception as exc:
        logger.error("Study stream error for session %s: %s", session_id, exc)
        error_payload = json.dumps(
            {"content": "", "done": True, "error": str(exc)},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n".encode("utf-8")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/study/stream", tags=["study"], summary="Streaming study helper")
async def study_stream(request: StudyRequest) -> StreamingResponse:
    """
    Generate study materials for a given topic with SSE streaming.

    Request types:
    - **summary**: Concise topic summary with bullet points
    - **flashcards**: Q&A flashcard pairs
    - **quiz**: MCQ quiz questions with answers
    - **mindmap**: Visual mind map in text format
    - **notes**: Exam-ready study notes
    """
    is_valid, error = validate_topic(request.topic)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    session_id = str(uuid.uuid4())
    logger.info("Study stream | type=%s | subject=%s", request.request_type, request.subject)

    return StreamingResponse(
        _study_stream(request, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-ID": session_id,
        },
    )


@router.get("/study/types", tags=["study"], summary="List available study request types")
async def list_study_types():
    """Return available study content generation types."""
    return {
        "types": [
            {"code": "summary", "name_bn": "সারসংক্ষেপ", "description": "বিষয়ের সংক্ষিপ্ত সারসংক্ষেপ"},
            {"code": "flashcards", "name_bn": "ফ্ল্যাশকার্ড", "description": "প্রশ্ন-উত্তর ফ্ল্যাশকার্ড"},
            {"code": "quiz", "name_bn": "কুইজ", "description": "MCQ কুইজ প্রশ্ন"},
            {"code": "mindmap", "name_bn": "মাইন্ড ম্যাপ", "description": "বিষয়ের ম্যাপিং"},
            {"code": "notes", "name_bn": "নোট", "description": "পরীক্ষার নোট"},
        ]
    }
