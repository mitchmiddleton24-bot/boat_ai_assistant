from pydantic import BaseModel

class PromptRequest(BaseModel):
    model: str
    prompt: str
