from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter()


class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(payload: UserLogin) -> Dict[str, str]:
    """
    Very simple dummy login endpoint.

    For now this just checks against a hard coded user so that Render
    has a working endpoint and the rest of the API can be tested.
    Replace this logic later with real authentication.
    """
    # Dummy credentials – change later when you add real auth
    if payload.email != "test@example.com" or payload.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Dummy token just so the client has something to work with
    return {
        "access_token": "dummy-token",
        "token_type": "bearer",
    }
