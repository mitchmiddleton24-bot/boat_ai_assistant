# src/services/openai_client.py

import os
from typing import Optional

from openai import OpenAI

_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Add it to your .env file before running the app."
    )

_client = OpenAI(api_key=_api_key)


def summarize_text(*, prompt: str, content: str, model: str = "gpt-4.1-mini") -> str:
    """
    Helper to send a summarization request to OpenAI.

    prompt - system style instructions
    content - the combined raw text you want summarized
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content},
    ]

    response = _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=800,
    )

    return response.choices[0].message.content.strip()
