from fastapi import APIRouter
from models.user import UserLogin
from utils.jwt_handler import create_token

router = APIRouter()

@router.post("/login")
def login(user: UserLogin):
    # Later replace with real database auth
    token = create_token({"email": user.email})
    return {"access_token": token}
