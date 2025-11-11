import os
from pathlib import Path
from openai import OpenAI
import anthropic
from dotenv import load_dotenv

# --- Load .env ---
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)
print("OPENAI KEY:", os.getenv("OPENAI_API_KEY"))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

print("DEBUG - OpenAI Key:", os.getenv("OPENAI_API_KEY"))
print("DEBUG - Anthropic Key:", os.getenv("ANTHROPIC_API_KEY"))

# --- Fetch keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

# --- Constants ---
ANTHROPIC_MODEL = "claude-3-haiku-20240307"
MAX_TOKENS = 2048
TEMPERATURE = 0.7

# --- API Clients ---
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# --- Functions ---
def ask_openai(prompt):
    if not prompt:
        return "No prompt provided."
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {e}"

def ask_claude(prompt):
    if not prompt:
        return "No prompt provided."
    try:
        response = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Claude Error: {e}"

# --- Main ---
if __name__ == "__main__":
    try:
        mode = os.environ.get("MODEL_MODE", "openai").strip().lower()
        prompt = os.environ.get("PROMPT", "What is the weather like today?").strip()

        if mode == "openai":
            print("\n--- OpenAI GPT-4 Response ---")
            print(ask_openai(prompt))
        elif mode == "claude":
            print("\n--- Claude 3 Haiku Response ---")
            print(ask_claude(prompt))
        else:
            print("Invalid selection. Please choose 'openai' or 'claude'.")

    except KeyboardInterrupt:
        print("\nProgram exited by user.")
