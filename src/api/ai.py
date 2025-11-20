from fastapi import APIRouter
from src.models.prompt import PromptRequest
from src.services.openai_client import ask_openai

router = APIRouter()

@router.post("/ask")
async def ask_ai(prompt: PromptRequest):
    """
    Send a prompt to OpenAI (or Anthropic) and return the response.
    """
    answer = await ask_openai(prompt.prompt)
    return {"response": answer}
