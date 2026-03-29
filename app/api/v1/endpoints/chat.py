"""
Streaming Chat Endpoint

Route: POST /api/v1/chat/stream  – Server-Sent Events (SSE)
Route: POST /api/v1/chat         – Non-streaming (full response)
"""

import json
import logging
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SubjectCode,
)
from app.services.banglish_parser import banglish_parser
from app.services.nctb_context_service import nctb_service
from app.services.rag_service import rag_service
from app.services.ai_router import ai_router
from app.services.cache_service import cache_service
from app.core.config import settings
from app.utils.validators import validate_message, sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _event_stream(
    request: ChatRequest,
    session_id: str,
) -> AsyncGenerator[bytes, None]:
    """Build and stream an SSE (Server-Sent Events) response."""
    try:
        # 1. Sanitise and parse Banglish input
        sanitized = sanitize_text(request.message)
        parse_result = await banglish_parser.full_parse(sanitized)
        normalized_message = parse_result["normalized"]

        # Auto-detect subject if not provided or set to GENERAL
        detected_subject = parse_result.get("detected_subject")
        subject = request.subject
        if (subject is None or subject == SubjectCode.GENERAL) and detected_subject:
            subject = detected_subject

        # 2. Build NCTB system prompt
        system_prompt = await nctb_service.get_context_prompt(
            class_level=request.class_level,
            subject=subject,
            exam_type=request.exam_type,
            board=request.board,
            data_saver_mode=request.data_saver_mode,
        )

        # 3. Query RAG for relevant context
        rag_context = ""
        if request.include_rag:
            rag_context = await rag_service.query(
                query=normalized_message,
                subject=subject.value if subject else None,
                class_level=request.class_level.value if request.class_level else None,
                exam_type=request.exam_type.value if request.exam_type else None,
            )

        # 4. Stream AI response
        chunk_size = settings.CHUNK_SIZE // 2 if request.data_saver_mode else settings.CHUNK_SIZE
        chunk_buffer = ""

        async for text_chunk in ai_router.route(
            message=normalized_message,
            system_prompt=system_prompt,
            rag_context=rag_context,
            preferred_model=request.preferred_model,
        ):
            chunk_buffer += text_chunk

            while len(chunk_buffer) >= chunk_size:
                emit, chunk_buffer = chunk_buffer[:chunk_size], chunk_buffer[chunk_size:]
                payload = json.dumps({"content": emit, "done": False}, ensure_ascii=False)
                yield f"data: {payload}\n\n".encode("utf-8")

        # Flush remaining buffer
        if chunk_buffer:
            payload = json.dumps({"content": chunk_buffer, "done": False}, ensure_ascii=False)
            yield f"data: {payload}\n\n".encode("utf-8")

        # Final done signal
        yield b"data: [DONE]\n\n"

    except Exception as exc:
        logger.error("Streaming error for session %s: %s", session_id, exc)
        error_payload = json.dumps(
            {"content": "", "done": True, "error": str(exc)},
            ensure_ascii=False,
        )
        yield f"data: {error_payload}\n\n".encode("utf-8")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat/stream", tags=["chat"], summary="Streaming chat with NCTB context")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Server-Sent Events (SSE) streaming chat endpoint.

    - Parses Banglish input and normalises it to Bengali.
    - Injects NCTB curriculum context based on class/subject/board selection.
    - Queries ChromaDB for previous-year questions and shortcuts (RAG).
    - Routes to the best available AI model (Gemini / DeepSeek / Grok).
    - Streams the response using Server-Sent Events (SSE).
    """
    is_valid, error = validate_message(request.message)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    session_id = request.session_id or str(uuid.uuid4())
    logger.info(
        "Chat stream | session=%s | class=%s | subject=%s | model=%s",
        session_id,
        request.class_level,
        request.subject,
        request.preferred_model,
    )

    return StreamingResponse(
        _event_stream(request, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-ID": session_id,
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.post("/chat", tags=["chat"], response_model=ChatResponse, summary="Non-streaming chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Non-streaming chat endpoint (collects the full response before returning).
    Useful for clients that don't support SSE.
    """
    is_valid, error = validate_message(request.message)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    session_id = request.session_id or str(uuid.uuid4())

    sanitized = sanitize_text(request.message)
    parse_result = await banglish_parser.full_parse(sanitized)
    normalized_message = parse_result["normalized"]

    detected_subject = parse_result.get("detected_subject")
    subject = request.subject
    if (subject is None or subject == SubjectCode.GENERAL) and detected_subject:
        subject = detected_subject

    system_prompt = await nctb_service.get_context_prompt(
        class_level=request.class_level,
        subject=subject,
        exam_type=request.exam_type,
        board=request.board,
        data_saver_mode=request.data_saver_mode,
    )

    rag_context = ""
    if request.include_rag:
        rag_context = await rag_service.query(
            query=normalized_message,
            subject=subject.value if subject else None,
            class_level=request.class_level.value if request.class_level else None,
            exam_type=request.exam_type.value if request.exam_type else None,
        )

    full_response = ""
    async for chunk in ai_router.route(
        message=normalized_message,
        system_prompt=system_prompt,
        rag_context=rag_context,
        preferred_model=request.preferred_model,
    ):
        full_response += chunk

    return ChatResponse(
        message=full_response,
        session_id=session_id,
        model_used=request.preferred_model.value,
        subject=subject.value if subject else None,
        class_level=request.class_level.value if request.class_level else None,
        rag_used=bool(rag_context),
    )


@router.get("/subjects", tags=["metadata"], summary="List supported subjects")
async def list_subjects():
    """Return all NCTB-supported subjects with Bengali names."""
    return {
        "subjects": [
            {"code": code, "name_bn": name_bn}
            for code, name_bn in settings.SUPPORTED_SUBJECTS.items()
        ]
    }


@router.get("/classes", tags=["metadata"], summary="List supported class levels")
async def list_classes():
    """Return supported class levels and boards."""
    return {
        "classes": settings.SUPPORTED_CLASSES,
        "boards": settings.SUPPORTED_BOARDS,
    }


@router.get("/health", tags=["health"], response_model=HealthResponse)
async def health_check():
    """API health check."""
    available_models = []
    if settings.GEMINI_API_KEY:
        available_models.append("gemini")
    if settings.DEEPSEEK_API_KEY:
        available_models.append("deepseek")
    if settings.GROK_API_KEY:
        available_models.append("grok")

    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        models_available=available_models,
    )
