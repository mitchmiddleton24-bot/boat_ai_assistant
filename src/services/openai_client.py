import os
from openai import OpenAI

# Read API key from environment / .env
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment or .env file")

client = OpenAI(api_key=api_key)


def simple_chat(prompt: str, model: str = "gpt-4.1-mini") -> str:
    """
    Simple helper to send a prompt to OpenAI and get back text.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def ask_openai(
    user_prompt: str,
    system_prompt: str | None = None,
    model: str = "gpt-4.1-mini",
) -> str:
    """
    Backward-compatible helper used by the rest of your project.

    Other modules can keep doing:
        from src.services.openai_client import ask_openai
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content
