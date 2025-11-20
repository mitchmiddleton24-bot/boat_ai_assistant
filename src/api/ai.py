from fastapi import APIRouter
from models.prompt import PromptRequest
from services.openai_client import ask_openai
from services.anthropic_client import ask_claude

router = APIRouter()

@router.post("/ask")
async def ask_ai(req: PromptRequest):
    model = req.model.lower()
    prompt = req.prompt

    if model == "openai":
        return {"response": ask_openai(prompt)}
    if model == "claude":
        return {"response": ask_claude(prompt)}

    return {"error": "Invalid model. Use 'openai' or 'claude'."}
