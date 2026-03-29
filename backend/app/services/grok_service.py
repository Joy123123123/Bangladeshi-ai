"""
Grok (xAI) AI service.

Grok exposes an OpenAI-compatible API at api.x.ai.
"""

from typing import List, Optional

from openai import AsyncOpenAI

from app.utils.config import settings

_GROK_BASE_URL = "https://api.x.ai/v1"
_GROK_MODEL = "grok-beta"


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.grok_api_key,
        base_url=_GROK_BASE_URL,
    )


async def generate_response(
    prompt: str,
    system_prompt: str,
    history: Optional[List[dict]] = None,
) -> str:
    """
    Generate a response from Grok.

    Args:
        prompt: The user's latest message.
        system_prompt: System-level instruction.
        history: Previous turns as list of {"role": ..., "content": ...}.

    Returns:
        The assistant's text reply.
    """
    client = _get_client()

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=_GROK_MODEL,
        messages=messages,  # type: ignore[arg-type]
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""
