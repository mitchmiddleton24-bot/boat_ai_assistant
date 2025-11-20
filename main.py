from fastapi import FastAPI
from api.ai import router as ai_router
from api.upload import router as upload_router
from api.reports import router as reports_router
from api.subcontractors import router as subcontractor_router
from api.auth import router as auth_router

app = FastAPI(
    title="Boat AI Assistant",
    version="1.0.0",
    description="Cloud-based AI assistant for construction & marine companies."
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(subcontractor_router, prefix="/subcontractors", tags=["Subcontractors"])

@app.get("/")
def root():
    return {"message": "Boat AI Assistant API is running."}
