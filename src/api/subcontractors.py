from fastapi import APIRouter
from models.subcontractor import SubcontractorScore

router = APIRouter()

@router.get("/dummy")
def get_dummy_scores():
    return [
        SubcontractorScore(name="Alpha Concrete", score=92),
        SubcontractorScore(name="Miller Electrical", score=85),
    ]
