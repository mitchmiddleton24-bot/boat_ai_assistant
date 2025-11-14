import os
from pathlib import Path
from openai import OpenAI
import anthropic
import data_loader
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

# --- Load .env ---
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

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

# --- FastAPI app ---
app = FastAPI(
    title="Boat AI Assistant",
    description="API that lets you query OpenAI or Claude",
    version="1.0.0"
)

# --- Root route (so Render knows the app works) ---
@app.get("/", tags=["System"])
def read_root():
    return {"message": "Hello from boat_ai_assistant!"}

class PromptRequest(BaseModel):
    prompt: str = Field(..., example="What is condition-based maintenance?")
    model: str = Field(..., example="openai", description="Choose either 'openai' or 'claude'")

@app.post("/ask", summary="Query a model", description="Sends a prompt to OpenAI or Claude and returns the result.")
async def ask_ai(req: PromptRequest):
    prompt = req.prompt.strip()
    model = req.model.lower().strip()

    if not prompt:
        return {"error": "Prompt is required."}

    try:
        if model == "openai":
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return {"response": response.choices[0].message.content}
        elif model == "claude":
            response = anthropic_client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"response": response.content[0].text}
        else:
            return {"error": "Invalid model. Use 'openai' or 'claude'."}
    except Exception as e:
        return {"error": str(e)}

@app.get("/internal/status", tags=["Internal"])
def internal_status():
    return {"status": "Boat AI Assistant is running."}

@app.get("/internal/models", tags=["Internal"])
def list_models():
    return {"models": ["openai", "claude"]}

from data_loader import (
    get_dummy_emails,
    get_dummy_transcript,
    load_email_data,
    load_subcontractor_data,
    load_transcript_data,
    load_stats_summary,
)

@app.get("/data/emails", tags=["Internal Data"])
def get_emails():
    return {"emails": get_dummy_emails()}

@app.get("/data/transcript", tags=["Internal Data"])
def get_transcript():
    return {"transcript": get_dummy_transcript()}

@app.get("/data/email_data", tags=["Internal Data"])
def get_email_data():
    return JSONResponse(content={"email_data": load_email_data()})

@app.get("/data/subcontractors", tags=["Internal Data"])
def get_subcontractors():
    return JSONResponse(content={"subcontractors": load_subcontractor_data()})

@app.get("/data/transcripts", tags=["Internal Data"])
def get_transcripts():
    return JSONResponse(content={"transcripts": load_transcript_data()})

@app.get("/data/stats_summary", tags=["Internal Data"])
def get_stats():
    return JSONResponse(content={"stats": load_stats_summary()})
