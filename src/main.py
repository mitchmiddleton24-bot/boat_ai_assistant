import os
import anthropic
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Constants ---
ANTHROPIC_MODEL = "claude-3-haiku-20240307"
MAX_TOKENS = 2048
TEMPERATURE = 0.7

# --- Clients ---
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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
        mode = input("Choose model [openai / claude]: ").strip().lower()
        prompt = input("Enter your prompt: ").strip()

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
