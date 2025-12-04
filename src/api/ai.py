# src/api/ai.py

from fastapi import APIRouter
from pydantic import BaseModel
from src.services.openai_client import summarize_text

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    content: str


@router.post("/ask")
async def ask_ai(req: PromptRequest):
    """
    General-purpose AI endpoint for testing the OpenAI connection.
    """
    response = summarize_text(
        prompt=req.prompt,
        content=req.content
    )
    return {"response": response}
