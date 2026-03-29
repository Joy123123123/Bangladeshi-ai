"""
Google Gemini AI service.

Uses the google-generativeai SDK.
Gemini 1.5 Flash is free-tier and very capable.
"""

from typing import List, Optional

import google.generativeai as genai

from app.utils.config import settings


def _get_client() -> genai.GenerativeModel:
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


async def generate_response(
    prompt: str,
    system_prompt: str,
    history: Optional[List[dict]] = None,
) -> str:
    """
    Generate a response from Gemini.

    Args:
        prompt: The user's latest message.
        system_prompt: System instruction prepended to the conversation.
        history: Previous turns as list of {"role": ..., "parts": [...]}.

    Returns:
        The assistant's text reply.
    """
    model = _get_client()

    # Build Gemini-format history
    gemini_history: List[dict] = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

    # Prepend system prompt as a user/model exchange if no native system support
    if system_prompt and not gemini_history:
        gemini_history = [
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["Understood! I am ready to help."]},
        ]

    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(prompt)
    return response.text
