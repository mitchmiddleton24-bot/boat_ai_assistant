from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

from src.api import graph_endpoints
from src.api.auth import router as auth_router
from src.api.ai import router as ai_router
from src.api.upload import router as upload_router
from src.api.reports import router as reports_router
from src.api.subcontractors import router as subcontractor_router
from src.api.weekly_reports import router as weekly_reports_router
from src.api import weekly_ai_reports

app = FastAPI(
    title="Boat AI Assistant",
    version="1.0.0",
    description="Cloud based AI assistant for construction and marine companies.",
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(subcontractor_router, prefix="/subcontractors", tags=["Subcontractors"])
app.include_router(weekly_reports_router, prefix="/weekly", tags=["Weekly"])
app.include_router(graph_endpoints.router)
app.include_router(weekly_ai_reports.router)


@app.get("/")
def root():
    return {"message": "Boat AI Assistant API is running."}
