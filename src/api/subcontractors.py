from fastapi import APIRouter
from src.services.subcontractor_finder import get_dummy_scores

router = APIRouter()

@router.get("/dummy")
async def get_dummy_sub_scores():
    """
    Return placeholder subcontractor performance scores.
    """
    scores = await get_dummy_scores()
    return {"subcontractor_scores": scores}
