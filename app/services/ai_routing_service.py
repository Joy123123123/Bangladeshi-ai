"""
AI Routing Service

Routes user queries to the most appropriate AI model:
  - Gemini (Google) – default, best for educational content
  - DeepSeek – great for math / coding / STEM reasoning
  - Grok (xAI) – strong at general knowledge

Implements automatic fallback and load balancing.
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional

from app.core.config import settings
from app.core.prompts_bn import ERROR_MESSAGES
from app.models.schemas import AIModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports for AI SDKs
# ---------------------------------------------------------------------------

def _get_gemini():
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        return None


def _get_openai_client(base_url: str, api_key: str):
    try:
        from openai import AsyncOpenAI
        return AsyncOpenAI(base_url=base_url, api_key=api_key)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Model adapters
# ---------------------------------------------------------------------------

async def _stream_gemini(
    message: str,
    system_prompt: str,
    rag_context: str,
) -> AsyncGenerator[str, None]:
    """Stream response from Google Gemini."""
    genai = _get_gemini()
    if genai is None:
        yield ERROR_MESSAGES["model_unavailable"]
        return

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL_NAME,
        system_instruction=system_prompt,
    )

    full_prompt = f"{rag_context}\n\n{message}" if rag_context else message

    try:
        response = model.generate_content(full_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0)
    except Exception as exc:
        logger.error("Gemini streaming error: %s", exc)
        yield ERROR_MESSAGES["model_unavailable"]


async def _stream_openai_compatible(
    message: str,
    system_prompt: str,
    rag_context: str,
    model_name: str,
    base_url: str,
    api_key: str,
) -> AsyncGenerator[str, None]:
    """Stream response from any OpenAI-compatible API (DeepSeek, Grok)."""
    client = _get_openai_client(base_url=base_url, api_key=api_key)
    if client is None:
        yield ERROR_MESSAGES["model_unavailable"]
        return

    user_content = f"{rag_context}\n\n{message}" if rag_context else message
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    try:
        stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
            max_tokens=settings.MAX_TOKENS,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta
                await asyncio.sleep(0)
    except Exception as exc:
        logger.error("OpenAI-compatible streaming error (%s): %s", model_name, exc)
        yield ERROR_MESSAGES["model_unavailable"]


# ---------------------------------------------------------------------------
# AI Router
# ---------------------------------------------------------------------------

class AIRoutingService:
    """Select the best AI model and stream its response."""

    def _select_model(
        self,
        preferred: AIModel,
        message: str,
    ) -> AIModel:
        """
        Choose the model to use.

        AUTO strategy:
          - Math/STEM hints → DeepSeek (strong reasoning)
          - Everything else → Gemini
        """
        if preferred != AIModel.AUTO:
            return preferred

        # Simple heuristic: keywords suggesting math/code → DeepSeek
        stem_keywords = ["solve", "calculate", "গণিত", "math", "code", "algorithm", "proof"]
        lower = message.lower()
        if any(kw in lower for kw in stem_keywords) and settings.DEEPSEEK_API_KEY:
            return AIModel.DEEPSEEK

        if settings.GEMINI_API_KEY:
            return AIModel.GEMINI
        if settings.DEEPSEEK_API_KEY:
            return AIModel.DEEPSEEK
        if settings.GROK_API_KEY:
            return AIModel.GROK

        return AIModel.GEMINI

    async def route(
        self,
        message: str,
        system_prompt: str,
        rag_context: str = "",
        preferred_model: AIModel = AIModel.AUTO,
    ) -> AsyncGenerator[str, None]:
        """
        Route the query to the selected model and return an async generator
        that yields text chunks.
        """
        model = self._select_model(preferred_model, message)
        logger.info("Routing query to model: %s", model.value)

        primary_gen = self._get_generator(model, message, system_prompt, rag_context)
        try:
            async for chunk in primary_gen:
                yield chunk
        except Exception as exc:
            logger.error("Primary model %s failed: %s – trying fallback", model.value, exc)
            fallback = self._get_fallback_model(model)
            if fallback:
                async for chunk in self._get_generator(fallback, message, system_prompt, rag_context):
                    yield chunk
            else:
                yield ERROR_MESSAGES["model_unavailable"]

    def _get_generator(
        self,
        model: AIModel,
        message: str,
        system_prompt: str,
        rag_context: str,
    ) -> AsyncGenerator[str, None]:
        if model == AIModel.GEMINI:
            return _stream_gemini(message, system_prompt, rag_context)
        elif model == AIModel.DEEPSEEK:
            return _stream_openai_compatible(
                message=message,
                system_prompt=system_prompt,
                rag_context=rag_context,
                model_name=settings.DEEPSEEK_MODEL_NAME,
                base_url=settings.DEEPSEEK_BASE_URL,
                api_key=settings.DEEPSEEK_API_KEY,
            )
        elif model == AIModel.GROK:
            return _stream_openai_compatible(
                message=message,
                system_prompt=system_prompt,
                rag_context=rag_context,
                model_name=settings.GROK_MODEL_NAME,
                base_url=settings.GROK_BASE_URL,
                api_key=settings.GROK_API_KEY,
            )
        # Fallback
        return _stream_gemini(message, system_prompt, rag_context)

    def _get_fallback_model(self, failed_model: AIModel) -> Optional[AIModel]:
        """Return the next available fallback model."""
        order = [AIModel.GEMINI, AIModel.DEEPSEEK, AIModel.GROK]
        for m in order:
            if m != failed_model:
                api_key = {
                    AIModel.GEMINI: settings.GEMINI_API_KEY,
                    AIModel.DEEPSEEK: settings.DEEPSEEK_API_KEY,
                    AIModel.GROK: settings.GROK_API_KEY,
                }.get(m, "")
                if api_key:
                    return m
        return None


ai_router = AIRoutingService()
