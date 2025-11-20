from pydantic import BaseModel

class SubcontractorScore(BaseModel):
    name: str
    score: int
