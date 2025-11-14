import os
from anthropic import Anthropic

# Load API key from environment variable
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def rewrite_with_claude(raw_text: str, tone: str = "executive") -> str:
    system_prompt = (
        "You are a helpful assistant that rewrites internal company reports into clean, professional summaries. "
        "Format the response like an executive summary with brief sections. Use a polished tone suitable for business communication."
    )

    user_prompt = f"""Here is the raw report text:
---
{raw_text}
---
Reformat and rewrite this report to be professional, well-structured, and concise. Keep all important information, but feel free to reword or polish for clarity.
"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Or "claude-3-sonnet-20240229"
        max_tokens=1024,
        temperature=0.5,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.content[0].text
