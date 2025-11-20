from fastapi import APIRouter, HTTPException
from src.models.user_login import UserLogin
from src.utils.jwt_handler import create_access_token

router = APIRouter()

@router.post("/login")
def login(user: UserLogin):
    """
    Simple placeholder login endpoint.
    Accepts a username and password and returns a JWT token.
    """
    if user.username == "" or user.password == "":
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
